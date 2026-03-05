#!/usr/bin/env python3
"""
Demo script for Enhanced CLI
Shows all the beautiful progress display and communication features
"""

import sys
import os
import time
import threading
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from ai_local_models.cli_enhanced import EnhancedCLI, CommunicationMode

def simulate_download_progress(cli):
    """Simulate model download with progress"""
    print("\n🎯 Simulating Model Download with Progress")
    print("=" * 50)

    task = cli.start_task('demo_download', 'Downloading Llama 2 7B Model', 'download')

    # Simulate download progress
    total_size = 4_000_000_000  # 4GB
    downloaded = 0
    chunk_size = 50_000_000     # 50MB chunks

    while downloaded < total_size:
        time.sleep(0.2)
        downloaded += chunk_size
        progress = (downloaded / total_size) * 100
        cli.update_task_progress(task.id, progress, 1024 * 1024 * 50)  # 50MB/s

    cli.complete_task(task.id)
    print("✅ Download completed successfully!")

def simulate_model_loading(cli):
    """Simulate model loading with progress"""
    print("\n🔄 Simulating Model Loading with Progress")
    print("=" * 50)

    task = cli.start_task('demo_loading', 'Loading Llama 2 7B to GPU', 'load')

    # Simulate loading progress
    for i in range(101):
        time.sleep(0.1)
        cli.update_task_progress(task.id, i, 1024 * 1024 * 100)  # 100MB/s

    cli.complete_task(task.id)
    print("✅ Model loaded successfully!")

def demonstrate_communication_modes(cli):
    """Demonstrate different communication modes"""
    print("\n💬 Demonstrating Communication Modes")
    print("=" * 50)

    # Text communication
    print("\n📝 Testing Text Communication:")
    result = cli.handle_communication(CommunicationMode.TEXT,
        "Hello AI, please analyze my financial data and provide insights.")
    print(f"✅ Result: {result['success']}")
    print(f"💡 Suggested models: {', '.join(result['suggested_models'])}")

    # File communication
    print("\n📁 Testing File Communication:")
    # Create a dummy file for testing
    test_file = Path("test_document.pdf")
    test_file.touch()  # Create empty file
    try:
        result = cli.handle_communication(CommunicationMode.FILE, str(test_file))
        print(f"✅ Result: {result['success']}")
        print(f"📄 Content Type: {result['content_type']}")
        print(f"💡 Suggested models: {', '.join(result['suggested_models'])}")
    finally:
        test_file.unlink()  # Clean up

    # Image communication
    print("\n🖼️ Testing Image Communication:")
    result = cli.handle_communication(CommunicationMode.IMAGE, "sample_image.jpg")
    print(f"✅ Result: {result['success']}")
    print(f"💡 Suggested models: {', '.join(result['suggested_models'])}")

    # Voice communication
    print("\n🎵 Testing Voice Communication:")
    result = cli.handle_communication(CommunicationMode.VOICE, "audio_data.wav")
    print(f"✅ Result: {result['success']}")
    print(f"💡 Suggested models: {', '.join(result['suggested_models'])}")

def demonstrate_model_suggestions(cli):
    """Demonstrate model suggestions for different content types"""
    print("\n🎯 Demonstrating Model Suggestions")
    print("=" * 50)

    content_types = ['text', 'image', 'audio', 'pdf', 'data']

    for content_type in content_types:
        suggestions = cli.suggest_model(content_type)
        print(f"\n📋 Content Type: {content_type.upper()}")
        print(f"💡 Suggested Models: {', '.join(suggestions)}")

def demonstrate_gpu_detection(cli):
    """Demonstrate GPU detection capabilities"""
    print("\n🔍 Demonstrating GPU Detection")
    print("=" * 50)

    gpu_info = cli._get_gpu_info()
    print(f"🎯 GPU Available: {gpu_info['available']}")
    print(f"🏷️ GPU Name: {gpu_info['name']}")
    print(f"💾 Memory: {gpu_info['memory_gb']:.1f}GB")
    print(f"🔧 Type: {gpu_info['type']}")

    if gpu_info['available']:
        print("✅ GPU acceleration will be used!")
    else:
        print("⚠️ Running in CPU mode")

