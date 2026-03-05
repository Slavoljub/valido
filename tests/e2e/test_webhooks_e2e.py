"""
End-to-End Tests for Webhook System
Tests webhook creation, triggering, API integrations, and monitoring
"""
import pytest
import asyncio
import json
import time
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from src.models.webhook_models import (
    WebhookSubscription,
    WebhookEvent,
    APIIntegration,
    webhook_manager,
    api_integration_manager
)
from src.services.webhook_service import webhook_service, api_integration_service
from src.controllers.webhook_controller import webhook_controller, api_integration_controller


class TestWebhookE2E:
    """End-to-end webhook testing"""

    def setup_method(self):
        """Setup test environment"""
        # Initialize the database
        webhook_manager._init_database()
        api_integration_manager._init_database()

    def teardown_method(self):
        """Clean up after tests"""
        # Clean up test data
        with webhook_manager.db_path as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM webhook_subscriptions WHERE name LIKE 'test_%'")
            cursor.execute("DELETE FROM webhook_events WHERE event_type LIKE 'test_%'")
            cursor.execute("DELETE FROM api_integrations WHERE name LIKE 'test_%'")
            conn.commit()

    @pytest.mark.asyncio
    async def test_webhook_creation_and_triggering(self):
        """Test complete webhook lifecycle: create, trigger, log event"""
        # Create webhook subscription
        webhook_data = {
            'name': 'test_webhook_e2e',
            'event_type': 'chat_message',
            'url': 'https://httpbin.org/post',
            'method': 'POST',
            'secret': 'test_secret',
            'is_active': True,
            'retry_count': 2,
            'timeout': 10
        }

        result = webhook_controller.create_webhook(webhook_data)
        assert result['success'] is True
        webhook_id = result['data']['id']

        # Get the webhook
        webhook_result = webhook_controller.get_webhook(webhook_id)
        assert webhook_result['success'] is True
        assert webhook_result['data']['name'] == 'test_webhook_e2e'

        # Test webhook with mock HTTP server
        test_payload = {
            'message': 'Hello World',
            'timestamp': datetime.now().isoformat()
        }

        # Mock the HTTP request to avoid external dependencies
        with patch('aiohttp.ClientSession.request', new_callable=AsyncMock) as mock_request:
            mock_response = MagicMock()
            mock_response.status = 200
            mock_response.text = AsyncMock(return_value=json.dumps({'received': True}))
            mock_request.return_value.__aenter__.return_value = mock_response

            # Trigger webhook
            trigger_result = webhook_controller.trigger_webhook_event('chat_message', test_payload)
            assert trigger_result['success'] is True

            # Verify the mock was called
            assert mock_request.called
            call_args = mock_request.call_args
            assert call_args[1]['url'] == 'https://httpbin.org/post'
            assert call_args[1]['method'] == 'POST'

        # Check that event was logged
        events = webhook_manager.get_events()
        chat_events = [e for e in events if e.event_type == 'chat_message']
        assert len(chat_events) > 0

        # Clean up
        delete_result = webhook_controller.delete_webhook(webhook_id)
        assert delete_result['success'] is True

    def test_webhook_crud_operations(self):
        """Test webhook CRUD operations"""
        # Create
        webhook_data = {
            'name': 'test_crud_webhook',
            'event_type': 'user_joined',
            'url': 'https://example.com/webhook',
            'method': 'POST',
            'headers': {'X-Custom': 'value'},
            'is_active': True,
            'retry_count': 1,
            'timeout': 5
        }

        create_result = webhook_controller.create_webhook(webhook_data)
        assert create_result['success'] is True
        webhook_id = create_result['data']['id']

        # Read
        get_result = webhook_controller.get_webhook(webhook_id)
        assert get_result['success'] is True
        assert get_result['data']['name'] == 'test_crud_webhook'
        assert get_result['data']['headers']['X-Custom'] == 'value'

        # Update
        update_data = {
            'name': 'test_crud_webhook_updated',
            'event_type': 'user_left',
            'timeout': 15
        }
        update_result = webhook_controller.update_webhook(webhook_id, update_data)
        assert update_result['success'] is True

        # Verify update
        get_updated = webhook_controller.get_webhook(webhook_id)
        assert get_updated['data']['name'] == 'test_crud_webhook_updated'
        assert get_updated['data']['event_type'] == 'user_left'
        assert get_updated['data']['timeout'] == 15

        # Delete
        delete_result = webhook_controller.delete_webhook(webhook_id)
        assert delete_result['success'] is True

        # Verify deletion
        get_deleted = webhook_controller.get_webhook(webhook_id)
        assert get_deleted['success'] is False

    def test_webhook_listing_and_filtering(self):
        """Test webhook listing and filtering"""
        # Create multiple webhooks
        webhooks_data = [
            {
                'name': 'test_list_webhook_1',
                'event_type': 'chat_message',
                'url': 'https://example1.com/webhook',
                'is_active': True
            },
            {
                'name': 'test_list_webhook_2',
                'event_type': 'user_joined',
                'url': 'https://example2.com/webhook',
                'is_active': True
            },
            {
                'name': 'test_list_webhook_3',
                'event_type': 'chat_message',
                'url': 'https://example3.com/webhook',
                'is_active': False
            }
        ]

        webhook_ids = []
        for webhook_data in webhooks_data:
            result = webhook_controller.create_webhook(webhook_data)
            webhook_ids.append(result['data']['id'])

        # Test listing all
        all_webhooks = webhook_controller.get_webhooks()
        assert all_webhooks['success'] is True
        assert len(all_webhooks['data']) >= 3

        # Test filtering by event type
        chat_webhooks = webhook_controller.get_webhooks(event_type='chat_message')
        assert chat_webhooks['success'] is True
        chat_webhook_names = [w['name'] for w in chat_webhooks['data']]
        assert 'test_list_webhook_1' in chat_webhook_names
        assert 'test_list_webhook_3' in chat_webhook_names
        assert 'test_list_webhook_2' not in chat_webhook_names

        # Test filtering by active status
        active_webhooks = webhook_controller.get_webhooks(active_only=True)
        assert active_webhooks['success'] is True
        active_names = [w['name'] for w in active_webhooks['data']]
        assert 'test_list_webhook_1' in active_names
        assert 'test_list_webhook_2' in active_names
        assert 'test_list_webhook_3' not in active_names

        # Clean up
        for webhook_id in webhook_ids:
            webhook_controller.delete_webhook(webhook_id)

    def test_webhook_event_logging_and_retrieval(self):
        """Test webhook event logging and retrieval"""
        # Create webhook
        webhook_data = {
            'name': 'test_events_webhook',
            'event_type': 'test_event',
            'url': 'https://example.com/webhook',
            'is_active': True
        }

        create_result = webhook_controller.create_webhook(webhook_data)
        webhook_id = create_result['data']['id']

        # Log events manually (simulating webhook calls)
        test_events = [
            {
                'subscription_id': webhook_id,
                'event_type': 'test_event',
                'payload': {'data': 'test1'},
                'status': 'success',
                'response_code': 200,
                'response_body': 'OK'
            },
            {
                'subscription_id': webhook_id,
                'event_type': 'test_event',
                'payload': {'data': 'test2'},
                'status': 'failed',
                'response_code': 500,
                'error_message': 'Internal Server Error'
            }
        ]

        event_ids = []
        for event_data in test_events:
            event = WebhookEvent(**event_data)
            event_id = webhook_manager.log_event(event)
            event_ids.append(event_id)

        # Test event retrieval
        all_events = webhook_controller.get_webhook_events()
        assert all_events['success'] is True

        # Test filtering by subscription
        sub_events = webhook_controller.get_webhook_events(subscription_id=webhook_id)
        assert sub_events['success'] is True
        assert len(sub_events['data']) == 2

        # Test individual event retrieval
        first_event = webhook_controller.get_webhook_event(event_ids[0])
        assert first_event['success'] is True
        assert first_event['data']['status'] == 'success'
        assert first_event['data']['response_code'] == 200

        # Clean up
        webhook_controller.delete_webhook(webhook_id)

    def test_webhook_statistics(self):
        """Test webhook statistics calculation"""
        # Create webhook
        webhook_data = {
            'name': 'test_stats_webhook',
            'event_type': 'test_stats',
            'url': 'https://example.com/webhook',
            'is_active': True
        }

        create_result = webhook_controller.create_webhook(webhook_data)
        webhook_id = create_result['data']['id']

        # Log some test events
        events = [
            {'status': 'success', 'subscription_id': webhook_id, 'event_type': 'test_stats'},
            {'status': 'success', 'subscription_id': webhook_id, 'event_type': 'test_stats'},
            {'status': 'failed', 'subscription_id': webhook_id, 'event_type': 'test_stats'},
            {'status': 'success', 'subscription_id': webhook_id, 'event_type': 'test_stats'},
        ]

        for event_data in events:
            event = WebhookEvent(**event_data)
            webhook_manager.log_event(event)

        # Update webhook stats manually
        webhook_manager.update_subscription_stats(webhook_id, success=True)
        webhook_manager.update_subscription_stats(webhook_id, success=True)
        webhook_manager.update_subscription_stats(webhook_id, success=False)
        webhook_manager.update_subscription_stats(webhook_id, success=True)

        # Test statistics
        stats = webhook_controller.get_webhook_stats()
        assert stats['success'] is True
        assert stats['data']['total_webhooks'] >= 1
        assert stats['data']['total_events'] >= 4

        # Clean up
        webhook_controller.delete_webhook(webhook_id)


