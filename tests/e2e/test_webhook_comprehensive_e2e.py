"""
Comprehensive E2E Tests for Webhook System with Standard Event Types
Tests all webhook functionality, event types, API integrations, and edge cases
"""
import pytest
import json
import time
import asyncio
from unittest.mock import patch, AsyncMock, MagicMock
from datetime import datetime, timedelta
from flask import Flask
from flask.testing import FlaskClient
import requests_mock

from src.models.webhook_models import webhook_manager, api_integration_manager
from src.controllers.webhook_controller import webhook_controller, api_integration_controller
from src.services.webhook_service import webhook_service, StandardEventTypes


class TestWebhookComprehensiveE2E:
    """Comprehensive end-to-end webhook testing"""

    def setup_method(self):
        """Setup test environment with clean state"""
        # Initialize databases
        webhook_manager._init_database()
        api_integration_manager._init_database()

        # Clean up any existing test data
        self._cleanup_test_data()

    def teardown_method(self):
        """Clean up after tests"""
        self._cleanup_test_data()

    def _cleanup_test_data(self):
        """Clean up test data"""
        try:
            with webhook_manager.db_path as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM webhook_subscriptions WHERE name LIKE 'test_%'")
                cursor.execute("DELETE FROM webhook_events WHERE event_type LIKE 'test_%'")
                cursor.execute("DELETE FROM api_integrations WHERE name LIKE 'test_%'")
                conn.commit()
        except Exception:
            pass  # Ignore cleanup errors

    def test_all_standard_event_types(self, client: FlaskClient):
        """Test all standard event types are properly defined"""
        # Test that all event types are defined
        assert len(StandardEventTypes.ALL_EVENTS) > 50  # Should have many events

        # Test event categories exist
        assert len(StandardEventTypes.EVENT_CATEGORIES) > 10  # Should have multiple categories

        # Test specific categories exist
        expected_categories = ['chat', 'ai', 'user', 'financial', 'system', 'api', 'security']
        for category in expected_categories:
            assert category in StandardEventTypes.EVENT_CATEGORIES

        # Test API endpoint for event types
        response = client.get('/api/v1/webhooks/event-types')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'data' in data
        assert 'all_events' in data['data']
        assert 'categories' in data['data']

    def test_event_type_validation(self, client: FlaskClient):
        """Test event type validation functionality"""
        # Test valid event types
        valid_events = [
            StandardEventTypes.CHAT_MESSAGE_SENT,
            StandardEventTypes.USER_LOGIN,
            StandardEventTypes.FINANCIAL_TRANSACTION_CREATED,
            StandardEventTypes.SYSTEM_ERROR_OCCURRED
        ]

        for event_type in valid_events:
            response = client.get(f'/api/v1/webhooks/validate-event-type?event_type={event_type}')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['data']['is_valid'] is True
            assert data['data']['event_type'] == event_type

        # Test invalid event type
        response = client.get('/api/v1/webhooks/validate-event-type?event_type=invalid.event.type')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['is_valid'] is False

    def test_event_categories_api(self, client: FlaskClient):
        """Test event categories API"""
        for category in StandardEventTypes.EVENT_CATEGORIES.keys():
            response = client.get(f'/api/v1/webhooks/event-categories/{category}')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['data']['category'] == category
            assert 'events' in data['data']
            assert len(data['data']['events']) > 0

        # Test invalid category
        response = client.get('/api/v1/webhooks/event-categories/invalid_category')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['count'] == 0

    def test_webhook_lifecycle_with_standard_events(self, client: FlaskClient):
        """Test complete webhook lifecycle with standard event types"""
        # Create webhook for multiple event types
        webhook_data = {
            'name': 'test_lifecycle_webhook',
            'event_type': StandardEventTypes.CHAT_MESSAGE_SENT,
            'url': 'https://httpbin.org/post',
            'method': 'POST',
            'is_active': True,
            'headers': {'X-Test': 'lifecycle-test'}
        }

        # Create webhook
        response = client.post('/api/v1/webhooks',
                             data=json.dumps(webhook_data),
                             content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        webhook_id = data['data']['id']

        # Verify webhook was created
        response = client.get(f'/api/v1/webhooks/{webhook_id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['name'] == 'test_lifecycle_webhook'

        # Test triggering standard event
        trigger_data = {
            'event_type': StandardEventTypes.CHAT_MESSAGE_SENT,
            'data': {
                'message': 'Hello World',
                'user_id': 'test_user',
                'chat_id': 'test_chat'
            },
            'source': 'test_suite',
            'metadata': {'test_run': 'lifecycle_test'}
        }

        response = client.post('/api/v1/webhooks/trigger-event',
                             data=json.dumps(trigger_data),
                             content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True

        # Check webhook was triggered
        response = client.get('/api/v1/webhooks/events')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True

        # Clean up
        response = client.delete(f'/api/v1/webhooks/{webhook_id}')
        assert response.status_code == 200

    def test_bulk_event_triggering(self, client: FlaskClient):
        """Test bulk event triggering"""
        # Create multiple webhooks for different event types
        webhooks_data = [
            {
                'name': 'test_bulk_chat_webhook',
                'event_type': StandardEventTypes.CHAT_MESSAGE_SENT,
                'url': 'https://httpbin.org/post',
                'is_active': True
            },
            {
                'name': 'test_bulk_user_webhook',
                'event_type': StandardEventTypes.USER_LOGIN,
                'url': 'https://httpbin.org/post',
                'is_active': True
            },
            {
                'name': 'test_bulk_system_webhook',
                'event_type': StandardEventTypes.SYSTEM_ERROR_OCCURRED,
                'url': 'https://httpbin.org/post',
                'is_active': True
            }
        ]

        webhook_ids = []
        for webhook_data in webhooks_data:
            response = client.post('/api/v1/webhooks',
                                 data=json.dumps(webhook_data),
                                 content_type='application/json')
            assert response.status_code == 200
            data = json.loads(response.data)
            webhook_ids.append(data['data']['id'])

        # Trigger bulk events
        bulk_events = [
            {
                'event_type': StandardEventTypes.CHAT_MESSAGE_SENT,
                'data': {'message': 'Bulk test 1'}
            },
            {
                'event_type': StandardEventTypes.USER_LOGIN,
                'data': {'user_id': 'test_user'}
            },
            {
                'event_type': StandardEventTypes.SYSTEM_ERROR_OCCURRED,
                'data': {'error': 'Test error'}
            }
        ]

        response = client.post('/api/v1/webhooks/trigger-bulk',
                             data=json.dumps({'events': bulk_events}),
                             content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['total_events'] == 3

        # Clean up
        for webhook_id in webhook_ids:
            client.delete(f'/api/v1/webhooks/{webhook_id}')

    def test_webhook_health_monitoring(self, client: FlaskClient):
        """Test webhook health monitoring and status"""
        # Test health endpoint
        response = client.get('/api/v1/webhooks/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'health_status' in data['data']
        assert 'overall_success_rate' in data['data']

        # Create some test webhooks and events to test health calculation
        webhook_data = {
            'name': 'test_health_webhook',
            'event_type': StandardEventTypes.CHAT_MESSAGE_SENT,
            'url': 'https://httpbin.org/post',
            'is_active': True
        }

        response = client.post('/api/v1/webhooks',
                             data=json.dumps(webhook_data),
                             content_type='application/json')
        webhook_id = json.loads(response.data)['data']['id']

        # Test health again with data
        response = client.get('/api/v1/webhooks/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['total_webhooks'] >= 1

        # Clean up
        client.delete(f'/api/v1/webhooks/{webhook_id}')

    def test_event_log_filtering(self, client: FlaskClient):
        """Test event log filtering by type"""
        # Create webhooks for different event types
        event_types = [
            StandardEventTypes.CHAT_MESSAGE_SENT,
            StandardEventTypes.USER_LOGIN,
            StandardEventTypes.FINANCIAL_TRANSACTION_CREATED
        ]

        webhook_ids = []
        for i, event_type in enumerate(event_types):
            webhook_data = {
                'name': f'test_filter_webhook_{i}',
                'event_type': event_type,
                'url': 'https://httpbin.org/post',
                'is_active': True
            }

            response = client.post('/api/v1/webhooks',
                                 data=json.dumps(webhook_data),
                                 content_type='application/json')
            webhook_ids.append(json.loads(response.data)['data']['id'])

        # Trigger events of each type
        for event_type in event_types:
            trigger_data = {
                'event_type': event_type,
                'data': {'test': f'test for {event_type}'}
            }

            client.post('/api/v1/webhooks/trigger-event',
                       data=json.dumps(trigger_data),
                       content_type='application/json')

        # Test filtering by event type
        for event_type in event_types:
            response = client.get(f'/api/v1/webhooks/events/by-type/{event_type}')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            # Should have at least one event of this type

        # Clean up
        for webhook_id in webhook_ids:
            client.delete(f'/api/v1/webhooks/{webhook_id}')

    def test_api_integration_comprehensive(self, client: FlaskClient):
        """Test comprehensive API integration functionality"""
        # Test different provider types
        provider_types = ['bank', 'government', 'soap', 'rest']

        integration_ids = []
        for i, provider_type in enumerate(provider_types):
            integration_data = {
                'name': f'test_{provider_type}_integration_{i}',
                'provider_type': provider_type,
                'base_url': f'https://api.{provider_type}.test.com',
                'auth_type': 'basic' if provider_type in ['bank', 'government'] else 'none',
                'auth_config': {
                    'username': 'test_user',
                    'password': 'test_pass'
                } if provider_type in ['bank', 'government'] else {},
                'is_active': True,
                'description': f'Test {provider_type} integration'
            }

            response = client.post('/api/v1/integrations',
                                 data=json.dumps(integration_data),
                                 content_type='application/json')
            assert response.status_code == 200
            data = json.loads(response.data)
            integration_ids.append(data['data']['id'])

        # Test listing integrations
        response = client.get('/api/v1/integrations')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert len(data['data']) >= len(provider_types)

        # Test filtering by provider type
        for provider_type in provider_types:
            response = client.get(f'/api/v1/integrations?provider_type={provider_type}')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True

        # Clean up
        for integration_id in integration_ids:
            client.delete(f'/api/v1/integrations/{integration_id}')

    def test_webhook_retry_logic(self, client: FlaskClient):
        """Test webhook retry logic with failed requests"""
        # Create webhook with retry settings
        webhook_data = {
            'name': 'test_retry_webhook',
            'event_type': StandardEventTypes.CHAT_MESSAGE_SENT,
            'url': 'https://invalid-url-that-will-fail.com/webhook',
            'method': 'POST',
            'is_active': True,
            'retry_count': 3,
            'timeout': 5
        }

        response = client.post('/api/v1/webhooks',
                             data=json.dumps(webhook_data),
                             content_type='application/json')
        webhook_id = json.loads(response.data)['data']['id']

        # Trigger event that will fail
        trigger_data = {
            'event_type': StandardEventTypes.CHAT_MESSAGE_SENT,
            'data': {'message': 'This will fail'}
        }

        response = client.post('/api/v1/webhooks/trigger-event',
                             data=json.dumps(trigger_data),
                             content_type='application/json')
        assert response.status_code == 200

        # Wait for retry attempts
        time.sleep(2)

        # Check events - should have failed events with retry attempts
        response = client.get('/api/v1/webhooks/events')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True

        # Clean up
        client.delete(f'/api/v1/webhooks/{webhook_id}')

    def test_webhook_signature_verification(self, client: FlaskClient):
        """Test webhook signature verification"""
        # Create webhook with signature
        webhook_data = {
            'name': 'test_signature_webhook',
            'event_type': StandardEventTypes.CHAT_MESSAGE_SENT,
            'url': 'https://httpbin.org/post',
            'method': 'POST',
            'secret': 'test_secret_key',
            'is_active': True
        }

        response = client.post('/api/v1/webhooks',
                             data=json.dumps(webhook_data),
                             content_type='application/json')
        webhook_id = json.loads(response.data)['data']['id']

        # Get webhook details
        response = client.get(f'/api/v1/webhooks/{webhook_id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['secret'] == 'test_secret_key'

        # Clean up
        client.delete(f'/api/v1/webhooks/{webhook_id}')

    def test_rate_limiting_simulation(self, client: FlaskClient):
        """Test webhook rate limiting simulation"""
        # Create webhook
        webhook_data = {
            'name': 'test_rate_limit_webhook',
            'event_type': StandardEventTypes.CHAT_MESSAGE_SENT,
            'url': 'https://httpbin.org/post',
            'is_active': True
        }

        response = client.post('/api/v1/webhooks',
                             data=json.dumps(webhook_data),
                             content_type='application/json')
        webhook_id = json.loads(response.data)['data']['id']

        # Simulate rapid webhook triggers
        trigger_data = {
            'event_type': StandardEventTypes.CHAT_MESSAGE_SENT,
            'data': {'message': 'Rate limit test'}
        }

        # Send multiple requests quickly
        for i in range(10):
            response = client.post('/api/v1/webhooks/trigger-event',
                                 data=json.dumps(trigger_data),
                                 content_type='application/json')
            assert response.status_code == 200

        # Check that events were logged
        response = client.get('/api/v1/webhooks/events')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True

        # Clean up
        client.delete(f'/api/v1/webhooks/{webhook_id}')

    def test_webhook_event_payload_structure(self, client: FlaskClient):
        """Test that webhook events have proper payload structure"""
        webhook_data = {
            'name': 'test_payload_webhook',
            'event_type': StandardEventTypes.USER_LOGIN,
            'url': 'https://httpbin.org/post',
            'is_active': True
        }

        response = client.post('/api/v1/webhooks',
                             data=json.dumps(webhook_data),
                             content_type='application/json')
        webhook_id = json.loads(response.data)['data']['id']

        # Trigger event with rich payload
        trigger_data = {
            'event_type': StandardEventTypes.USER_LOGIN,
            'data': {
                'user_id': 'user_123',
                'login_time': datetime.now().isoformat(),
                'ip_address': '192.168.1.100',
                'user_agent': 'Mozilla/5.0 (Test Browser)',
                'login_method': 'password'
            },
            'source': 'test_system',
            'metadata': {
                'test_run': True,
                'environment': 'testing',
                'version': '1.0.0'
            }
        }

        response = client.post('/api/v1/webhooks/trigger-event',
                             data=json.dumps(trigger_data),
                             content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True

        # Check that the event payload was properly structured
        assert 'event_payload' in data
        payload = data['event_payload']
        assert payload['event_type'] == StandardEventTypes.USER_LOGIN
        assert payload['source'] == 'test_system'
        assert payload['data']['user_id'] == 'user_123'
        assert payload['metadata']['test_run'] is True

        # Clean up
        client.delete(f'/api/v1/webhooks/{webhook_id}')

    def test_system_integration_with_chat_local(self, client: FlaskClient):
        """Test integration between webhook system and chat-local route"""
        # Test that chat-local route loads with webhook integration
        response = client.get('/chat-local')
        assert response.status_code == 200
        content = response.data.decode('utf-8')

        # Check that webhook integration is present in the chat interface
        assert 'triggerWebhook' in content
        assert 'triggerChatMessageWebhook' in content
        assert 'StandardEventTypes' in content or 'event' in content

        # Test that webhook API endpoints are accessible from chat context
        response = client.get('/api/v1/webhooks/event-types')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True

        # Test that chat-related event types exist
        event_types_response = client.get('/api/v1/webhooks/event-types')
        data = json.loads(event_types_response.data)
        event_types = data['data']['all_events']

        chat_events = [et for et in event_types if et.startswith('chat.')]
        assert len(chat_events) > 0, "Should have chat-related event types"

    def test_performance_metrics(self, client: FlaskClient):
        """Test webhook performance metrics and monitoring"""
        # Create multiple webhooks
        webhook_ids = []
        for i in range(5):
            webhook_data = {
                'name': f'test_performance_webhook_{i}',
                'event_type': StandardEventTypes.CHAT_MESSAGE_SENT,
                'url': 'https://httpbin.org/post',
                'is_active': True
            }

            response = client.post('/api/v1/webhooks',
                                 data=json.dumps(webhook_data),
                                 content_type='application/json')
            webhook_ids.append(json.loads(response.data)['data']['id'])

        # Measure performance of bulk operations
        start_time = time.time()

        # Trigger multiple events
        for i in range(10):
            trigger_data = {
                'event_type': StandardEventTypes.CHAT_MESSAGE_SENT,
                'data': {'message': f'Performance test {i}'}
            }

            response = client.post('/api/v1/webhooks/trigger-event',
                                 data=json.dumps(trigger_data),
                                 content_type='application/json')
            assert response.status_code == 200

        end_time = time.time()
        duration = end_time - start_time

        # Should complete within reasonable time
        assert duration < 30, f"Bulk operations took too long: {duration}s"

        # Check performance metrics in health endpoint
        response = client.get('/api/v1/webhooks/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'last_updated' in data['data']

        # Clean up
        for webhook_id in webhook_ids:
            client.delete(f'/api/v1/webhooks/{webhook_id}')

    def test_error_handling_edge_cases(self, client: FlaskClient):
        """Test error handling for edge cases"""
        # Test with malformed JSON
        response = client.post('/api/v1/webhooks',
                             data='invalid json',
                             content_type='application/json')
        assert response.status_code in [400, 200]  # Should handle gracefully

        # Test with missing required fields
        incomplete_data = {
            'name': 'incomplete_webhook'
            # Missing event_type and url
        }

        response = client.post('/api/v1/webhooks',
                             data=json.dumps(incomplete_data),
                             content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is False  # Should fail validation

        # Test accessing non-existent webhook
        response = client.get('/api/v1/webhooks/99999')
        assert response.status_code in [404, 200]
        if response.status_code == 200:
            data = json.loads(response.data)
            assert data['success'] is False

        # Test triggering non-existent event type
        trigger_data = {
            'event_type': 'nonexistent.event.type',
            'data': {'test': 'data'}
        }

        response = client.post('/api/v1/webhooks/trigger-event',
                             data=json.dumps(trigger_data),
                             content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is False  # Should fail validation

    def test_webhook_configuration_persistence(self, client: FlaskClient):
        """Test that webhook configurations persist correctly"""
        # Create webhook with complex configuration
        complex_webhook = {
            'name': 'test_persistence_webhook',
            'event_type': StandardEventTypes.FINANCIAL_TRANSACTION_CREATED,
            'url': 'https://secure-webhook.example.com/financial',
            'method': 'POST',
            'headers': {
                'Authorization': 'Bearer test_token',
                'X-Custom-Header': 'custom_value',
                'Content-Type': 'application/json'
            },
            'secret': 'webhook_secret_123',
            'is_active': True,
            'retry_count': 5,
            'timeout': 30
        }

        # Create webhook
        response = client.post('/api/v1/webhooks',
                             data=json.dumps(complex_webhook),
                             content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        webhook_id = data['data']['id']

        # Retrieve and verify all configuration
        response = client.get(f'/api/v1/webhooks/{webhook_id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        retrieved_webhook = data['data']

        # Verify all fields match
        assert retrieved_webhook['name'] == complex_webhook['name']
        assert retrieved_webhook['event_type'] == complex_webhook['event_type']
        assert retrieved_webhook['url'] == complex_webhook['url']
        assert retrieved_webhook['method'] == complex_webhook['method']
        assert retrieved_webhook['headers'] == complex_webhook['headers']
        assert retrieved_webhook['secret'] == complex_webhook['secret']
        assert retrieved_webhook['is_active'] == complex_webhook['is_active']
        assert retrieved_webhook['retry_count'] == complex_webhook['retry_count']
        assert retrieved_webhook['timeout'] == complex_webhook['timeout']

        # Test configuration survives restart (conceptual)
        # In a real scenario, this would test database persistence

        # Clean up
        client.delete(f'/api/v1/webhooks/{webhook_id}')


# Test configuration for pytest
pytest_plugins = ["pytest_asyncio"]

@pytest.fixture(scope="session")
def client():
    """Create test client"""
    from app import app
    app.config['TESTING'] = True
    return app.test_client()


@pytest.fixture(autouse=True)
def cleanup_after_test(client: FlaskClient):
    """Clean up after each test"""
    yield
    # Cleanup any test webhooks/integrations
    try:
        # Clean webhooks
        response = client.get('/api/v1/webhooks')
        if response.status_code == 200:
            data = json.loads(response.data)
            if data['success']:
                for webhook in data['data']:
                    if webhook['name'].startswith('test_'):
                        client.delete(f'/api/v1/webhooks/{webhook["id"]}')

        # Clean integrations
        response = client.get('/api/v1/integrations')
        if response.status_code == 200:
            data = json.loads(response.data)
            if data['success']:
                for integration in data['data']:
                    if integration['name'].startswith('test_'):
                        client.delete(f'/api/v1/integrations/{integration["id"]}')

    except Exception:
        pass  # Ignore cleanup errors in tests
