"""
Integration Tests for Webhook System Components
Tests integration between webhook service, models, controllers, and external systems
"""
import pytest
import json
import asyncio
import time
from unittest.mock import patch, AsyncMock, MagicMock
from datetime import datetime, timedelta
from flask import Flask
from flask.testing import FlaskClient

from src.models.webhook_models import webhook_manager, api_integration_manager
from src.controllers.webhook_controller import webhook_controller, api_integration_controller
from src.services.webhook_service import webhook_service, StandardEventTypes


class TestWebhookServiceIntegration:
    """Test webhook service integration with models and controllers"""

    def setup_method(self):
        """Setup test environment"""
        webhook_manager._init_database()
        api_integration_manager._init_database()
        self._cleanup_test_data()

    def teardown_method(self):
        """Clean up test environment"""
        self._cleanup_test_data()

    def _cleanup_test_data(self):
        """Clean up test data"""
        with webhook_manager.db_path as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM webhook_subscriptions WHERE name LIKE 'test_%'")
            cursor.execute("DELETE FROM webhook_events WHERE event_type LIKE 'test_%'")
            cursor.execute("DELETE FROM api_integrations WHERE name LIKE 'test_%'")
            conn.commit()

    @pytest.mark.asyncio
    async def test_webhook_service_model_integration(self):
        """Test integration between webhook service and models"""
        # Create webhook through models
        webhook_data = {
            'name': 'service_integration_test',
            'event_type': StandardEventTypes.CHAT_MESSAGE_SENT,
            'url': 'https://httpbin.org/post',
            'method': 'POST',
            'is_active': True,
            'secret': 'test_secret'
        }

        webhook_id = webhook_manager.create_subscription(
            type('WebhookSubscription', (), webhook_data)()
        )

        # Get webhook through service
        subscriptions = webhook_manager.get_subscriptions(
            event_type=StandardEventTypes.CHAT_MESSAGE_SENT
        )
        assert len(subscriptions) >= 1

        # Test service methods
        available_events = webhook_service.get_available_event_types()
        assert StandardEventTypes.CHAT_MESSAGE_SENT in available_events

        categories = webhook_service.get_event_categories()
        assert 'chat' in categories
        assert StandardEventTypes.CHAT_MESSAGE_SENT in categories['chat']

        # Clean up
        webhook_manager.delete_subscription(webhook_id)

    @pytest.mark.asyncio
    async def test_service_controller_integration(self):
        """Test integration between service and controller layers"""
        # Create webhook through controller
        webhook_data = {
            'name': 'controller_service_test',
            'event_type': StandardEventTypes.USER_LOGIN,
            'url': 'https://httpbin.org/post',
            'is_active': True
        }

        result = webhook_controller.create_webhook(webhook_data)
        assert result['success'] is True
        webhook_id = result['data']['id']

        # Test service integration
        test_payload = {
            'user_id': 'test_user',
            'login_time': datetime.now().isoformat()
        }

        # Mock the actual HTTP call to avoid external dependencies
        with patch('src.services.webhook_service.webhook_service.trigger_webhook', new_callable=AsyncMock) as mock_trigger:
            mock_trigger.return_value = [
                {
                    'subscription_id': webhook_id,
                    'success': True,
                    'status_code': 200
                }
            ]

            # Trigger through service
            trigger_result = await webhook_service.trigger_event(
                StandardEventTypes.USER_LOGIN,
                test_payload
            )
            assert trigger_result['success'] is True

            # Verify service was called
            mock_trigger.assert_called_once()

        # Clean up
        webhook_controller.delete_webhook(webhook_id)

    def test_bulk_operations_integration(self, client: FlaskClient):
        """Test bulk operations across all layers"""
        # Create multiple webhooks through controller
        webhook_ids = []
        event_types = [
            StandardEventTypes.CHAT_MESSAGE_SENT,
            StandardEventTypes.USER_LOGIN,
            StandardEventTypes.FINANCIAL_TRANSACTION_CREATED
        ]

        for i, event_type in enumerate(event_types):
            webhook_data = {
                'name': f'bulk_test_webhook_{i}',
                'event_type': event_type,
                'url': 'https://httpbin.org/post',
                'is_active': True
            }

            response = client.post('/api/v1/webhooks',
                                 data=json.dumps(webhook_data),
                                 content_type='application/json')
            assert response.status_code == 200
            data = json.loads(response.data)
            webhook_ids.append(data['data']['id'])

        # Test bulk trigger through controller
        bulk_events = [
            {
                'event_type': StandardEventTypes.CHAT_MESSAGE_SENT,
                'data': {'message': 'Bulk chat test'}
            },
            {
                'event_type': StandardEventTypes.USER_LOGIN,
                'data': {'user_id': 'bulk_test_user'}
            },
            {
                'event_type': StandardEventTypes.FINANCIAL_TRANSACTION_CREATED,
                'data': {'amount': 100.00}
            }
        ]

        response = client.post('/api/v1/webhooks/trigger-bulk',
                             data=json.dumps({'events': bulk_events}),
                             content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['total_events'] == 3

        # Verify events were created in database
        response = client.get('/api/v1/webhooks/events')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True

        # Clean up
        for webhook_id in webhook_ids:
            client.delete(f'/api/v1/webhooks/{webhook_id}')

    def test_event_type_integration_across_layers(self, client: FlaskClient):
        """Test event type integration across all layers"""
        # Test service layer
        available_events = webhook_service.get_available_event_types()
        assert len(available_events) > 50  # Should have many event types

        # Test controller layer
        response = client.get('/api/v1/webhooks/event-types')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        controller_events = data['data']['all_events']

        # Events should match between service and controller
        assert len(controller_events) == len(available_events)

        # Test specific categories
        for category in StandardEventTypes.EVENT_CATEGORIES.keys():
            # Service layer
            service_events = webhook_service.get_events_by_category(category)
            assert len(service_events) > 0

            # Controller layer
            response = client.get(f'/api/v1/webhooks/event-categories/{category}')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            controller_category_events = data['data']['events']

            # Should match
            assert len(controller_category_events) == len(service_events)

    def test_health_monitoring_integration(self, client: FlaskClient):
        """Test health monitoring integration across layers"""
        # Create some test data
        webhook_data = {
            'name': 'health_test_webhook',
            'event_type': StandardEventTypes.CHAT_MESSAGE_SENT,
            'url': 'https://httpbin.org/post',
            'is_active': True
        }

        response = client.post('/api/v1/webhooks',
                             data=json.dumps(webhook_data),
                             content_type='application/json')
        webhook_id = json.loads(response.data)['data']['id']

        # Test health endpoint
        response = client.get('/api/v1/webhooks/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'health_status' in data['data']
        assert 'total_webhooks' in data['data']
        assert 'overall_success_rate' in data['data']

        # Verify health data includes our webhook
        assert data['data']['total_webhooks'] >= 1

        # Clean up
        client.delete(f'/api/v1/webhooks/{webhook_id}')

    def test_statistics_integration(self, client: FlaskClient):
        """Test statistics integration across layers"""
        # Create webhook and generate some events
        webhook_data = {
            'name': 'stats_test_webhook',
            'event_type': StandardEventTypes.USER_LOGIN,
            'url': 'https://httpbin.org/post',
            'is_active': True
        }

        response = client.post('/api/v1/webhooks',
                             data=json.dumps(webhook_data),
                             content_type='application/json')
        webhook_id = json.loads(response.data)['data']['id']

        # Generate some test events
        for i in range(5):
            trigger_data = {
                'event_type': StandardEventTypes.USER_LOGIN,
                'data': {'user_id': f'test_user_{i}'}
            }

            client.post('/api/v1/webhooks/trigger-event',
                       data=json.dumps(trigger_data),
                       content_type='application/json')

        # Test statistics endpoint
        response = client.get('/api/v1/webhooks/stats')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'total_webhooks' in data['data']
        assert 'total_events' in data['data']
        assert 'successful_events' in data['data']

        # Test that statistics include our webhook
        assert data['data']['total_webhooks'] >= 1
        assert data['data']['total_events'] >= 5

        # Clean up
        client.delete(f'/api/v1/webhooks/{webhook_id}')

    @pytest.mark.asyncio
    async def test_async_service_integration(self):
        """Test async service integration with proper initialization"""
        # Test service initialization
        await webhook_service.initialize()

        try:
            # Test that service is properly initialized
            assert webhook_service.event_types is not None
            assert webhook_service.session is not None

            # Test event validation
            assert webhook_service.validate_event_type(StandardEventTypes.CHAT_MESSAGE_SENT)
            assert not webhook_service.validate_event_type('invalid.event.type')

            # Test event triggering
            test_payload = {
                'message': 'Async integration test',
                'timestamp': datetime.now().isoformat()
            }

            # Mock the webhook call
            with patch.object(webhook_service, 'trigger_webhook', new_callable=AsyncMock) as mock_trigger:
                mock_trigger.return_value = [
                    {
                        'subscription_id': 1,
                        'success': True,
                        'status_code': 200
                    }
                ]

                result = await webhook_service.trigger_event(
                    StandardEventTypes.CHAT_MESSAGE_SENT,
                    test_payload
                )

                assert result['success'] is True
                mock_trigger.assert_called_once()

        finally:
            await webhook_service.close()

    def test_error_handling_integration(self, client: FlaskClient):
        """Test error handling integration across layers"""
        # Test invalid webhook creation
        invalid_webhook = {
            'name': '',  # Empty name should fail
            'event_type': StandardEventTypes.CHAT_MESSAGE_SENT,
            'url': 'invalid-url'
        }

        response = client.post('/api/v1/webhooks',
                             data=json.dumps(invalid_webhook),
                             content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is False  # Should fail validation

        # Test invalid event trigger
        invalid_trigger = {
            'event_type': 'invalid.event.type',
            'data': {'test': 'data'}
        }

        response = client.post('/api/v1/webhooks/trigger-event',
                             data=json.dumps(invalid_trigger),
                             content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is False  # Should fail validation

        # Test accessing non-existent webhook
        response = client.get('/api/v1/webhooks/99999')
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = json.loads(response.data)
            assert data['success'] is False

    def test_concurrent_operations_integration(self, client: FlaskClient):
        """Test concurrent operations integration"""
        import threading
        import queue

        # Create webhook
        webhook_data = {
            'name': 'concurrent_test_webhook',
            'event_type': StandardEventTypes.CHAT_MESSAGE_SENT,
            'url': 'https://httpbin.org/post',
            'is_active': True
        }

        response = client.post('/api/v1/webhooks',
                             data=json.dumps(webhook_data),
                             content_type='application/json')
        webhook_id = json.loads(response.data)['data']['id']

        # Function to perform operations concurrently
        def perform_operation(operation_id):
            try:
                trigger_data = {
                    'event_type': StandardEventTypes.CHAT_MESSAGE_SENT,
                    'data': {'operation_id': operation_id}
                }

                response = client.post('/api/v1/webhooks/trigger-event',
                                     data=json.dumps(trigger_data),
                                     content_type='application/json')
                return response.status_code == 200
            except Exception as e:
                return False

        # Run multiple operations concurrently
        results = []
        threads = []

        for i in range(10):
            thread = threading.Thread(target=lambda: results.append(perform_operation(i)))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # All operations should succeed
        assert all(results), "Some concurrent operations failed"

        # Verify events were created
        response = client.get('/api/v1/webhooks/events')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True

        # Clean up
        client.delete(f'/api/v1/webhooks/{webhook_id}')

    def test_data_consistency_integration(self, client: FlaskClient):
        """Test data consistency across all layers"""
        # Create webhook through API
        webhook_data = {
            'name': 'consistency_test_webhook',
            'event_type': StandardEventTypes.FINANCIAL_TRANSACTION_CREATED,
            'url': 'https://httpbin.org/post',
            'method': 'POST',
            'headers': {'X-Test': 'consistency'},
            'secret': 'test_secret',
            'is_active': True,
            'retry_count': 3,
            'timeout': 15
        }

        response = client.post('/api/v1/webhooks',
                             data=json.dumps(webhook_data),
                             content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        webhook_id = data['data']['id']

        # Verify data consistency through different endpoints
        endpoints = [
            f'/api/v1/webhooks/{webhook_id}',
            '/api/v1/webhooks',
            '/api/v1/webhooks/stats',
            '/api/v1/webhooks/health'
        ]

        webhook_data_consistent = None

        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True

            if endpoint == f'/api/v1/webhooks/{webhook_id}':
                webhook_data_consistent = data['data']
            elif endpoint == '/api/v1/webhooks':
                # Find our webhook in the list
                webhooks = data['data']
                matching_webhook = next((w for w in webhooks if w['id'] == webhook_id), None)
                assert matching_webhook is not None

                # Compare key fields
                if webhook_data_consistent:
                    assert matching_webhook['name'] == webhook_data_consistent['name']
                    assert matching_webhook['event_type'] == webhook_data_consistent['event_type']
                    assert matching_webhook['url'] == webhook_data_consistent['url']

        # Clean up
        client.delete(f'/api/v1/webhooks/{webhook_id}')

    def test_api_integration_full_lifecycle(self, client: FlaskClient):
        """Test complete API integration lifecycle"""
        # Create API integration
        integration_data = {
            'name': 'lifecycle_test_integration',
            'provider_type': 'bank',
            'base_url': 'https://api.testbank.com',
            'auth_type': 'basic',
            'auth_config': {
                'username': 'test_user',
                'password': 'test_pass'
            },
            'timeout': 30,
            'retry_count': 2,
            'is_active': True,
            'description': 'Full lifecycle test'
        }

        response = client.post('/api/v1/integrations',
                             data=json.dumps(integration_data),
                             content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        integration_id = data['data']['id']

        # Test retrieval
        response = client.get(f'/api/v1/integrations/{integration_id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['name'] == 'lifecycle_test_integration'

        # Test listing
        response = client.get('/api/v1/integrations')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert len(data['data']) >= 1

        # Test update
        update_data = {
            'name': 'lifecycle_test_integration_updated',
            'timeout': 60
        }

        response = client.put(f'/api/v1/integrations/{integration_id}',
                            data=json.dumps(update_data),
                            content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True

        # Verify update
        response = client.get(f'/api/v1/integrations/{integration_id}')
        data = json.loads(response.data)
        assert data['data']['name'] == 'lifecycle_test_integration_updated'
        assert data['data']['timeout'] == 60

        # Test deletion
        response = client.delete(f'/api/v1/integrations/{integration_id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True

        # Verify deletion
        response = client.get(f'/api/v1/integrations/{integration_id}')
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = json.loads(response.data)
            assert data['success'] is False

    def test_cross_component_data_flow(self, client: FlaskClient):
        """Test data flow between different components"""
        # Create webhook and integration
        webhook_data = {
            'name': 'cross_component_webhook',
            'event_type': StandardEventTypes.API_INTEGRATION_CONNECTED,
            'url': 'https://httpbin.org/post',
            'is_active': True
        }

        response = client.post('/api/v1/webhooks',
                             data=json.dumps(webhook_data),
                             content_type='application/json')
        webhook_id = json.loads(response.data)['data']['id']

        integration_data = {
            'name': 'cross_component_integration',
            'provider_type': 'rest',
            'base_url': 'https://api.test.com',
            'auth_type': 'none',
            'is_active': True
        }

        response = client.post('/api/v1/integrations',
                             data=json.dumps(integration_data),
                             content_type='application/json')
        integration_id = json.loads(response.data)['data']['id']

        # Trigger webhook about integration connection
        trigger_data = {
            'event_type': StandardEventTypes.API_INTEGRATION_CONNECTED,
            'data': {
                'integration_id': integration_id,
                'integration_name': 'cross_component_integration',
                'connection_time': datetime.now().isoformat()
            }
        }

        response = client.post('/api/v1/webhooks/trigger-event',
                             data=json.dumps(trigger_data),
                             content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True

        # Verify event was logged
        response = client.get('/api/v1/webhooks/events')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True

        # Verify both components can be retrieved independently
        response = client.get(f'/api/v1/webhooks/{webhook_id}')
        assert response.status_code == 200

        response = client.get(f'/api/v1/integrations/{integration_id}')
        assert response.status_code == 200

        # Clean up
        client.delete(f'/api/v1/webhooks/{webhook_id}')
        client.delete(f'/api/v1/integrations/{integration_id}')


# Test fixtures and configuration
@pytest.fixture(scope="session")
def client():
    """Create test client"""
    from app import app
    app.config['TESTING'] = True
    return app.test_client()


@pytest.fixture(autouse=True)
def cleanup_integration_data(client: FlaskClient):
    """Clean up test data after each test"""
    yield
    try:
        # Clean webhooks
        response = client.get('/api/v1/webhooks')
        if response.status_code == 200:
            data = json.loads(response.data)
            if data['success']:
                for webhook in data['data']:
                    if webhook['name'].startswith(('test_', 'integration_', 'cross_', 'bulk_', 'service_')):
                        client.delete(f'/api/v1/webhooks/{webhook["id"]}')

        # Clean integrations
        response = client.get('/api/v1/integrations')
        if response.status_code == 200:
            data = json.loads(response.data)
            if data['success']:
                for integration in data['data']:
                    if integration['name'].startswith(('test_', 'integration_', 'lifecycle_', 'cross_')):
                        client.delete(f'/api/v1/integrations/{integration["id"]}')

    except Exception:
        pass  # Ignore cleanup errors
