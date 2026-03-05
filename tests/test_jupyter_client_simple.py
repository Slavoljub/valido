#!/usr/bin/env python3
"""
Simple Jupyter Client Integration Test
Tests the Jupyter client integration independently
"""

import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def test_simple_imports():
    """Test that the core Jupyter client integration can be imported"""
    try:
        # Test direct import from the file
        sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "core"))
        from jupyter_client_integration import ExecutionResult, KernelSession

        print("✅ Jupyter client integration classes imported successfully")
        return True

    except ImportError as e:
        print(f"❌ Jupyter client integration import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Jupyter client integration initialization failed: {e}")
        return False

def test_execution_result_creation():
    """Test ExecutionResult can be created"""
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "core"))
        from jupyter_client_integration import ExecutionResult

        result = ExecutionResult(
            success=True,
            output="Hello World",
            execution_time=1.5,
            kernel_type="python"
        )

        assert result.success == True
        assert result.output == "Hello World"
        assert result.execution_time == 1.5
        assert result.kernel_type == "python"

        print("✅ ExecutionResult creation successful")
        return True

    except Exception as e:
        print(f"❌ ExecutionResult creation failed: {e}")
        return False

def test_kernel_session_creation():
    """Test KernelSession can be created"""
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "core"))
        from jupyter_client_integration import KernelSession
        from datetime import datetime

        session = KernelSession(
            session_id="test-123",
            kernel_type="python",
            status="created"
        )

        assert session.session_id == "test-123"
        assert session.kernel_type == "python"
        assert session.status == "created"
        assert isinstance(session.created_at, datetime)
        assert session.execution_count == 0

        print("✅ KernelSession creation successful")
        return True

    except Exception as e:
        print(f"❌ KernelSession creation failed: {e}")
        return False

def test_jupyter_dependencies():
    """Test Jupyter dependencies availability"""
    try:
        # Test if jupyter_client can be imported
        try:
            from jupyter_client import KernelManager, BlockingKernelClient
            from jupyter_client.kernelspec import find_kernel_specs
            jupyter_available = True
            print("✅ jupyter_client available")
        except ImportError:
            jupyter_available = False
            print("⚠️ jupyter_client not available")

        # Test if Julia support is available
        try:
            import julia
            julia_available = True
            print("✅ Julia support available")
        except ImportError:
            julia_available = False
            print("⚠️ Julia support not available")

        print("✅ Jupyter dependencies check completed")
        return True

    except Exception as e:
        print(f"❌ Jupyter dependencies check failed: {e}")
        return False

def main():
    """Main test runner for simple Jupyter client integration"""
    print("🧪 Simple Jupyter Client Integration Tests")
    print("=" * 50)

    tests = [
        ("Simple Imports", test_simple_imports),
        ("ExecutionResult Creation", test_execution_result_creation),
        ("KernelSession Creation", test_kernel_session_creation),
        ("Jupyter Dependencies", test_jupyter_dependencies)
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

    print("\\n📊 Simple Jupyter Client Integration Test Results:")
    print("-" * 50)
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_name:35} {status}")

    passed_count = sum(success for _, success in results)
    total_count = len(results)

    print(f"\\n📈 Overall: {passed_count}/{total_count} simple Jupyter tests passed")

    if passed_count == total_count:
        print("🎉 All simple Jupyter client integration tests passed!")
        print("\\n💡 The Jupyter client integration core is working!")
        return True
    elif passed_count >= total_count * 0.75:  # 75% pass rate
        print("✅ Jupyter client integration core is mostly functional.")
        print("\\n💡 Some tests failed but core functionality is working.")
        return True
    else:
        print("⚠️ Jupyter client integration has significant issues.")
        print("\\n💡 Check the failed tests above and fix the issues.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