def demonstrate_progress_bars(cli):
    """Demonstrate various progress bar scenarios"""
    print("\n📊 Demonstrating Progress Bars")
    print("=" * 50)

    # Fast download simulation
    print("\n🚀 Fast Download (200MB/s):")
    task1 = cli.start_task('fast_download', 'Downloading Mistral 7B', 'download')
    for i in range(101):
        time.sleep(0.05)
        cli.update_task_progress(task1.id, i, 1024 * 1024 * 200)  # 200MB/s
    cli.complete_task(task1.id)

    # Slow processing simulation
    print("\n🐌 Slow Processing (2MB/s):")
    task2 = cli.start_task('slow_process', 'Processing Large Dataset', 'process')
    for i in range(101):
        time.sleep(0.1)
        cli.update_task_progress(task2.id, i, 1024 * 1024 * 2)  # 2MB/s
    cli.complete_task(task2.id)

    # Failed task simulation
    print("\n❌ Failed Task Simulation:")
    task3 = cli.start_task('failed_task', 'Loading Corrupted Model', 'load')
    for i in range(50):
        time.sleep(0.1)
        cli.update_task_progress(task3.id, i, 1024 * 1024 * 50)
    cli.fail_task(task3.id, "Model file corrupted or incomplete")

def run_interactive_demo(cli):
    """Run interactive demo mode"""
    print("\n🎮 Interactive Demo Mode")
    print("=" * 50)
    print("Commands:")
    print("  /demo download  - Show download progress")
    print("  /demo load      - Show model loading progress")
    print("  /demo gpu       - Show GPU detection")
    print("  /demo suggest   - Show model suggestions")
    print("  /demo comm      - Show communication modes")
    print("  /demo progress  - Show progress bar demos")
    print("  /quit           - Exit demo")
    print("=" * 50)

    while True:
        try:
            cmd = input("\n🎯 Enter command: ").strip().lower()

            if cmd == '/quit':
                break
            elif cmd == '/demo download':
                simulate_download_progress(cli)
            elif cmd == '/demo load':
                simulate_model_loading(cli)
            elif cmd == '/demo gpu':
                demonstrate_gpu_detection(cli)
            elif cmd == '/demo suggest':
                demonstrate_model_suggestions(cli)
            elif cmd == '/demo comm':
                demonstrate_communication_modes(cli)
            elif cmd == '/demo progress':
                demonstrate_progress_bars(cli)
            else:
                print("❓ Unknown command. Type '/quit' to exit or use '/demo <feature>'")

        except KeyboardInterrupt:
            print("\n👋 Demo interrupted by user")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def main():
    """Main demo function"""
    print("🤖 Enhanced AI Local Models CLI - Demo")
    print("=" * 60)

    # Initialize CLI
    cli = EnhancedCLI()

    # Show system status
    cli.show_system_status()

    # Show sample questions
    cli.show_sample_questions()

    # Run demonstrations
    try:
        # Automated demonstrations
        simulate_download_progress(cli)
        simulate_model_loading(cli)
        demonstrate_gpu_detection(cli)
        demonstrate_model_suggestions(cli)
        demonstrate_communication_modes(cli)
        demonstrate_progress_bars(cli)

        # Interactive mode
        run_interactive_demo(cli)

    except KeyboardInterrupt:
        print("\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"❌ Demo error: {e}")
    finally:
        cli.cleanup()

    print("\n🎉 Demo completed!")
    print("\nTo use the enhanced CLI in your applications:")
    print("1. Import: from ai_local_models.cli_enhanced import EnhancedCLI")
    print("2. Initialize: cli = EnhancedCLI()")
    print("3. Run interactive: cli.run()")
    print("4. Or use programmatically with cli.handle_communication()")

if __name__ == '__main__':
    main()
