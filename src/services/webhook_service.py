"""
Webhook Service for managing webhook operations and API integrations
Enhanced with comprehensive event types and advanced features
"""
import asyncio
import aiohttp
import requests
import json
import hmac
import hashlib
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from urllib.parse import urljoin
import logging
from dataclasses import dataclass, asdict

from src.models.webhook_models import (
    WebhookSubscription,
    WebhookEvent,
    APIIntegration,
    webhook_manager,
    api_integration_manager
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class WebhookEventPayload:
    """Standard webhook event payload structure"""
    event_id: str
    event_type: str
    timestamp: str
    source: str
    data: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if not self.event_id:
            self.event_id = str(uuid.uuid4())
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


class StandardEventTypes:
    """Comprehensive standard event types"""

    # Chat & Communication Events
    CHAT_MESSAGE_SENT = "chat.message.sent"
    CHAT_MESSAGE_RECEIVED = "chat.message.received"
    CHAT_MESSAGE_EDITED = "chat.message.edited"
    CHAT_MESSAGE_DELETED = "chat.message.deleted"
    CHAT_TYPING_START = "chat.typing.start"
    CHAT_TYPING_STOP = "chat.typing.stop"
    CHAT_USER_JOINED = "chat.user.joined"
    CHAT_USER_LEFT = "chat.user.left"
    CHAT_USER_BANNED = "chat.user.banned"
    CHAT_USER_UNBANNED = "chat.user.unbanned"
    CHAT_ROOM_CREATED = "chat.room.created"
    CHAT_ROOM_UPDATED = "chat.room.updated"
    CHAT_ROOM_DELETED = "chat.room.deleted"

    # AI & Model Events
    AI_MODEL_SWITCHED = "ai.model.switched"
    AI_RESPONSE_GENERATED = "ai.response.generated"
    AI_RESPONSE_FAILED = "ai.response.failed"
    AI_TOKEN_USAGE = "ai.token.usage"
    AI_RATE_LIMIT_HIT = "ai.rate.limit.hit"
    AI_QUOTA_EXCEEDED = "ai.quota.exceeded"

    # User & Authentication Events
    USER_CREATED = "user.created"
    USER_UPDATED = "user.updated"
    USER_DELETED = "user.deleted"
    USER_LOGIN = "user.login"
    USER_LOGOUT = "user.logout"
    USER_PASSWORD_RESET = "user.password.reset"
    USER_EMAIL_VERIFIED = "user.email.verified"
    USER_PROFILE_UPDATED = "user.profile.updated"

    # Financial & Business Events
    FINANCIAL_TRANSACTION_CREATED = "financial.transaction.created"
    FINANCIAL_TRANSACTION_UPDATED = "financial.transaction.updated"
    FINANCIAL_TRANSACTION_COMPLETED = "financial.transaction.completed"
    FINANCIAL_INVOICE_CREATED = "financial.invoice.created"
    FINANCIAL_INVOICE_PAID = "financial.invoice.paid"
    FINANCIAL_PAYMENT_RECEIVED = "financial.payment.received"
    FINANCIAL_PAYMENT_FAILED = "financial.payment.failed"
    FINANCIAL_REFUND_PROCESSED = "financial.refund.processed"
    FINANCIAL_SUBSCRIPTION_CREATED = "financial.subscription.created"
    FINANCIAL_SUBSCRIPTION_CANCELLED = "financial.subscription.cancelled"

    # System & Error Events
    SYSTEM_ERROR_OCCURRED = "system.error.occurred"
    SYSTEM_WARNING_TRIGGERED = "system.warning.triggered"
    SYSTEM_MAINTENANCE_STARTED = "system.maintenance.started"
    SYSTEM_MAINTENANCE_COMPLETED = "system.maintenance.completed"
    SYSTEM_BACKUP_STARTED = "system.backup.started"
    SYSTEM_BACKUP_COMPLETED = "system.backup.completed"
    SYSTEM_UPDATE_AVAILABLE = "system.update.available"
    SYSTEM_UPDATE_INSTALLED = "system.update.installed"

    # API & Integration Events
    API_REQUEST_RECEIVED = "api.request.received"
    API_REQUEST_COMPLETED = "api.request.completed"
    API_REQUEST_FAILED = "api.request.failed"
    API_RATE_LIMIT_EXCEEDED = "api.rate.limit.exceeded"
    API_INTEGRATION_CONNECTED = "api.integration.connected"
    API_INTEGRATION_DISCONNECTED = "api.integration.disconnected"
    API_INTEGRATION_ERROR = "api.integration.error"

    # Security Events
    SECURITY_LOGIN_ATTEMPT = "security.login.attempt"
    SECURITY_LOGIN_FAILED = "security.login.failed"
    SECURITY_LOGIN_SUCCESS = "security.login.success"
    SECURITY_LOGOUT = "security.logout"
    SECURITY_PASSWORD_CHANGED = "security.password.changed"
    SECURITY_SUSPICIOUS_ACTIVITY = "security.suspicious.activity"
    SECURITY_BREACH_ATTEMPT = "security.breach.attempt"
    SECURITY_API_KEY_CREATED = "security.api.key.created"
    SECURITY_API_KEY_REVOKED = "security.api.key.revoked"

    # File & Media Events
    FILE_UPLOADED = "file.uploaded"
    FILE_DOWNLOADED = "file.downloaded"
    FILE_DELETED = "file.deleted"
    FILE_PROCESSING_STARTED = "file.processing.started"
    FILE_PROCESSING_COMPLETED = "file.processing.completed"
    FILE_PROCESSING_FAILED = "file.processing.failed"
    MEDIA_CONVERSION_STARTED = "media.conversion.started"
    MEDIA_CONVERSION_COMPLETED = "media.conversion.completed"

    # Analytics & Monitoring Events
    ANALYTICS_PAGE_VIEW = "analytics.page.view"
    ANALYTICS_USER_ACTION = "analytics.user.action"
    ANALYTICS_FEATURE_USAGE = "analytics.feature.usage"
    ANALYTICS_PERFORMANCE_METRIC = "analytics.performance.metric"
    ANALYTICS_ERROR_TRACKED = "analytics.error.tracked"
    ANALYTICS_CONVERSION_COMPLETED = "analytics.conversion.completed"

    # Notification Events
    NOTIFICATION_SENT = "notification.sent"
    NOTIFICATION_DELIVERED = "notification.delivered"
    NOTIFICATION_FAILED = "notification.failed"
    NOTIFICATION_CLICKED = "notification.clicked"
    NOTIFICATION_DISMISSED = "notification.dismissed"

    # Workflow & Automation Events
    WORKFLOW_STARTED = "workflow.started"
    WORKFLOW_COMPLETED = "workflow.completed"
    WORKFLOW_FAILED = "workflow.failed"
    WORKFLOW_STEP_COMPLETED = "workflow.step.completed"
    AUTOMATION_TRIGGERED = "automation.triggered"
    AUTOMATION_EXECUTED = "automation.executed"

    # Database & Data Events
    DATABASE_RECORD_CREATED = "database.record.created"
    DATABASE_RECORD_UPDATED = "database.record.updated"
    DATABASE_RECORD_DELETED = "database.record.deleted"
    DATABASE_BACKUP_CREATED = "database.backup.created"
    DATABASE_MIGRATION_STARTED = "database.migration.started"
    DATABASE_MIGRATION_COMPLETED = "database.migration.completed"

    # Third-party Integration Events
    INTEGRATION_WEBHOOK_RECEIVED = "integration.webhook.received"
    INTEGRATION_API_CALLED = "integration.api.called"
    INTEGRATION_DATA_SYNCED = "integration.data.synced"
    INTEGRATION_ERROR_OCCURRED = "integration.error.occurred"

    # All event types as a list for easy reference
    ALL_EVENTS = [
        # Chat events
        CHAT_MESSAGE_SENT, CHAT_MESSAGE_RECEIVED, CHAT_MESSAGE_EDITED, CHAT_MESSAGE_DELETED,
        CHAT_TYPING_START, CHAT_TYPING_STOP, CHAT_USER_JOINED, CHAT_USER_LEFT,
        CHAT_USER_BANNED, CHAT_USER_UNBANNED, CHAT_ROOM_CREATED, CHAT_ROOM_UPDATED, CHAT_ROOM_DELETED,

        # AI events
        AI_MODEL_SWITCHED, AI_RESPONSE_GENERATED, AI_RESPONSE_FAILED, AI_TOKEN_USAGE,
        AI_RATE_LIMIT_HIT, AI_QUOTA_EXCEEDED,

        # User events
        USER_CREATED, USER_UPDATED, USER_DELETED, USER_LOGIN, USER_LOGOUT,
        USER_PASSWORD_RESET, USER_EMAIL_VERIFIED, USER_PROFILE_UPDATED,

        # Financial events
        FINANCIAL_TRANSACTION_CREATED, FINANCIAL_TRANSACTION_UPDATED, FINANCIAL_TRANSACTION_COMPLETED,
        FINANCIAL_INVOICE_CREATED, FINANCIAL_INVOICE_PAID, FINANCIAL_PAYMENT_RECEIVED,
        FINANCIAL_PAYMENT_FAILED, FINANCIAL_REFUND_PROCESSED, FINANCIAL_SUBSCRIPTION_CREATED,
        FINANCIAL_SUBSCRIPTION_CANCELLED,

        # System events
        SYSTEM_ERROR_OCCURRED, SYSTEM_WARNING_TRIGGERED, SYSTEM_MAINTENANCE_STARTED,
        SYSTEM_MAINTENANCE_COMPLETED, SYSTEM_BACKUP_STARTED, SYSTEM_BACKUP_COMPLETED,
        SYSTEM_UPDATE_AVAILABLE, SYSTEM_UPDATE_INSTALLED,

        # API events
        API_REQUEST_RECEIVED, API_REQUEST_COMPLETED, API_REQUEST_FAILED, API_RATE_LIMIT_EXCEEDED,
        API_INTEGRATION_CONNECTED, API_INTEGRATION_DISCONNECTED, API_INTEGRATION_ERROR,

        # Security events
        SECURITY_LOGIN_ATTEMPT, SECURITY_LOGIN_FAILED, SECURITY_LOGIN_SUCCESS, SECURITY_LOGOUT,
        SECURITY_PASSWORD_CHANGED, SECURITY_SUSPICIOUS_ACTIVITY, SECURITY_BREACH_ATTEMPT,
        SECURITY_API_KEY_CREATED, SECURITY_API_KEY_REVOKED,

        # File events
        FILE_UPLOADED, FILE_DOWNLOADED, FILE_DELETED, FILE_PROCESSING_STARTED,
        FILE_PROCESSING_COMPLETED, FILE_PROCESSING_FAILED, MEDIA_CONVERSION_STARTED,
        MEDIA_CONVERSION_COMPLETED,

        # Analytics events
        ANALYTICS_PAGE_VIEW, ANALYTICS_USER_ACTION, ANALYTICS_FEATURE_USAGE,
        ANALYTICS_PERFORMANCE_METRIC, ANALYTICS_ERROR_TRACKED, ANALYTICS_CONVERSION_COMPLETED,

        # Notification events
        NOTIFICATION_SENT, NOTIFICATION_DELIVERED, NOTIFICATION_FAILED,
        NOTIFICATION_CLICKED, NOTIFICATION_DISMISSED,

        # Workflow events
        WORKFLOW_STARTED, WORKFLOW_COMPLETED, WORKFLOW_FAILED, WORKFLOW_STEP_COMPLETED,
        AUTOMATION_TRIGGERED, AUTOMATION_EXECUTED,

        # Database events
        DATABASE_RECORD_CREATED, DATABASE_RECORD_UPDATED, DATABASE_RECORD_DELETED,
        DATABASE_BACKUP_CREATED, DATABASE_MIGRATION_STARTED, DATABASE_MIGRATION_COMPLETED,

        # Integration events
        INTEGRATION_WEBHOOK_RECEIVED, INTEGRATION_API_CALLED, INTEGRATION_DATA_SYNCED,
        INTEGRATION_ERROR_OCCURRED
    ]

    # Event categories for organization
    EVENT_CATEGORIES = {
        'chat': [CHAT_MESSAGE_SENT, CHAT_MESSAGE_RECEIVED, CHAT_MESSAGE_EDITED, CHAT_MESSAGE_DELETED,
                 CHAT_TYPING_START, CHAT_TYPING_STOP, CHAT_USER_JOINED, CHAT_USER_LEFT,
                 CHAT_USER_BANNED, CHAT_USER_UNBANNED, CHAT_ROOM_CREATED, CHAT_ROOM_UPDATED, CHAT_ROOM_DELETED],
        'ai': [AI_MODEL_SWITCHED, AI_RESPONSE_GENERATED, AI_RESPONSE_FAILED, AI_TOKEN_USAGE,
               AI_RATE_LIMIT_HIT, AI_QUOTA_EXCEEDED],
        'user': [USER_CREATED, USER_UPDATED, USER_DELETED, USER_LOGIN, USER_LOGOUT,
                 USER_PASSWORD_RESET, USER_EMAIL_VERIFIED, USER_PROFILE_UPDATED],
        'financial': [FINANCIAL_TRANSACTION_CREATED, FINANCIAL_TRANSACTION_UPDATED, FINANCIAL_TRANSACTION_COMPLETED,
                      FINANCIAL_INVOICE_CREATED, FINANCIAL_INVOICE_PAID, FINANCIAL_PAYMENT_RECEIVED,
                      FINANCIAL_PAYMENT_FAILED, FINANCIAL_REFUND_PROCESSED, FINANCIAL_SUBSCRIPTION_CREATED,
                      FINANCIAL_SUBSCRIPTION_CANCELLED],
        'system': [SYSTEM_ERROR_OCCURRED, SYSTEM_WARNING_TRIGGERED, SYSTEM_MAINTENANCE_STARTED,
                   SYSTEM_MAINTENANCE_COMPLETED, SYSTEM_BACKUP_STARTED, SYSTEM_BACKUP_COMPLETED,
                   SYSTEM_UPDATE_AVAILABLE, SYSTEM_UPDATE_INSTALLED],
        'api': [API_REQUEST_RECEIVED, API_REQUEST_COMPLETED, API_REQUEST_FAILED, API_RATE_LIMIT_EXCEEDED,
                API_INTEGRATION_CONNECTED, API_INTEGRATION_DISCONNECTED, API_INTEGRATION_ERROR],
        'security': [SECURITY_LOGIN_ATTEMPT, SECURITY_LOGIN_FAILED, SECURITY_LOGIN_SUCCESS, SECURITY_LOGOUT,
                     SECURITY_PASSWORD_CHANGED, SECURITY_SUSPICIOUS_ACTIVITY, SECURITY_BREACH_ATTEMPT,
                     SECURITY_API_KEY_CREATED, SECURITY_API_KEY_REVOKED],
        'file': [FILE_UPLOADED, FILE_DOWNLOADED, FILE_DELETED, FILE_PROCESSING_STARTED,
                 FILE_PROCESSING_COMPLETED, FILE_PROCESSING_FAILED, MEDIA_CONVERSION_STARTED,
                 MEDIA_CONVERSION_COMPLETED],
        'analytics': [ANALYTICS_PAGE_VIEW, ANALYTICS_USER_ACTION, ANALYTICS_FEATURE_USAGE,
                      ANALYTICS_PERFORMANCE_METRIC, ANALYTICS_ERROR_TRACKED, ANALYTICS_CONVERSION_COMPLETED],
        'notification': [NOTIFICATION_SENT, NOTIFICATION_DELIVERED, NOTIFICATION_FAILED,
                         NOTIFICATION_CLICKED, NOTIFICATION_DISMISSED],
        'workflow': [WORKFLOW_STARTED, WORKFLOW_COMPLETED, WORKFLOW_FAILED, WORKFLOW_STEP_COMPLETED,
                     AUTOMATION_TRIGGERED, AUTOMATION_EXECUTED],
        'database': [DATABASE_RECORD_CREATED, DATABASE_RECORD_UPDATED, DATABASE_RECORD_DELETED,
                     DATABASE_BACKUP_CREATED, DATABASE_MIGRATION_STARTED, DATABASE_MIGRATION_COMPLETED],
        'integration': [INTEGRATION_WEBHOOK_RECEIVED, INTEGRATION_API_CALLED, INTEGRATION_DATA_SYNCED,
                        INTEGRATION_ERROR_OCCURRED]
    }


class WebhookService:
    """Service for managing webhook operations with comprehensive event support"""

    def __init__(self):
        self.session = None
        self.event_types = StandardEventTypes()
        self.event_queue = asyncio.Queue()
        self.is_processing = False

    async def initialize(self):
        """Initialize HTTP session and start event processor"""
        if not self.session:
            self.session = aiohttp.ClientSession()

        # Start event processing task
        if not self.is_processing:
            self.is_processing = True
            asyncio.create_task(self._process_event_queue())

    async def close(self):
        """Close HTTP session and stop processing"""
        self.is_processing = False
        if self.session:
            await self.session.close()
            self.session = None

    async def _process_event_queue(self):
        """Background task to process queued events"""
        while self.is_processing:
            try:
                # Get event from queue with timeout
                event_data = await asyncio.wait_for(self.event_queue.get(), timeout=1.0)
                await self._send_webhook_event(event_data['subscription'], event_data['event'])
                self.event_queue.task_done()
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error processing event queue: {e}")
                continue

    def get_available_event_types(self) -> List[str]:
        """Get all available event types"""
        return self.event_types.ALL_EVENTS

    def get_event_categories(self) -> Dict[str, List[str]]:
        """Get event types organized by category"""
        return self.event_types.EVENT_CATEGORIES

    def validate_event_type(self, event_type: str) -> bool:
        """Validate if event type is supported"""
        return event_type in self.event_types.ALL_EVENTS

    def get_events_by_category(self, category: str) -> List[str]:
        """Get event types for a specific category"""
        return self.event_types.EVENT_CATEGORIES.get(category, [])

    async def trigger_event(self, event_type: str, data: Dict[str, Any],
                          source: str = "valido_ai", metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Trigger a webhook event with standardized payload"""
        try:
            if not self.validate_event_type(event_type):
                return {
                    'success': False,
                    'error': f'Unsupported event type: {event_type}',
                    'available_types': self.get_available_event_types()
                }

            # Create standardized payload
            payload = WebhookEventPayload(
                event_id="",
                event_type=event_type,
                timestamp="",
                source=source,
                data=data,
                metadata=metadata or {}
            )

            # Get subscriptions for this event type
            subscriptions = webhook_manager.get_subscriptions(event_type=event_type)

            if not subscriptions:
                return {
                    'success': True,
                    'message': f'No subscriptions for event type: {event_type}',
                    'event_payload': asdict(payload)
                }

            # Trigger webhooks
            results = await self.trigger_webhook(event_type, asdict(payload))

            return {
                'success': True,
                'message': f'Event {event_type} triggered successfully',
                'subscriptions_triggered': len(subscriptions),
                'results': results,
                'event_payload': asdict(payload)
            }

        except Exception as e:
            logger.error(f"Error triggering event {event_type}: {e}")
            return {
                'success': False,
                'error': str(e),
                'event_type': event_type
            }

    async def trigger_bulk_events(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Trigger multiple events in batch"""
        results = []

        for event_data in events:
            event_type = event_data.get('event_type')
            data = event_data.get('data', {})
            source = event_data.get('source', 'valido_ai')
            metadata = event_data.get('metadata')

            result = await self.trigger_event(event_type, data, source, metadata)
            results.append(result)

        # Count successes and failures
        successful = sum(1 for r in results if r['success'])
        failed = len(results) - successful

        return {
            'success': failed == 0,
            'total_events': len(events),
            'successful': successful,
            'failed': failed,
            'results': results
        }

    async def trigger_conditional_event(self, event_type: str, data: Dict[str, Any],
                                      condition_func: callable) -> Dict[str, Any]:
        """Trigger event only if condition is met"""
        try:
            if condition_func(data):
                return await self.trigger_event(event_type, data)
            else:
                return {
                    'success': True,
                    'message': f'Event {event_type} not triggered - condition not met',
                    'condition_not_met': True
                }
        except Exception as e:
            return {
                'success': False,
                'error': f'Error in conditional trigger: {e}'
            }

    def _generate_signature(self, payload: str, secret: str) -> str:
        """Generate HMAC signature for webhook payload"""
        return hmac.new(
            secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

    def _prepare_headers(self, subscription: WebhookSubscription, payload: str) -> Dict[str, str]:
        """Prepare headers for webhook request"""
        headers = subscription.headers.copy() if subscription.headers else {}

        # Add content type if not specified
        if 'Content-Type' not in headers:
            headers['Content-Type'] = 'application/json'

        # Add signature if secret is provided
        if subscription.secret:
            signature = self._generate_signature(payload, subscription.secret)
            headers['X-Hub-Signature-256'] = f'sha256={signature}'
            headers['X-Webhook-Signature'] = signature

        # Add timestamp
        headers['X-Webhook-Timestamp'] = str(int(time.time()))

        return headers

    async def trigger_webhook(self, event_type: str, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Trigger webhooks for a specific event type"""
        await self.initialize()

        subscriptions = webhook_manager.get_subscriptions(event_type=event_type)
        results = []

        for subscription in subscriptions:
            try:
                result = await self._send_webhook(subscription, event_type, payload)
                results.append(result)
            except Exception as e:
                logger.error(f"Error triggering webhook {subscription.id}: {e}")
                results.append({
                    'subscription_id': subscription.id,
                    'success': False,
                    'error': str(e)
                })

        return results

    async def _send_webhook(self, subscription: WebhookSubscription, event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Send webhook to a specific subscription"""
        payload_str = json.dumps(payload)
        headers = self._prepare_headers(subscription, payload_str)

        webhook_event = WebhookEvent(
            subscription_id=subscription.id,
            event_type=event_type,
            payload=payload
        )

        try:
            # Create timeout
            timeout = aiohttp.ClientTimeout(total=subscription.timeout)

            # Send request
            async with self.session.request(
                method=subscription.method,
                url=subscription.url,
                data=payload_str,
                headers=headers,
                timeout=timeout
            ) as response:
                response_text = await response.text()
                webhook_event.status = 'sent'
                webhook_event.response_code = response.status
                webhook_event.response_body = response_text
                webhook_event.sent_at = datetime.now()

                success = response.status < 400
                if success:
                    webhook_event.status = 'success'
                else:
                    webhook_event.status = 'failed'
                    webhook_event.error_message = f"HTTP {response.status}: {response_text}"

        except asyncio.TimeoutError:
            webhook_event.status = 'failed'
            webhook_event.error_message = f"Timeout after {subscription.timeout} seconds"
        except Exception as e:
            webhook_event.status = 'failed'
            webhook_event.error_message = str(e)

        # Log the event
        event_id = webhook_manager.log_event(webhook_event)

        # Update subscription statistics
        webhook_manager.update_subscription_stats(subscription.id, success=webhook_event.status == 'success')

        # Handle retries if failed
        if webhook_event.status == 'failed' and webhook_event.retry_count < subscription.retry_count:
            await self._retry_webhook(subscription, webhook_event)

        return {
            'subscription_id': subscription.id,
            'event_id': event_id,
            'success': webhook_event.status == 'success',
            'status_code': webhook_event.response_code,
            'error': webhook_event.error_message
        }

    async def _retry_webhook(self, subscription: WebhookSubscription, original_event: WebhookEvent):
        """Retry failed webhook"""
        for attempt in range(1, subscription.retry_count - original_event.retry_count + 1):
            logger.info(f"Retrying webhook {subscription.id} (attempt {attempt})")

            retry_event = WebhookEvent(
                subscription_id=subscription.id,
                event_type=original_event.event_type,
                payload=original_event.payload,
                retry_count=attempt
            )

            try:
                payload_str = json.dumps(original_event.payload)
                headers = self._prepare_headers(subscription, payload_str)
                timeout = aiohttp.ClientTimeout(total=subscription.timeout)

                async with self.session.request(
                    method=subscription.method,
                    url=subscription.url,
                    data=payload_str,
                    headers=headers,
                    timeout=timeout
                ) as response:
                    response_text = await response.text()
                    retry_event.status = 'success' if response.status < 400 else 'failed'
                    retry_event.response_code = response.status
                    retry_event.response_body = response_text
                    retry_event.sent_at = datetime.now()

                    if retry_event.status == 'success':
                        webhook_manager.update_subscription_stats(subscription.id, success=True)
                        break

            except Exception as e:
                retry_event.status = 'failed'
                retry_event.error_message = str(e)

            # Log retry event
            webhook_manager.log_event(retry_event)

            # Wait before next retry (exponential backoff)
            await asyncio.sleep(2 ** attempt)


class APIIntegrationService:
    """Service for managing API integrations (banks, government, SOAP, etc.)"""

    def __init__(self):
        self.session = None

    async def initialize(self):
        """Initialize HTTP session"""
        if not self.session:
            self.session = aiohttp.ClientSession()

    async def close(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
            self.session = None

    def _prepare_auth_headers(self, integration: APIIntegration) -> Dict[str, str]:
        """Prepare authentication headers"""
        headers = integration.headers.copy() if integration.headers else {}

        if integration.auth_type == 'basic' and 'username' in integration.auth_config:
            import base64
            credentials = f"{integration.auth_config['username']}:{integration.auth_config.get('password', '')}"
            headers['Authorization'] = f"Basic {base64.b64encode(credentials.encode()).decode()}"

        elif integration.auth_type == 'bearer' and 'token' in integration.auth_config:
            headers['Authorization'] = f"Bearer {integration.auth_config['token']}"

        elif integration.auth_type == 'api_key' and 'api_key' in integration.auth_config:
            key_name = integration.auth_config.get('key_name', 'X-API-Key')
            headers[key_name] = integration.auth_config['api_key']

        return headers

    async def call_api(self, integration_id: int, endpoint: str, method: str = 'GET',
                      data: Dict[str, Any] = None, headers: Dict[str, str] = None) -> Dict[str, Any]:
        """Call an API integration"""
        await self.initialize()

        integration = self._get_integration_by_id(integration_id)
        if not integration:
            return {'success': False, 'error': 'Integration not found'}

        try:
            # Prepare URL
            url = urljoin(integration.base_url, endpoint)

            # Prepare headers
            request_headers = self._prepare_auth_headers(integration)
            if headers:
                request_headers.update(headers)

            # Prepare data
            request_data = None
            if data:
                if integration.provider_type == 'soap':
                    request_data = self._prepare_soap_request(data)
                    request_headers['Content-Type'] = 'text/xml'
                else:
                    request_data = json.dumps(data)
                    request_headers['Content-Type'] = 'application/json'

            # Make request
            timeout = aiohttp.ClientTimeout(total=integration.timeout)

            async with self.session.request(
                method=method,
                url=url,
                data=request_data,
                headers=request_headers,
                timeout=timeout
            ) as response:
                response_text = await response.text()

                # Handle SOAP response
                if integration.provider_type == 'soap':
                    result = self._parse_soap_response(response_text)
                else:
                    result = json.loads(response_text) if response_text else {}

                success = response.status < 400
                api_integration_manager.update_integration_stats(integration_id, success=success)

                return {
                    'success': success,
                    'status_code': response.status,
                    'data': result,
                    'headers': dict(response.headers),
                    'integration': {
                        'id': integration.id,
                        'name': integration.name,
                        'provider_type': integration.provider_type
                    }
                }

        except Exception as e:
            logger.error(f"Error calling API integration {integration_id}: {e}")
            api_integration_manager.update_integration_stats(integration_id, success=False)
            return {'success': False, 'error': str(e)}

    def _get_integration_by_id(self, integration_id: int) -> Optional[APIIntegration]:
        """Get API integration by ID"""
        integrations = api_integration_manager.get_integrations(active_only=False)
        for integration in integrations:
            if integration.id == integration_id:
                return integration
        return None

    def _prepare_soap_request(self, data: Dict[str, Any]) -> str:
        """Prepare SOAP request XML"""
        # This is a basic SOAP wrapper - you might need to customize based on specific SOAP services
        soap_body = ""
        for key, value in data.items():
            soap_body += f"<{key}>{value}</{key}>"

        soap_request = f"""<?xml version="1.0" encoding="utf-8"?>
        <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
            <soap:Body>
                <Request>
                    {soap_body}
                </Request>
            </soap:Body>
        </soap:Envelope>"""

        return soap_request

    def _parse_soap_response(self, response_text: str) -> Dict[str, Any]:
        """Parse SOAP response XML"""
        # This is a basic SOAP response parser - you might need to customize based on specific SOAP services
        try:
            # Simple XML parsing - for production, consider using xml.etree.ElementTree or lxml
            import xml.etree.ElementTree as ET
            root = ET.fromstring(response_text)

            # Extract response data (customize based on SOAP service response format)
            response_data = {}
            for elem in root.iter():
                if elem.tag.endswith('Response') or elem.tag.endswith('Result'):
                    for child in elem:
                        if child.text and child.text.strip():
                            response_data[child.tag.split('}')[-1]] = child.text.strip()

            return response_data
        except Exception as e:
            logger.error(f"Error parsing SOAP response: {e}")
            return {'raw_response': response_text}

    async def test_integration(self, integration_id: int) -> Dict[str, Any]:
        """Test an API integration"""
        integration = self._get_integration_by_id(integration_id)
        if not integration:
            return {'success': False, 'error': 'Integration not found'}

        # Test with a simple GET request to the base URL
        try:
            await self.initialize()
            timeout = aiohttp.ClientTimeout(total=10)  # Shorter timeout for testing

            headers = self._prepare_auth_headers(integration)

            async with self.session.get(
                integration.base_url,
                headers=headers,
                timeout=timeout
            ) as response:
                return {
                    'success': response.status < 400,
                    'status_code': response.status,
                    'response_time': response.elapsed.total_seconds() if hasattr(response, 'elapsed') else 0,
                    'headers': dict(response.headers),
                    'integration': {
                        'id': integration.id,
                        'name': integration.name,
                        'provider_type': integration.provider_type
                    }
                }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'integration': {
                    'id': integration.id,
                    'name': integration.name,
                    'provider_type': integration.provider_type
                }
            }


# Global service instances
webhook_service = WebhookService()
api_integration_service = APIIntegrationService()


async def initialize_services():
    """Initialize all webhook and API integration services"""
    await webhook_service.initialize()
    await api_integration_service.initialize()


async def close_services():
    """Close all webhook and API integration services"""
    await webhook_service.close()
    await api_integration_service.close()