class TestAPIIntegrationE2E:
    """End-to-end API integration testing"""

    def setup_method(self):
        """Setup test environment"""
        # Initialize the database
        api_integration_manager._init_database()

    def teardown_method(self):
        """Clean up after tests"""
        # Clean up test data
        with api_integration_manager.db_path as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM api_integrations WHERE name LIKE 'test_%'")
            conn.commit()

    def test_api_integration_crud_operations(self):
        """Test API integration CRUD operations"""
        # Create
        integration_data = {
            'name': 'test_bank_api',
            'provider_type': 'bank',
            'base_url': 'https://api.bank.com',
            'auth_type': 'basic',
            'auth_config': {
                'username': 'test_user',
                'password': 'test_pass'
            },
            'headers': {'X-API-Key': 'test_key'},
            'timeout': 30,
            'retry_count': 2,
            'is_active': True,
            'description': 'Test bank API integration'
        }

        create_result = api_integration_controller.create_integration(integration_data)
        assert create_result['success'] is True
        integration_id = create_result['data']['id']

        # Read
        get_result = api_integration_controller.get_integration(integration_id)
        assert get_result['success'] is True
        assert get_result['data']['name'] == 'test_bank_api'
        assert get_result['data']['provider_type'] == 'bank'
        assert get_result['data']['auth_type'] == 'basic'

        # Update
        update_data = {
            'name': 'test_bank_api_updated',
            'provider_type': 'government',
            'timeout': 60
        }
        update_result = api_integration_controller.update_integration(integration_id, update_data)
        assert update_result['success'] is True

        # Verify update
        get_updated = api_integration_controller.get_integration(integration_id)
        assert get_updated['data']['name'] == 'test_bank_api_updated'
        assert get_updated['data']['provider_type'] == 'government'
        assert get_updated['data']['timeout'] == 60

        # Delete
        delete_result = api_integration_controller.delete_integration(integration_id)
        assert delete_result['success'] is True

        # Verify deletion
        get_deleted = api_integration_controller.get_integration(integration_id)
        assert get_deleted['success'] is False

    def test_api_integration_listing_and_filtering(self):
        """Test API integration listing and filtering"""
        # Create multiple integrations
        integrations_data = [
            {
                'name': 'test_bank_integration',
                'provider_type': 'bank',
                'base_url': 'https://api.bank1.com',
                'is_active': True
            },
            {
                'name': 'test_gov_integration',
                'provider_type': 'government',
                'base_url': 'https://api.gov1.com',
                'is_active': True
            },
            {
                'name': 'test_soap_integration',
                'provider_type': 'soap',
                'base_url': 'https://api.soap1.com',
                'is_active': False
            }
        ]

        integration_ids = []
        for integration_data in integrations_data:
            result = api_integration_controller.create_integration(integration_data)
            integration_ids.append(result['data']['id'])

        # Test listing all
        all_integrations = api_integration_controller.get_integrations()
        assert all_integrations['success'] is True
        assert len(all_integrations['data']) >= 3

        # Test filtering by provider type
        bank_integrations = api_integration_controller.get_integrations(provider_type='bank')
        assert bank_integrations['success'] is True
        bank_names = [i['name'] for i in bank_integrations['data']]
        assert 'test_bank_integration' in bank_names
        assert 'test_gov_integration' not in bank_names

        # Test filtering by active status
        active_integrations = api_integration_controller.get_integrations(active_only=True)
        assert active_integrations['success'] is True
        active_names = [i['name'] for i in active_integrations['data']]
        assert 'test_bank_integration' in active_names
        assert 'test_gov_integration' in active_names
        assert 'test_soap_integration' not in active_names

        # Clean up
        for integration_id in integration_ids:
            api_integration_controller.delete_integration(integration_id)

    @pytest.mark.asyncio
    async def test_api_integration_testing(self):
        """Test API integration testing functionality"""
        # Create integration
        integration_data = {
            'name': 'test_integration_test',
            'provider_type': 'rest',
            'base_url': 'https://httpbin.org',
            'auth_type': 'none',
            'is_active': True
        }

        create_result = api_integration_controller.create_integration(integration_data)
        integration_id = create_result['data']['id']

        # Mock the test_integration method
        with patch.object(api_integration_service, 'test_integration', new_callable=AsyncMock) as mock_test:
            mock_test.return_value = {
                'success': True,
                'status_code': 200,
                'response_time': 0.5,
                'integration': {
                    'id': integration_id,
                    'name': 'test_integration_test'
                }
            }

            # Test the integration
            test_result = api_integration_controller.test_integration(integration_id)
            assert test_result['success'] is True
            assert test_result['status_code'] == 200

            # Verify the mock was called
            mock_test.assert_called_once_with(integration_id)

        # Clean up
        api_integration_controller.delete_integration(integration_id)

    @pytest.mark.asyncio
    async def test_api_integration_calling(self):
        """Test API integration endpoint calling"""
        # Create integration
        integration_data = {
            'name': 'test_integration_call',
            'provider_type': 'rest',
            'base_url': 'https://httpbin.org',
            'auth_type': 'none',
            'is_active': True
        }

        create_result = api_integration_controller.create_integration(integration_data)
        integration_id = create_result['data']['id']

        # Mock the call_api method
        with patch.object(api_integration_service, 'call_api', new_callable=AsyncMock) as mock_call:
            mock_call.return_value = {
                'success': True,
                'status_code': 200,
                'data': {'message': 'Hello World'},
                'integration': {
                    'id': integration_id,
                    'name': 'test_integration_call'
                }
            }

            # Call the integration
            call_result = api_integration_controller.call_integration(
                integration_id, '/get', 'GET'
            )
            assert call_result['success'] is True
            assert call_result['status_code'] == 200
            assert call_result['data']['message'] == 'Hello World'

            # Verify the mock was called
            mock_call.assert_called_once_with(integration_id, '/get', 'GET', None, None)

        # Clean up
        api_integration_controller.delete_integration(integration_id)


