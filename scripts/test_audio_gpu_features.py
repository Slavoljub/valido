#!/usr/bin/env python3
"""
Test Audio Models and GPU Selection Features
Tests the new audio processing models and GPU selection functionality
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / 'src'))

def test_gpu_detection():
    """Test GPU detection functionality"""
    print("🔍 Testing GPU Detection...")
    
    try:
        from src.ai_local_models.gpu_detector import gpu_detector
        
        # Test GPU status
        gpu_status = gpu_detector.get_gpu_status()
        print(f"✅ GPU Status: {gpu_status['gpu_available']}")
        if gpu_status['gpu_available']:
            print(f"   GPU Type: {gpu_status['gpu_type']}")
            print(f"   Memory: {gpu_status['memory_gb']:.1f}GB")
            print(f"   Backend: {gpu_status['recommended_backend']}")
        
        # Test available GPUs
        available_gpus = gpu_detector.get_available_gpus()
        print(f"✅ Available GPUs: {len(available_gpus)}")
        for gpu in available_gpus:
            print(f"   - {gpu['name']} ({gpu['type']})")
        
        # Test GPU configuration
        gpu_config = gpu_detector.get_gpu_config('auto')
        print(f"✅ Auto GPU Config: {gpu_config['device']}")
        
        return True
    except Exception as e:
        print(f"❌ GPU Detection Error: {e}")
        return False

def test_audio_models():
    """Test audio models functionality"""
    print("\n🎵 Testing Audio Models...")
    
    try:
        from src.ai_local_models.model_downloader import ModelDownloader
        
        model_downloader = ModelDownloader()
        
        # Test getting audio models
        audio_models = model_downloader.get_audio_models()
        print(f"✅ Audio Models Found: {len(audio_models)}")
        
        for model in audio_models:
            print(f"   - {model['name']} ({model['size_mb']}MB)")
            print(f"     Type: {model['type']}")
            print(f"     Tags: {', '.join(model['tags'])}")
            print(f"     Downloaded: {model['downloaded']}")
        
        # Test getting models by type
        text_models = model_downloader.get_text_models()
        print(f"✅ Text Models Found: {len(text_models)}")
        
        # Test recommended audio models
        recommended_audio = model_downloader.get_recommended_audio_models()
        print(f"✅ Recommended Audio Models: {len(recommended_audio)}")
        
        return True
    except Exception as e:
        print(f"❌ Audio Models Error: {e}")
        return False

def test_model_configuration():
    """Test model configuration with different types"""
    print("\n⚙️ Testing Model Configuration...")
    
    try:
        from src.ai_local_models.model_downloader import ModelDownloader
        
        model_downloader = ModelDownloader()
        config = model_downloader.get_popular_models_config()
        
        # Count models by type
        text_models = [k for k, v in config.items() if v.get('type') == 'text']
        audio_models = [k for k, v in config.items() if v.get('type') == 'audio']
        
        print(f"✅ Text Models: {len(text_models)}")
        print(f"✅ Audio Models: {len(audio_models)}")
        
        # Show some examples
        print("\n📝 Text Model Examples:")
        for model_id in text_models[:3]:
            model = config[model_id]
            print(f"   - {model['name']}: {model['description']}")
        
        print("\n🎵 Audio Model Examples:")
        for model_id in audio_models[:3]:
            model = config[model_id]
            print(f"   - {model['name']}: {model['description']}")
        
        return True
    except Exception as e:
        print(f"❌ Model Configuration Error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing Audio Models and GPU Selection Features")
    print("=" * 60)
    
    tests = [
        test_gpu_detection,
        test_audio_models,
        test_model_configuration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Audio models and GPU selection are working correctly.")
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
