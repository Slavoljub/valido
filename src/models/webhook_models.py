"""
Webhook Models and Database Operations
"""
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class WebhookSubscription:
    """Webhook subscription data model"""
    id: Optional[int] = None
    name: str = ""
    url: str = ""
    event_type: str = ""
    method: str = "POST"
    headers: Dict[str, str] = None
    secret: str = ""
    is_active: bool = True
    retry_count: int = 3
    timeout: int = 30
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_triggered: Optional[datetime] = None
    trigger_count: int = 0
    success_count: int = 0
    failure_count: int = 0

    def __post_init__(self):
        if self.headers is None:
            self.headers = {}
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()


@dataclass
class WebhookEvent:
    """Webhook event data model"""
    id: Optional[int] = None
    subscription_id: int = 0
    event_type: str = ""
    payload: Dict[str, Any] = None
    status: str = "pending"  # pending, sent, failed, retry
    response_code: Optional[int] = None
    response_body: Optional[str] = None
    error_message: Optional[str] = None
    created_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    retry_count: int = 0

    def __post_init__(self):
        if self.payload is None:
            self.payload = {}
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class APIIntegration:
    """API integration data model for banks, government services, etc."""
    id: Optional[int] = None
    name: str = ""
    provider_type: str = ""  # bank, government, soap, rest
    base_url: str = ""
    auth_type: str = "none"  # none, basic, bearer, oauth2, api_key, certificate
    auth_config: Dict[str, Any] = None
    headers: Dict[str, str] = None
    timeout: int = 30
    retry_count: int = 3
    is_active: bool = True
    description: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_used: Optional[datetime] = None
    usage_count: int = 0
    success_count: int = 0
    failure_count: int = 0

    def __post_init__(self):
        if self.auth_config is None:
            self.auth_config = {}
        if self.headers is None:
            self.headers = {}
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()


