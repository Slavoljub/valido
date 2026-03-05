#!/usr/bin/env python3
"""
ValidoAI Application Test Script
Tests if the application can start and basic functionality works
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_imports():
    """Test all critical imports"""
    print("🧪 Testing critical imports...")

    try:
        from app import app
        print("✅ App import successful")

        from src.config.unified_config import config
        print("✅ Config import successful")

        from src.database.unified_db_manager import db
        print("✅ Database manager import successful")

        from src.ai_manager import ai_safety_manager, redis_cache
        print("✅ AI manager import successful")

        from src.controllers.chat_controller import ChatController
        print("✅ Chat controller import successful")

        return True

    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_database():
    """Test database functionality"""
    print("\n🗄️ Testing database functionality...")

    try:
        from src.database.unified_db_manager import db

        # Test basic connection
        connection = db.get_connection()
        print("✅ Database connection successful")

        # Test table creation
        db.create_tables()
        print("✅ Database tables created")

        # Test sample data insertion
        db.insert_default_data()
        print("✅ Sample data inserted")

        # Test query execution
        result = db.execute_query("SELECT COUNT(*) as user_count FROM users", fetch="one")
        print(f"✅ Query execution successful: {result['user_count']} users")

        return True

    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def test_ai_components():
    """Test AI components"""
    print("\n🤖 Testing AI components...")

    try:
        from src.ai_manager import ai_safety_manager, redis_cache, env_config

        # Test safety manager
        context = ai_safety_manager.AIContext(user_id="test")
        result = ai_safety_manager.validate_input("Hello world", context)
        print(f"✅ AI safety validation: {result}")

        # Test environment config
        debug_mode = env_config.get('debug', False)
        print(f"✅ Environment config: debug={debug_mode}")

        # Test model manager
        from src.ai_manager import ModelDownloader
        downloader = ModelDownloader()
        text_models = downloader.get_text_models()
        print(f"✅ Model downloader: {len(text_models)} text models available")

        return True

    except Exception as e:
        print(f"❌ AI components error: {e}")
        return False

def test_flask_app():
    """Test Flask application"""
    print("\n🌐 Testing Flask application...")

    try:
        from app import app

        with app.test_client() as client:
            # Test health endpoint
            response = client.get('/health')
            if response.status_code == 200:
                print("✅ Health endpoint working")
            else:
                print(f"⚠️ Health endpoint returned {response.status_code}")

            # Test home page
            response = client.get('/')
            if response.status_code == 200:
                print("✅ Home page working")
            else:
                print(f"⚠️ Home page returned {response.status_code}")

            return True

    except Exception as e:
        print(f"❌ Flask app error: {e}")
        return False

def test_configuration():
    """Test configuration loading"""
    print("\n⚙️ Testing configuration...")

    try:
        from src.config.unified_config import config

        # Test basic config values
        print(f"✅ Debug mode: {config.debug}")
        print(f"✅ Testing mode: {config.testing}")
        print(f"✅ Database type: {config.database.type}")
        print(f"✅ AI enabled: {config.ai_enabled}")

        return True

    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def run_all_tests():
    """Run all tests"""
    print("🚀 Starting ValidoAI Application Tests")
    print("=" * 50)

    tests = [
        test_imports,
        test_configuration,
        test_database,
        test_ai_components,
        test_flask_app
    ]

    results = []

    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            results.append(False)

    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)

    passed = sum(results)
    total = len(results)

    for i, (test, result) in enumerate(zip(tests, results)):
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{i+1}. {test.__name__}: {status}")

    print(f"\n📈 Overall: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! ValidoAI is ready to run.")
        return True
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
