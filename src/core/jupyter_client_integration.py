#!/usr/bin/env python3
"""
Jupyter Client Integration for ValidoAI
Execute code in Python and Julia kernels, capture outputs
"""

import os
import sys
import json
import asyncio
import logging
import tempfile
import subprocess
from typing import Dict, List, Any, Optional, Tuple, Union
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import threading
import uuid

# Jupyter client imports
try:
    from jupyter_client import KernelManager, BlockingKernelClient
    from jupyter_client.kernelspec import find_kernel_specs, get_kernel_spec
    JUPYTER_AVAILABLE = True
except ImportError:
    JUPYTER_AVAILABLE = False
    print("⚠️ jupyter_client not available. Install with: pip install jupyter-client")

# Julia kernel support
try:
    import julia
    from julia.api import Julia
    JULIA_AVAILABLE = True
except ImportError:
    JULIA_AVAILABLE = False
    print("⚠️ Julia support not available. Install with: pip install julia")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ExecutionResult:
    """Result of code execution"""
    success: bool
    output: str = ""
    error: str = ""
    execution_time: float = 0.0
    kernel_type: str = "python"
    result_data: Any = None
    images: List[Dict[str, Any]] = field(default_factory=list)
    html_output: str = ""
    execution_id: str = field(default_factory=lambda: str(uuid.uuid4()))

@dataclass
class KernelSession:
    """Represents a kernel execution session"""
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    kernel_type: str = "python"
    kernel_manager: Any = None
    kernel_client: Any = None
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    status: str = "created"  # created, running, idle, error, shutdown
    execution_count: int = 0