class WebhookManager:
    """Database operations for webhooks"""

    def __init__(self, db_path: str = "data/sqlite/app.db"):
        self.db_path = db_path
        self._init_database()

    def _init_database(self):
        """Initialize database tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Create webhook_subscriptions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS webhook_subscriptions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    url TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    method TEXT DEFAULT 'POST',
                    headers TEXT,
                    secret TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    retry_count INTEGER DEFAULT 3,
                    timeout INTEGER DEFAULT 30,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_triggered TIMESTAMP,
                    trigger_count INTEGER DEFAULT 0,
                    success_count INTEGER DEFAULT 0,
                    failure_count INTEGER DEFAULT 0
                )
            """)

            # Create webhook_events table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS webhook_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    subscription_id INTEGER,
                    event_type TEXT NOT NULL,
                    payload TEXT,
                    status TEXT DEFAULT 'pending',
                    response_code INTEGER,
                    response_body TEXT,
                    error_message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    sent_at TIMESTAMP,
                    retry_count INTEGER DEFAULT 0,
                    FOREIGN KEY (subscription_id) REFERENCES webhook_subscriptions (id)
                )
            """)

            # Create api_integrations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS api_integrations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    provider_type TEXT NOT NULL,
                    base_url TEXT NOT NULL,
                    auth_type TEXT DEFAULT 'none',
                    auth_config TEXT,
                    headers TEXT,
                    timeout INTEGER DEFAULT 30,
                    retry_count INTEGER DEFAULT 3,
                    is_active BOOLEAN DEFAULT 1,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_used TIMESTAMP,
                    usage_count INTEGER DEFAULT 0,
                    success_count INTEGER DEFAULT 0,
                    failure_count INTEGER DEFAULT 0
                )
            """)

            conn.commit()

    def create_subscription(self, subscription: WebhookSubscription) -> int:
        """Create a new webhook subscription"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO webhook_subscriptions
                (name, url, event_type, method, headers, secret, is_active, retry_count, timeout)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                subscription.name,
                subscription.url,
                subscription.event_type,
                subscription.method,
                json.dumps(subscription.headers) if subscription.headers else '{}',
                subscription.secret,
                subscription.is_active,
                subscription.retry_count,
                subscription.timeout
            ))
            conn.commit()
            return cursor.lastrowid

    def get_subscriptions(self, event_type: str = None, active_only: bool = True) -> List[WebhookSubscription]:
        """Get webhook subscriptions"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM webhook_subscriptions"
            params = []

            if event_type or active_only:
                conditions = []
                if event_type:
                    conditions.append("event_type = ?")
                    params.append(event_type)
                if active_only:
                    conditions.append("is_active = 1")
                query += " WHERE " + " AND ".join(conditions)

            cursor.execute(query, params)
            rows = cursor.fetchall()

            subscriptions = []
            for row in rows:
                headers = json.loads(row[5]) if row[5] else {}
                subscription = WebhookSubscription(
                    id=row[0],
                    name=row[1],
                    url=row[2],
                    event_type=row[3],
                    method=row[4],
                    headers=headers,
                    secret=row[6],
                    is_active=bool(row[7]),
                    retry_count=row[8],
                    timeout=row[9],
                    created_at=datetime.fromisoformat(row[10]) if row[10] else None,
                    updated_at=datetime.fromisoformat(row[11]) if row[11] else None,
                    last_triggered=datetime.fromisoformat(row[12]) if row[12] else None,
                    trigger_count=row[13],
                    success_count=row[14],
                    failure_count=row[15]
                )
                subscriptions.append(subscription)

            return subscriptions

    def update_subscription(self, subscription: WebhookSubscription) -> bool:
        """Update a webhook subscription"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE webhook_subscriptions SET
                name = ?, url = ?, event_type = ?, method = ?, headers = ?,
                secret = ?, is_active = ?, retry_count = ?, timeout = ?, updated_at = ?
                WHERE id = ?
            """, (
                subscription.name,
                subscription.url,
                subscription.event_type,
                subscription.method,
                json.dumps(subscription.headers) if subscription.headers else '{}',
                subscription.secret,
                subscription.is_active,
                subscription.retry_count,
                subscription.timeout,
                datetime.now().isoformat(),
                subscription.id
            ))
            conn.commit()
            return cursor.rowcount > 0

    def delete_subscription(self, subscription_id: int) -> bool:
        """Delete a webhook subscription"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM webhook_subscriptions WHERE id = ?", (subscription_id,))
            conn.commit()
            return cursor.rowcount > 0

    def log_event(self, event: WebhookEvent) -> int:
        """Log a webhook event"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO webhook_events
                (subscription_id, event_type, payload, status, response_code,
                 response_body, error_message, sent_at, retry_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                event.subscription_id,
                event.event_type,
                json.dumps(event.payload) if event.payload else '{}',
                event.status,
                event.response_code,
                event.response_body,
                event.error_message,
                event.sent_at.isoformat() if event.sent_at else None,
                event.retry_count
            ))
            conn.commit()
            return cursor.lastrowid

    def get_events(self, subscription_id: int = None, limit: int = 50) -> List[WebhookEvent]:
        """Get webhook events"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM webhook_events"
            params = []

            if subscription_id:
                query += " WHERE subscription_id = ?"
                params.append(subscription_id)

            query += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)

            cursor.execute(query, params)
            rows = cursor.fetchall()

            events = []
            for row in rows:
                payload = json.loads(row[3]) if row[3] else {}
                event = WebhookEvent(
                    id=row[0],
                    subscription_id=row[1],
                    event_type=row[2],
                    payload=payload,
                    status=row[4],
                    response_code=row[5],
                    response_body=row[6],
                    error_message=row[7],
                    created_at=datetime.fromisoformat(row[8]) if row[8] else None,
                    sent_at=datetime.fromisoformat(row[9]) if row[9] else None,
                    retry_count=row[10]
                )
                events.append(event)

            return events

    def update_subscription_stats(self, subscription_id: int, success: bool = True):
        """Update subscription statistics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            if success:
                cursor.execute("""
                    UPDATE webhook_subscriptions SET
                    success_count = success_count + 1,
                    trigger_count = trigger_count + 1,
                    last_triggered = ?
                    WHERE id = ?
                """, (datetime.now().isoformat(), subscription_id))
            else:
                cursor.execute("""
                    UPDATE webhook_subscriptions SET
                    failure_count = failure_count + 1,
                    trigger_count = trigger_count + 1,
                    last_triggered = ?
                    WHERE id = ?
                """, (datetime.now().isoformat(), subscription_id))
            conn.commit()


