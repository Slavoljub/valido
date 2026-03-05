"""
Integration Tests for Chat-Local Route with Webhook System
Tests the complete integration between chat functionality and webhook system
"""
import pytest
import json
from unittest.mock import patch, AsyncMock, MagicMock
from flask import Flask
from flask.testing import FlaskClient
import asyncio


class TestChatWebhookIntegration:
    """Test chat-local route integration with webhooks"""

    def setup_method(self):
        """Setup test environment"""
        from src.models.webhook_models import webhook_manager
        webhook_manager._init_database()

    def test_chat_route_response(self, client: FlaskClient):
        """Test that /chat-local route returns correct response"""
        response = client.get('/chat-local')
        assert response.status_code == 200
        assert b'chat-local' in response.data or b'Chat' in response.data

    def test_chat_route_webhook_integration(self, client: FlaskClient):
        """Test webhook integration in chat route"""
        # Create a test webhook for chat messages
        from src.controllers.webhook_controller import webhook_controller

        webhook_data = {
            'name': 'test_chat_integration',
            'event_type': 'chat_message',
            'url': 'https://httpbin.org/post',
            'method': 'POST',
            'is_active': True
        }

        result = webhook_controller.create_webhook(webhook_data)
        assert result['success'] is True
        webhook_id = result['data']['id']

        # Test that webhook is registered
        webhooks = webhook_controller.get_webhooks(event_type='chat_message')
        assert webhooks['success'] is True
        assert len(webhooks['data']) > 0

        # Clean up
        webhook_controller.delete_webhook(webhook_id)

    @pytest.mark.asyncio
    async def test_chat_webhook_triggering_simulation(self):
        """Simulate webhook triggering from chat events"""
        from src.controllers.webhook_controller import webhook_controller

        # Create webhook
        webhook_data = {
            'name': 'test_chat_simulation',
            'event_type': 'chat_message',
            'url': 'https://httpbin.org/post',
            'is_active': True
        }

        result = webhook_controller.create_webhook(webhook_data)
        webhook_id = result['data']['id']

        # Simulate chat message event
        chat_payload = {
            'chat_id': 'simulated_chat_001',
            'user_id': 'test_user_001',
            'message': {
                'text': 'Hello, this is a test message',
                'attachments': 0,
                'model': 'gpt-3.5-turbo'
            },
            'response': {
                'text': 'Hello! How can I help you today?',
                'model': 'gpt-3.5-turbo',
                'provider': 'openai'
            },
            'session_info': {
                'total_messages': 2,
                'chat_duration': 5000
            }
        }

        # Mock the webhook service to avoid actual HTTP calls
        with patch('src.services.webhook_service.webhook_service.trigger_webhook', new_callable=AsyncMock) as mock_trigger:
            mock_trigger.return_value = [
                {
                    'subscription_id': webhook_id,
                    'success': True,
                    'status_code': 200
                }
            ]

            # Trigger the webhook
            trigger_result = webhook_controller.trigger_webhook_event('chat_message', chat_payload)
            assert trigger_result['success'] is True

            # Verify the mock was called
            mock_trigger.assert_called_once_with('chat_message', chat_payload)

        # Clean up
        webhook_controller.delete_webhook(webhook_id)


class TestSettingsWebhookIntegration:
    """Test settings route integration with webhook management"""

    def test_settings_webhook_route(self, client: FlaskClient):
        """Test /settings/webhooks route"""
        response = client.get('/settings/webhooks')
        assert response.status_code == 200
        assert b'webhook' in response.data.lower() or b'Webhook' in response.data

    def test_webhook_api_endpoints(self, client: FlaskClient):
        """Test webhook API endpoints"""
        from src.controllers.webhook_controller import webhook_controller

        # Test GET /api/v1/webhooks
        with patch.object(webhook_controller, 'get_webhooks') as mock_get:
            mock_get.return_value = {'success': True, 'data': [], 'total': 0}

            response = client.get('/api/v1/webhooks')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True

    def test_webhook_creation_via_api(self, client: FlaskClient):
        """Test webhook creation through API"""
        from src.controllers.webhook_controller import webhook_controller

        webhook_data = {
            'name': 'api_test_webhook',
            'event_type': 'test_event',
            'url': 'https://example.com/webhook',
            'method': 'POST',
            'is_active': True
        }

        with patch.object(webhook_controller, 'create_webhook') as mock_create:
            mock_create.return_value = {'success': True, 'data': {'id': 123}}

            response = client.post('/api/v1/webhooks',
                                 data=json.dumps(webhook_data),
                                 content_type='application/json')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True