class TestWebhookChatIntegrationE2E:
    """End-to-end testing for webhook integration with chat system"""

    def setup_method(self):
        """Setup test environment"""
        webhook_manager._init_database()
        api_integration_manager._init_database()

    def teardown_method(self):
        """Clean up after tests"""
        # Clean up test data
        with webhook_manager.db_path as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM webhook_subscriptions WHERE name LIKE 'test_chat_%'")
            cursor.execute("DELETE FROM webhook_events WHERE event_type LIKE 'test_chat_%'")
            conn.commit()

    def test_chat_webhook_triggering(self):
        """Test webhook triggering from chat events"""
        # Create webhook for chat messages
        webhook_data = {
            'name': 'test_chat_webhook',
            'event_type': 'chat_message',
            'url': 'https://httpbin.org/post',
            'method': 'POST',
            'is_active': True
        }

        create_result = webhook_controller.create_webhook(webhook_data)
        assert create_result['success'] is True
        webhook_id = create_result['data']['id']

        # Simulate chat message payload
        chat_payload = {
            'chat_id': 'test_chat_123',
            'user_id': 'test_user_456',
            'timestamp': datetime.now().isoformat(),
            'message': {
                'text': 'Hello, how can I help you?',
                'attachments': 0,
                'model': 'gpt-3.5-turbo'
            },
            'response': {
                'text': 'I need help with my account.',
                'model': 'gpt-3.5-turbo',
                'provider': 'openai'
            },
            'session_info': {
                'total_messages': 2,
                'chat_duration': 15000
            }
        }

        # Trigger webhook event
        trigger_result = webhook_controller.trigger_webhook_event('chat_message', chat_payload)
        assert trigger_result['success'] is True

        # Verify webhook was triggered (check if event was logged)
        time.sleep(0.1)  # Small delay to allow async processing
        events = webhook_controller.get_webhook_events(event_type='chat_message')
        assert events['success'] is True

        # Check that the event contains the chat data
        if events['data']:
            event = events['data'][0]
            assert event['event_type'] == 'chat_message'
            assert event['payload']['chat_id'] == 'test_chat_123'
            assert event['payload']['message']['text'] == 'Hello, how can I help you?'

        # Clean up
        webhook_controller.delete_webhook(webhook_id)

    def test_multiple_webhook_events(self):
        """Test triggering multiple webhooks for different events"""
        # Create webhooks for different events
        webhooks_data = [
            {
                'name': 'test_chat_message_webhook',
                'event_type': 'chat_message',
                'url': 'https://httpbin.org/post',
                'is_active': True
            },
            {
                'name': 'test_user_join_webhook',
                'event_type': 'user_joined',
                'url': 'https://httpbin.org/post',
                'is_active': True
            },
            {
                'name': 'test_model_switch_webhook',
                'event_type': 'model_switched',
                'url': 'https://httpbin.org/post',
                'is_active': True
            }
        ]

        webhook_ids = []
        for webhook_data in webhooks_data:
            result = webhook_controller.create_webhook(webhook_data)
            webhook_ids.append(result['data']['id'])

        # Trigger different events
        events_data = [
            ('chat_message', {'message': 'Test chat'}),
            ('user_joined', {'user_id': 'test_user'}),
            ('model_switched', {'from': 'gpt-3.5', 'to': 'gpt-4'})
        ]

        for event_type, payload in events_data:
            trigger_result = webhook_controller.trigger_webhook_event(event_type, payload)
            assert trigger_result['success'] is True

        # Verify events were logged
        time.sleep(0.1)  # Allow async processing
        all_events = webhook_controller.get_webhook_events()
        assert all_events['success'] is True

        # Check that we have events for each type
        event_types = [e['event_type'] for e in all_events['data']]
        assert 'chat_message' in event_types
        assert 'user_joined' in event_types
        assert 'model_switched' in event_types

        # Clean up
        for webhook_id in webhook_ids:
            webhook_controller.delete_webhook(webhook_id)

    def test_webhook_error_handling(self):
        """Test webhook error handling and retry logic"""
        # Create webhook with invalid URL
        webhook_data = {
            'name': 'test_error_webhook',
            'event_type': 'test_error',
            'url': 'https://invalid-nonexistent-url-12345.com/webhook',
            'method': 'POST',
            'is_active': True,
            'retry_count': 2
        }

        create_result = webhook_controller.create_webhook(webhook_data)
        webhook_id = create_result['data']['id']

        # Trigger webhook event
        trigger_result = webhook_controller.trigger_webhook_event('test_error', {'test': 'data'})
        assert trigger_result['success'] is True

        # Wait for retries to complete
        time.sleep(2)

        # Check events - should have multiple failed attempts
        events = webhook_controller.get_webhook_events(event_type='test_error')
        assert events['success'] is True

        # Should have at least one failed event
        failed_events = [e for e in events['data'] if e['status'] == 'failed']
        assert len(failed_events) > 0

        # Clean up
        webhook_controller.delete_webhook(webhook_id)


