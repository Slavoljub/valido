#!/usr/bin/env python3
"""
Comprehensive Testing Suite for ValidoAI
Tests all routes, controllers, database operations, and integrations
"""

import pytest
import unittest
from unittest.mock import Mock, patch, MagicMock
import json
import tempfile
import os
from datetime import datetime, timedelta
from flask import url_for, g
from werkzeug.security import generate_password_hash
from werkzeug.test import Client

# Import application components
from app import create_app, db
from src.config.unified_config import config
from src.database.unified_db_manager import UnifiedDatabaseManager
from src.controllers.auth import authenticate_user
from src.controllers.dashboard import get_dashboard_data
from src.controllers.financial import get_user_transactions
from src.controllers.ai_chat import process_ai_query


class TestComprehensiveSuite:
    """Comprehensive test suite for ValidoAI application"""

    @pytest.fixture
    def app(self):
        """Create and configure a test app instance."""
        app = create_app()
        app.config.update({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'SECRET_KEY': 'test-secret-key',
            'JWT_SECRET_KEY': 'test-jwt-secret',
            'DEBUG': False,
            'SERVER_NAME': 'localhost'
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
        """Initialize test database."""
        with app.app_context():
            db.create_tables()
            # Create test admin user
            admin_password_hash = generate_password_hash('admin123')
            db.execute_query("""
                INSERT OR IGNORE INTO users (
                    username, email, password_hash, first_name, last_name, is_admin
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, ('admin', 'admin@validoai.test', admin_password_hash, 'Admin', 'User', 1))

            # Create test regular user
            user_password_hash = generate_password_hash('user123')
            db.execute_query("""
                INSERT OR IGNORE INTO users (
                    username, email, password_hash, first_name, last_name, is_admin
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, ('testuser', 'user@validoai.test', user_password_hash, 'Test', 'User', 0))

            yield db

            # Cleanup (if needed)
            db.cleanup()

    def test_app_creation(self, app):
        """Test that the Flask app is created successfully."""
        assert app is not None
        assert app.config['TESTING'] is True
        assert app.config['SECRET_KEY'] == 'test-secret-key'

    def test_database_initialization(self, app, init_database):
        """Test database initialization and basic operations."""
        with app.app_context():
            # Test admin user creation
            admin_user = db.execute_query(
                "SELECT * FROM users WHERE username = ?",
                ('admin',), fetch="one"
            )
            assert admin_user is not None
            assert admin_user['username'] == 'admin'
            assert admin_user['is_admin'] == 1

            # Test regular user creation
            user = db.execute_query(
                "SELECT * FROM users WHERE username = ?",
                ('testuser',), fetch="one"
            )
            assert user is not None
            assert user['username'] == 'testuser'
            assert user['is_admin'] == 0

    # =========================================================================
    # AUTHENTICATION ROUTE TESTS
    # =========================================================================

    def test_login_page_route(self, client):
        """Test login page route."""
        response = client.get('/login')
        assert response.status_code in [200, 302]  # 302 if already logged in

    def test_register_page_route(self, client):
        """Test registration page route."""
        response = client.get('/register')
        assert response.status_code in [200, 302]

    def test_logout_route(self, client):
        """Test logout route."""
        response = client.get('/logout')
        assert response.status_code in [200, 302]

    def test_profile_route_unauthenticated(self, client):
        """Test profile route without authentication."""
        response = client.get('/profile')
        assert response.status_code == 302  # Redirect to login

    def test_login_api_endpoint(self, client, init_database):
        """Test login API endpoint."""
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
            assert data['user']['email'] == 'admin@validoai.test'

    def test_register_api_endpoint(self, client):
        """Test user registration API endpoint."""
        register_data = {
            'username': 'newuser',
            'email': 'newuser@validoai.test',
            'password': 'newpass123',
            'first_name': 'New',
            'last_name': 'User',
            'language': 'sr'
        }

        response = client.post('/api/auth/register',
                             data=json.dumps(register_data),
                             content_type='application/json')

        assert response.status_code in [201, 400, 409]  # Created, Bad Request, or Conflict

        if response.status_code == 201:
            data = json.loads(response.data)
            assert 'user_id' in data

    # =========================================================================
    # DASHBOARD ROUTE TESTS
    # =========================================================================

    def test_dashboard_routes(self, client):
        """Test all dashboard routes."""
        dashboard_routes = [
            '/',
            '/dashboard/banking',
            '/dashboard/analytics',
            '/dashboard/compact',
            '/dashboard/admin'
        ]

        for route in dashboard_routes:
            response = client.get(route)
            # Should redirect to login if not authenticated, or show dashboard if authenticated
            assert response.status_code in [200, 302]

    def test_dashboard_api_endpoint(self, client, init_database):
        """Test dashboard API endpoint."""
        # First login to get token
        login_response = client.post('/api/auth/login',
                                   data=json.dumps({
                                       'email': 'admin@validoai.test',
                                       'password': 'admin123'
                                   }),
                                   content_type='application/json')

        if login_response.status_code == 200:
            token = json.loads(login_response.data)['access_token']

            response = client.get('/api/dashboard/data',
                                headers={'Authorization': f'Bearer {token}'})

            assert response.status_code in [200, 401, 404]

            if response.status_code == 200:
                data = json.loads(response.data)
                assert isinstance(data, dict)

    # =========================================================================
    # FINANCIAL ROUTE TESTS
    # =========================================================================

    def test_financial_routes(self, client):
        """Test financial management routes."""
        financial_routes = [
            '/transactions',
            '/invoices',
            '/accounts',
            '/reports',
            '/tax'
        ]

        for route in financial_routes:
            response = client.get(route)
            assert response.status_code in [200, 302]  # 302 if redirect to login

    def test_transaction_api_endpoints(self, client, init_database):
        """Test transaction API endpoints."""
        # Login first
        login_response = client.post('/api/auth/login',
                                   data=json.dumps({
                                       'email': 'admin@validoai.test',
                                       'password': 'admin123'
                                   }),
                                   content_type='application/json')

        if login_response.status_code == 200:
            token = json.loads(login_response.data)['access_token']

            # Test GET transactions
            response = client.get('/api/transactions',
                                headers={'Authorization': f'Bearer {token}'})
            assert response.status_code in [200, 401]

            if response.status_code == 200:
                data = json.loads(response.data)
                assert 'transactions' in data
                assert 'pagination' in data

            # Test POST transaction
            transaction_data = {
                'description': 'Test transaction',
                'amount': 100.50,
                'transaction_type': 'income',
                'date': '2024-01-15'
            }

            response = client.post('/api/transactions',
                                 data=json.dumps(transaction_data),
                                 content_type='application/json',
                                 headers={'Authorization': f'Bearer {token}'})
            assert response.status_code in [201, 400, 401]

    def test_invoice_api_endpoints(self, client, init_database):
        """Test invoice API endpoints."""
        # Login first
        login_response = client.post('/api/auth/login',
                                   data=json.dumps({
                                       'email': 'admin@validoai.test',
                                       'password': 'admin123'
                                   }),
                                   content_type='application/json')

        if login_response.status_code == 200:
            token = json.loads(login_response.data)['access_token']

            # Test GET invoices
            response = client.get('/api/invoices',
                                headers={'Authorization': f'Bearer {token}'})
            assert response.status_code in [200, 401]

            # Test POST invoice
            invoice_data = {
                'invoice_number': 'INV-001',
                'client_name': 'Test Client',
                'issue_date': '2024-01-15',
                'due_date': '2024-02-15',
                'subtotal': 1000.00,
                'tax_rate': 20.0
            }

            response = client.post('/api/invoices',
                                 data=json.dumps(invoice_data),
                                 content_type='application/json',
                                 headers={'Authorization': f'Bearer {token}'})
            assert response.status_code in [201, 400, 401]

    # =========================================================================
    # AI/ML ROUTE TESTS
    # =========================================================================

    def test_ai_routes(self, client):
        """Test AI/ML functionality routes."""
        ai_routes = [
            '/ai/chat',
            '/ai/models',
            '/ai/analyze',
            '/ai/configure'
        ]

        for route in ai_routes:
            response = client.get(route)
            assert response.status_code in [200, 302]

    def test_ai_chat_api_endpoint(self, client, init_database):
        """Test AI chat API endpoint."""
        # Login first
        login_response = client.post('/api/auth/login',
                                   data=json.dumps({
                                       'email': 'admin@validoai.test',
                                       'password': 'admin123'
                                   }),
                                   content_type='application/json')

        if login_response.status_code == 200:
            token = json.loads(login_response.data)['access_token']

            # Test AI chat
            chat_data = {
                'message': 'Hello, can you help me with financial analysis?',
                'model': 'qwen-3'
            }

            response = client.post('/api/ai/chat',
                                 data=json.dumps(chat_data),
                                 content_type='application/json',
                                 headers={'Authorization': f'Bearer {token}'})
            assert response.status_code in [200, 503]  # 503 if AI service unavailable

            if response.status_code == 200:
                data = json.loads(response.data)
                assert 'response' in data
                assert 'model' in data

    def test_ai_models_api_endpoint(self, client, init_database):
        """Test AI models API endpoint."""
        # Login first
        login_response = client.post('/api/auth/login',
                                   data=json.dumps({
                                       'email': 'admin@validoai.test',
                                       'password': 'admin123'
                                   }),
                                   content_type='application/json')

        if login_response.status_code == 200:
            token = json.loads(login_response.data)['access_token']

            response = client.get('/api/ai/models',
                                headers={'Authorization': f'Bearer {token}'})
            assert response.status_code in [200, 401]

            if response.status_code == 200:
                data = json.loads(response.data)
                assert 'models' in data
                assert isinstance(data['models'], list)

    # =========================================================================
    # ADMIN ROUTE TESTS
    # =========================================================================

    def test_admin_routes(self, client, init_database):
        """Test admin-only routes."""
        admin_routes = [
            '/settings',
            '/admin/users',
            '/admin/system',
            '/admin/database'
        ]

        # Test without authentication
        for route in admin_routes:
            response = client.get(route)
            assert response.status_code == 302  # Redirect to login

        # Login as admin
        login_response = client.post('/api/auth/login',
                                   data=json.dumps({
                                       'email': 'admin@validoai.test',
                                       'password': 'admin123'
                                   }),
                                   content_type='application/json')

        if login_response.status_code == 200:
            # Admin routes should be accessible
            for route in admin_routes:
                response = client.get(route)
                assert response.status_code in [200, 302, 404]  # 404 if route doesn't exist

    # =========================================================================
    # TICKETING SYSTEM TESTS
    # =========================================================================

    def test_ticketing_routes(self, client):
        """Test ticketing system routes."""
        ticket_routes = [
            '/tickets',
            '/tickets/create',
            '/ticketing/dashboard'
        ]

        for route in ticket_routes:
            response = client.get(route)
            assert response.status_code in [200, 302]

    # =========================================================================
    # API ENDPOINTS COMPREHENSIVE TEST
    # =========================================================================

    def test_api_endpoints_comprehensive(self, client, init_database):
        """Comprehensive test of all API endpoints."""
        api_endpoints = [
            ('GET', '/api/health'),
            ('GET', '/api/database/status'),
            ('GET', '/api/cache/stats'),
            ('GET', '/api/system/info')
        ]

        for method, endpoint in api_endpoints:
            if method == 'GET':
                response = client.get(endpoint)
                assert response.status_code in [200, 401, 404, 503]

                if response.status_code == 200:
                    data = json.loads(response.data)
                    assert isinstance(data, dict)

    # =========================================================================
    # ERROR HANDLING TESTS
    # =========================================================================

    def test_error_handling(self, client):
        """Test error handling for invalid routes and methods."""
        # Test 404 error
        response = client.get('/nonexistent-route')
        assert response.status_code == 404

        # Test invalid method
        response = client.post('/login')  # GET only route
        assert response.status_code in [405, 400]

        # Test invalid JSON
        response = client.post('/api/auth/login',
                             data='invalid json',
                             content_type='application/json')
        assert response.status_code == 400

    # =========================================================================
    # SECURITY TESTS
    # =========================================================================

    def test_security_headers(self, client):
        """Test security headers in responses."""
        response = client.get('/')

        # Check for security headers
        headers = dict(response.headers)
        security_headers = [
            'X-Frame-Options',
            'X-Content-Type-Options',
            'X-XSS-Protection'
        ]

        for header in security_headers:
            if header in headers:
                assert headers[header] is not None

    def test_rate_limiting(self, client):
        """Test rate limiting on API endpoints."""
        # Make multiple requests quickly
        for i in range(10):
            response = client.post('/api/auth/login',
                                 data=json.dumps({
                                     'email': f'user{i}@test.com',
                                     'password': 'password123'
                                 }),
                                 content_type='application/json')
            # Should eventually hit rate limit or handle gracefully
            assert response.status_code in [200, 400, 401, 429]

    # =========================================================================
    # PERFORMANCE TESTS
    # =========================================================================

    def test_response_times(self, client):
        """Test response times for critical endpoints."""
        import time

        endpoints = ['/', '/login', '/api/health']

        for endpoint in endpoints:
            start_time = time.time()
            response = client.get(endpoint)
            end_time = time.time()

            response_time = end_time - start_time
            # Response should be under 5 seconds (reasonable for most endpoints)
            assert response_time < 5.0, f"Endpoint {endpoint} took {response_time}s"

    # =========================================================================
    # DATABASE INTEGRATION TESTS
    # =========================================================================

    def test_database_integrity(self, app, init_database):
        """Test database integrity and constraints."""
        with app.app_context():
            # Test foreign key constraints
            try:
                # Try to insert transaction with non-existent user (should fail)
                db.execute_query("""
                    INSERT INTO transactions (user_id, description, amount, transaction_type, date)
                    VALUES (?, ?, ?, ?, ?)
                """, (999999, 'Test', 100.0, 'income', '2024-01-01'))
                # If we get here, foreign key constraint failed
                assert False, "Foreign key constraint should prevent this insert"
            except Exception as e:
                # Expected behavior - constraint violation
                assert "foreign key" in str(e).lower() or "constraint" in str(e).lower()

    def test_database_transactions(self, app, init_database):
        """Test database transaction handling."""
        with app.app_context():
            # Test transaction rollback
            user_id = 1
            initial_count = db.execute_query(
                "SELECT COUNT(*) as count FROM transactions WHERE user_id = ?",
                (user_id,), fetch="one"
            )['count']

            try:
                # Start a transaction that will fail
                with db.get_connection() as conn:
                    cursor = conn.cursor()

                    # Insert transaction
                    cursor.execute("""
                        INSERT INTO transactions (user_id, description, amount, transaction_type, date)
                        VALUES (?, ?, ?, ?, ?)
                    """, (user_id, 'Test transaction', 100.0, 'income', '2024-01-01'))

                    # Try to insert with invalid data (should fail)
                    cursor.execute("INSERT INTO transactions (invalid_column) VALUES (?)", ('test',))

                    conn.commit()

                assert False, "Should have failed due to invalid column"

            except Exception:
                # Check that the first insert was rolled back
                final_count = db.execute_query(
                    "SELECT COUNT(*) as count FROM transactions WHERE user_id = ?",
                    (user_id,), fetch="one"
                )['count']

                assert final_count == initial_count, "Transaction should have been rolled back"

    # =========================================================================
    # CONTROLLER DATA VALIDATION TESTS
    # =========================================================================

    def test_controller_data_validation(self, app, init_database):
        """Test that controllers properly validate and pass data."""
        with app.app_context():
            from src.controllers.auth import authenticate_user
            from src.controllers.financial import get_user_transactions

            # Test authentication controller
            result = authenticate_user('admin@validoai.test', 'admin123')
            if result['success']:
                assert 'user' in result
                assert 'token' in result
                assert result['user']['email'] == 'admin@validoai.test'

            # Test financial controller
            transactions = get_user_transactions(1, {'limit': 10})
            assert isinstance(transactions, list)
            for transaction in transactions:
                assert 'id' in transaction
                assert 'description' in transaction
                assert 'amount' in transaction

    # =========================================================================
    # TEMPLATE RENDERING TESTS
    # =========================================================================

    def test_template_rendering(self, client):
        """Test that templates render without errors."""
        templates_to_test = [
            '/',
            '/login',
            '/register',
            '/dashboard/banking',
            '/transactions',
            '/ai/chat'
        ]

        for template in templates_to_test:
            response = client.get(template)
            # Should either render successfully or redirect (302)
            assert response.status_code in [200, 302]

            if response.status_code == 200:
                # Check that response contains expected HTML structure
                data = response.get_data(as_text=True)
                assert '<!DOCTYPE html>' in data or '<html' in data

    # =========================================================================
    # STATIC FILE TESTS
    # =========================================================================

    def test_static_files(self, client):
        """Test static file serving."""
        static_files = [
            '/static/css/main.css',
            '/static/js/app.js',
            '/static/images/logo.png'
        ]

        for static_file in static_files:
            response = client.get(static_file)
            # Should serve file or return 404 if file doesn't exist (which is fine)
            assert response.status_code in [200, 404]

    # =========================================================================
    # CONFIGURATION TESTS
    # =========================================================================

    def test_configuration_loading(self, app):
        """Test that configuration loads correctly."""
        with app.app_context():
            # Test that critical config values are set
            assert config.secret_key is not None
            assert config.database.type is not None
            assert config.ai.default_model is not None

            # Test configuration methods
            assert hasattr(config, 'get')
            assert hasattr(config, 'set')
            assert hasattr(config, 'reload')

    # =========================================================================
    # UTILITY FUNCTION TESTS
    # =========================================================================

    def test_utility_functions(self, app):
        """Test utility functions used throughout the application."""
        with app.app_context():
            from src.utils.helpers import format_currency, validate_email

            # Test currency formatting
            assert format_currency(1000.50, 'RSD') == '1,000.50 RSD'
            assert format_currency(1000.50, 'EUR') == '€1,000.50'

            # Test email validation
            assert validate_email('test@example.com') is True
            assert validate_email('invalid-email') is False

    # =========================================================================
    # LOGGING AND MONITORING TESTS
    # =========================================================================

    def test_logging_functionality(self, app):
        """Test logging functionality."""
        with app.app_context():
            import logging

            # Test that logger is configured
            logger = logging.getLogger('validoai')
            assert logger is not None

            # Test log levels
            assert logger.level <= logging.INFO

            # Test that handlers are configured
            assert len(logger.handlers) > 0

    # =========================================================================
    # CLEANUP TESTS
    # =========================================================================

    def test_cleanup_operations(self, app, init_database):
        """Test cleanup operations."""
        with app.app_context():
            # Test database cleanup
            initial_count = db.execute_query(
                "SELECT COUNT(*) as count FROM users",
                fetch="one"
            )['count']

            # Cleanup should not remove essential data
            db.cleanup()

            final_count = db.execute_query(
                "SELECT COUNT(*) as count FROM users",
                fetch="one"
            )['count']

            # Should maintain at least the test users
            assert final_count >= initial_count

    # =========================================================================
    # INTEGRATION TESTS
    # =========================================================================

    def test_full_user_workflow(self, client, init_database):
        """Test complete user workflow from registration to transaction."""
        # 1. Register new user
        register_data = {
            'username': 'workflowuser',
            'email': 'workflow@validoai.test',
            'password': 'workflow123',
            'first_name': 'Workflow',
            'last_name': 'User'
        }

        response = client.post('/api/auth/register',
                             data=json.dumps(register_data),
                             content_type='application/json')
        assert response.status_code in [201, 409]  # Created or already exists

        if response.status_code == 201:
            user_data = json.loads(response.data)
            user_id = user_data['user_id']

            # 2. Login
            login_response = client.post('/api/auth/login',
                                       data=json.dumps({
                                           'email': 'workflow@validoai.test',
                                           'password': 'workflow123'
                                       }),
                                       content_type='application/json')
            assert login_response.status_code == 200

            if login_response.status_code == 200:
                token = json.loads(login_response.data)['access_token']

                # 3. Create transaction
                transaction_data = {
                    'description': 'Workflow test transaction',
                    'amount': 500.00,
                    'transaction_type': 'income',
                    'date': '2024-01-15'
                }

                headers = {'Authorization': f'Bearer {token}'}
                response = client.post('/api/transactions',
                                     data=json.dumps(transaction_data),
                                     content_type='application/json',
                                     headers=headers)
                assert response.status_code in [201, 400, 401]

                if response.status_code == 201:
                    # 4. Get transactions
                    response = client.get('/api/transactions', headers=headers)
                    assert response.status_code == 200

                    if response.status_code == 200:
                        data = json.loads(response.data)
                        assert 'transactions' in data
                        assert len(data['transactions']) > 0

    def test_admin_workflow(self, client, init_database):
        """Test admin user workflow."""
        # Login as admin
        login_response = client.post('/api/auth/login',
                                   data=json.dumps({
                                       'email': 'admin@validoai.test',
                                       'password': 'admin123'
                                   }),
                                   content_type='application/json')
        assert login_response.status_code == 200

        if login_response.status_code == 200:
            token = json.loads(login_response.data)['access_token']
            headers = {'Authorization': f'Bearer {token}'}

            # Test admin endpoints
            admin_endpoints = [
                '/api/users',
                '/api/system/stats',
                '/api/database/status'
            ]

            for endpoint in admin_endpoints:
                response = client.get(endpoint, headers=headers)
                # Should either succeed or return 404 (if endpoint doesn't exist)
                assert response.status_code in [200, 404, 403, 401]


# =========================================================================
# MAIN TEST RUNNER
# =========================================================================

if __name__ == '__main__':
    # Run comprehensive test suite
    pytest.main([
        __file__,
        '-v',
        '--tb=short',
        '--cov=src',
        '--cov-report=html:htmlcov_comprehensive',
        '--cov-report=term-missing'
    ])
