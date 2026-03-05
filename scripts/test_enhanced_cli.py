#!/usr/bin/env python3
"""
Test script for Enhanced CLI functionality
Tests all the new features and communication modes
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from ai_local_models.cli_enhanced import EnhancedCLI, CommunicationMode

def test_basic_functionality():
    """Test basic CLI functionality"""
    print("🧪 Testing Basic CLI Functionality")
    print("=" * 40)

    cli = EnhancedCLI()

    # Test GPU detection
    print("🔍 Testing GPU Detection...")
    gpu_info = cli._get_gpu_info()
    print(f"   GPU Available: {gpu_info['available']}")
    print(f"   GPU Name: {gpu_info['name']}")
    print(f"   Memory: {gpu_info['memory_gb']:.1f}GB")
    assert 'available' in gpu_info
    assert 'name' in gpu_info
    assert 'memory_gb' in gpu_info
    print("   ✅ GPU detection working")

    # Test model suggestions
    print("\n💡 Testing Model Suggestions...")
    text_suggestions = cli.suggest_model('text')
    image_suggestions = cli.suggest_model('image')
    audio_suggestions = cli.suggest_model('audio')
    pdf_suggestions = cli.suggest_model('pdf')

    assert len(text_suggestions) > 0
    assert len(image_suggestions) > 0
    assert len(audio_suggestions) > 0
    assert len(pdf_suggestions) > 0
    print("   ✅ Model suggestions working")

    return True

def test_communication_modes():
    """Test different communication modes"""
    print("\n🗣️ Testing Communication Modes")
    print("=" * 40)

    cli = EnhancedCLI()

    # Test text communication
    print("📝 Testing Text Communication...")
    text_result = cli.handle_communication(
        CommunicationMode.TEXT,
        "Hello AI, please analyze my financial data."
    )
    assert text_result['success'] == True
    assert 'suggested_models' in text_result
    assert len(text_result['suggested_models']) > 0
    print("   ✅ Text communication working")

    # Test voice communication
    print("\n🎵 Testing Voice Communication...")
    voice_result = cli.handle_communication(
        CommunicationMode.VOICE,
        "voice_input.wav"
    )
    assert voice_result['success'] == True
    assert 'suggested_models' in voice_result
    print("   ✅ Voice communication working")

    # Test image communication
    print("\n🖼️ Testing Image Communication...")
    image_result = cli.handle_communication(
        CommunicationMode.IMAGE,
        "sample_image.jpg"
    )
    assert image_result['success'] == True
    assert 'suggested_models' in image_result
    print("   ✅ Image communication working")

    return True

def test_task_progress():
    """Test task progress functionality"""
    print("\n📊 Testing Task Progress")
    print("=" * 40)

    cli = EnhancedCLI()

    # Test task lifecycle
    print("🔄 Testing Task Lifecycle...")

    # Start a task
    task = cli.start_task('test_task', 'Testing Progress', 'test')
    assert task.id == 'test_task'
    assert task.status == 'running'
    assert task.progress == 0.0
    print("   ✅ Task started")

    # Update progress
    cli.update_task_progress('test_task', 50.0, 1024 * 1024 * 10)  # 10MB/s
    assert task.progress == 50.0
    assert task.speed == 1024 * 1024 * 10
    print("   ✅ Progress updated")

    # Complete task
    cli.complete_task('test_task')
    assert task.status == 'completed'
    assert task.progress == 100.0
    print("   ✅ Task completed")

    return True

def test_utility_functions():
    """Test utility functions"""
    print("\n🛠️ Testing Utility Functions")
    print("=" * 40)

    cli = EnhancedCLI()

    # Test byte formatting
    assert cli._format_bytes(1024) == "1.00 KB"
    assert cli._format_bytes(1024 * 1024) == "1.00 MB"
    assert cli._format_bytes(1024 * 1024 * 1024) == "1.00 GB"
    print("   ✅ Byte formatting working")

    # Test time formatting
    assert "s" in cli._format_time(30)
    assert "m" in cli._format_time(90)
    assert "h" in cli._format_time(3600)
    print("   ✅ Time formatting working")

    return True

def test_file_communication():
    """Test file communication with real file"""
    print("\n📁 Testing File Communication")
    print("=" * 40)

    cli = EnhancedCLI()

    # Create a test file
    test_file = Path("test_document.pdf")
    test_file.touch()  # Create empty file

    try:
        # Test file communication
        result = cli.handle_communication(CommunicationMode.FILE, str(test_file))
        assert result['success'] == True
        assert result['content_type'] == 'pdf'
        assert 'suggested_models' in result
        assert len(result['suggested_models']) > 0
        print("   ✅ File communication working")

    finally:
        # Clean up
        if test_file.exists():
            test_file.unlink()

    return True

def test_error_handling():
    """Test error handling"""
    print("\n⚠️ Testing Error Handling")
    print("=" * 40)

    cli = EnhancedCLI()

    # Test failed task
    print("❌ Testing Failed Task...")
    task = cli.start_task('fail_test', 'Testing Failure', 'test')
    cli.fail_task('fail_test', 'Test error message')

    assert task.status == 'failed'
    assert task.error_message == 'Test error message'
    print("   ✅ Error handling working")

    # Test invalid communication
    print("\n🚫 Testing Invalid Communication...")
    try:
        cli.handle_communication("invalid_mode", "test")
        print("   ❌ Should have raised an error")
        return False
    except Exception:
        print("   ✅ Invalid communication handled")

    return True

def run_all_tests():
    """Run all tests"""
    print("🚀 Enhanced CLI Test Suite")
    print("=" * 60)

    tests = [
        test_basic_functionality,
        test_communication_modes,
        test_task_progress,
        test_utility_functions,
        test_file_communication,
        test_error_handling
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
                print(f"✅ {test.__name__} PASSED")
            else:
                failed += 1
                print(f"❌ {test.__name__} FAILED")
        except Exception as e:
            failed += 1
            print(f"❌ {test.__name__} FAILED: {e}")

    print("\n" + "=" * 60)
    print("📊 Test Results:")
    print(f"   ✅ Passed: {passed}")
    print(f"   ❌ Failed: {failed}")
    print(".1f")

    if failed == 0:
        print("🎉 All tests passed!")
        return True
    else:
        print("⚠️ Some tests failed")
        return False

def main():
    """Main test function"""
    try:
        success = run_all_tests()
        if success:
            print("\n🎯 Enhanced CLI is working correctly!")
            print("\nTo use the enhanced CLI:")
            print("1. python src/ai_local_models/cli_enhanced.py")
            print("2. Or use: python scripts/demo_enhanced_cli.py")
            sys.exit(0)
        else:
            print("\n❌ Some tests failed. Please check the implementation.")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n👋 Tests interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Test suite error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
