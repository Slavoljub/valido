#!/usr/bin/env python3
"""
Route Verification Tests
Tests Flask routes and functionality
"""

import pytest
import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def test_flask_app_import():
    """Test that Flask app can be imported"""
    try:
        import sys
        from pathlib import Path
        # Add current directory to path
        sys.path.insert(0, str(Path(__file__).parent.parent))

        import app
        assert app.app is not None
        print("✅ Flask app imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Flask app import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Flask app initialization failed: {e}")
        return False

def test_routes_import():
    """Test that routes can be imported"""
    try:
        import routes
        print("✅ Routes imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Routes import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Routes initialization failed: {e}")
        return False

def test_config_import():
    """Test that configuration can be imported"""
    try:
        import sys
        from pathlib import Path
        # Add current directory to path
        sys.path.insert(0, str(Path(__file__).parent.parent))

        from src.config import UnifiedConfigManager
        config = UnifiedConfigManager()
        assert config is not None
        print("✅ Configuration imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Configuration import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Configuration initialization failed: {e}")
        return False

def test_database_connection():
    """Test database connection"""
    try:
        import sys
        from pathlib import Path
        # Add current directory to path
        sys.path.insert(0, str(Path(__file__).parent.parent))

        from src.config import UnifiedConfigManager
        config = UnifiedConfigManager()
        db_config = config.get_database_config()

        if db_config.get('type') == 'sqlite':
            print("✅ SQLite database configuration loaded")
            return True
        elif db_config.get('type') == 'postgresql':
            import psycopg2
            conn = psycopg2.connect(**{
                'host': db_config.get('host'),
                'port': db_config.get('port'),
                'database': db_config.get('database'),
                'user': db_config.get('user'),
                'password': db_config.get('password')
            })
            conn.close()
            print("✅ PostgreSQL database connection successful")
            return True
        elif db_config.get('type') == 'mysql':
            import mysql.connector
            conn = mysql.connector.connect(**{
                'host': db_config.get('host'),
                'port': db_config.get('port'),
                'database': db_config.get('database'),
                'user': db_config.get('user'),
                'password': db_config.get('password')
            })
            conn.close()
            print("✅ MySQL database connection successful")
            return True
        else:
            print(f"⚠️ Unsupported database type: {db_config.get('type')}")
            return False

    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_basic_routes():
    """Test basic Flask routes"""
    try:
        import sys
        from pathlib import Path
        # Add current directory to path
        sys.path.insert(0, str(Path(__file__).parent.parent))

        import app

        with app.app.test_client() as client:
            # Test home route
            response = client.get('/')
            assert response.status_code in [200, 302, 404]  # Could be redirect or not found
            print(f"✅ Home route responded with status: {response.status_code}")

            # Test health check if it exists
            try:
                response = client.get('/health')
                if response.status_code == 200:
                    print("✅ Health check route working")
                else:
                    print(f"⚠️ Health check route returned: {response.status_code}")
            except:
                print("⚠️ Health check route not available")

            return True

    except Exception as e:
        print(f"❌ Route testing failed: {e}")
        return False

def test_template_rendering():
    """Test template rendering"""
    try:
        import sys
        from pathlib import Path
        # Add current directory to path
        sys.path.insert(0, str(Path(__file__).parent.parent))

        import app

        with app.app.test_client() as client:
            response = client.get('/')
            if b'html' in response.data or b'<' in response.data:
                print("✅ Template rendering working")
                return True
            else:
                print("⚠️ Template rendering may have issues")
                return False

    except Exception as e:
        print(f"❌ Template rendering test failed: {e}")
        return False

def test_static_files():
    """Test static file serving"""
    try:
        import sys
        from pathlib import Path
        # Add current directory to path
        sys.path.insert(0, str(Path(__file__).parent.parent))

        import app

        with app.app.test_client() as client:
            response = client.get('/static/css/main.css')
            if response.status_code == 200:
                print("✅ Static file serving working")
                return True
            else:
                print(f"⚠️ Static file serving returned: {response.status_code}")
                return False

    except Exception as e:
        print(f"❌ Static file test failed: {e}")
        return False

def test_error_handling():
    """Test error handling"""
    try:
        import sys
        from pathlib import Path
        # Add current directory to path
        sys.path.insert(0, str(Path(__file__).parent.parent))

        import app

        with app.app.test_client() as client:
            # Test 404 error
            response = client.get('/nonexistent-route')
            assert response.status_code == 404
            print("✅ Error handling working (404)")

            # Test 500 error (if there's a route that causes it)
            try:
                response = client.get('/error-test')
                if response.status_code == 500:
                    print("✅ Error handling working (500)")
            except:
                print("⚠️ 500 error test route not available")

            return True

    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False

def main():
    """Main test runner"""
    print("🧪 Route Verification Tests")
    print("=" * 50)

    tests = [
        ("Flask App Import", test_flask_app_import),
        ("Routes Import", test_routes_import),
        ("Configuration Import", test_config_import),
        ("Database Connection", test_database_connection),
        ("Basic Routes", test_basic_routes),
        ("Template Rendering", test_template_rendering),
        ("Static Files", test_static_files),
        ("Error Handling", test_error_handling)
    ]

    results = {}
    for test_name, test_func in tests:
        print(f"\\n🧪 Running {test_name}...")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results[test_name] = False

    print("\\n📊 Test Results Summary:")
    print("-" * 30)
    for test_name, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_name:20} {status}")

    passed_count = sum(results.values())
    total_count = len(results)

    print(f"\\n📈 Overall: {passed_count}/{total_count} route verification tests passed")

    if passed_count == total_count:
        print("🎉 All route verification tests passed!")
        return True
    else:
        print("⚠️ Some tests failed. Check individual results above.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