class APIIntegrationManager:
    """Database operations for API integrations"""

    def __init__(self, db_path: str = "data/sqlite/app.db"):
        self.db_path = db_path
        # Database initialization is handled by WebhookManager

    def _init_database(self):
        """Initialize database tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Create api_integrations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS api_integrations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    provider_type TEXT NOT NULL,
                    base_url TEXT NOT NULL,
                    auth_type TEXT DEFAULT 'none',
                    auth_config TEXT,
                    headers TEXT,
                    timeout INTEGER DEFAULT 30,
                    retry_count INTEGER DEFAULT 3,
                    is_active BOOLEAN DEFAULT 1,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_used TIMESTAMP,
                    usage_count INTEGER DEFAULT 0,
                    success_count INTEGER DEFAULT 0,
                    failure_count INTEGER DEFAULT 0
                )
            """)

            conn.commit()

    def create_integration(self, integration: APIIntegration) -> int:
        """Create a new API integration"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO api_integrations
                (name, provider_type, base_url, auth_type, auth_config, headers,
                 timeout, retry_count, is_active, description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                integration.name,
                integration.provider_type,
                integration.base_url,
                integration.auth_type,
                json.dumps(integration.auth_config) if integration.auth_config else '{}',
                json.dumps(integration.headers) if integration.headers else '{}',
                integration.timeout,
                integration.retry_count,
                integration.is_active,
                integration.description
            ))
            conn.commit()
            return cursor.lastrowid

    def get_integrations(self, provider_type: str = None, active_only: bool = True) -> List[APIIntegration]:
        """Get API integrations"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM api_integrations"
            params = []

            if provider_type or active_only:
                conditions = []
                if provider_type:
                    conditions.append("provider_type = ?")
                    params.append(provider_type)
                if active_only:
                    conditions.append("is_active = 1")
                query += " WHERE " + " AND ".join(conditions)

            cursor.execute(query, params)
            rows = cursor.fetchall()

            integrations = []
            for row in rows:
                auth_config = json.loads(row[5]) if row[5] else {}
                headers = json.loads(row[6]) if row[6] else {}
                integration = APIIntegration(
                    id=row[0],
                    name=row[1],
                    provider_type=row[2],
                    base_url=row[3],
                    auth_type=row[4],
                    auth_config=auth_config,
                    headers=headers,
                    timeout=row[7],
                    retry_count=row[8],
                    is_active=bool(row[9]),
                    description=row[10],
                    created_at=datetime.fromisoformat(row[11]) if row[11] else None,
                    updated_at=datetime.fromisoformat(row[12]) if row[12] else None,
                    last_used=datetime.fromisoformat(row[13]) if row[13] else None,
                    usage_count=row[14],
                    success_count=row[15],
                    failure_count=row[16]
                )
                integrations.append(integration)

            return integrations

    def update_integration(self, integration: APIIntegration) -> bool:
        """Update an API integration"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE api_integrations SET
                name = ?, provider_type = ?, base_url = ?, auth_type = ?,
                auth_config = ?, headers = ?, timeout = ?, retry_count = ?,
                is_active = ?, description = ?, updated_at = ?
                WHERE id = ?
            """, (
                integration.name,
                integration.provider_type,
                integration.base_url,
                integration.auth_type,
                json.dumps(integration.auth_config) if integration.auth_config else '{}',
                json.dumps(integration.headers) if integration.headers else '{}',
                integration.timeout,
                integration.retry_count,
                integration.is_active,
                integration.description,
                datetime.now().isoformat(),
                integration.id
            ))
            conn.commit()
            return cursor.rowcount > 0

    def delete_integration(self, integration_id: int) -> bool:
        """Delete an API integration"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM api_integrations WHERE id = ?", (integration_id,))
            conn.commit()
            return cursor.rowcount > 0

    def update_integration_stats(self, integration_id: int, success: bool = True):
        """Update integration statistics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            if success:
                cursor.execute("""
                    UPDATE api_integrations SET
                    success_count = success_count + 1,
                    usage_count = usage_count + 1,
                    last_used = ?
                    WHERE id = ?
                """, (datetime.now().isoformat(), integration_id))
            else:
                cursor.execute("""
                    UPDATE api_integrations SET
                    failure_count = failure_count + 1,
                    usage_count = usage_count + 1,
                    last_used = ?
                    WHERE id = ?
                """, (datetime.now().isoformat(), integration_id))
            conn.commit()


# Global instances
webhook_manager = WebhookManager()
api_integration_manager = APIIntegrationManager()