class JupyterKernelManager:
    """Manages Jupyter kernels for code execution"""

    def __init__(self):
        self.sessions: Dict[str, KernelSession] = {}
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.lock = threading.Lock()
        self.default_timeout = 30  # seconds
        self.max_sessions = 10

        # Kernel configurations
        self.python_kernel_name = "validoai-python"
        self.julia_kernel_name = "julia-1.11"  # Adjust based on installed version

        logger.info("🧠 Jupyter Kernel Manager initialized")

    def create_session(self, kernel_type: str = "python") -> str:
        """Create a new kernel session"""
        with self.lock:
            # Check session limit
            if len(self.sessions) >= self.max_sessions:
                self._cleanup_idle_sessions()

            session_id = str(uuid.uuid4())

            if kernel_type == "python":
                kernel_name = self.python_kernel_name
            elif kernel_type == "julia":
                kernel_name = self.julia_kernel_name
            else:
                raise ValueError(f"Unsupported kernel type: {kernel_type}")

            try:
                # Create kernel manager and client
                km = KernelManager(kernel_name=kernel_name)
                km.start_kernel()

                kc = km.client()
                kc.start_channels()

                # Wait for kernel to be ready
                kc.wait_for_ready(timeout=10)

                session = KernelSession(
                    session_id=session_id,
                    kernel_type=kernel_type,
                    kernel_manager=km,
                    kernel_client=kc,
                    status="running"
                )

                self.sessions[session_id] = session

                logger.info(f"✅ Created {kernel_type} kernel session: {session_id}")
                return session_id

            except Exception as e:
                logger.error(f"❌ Failed to create {kernel_type} kernel session: {e}")
                raise

    def execute_code(self, session_id: str, code: str,
                    timeout: int = None) -> ExecutionResult:
        """Execute code in a kernel session"""
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")

        session = self.sessions[session_id]
        if session.status != "running":
            raise RuntimeError(f"Session {session_id} is not running")

        timeout = timeout or self.default_timeout
        start_time = datetime.now()

        try:
            # Execute code
            kc = session.kernel_client

            # Send execute request
            msg_id = kc.execute(code, silent=False, store_history=True)

            # Collect outputs
            outputs = []
            errors = []
            images = []
            html_output = ""

            # Poll for results
            timeout_time = datetime.now() + timedelta(seconds=timeout)
            while datetime.now() < timeout_time:
                try:
                    # Get messages with short timeout
                    msg = kc.get_iopub_msg(timeout=0.1)

                    msg_type = msg['msg_type']
                    content = msg['content']

                    if msg_type == 'stream':
                        if content['name'] == 'stdout':
                            outputs.append(content['text'])
                        elif content['name'] == 'stderr':
                            errors.append(content['text'])

                    elif msg_type == 'display_data':
                        if 'data' in content:
                            data = content['data']
                            if 'text/plain' in data:
                                outputs.append(data['text/plain'])
                            if 'image/png' in data:
                                images.append({
                                    'type': 'png',
                                    'data': data['image/png']
                                })
                            if 'text/html' in data:
                                html_output += data['text/html']

                    elif msg_type == 'execute_result':
                        if 'data' in content:
                            data = content['data']
                            if 'text/plain' in data:
                                outputs.append(data['text/plain'])

                    elif msg_type == 'error':
                        errors.extend(content['traceback'])

                    elif msg_type == 'status' and content['execution_state'] == 'idle':
                        break

                except Exception:
                    # No more messages, continue checking
                    continue

            # Wait for execution to complete
            reply = kc.get_shell_msg(timeout=timeout)
            if reply['content']['status'] == 'error':
                errors.extend(reply['content']['traceback'])

            execution_time = (datetime.now() - start_time).total_seconds()

            # Update session activity
            session.last_activity = datetime.now()
            session.execution_count += 1

            success = len(errors) == 0
            result = ExecutionResult(
                success=success,
                output="\n".join(outputs),
                error="\n".join(errors),
                execution_time=execution_time,
                kernel_type=session.kernel_type,
                images=images,
                html_output=html_output
            )

            logger.info(f"✅ Code executed in {execution_time:.2f}s, success: {success}")
            return result

        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"❌ Code execution failed: {e}")
            return ExecutionResult(
                success=False,
                error=str(e),
                execution_time=execution_time,
                kernel_type=session.kernel_type
            )

    def shutdown_session(self, session_id: str):
        """Shutdown a kernel session"""
        if session_id not in self.sessions:
            return

        session = self.sessions[session_id]

        try:
            if session.kernel_client:
                session.kernel_client.stop_channels()
            if session.kernel_manager:
                session.kernel_manager.shutdown_kernel()

            session.status = "shutdown"
            logger.info(f"✅ Shutdown kernel session: {session_id}")

        except Exception as e:
            logger.error(f"❌ Error shutting down session {session_id}: {e}")
        finally:
            del self.sessions[session_id]

    def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """Get information about a session"""
        if session_id not in self.sessions:
            return None

        session = self.sessions[session_id]
        return {
            'session_id': session.session_id,
            'kernel_type': session.kernel_type,
            'status': session.status,
            'created_at': session.created_at.isoformat(),
            'last_activity': session.last_activity.isoformat(),
            'execution_count': session.execution_count
        }

    def list_sessions(self) -> List[Dict[str, Any]]:
        """List all active sessions"""
        return [self.get_session_info(sid) for sid in self.sessions.keys()]

    def _cleanup_idle_sessions(self, max_idle_minutes: int = 30):
        """Clean up idle sessions"""
        now = datetime.now()
        to_remove = []

        for session_id, session in self.sessions.items():
            idle_time = now - session.last_activity
            if idle_time.total_seconds() > max_idle_minutes * 60:
                to_remove.append(session_id)

        for session_id in to_remove:
            logger.info(f"🧹 Cleaning up idle session: {session_id}")
            self.shutdown_session(session_id)

class JuliaKernelManager:
    """Manages Julia kernel for code execution"""

    def __init__(self):
        self.julia_instance = None
        self.initialized = False

        if JULIA_AVAILABLE:
            try:
                self.julia_instance = Julia(compiled_modules=False)
                self.initialized = True
                logger.info("✅ Julia kernel initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Julia: {e}")
        else:
            logger.warning("⚠️ Julia not available for kernel execution")

    def execute_code(self, code: str, timeout: int = 30) -> ExecutionResult:
        """Execute Julia code"""
        if not self.initialized:
            return ExecutionResult(
                success=False,
                error="Julia kernel not initialized",
                kernel_type="julia"
            )

        start_time = datetime.now()

        try:
            # Execute Julia code
            result = self.julia_instance.eval(code)

            execution_time = (datetime.now() - start_time).total_seconds()

            return ExecutionResult(
                success=True,
                output=str(result),
                execution_time=execution_time,
                kernel_type="julia",
                result_data=result
            )

        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            return ExecutionResult(
                success=False,
                error=str(e),
                execution_time=execution_time,
                kernel_type="julia"
            )

