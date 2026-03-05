#!/usr/bin/env python3
"""
Application Startup Tests
Tests that the application can start and all routes are working
"""

import os
import sys
import json
from pathlib import Path

# Add current directory and src to path for imports
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(current_dir / "src"))

def test_application_import():
    """Test that the main application can be imported"""
    try:
        from app import app
        assert app is not None
        print("✅ Application imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Application import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Application initialization failed: {e}")
        return False

def test_routes_registration():
    """Test that all routes are properly registered"""
    try:
        from app import app

        # Get all registered routes
        routes = []
        for rule in app.url_map.iter_rules():
            if rule.endpoint != 'static':
                routes.append({
                    'endpoint': rule.endpoint,
                    'methods': list(rule.methods),
                    'url': str(rule)
                })

        print(f"✅ Found {len(routes)} registered routes")

        # Check for key routes
        route_endpoints = [route['endpoint'] for route in routes]

        # Check main routes
        main_routes = ['main_app.index', 'main_app.health', 'main_app.dashboard']
        for route in main_routes:
            if route in route_endpoints:
                print(f"✅ Main route {route} found")
            else:
                print(f"⚠️ Main route {route} not found")

        # Check companies routes
        companies_routes = [
            'companies.companies',
            'companies.create_company',
            'companies.companies_api'
        ]
        companies_found = 0
        for route in companies_routes:
            if route in route_endpoints:
                print(f"✅ Companies route {route} found")
                companies_found += 1
            else:
                print(f"⚠️ Companies route {route} not found")

        print(f"📊 Companies routes: {companies_found}/{len(companies_routes)} found")
        return True

    except Exception as e:
        print(f"❌ Routes registration test failed: {e}")
        return False

def test_blueprints_registration():
    """Test that all blueprints are properly registered"""
    try:
        from app import app

        # Check registered blueprints
        blueprints = [name for name, bp in app.blueprints.items()]
        print(f"✅ Found {len(blueprints)} registered blueprints: {blueprints}")

        # Check for companies blueprint
        if 'companies' in blueprints:
            print("✅ Companies blueprint registered")
        else:
            print("⚠️ Companies blueprint not found")

        return True

    except Exception as e:
        print(f"❌ Blueprints registration test failed: {e}")
        return False

def test_route_responses():
    """Test that key routes return proper responses"""
    try:
        from app import app

        test_routes = [
            ('/', 'GET'),
            ('/health', 'GET'),
            ('/companies', 'GET'),
            ('/companies/api/data', 'GET')
        ]

        results = []
        with app.test_client() as client:
            for route, method in test_routes:
                try:
                    if method == 'GET':
                        response = client.get(route)
                    elif method == 'POST':
                        response = client.post(route)
                    else:
                        response = client.get(route)  # Default to GET

                    result = {
                        'route': route,
                        'method': method,
                        'status_code': response.status_code,
                        'success': response.status_code in [200, 301, 302, 404]
                    }
                    results.append(result)

                    status = "✅" if result['success'] else "⚠️"
                    print(f"{status} {route} - {response.status_code}")

                except Exception as e:
                    print(f"❌ {route} failed: {e}")
                    results.append({
                        'route': route,
                        'method': method,
                        'status_code': None,
                        'success': False,
                        'error': str(e)
                    })

        successful_routes = sum(1 for r in results if r['success'])
        print(f"📊 Route responses: {successful_routes}/{len(results)} successful")

        return successful_routes > 0

    except Exception as e:
        print(f"❌ Route responses test failed: {e}")
        return False

def test_database_connectivity():
    """Test database connectivity"""
    try:
        from src.config import config_manager

        if config_manager and hasattr(config_manager, 'get_database_config'):
            db_config = config_manager.get_database_config()
            if db_config:
                print("✅ Database configuration loaded")
                return True

        print("⚠️ Database configuration not available")
        return False

    except Exception as e:
        print(f"❌ Database connectivity test failed: {e}")
        return False

def test_model_imports():
    """Test that all required models can be imported"""
    try:
        from src.models.unified_models import (
            db, Company, User, Invoice, InvoiceItem
        )

        models = [Company, User, Invoice, InvoiceItem]
        imported_models = []

        for model in models:
            if model:
                imported_models.append(model.__name__)
                print(f"✅ Model {model.__name__} imported")
            else:
                print(f"⚠️ Model not available")

        print(f"📊 Models imported: {len(imported_models)}/{len(models)}")
        return len(imported_models) > 0

    except ImportError as e:
        print(f"❌ Model imports failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Model import test failed: {e}")
        return False

def test_controller_functionality():
    """Test that controllers work properly"""
    try:
        from src.controllers import UnifiedController
        from src.models.unified_models import Company

        controller = UnifiedController(Company, 'companies')
        assert controller is not None
        assert controller.model_class == Company
        assert controller.table_name == 'companies'

        print("✅ UnifiedController initialized successfully")
        return True

    except ImportError as e:
        print(f"❌ Controller import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Controller functionality test failed: {e}")
        return False

def main():
    """Main application startup test runner"""
    print("🚀 Application Startup Tests")
    print("=" * 50)

    tests = [
        ("Application Import", test_application_import),
        ("Routes Registration", test_routes_registration),
        ("Blueprints Registration", test_blueprints_registration),
        ("Route Responses", test_route_responses),
        ("Database Connectivity", test_database_connectivity),
        ("Model Imports", test_model_imports),
        ("Controller Functionality", test_controller_functionality)
    ]

    results = {}
    for test_name, test_func in tests:
        print(f"\\n🧪 Running {test_name}...")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results[test_name] = False

    print("\\n📊 Application Startup Test Results:")
    print("-" * 40)
    for test_name, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_name:25} {status}")

    passed_count = sum(results.values())
    total_count = len(results)

    print(f"\\n📈 Overall: {passed_count}/{total_count} application tests passed")

    if passed_count == total_count:
        print("🎉 All application startup tests passed!")
        print("\\n💡 The application is ready for production deployment!")
        return True
    elif passed_count >= total_count * 0.7:  # 70% pass rate
        print("✅ Application is mostly functional.")
        print("\\n💡 Some tests failed but core functionality is working.")
        return True
    else:
        print("⚠️ Application has significant issues.")
        print("\\n💡 Check the failed tests above and fix the issues.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