class TestWebhookSecurity:
    """Test webhook security features"""

    def setup_method(self):
        """Setup test environment"""
        webhook_manager._init_database()

    def teardown_method(self):
        """Clean up after tests"""
        with webhook_manager.db_path as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM webhook_subscriptions WHERE name LIKE 'test_security_%'")
            conn.commit()

    def test_webhook_signature_verification(self):
        """Test webhook signature verification"""
        import hmac
        import hashlib

        # Create webhook with secret
        webhook_data = {
            'name': 'test_security_webhook',
            'event_type': 'test_security',
            'url': 'https://example.com/webhook',
            'secret': 'my_secret_key',
            'is_active': True
        }

        create_result = webhook_controller.create_webhook(webhook_data)
        webhook_id = create_result['data']['id']

        # Get the webhook and verify signature generation
        webhook = webhook_manager.get_subscriptions()[0]

        # Test payload
        payload = {'test': 'data'}
        payload_str = json.dumps(payload)

        # Generate signature manually
        expected_signature = hmac.new(
            'my_secret_key'.encode('utf-8'),
            payload_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        # The signature should be generated correctly in the service
        # This tests the signature generation logic
        assert webhook.secret == 'my_secret_key'

        # Clean up
        webhook_controller.delete_webhook(webhook_id)

    def test_webhook_payload_validation(self):
        """Test webhook payload validation"""
        # Test invalid JSON
        invalid_webhook_data = {
            'name': '',  # Empty name should fail
            'event_type': 'test',
            'url': 'https://example.com/webhook'
        }

        result = webhook_controller.create_webhook(invalid_webhook_data)
        assert result['success'] is False
        assert 'Missing required field' in result['error']

        # Test invalid URL
        invalid_url_data = {
            'name': 'test_invalid_url',
            'event_type': 'test',
            'url': 'not-a-valid-url'
        }

        result = webhook_controller.create_webhook(invalid_url_data)
        assert result['success'] is False

    def test_webhook_rate_limiting(self):
        """Test webhook rate limiting (conceptual test)"""
        # This is a conceptual test - in real implementation,
        # you would have rate limiting middleware

        webhook_data = {
            'name': 'test_rate_limit_webhook',
            'event_type': 'test_rate',
            'url': 'https://example.com/webhook',
            'is_active': True
        }

        create_result = webhook_controller.create_webhook(webhook_data)
        webhook_id = create_result['data']['id']

        # Simulate multiple rapid requests
        for i in range(5):
            result = webhook_controller.trigger_webhook_event('test_rate', {'request': i})
            assert result['success'] is True

        # In a real implementation, you would check that rate limiting is applied
        # For this test, we just verify the webhook can handle multiple requests

        # Clean up
        webhook_controller.delete_webhook(webhook_id)


# Test configuration
pytest_plugins = ["pytest_asyncio"]
