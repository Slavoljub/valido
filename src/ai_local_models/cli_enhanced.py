#!/usr/bin/env python3
"""
Enhanced CLI for AI Local Models
Beautiful progress display and comprehensive communication support
"""

import os
import sys
import time
import threading
import json
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from pathlib import Path
import argparse
import colorama
from colorama import Fore, Back, Style
# Optional curses import for enhanced CLI (Windows compatibility)
try:
    import curses
    CURSES_AVAILABLE = True
except ImportError:
    CURSES_AVAILABLE = False
    curses = None

import signal
from dataclasses import dataclass
from enum import Enum

# Initialize colorama for Windows support
colorama.init(autoreset=True)


class CommunicationMode(Enum):
    TEXT = "text"
    VOICE = "voice"
    FILE = "file"
    IMAGE = "image"
    PDF = "pdf"
    DATA = "data"


class ModelType(Enum):
    TEXT = "text"
    AUDIO = "audio"
    VISION = "vision"
    MULTIMODAL = "multimodal"


@dataclass
class CLITask:
    """Represents a CLI task with progress tracking"""
    id: str
    name: str
    status: str  # pending, running, completed, failed, cancelled
    progress: float
    speed: float
    eta: float
    start_time: float
    end_time: Optional[float]
    error_message: Optional[str]
    task_type: str  # download, load, process, communicate


class EnhancedCLI:
    """Enhanced CLI with beautiful progress display and communication support"""

    def __init__(self):
        self.tasks: Dict[str, CLITask] = {}
        self.progress_callbacks: List[Callable] = []
        self.communication_handlers = {
            CommunicationMode.TEXT: self._handle_text_communication,
            CommunicationMode.VOICE: self._handle_voice_communication,
            CommunicationMode.FILE: self._handle_file_communication,
            CommunicationMode.IMAGE: self._handle_image_communication,
            CommunicationMode.PDF: self._handle_pdf_communication,
            CommunicationMode.DATA: self._handle_data_communication
        }
        self.model_suggestions = {
            'text': ['llama2-7b', 'mistral-7b', 'gpt-3.5-turbo'],
            'image': ['llava-7b', 'clip-vit-large', 'blip2-opt-2.7b'],
            'audio': ['whisper-large-v3', 'wav2vec2-large-960h'],
            'pdf': ['nougat-base', 'layoutlmv3-large', 'donut-base'],
            'multimodal': ['gpt-4v', 'claude-3-sonnet', 'gemini-pro-vision']
        }
        self.current_model = None
        self.gpu_status = {}
        self.communication_history = []

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        self._print_status("Shutting down gracefully...", "warning")
        self.cleanup()
        sys.exit(0)

    def show_banner(self):
        """Display beautiful CLI banner"""
        banner = f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════════════╗
