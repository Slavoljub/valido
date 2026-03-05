"""
Webhook Controller - Handles webhook and API integration management with comprehensive event support
"""
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

from src.models.webhook_models import (
    WebhookSubscription,
    WebhookEvent,
    APIIntegration,
    webhook_manager,
    api_integration_manager
)
from src.services.webhook_service import (
    webhook_service,
    api_integration_service,
    StandardEventTypes,
    WebhookEventPayload
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WebhookController:
    """Controller for webhook management operations"""

    @staticmethod
    def get_webhooks() -> Dict[str, Any]:
        """Get all webhooks"""
        try:
            webhooks = webhook_manager.get_subscriptions()
            return {
                'success': True,
                'data': [
                    {
                        'id': w.id,
                        'name': w.name,
                        'event_type': w.event_type,
                        'url': w.url,
                        'method': w.method,
                        'headers': w.headers,
                        'secret': w.secret,
                        'is_active': w.is_active,
                        'retry_count': w.retry_count,
                        'timeout': w.timeout,
                        'created_at': w.created_at.isoformat() if w.created_at else None,
                        'updated_at': w.updated_at.isoformat() if w.updated_at else None,
                        'last_triggered': w.last_triggered.isoformat() if w.last_triggered else None,
                        'trigger_count': w.trigger_count,
                        'success_count': w.success_count,
                        'failure_count': w.failure_count
                    } for w in webhooks
                ],
                'total': len(webhooks)
            }
        except Exception as e:
            logger.error(f"Error getting webhooks: {e}")
            return {'success': False, 'error': str(e)}

    @staticmethod
    def get_webhook(webhook_id: int) -> Dict[str, Any]:
        """Get a specific webhook"""
        try:
            webhooks = webhook_manager.get_subscriptions()
            webhook = next((w for w in webhooks if w.id == webhook_id), None)

            if not webhook:
                return {'success': False, 'error': 'Webhook not found'}

            return {
                'success': True,
                'data': {
                    'id': webhook.id,
                    'name': webhook.name,
                    'event_type': webhook.event_type,
                    'url': webhook.url,
                    'method': webhook.method,
                    'headers': webhook.headers,
                    'secret': webhook.secret,
                    'is_active': webhook.is_active,
                    'retry_count': webhook.retry_count,
                    'timeout': webhook.timeout,
                    'created_at': webhook.created_at.isoformat() if webhook.created_at else None,
                    'updated_at': webhook.updated_at.isoformat() if webhook.updated_at else None,
                    'last_triggered': webhook.last_triggered.isoformat() if webhook.last_triggered else None,
                    'trigger_count': webhook.trigger_count,
                    'success_count': webhook.success_count,
                    'failure_count': webhook.failure_count
                }
            }
        except Exception as e:
            logger.error(f"Error getting webhook {webhook_id}: {e}")
            return {'success': False, 'error': str(e)}

    @staticmethod
    def create_webhook(data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new webhook"""
        try:
            # Validate required fields
            required_fields = ['name', 'event_type', 'url']
            for field in required_fields:
                if not data.get(field):
                    return {'success': False, 'error': f'Missing required field: {field}'}

            webhook = WebhookSubscription(
                name=data['name'],
                event_type=data['event_type'],
                url=data['url'],
                method=data.get('method', 'POST'),
                headers=data.get('headers', {}),
                secret=data.get('secret', ''),
                is_active=data.get('is_active', True),
                retry_count=data.get('retry_count', 3),
                timeout=data.get('timeout', 30)
            )

            webhook_id = webhook_manager.create_subscription(webhook)

            logger.info(f"Created webhook {webhook_id}: {webhook.name}")
            return {
                'success': True,
                'data': {'id': webhook_id},
                'message': 'Webhook created successfully'
            }
        except Exception as e:
            logger.error(f"Error creating webhook: {e}")
            return {'success': False, 'error': str(e)}

    @staticmethod
    def update_webhook(webhook_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a webhook"""
        try:
            # Get existing webhook
            webhooks = webhook_manager.get_subscriptions()
            existing_webhook = next((w for w in webhooks if w.id == webhook_id), None)

            if not existing_webhook:
                return {'success': False, 'error': 'Webhook not found'}

            # Update fields
            existing_webhook.name = data.get('name', existing_webhook.name)
            existing_webhook.event_type = data.get('event_type', existing_webhook.event_type)
            existing_webhook.url = data.get('url', existing_webhook.url)
            existing_webhook.method = data.get('method', existing_webhook.method)
            existing_webhook.headers = data.get('headers', existing_webhook.headers)
            existing_webhook.secret = data.get('secret', existing_webhook.secret)
            existing_webhook.is_active = data.get('is_active', existing_webhook.is_active)
            existing_webhook.retry_count = data.get('retry_count', existing_webhook.retry_count)
            existing_webhook.timeout = data.get('timeout', existing_webhook.timeout)

            success = webhook_manager.update_subscription(existing_webhook)

            if success:
                logger.info(f"Updated webhook {webhook_id}: {existing_webhook.name}")
                return {
                    'success': True,
                    'message': 'Webhook updated successfully'
                }
            else:
                return {'success': False, 'error': 'Failed to update webhook'}
        except Exception as e:
            logger.error(f"Error updating webhook {webhook_id}: {e}")
            return {'success': False, 'error': str(e)}

    @staticmethod
    def delete_webhook(webhook_id: int) -> Dict[str, Any]:
        """Delete a webhook"""
        try:
            success = webhook_manager.delete_subscription(webhook_id)

            if success:
                logger.info(f"Deleted webhook {webhook_id}")
                return {
                    'success': True,
                    'message': 'Webhook deleted successfully'
                }
            else:
                return {'success': False, 'error': 'Webhook not found'}
        except Exception as e:
            logger.error(f"Error deleting webhook {webhook_id}: {e}")
            return {'success': False, 'error': str(e)}

    @staticmethod
    def test_webhook(webhook_id: int) -> Dict[str, Any]:
        """Test a webhook by sending a test payload"""
        try:
            import asyncio

            # Get webhook details
            webhooks = webhook_manager.get_subscriptions()
            webhook = next((w for w in webhooks if w.id == webhook_id), None)

            if not webhook:
                return {'success': False, 'error': 'Webhook not found'}

            # Create test payload
            test_payload = {
                'event': 'test',
                'timestamp': datetime.now().isoformat(),
                'webhook_id': webhook_id,
                'webhook_name': webhook.name,
                'message': 'This is a test webhook from ValidoAI'
            }

            # Send webhook asynchronously
            async def send_test():
                return await webhook_service._send_webhook(webhook, 'test', test_payload)

            # Run the test
            result = asyncio.run(send_test())

            return {
                'success': True,
                'data': result,
                'message': 'Webhook test completed'
            }
        except Exception as e:
            logger.error(f"Error testing webhook {webhook_id}: {e}")
            return {'success': False, 'error': str(e)}

    @staticmethod
    def get_webhook_events(subscription_id: Optional[int] = None, limit: int = 50) -> Dict[str, Any]:
        """Get webhook events"""
        try:
            events = webhook_manager.get_events(subscription_id, limit)

            # Enrich events with subscription names
            webhooks = webhook_manager.get_subscriptions()
            webhook_map = {w.id: w.name for w in webhooks}

            enriched_events = []
            for event in events:
                enriched_event = {
                    'id': event.id,
                    'subscription_id': event.subscription_id,
                    'subscription_name': webhook_map.get(event.subscription_id, 'Unknown'),
                    'event_type': event.event_type,
                    'payload': event.payload,
                    'status': event.status,
                    'response_code': event.response_code,
                    'response_body': event.response_body,
                    'error_message': event.error_message,
                    'created_at': event.created_at.isoformat() if event.created_at else None,
                    'sent_at': event.sent_at.isoformat() if event.sent_at else None,
                    'retry_count': event.retry_count
                }
                enriched_events.append(enriched_event)

            return {
                'success': True,
                'data': enriched_events,
                'total': len(enriched_events)
            }
        except Exception as e:
            logger.error(f"Error getting webhook events: {e}")
            return {'success': False, 'error': str(e)}

    @staticmethod
    def get_webhook_event(event_id: int) -> Dict[str, Any]:
        """Get a specific webhook event"""
        try:
            events = webhook_manager.get_events()
            event = next((e for e in events if e.id == event_id), None)

            if not event:
                return {'success': False, 'error': 'Event not found'}

            # Get subscription name
            webhooks = webhook_manager.get_subscriptions()
            webhook_map = {w.id: w.name for w in webhooks}

            return {
                'success': True,
                'data': {
                    'id': event.id,
                    'subscription_id': event.subscription_id,
                    'subscription_name': webhook_map.get(event.subscription_id, 'Unknown'),
                    'event_type': event.event_type,
                    'payload': event.payload,
                    'status': event.status,
                    'response_code': event.response_code,
                    'response_body': event.response_body,
                    'error_message': event.error_message,
                    'created_at': event.created_at.isoformat() if event.created_at else None,
                    'sent_at': event.sent_at.isoformat() if event.sent_at else None,
                    'retry_count': event.retry_count
                }
            }
        except Exception as e:
            logger.error(f"Error getting webhook event {event_id}: {e}")
            return {'success': False, 'error': str(e)}

    @staticmethod
    def get_webhook_stats() -> Dict[str, Any]:
        """Get webhook statistics"""
        try:
            webhooks = webhook_manager.get_subscriptions()
            events = webhook_manager.get_events()

            total_webhooks = len(webhooks)
            active_webhooks = len([w for w in webhooks if w.is_active])
            total_events = len(events)
            successful_events = len([e for e in events if e.status == 'success'])
            failed_events = len([e for e in events if e.status == 'failed'])

            success_rate = (successful_events / total_events * 100) if total_events > 0 else 0

            return {
                'success': True,
                'data': {
                    'total_webhooks': total_webhooks,
                    'active_webhooks': active_webhooks,
                    'total_events': total_events,
                    'successful_events': successful_events,
                    'failed_events': failed_events,
                    'success_rate': round(success_rate, 2)
                }
            }
        except Exception as e:
            logger.error(f"Error getting webhook stats: {e}")
            return {'success': False, 'error': str(e)}

    @staticmethod
    def get_available_event_types() -> Dict[str, Any]:
        """Get all available event types organized by category"""
        try:
            return {
                'success': True,
                'data': {
                    'all_events': StandardEventTypes.ALL_EVENTS,
                    'categories': StandardEventTypes.EVENT_CATEGORIES,
                    'total_events': len(StandardEventTypes.ALL_EVENTS),
                    'total_categories': len(StandardEventTypes.EVENT_CATEGORIES)
                }
            }
        except Exception as e:
            logger.error(f"Error getting event types: {e}")
            return {'success': False, 'error': str(e)}

    @staticmethod
    def get_events_by_category(category: str) -> Dict[str, Any]:
        """Get event types for a specific category"""
        try:
            events = StandardEventTypes.EVENT_CATEGORIES.get(category, [])
            return {
                'success': True,
                'data': {
                    'category': category,
                    'events': events,
                    'count': len(events)
                }
            }
        except Exception as e:
            logger.error(f"Error getting events by category {category}: {e}")
            return {'success': False, 'error': str(e)}

    @staticmethod
    def validate_event_type(event_type: str) -> Dict[str, Any]:
        """Validate if an event type is supported"""
        try:
            is_valid = event_type in StandardEventTypes.ALL_EVENTS

            # Find which category it belongs to
            category = None
            for cat, events in StandardEventTypes.EVENT_CATEGORIES.items():
                if event_type in events:
                    category = cat
                    break

            return {
                'success': True,
                'data': {
                    'event_type': event_type,
                    'is_valid': is_valid,
                    'category': category,
                    'available_types': StandardEventTypes.ALL_EVENTS if not is_valid else []
                }
            }
        except Exception as e:
            logger.error(f"Error validating event type {event_type}: {e}")
            return {'success': False, 'error': str(e)}

    @staticmethod
    def trigger_standard_event(event_type: str, data: Dict[str, Any],
                              source: str = "valido_ai", metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Trigger a standard event using the webhook service"""
        try:
            import asyncio

            async def trigger():
                return await webhook_service.trigger_event(event_type, data, source, metadata)

            result = asyncio.run(trigger())
            return result
        except Exception as e:
            logger.error(f"Error triggering standard event {event_type}: {e}")
            return {'success': False, 'error': str(e)}

    @staticmethod
    def trigger_bulk_events(events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Trigger multiple events in batch"""
        try:
            import asyncio

            async def trigger():
                return await webhook_service.trigger_bulk_events(events)

            result = asyncio.run(trigger())
            return result
        except Exception as e:
            logger.error(f"Error triggering bulk events: {e}")
            return {'success': False, 'error': str(e)}

    @staticmethod
    def get_event_logs_by_type(event_type: str, limit: int = 50) -> Dict[str, Any]:
        """Get event logs filtered by event type"""
        try:
            events = webhook_manager.get_events()
            filtered_events = [e for e in events if e.event_type == event_type]

            # Sort by creation date, most recent first
            filtered_events.sort(key=lambda x: x.created_at or datetime.min, reverse=True)

            # Limit results
            filtered_events = filtered_events[:limit]

            return {
                'success': True,
                'data': [
                    {
                        'id': event.id,
                        'subscription_id': event.subscription_id,
                        'event_type': event.event_type,
                        'payload': event.payload,
                        'status': event.status,
                        'response_code': event.response_code,
                        'response_body': event.response_body,
                        'error_message': event.error_message,
                        'created_at': event.created_at.isoformat() if event.created_at else None,
                        'sent_at': event.sent_at.isoformat() if event.sent_at else None,
                        'retry_count': event.retry_count
                    } for event in filtered_events
                ],
                'total': len(filtered_events)
            }
        except Exception as e:
            logger.error(f"Error getting event logs by type {event_type}: {e}")
            return {'success': False, 'error': str(e)}

    @staticmethod
    def get_webhook_health_status() -> Dict[str, Any]:
        """Get overall webhook system health status"""
        try:
            webhooks = webhook_manager.get_subscriptions()
            events = webhook_manager.get_events()

            # Calculate health metrics
            total_webhooks = len(webhooks)
            active_webhooks = len([w for w in webhooks if w.is_active])

            # Recent events (last 24 hours)
            recent_events = [e for e in events if e.created_at and
                           (datetime.now() - e.created_at).total_seconds() < 86400]

            successful_recent = len([e for e in recent_events if e.status == 'success'])
            failed_recent = len([e for e in recent_events if e.status == 'failed'])

            # Overall success rate
            total_events = len(events)
            successful_events = len([e for e in events if e.status == 'success'])
            overall_success_rate = (successful_events / total_events * 100) if total_events > 0 else 100

            # Health status based on metrics
            if overall_success_rate >= 95 and failed_recent == 0:
                health_status = "excellent"
            elif overall_success_rate >= 90:
                health_status = "good"
            elif overall_success_rate >= 75:
                health_status = "warning"
            else:
                health_status = "critical"

            return {
                'success': True,
                'data': {
                    'health_status': health_status,
                    'overall_success_rate': round(overall_success_rate, 2),
                    'total_webhooks': total_webhooks,
                    'active_webhooks': active_webhooks,
                    'total_events_24h': len(recent_events),
                    'successful_events_24h': successful_recent,
                    'failed_events_24h': failed_recent,
                    'last_updated': datetime.now().isoformat()
                }
            }
        except Exception as e:
            logger.error(f"Error getting webhook health status: {e}")
            return {
                'success': False,
                'error': str(e),
                'health_status': 'error'
            }

    @staticmethod
    def trigger_webhook_event(event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Trigger a webhook event (for internal use)"""
        try:
            import asyncio

            # Trigger webhooks asynchronously
            async def trigger():
                return await webhook_service.trigger_webhook(event_type, payload)

            results = asyncio.run(trigger())

            return {
                'success': True,
                'data': results,
                'message': f'Triggered {len(results)} webhooks for event: {event_type}'
            }
        except Exception as e:
            logger.error(f"Error triggering webhook event {event_type}: {e}")
            return {'success': False, 'error': str(e)}


class APIIntegrationController:
    """Controller for API integration management operations"""

    @staticmethod
    def get_integrations() -> Dict[str, Any]:
        """Get all API integrations"""
        try:
            integrations = api_integration_manager.get_integrations()
            return {
                'success': True,
                'data': [
                    {
                        'id': i.id,
                        'name': i.name,
                        'provider_type': i.provider_type,
                        'base_url': i.base_url,
                        'auth_type': i.auth_type,
                        'auth_config': i.auth_config,
                        'headers': i.headers,
                        'timeout': i.timeout,
                        'retry_count': i.retry_count,
                        'is_active': i.is_active,
                        'description': i.description,
                        'created_at': i.created_at.isoformat() if i.created_at else None,
                        'updated_at': i.updated_at.isoformat() if i.updated_at else None,
                        'last_used': i.last_used.isoformat() if i.last_used else None,
                        'usage_count': i.usage_count,
                        'success_count': i.success_count,
                        'failure_count': i.failure_count
                    } for i in integrations
                ],
                'total': len(integrations)
            }
        except Exception as e:
            logger.error(f"Error getting API integrations: {e}")
            return {'success': False, 'error': str(e)}

    @staticmethod
    def get_integration(integration_id: int) -> Dict[str, Any]:
        """Get a specific API integration"""
        try:
            integrations = api_integration_manager.get_integrations()
            integration = next((i for i in integrations if i.id == integration_id), None)

            if not integration:
                return {'success': False, 'error': 'API integration not found'}

            return {
                'success': True,
                'data': {
                    'id': integration.id,
                    'name': integration.name,
                    'provider_type': integration.provider_type,
                    'base_url': integration.base_url,
                    'auth_type': integration.auth_type,
                    'auth_config': integration.auth_config,
                    'headers': integration.headers,
                    'timeout': integration.timeout,
                    'retry_count': integration.retry_count,
                    'is_active': integration.is_active,
                    'description': integration.description,
                    'created_at': integration.created_at.isoformat() if integration.created_at else None,
                    'updated_at': integration.updated_at.isoformat() if integration.updated_at else None,
                    'last_used': integration.last_used.isoformat() if integration.last_used else None,
                    'usage_count': integration.usage_count,
                    'success_count': integration.success_count,
                    'failure_count': integration.failure_count
                }
            }
        except Exception as e:
            logger.error(f"Error getting API integration {integration_id}: {e}")
            return {'success': False, 'error': str(e)}

    @staticmethod
    def create_integration(data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new API integration"""
        try:
            # Validate required fields
            required_fields = ['name', 'provider_type', 'base_url']
            for field in required_fields:
                if not data.get(field):
                    return {'success': False, 'error': f'Missing required field: {field}'}

            integration = APIIntegration(
                name=data['name'],
                provider_type=data['provider_type'],
                base_url=data['base_url'],
                auth_type=data.get('auth_type', 'none'),
                auth_config=data.get('auth_config', {}),
                headers=data.get('headers', {}),
                timeout=data.get('timeout', 30),
                retry_count=data.get('retry_count', 3),
                is_active=data.get('is_active', True),
                description=data.get('description', '')
            )

            integration_id = api_integration_manager.create_integration(integration)

            logger.info(f"Created API integration {integration_id}: {integration.name}")
            return {
                'success': True,
                'data': {'id': integration_id},
                'message': 'API integration created successfully'
            }
        except Exception as e:
            logger.error(f"Error creating API integration: {e}")
            return {'success': False, 'error': str(e)}

    @staticmethod
    def update_integration(integration_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an API integration"""
        try:
            # Get existing integration
            integrations = api_integration_manager.get_integrations()
            existing_integration = next((i for i in integrations if i.id == integration_id), None)

            if not existing_integration:
                return {'success': False, 'error': 'API integration not found'}

            # Update fields
            existing_integration.name = data.get('name', existing_integration.name)
            existing_integration.provider_type = data.get('provider_type', existing_integration.provider_type)
            existing_integration.base_url = data.get('base_url', existing_integration.base_url)
            existing_integration.auth_type = data.get('auth_type', existing_integration.auth_type)
            existing_integration.auth_config = data.get('auth_config', existing_integration.auth_config)
            existing_integration.headers = data.get('headers', existing_integration.headers)
            existing_integration.timeout = data.get('timeout', existing_integration.timeout)
            existing_integration.retry_count = data.get('retry_count', existing_integration.retry_count)
            existing_integration.is_active = data.get('is_active', existing_integration.is_active)
            existing_integration.description = data.get('description', existing_integration.description)

            success = api_integration_manager.update_integration(existing_integration)

            if success:
                logger.info(f"Updated API integration {integration_id}: {existing_integration.name}")
                return {
                    'success': True,
                    'message': 'API integration updated successfully'
                }
            else:
                return {'success': False, 'error': 'Failed to update API integration'}
        except Exception as e:
            logger.error(f"Error updating API integration {integration_id}: {e}")
            return {'success': False, 'error': str(e)}

    @staticmethod
    def delete_integration(integration_id: int) -> Dict[str, Any]:
        """Delete an API integration"""
        try:
            success = api_integration_manager.delete_integration(integration_id)

            if success:
                logger.info(f"Deleted API integration {integration_id}")
                return {
                    'success': True,
                    'message': 'API integration deleted successfully'
                }
            else:
                return {'success': False, 'error': 'API integration not found'}
        except Exception as e:
            logger.error(f"Error deleting API integration {integration_id}: {e}")
            return {'success': False, 'error': str(e)}

    @staticmethod
    def test_integration(integration_id: int) -> Dict[str, Any]:
        """Test an API integration"""
        try:
            import asyncio

            # Test the integration
            result = asyncio.run(api_integration_service.test_integration(integration_id))

            return result
        except Exception as e:
            logger.error(f"Error testing API integration {integration_id}: {e}")
            return {'success': False, 'error': str(e)}

    @staticmethod
    def call_integration(integration_id: int, endpoint: str, method: str = 'GET',
                        data: Optional[Dict[str, Any]] = None,
                        headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Call an API integration endpoint"""
        try:
            import asyncio

            # Call the integration
            result = asyncio.run(api_integration_service.call_api(
                integration_id, endpoint, method, data, headers
            ))

            return result
        except Exception as e:
            logger.error(f"Error calling API integration {integration_id}: {e}")
            return {'success': False, 'error': str(e)}


# Global controller instances
webhook_controller = WebhookController()
api_integration_controller = APIIntegrationController()