class CodeExecutionEngine:
    """Unified code execution engine for Python and Julia"""

    def __init__(self):
        self.jupyter_manager = JupyterKernelManager()
        self.julia_manager = JuliaKernelManager()
        self.active_sessions: Dict[str, str] = {}  # user_id -> session_id

        logger.info("🚀 Code Execution Engine initialized")

    def create_session(self, kernel_type: str = "python", user_id: str = None) -> str:
        """Create a new execution session"""
        session_id = self.jupyter_manager.create_session(kernel_type)

        if user_id:
            # Clean up existing session for user
            if user_id in self.active_sessions:
                old_session = self.active_sessions[user_id]
                self.jupyter_manager.shutdown_session(old_session)

            self.active_sessions[user_id] = session_id

        return session_id

    def execute_code(self, code: str, kernel_type: str = "python",
                    session_id: str = None, user_id: str = None,
                    timeout: int = 30) -> ExecutionResult:
        """Execute code using appropriate kernel"""

        # Handle Julia execution separately
        if kernel_type == "julia":
            return self.julia_manager.execute_code(code, timeout)

        # Handle Python execution via Jupyter
        if not session_id:
            if user_id and user_id in self.active_sessions:
                session_id = self.active_sessions[user_id]
            else:
                # Create new session
                session_id = self.create_session(kernel_type, user_id)

        return self.jupyter_manager.execute_code(session_id, code, timeout)

    def execute_batch(self, code_blocks: List[str], kernel_type: str = "python",
                     user_id: str = None) -> List[ExecutionResult]:
        """Execute multiple code blocks"""
        results = []

        for code in code_blocks:
            result = self.execute_code(code, kernel_type, user_id=user_id)
            results.append(result)

            # Stop on first error
            if not result.success:
                break

        return results

    async def execute_async(self, code: str, kernel_type: str = "python",
                           session_id: str = None, user_id: str = None) -> ExecutionResult:
        """Execute code asynchronously"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.execute_code,
            code,
            kernel_type,
            session_id,
            user_id
        )

    def cleanup_user_sessions(self, user_id: str):
        """Clean up all sessions for a user"""
        if user_id in self.active_sessions:
            session_id = self.active_sessions[user_id]
            self.jupyter_manager.shutdown_session(session_id)
            del self.active_sessions[user_id]

    def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """Get session information"""
        return self.jupyter_manager.get_session_info(session_id)

    def list_sessions(self) -> List[Dict[str, Any]]:
        """List all active sessions"""
        return self.jupyter_manager.list_sessions()

    def shutdown_all_sessions(self):
        """Shutdown all active sessions"""
        for session_id in list(self.active_sessions.values()):
            self.jupyter_manager.shutdown_session(session_id)
        self.active_sessions.clear()

        logger.info("✅ All sessions shutdown")

# Global execution engine instance
execution_engine = CodeExecutionEngine()

def get_execution_engine() -> CodeExecutionEngine:
    """Get the global execution engine instance"""
    return execution_engine

def execute_python_code(code: str, session_id: str = None, user_id: str = None) -> ExecutionResult:
    """Execute Python code"""
    return execution_engine.execute_code(code, "python", session_id, user_id)

def execute_julia_code(code: str) -> ExecutionResult:
    """Execute Julia code"""
    return execution_engine.execute_code(code, "julia")

def create_execution_session(kernel_type: str = "python", user_id: str = None) -> str:
    """Create a new execution session"""
    return execution_engine.create_session(kernel_type, user_id)

def test_jupyter_integration():
    """Test Jupyter integration functionality"""
    print("🧪 Testing Jupyter Integration")
    print("=" * 50)

    tests = [
        ("Python Code Execution", test_python_execution),
        ("Julia Code Execution", test_julia_execution),
        ("Session Management", test_session_management),
        ("Batch Execution", test_batch_execution)
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\\n🧪 Running {test_name}...")
        try:
            result = test_func()
            results.append((test_name, result))
            print(f"✅ {test_name}: {'PASSED' if result else 'FAILED'}")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
            results.append((test_name, False))

    print("\\n📊 Test Results Summary:")
    print("-" * 30)
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_name:25} {status}")

    passed_count = sum(results)
    total_count = len(results)

    print(f"\\n📈 Overall: {passed_count}/{total_count} Jupyter integration tests passed")

    return passed_count == total_count

def test_python_execution():
    """Test Python code execution"""
    code = """