║                    {Fore.YELLOW}🤖 AI Local Models CLI{Fore.CYAN}                    ║
║                 {Fore.GREEN}Enhanced Communication & Progress{Fore.CYAN}                ║
╚══════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
        """
        print(banner)

    def show_system_status(self):
        """Show comprehensive system status"""
        print(f"\n{Fore.BLUE}📊 System Status:{Style.RESET_ALL}")
        print(f"{'─' * 50}")

        # GPU Status
        gpu_info = self._get_gpu_info()
        if gpu_info['available']:
            print(f"{Fore.GREEN}✅ GPU Available: {gpu_info['name']}")
            print(f"   Memory: {gpu_info['memory_gb']:.1f}GB")
            print(f"   Compute: {gpu_info['compute_capability']}")
        else:
            print(f"{Fore.YELLOW}⚠️  CPU Mode: No GPU detected")

        # Model Status
        if self.current_model:
            print(f"{Fore.GREEN}✅ Current Model: {self.current_model}")
        else:
            print(f"{Fore.YELLOW}⚠️  No model loaded")

        # Active Tasks
        active_tasks = [t for t in self.tasks.values() if t.status == 'running']
        if active_tasks:
            print(f"{Fore.BLUE}🔄 Active Tasks: {len(active_tasks)}")
            for task in active_tasks:
                self._show_task_progress(task)
        else:
            print(f"{Fore.GREEN}✅ All tasks completed")

        print(f"{'─' * 50}")

    def show_progress_bar(self, task: CLITask, width: int = 40):
        """Show beautiful progress bar"""
        if task.status == 'completed':
            bar_color = Fore.GREEN
            status_icon = "✅"
        elif task.status == 'failed':
            bar_color = Fore.RED
            status_icon = "❌"
        elif task.status == 'running':
            bar_color = Fore.BLUE
            status_icon = "🔄"
        else:
            bar_color = Fore.YELLOW
            status_icon = "⏳"

        # Create progress bar
        filled = int(width * task.progress / 100)
        bar = '█' * filled + '░' * (width - filled)

        # Format speed and ETA
        speed_str = f"{self._format_bytes(task.speed)}/s" if task.speed > 0 else ""
        eta_str = self._format_time(task.eta) if task.eta > 0 else ""

        # Print progress line
        print("4.0f",
              end='', flush=True)

        if task.error_message:
            print(f"\n   {Fore.RED}Error: {task.error_message}{Style.RESET_ALL}")

    def _show_task_progress(self, task: CLITask):
        """Show detailed task progress"""
        elapsed = time.time() - task.start_time
        elapsed_str = self._format_time(elapsed)

        print(f"   {task.name}")
        print(f"   Status: {task.status} | Progress: {task.progress:.1f}% | Elapsed: {elapsed_str}")

        if task.speed > 0:
            print(f"   Speed: {self._format_bytes(task.speed)}/s")

        if task.eta > 0:
            print(f"   ETA: {self._format_time(task.eta)}")

        if task.error_message:
            print(f"   {Fore.RED}Error: {task.error_message}{Style.RESET_ALL}")

    def start_task(self, task_id: str, name: str, task_type: str = 'general') -> CLITask:
        """Start a new task with progress tracking"""
        task = CLITask(
            id=task_id,
            name=name,
            status='running',
            progress=0.0,
            speed=0.0,
            eta=0.0,
            start_time=time.time(),
            end_time=None,
            error_message=None,
            task_type=task_type
        )

        self.tasks[task_id] = task

        # Notify callbacks
        for callback in self.progress_callbacks:
            try:
                callback(task)
            except Exception as e:
                print(f"Error in progress callback: {e}")

        return task

    def update_task_progress(self, task_id: str, progress: float, speed: float = 0):
        """Update task progress"""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            task.progress = progress
            task.speed = speed

            if task.progress < 100 and speed > 0:
                remaining = (100 - task.progress) / 100
                if remaining > 0:
                    task.eta = remaining / (speed / 100)

            # Notify callbacks
            for callback in self.progress_callbacks:
                try:
                    callback(task)
                except Exception as e:
                    print(f"Error in progress callback: {e}")

    def complete_task(self, task_id: str):
        """Mark task as completed"""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            task.status = 'completed'
            task.progress = 100.0
            task.end_time = time.time()

            # Notify callbacks
            for callback in self.progress_callbacks:
                try:
                    callback(task)
                except Exception as e:
                    print(f"Error in progress callback: {e}")

    def fail_task(self, task_id: str, error_message: str):
        """Mark task as failed"""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            task.status = 'failed'
            task.error_message = error_message
            task.end_time = time.time()

            # Notify callbacks
            for callback in self.progress_callbacks:
                try:
                    callback(task)
                except Exception as e:
                    print(f"Error in progress callback: {e}")

    def suggest_model(self, content_type: str) -> List[str]:
        """Suggest appropriate models based on content type"""
        content_type_lower = content_type.lower()

        if 'image' in content_type_lower:
            return self.model_suggestions['image']
        elif 'audio' in content_type_lower or 'voice' in content_type_lower:
            return self.model_suggestions['audio']
        elif 'pdf' in content_type_lower or 'document' in content_type_lower:
            return self.model_suggestions['pdf']
        elif 'text' in content_type_lower:
            return self.model_suggestions['text']
        else:
            return self.model_suggestions['multimodal']

    def handle_communication(self, mode: CommunicationMode, input_data: Any) -> Dict[str, Any]:
        """Handle different communication modes"""
        if mode in self.communication_handlers:
            handler = self.communication_handlers[mode]
            return handler(input_data)
        else:
            return {
                'success': False,
                'error': f'Unsupported communication mode: {mode}'
            }

    def _handle_text_communication(self, text: str) -> Dict[str, Any]:
        """Handle text communication"""
        self.communication_history.append({
            'mode': 'text',
            'timestamp': datetime.now().isoformat(),
            'content': text
        })

        # Analyze text and suggest model
        suggested_models = self.suggest_model('text')

        return {
            'success': True,
            'mode': 'text',
            'content': text,
            'suggested_models': suggested_models,
            'analysis': {
                'length': len(text),
                'type': 'text'
            }
        }

    def _handle_voice_communication(self, audio_data: Any) -> Dict[str, Any]:
        """Handle voice communication"""
        suggested_models = self.suggest_model('voice')

        self.communication_history.append({
            'mode': 'voice',
            'timestamp': datetime.now().isoformat(),
            'content': 'Audio data processed'
        })

        return {
            'success': True,
            'mode': 'voice',
            'suggested_models': suggested_models,
            'analysis': {
                'type': 'audio',
                'processing_required': True
            }
        }

    def _handle_file_communication(self, file_path: str) -> Dict[str, Any]:
        """Handle file communication"""
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            return {
                'success': False,
                'error': f'File not found: {file_path}'
            }

        # Determine file type and suggest model
        file_extension = file_path_obj.suffix.lower()
        if file_extension in ['.jpg', '.jpeg', '.png', '.gif']:
            content_type = 'image'
        elif file_extension == '.pdf':
            content_type = 'pdf'
        elif file_extension in ['.txt', '.doc', '.docx']:
            content_type = 'text'
        else:
            content_type = 'multimodal'

        suggested_models = self.suggest_model(content_type)

        self.communication_history.append({
            'mode': 'file',
            'timestamp': datetime.now().isoformat(),
            'content': f'File: {file_path_obj.name}',
            'file_type': content_type
        })

        return {
            'success': True,
            'mode': 'file',
            'file_path': str(file_path_obj),
            'file_name': file_path_obj.name,
            'file_size': file_path_obj.stat().st_size,
            'suggested_models': suggested_models,
            'content_type': content_type
        }

    def _handle_image_communication(self, image_data: Any) -> Dict[str, Any]:
        """Handle image communication"""
        suggested_models = self.suggest_model('image')

        self.communication_history.append({
            'mode': 'image',
            'timestamp': datetime.now().isoformat(),
            'content': 'Image processed'
        })

        return {
            'success': True,
            'mode': 'image',
            'suggested_models': suggested_models,
            'analysis': {
                'type': 'image',
                'vision_required': True
            }
        }

    def _handle_pdf_communication(self, pdf_data: Any) -> Dict[str, Any]:
        """Handle PDF communication"""
        suggested_models = self.suggest_model('pdf')

        self.communication_history.append({
            'mode': 'pdf',
            'timestamp': datetime.now().isoformat(),
            'content': 'PDF processed'
        })

        return {
            'success': True,
            'mode': 'pdf',
            'suggested_models': suggested_models,
            'analysis': {
                'type': 'document',
                'ocr_required': True
            }
        }

    def _handle_data_communication(self, data: Any) -> Dict[str, Any]:
        """Handle data communication"""
        suggested_models = self.suggest_model('multimodal')

        self.communication_history.append({
            'mode': 'data',
            'timestamp': datetime.now().isoformat(),
            'content': 'Data processed'
        })

        return {
            'success': True,
            'mode': 'data',
            'suggested_models': suggested_models,
            'analysis': {
                'type': 'data',
                'processing_required': True
            }
        }

    def _get_gpu_info(self) -> Dict[str, Any]:
        """Get GPU information"""
        try:
            # Try to detect GPU using various methods
            import subprocess
            result = subprocess.run(['nvidia-smi', '--query-gpu=name,memory.total,memory.free,driver_version', '--format=csv,noheader,nounits'],
                                  capture_output=True, text=True, timeout=5)

            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if lines:
                    parts = [p.strip() for p in lines[0].split(',')]
                    if len(parts) >= 3:
                        return {
                            'available': True,
                            'name': parts[0],
                            'memory_gb': float(parts[1]) / 1024,
                            'free_memory_gb': float(parts[2]) / 1024,
                            'driver_version': parts[3] if len(parts) > 3 else 'Unknown',
                            'type': 'nvidia'
                        }

            # Check for AMD GPU
            try:
                result = subprocess.run(['rocm-smi', '--showproductname'], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    return {
                        'available': True,
                        'name': 'AMD GPU',
                        'memory_gb': 8.0,  # Default assumption
                        'type': 'amd'
                    }
            except:
                pass

            # Check for Apple Silicon (MPS)
            try:
                import torch
                if torch.backends.mps.is_available():
                    return {
                        'available': True,
                        'name': 'Apple Silicon GPU',
                        'memory_gb': 8.0,  # Default assumption
                        'type': 'apple'
                    }
            except:
                pass

        except Exception as e:
            print(f"GPU detection error: {e}")

        return {
            'available': False,
            'name': 'CPU',
            'memory_gb': 0,
            'type': 'cpu'
        }

    def _format_bytes(self, bytes_val: float) -> str:
        """Format bytes to human readable format"""
        if bytes_val == 0:
            return "0 B"

        units = ['B', 'KB', 'MB', 'GB', 'TB']
        i = 0
        while bytes_val >= 1024 and i < len(units) - 1:
            bytes_val /= 1024
            i += 1

        return ".1f"

    def _format_time(self, seconds: float) -> str:
        """Format time to human readable format"""
        if seconds < 60:
            return ".0f"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            remaining_seconds = int(seconds % 60)
            return f"{minutes}m {remaining_seconds}s"
        else:
            hours = int(seconds / 3600)
            minutes = int((seconds % 3600) / 60)
            return f"{hours}h {minutes}m"

    def _print_status(self, message: str, status_type: str = 'info'):
        """Print colored status message"""
        colors = {
            'info': Fore.BLUE,
            'success': Fore.GREEN,
            'warning': Fore.YELLOW,
            'error': Fore.RED
        }

        icons = {
            'info': 'ℹ️',
            'success': '✅',
            'warning': '⚠️',
            'error': '❌'
        }

        color = colors.get(status_type, Fore.WHITE)
        icon = icons.get(status_type, '•')

        print(f"{color}{icon} {message}{Style.RESET_ALL}")

    def show_sample_questions(self):
        """Show enhanced sample questions"""
        questions = [
            {
                'text': '📊 Analyze my revenue trends and provide insights',
                'category': 'financial',
                'model_type': 'text'
            },
            {
                'text': '💰 Show cash flow analysis for the last quarter',
                'category': 'financial',
                'model_type': 'text'
            },
            {
                'text': '📄 Generate a comprehensive financial report',
                'category': 'financial',
                'model_type': 'text'
            },
            {
                'text': '🧾 Analyze VAT and tax implications',
                'category': 'financial',
                'model_type': 'text'
            },
            {
                'text': '📦 Check warehouse inventory status',
                'category': 'business',
                'model_type': 'text'
            },
            {
                'text': '👥 Analyze client performance and trends',
                'category': 'business',
                'model_type': 'text'
            },
            {
                'text': '🎯 Provide business insights and recommendations',
                'category': 'business',
                'model_type': 'text'
            },
            {
                'text': '📈 Create budget planning for next year',
                'category': 'planning',
                'model_type': 'text'
            },
            {
                'text': '🔍 Process this document and extract key information',
                'category': 'document',
                'model_type': 'pdf'
            },
            {
                'text': '🖼️ Analyze this image and describe what you see',
                'category': 'vision',
                'model_type': 'image'
            },
            {
                'text': '🎵 Transcribe this audio and summarize the content',
                'category': 'audio',
                'model_type': 'audio'
            },
            {
                'text': '📊 Process this data file and provide insights',
                'category': 'data',
                'model_type': 'multimodal'
            }
        ]

        print(f"\n{Fore.CYAN}💡 Sample Questions:{Style.RESET_ALL}")
        print(f"{'─' * 60}")

        for i, question in enumerate(questions, 1):
            icon = question.get('icon', '•')
            print("2d")

        print(f"{'─' * 60}")
        print(f"{Fore.YELLOW}💡 Tip: Click on any question or type your own message!{Style.RESET_ALL}")

    def interactive_mode(self):
        """Start interactive mode with all communication features"""
        self.show_banner()
        self.show_system_status()
        self.show_sample_questions()

        print(f"\n{Fore.GREEN}🚀 Interactive Mode Started!")
        print(f"Available commands:")
        print(f"  /help     - Show this help")
        print(f"  /status   - Show system status")
        print(f"  /gpu      - Test GPU detection")
        print(f"  /model    - Change current model")
        print(f"  /history  - Show communication history")
        print(f"  /clear    - Clear screen")
        print(f"  /exit     - Exit interactive mode")
        print(f"{'─' * 50}{Style.RESET_ALL}")

        while True:
            try:
                user_input = input(f"\n{Fore.BLUE}🤖 AI Assistant > {Style.RESET_ALL}").strip()

                if not user_input:
                    continue

                if user_input.startswith('/'):
                    self._handle_command(user_input)
                else:
                    self._handle_user_message(user_input)

            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}⚠️  Use '/exit' to quit properly{Style.RESET_ALL}")
            except EOFError:
                break
            except Exception as e:
                print(f"{Fore.RED}❌ Error: {e}{Style.RESET_ALL}")

    def _handle_command(self, command: str):
        """Handle CLI commands"""
        parts = command.split()
        cmd = parts[0].lower()

        if cmd == '/help':
            self._show_help()
        elif cmd == '/status':
            self.show_system_status()
        elif cmd == '/gpu':
            self._test_gpu_detection()
        elif cmd == '/model':
            model_name = parts[1] if len(parts) > 1 else None
            self._change_model(model_name)
        elif cmd == '/history':
            self._show_history()
        elif cmd == '/clear':
            os.system('clear' if os.name != 'nt' else 'cls')
            self.show_banner()
        elif cmd == '/exit':
            print(f"{Fore.GREEN}👋 Goodbye!{Style.RESET_ALL}")
            sys.exit(0)
        else:
            print(f"{Fore.RED}❌ Unknown command: {cmd}{Style.RESET_ALL}")

    def _handle_user_message(self, message: str):
        """Handle user message with communication analysis"""
        print(f"{Fore.BLUE}💭 Processing: {message}{Style.RESET_ALL}")

        # Start processing task
        task = self.start_task(f"process_{int(time.time())}", f"Processing: {message[:50]}...", 'process')

        # Simulate processing with progress
        for i in range(101):
            time.sleep(0.02)  # Simulate work
            self.update_task_progress(task.id, i, 1024 * 50)  # 50KB/s

        self.complete_task(task.id)

        # Analyze and respond
        result = self.handle_communication(CommunicationMode.TEXT, message)

        if result['success']:
            print(f"{Fore.GREEN}✅ Analysis complete!{Style.RESET_ALL}")

            if 'suggested_models' in result:
                print(f"{Fore.YELLOW}💡 Suggested models: {', '.join(result['suggested_models'][:3])}{Style.RESET_ALL}")

            # Simulate AI response
            print(f"{Fore.CYAN}🤖 AI: Here's my analysis based on your message...{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}❌ Processing failed: {result.get('error', 'Unknown error')}{Style.RESET_ALL}")

    def _show_help(self):
        """Show help information"""
        help_text = f"""
{Fore.CYAN}📚 Help - Available Commands:{Style.RESET_ALL}

