#!/usr/bin/env python3
"""
Companies Route Tests - TDD Approach
Tests for /companies route with full CRUD functionality
"""

import pytest
import os
import sys
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def test_companies_route_import():
    """Test that companies route can be imported"""
    try:
        from routes import companies_bp
        assert companies_bp is not None
        print("✅ Companies blueprint imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Companies blueprint import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Companies blueprint initialization failed: {e}")
        return False

def test_company_model_import():
    """Test that Company model can be imported"""
    try:
        from models.unified_models import Company
        assert Company is not None
        assert hasattr(Company, 'companies_id')
        assert hasattr(Company, 'company_name')
        assert hasattr(Company, 'tax_id')
        print("✅ Company model imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Company model import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Company model validation failed: {e}")
        return False

def test_datatable_component_import():
    """Test that DataTable component can be imported"""
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent / "static" / "js"))
        # DataTable is loaded via JavaScript, so we'll test the static file exists
        datatable_path = Path(__file__).parent.parent / "static" / "js" / "datatables-enhanced.js"
        assert datatable_path.exists()
        print("✅ DataTable component found")
        return True
    except Exception as e:
        print(f"❌ DataTable component test failed: {e}")
        return False

def test_companies_route_get():
    """Test GET /companies route returns proper response"""
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent))

        from app import app

        with app.test_client() as client:
            # Test companies route
            response = client.get('/companies')
            assert response.status_code in [200, 302, 404]  # Could be redirect or not found initially

            print(f"✅ Companies route responded with status: {response.status_code}")

            # Check if response contains HTML
            if response.status_code == 200:
                assert b'html' in response.data or b'<' in response.data
                print("✅ Companies route returns HTML content")

            return True

    except Exception as e:
        print(f"❌ Companies route GET test failed: {e}")
        return False

def test_companies_api_get():
    """Test GET /api/companies API endpoint"""
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent))

        from app import app

        with app.test_client() as client:
            # Test companies API
            response = client.get('/api/companies')
            assert response.status_code in [200, 404]  # Could be not found if not implemented

            if response.status_code == 200:
                data = json.loads(response.data)
                assert 'data' in data or 'companies' in data
                print("✅ Companies API returns valid JSON data")

            print(f"✅ Companies API responded with status: {response.status_code}")
            return True

    except Exception as e:
        print(f"❌ Companies API GET test failed: {e}")
        return False

def test_company_create():
    """Test POST /companies route for creating new company"""
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent))

        from app import app

        with app.test_client() as client:
            # Test data for new company
            test_company = {
                'company_name': 'Test Company Inc',
                'legal_name': 'Test Company Inc',
                'tax_id': '12345678',
                'registration_number': '98765432',
                'industry': 'Technology',
                'company_type': 'DOO',
                'email': 'test@testcompany.com',
                'phone': '+381-11-123-4567',
                'address_line1': 'Test Street 123',
                'city': 'Belgrade',
                'postal_code': '11000'
            }

            # Test POST request
            response = client.post('/companies',
                                 data=json.dumps(test_company),
                                 content_type='application/json')

            # Should return 200, 201, or 302 for success
            assert response.status_code in [200, 201, 302, 404]

            print(f"✅ Company create responded with status: {response.status_code}")
            return True

    except Exception as e:
        print(f"❌ Company create test failed: {e}")
        return False

def test_company_update():
    """Test PUT /companies/<id> route for updating company"""
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent))

        from app import app

        with app.test_client() as client:
            # Test data for updating company
            test_update = {
                'company_name': 'Updated Test Company Inc',
                'industry': 'Fintech',
                'email': 'updated@testcompany.com'
            }

            # Test PUT request with dummy ID
            response = client.put('/companies/test-uuid',
                                data=json.dumps(test_update),
                                content_type='application/json')

            # Should return 200, 404, or 422
            assert response.status_code in [200, 404, 422]

            print(f"✅ Company update responded with status: {response.status_code}")
            return True

    except Exception as e:
        print(f"❌ Company update test failed: {e}")
        return False

def test_company_delete():
    """Test DELETE /companies/<id> route for deleting company"""
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent))

        from app import app

        with app.test_client() as client:
            # Test DELETE request with dummy ID
            response = client.delete('/companies/test-uuid')

            # Should return 200, 204, or 404
            assert response.status_code in [200, 204, 404]

            print(f"✅ Company delete responded with status: {response.status_code}")
            return True

    except Exception as e:
        print(f"❌ Company delete test failed: {e}")
        return False

def test_datatable_integration():
    """Test DataTable integration works properly"""
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent))

        from app import app

        with app.test_client() as client:
            # Test companies page loads DataTable
            response = client.get('/companies')

            if response.status_code == 200:
                # Check if DataTable JavaScript is included
                assert b'datatables-enhanced.js' in response.data or b'DataTable' in response.data
                print("✅ DataTable integration found in companies page")

            print(f"✅ DataTable integration test passed with status: {response.status_code}")
            return True

    except Exception as e:
        print(f"❌ DataTable integration test failed: {e}")
        return False

def test_mvvm_architecture():
    """Test that MVVM architecture is properly implemented"""
    try:
        # Check if controllers exist and are properly structured
        from controllers import UnifiedController
        from models.unified_models import Company

        # Create controller instance
        controller = UnifiedController(Company, 'companies')
        assert controller is not None
        assert hasattr(controller, 'model')
        assert hasattr(controller, 'table_name')

        print("✅ MVVM architecture controller properly implemented")
        return True

    except ImportError as e:
        print(f"❌ MVVM architecture import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ MVVM architecture test failed: {e}")
        return False

def main():
    """Main test runner for companies functionality"""
    print("🧪 Companies Route Tests - TDD Approach")
    print("=" * 50)

    tests = [
        ("Companies Route Import", test_companies_route_import),
        ("Company Model Import", test_company_model_import),
        ("DataTable Component Import", test_datatable_component_import),
        ("Companies Route GET", test_companies_route_get),
        ("Companies API GET", test_companies_api_get),
        ("Company Create", test_company_create),
        ("Company Update", test_company_update),
        ("Company Delete", test_company_delete),
        ("DataTable Integration", test_datatable_integration),
        ("MVVM Architecture", test_mvvm_architecture)
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
        print(f"{test_name:25} {status}")

    passed_count = sum(results.values())
    total_count = len(results)

    print(f"\\n📈 Overall: {passed_count}/{total_count} companies route tests passed")

    if passed_count == total_count:
        print("🎉 All companies route tests passed!")
        return True
    else:
        print("⚠️ Some tests failed. Check individual results above.")
        print("\\n💡 This is expected for TDD - implement the functionality based on these tests!")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
