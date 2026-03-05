#!/usr/bin/env python3
"""
Test script for AI Models functionality
Tests model downloading, status checking, and progress tracking
"""

import sys
import os
import time
import requests
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.ai_local_models.model_manager import model_manager
from src.ai_local_models.download_progress import progress_tracker

def test_model_manager():
    """Test the model manager functionality"""
    print("🧪 Testing AI Model Manager...")
    
    # Test system info
    print("\n📊 System Information:")
    system_info = model_manager.get_system_info()
    for key, value in system_info.items():
        print(f"  {key}: {value}")
    
    # Test available models
    print("\n🤖 Available Models:")
    models = model_manager.get_available_models()
    for model in models:
        status = model_manager.get_model_status(model.name)
        print(f"  {model.name}: {status.get('status', 'unknown')}")
    
    print(f"\n✅ Found {len(models)} available models")

def test_progress_tracker():
    """Test the progress tracker functionality"""
    print("\n📈 Testing Progress Tracker...")
    
    # Test progress tracking
    progress_tracker.start_download("test-model", 1024 * 1024)  # 1MB
    
    # Simulate progress updates
    for i in range(0, 101, 10):
        progress_tracker.update_progress("test-model", i * 1024 * 10)  # 10KB increments
        time.sleep(0.1)
    
    progress_tracker.complete_download("test-model", True)
    
    # Get progress data
    progress_data = progress_tracker.to_dict()
    print(f"  Progress data: {progress_data}")
    
    # Get summary
    summary = progress_tracker.get_summary()
    print(f"  Summary: {summary}")
    
    # Clean up
    progress_tracker.clear_all()

def test_model_download():
    """Test actual model download (small model)"""
    print("\n⬇️ Testing Model Download...")
    
    # Find a small model to test with
    models = model_manager.get_available_models()
    small_models = [m for m in models if m.size_gb <= 2.0]  # 2GB or less
    
    if not small_models:
        print("  ❌ No small models available for testing")
        return
    
    test_model = small_models[0]
    print(f"  Testing with: {test_model.name}")
    
    # Check if already downloaded
    status = model_manager.get_model_status(test_model.name)
    if status.get('status') == 'downloaded':
        print(f"  ✅ Model {test_model.name} already downloaded")
        return
    
    # Start download
    print(f"  Starting download of {test_model.name}...")
    
    def progress_callback(name, progress, status):
        print(f"    {name}: {progress:.1f}% - {status}")
    
    success = model_manager.download_model(test_model.name, progress_callback)
    
    if success:
        print(f"  ✅ Download started successfully for {test_model.name}")
    else:
        print(f"  ❌ Failed to start download for {test_model.name}")

def test_api_endpoints():
    """Test API endpoints (requires Flask app running)"""
    print("\n🌐 Testing API Endpoints...")
    
    base_url = "http://localhost:5000"
    
    try:
        # Test system info endpoint
        response = requests.get(f"{base_url}/api/ai-models/system-info", timeout=5)
        if response.status_code == 200:
            print("  ✅ System info endpoint working")
        else:
            print(f"  ❌ System info endpoint failed: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"  ⚠️ Could not test API endpoints: {e}")
        print("  Make sure the Flask app is running on localhost:5000")

def main():
    """Run all tests"""
    print("🚀 AI Models Test Suite")
    print("=" * 50)
    
    try:
        test_model_manager()
        test_progress_tracker()
        test_model_download()
        test_api_endpoints()
        
        print("\n" + "=" * 50)
        print("✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
