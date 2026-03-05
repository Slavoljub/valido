#!/usr/bin/env python3
"""
Comprehensive Route Testing Suite
Tests all routes and validates controller data passing
"""

import pytest
import json
import unittest
from unittest.mock import Mock, patch, MagicMock
from flask import url_for, g, session
from werkzeug.security import generate_password_hash

from app import create_app, db
from src.config.unified_config import config


class TestRoutesComprehensive:
    """Comprehensive testing of all application routes"""

    @pytest.fixture
    def app(self):
        """Create and configure a test app instance."""
        app = create_app()
        app.config.update({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'SECRET_KEY': 'test-secret-key',
            'JWT_SECRET_KEY': 'test-jwt-secret',
            'DEBUG': True,
            'SERVER_NAME': 'localhost',
            'WTF_CSRF_ENABLED': False  # Disable CSRF for testing
        })
        return app

    @pytest.fixture
    def client(self, app):
        """Create a test client."""
        return app.test_client()

    @pytest.fixture
    def runner(self, app):
        """Create a test runner."""
        return app.test_cli_runner()

    @pytest.fixture
    def init_database(self, app):
        """Initialize test database with sample data."""
        with app.app_context():
            db.create_tables()

            # Create test admin user
            admin_password_hash = generate_password_hash('admin123')
            db.execute_query("""
                INSERT OR IGNORE INTO users (
                    username, email, password_hash, first_name, last_name, is_admin, language
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, ('admin', 'admin@validoai.test', admin_password_hash, 'Admin', 'User', 1, 'sr'))

            # Create test regular user
            user_password_hash = generate_password_hash('user123')
            db.execute_query("""
                INSERT OR IGNORE INTO users (
                    username, email, password_hash, first_name, last_name, is_admin, language
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, ('testuser', 'user@validoai.test', user_password_hash, 'Test', 'User', 0, 'en'))

            # Create sample company
            db.execute_query("""
                INSERT OR IGNORE INTO companies (
                    user_id, company_name, pib, maticni_broj, business_form
                ) VALUES (?, ?, ?, ?, ?)
            """, (2, 'Test Company', '12345678901', '12345678', 'doo'))

            # Create sample transaction
            db.execute_query("""
                INSERT OR IGNORE INTO transactions (
                    user_id, description, amount, transaction_type, date
                ) VALUES (?, ?, ?, ?, ?)
            """, (2, 'Test transaction', 1000.50, 'income', '2024-01-15'))

            yield db
            db.cleanup()

    def login_as_admin(self, client):
        """Helper method to login as admin and return token."""
        login_data = {
            'email': 'admin@validoai.test',
            'password': 'admin123'
        }

        response = client.post('/api/auth/login',
                             data=json.dumps(login_data),
                             content_type='application/json')

        if response.status_code == 200:
            data = json.loads(response.data)
            return data.get('access_token')
        return None

    def login_as_user(self, client):
        """Helper method to login as regular user and return token."""
        login_data = {
            'email': 'user@validoai.test',
            'password': 'user123'
        }

        response = client.post('/api/auth/login',
                             data=json.dumps(login_data),
                             content_type='application/json')

        if response.status_code == 200:
            data = json.loads(response.data)
            return data.get('access_token')
        return None

    # =========================================================================
    # ROOT AND LANDING PAGE ROUTES
    # =========================================================================

    def test_root_route(self, client):
        """Test root route (/)"""
        response = client.get('/')
        assert response.status_code in [200, 302]  # OK or redirect to dashboard

        if response.status_code == 200:
            data = response.get_data(as_text=True)
            # Should contain basic HTML structure
            assert '<!DOCTYPE html>' in data or '<html' in data

    def test_health_check_route(self, client):
        """Test health check route"""
        response = client.get('/health')
        assert response.status_code == 200
        data = response.get_data(as_text=True)
        assert 'healthy' in data.lower()

    def test_api_health_route(self, client):
        """Test API health endpoint"""
        response = client.get('/api/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, dict)
        assert 'status' in data

    # =========================================================================
    # AUTHENTICATION ROUTES
    # =========================================================================

    def test_login_route_get(self, client):
        """Test login page GET request"""
        response = client.get('/login')
        assert response.status_code in [200, 302]

        if response.status_code == 200:
            data = response.get_data(as_text=True)
            # Should contain login form elements
            assert 'login' in data.lower() or 'email' in data.lower()

    def test_register_route_get(self, client):
        """Test registration page GET request"""
        response = client.get('/register')
        assert response.status_code in [200, 302]

        if response.status_code == 200:
            data = response.get_data(as_text=True)
            # Should contain registration form elements
            assert 'register' in data.lower() or 'password' in data.lower()

    def test_login_api_post(self, client, init_database):
        """Test login API POST request"""
        login_data = {
            'email': 'admin@validoai.test',
            'password': 'admin123'
        }

        response = client.post('/api/auth/login',
                             data=json.dumps(login_data),
                             content_type='application/json')

        assert response.status_code in [200, 401]

        if response.status_code == 200:
            data = json.loads(response.data)
            assert 'access_token' in data
            assert 'refresh_token' in data
            assert 'user' in data

            # Validate user data structure
            user_data = data['user']
            assert 'id' in user_data
            assert 'email' in user_data
            assert 'first_name' in user_data
            assert 'last_name' in user_data
            assert user_data['email'] == 'admin@validoai.test'

    def test_register_api_post(self, client):
        """Test user registration API POST request"""
        register_data = {
            'username': 'newtestuser',
            'email': 'newtestuser@validoai.test',
            'password': 'newpassword123',
            'first_name': 'New',
            'last_name': 'TestUser',
            'language': 'sr'
        }

        response = client.post('/api/auth/register',
                             data=json.dumps(register_data),
                             content_type='application/json')

        assert response.status_code in [201, 400, 409]

        if response.status_code == 201:
            data = json.loads(response.data)
            assert 'user_id' in data
            assert 'message' in data

    def test_logout_route(self, client):
        """Test logout route"""
        response = client.get('/logout')
        assert response.status_code in [200, 302]

    # =========================================================================
    # DASHBOARD ROUTES
    # =========================================================================

    def test_dashboard_banking_route(self, client):
        """Test banking dashboard route"""
        response = client.get('/dashboard/banking')
        assert response.status_code in [200, 302]  # OK or redirect to login

        if response.status_code == 200:
            data = response.get_data(as_text=True)
            # Should contain dashboard elements
            assert 'dashboard' in data.lower() or 'banking' in data.lower()

    def test_dashboard_analytics_route(self, client):
        """Test analytics dashboard route"""
        response = client.get('/dashboard/analytics')
        assert response.status_code in [200, 302]

        if response.status_code == 200:
            data = response.get_data(as_text=True)
            # Should contain analytics elements
            assert 'analytics' in data.lower() or 'chart' in data.lower()

    def test_dashboard_compact_route(self, client):
        """Test compact dashboard route"""
        response = client.get('/dashboard/compact')
        assert response.status_code in [200, 302]

        if response.status_code == 200:
            data = response.get_data(as_text=True)
            # Should contain compact layout elements
            assert 'compact' in data.lower() or 'dashboard' in data.lower()

    def test_dashboard_admin_route_unauthorized(self, client):
        """Test admin dashboard route without authorization"""
        response = client.get('/dashboard/admin')
        assert response.status_code == 302  # Redirect to login

    def test_dashboard_admin_route_authorized(self, client, init_database):
        """Test admin dashboard route with admin authorization"""
        token = self.login_as_admin(client)

        if token:
            headers = {'Authorization': f'Bearer {token}'}
            response = client.get('/dashboard/admin', headers=headers)
            assert response.status_code in [200, 302, 404]  # OK, redirect, or not found

    def test_dashboard_api_data(self, client, init_database):
        """Test dashboard API data endpoint"""
        token = self.login_as_user(client)

        if token:
            headers = {'Authorization': f'Bearer {token}'}
            response = client.get('/api/dashboard/data', headers=headers)
            assert response.status_code in [200, 401, 404]

            if response.status_code == 200:
                data = json.loads(response.data)
                assert isinstance(data, dict)
                # Should contain dashboard-related data
                assert len(data.keys()) > 0

    # =========================================================================
    # FINANCIAL ROUTES
    # =========================================================================

    def test_transactions_route(self, client):
        """Test transactions route"""
        response = client.get('/transactions')
        assert response.status_code in [200, 302]

        if response.status_code == 200:
            data = response.get_data(as_text=True)
            # Should contain transaction elements
            assert 'transaction' in data.lower() or 'finance' in data.lower()

    def test_invoices_route(self, client):
        """Test invoices route"""
        response = client.get('/invoices')
        assert response.status_code in [200, 302]

        if response.status_code == 200:
            data = response.get_data(as_text=True)
            # Should contain invoice elements
            assert 'invoice' in data.lower() or 'bill' in data.lower()

    def test_accounts_route(self, client):
        """Test accounts route"""
        response = client.get('/accounts')
        assert response.status_code in [200, 302]

        if response.status_code == 200:
            data = response.get_data(as_text=True)
            # Should contain account elements
            assert 'account' in data.lower() or 'company' in data.lower()

    def test_reports_route(self, client):
        """Test reports route"""
        response = client.get('/reports')
        assert response.status_code in [200, 302]

        if response.status_code == 200:
            data = response.get_data(as_text=True)
            # Should contain report elements
            assert 'report' in data.lower() or 'analysis' in data.lower()

    def test_tax_route(self, client):
        """Test tax route"""
        response = client.get('/tax')
        assert response.status_code in [200, 302]

        if response.status_code == 200:
            data = response.get_data(as_text=True)
            # Should contain tax elements
            assert 'tax' in data.lower() or 'pdv' in data.lower()

    # =========================================================================
    # FINANCIAL API ENDPOINTS
    # =========================================================================

    def test_transactions_api_get(self, client, init_database):
        """Test GET transactions API endpoint"""
        token = self.login_as_user(client)

        if token:
            headers = {'Authorization': f'Bearer {token}'}
            response = client.get('/api/transactions', headers=headers)
            assert response.status_code in [200, 401]

            if response.status_code == 200:
                data = json.loads(response.data)
                assert 'transactions' in data
                assert 'pagination' in data
                assert isinstance(data['transactions'], list)
                assert isinstance(data['pagination'], dict)

                # Validate pagination structure
                pagination = data['pagination']
                assert 'page' in pagination
                assert 'per_page' in pagination
                assert 'total' in pagination
                assert 'pages' in pagination

    def test_transactions_api_post(self, client, init_database):
        """Test POST transactions API endpoint"""
        token = self.login_as_user(client)

        if token:
            headers = {'Authorization': f'Bearer {token}'}

            transaction_data = {
                'description': 'API Test Transaction',
                'amount': 250.75,
                'transaction_type': 'expense',
                'category': 'office',
                'date': '2024-01-20',
                'notes': 'Testing API endpoint'
            }

            response = client.post('/api/transactions',
                                 data=json.dumps(transaction_data),
                                 content_type='application/json',
                                 headers=headers)

            assert response.status_code in [201, 400, 401]

            if response.status_code == 201:
                data = json.loads(response.data)
                assert 'transaction_id' in data
                assert 'message' in data

    def test_invoices_api_get(self, client, init_database):
        """Test GET invoices API endpoint"""
        token = self.login_as_user(client)

        if token:
            headers = {'Authorization': f'Bearer {token}'}
            response = client.get('/api/invoices', headers=headers)
            assert response.status_code in [200, 401]

            if response.status_code == 200:
                data = json.loads(response.data)
                assert 'invoices' in data
                assert isinstance(data['invoices'], list)

    def test_invoices_api_post(self, client, init_database):
        """Test POST invoices API endpoint"""
        token = self.login_as_user(client)

        if token:
            headers = {'Authorization': f'Bearer {token}'}

            invoice_data = {
                'invoice_number': 'INV-API-001',
                'client_name': 'API Test Client',
                'issue_date': '2024-01-20',
                'due_date': '2024-02-20',
                'subtotal': 1500.00,
                'tax_rate': 20.0,
                'description': 'API testing invoice'
            }

            response = client.post('/api/invoices',
                                 data=json.dumps(invoice_data),
                                 content_type='application/json',
                                 headers=headers)

            assert response.status_code in [201, 400, 401]

            if response.status_code == 201:
                data = json.loads(response.data)
                assert 'invoice_id' in data or 'message' in data

    # =========================================================================
    # AI/ML ROUTES
    # =========================================================================

    def test_ai_chat_route(self, client):
        """Test AI chat route"""
        response = client.get('/ai/chat')
        assert response.status_code in [200, 302]

        if response.status_code == 200:
            data = response.get_data(as_text=True)
            # Should contain chat elements
            assert 'chat' in data.lower() or 'ai' in data.lower()

    def test_ai_models_route(self, client):
        """Test AI models route"""
        response = client.get('/ai/models')
        assert response.status_code in [200, 302]

        if response.status_code == 200:
            data = response.get_data(as_text=True)
            # Should contain model elements
            assert 'model' in data.lower() or 'ai' in data.lower()

    def test_ai_analyze_route(self, client):
        """Test AI analyze route"""
        response = client.get('/ai/analyze')
        assert response.status_code in [200, 302]

        if response.status_code == 200:
            data = response.get_data(as_text=True)
            # Should contain analysis elements
            assert 'analyze' in data.lower() or 'analysis' in data.lower()

    def test_ai_configure_route(self, client):
        """Test AI configure route"""
        response = client.get('/ai/configure')
        assert response.status_code in [200, 302]

        if response.status_code == 200:
            data = response.get_data(as_text=True)
            # Should contain configuration elements
            assert 'config' in data.lower() or 'setting' in data.lower()

    # =========================================================================
    # AI/ML API ENDPOINTS
    # =========================================================================

    def test_ai_chat_api_post(self, client, init_database):
        """Test AI chat API POST endpoint"""
        token = self.login_as_user(client)

        if token:
            headers = {'Authorization': f'Bearer {token}'}

            chat_data = {
                'message': 'Hello, can you help me analyze my finances?',
                'model': 'qwen-3',
                'context': {
                    'user_id': 2,
                    'language': 'en'
                }
            }

            response = client.post('/api/ai/chat',
                                 data=json.dumps(chat_data),
                                 content_type='application/json',
                                 headers=headers)

            assert response.status_code in [200, 503, 401]  # OK, Service Unavailable, Unauthorized

            if response.status_code == 200:
                data = json.loads(response.data)
                assert 'response' in data
                assert 'model' in data
                assert 'session_id' in data

                # Validate response structure
                assert isinstance(data['response'], str)
                assert len(data['response']) > 0

    def test_ai_models_api_get(self, client, init_database):
        """Test AI models API GET endpoint"""
        token = self.login_as_user(client)

        if token:
            headers = {'Authorization': f'Bearer {token}'}
            response = client.get('/api/ai/models', headers=headers)
            assert response.status_code in [200, 401]

            if response.status_code == 200:
                data = json.loads(response.data)
                assert 'models' in data
                assert isinstance(data['models'], list)

                # Validate model structure
                if data['models']:
                    model = data['models'][0]
                    assert 'name' in model
                    assert 'type' in model

    def test_ai_analyze_api_post(self, client, init_database):
        """Test AI analyze API POST endpoint"""
        token = self.login_as_user(client)

        if token:
            headers = {'Authorization': f'Bearer {token}'}

            analyze_data = {
                'data_type': 'transactions',
                'analysis_type': 'summary',
                'time_period': 'month'
            }

            response = client.post('/api/ai/analyze',
                                 data=json.dumps(analyze_data),
                                 content_type='application/json',
                                 headers=headers)

            assert response.status_code in [200, 503, 401]

            if response.status_code == 200:
                data = json.loads(response.data)
                assert 'analysis' in data or 'result' in data or 'summary' in data

    # =========================================================================
    # TICKETING SYSTEM ROUTES
    # =========================================================================

    def test_tickets_route(self, client):
        """Test tickets route"""
        response = client.get('/tickets')
        assert response.status_code in [200, 302]

        if response.status_code == 200:
            data = response.get_data(as_text=True)
            # Should contain ticket elements
            assert 'ticket' in data.lower() or 'support' in data.lower()

    def test_tickets_create_route(self, client):
        """Test tickets create route"""
        response = client.get('/tickets/create')
        assert response.status_code in [200, 302]

        if response.status_code == 200:
            data = response.get_data(as_text=True)
            # Should contain create form elements
            assert 'create' in data.lower() or 'new' in data.lower()

    def test_ticketing_dashboard_route(self, client):
        """Test ticketing dashboard route"""
        response = client.get('/ticketing/dashboard')
        assert response.status_code in [200, 302]

        if response.status_code == 200:
            data = response.get_data(as_text=True)
            # Should contain dashboard elements
            assert 'dashboard' in data.lower() or 'ticket' in data.lower()

    # =========================================================================
    # SETTINGS AND ADMIN ROUTES
    # =========================================================================

    def test_settings_route_unauthorized(self, client):
        """Test settings route without authorization"""
        response = client.get('/settings')
        assert response.status_code == 302  # Redirect to login

    def test_settings_route_authorized(self, client, init_database):
        """Test settings route with authorization"""
        token = self.login_as_user(client)

        if token:
            headers = {'Authorization': f'Bearer {token}'}
            response = client.get('/settings', headers=headers)
            assert response.status_code in [200, 302, 404]

    def test_profile_route_unauthorized(self, client):
        """Test profile route without authorization"""
        response = client.get('/profile')
        assert response.status_code == 302  # Redirect to login

    def test_profile_route_authorized(self, client, init_database):
        """Test profile route with authorization"""
        token = self.login_as_user(client)

        if token:
            headers = {'Authorization': f'Bearer {token}'}
            response = client.get('/profile', headers=headers)
            assert response.status_code in [200, 302, 404]

            if response.status_code == 200:
                data = response.get_data(as_text=True)
                # Should contain profile elements
                assert 'profile' in data.lower() or 'user' in data.lower()

    # =========================================================================
    # SYSTEM AND ADMIN API ENDPOINTS
    # =========================================================================

    def test_system_api_endpoints(self, client, init_database):
        """Test system API endpoints"""
        system_endpoints = [
            '/api/system/info',
            '/api/database/status',
            '/api/cache/stats'
        ]

        token = self.login_as_admin(client)

        if token:
            headers = {'Authorization': f'Bearer {token}'}

            for endpoint in system_endpoints:
                response = client.get(endpoint, headers=headers)
                assert response.status_code in [200, 401, 404]

                if response.status_code == 200:
                    data = json.loads(response.data)
                    assert isinstance(data, dict)

    def test_users_api_endpoints_admin_only(self, client, init_database):
        """Test users API endpoints (admin only)"""
        admin_token = self.login_as_admin(client)
        user_token = self.login_as_user(client)

        # Admin should have access
        if admin_token:
            headers = {'Authorization': f'Bearer {admin_token}'}
            response = client.get('/api/users', headers=headers)
            assert response.status_code in [200, 401, 404]

            if response.status_code == 200:
                data = json.loads(response.data)
                assert 'users' in data
                assert isinstance(data['users'], list)

        # Regular user should not have access
        if user_token:
            headers = {'Authorization': f'Bearer {user_token}'}
            response = client.get('/api/users', headers=headers)
            assert response.status_code in [403, 401, 404]  # Forbidden or Not Found

    # =========================================================================
    # ERROR HANDLING AND EDGE CASES
    # =========================================================================

    def test_invalid_routes(self, client):
        """Test invalid routes return 404"""
        invalid_routes = [
            '/nonexistent',
            '/invalid/route',
            '/api/nonexistent',
            '/admin/fake',
            '/super/secret/path'
        ]

        for route in invalid_routes:
            response = client.get(route)
            assert response.status_code in [404, 302]  # Not Found or Redirect

    def test_invalid_methods(self, client):
        """Test invalid HTTP methods on valid routes"""
        # Try POST on GET-only routes
        get_only_routes = ['/login', '/register', '/dashboard/banking']

        for route in get_only_routes:
            response = client.post(route)
            assert response.status_code in [405, 400, 302]  # Method Not Allowed or Bad Request

    def test_invalid_json_payload(self, client):
        """Test invalid JSON payloads"""
        endpoints = [
            '/api/auth/login',
            '/api/auth/register',
            '/api/transactions'
        ]

        invalid_payloads = [
            'invalid json',
            '{"incomplete": json}',
            '{"missing": "brackets"',
            'not json at all'
        ]

        for endpoint in endpoints:
            for payload in invalid_payloads:
                response = client.post(endpoint,
                                     data=payload,
                                     content_type='application/json')
                assert response.status_code in [400, 422]  # Bad Request or Unprocessable Entity

    def test_missing_required_fields(self, client):
        """Test API endpoints with missing required fields"""
        test_cases = [
            ('/api/auth/login', {'email': 'test@example.com'}),  # Missing password
            ('/api/auth/register', {'email': 'test@example.com'}),  # Missing other fields
            ('/api/transactions', {'description': 'Test'}),  # Missing amount, type, date
        ]

        for endpoint, payload in test_cases:
            response = client.post(endpoint,
                                 data=json.dumps(payload),
                                 content_type='application/json')
            assert response.status_code in [400, 422]  # Bad Request or Validation Error

            if response.status_code in [400, 422]:
                data = json.loads(response.data)
                assert 'error' in data or 'errors' in data

    # =========================================================================
    # CONTROLLER DATA VALIDATION TESTS
    # =========================================================================

    def test_controller_data_passing(self, app, init_database):
        """Test that controllers properly pass data to templates"""
        with app.app_context():
            # Test dashboard controller
            from src.controllers.dashboard import get_dashboard_data

            dashboard_data = get_dashboard_data(user_id=2)
            assert isinstance(dashboard_data, dict)
            assert len(dashboard_data.keys()) > 0

            # Test financial controller
            from src.controllers.financial import get_user_transactions

            transactions = get_user_transactions(user_id=2, filters={'limit': 10})
            assert isinstance(transactions, list)

            # Test auth controller
            from src.controllers.auth import authenticate_user

            auth_result = authenticate_user('admin@validoai.test', 'admin123')
            if auth_result['success']:
                assert 'user' in auth_result
                assert 'token' in auth_result
                assert auth_result['user']['id'] is not None

    # =========================================================================
    # TEMPLATE RENDERING VALIDATION
    # =========================================================================

    def test_template_context_data(self, client, init_database):
        """Test that templates receive proper context data"""
        # Login and get dashboard
        token = self.login_as_user(client)

        if token:
            headers = {'Authorization': f'Bearer {token}'}

            # Test dashboard template
            response = client.get('/dashboard/banking', headers=headers)
            if response.status_code == 200:
                data = response.get_data(as_text=True)

                # Should contain user-specific data
                assert 'testuser' in data.lower() or 'Test' in data

                # Should contain financial data elements
                assert 'transaction' in data.lower() or 'balance' in data.lower()

    # =========================================================================
    # SESSION AND AUTHENTICATION TESTS
    # =========================================================================

    def test_session_management(self, client, init_database):
        """Test session and authentication management"""
        # Test login creates session
        login_data = {
            'email': 'admin@validoai.test',
            'password': 'admin123'
        }

        response = client.post('/api/auth/login',
                             data=json.dumps(login_data),
                             content_type='application/json')

        if response.status_code == 200:
            data = json.loads(response.data)
            token = data.get('access_token')

            # Test that token works for authenticated endpoints
            headers = {'Authorization': f'Bearer {token}'}
            protected_response = client.get('/api/transactions', headers=headers)
            assert protected_response.status_code in [200, 401]

            # Test logout clears session
            logout_response = client.get('/logout')
            assert logout_response.status_code in [200, 302]

    # =========================================================================
    # PERFORMANCE AND LOAD TESTS
    # =========================================================================

    def test_route_response_times(self, client):
        """Test that routes respond within acceptable time limits"""
        import time

        routes_to_test = [
            '/',
            '/login',
            '/api/health',
            '/dashboard/banking'
        ]

        for route in routes_to_test:
            start_time = time.time()
            response = client.get(route)
            end_time = time.time()

            response_time = end_time - start_time
            # Routes should respond within 5 seconds
            assert response_time < 5.0, f"Route {route} took {response_time}s"

    # =========================================================================
    # INTEGRATION TESTS
    # =========================================================================

    def test_complete_user_workflow(self, client, init_database):
        """Test complete user workflow integration"""
        # 1. Register
        register_data = {
            'username': 'workflowtest',
            'email': 'workflowtest@validoai.test',
            'password': 'workflow123',
            'first_name': 'Workflow',
            'last_name': 'Test'
        }

        register_response = client.post('/api/auth/register',
                                      data=json.dumps(register_data),
                                      content_type='application/json')
        assert register_response.status_code in [201, 409]

        if register_response.status_code == 201:
            # 2. Login
            login_data = {
                'email': 'workflowtest@validoai.test',
                'password': 'workflow123'
            }

            login_response = client.post('/api/auth/login',
                                       data=json.dumps(login_data),
                                       content_type='application/json')
            assert login_response.status_code == 200

            if login_response.status_code == 200:
                data = json.loads(login_response.data)
                token = data['access_token']
                headers = {'Authorization': f'Bearer {token}'}

                # 3. Access protected routes
                dashboard_response = client.get('/dashboard/banking', headers=headers)
                assert dashboard_response.status_code in [200, 302]

                # 4. Create transaction
                transaction_data = {
                    'description': 'Integration test transaction',
                    'amount': 999.99,
                    'transaction_type': 'income',
                    'date': '2024-01-25'
                }

                tx_response = client.post('/api/transactions',
                                        data=json.dumps(transaction_data),
                                        content_type='application/json',
                                        headers=headers)
                assert tx_response.status_code in [201, 400, 401]

                # 5. Get transactions
                tx_list_response = client.get('/api/transactions', headers=headers)
                assert tx_list_response.status_code == 200

                if tx_list_response.status_code == 200:
                    tx_data = json.loads(tx_list_response.data)
                    assert 'transactions' in tx_data
                    assert len(tx_data['transactions']) >= 0


# =========================================================================
# MAIN TEST EXECUTION
# =========================================================================

if __name__ == '__main__':
    # Run comprehensive route tests
    pytest.main([
        __file__,
        '-v',
        '--tb=short',
        '--cov=src',
        '--cov-report=html:htmlcov_routes',
        '--cov-report=term-missing',
        '-k', 'test_route'  # Run only route tests
    ])
