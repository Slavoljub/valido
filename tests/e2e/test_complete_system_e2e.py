"""
Complete System E2E Tests
Tests the entire application including all routes, webhooks, API integrations, and chat functionality
"""
import pytest
import json
import time
from unittest.mock import patch, AsyncMock, MagicMock
from flask import Flask
from flask.testing import FlaskClient
import asyncio


class TestCompleteSystemE2E:
    """Complete end-to-end system testing"""

    def test_all_main_routes_accessible(self, client: FlaskClient):
        """Test that all main application routes are accessible and return correct responses"""
        routes_to_test = [
            ('/', 'dashboard', ['dashboard', 'valido', 'financial', 'ai']),
            ('/chat-local', 'chat-local', ['chat', 'ai', 'local', 'model']),
            ('/settings', 'settings', ['settings', 'configuration', 'system']),
            ('/settings/questions', 'questions', ['question', 'category', 'ai', 'chat']),
            ('/settings/webhooks', 'webhooks', ['webhook', 'integration', 'api']),
            ('/ml-alg-demo', 'ml-demo', ['machine', 'learning', 'algorithm', 'demo']),
        ]

        for route, route_name, expected_keywords in routes_to_test:
            response = client.get(route)
            assert response.status_code == 200, f"Route {route} should return 200"

            content = response.data.decode('utf-8').lower()

            # Check that at least one expected keyword is present
            keyword_found = any(keyword in content for keyword in expected_keywords)
            assert keyword_found, f"Route {route} should contain one of {expected_keywords}"

            print(f"✅ Route {route} - OK (Status: {response.status_code})")

    def test_api_routes_functionality(self, client: FlaskClient):
        """Test all API routes return valid JSON responses"""
        api_routes = [
            '/api/v1/webhooks',
            '/api/v1/integrations',
            '/api/v1/webhooks/stats',
            '/api/v1/webhooks/events',
        ]

        for route in api_routes:
            response = client.get(route)
            assert response.status_code == 200, f"API route {route} should return 200"

            try:
                data = json.loads(response.data)
                assert isinstance(data, dict), f"Route {route} should return dict"
                assert 'success' in data, f"Route {route} should have 'success' field"
            except json.JSONDecodeError:
                pytest.fail(f"Route {route} should return valid JSON")

            print(f"✅ API Route {route} - OK (Status: {response.status_code})")

    def test_webhook_system_integration(self, client: FlaskClient):
        """Test complete webhook system integration"""
        from src.controllers.webhook_controller import webhook_controller

        # Clean up any existing test webhooks
        existing_webhooks = webhook_controller.get_webhooks()
        if existing_webhooks['success']:
            for webhook in existing_webhooks['data']:
                if webhook['name'].startswith('e2e_test_'):
                    webhook_controller.delete_webhook(webhook['id'])

        # Create test webhook
        webhook_data = {
            'name': 'e2e_test_webhook',
            'event_type': 'e2e_test_event',
            'url': 'https://httpbin.org/post',
            'method': 'POST',
            'is_active': True,
            'timeout': 10,
            'retry_count': 1
        }

        # Test webhook creation via API
        response = client.post('/api/v1/webhooks',
                             data=json.dumps(webhook_data),
                             content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        webhook_id = data['data']['id']

        # Test webhook retrieval via API
        response = client.get(f'/api/v1/webhooks/{webhook_id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['name'] == 'e2e_test_webhook'

        # Test webhook listing via API
        response = client.get('/api/v1/webhooks')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['total'] >= 1

        # Test webhook event triggering via API
        trigger_data = {
            'event_type': 'e2e_test_event',
            'payload': {
                'test_run': 'complete_system_e2e',
                'timestamp': time.time(),
                'source': 'e2e_test'
            }
        }

        response = client.post('/api/v1/webhooks/trigger',
                             data=json.dumps(trigger_data),
                             content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True

        # Test webhook event retrieval via API
        response = client.get('/api/v1/webhooks/events')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True

        # Test webhook statistics via API
        response = client.get('/api/v1/webhooks/stats')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'total_webhooks' in data['data']

        # Test webhook deletion via API
        response = client.delete(f'/api/v1/webhooks/{webhook_id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True

        print("✅ Webhook System Integration - OK")

    def test_api_integration_system(self, client: FlaskClient):
        """Test complete API integration system"""
        from src.controllers.webhook_controller import api_integration_controller

        # Clean up any existing test integrations
        existing_integrations = api_integration_controller.get_integrations()
        if existing_integrations['success']:
            for integration in existing_integrations['data']:
                if integration['name'].startswith('e2e_test_'):
                    api_integration_controller.delete_integration(integration['id'])

        # Create test API integration
        integration_data = {
            'name': 'e2e_test_bank_api',
            'provider_type': 'bank',
            'base_url': 'https://api.testbank.com',
            'auth_type': 'basic',
            'auth_config': {
                'username': 'test_user',
                'password': 'test_pass'
            },
            'headers': {
                'User-Agent': 'ValidoAI-E2E-Test/1.0'
            },
            'timeout': 30,
            'retry_count': 2,
            'is_active': True,
            'description': 'E2E test bank API integration'
        }

        # Test integration creation via API
        response = client.post('/api/v1/integrations',
                             data=json.dumps(integration_data),
                             content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        integration_id = data['data']['id']

        # Test integration retrieval via API
        response = client.get(f'/api/v1/integrations/{integration_id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['name'] == 'e2e_test_bank_api'

        # Test integration listing via API
        response = client.get('/api/v1/integrations')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['total'] >= 1

        # Test integration update via API
        update_data = {
            'name': 'e2e_test_bank_api_updated',
            'timeout': 60,
            'description': 'Updated E2E test integration'
        }

        response = client.put(f'/api/v1/integrations/{integration_id}',
                            data=json.dumps(update_data),
                            content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True

        # Test integration deletion via API
        response = client.delete(f'/api/v1/integrations/{integration_id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True

        print("✅ API Integration System - OK")

    def test_question_management_integration(self, client: FlaskClient):
        """Test question management system integration"""
        # Test questions route
        response = client.get('/settings/questions')
        assert response.status_code == 200
        assert b'question' in response.data.lower()

        # Test question categories API
        response = client.get('/api/questions/categories')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True

        # Test question suggestions API
        response = client.get('/api/questions/suggestions?category=all')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True

        print("✅ Question Management Integration - OK")

    def test_chat_functionality_integration(self, client: FlaskClient):
        """Test chat functionality integration"""
        # Test chat-local route
        response = client.get('/chat-local')
        assert response.status_code == 200
        assert b'chat' in response.data.lower()

        # Test that webhook integration is present in chat template
        content = response.data.decode('utf-8')
        assert 'triggerWebhook' in content, "Chat should have webhook integration"
        assert 'triggerChatMessageWebhook' in content, "Chat should have chat message webhook"

        print("✅ Chat Functionality Integration - OK")

    def test_settings_integration(self, client: FlaskClient):
        """Test settings system integration"""
        # Test main settings route
        response = client.get('/settings')
        assert response.status_code == 200
        assert b'settings' in response.data.lower()

        # Test webhooks settings route
        response = client.get('/settings/webhooks')
        assert response.status_code == 200
        assert b'webhook' in response.data.lower()

        print("✅ Settings Integration - OK")

    def test_system_health_check(self, client: FlaskClient):
        """Test system health and monitoring"""
        # Test that the application can handle multiple requests
        for i in range(5):
            response = client.get('/')
            assert response.status_code == 200

        # Test API endpoints under load
        for i in range(3):
            response = client.get('/api/v1/webhooks')
            assert response.status_code == 200
            response = client.get('/api/v1/integrations')
            assert response.status_code == 200

        print("✅ System Health Check - OK")

    def test_error_handling(self, client: FlaskClient):
        """Test error handling across the system"""
        # Test invalid API calls
        response = client.get('/api/v1/webhooks/99999')
        # Should return 404 or success: false
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = json.loads(response.data)
            assert data['success'] is False

        # Test invalid integration calls
        response = client.get('/api/v1/integrations/99999')
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = json.loads(response.data)
            assert data['success'] is False

        # Test invalid webhook operations
        response = client.post('/api/v1/webhooks',
                             data=json.dumps({'invalid': 'data'}),
                             content_type='application/json')
        assert response.status_code in [200, 400]
        if response.status_code == 200:
            data = json.loads(response.data)
            assert data['success'] is False

        print("✅ Error Handling - OK")

    @pytest.mark.asyncio
    async def test_webhook_async_processing(self):
        """Test asynchronous webhook processing"""
        from src.controllers.webhook_controller import webhook_controller

        # Create test webhook
        webhook_data = {
            'name': 'async_test_webhook',
            'event_type': 'async_test',
            'url': 'https://httpbin.org/post',
            'is_active': True
        }

        result = webhook_controller.create_webhook(webhook_data)
        assert result['success'] is True
        webhook_id = result['data']['id']

        # Mock async webhook processing
        with patch('src.services.webhook_service.webhook_service.trigger_webhook', new_callable=AsyncMock) as mock_trigger:
            mock_trigger.return_value = [
                {
                    'subscription_id': webhook_id,
                    'success': True,
                    'status_code': 200
                }
            ]

            # Trigger webhook event
            trigger_result = webhook_controller.trigger_webhook_event('async_test', {'test': 'async'})
            assert trigger_result['success'] is True

            # Verify async processing was called
            mock_trigger.assert_called_once()

        # Clean up
        webhook_controller.delete_webhook(webhook_id)

        print("✅ Async Webhook Processing - OK")

    def test_database_integrity(self, client: FlaskClient):
        """Test database integrity and relationships"""
        from src.models.webhook_models import webhook_manager, api_integration_manager

        # Test webhook database operations
        webhook_data = {
            'name': 'integrity_test_webhook',
            'event_type': 'integrity_test',
            'url': 'https://example.com/webhook',
            'is_active': True
        }

        webhook_id = webhook_manager.create_subscription(
            type('WebhookSubscription', (), webhook_data)()
        )

        # Verify webhook was created
        webhooks = webhook_manager.get_subscriptions()
        assert len([w for w in webhooks if w.id == webhook_id]) == 1

        # Test API integration database operations
        integration_data = {
            'name': 'integrity_test_integration',
            'provider_type': 'test',
            'base_url': 'https://test.com',
            'is_active': True
        }

        integration_id = api_integration_manager.create_integration(
            type('APIIntegration', (), integration_data)()
        )

        # Verify integration was created
        integrations = api_integration_manager.get_integrations()
        assert len([i for i in integrations if i.id == integration_id]) == 1

        # Clean up
        webhook_manager.delete_subscription(webhook_id)
        api_integration_manager.delete_integration(integration_id)

        print("✅ Database Integrity - OK")

    def test_complete_user_workflow(self, client: FlaskClient):
        """Test complete user workflow from start to finish"""
        # 1. User visits dashboard
        response = client.get('/')
        assert response.status_code == 200

        # 2. User goes to settings
        response = client.get('/settings')
        assert response.status_code == 200

        # 3. User creates a webhook
        webhook_data = {
            'name': 'user_workflow_test',
            'event_type': 'user_test',
            'url': 'https://httpbin.org/post',
            'is_active': True
        }

        response = client.post('/api/v1/webhooks',
                             data=json.dumps(webhook_data),
                             content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        webhook_id = data['data']['id']

        # 4. User goes to chat
        response = client.get('/chat-local')
        assert response.status_code == 200

        # 5. User creates API integration
        integration_data = {
            'name': 'user_workflow_integration',
            'provider_type': 'bank',
            'base_url': 'https://api.testbank.com',
            'auth_type': 'none',
            'is_active': True
        }

        response = client.post('/api/v1/integrations',
                             data=json.dumps(integration_data),
                             content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        integration_id = data['data']['id']

        # 6. User triggers webhook event
        trigger_data = {
            'event_type': 'user_test',
            'payload': {'user_workflow': 'completed'}
        }

        response = client.post('/api/v1/webhooks/trigger',
                             data=json.dumps(trigger_data),
                             content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True

        # 7. User checks webhook events
        response = client.get('/api/v1/webhooks/events')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True

        # 8. User cleans up
        response = client.delete(f'/api/v1/webhooks/{webhook_id}')
        assert response.status_code == 200

        response = client.delete(f'/api/v1/integrations/{integration_id}')
        assert response.status_code == 200

        print("✅ Complete User Workflow - OK")

    def test_system_performance(self, client: FlaskClient):
        """Test system performance under load"""
        import time

        # Test response times for critical routes
        routes_to_benchmark = [
            '/',
            '/chat-local',
            '/settings',
            '/settings/webhooks',
            '/api/v1/webhooks',
            '/api/v1/integrations'
        ]

        for route in routes_to_benchmark:
            start_time = time.time()
            response = client.get(route)
            end_time = time.time()

            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            assert response.status_code == 200
            assert response_time < 5000  # Should respond within 5 seconds

            print(".2f")

        print("✅ System Performance - OK")

    def test_security_headers(self, client: FlaskClient):
        """Test security headers are present"""
        response = client.get('/')

        # Check for basic security headers
        headers = dict(response.headers)
        security_headers = [
            'X-Content-Type-Options',
            'X-Frame-Options',
            'X-XSS-Protection'
        ]

        for header in security_headers:
            assert header in headers, f"Security header {header} should be present"

        print("✅ Security Headers - OK")


# Test configuration
def pytest_configure(config):
    """Configure pytest for e2e tests"""
    config.addinivalue_line(
        "markers", "e2e: mark test as end-to-end test"
    )


@pytest.fixture(scope="session")
def client():
    """Create test client"""
    from app import app
    app.config['TESTING'] = True
    return app.test_client()


@pytest.fixture(autouse=True)
def cleanup_test_data():
    """Clean up test data after each test"""
    yield
    # Cleanup code would go here if needed