class TestRouteResponseValidation:
    """Test all routes return correct responses"""

    def test_dashboard_route(self, client: FlaskClient):
        """Test dashboard route response"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'dashboard' in response.data.lower() or b'valido' in response.data.lower()

    def test_settings_route(self, client: FlaskClient):
        """Test settings route response"""
        response = client.get('/settings')
        assert response.status_code == 200
        assert b'settings' in response.data.lower() or b'Settings' in response.data

    def test_questions_settings_route(self, client: FlaskClient):
        """Test questions settings route response"""
        response = client.get('/settings/questions')
        assert response.status_code == 200
        assert b'question' in response.data.lower() or b'Question' in response.data

    def test_chat_local_route(self, client: FlaskClient):
        """Test chat-local route response"""
        response = client.get('/chat-local')
        assert response.status_code == 200
        assert b'chat' in response.data.lower() or b'Chat' in response.data

    def test_api_routes(self, client: FlaskClient):
        """Test API routes return valid JSON"""
        api_routes = [
            '/api/v1/webhooks',
            '/api/v1/integrations'
        ]

        for route in api_routes:
            response = client.get(route)
            assert response.status_code == 200
            try:
                data = json.loads(response.data)
                assert isinstance(data, dict)
                assert 'success' in data
            except json.JSONDecodeError:
                pytest.fail(f"Route {route} did not return valid JSON")

    def test_static_file_serving(self, client: FlaskClient):
        """Test static file serving"""
        response = client.get('/static/css/main.css')
        # Should either return 200 (if file exists) or 404 (if not)
        assert response.status_code in [200, 404]


class TestWebhookAPIFlow:
    """Test complete webhook API flow"""

    def setup_method(self):
        """Setup test environment"""
        from src.models.webhook_models import webhook_manager
        webhook_manager._init_database()

    def test_webhook_full_lifecycle(self, client: FlaskClient):
        """Test complete webhook lifecycle through API"""
        # 1. Create webhook
        webhook_data = {
            'name': 'full_lifecycle_test',
            'event_type': 'lifecycle_test',
            'url': 'https://httpbin.org/post',
            'method': 'POST',
            'is_active': True,
            'retry_count': 1,
            'timeout': 10
        }

        response = client.post('/api/v1/webhooks',
                             data=json.dumps(webhook_data),
                             content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        webhook_id = data['data']['id']

        # 2. Get webhook
        response = client.get(f'/api/v1/webhooks/{webhook_id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['name'] == 'full_lifecycle_test'

        # 3. Update webhook
        update_data = {
            'name': 'full_lifecycle_test_updated',
            'timeout': 20
        }

        response = client.put(f'/api/v1/webhooks/{webhook_id}',
                            data=json.dumps(update_data),
                            content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True

        # 4. Trigger webhook event
        trigger_data = {
            'event_type': 'lifecycle_test',
            'payload': {'test': 'lifecycle test'}
        }

        response = client.post('/api/v1/webhooks/trigger',
                             data=json.dumps(trigger_data),
                             content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True

        # 5. Get webhook events
        response = client.get(f'/api/v1/webhooks/events?subscription_id={webhook_id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True

        # 6. Delete webhook
        response = client.delete(f'/api/v1/webhooks/{webhook_id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True

        # 7. Verify deletion
        response = client.get(f'/api/v1/webhooks/{webhook_id}')
        assert response.status_code == 404 or (response.status_code == 200 and
                                              json.loads(response.data)['success'] is False)


class TestErrorHandling:
    """Test error handling in webhook system"""

    def test_invalid_webhook_creation(self, client: FlaskClient):
        """Test creating webhook with invalid data"""
        invalid_data = {
            'name': '',  # Empty name
            'event_type': 'test',
            'url': 'not-a-valid-url'
        }

        response = client.post('/api/v1/webhooks',
                             data=json.dumps(invalid_data),
                             content_type='application/json')
        assert response.status_code == 400 or response.status_code == 200
        if response.status_code == 200:
            data = json.loads(response.data)
            assert data['success'] is False

    def test_nonexistent_webhook_operations(self, client: FlaskClient):
        """Test operations on non-existent webhooks"""
        # Try to get non-existent webhook
        response = client.get('/api/v1/webhooks/99999')
        assert response.status_code == 404 or (response.status_code == 200 and
                                              json.loads(response.data)['success'] is False)

        # Try to update non-existent webhook
        response = client.put('/api/v1/webhooks/99999',
                            data=json.dumps({'name': 'test'}),
                            content_type='application/json')
        assert response.status_code == 404 or (response.status_code == 200 and
                                              json.loads(response.data)['success'] is False)

        # Try to delete non-existent webhook
        response = client.delete('/api/v1/webhooks/99999')
        assert response.status_code == 404 or (response.status_code == 200 and
                                              json.loads(response.data)['success'] is False)


class TestAPIIntegrationFlow:
    """Test API integration flow"""

    def setup_method(self):
        """Setup test environment"""
        from src.models.webhook_models import api_integration_manager
        api_integration_manager._init_database()

    def test_api_integration_lifecycle(self, client: FlaskClient):
        """Test complete API integration lifecycle"""
        # 1. Create integration
        integration_data = {
            'name': 'test_api_integration',
            'provider_type': 'bank',
            'base_url': 'https://api.testbank.com',
            'auth_type': 'basic',
            'auth_config': {
                'username': 'test_user',
                'password': 'test_pass'
            },
            'is_active': True,
            'description': 'Test bank API'
        }

        response = client.post('/api/v1/integrations',
                             data=json.dumps(integration_data),
                             content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        integration_id = data['data']['id']

        # 2. Get integration
        response = client.get(f'/api/v1/integrations/{integration_id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['name'] == 'test_api_integration'

        # 3. Update integration
        update_data = {
            'name': 'test_api_integration_updated',
            'timeout': 60
        }

        response = client.put(f'/api/v1/integrations/{integration_id}',
                            data=json.dumps(update_data),
                            content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True

        # 4. Test integration
        response = client.post(f'/api/v1/integrations/{integration_id}/test')
        assert response.status_code == 200
        data = json.loads(response.data)
        # Test result may be true or false depending on endpoint availability

        # 5. Delete integration
        response = client.delete(f'/api/v1/integrations/{integration_id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
