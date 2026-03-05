#!/usr/bin/env python3
"""
Quick Test Runner for ValidoAI
=============================
Simple script to test imports, dependencies, and basic functionality.
"""

import sys
import os
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_basic_imports():
    """Test basic imports that should always work."""
    logger.info("🔍 Testing basic imports...")
    
    try:
        # Core Flask imports
        import flask
        import flask_sqlalchemy
        import flask_login
        import werkzeug
        import sqlalchemy
        from dotenv import load_dotenv
        logger.info("✅ Core Flask imports successful")
        
        # Project imports
        from src.config import config_manager
        from src.database import database_manager
        from src.models.unified_models import db
        from src.controllers import controller_manager
        logger.info("✅ Project imports successful")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Basic imports failed: {e}")
        return False

def test_lazy_loading():
    """Test lazy loading system."""
    logger.info("🔍 Testing lazy loading system...")
    
    try:
        from app import lazy_loader, is_available
        
        # Test some optional dependencies
        test_deps = [
            'tensorflow',
            'torch', 
            'openai',
            'pandas',
            'numpy',
            'requests',
            'flask_socketio'
        ]
        
        results = {}
        for dep in test_deps:
            available = is_available(dep)
            results[dep] = available
            status = "✅" if available else "❌"
            logger.info(f"  {status} {dep}: {'Available' if available else 'Not available'}")
        
        available_count = sum(results.values())
        total_count = len(results)
        logger.info(f"📊 Lazy loading test: {available_count}/{total_count} dependencies available")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Lazy loading test failed: {e}")
        return False

def test_controllers():
    """Test controller imports and instantiation."""
    logger.info("🔍 Testing controllers...")
    
    try:
        # Test example controller
        from src.controllers.example_controller import ExampleController
        example_controller = ExampleController()
        logger.info("✅ ExampleController imported and instantiated")
        
        # Test database controller
        from src.controllers.database_controller import DatabaseController
        db_controller = DatabaseController()
        logger.info("✅ DatabaseController imported and instantiated")
        
        # Test AI/ML controller
        from src.controllers.ai_ml_controller import AIMLController
        ai_controller = AIMLController()
        logger.info("✅ AIMLController imported and instantiated")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Controller test failed: {e}")
        return False

def test_app_creation():
    """Test Flask app creation."""
    logger.info("🔍 Testing Flask app creation...")
    
    try:
        from app import create_app
        app = create_app('testing')
        logger.info("✅ Flask app created successfully")
        
        # Test basic app properties
        assert app.config['TESTING'] == True
        assert 'SECRET_KEY' in app.config
        logger.info("✅ App configuration verified")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ App creation test failed: {e}")
        return False

def test_database_operations():
    """Test basic database operations."""
    logger.info("🔍 Testing database operations...")
    
    try:
        from src.database import database_manager
        
        # Test database status
        if hasattr(database_manager, 'get_status'):
            status = database_manager.get_status()
            logger.info("✅ Database status retrieved")
        else:
            logger.info("ℹ️ Database status method not available")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Database operations test failed: {e}")
        return False

def main():
    """Run all tests."""
    logger.info("🚀 Starting ValidoAI Quick Tests")
    logger.info("=" * 50)
    
    tests = [
        ("Basic Imports", test_basic_imports),
        ("Lazy Loading", test_lazy_loading),
        ("Controllers", test_controllers),
        ("App Creation", test_app_creation),
        ("Database Operations", test_database_operations),
    ]
    
    results = {}
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n📋 Running: {test_name}")
        try:
            success = test_func()
            results[test_name] = success
            if success:
                passed += 1
                logger.info(f"✅ {test_name}: PASSED")
            else:
                logger.error(f"❌ {test_name}: FAILED")
        except Exception as e:
            results[test_name] = False
            logger.error(f"❌ {test_name}: ERROR - {e}")
    
    # Summary
    logger.info("\n" + "=" * 50)
    logger.info("📊 TEST SUMMARY")
    logger.info("=" * 50)
    
    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"  {status} {test_name}")
    
    logger.info(f"\n📈 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! Application is ready to run.")
        return 0
    else:
        logger.error("⚠️ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