print("Hello from Python kernel!")
x = 2 + 3
print(f"2 + 3 = {x}")
import sys
print(f"Python version: {sys.version}")
"""
    result = execute_python_code(code)
    return result.success and "Hello from Python kernel!" in result.output

def test_julia_execution():
    """Test Julia code execution"""
    if not JULIA_AVAILABLE:
        print("⚠️ Julia not available, skipping test")
        return True

    code = """
println("Hello from Julia kernel!")
x = 2 + 3
println("2 + 3 = ", x)
"""
    result = execute_julia_code(code)
    return result.success and "Hello from Julia kernel!" in result.output

def test_session_management():
    """Test session management"""
    session_id = create_execution_session("python", "test_user")

    if not session_id:
        return False

    # Execute code in session
    result = execute_python_code("print('Session test')", session_id=session_id)
    if not result.success:
        return False

    # Get session info
    info = execution_engine.get_session_info(session_id)
    if not info or info['status'] != 'running':
        return False

    # Clean up
    execution_engine.cleanup_user_sessions("test_user")
    return True

def test_batch_execution():
    """Test batch code execution"""
    codes = [
        "print('Batch test 1')",
        "x = 10",
        "print(f'x = {x}')",
        "print('Batch test completed')"
    ]

    results = execution_engine.execute_batch(codes, "python")
    return len(results) == 4 and all(r.success for r in results)

if __name__ == '__main__':
    # CLI interface for Jupyter integration
    import argparse

    parser = argparse.ArgumentParser(description='Jupyter Client Integration CLI')
    parser.add_argument('action', choices=['test', 'execute', 'session'],
                       help='Action to perform')
    parser.add_argument('--code', '-c', help='Code to execute')
    parser.add_argument('--kernel', '-k', choices=['python', 'julia'],
                       default='python', help='Kernel type')
    parser.add_argument('--timeout', '-t', type=int, default=30,
                       help='Execution timeout in seconds')

    args = parser.parse_args()

    if args.action == 'test':
        success = test_jupyter_integration()
        sys.exit(0 if success else 1)

    elif args.action == 'execute':
        if not args.code:
            print("❌ Code is required for execution")
            sys.exit(1)

        print(f"🔧 Executing {args.kernel} code...")
        result = execution_engine.execute_code(args.code, args.kernel, timeout=args.timeout)

        print("📊 Execution Result:")
        print(f"Success: {result.success}")
        print(f"Execution Time: {result.execution_time:.2f}s")
        print(f"Kernel: {result.kernel_type}")

        if result.output:
            print("\\n📤 Output:")
            print(result.output)

        if result.error:
            print("\\n❌ Error:")
            print(result.error)

        if result.images:
            print(f"\\n🖼️ Generated {len(result.images)} images")

        if result.html_output:
            print("\\n🌐 HTML Output:")
            print(result.html_output)

    elif args.action == 'session':
        print("🔧 Creating new session...")
        session_id = execution_engine.create_session(args.kernel)
        print(f"✅ Created session: {session_id}")

        info = execution_engine.get_session_info(session_id)
        print(f"📊 Session Info: {json.dumps(info, indent=2)}")

    else:
        parser.print_help()
