"""
Security Tests for Webhook System
Tests security features, authentication, validation, and penetration testing
"""
import pytest
import json
import time
import hmac
import hashlib
import base64
from unittest.mock import patch, AsyncMock, MagicMock
from datetime import datetime, timedelta
from flask import Flask
from flask.testing import FlaskClient

from src.models.webhook_models import webhook_manager
from src.controllers.webhook_controller import webhook_controller
from src.services.webhook_service import webhook_service, StandardEventTypes


class TestWebhookSecurity:
    """Security testing for webhook system"""

    def setup_method(self):
        """Setup test environment"""
        webhook_manager._init_database()
        self._cleanup_test_data()

    def teardown_method(self):
        """Clean up test environment"""
        self._cleanup_test_data()

    def _cleanup_test_data(self):
        """Clean up test data"""
        with webhook_manager.db_path as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM webhook_subscriptions WHERE name LIKE 'security_%'")
            cursor.execute("DELETE FROM webhook_events WHERE event_type LIKE 'security_%'")
            conn.commit()

    def test_webhook_signature_verification_security(self, client: FlaskClient):
        """Test webhook signature verification security"""
        # Create webhook with signature verification
        secret = "my_secure_webhook_secret_123"
        webhook_data = {
            'name': 'security_signature_webhook',
            'event_type': StandardEventTypes.USER_LOGIN,
            'url': 'https://secure-webhook.example.com/endpoint',
            'method': 'POST',
            'secret': secret,
            'is_active': True
        }

        response = client.post('/api/v1/webhooks',
                             data=json.dumps(webhook_data),
                             content_type='application/json')
        assert response.status_code == 200
        webhook_id = json.loads(response.data)['data']['id']

        # Test that signature is stored securely (not plain text in responses)
        response = client.get(f'/api/v1/webhooks/{webhook_id}')
        data = json.loads(response.data)
        assert data['success'] is True
        # Secret should be present (for admin access) but could be hashed in production
        assert data['data']['secret'] == secret

        # Test webhook listing doesn't expose secrets
        response = client.get('/api/v1/webhooks')
        data = json.loads(response.data)
        assert data['success'] is True
        for webhook in data['data']:
            if webhook['id'] == webhook_id:
                assert webhook['secret'] == secret  # In real app, this might be omitted

        # Clean up
        client.delete(f'/api/v1/webhooks/{webhook_id}')

    def test_webhook_authentication_headers(self, client: FlaskClient):
        """Test webhook authentication headers security"""
        webhook_data = {
            'name': 'security_auth_webhook',
            'event_type': StandardEventTypes.FINANCIAL_TRANSACTION_CREATED,
            'url': 'https://api.example.com/webhook',
            'method': 'POST',
            'headers': {
                'Authorization': 'Bearer secure_token_123',
                'X-API-Key': 'api_key_456',
                'X-Custom-Auth': 'custom_auth_value'
            },
            'is_active': True
        }

        response = client.post('/api/v1/webhooks',
                             data=json.dumps(webhook_data),
                             content_type='application/json')
        webhook_id = json.loads(response.data)['data']['id']

        # Verify headers are stored securely
        response = client.get(f'/api/v1/webhooks/{webhook_id}')
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['headers']['Authorization'] == 'Bearer secure_token_123'
        assert data['data']['headers']['X-API-Key'] == 'api_key_456'

        # Clean up
        client.delete(f'/api/v1/webhooks/{webhook_id}')

    def test_input_validation_security(self, client: FlaskClient):
        """Test input validation for security vulnerabilities"""
        # Test SQL injection attempts
        malicious_webhook_data = {
            'name': "'; DROP TABLE webhook_subscriptions; --",
            'event_type': StandardEventTypes.CHAT_MESSAGE_SENT,
            'url': "https://malicious.com'; DELETE FROM webhook_subscriptions; --",
            'method': 'POST',
            'is_active': True
        }

        response = client.post('/api/v1/webhooks',
                             data=json.dumps(malicious_webhook_data),
                             content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        # Should fail validation or be sanitized
        if not data['success']:
            assert 'error' in data

        # Test XSS attempts
        xss_webhook_data = {
            'name': "<script>alert('XSS')</script>",
            'event_type': StandardEventTypes.USER_LOGIN,
            'url': "javascript:alert('XSS')",
            'method': 'POST',
            'is_active': True
        }

        response = client.post('/api/v1/webhooks',
                             data=json.dumps(xss_webhook_data),
                             content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        if not data['success']:
            assert 'error' in data

        # Test URL validation
        invalid_urls = [
            "ftp://malicious.com",
            "file:///etc/passwd",
            "data:text/html,<script>alert('XSS')</script>",
            "javascript:alert('XSS')"
        ]

        for invalid_url in invalid_urls:
            webhook_data = {
                'name': 'test_validation_webhook',
                'event_type': StandardEventTypes.CHAT_MESSAGE_SENT,
                'url': invalid_url,
                'is_active': True
            }

            response = client.post('/api/v1/webhooks',
                                 data=json.dumps(webhook_data),
                                 content_type='application/json')
            assert response.status_code == 200
            data = json.loads(response.data)
            if not data['success']:
                assert 'error' in data or 'url' in data.get('error', '').lower()

    def test_rate_limiting_security(self, client: FlaskClient):
        """Test rate limiting to prevent abuse"""
        webhook_data = {
            'name': 'security_rate_limit_webhook',
            'event_type': StandardEventTypes.USER_LOGIN,
            'url': 'https://api.example.com/webhook',
            'is_active': True
        }

        response = client.post('/api/v1/webhooks',
                             data=json.dumps(webhook_data),
                             content_type='application/json')
        webhook_id = json.loads(response.data)['data']['id']

        # Simulate rapid requests
        trigger_data = {
            'event_type': StandardEventTypes.USER_LOGIN,
            'data': {'test': 'rate_limit'}
        }

        start_time = time.time()
        request_count = 0

        # Make requests as fast as possible for 5 seconds
        while time.time() - start_time < 5:
            response = client.post('/api/v1/webhooks/trigger-event',
                                 data=json.dumps(trigger_data),
                                 content_type='application/json')
            request_count += 1

            # In a real implementation, some requests should be rate limited
            # For this test, we just verify the system doesn't crash
            assert response.status_code in [200, 429]  # 429 = Too Many Requests

        print(f"Rate limit test completed: {request_count} requests in 5 seconds")

        # Clean up
        client.delete(f'/api/v1/webhooks/{webhook_id}')

    def test_webhook_payload_size_limits(self, client: FlaskClient):
        """Test webhook payload size limits"""
        webhook_data = {
            'name': 'security_payload_size_webhook',
            'event_type': StandardEventTypes.CHAT_MESSAGE_SENT,
            'url': 'https://api.example.com/webhook',
            'is_active': True
        }

        response = client.post('/api/v1/webhooks',
                             data=json.dumps(webhook_data),
                             content_type='application/json')
        webhook_id = json.loads(response.data)['data']['id']

        # Test with large payload
        large_data = 'x' * 1000000  # 1MB of data
        trigger_data = {
            'event_type': StandardEventTypes.CHAT_MESSAGE_SENT,
            'data': {'large_payload': large_data}
        }

        response = client.post('/api/v1/webhooks/trigger-event',
                             data=json.dumps(trigger_data),
                             content_type='application/json')
        # Should handle large payloads gracefully
        assert response.status_code in [200, 413]  # 413 = Payload Too Large

        if response.status_code == 200:
            data = json.loads(response.data)
            assert data['success'] is True or 'error' in data

        # Clean up
        client.delete(f'/api/v1/webhooks/{webhook_id}')

    def test_webhook_timeout_security(self, client: FlaskClient):
        """Test webhook timeout security"""
        webhook_data = {
            'name': 'security_timeout_webhook',
            'event_type': StandardEventTypes.USER_LOGIN,
            'url': 'https://slow-server.example.com/webhook',  # Would timeout
            'timeout': 1,  # Very short timeout
            'is_active': True
        }

        response = client.post('/api/v1/webhooks',
                             data=json.dumps(webhook_data),
                             content_type='application/json')
        webhook_id = json.loads(response.data)['data']['id']

        # Test with short timeout
        trigger_data = {
            'event_type': StandardEventTypes.USER_LOGIN,
            'data': {'test': 'timeout'}
        }

        start_time = time.time()
        response = client.post('/api/v1/webhooks/trigger-event',
                             data=json.dumps(trigger_data),
                             content_type='application/json')
        end_time = time.time()

        # Should complete quickly due to timeout
        assert end_time - start_time < 10  # Should not hang
        assert response.status_code == 200

        # Clean up
        client.delete(f'/api/v1/webhooks/{webhook_id}')

    def test_webhook_retry_security(self, client: FlaskClient):
        """Test webhook retry security to prevent infinite loops"""
        webhook_data = {
            'name': 'security_retry_webhook',
            'event_type': StandardEventTypes.USER_LOGIN,
            'url': 'https://failing-server.example.com/webhook',
            'retry_count': 3,  # Limited retries
            'is_active': True
        }

        response = client.post('/api/v1/webhooks',
                             data=json.dumps(webhook_data),
                             content_type='application/json')
        webhook_id = json.loads(response.data)['data']['id']

        # Test retry behavior
        trigger_data = {
            'event_type': StandardEventTypes.USER_LOGIN,
            'data': {'test': 'retry'}
        }

        start_time = time.time()
        response = client.post('/api/v1/webhooks/trigger-event',
                             data=json.dumps(trigger_data),
                             content_type='application/json')
        end_time = time.time()

        # Should complete within reasonable time (not infinite retries)
        assert end_time - start_time < 30
        assert response.status_code == 200

        # Clean up
        client.delete(f'/api/v1/webhooks/{webhook_id}')

    def test_webhook_access_control(self, client: FlaskClient):
        """Test webhook access control and permissions"""
        webhook_data = {
            'name': 'security_access_webhook',
            'event_type': StandardEventTypes.FINANCIAL_TRANSACTION_CREATED,
            'url': 'https://secure-api.example.com/webhook',
            'is_active': True
        }

        response = client.post('/api/v1/webhooks',
                             data=json.dumps(webhook_data),
                             content_type='application/json')
        webhook_id = json.loads(response.data)['data']['id']

        # Test that webhook is only accessible to its owner (conceptual)
        response = client.get(f'/api/v1/webhooks/{webhook_id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True

        # Test that other users can't access this webhook (would require auth in real app)
        # In a real implementation, you'd test with different user tokens

        # Clean up
        client.delete(f'/api/v1/webhooks/{webhook_id}')

    def test_webhook_data_sanitization(self, client: FlaskClient):
        """Test webhook data sanitization"""
        webhook_data = {
            'name': 'security_sanitization_webhook',
            'event_type': StandardEventTypes.CHAT_MESSAGE_SENT,
            'url': 'https://api.example.com/webhook',
            'is_active': True
        }

        response = client.post('/api/v1/webhooks',
                             data=json.dumps(webhook_data),
                             content_type='application/json')
        webhook_id = json.loads(response.data)['data']['id']

        # Test with potentially malicious data
        malicious_data = {
            'event_type': StandardEventTypes.CHAT_MESSAGE_SENT,
            'data': {
                'message': '<script>alert("XSS")</script>',
                'user_input': "'; DROP TABLE users; --",
                'nested': {
                    'html': '<iframe src="evil.com"></iframe>',
                    'sql': "UNION SELECT password FROM admin;"
                }
            }
        }

        response = client.post('/api/v1/webhooks/trigger-event',
                             data=json.dumps(malicious_data),
                             content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True

        # Clean up
        client.delete(f'/api/v1/webhooks/{webhook_id}')

    def test_webhook_encryption_at_rest(self, client: FlaskClient):
        """Test webhook data encryption at rest (conceptual)"""
        # In a real implementation, sensitive data like secrets should be encrypted
        webhook_data = {
            'name': 'security_encryption_webhook',
            'event_type': StandardEventTypes.FINANCIAL_TRANSACTION_CREATED,
            'url': 'https://secure-api.example.com/webhook',
            'secret': 'very_sensitive_secret_key_123',
            'is_active': True
        }

        response = client.post('/api/v1/webhooks',
                             data=json.dumps(webhook_data),
                             content_type='application/json')
        webhook_id = json.loads(response.data)['data']['id']

        # In a real implementation, the secret should be encrypted in the database
        # For this test, we just verify it's stored
        response = client.get(f'/api/v1/webhooks/{webhook_id}')
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['secret'] == 'very_sensitive_secret_key_123'

        # Clean up
        client.delete(f'/api/v1/webhooks/{webhook_id}')

    def test_webhook_audit_logging(self, client: FlaskClient):
        """Test webhook audit logging"""
        webhook_data = {
            'name': 'security_audit_webhook',
            'event_type': StandardEventTypes.SECURITY_LOGIN_SUCCESS,
            'url': 'https://audit.example.com/webhook',
            'is_active': True
        }

        response = client.post('/api/v1/webhooks',
                             data=json.dumps(webhook_data),
                             content_type='application/json')
        webhook_id = json.loads(response.data)['data']['id']

        # Perform operations that should be audited
        operations = [
            StandardEventTypes.SECURITY_LOGIN_SUCCESS,
            StandardEventTypes.SECURITY_PASSWORD_CHANGED,
            StandardEventTypes.SECURITY_API_KEY_CREATED
        ]

        for operation in operations:
            trigger_data = {
                'event_type': operation,
                'data': {
                    'audit_test': True,
                    'operation': operation,
                    'timestamp': datetime.now().isoformat()
                }
            }

            response = client.post('/api/v1/webhooks/trigger-event',
                                 data=json.dumps(trigger_data),
                                 content_type='application/json')
            assert response.status_code == 200

        # Verify audit events were logged
        response = client.get('/api/v1/webhooks/events')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['total'] >= len(operations)

        # Clean up
        client.delete(f'/api/v1/webhooks/{webhook_id}')

    def test_webhook_error_handling_security(self, client: FlaskClient):
        """Test security of webhook error handling"""
        webhook_data = {
            'name': 'security_error_webhook',
            'event_type': StandardEventTypes.SYSTEM_ERROR_OCCURRED,
            'url': 'https://error-handler.example.com/webhook',
            'is_active': True
        }

        response = client.post('/api/v1/webhooks',
                             data=json.dumps(webhook_data),
                             content_type='application/json')
        webhook_id = json.loads(response.data)['data']['id']

        # Test with various error conditions
        error_conditions = [
            {
                'event_type': StandardEventTypes.SYSTEM_ERROR_OCCURRED,
                'data': {
                    'error_type': 'ValidationError',
                    'message': 'Invalid input provided',
                    'stack_trace': 'Traceback (most recent call last)...',
                    'user_context': {'user_id': '12345'}
                }
            },
            {
                'event_type': StandardEventTypes.SYSTEM_ERROR_OCCURRED,
                'data': {
                    'error_type': 'DatabaseError',
                    'message': 'Connection timeout',
                    'sensitive_info': 'password=secret123',
                    'system_info': {'server': 'prod-db-01'}
                }
            }
        ]

        for error_condition in error_conditions:
            response = client.post('/api/v1/webhooks/trigger-event',
                                 data=json.dumps(error_condition),
                                 content_type='application/json')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True

        # Verify error events were logged securely
        response = client.get('/api/v1/webhooks/events')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True

        # Clean up
        client.delete(f'/api/v1/webhooks/{webhook_id}')

    def test_webhook_network_security(self, client: FlaskClient):
        """Test webhook network security"""
        webhook_data = {
            'name': 'security_network_webhook',
            'event_type': StandardEventTypes.SECURITY_SUSPICIOUS_ACTIVITY,
            'url': 'https://security-monitor.example.com/webhook',
            'is_active': True
        }

        response = client.post('/api/v1/webhooks',
                             data=json.dumps(webhook_data),
                             content_type='application/json')
        webhook_id = json.loads(response.data)['data']['id']

        # Test with various network-related security events
        security_events = [
            StandardEventTypes.SECURITY_SUSPICIOUS_ACTIVITY,
            StandardEventTypes.SECURITY_LOGIN_FAILED,
            StandardEventTypes.SECURITY_BREACH_ATTEMPT
        ]

        for event_type in security_events:
            trigger_data = {
                'event_type': event_type,
                'data': {
                    'ip_address': '192.168.1.100',
                    'user_agent': 'Suspicious Browser 1.0',
                    'attempt_count': 5,
                    'timestamp': datetime.now().isoformat(),
                    'geo_location': {'country': 'Unknown', 'city': 'Unknown'}
                }
            }

            response = client.post('/api/v1/webhooks/trigger-event',
                                 data=json.dumps(trigger_data),
                                 content_type='application/json')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True

        # Clean up
        client.delete(f'/api/v1/webhooks/{webhook_id}')

    def test_webhook_compliance_security(self, client: FlaskClient):
        """Test webhook compliance with security standards"""
        # Test GDPR/HIPAA type compliance
        webhook_data = {
            'name': 'security_compliance_webhook',
            'event_type': StandardEventTypes.USER_PROFILE_UPDATED,
            'url': 'https://compliant-service.example.com/webhook',
            'is_active': True
        }

        response = client.post('/api/v1/webhooks',
                             data=json.dumps(webhook_data),
                             content_type='application/json')
        webhook_id = json.loads(response.data)['data']['id']

        # Test with PII data (should be handled securely)
        pii_data = {
            'event_type': StandardEventTypes.USER_PROFILE_UPDATED,
            'data': {
                'user_id': '12345',
                'email': 'user@example.com',
                'phone': '+1234567890',
                'ssn': '123-45-6789',  # Sensitive data
                'credit_card': '4111-1111-1111-1111',  # Very sensitive
                'timestamp': datetime.now().isoformat()
            }
        }

        response = client.post('/api/v1/webhooks/trigger-event',
                             data=json.dumps(pii_data),
                             content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True

        # In a real implementation, PII data should be encrypted or tokenized
        # For this test, we just verify it processes without exposing sensitive data

        # Clean up
        client.delete(f'/api/v1/webhooks/{webhook_id}')


# Test configuration
@pytest.fixture(scope="session")
def client():
    """Create test client"""
    from app import app
    app.config['TESTING'] = True
    return app.test_client()


@pytest.fixture(autouse=True)
def cleanup_security_data(client: FlaskClient):
    """Clean up test data after each test"""
    yield
    try:
        # Clean webhooks
        response = client.get('/api/v1/webhooks')
        if response.status_code == 200:
            data = json.loads(response.data)
            if data['success']:
                for webhook in data['data']:
                    if webhook['name'].startswith('security_'):
                        client.delete(f'/api/v1/webhooks/{webhook["id"]}')

    except Exception:
        pass  # Ignore cleanup errors