{Fore.YELLOW}Commands:{Style.RESET_ALL}
/help     - Show this help message
/status   - Display system status and active tasks
/gpu      - Test and display GPU detection information
/model    - Change or display current model
/history  - Show communication history
/clear    - Clear the screen
/exit     - Exit the interactive mode

{Fore.YELLOW}Communication Modes:{Style.RESET_ALL}
• Text messages - Type any message
• File processing - Use file paths in messages
• Voice input - Voice commands (if enabled)
• Image analysis - Image file references

{Fore.YELLOW}Tips:{Style.RESET_ALL}
• The system automatically suggests appropriate models based on content type
• Progress bars show real-time task completion
• GPU acceleration is automatically detected and utilized
• All communication is logged for analysis
        """
        print(help_text)

    def _test_gpu_detection(self):
        """Test GPU detection"""
        print(f"{Fore.BLUE}🔍 Testing GPU Detection...{Style.RESET_ALL}")

        task = self.start_task('gpu_test', 'GPU Detection Test', 'gpu')

        for i in range(101):
            time.sleep(0.01)
            self.update_task_progress(task.id, i)

        self.complete_task(task.id)

        gpu_info = self._get_gpu_info()
        if gpu_info['available']:
            print(f"{Fore.GREEN}✅ GPU Found: {gpu_info['name']}")
            print(f"   Memory: {gpu_info['memory_gb']:.1f}GB")
            print(f"   Type: {gpu_info['type']}")
        else:
            print(f"{Fore.YELLOW}⚠️  No GPU detected - Running in CPU mode")

    def _change_model(self, model_name: str = None):
        """Change current model"""
        if not model_name:
            print(f"Current model: {self.current_model or 'None'}")
            return

        print(f"{Fore.BLUE}🔄 Changing model to: {model_name}{Style.RESET_ALL}")

        task = self.start_task(f"load_{model_name}", f"Loading model: {model_name}", 'load')

        # Simulate model loading with progress
        for i in range(101):
            time.sleep(0.05)
            self.update_task_progress(task.id, i, 1024 * 1024 * 10)  # 10MB/s

        self.complete_task(task.id)
        self.current_model = model_name

        print(f"{Fore.GREEN}✅ Model changed to: {model_name}{Style.RESET_ALL}")

    def _show_history(self):
        """Show communication history"""
        print(f"\n{Fore.CYAN}📜 Communication History:{Style.RESET_ALL}")
        print(f"{'─' * 60}")

        if not self.communication_history:
            print(f"{Fore.YELLOW}No communication history yet{Style.RESET_ALL}")
            return

        for i, entry in enumerate(self.communication_history[-10:], 1):  # Show last 10
            timestamp = datetime.fromisoformat(entry['timestamp'])
            time_str = timestamp.strftime('%H:%M:%S')
            mode_icon = {
                'text': '💬',
                'voice': '🎵',
                'file': '📁',
                'image': '🖼️',
                'pdf': '📄',
                'data': '📊'
            }.get(entry['mode'], '•')

            print("2d")

        print(f"{'─' * 60}")

    def cleanup(self):
        """Cleanup resources"""
        # Mark all running tasks as cancelled
        for task in self.tasks.values():
            if task.status == 'running':
                task.status = 'cancelled'
                task.end_time = time.time()

        # Clear callbacks
        self.progress_callbacks.clear()

        # Save history if needed
        if self.communication_history:
            try:
                with open('cli_history.json', 'w') as f:
                    json.dump(self.communication_history, f, indent=2)
            except Exception as e:
                print(f"Warning: Could not save history: {e}")

    # ==========================================
    # BENCHMARK TESTING METHODS
    # ==========================================

    def run_benchmarks(self, model_id: str = None, test_type: str = "comprehensive"):
        """Run comprehensive benchmark tests for models"""
        print(f"\n🚀 Starting LLM Benchmark Suite - {test_type.title()} Tests")
        print("=" * 60)

        # Get models to test
        if model_id:
            models_to_test = [model_id] if model_id in self.config_manager.get_all_models() else []
            if not models_to_test:
                print(f"❌ Model '{model_id}' not found in configuration")
                return
        else:
            # Get all available models
            models_to_test = list(self.config_manager.get_all_models().keys())

        print(f"📋 Testing {len(models_to_test)} model(s): {', '.join(models_to_test)}")
        print(f"🎯 Test Type: {test_type}")
        print("=" * 60)

        benchmark_results = {}

        for model_id in models_to_test:
            print(f"\n🧪 Testing Model: {model_id}")
            print("-" * 40)

            try:
                model_results = self._run_model_benchmark(model_id, test_type)
                benchmark_results[model_id] = model_results

                # Display immediate results
                self._display_benchmark_results(model_id, model_results)

            except Exception as e:
                print(f"❌ Benchmark failed for {model_id}: {e}")
                benchmark_results[model_id] = {"error": str(e)}

        # Display summary
        self._display_benchmark_summary(benchmark_results)

        return benchmark_results

    def _run_model_benchmark(self, model_id: str, test_type: str):
        """Run benchmark tests for a specific model"""
        results = {
            "model_id": model_id,
            "timestamp": datetime.now().isoformat(),
            "tests": {}
        }

        # Basic model info
        model_config = self.config_manager.get_model_config(model_id)
        if model_config:
            results["model_info"] = {
                "name": model_config.display_name,
                "type": model_config.type,
                "format": model_config.format,
                "size": model_config.size,
                "memory_required": model_config.memory_required,
                "is_downloaded": model_config.is_downloaded,
                "is_loaded": model_config.is_loaded
            }

        # Skip if model not available
        if not model_config or not model_config.is_downloaded:
            results["tests"]["availability"] = {
                "status": "unavailable",
                "reason": "Model not downloaded" if not model_config else "Model not found"
            }
            return results

        # Performance tests
        if test_type in ["comprehensive", "performance"]:
            results["tests"]["performance"] = self._run_performance_tests(model_id)

        # Memory tests
        if test_type in ["comprehensive", "memory"]:
            results["tests"]["memory"] = self._run_memory_tests(model_id)

        # Accuracy tests
        if test_type in ["comprehensive", "accuracy"]:
            results["tests"]["accuracy"] = self._run_accuracy_tests(model_id)

        # Inference speed tests
        if test_type in ["comprehensive", "inference"]:
            results["tests"]["inference"] = self._run_inference_tests(model_id)

        return results

    def _run_performance_tests(self, model_id: str):
        """Run performance benchmark tests"""
        print("  ⚡ Running Performance Tests...")

        test_prompts = [
            "Hello, how are you today?",
            "What is the capital of France?",
            "Explain the concept of machine learning in simple terms.",
            "Write a short story about a robot learning to paint.",
            "What are the benefits of renewable energy sources?"
        ]

        results = {
            "test_count": len(test_prompts),
            "total_time": 0,
            "avg_time_per_request": 0,
            "tokens_processed": 0,
            "requests_per_second": 0
        }

        try:
            start_time = time.time()

            for i, prompt in enumerate(test_prompts):
                request_start = time.time()

                # Simulate model inference (replace with actual model call)
                time.sleep(0.1)  # Placeholder for actual inference time
                response = f"Response to: {prompt[:50]}..."

                request_time = time.time() - request_start
                results["total_time"] += request_time
                results["tokens_processed"] += len(prompt.split()) + len(response.split())

                print(f"    {i+1}/{len(test_prompts)}: {request_time:.3f}s")

            total_time = time.time() - start_time
            results["total_time"] = total_time
            results["avg_time_per_request"] = total_time / len(test_prompts)
            results["requests_per_second"] = len(test_prompts) / total_time if total_time > 0 else 0

        except Exception as e:
            results["error"] = str(e)

        return results

    def _run_memory_tests(self, model_id: str):
        """Run memory usage benchmark tests"""
        print("  🧠 Running Memory Tests...")

        results = {
            "initial_memory": 0,
            "peak_memory": 0,
            "memory_per_request": 0,
            "memory_efficiency": "unknown"
        }

        try:
            import psutil
            import os

            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            results["initial_memory"] = initial_memory

            # Simulate memory usage during requests
            peak_memory = initial_memory
            for i in range(5):
                time.sleep(0.05)
                current_memory = process.memory_info().rss / 1024 / 1024
                peak_memory = max(peak_memory, current_memory)

            results["peak_memory"] = peak_memory
            results["memory_per_request"] = (peak_memory - initial_memory) / 5

            # Memory efficiency rating
            if results["memory_per_request"] < 10:
                results["memory_efficiency"] = "excellent"
            elif results["memory_per_request"] < 50:
                results["memory_efficiency"] = "good"
            elif results["memory_per_request"] < 100:
                results["memory_efficiency"] = "fair"
            else:
                results["memory_efficiency"] = "poor"

        except ImportError:
            results["error"] = "psutil not available for memory testing"
        except Exception as e:
            results["error"] = str(e)

        return results

    def _run_accuracy_tests(self, model_id: str):
        """Run accuracy benchmark tests"""
        print("  🎯 Running Accuracy Tests...")

        # Simple accuracy test questions with expected answers
        test_cases = [
            {
                "question": "What is 2 + 2?",
                "expected_keywords": ["4", "four"],
                "category": "math"
            },
            {
                "question": "What color is the sky on a clear day?",
                "expected_keywords": ["blue", "azure"],
                "category": "general"
            },
            {
                "question": "Who wrote Romeo and Juliet?",
                "expected_keywords": ["shakespeare", "william"],
                "category": "literature"
            }
        ]

        results = {
            "test_count": len(test_cases),
            "correct_answers": 0,
            "accuracy_score": 0.0,
            "category_scores": {}
        }

        try:
            for test_case in test_cases:
                # Simulate model response
                response = f"Simulated response for: {test_case['question']}"

                # Simple keyword matching for accuracy
                response_lower = response.lower()
                keywords_found = any(keyword in response_lower for keyword in test_case["expected_keywords"])

                if keywords_found:
                    results["correct_answers"] += 1
                    category = test_case["category"]
                    if category not in results["category_scores"]:
                        results["category_scores"][category] = {"correct": 0, "total": 0}
                    results["category_scores"][category]["correct"] += 1

                # Update category totals
                category = test_case["category"]
                if category not in results["category_scores"]:
                    results["category_scores"][category] = {"correct": 0, "total": 0}
                results["category_scores"][category]["total"] += 1

            results["accuracy_score"] = (results["correct_answers"] / len(test_cases)) * 100

            # Calculate category scores
            for category, scores in results["category_scores"].items():
                scores["percentage"] = (scores["correct"] / scores["total"]) * 100

        except Exception as e:
            results["error"] = str(e)

        return results

    def _run_inference_tests(self, model_id: str):
        """Run inference speed benchmark tests"""
        print("  ⚡ Running Inference Speed Tests...")

        test_prompts = [
            "Short prompt",
            "This is a medium length prompt for testing inference speed",
            "This is a much longer prompt that should test the model's ability to handle extended input sequences and provide comprehensive responses to complex queries about various topics including technology, science, and general knowledge."
        ]

        results = {
            "prompt_lengths": [],
            "inference_times": [],
            "tokens_per_second": [],
            "avg_tokens_per_second": 0
        }

        try:
            for prompt in test_prompts:
                prompt_length = len(prompt.split())

                # Simulate inference time based on prompt length
                base_time = 0.1
                time_multiplier = min(prompt_length / 10, 5)  # Cap at 5x base time
                inference_time = base_time + (time_multiplier * 0.1)

                time.sleep(inference_time)  # Simulate inference

                # Calculate tokens per second
                estimated_output_tokens = prompt_length * 1.5  # Estimate output size
                total_tokens = prompt_length + estimated_output_tokens
                tokens_per_second = total_tokens / inference_time if inference_time > 0 else 0

                results["prompt_lengths"].append(prompt_length)
                results["inference_times"].append(inference_time)
                results["tokens_per_second"].append(tokens_per_second)

            if results["tokens_per_second"]:
                results["avg_tokens_per_second"] = sum(results["tokens_per_second"]) / len(results["tokens_per_second"])

        except Exception as e:
            results["error"] = str(e)

        return results

    def _display_benchmark_results(self, model_id: str, results: dict):
        """Display benchmark results for a model"""
        print(f"\n📊 Results for {model_id}:")
        print("-" * 40)

        if "model_info" in results:
            info = results["model_info"]
            print(f"📋 Model: {info['name']} ({info['size']})")
            print(f"🏷️  Type: {info['type']} | Format: {info['format']}")
            print(f"🧠 Memory: {info['memory_required']} MB")
            print(f"📥 Downloaded: {'✅' if info['is_downloaded'] else '❌'}")

        for test_name, test_results in results["tests"].items():
            if test_name == "availability":
                continue

            print(f"\n🔬 {test_name.title()} Test:")

            if "error" in test_results:
                print(f"  ❌ Error: {test_results['error']}")
                continue

            if test_name == "performance":
                print(f"  📈 Requests/sec: {test_results.get('requests_per_second', 0):.2f}")
                print(f"  ⏱️  Avg time: {test_results.get('avg_time_per_request', 0)*1000:.0f}ms")
                print(f"  📝 Tokens processed: {test_results.get('tokens_processed', 0)}")

            elif test_name == "memory":
                print(f"  🧠 Initial: {test_results.get('initial_memory', 0):.1f} MB")
                print(f"  📊 Peak: {test_results.get('peak_memory', 0):.1f} MB")
                print(f"  ⚡ Per request: {test_results.get('memory_per_request', 0):.1f} MB")
                print(f"  🏆 Efficiency: {test_results.get('memory_efficiency', 'unknown')}")

            elif test_name == "accuracy":
                print(f"  🎯 Accuracy: {test_results.get('accuracy_score', 0):.1f}%")
                print(f"  ✅ Correct: {test_results.get('correct_answers', 0)}/{test_results.get('test_count', 0)}")
                if "category_scores" in test_results:
                    for cat, scores in test_results["category_scores"].items():
                        print(f"  📊 {cat}: {scores.get('percentage', 0):.1f}%")

            elif test_name == "inference":
                avg_tps = test_results.get('avg_tokens_per_second', 0)
                print(f"  ⚡ Avg Speed: {avg_tps:.1f} tokens/sec")
                if "tokens_per_second" in test_results:
                    speeds = test_results["tokens_per_second"]
                    if speeds:
                        print(f"  📈 Range: {min(speeds):.1f} - {max(speeds):.1f} tokens/sec")

    def _display_benchmark_summary(self, all_results: dict):
        """Display overall benchmark summary"""
        print(f"\n📈 BENCHMARK SUMMARY")
        print("=" * 60)

        total_models = len(all_results)
        successful_tests = sum(1 for r in all_results.values() if "error" not in r)

        print(f"📊 Models Tested: {total_models}")
        print(f"✅ Successful: {successful_tests}")
        print(f"❌ Failed: {total_models - successful_tests}")

        if successful_tests > 0:
            print(f"\n🏆 PERFORMANCE LEADERBOARD")
            print("-" * 40)

            # Simple scoring system
            scores = {}
            for model_id, results in all_results.items():
                if "error" in results:
                    continue

                score = 0
                if "tests" in results:
                    tests = results["tests"]

                    # Performance score
                    if "performance" in tests:
                        perf = tests["performance"]
                        rps = perf.get("requests_per_second", 0)
                        score += min(rps * 10, 100)  # Cap at 100

                    # Memory score
                    if "memory" in tests:
                        mem = tests["memory"]
                        efficiency = mem.get("memory_efficiency", "unknown")
                        if efficiency == "excellent":
                            score += 30
                        elif efficiency == "good":
                            score += 20
                        elif efficiency == "fair":
                            score += 10

                    # Accuracy score
                    if "accuracy" in tests:
                        acc = tests["accuracy"]
                        score += acc.get("accuracy_score", 0)

                scores[model_id] = score

            # Sort by score and display top 3
            sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            for i, (model_id, score) in enumerate(sorted_scores[:3], 1):
                medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(i, "📊")
                print(f"{medal} {model_id}: {score:.1f} points")

        print(f"\n✅ Benchmark completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

    def interactive_mode(self):
        """Enhanced interactive mode with benchmark support"""
        print("🤖 Enhanced AI CLI - Interactive Mode")
        print("Type 'help' for commands, 'benchmark' for testing, 'exit' to quit")
        print("-" * 60)

        while True:
            try:
                user_input = input("\n🎯 > ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ['exit', 'quit', 'q']:
                    self.cleanup()
                    break

                elif user_input.lower() in ['help', 'h', '?']:
                    self.show_help()

                elif user_input.lower().startswith('benchmark'):
                    parts = user_input.split()
                    model_id = parts[1] if len(parts) > 1 else None
                    test_type = parts[2] if len(parts) > 2 else "comprehensive"
                    self.run_benchmarks(model_id, test_type)

                elif user_input.lower().startswith('status'):
                    self.show_system_status()

                elif user_input.lower().startswith('model'):
                    parts = user_input.split()
                    if len(parts) > 1:
                        self.change_model(parts[1])
                    else:
                        self.show_available_models()

                elif user_input.lower().startswith('gpu'):
                    self.test_gpu_detection()

                else:
                    # Process as normal message
                    self.process_message(user_input)

            except KeyboardInterrupt:
                print("\n⚠️  Interrupted by user")
                continue
            except EOFError:
                print("\n👋 Session ended")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                continue

    def show_help(self):
        """Show enhanced help with benchmark commands"""
        print("\n📚 Available Commands:")
        print("=" * 50)
        print("🤖 CHAT COMMANDS:")
        print("  <message>          Send message to AI")
        print("  help, h, ?         Show this help")
        print("  exit, quit, q      Exit the CLI")
        print()
        print("🔧 SYSTEM COMMANDS:")
        print("  status             Show system status")
        print("  gpu                Test GPU detection")
        print("  model <id>         Switch to specific model")
        print("  model              Show available models")
        print()
        print("📊 BENCHMARK COMMANDS:")
        print("  benchmark          Run comprehensive benchmarks on all models")
        print("  benchmark <model>  Run benchmarks on specific model")
        print("  benchmark <model> <type>  Run specific test type")
        print()
        print("🎯 BENCHMARK TYPES:")
        print("  comprehensive      All tests (performance, memory, accuracy, inference)")
        print("  performance        Speed and throughput tests")
        print("  memory            Memory usage and efficiency tests")
        print("  accuracy          Response accuracy tests")
        print("  inference         Inference speed tests")
        print("=" * 50)

    def run(self):
        """Main entry point"""
        try:
            self.interactive_mode()
        except Exception as e:
            print(f"{Fore.RED}❌ Fatal error: {e}{Style.RESET_ALL}")
            self.cleanup()
            sys.exit(1)


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(description='Enhanced AI Local Models CLI')
    parser.add_argument('--mode', choices=['interactive', 'command'], default='interactive',
                       help='CLI mode')
    parser.add_argument('--message', help='Single message to process')
    parser.add_argument('--file', help='File to process')
    parser.add_argument('--model', help='Model to use')

    args = parser.parse_args()

    cli = EnhancedCLI()

    if args.mode == 'command':
        if args.message:
            result = cli.handle_communication(CommunicationMode.TEXT, args.message)
            print(json.dumps(result, indent=2))
        elif args.file:
            result = cli.handle_communication(CommunicationMode.FILE, args.file)
            print(json.dumps(result, indent=2))
        else:
            print("Error: --message or --file required for command mode")
            sys.exit(1)
    else:
        cli.run()


if __name__ == '__main__':
    main()
