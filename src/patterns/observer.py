"""
Observer Pattern Implementation for Database Events
Provides event-driven architecture for database operations
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Callable
from enum import Enum
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class EventType(Enum):
    """Database event types"""
    INSERT = "insert"
    UPDATE = "update"
    DELETE = "delete"
    SELECT = "select"
    CREATE_TABLE = "create_table"
    DROP_TABLE = "drop_table"
    BACKUP = "backup"
    RESTORE = "restore"
    CONNECTION_ESTABLISHED = "connection_established"
    CONNECTION_LOST = "connection_lost"
    ERROR = "error"

class DatabaseEvent:
    """Represents a database event"""
    
    def __init__(self, event_type: EventType, table_name: str = None, 
                 record_id: Any = None, data: Dict[str, Any] = None, 
                 timestamp: datetime = None, user_id: str = None):
        self.event_type = event_type
        self.table_name = table_name
        self.record_id = record_id
        self.data = data or {}
        self.timestamp = timestamp or datetime.now()
        self.user_id = user_id
        self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary"""
        return {
            'event_type': self.event_type.value,
            'table_name': self.table_name,
            'record_id': self.record_id,
            'data': self.data,
            'timestamp': self.timestamp.isoformat(),
            'user_id': self.user_id,
            'metadata': self.metadata
        }
    
    def __str__(self) -> str:
        return f"DatabaseEvent({self.event_type.value}, table={self.table_name}, id={self.record_id})"

class DatabaseObserver(ABC):
    """Abstract base class for database observers"""
    
    @abstractmethod
    def update(self, event: DatabaseEvent) -> None:
        """Handle database event"""
        pass
    
    @abstractmethod
    def get_observer_id(self) -> str:
        """Get unique observer identifier"""
        pass

class EventManager:
    """Manages database events and observers"""
    
    def __init__(self):
        self._observers: Dict[EventType, List[DatabaseObserver]] = {}
        self._event_history: List[DatabaseEvent] = []
        self._max_history_size = 1000
        self._enabled = True
    
    def subscribe(self, event_type: EventType, observer: DatabaseObserver) -> None:
        """Subscribe observer to specific event type"""
        if event_type not in self._observers:
            self._observers[event_type] = []
        
        if observer not in self._observers[event_type]:
            self._observers[event_type].append(observer)
            logger.info(f"Observer {observer.get_observer_id()} subscribed to {event_type.value}")
    
    def unsubscribe(self, event_type: EventType, observer: DatabaseObserver) -> None:
        """Unsubscribe observer from specific event type"""
        if event_type in self._observers and observer in self._observers[event_type]:
            self._observers[event_type].remove(observer)
            logger.info(f"Observer {observer.get_observer_id()} unsubscribed from {event_type.value}")
    
    def notify(self, event: DatabaseEvent) -> None:
        """Notify all observers of an event"""
        if not self._enabled:
            return
        
        # Add to history
        self._event_history.append(event)
        if len(self._event_history) > self._max_history_size:
            self._event_history.pop(0)
        
        # Notify observers
        if event.event_type in self._observers:
            for observer in self._observers[event.event_type]:
                try:
                    observer.update(event)
                except Exception as e:
                    logger.error(f"Error notifying observer {observer.get_observer_id()}: {e}")
        
        # Also notify general observers (if any)
        if EventType.ERROR in self._observers and event.event_type == EventType.ERROR:
            for observer in self._observers[EventType.ERROR]:
                try:
                    observer.update(event)
                except Exception as e:
                    logger.error(f"Error notifying error observer {observer.get_observer_id()}: {e}")
    
    def get_event_history(self, event_type: EventType = None, 
                         table_name: str = None, limit: int = 100) -> List[DatabaseEvent]:
        """Get event history with optional filters"""
        events = self._event_history
        
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        
        if table_name:
            events = [e for e in events if e.table_name == table_name]
        
        return events[-limit:] if limit else events
    
    def clear_history(self) -> None:
        """Clear event history"""
        self._event_history.clear()
    
    def enable(self) -> None:
        """Enable event notifications"""
        self._enabled = True
    
    def disable(self) -> None:
        """Disable event notifications"""
        self._enabled = False

# Concrete Observer Implementations

class AuditLogger(DatabaseObserver):
    """Logs all database events for audit purposes"""
    
    def __init__(self, log_file: str = None):
        self.observer_id = "audit_logger"
        self.log_file = log_file
        self.audit_logger = logging.getLogger("audit")
        
        if log_file:
            handler = logging.FileHandler(log_file)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.audit_logger.addHandler(handler)
            self.audit_logger.setLevel(logging.INFO)
    
    def update(self, event: DatabaseEvent) -> None:
        """Log database event"""
        log_message = f"DB_EVENT: {event.event_type.value} | Table: {event.table_name} | ID: {event.record_id} | User: {event.user_id}"
        self.audit_logger.info(log_message)
    
    def get_observer_id(self) -> str:
        return self.observer_id

class NotificationManager(DatabaseObserver):
    """Manages notifications for database events"""
    
    def __init__(self):
        self.observer_id = "notification_manager"
        self.notifications = []
        self.max_notifications = 100
    
    def update(self, event: DatabaseEvent) -> None:
        """Create notification for database event"""
        notification = {
            'id': len(self.notifications) + 1,
            'type': event.event_type.value,
            'message': self._create_message(event),
            'timestamp': event.timestamp,
            'table_name': event.table_name,
            'record_id': event.record_id,
            'user_id': event.user_id,
            'read': False
        }
        
        self.notifications.append(notification)
        
        # Keep only recent notifications
        if len(self.notifications) > self.max_notifications:
            self.notifications.pop(0)
    
    def _create_message(self, event: DatabaseEvent) -> str:
        """Create human-readable message for event"""
        messages = {
            EventType.INSERT: f"New record created in {event.table_name}",
            EventType.UPDATE: f"Record updated in {event.table_name}",
            EventType.DELETE: f"Record deleted from {event.table_name}",
            EventType.CREATE_TABLE: f"New table created: {event.table_name}",
            EventType.DROP_TABLE: f"Table dropped: {event.table_name}",
            EventType.BACKUP: f"Database backup completed",
            EventType.RESTORE: f"Database restore completed",
            EventType.ERROR: f"Database error: {event.data.get('error', 'Unknown error')}"
        }
        
        return messages.get(event.event_type, f"Database event: {event.event_type.value}")
    
    def get_notifications(self, unread_only: bool = False) -> List[Dict[str, Any]]:
        """Get notifications"""
        if unread_only:
            return [n for n in self.notifications if not n['read']]
        return self.notifications
    
    def mark_as_read(self, notification_id: int) -> None:
        """Mark notification as read"""
        for notification in self.notifications:
            if notification['id'] == notification_id:
                notification['read'] = True
                break
    
    def clear_notifications(self) -> None:
        """Clear all notifications"""
        self.notifications.clear()
    
    def get_observer_id(self) -> str:
        return self.observer_id

class CacheManager(DatabaseObserver):
    """Manages cache invalidation for database events"""
    
    def __init__(self):
        self.observer_id = "cache_manager"
        self.cache = {}
        self.table_cache_keys = {}
    
    def update(self, event: DatabaseEvent) -> None:
        """Invalidate cache based on database event"""
        if event.table_name:
            # Invalidate table-specific cache
            self._invalidate_table_cache(event.table_name)
            
            # Invalidate record-specific cache
            if event.record_id:
                self._invalidate_record_cache(event.table_name, event.record_id)
    
    def _invalidate_table_cache(self, table_name: str) -> None:
        """Invalidate all cache entries for a table"""
        keys_to_remove = []
        for key in self.cache.keys():
            if table_name in key:
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.cache[key]
            logger.info(f"Cache invalidated for key: {key}")
    
    def _invalidate_record_cache(self, table_name: str, record_id: Any) -> None:
        """Invalidate cache for specific record"""
        record_key = f"{table_name}:{record_id}"
        if record_key in self.cache:
            del self.cache[record_key]
            logger.info(f"Cache invalidated for record: {record_key}")
    
    def set_cache(self, key: str, value: Any, ttl: int = 3600) -> None:
        """Set cache value with TTL"""
        self.cache[key] = {
            'value': value,
            'expires_at': datetime.now().timestamp() + ttl
        }
    
    def get_cache(self, key: str) -> Any:
        """Get cache value if not expired"""
        if key in self.cache:
            cache_entry = self.cache[key]
            if datetime.now().timestamp() < cache_entry['expires_at']:
                return cache_entry['value']
            else:
                del self.cache[key]
        return None
    
    def clear_cache(self) -> None:
        """Clear all cache"""
        self.cache.clear()
    
    def get_observer_id(self) -> str:
        return self.observer_id

class MetricsCollector(DatabaseObserver):
    """Collects metrics for database operations"""
    
    def __init__(self):
        self.observer_id = "metrics_collector"
        self.metrics = {
            'total_operations': 0,
            'operations_by_type': {},
            'operations_by_table': {},
            'errors': 0,
            'last_operation_time': None,
            'operation_times': []
        }
    
    def update(self, event: DatabaseEvent) -> None:
        """Update metrics based on database event"""
        # Update total operations
        self.metrics['total_operations'] += 1
        
        # Update operations by type
        event_type = event.event_type.value
        self.metrics['operations_by_type'][event_type] = \
            self.metrics['operations_by_type'].get(event_type, 0) + 1
        
        # Update operations by table
        if event.table_name:
            self.metrics['operations_by_table'][event.table_name] = \
                self.metrics['operations_by_table'].get(event.table_name, 0) + 1
        
        # Update error count
        if event.event_type == EventType.ERROR:
            self.metrics['errors'] += 1
        
        # Update last operation time
        self.metrics['last_operation_time'] = event.timestamp
        
        # Store operation time for performance analysis
        self.metrics['operation_times'].append(event.timestamp)
        if len(self.metrics['operation_times']) > 1000:
            self.metrics['operation_times'].pop(0)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        return self.metrics.copy()
    
    def reset_metrics(self) -> None:
        """Reset all metrics"""
        self.metrics = {
            'total_operations': 0,
            'operations_by_type': {},
            'operations_by_table': {},
            'errors': 0,
            'last_operation_time': None,
            'operation_times': []
        }
    
    def get_observer_id(self) -> str:
        return self.observer_id

# Global event manager instance
event_manager = EventManager()

# Register default observers
def register_default_observers():
    """Register default observers with the event manager"""
    audit_logger = AuditLogger()
    notification_manager = NotificationManager()
    cache_manager = CacheManager()
    metrics_collector = MetricsCollector()
    
    # Subscribe to all event types
    for event_type in EventType:
        event_manager.subscribe(event_type, audit_logger)
        event_manager.subscribe(event_type, notification_manager)
        event_manager.subscribe(event_type, cache_manager)
        event_manager.subscribe(event_type, metrics_collector)
    
    logger.info("Default observers registered successfully")

# Helper function to create and notify events
def notify_event(event_type: EventType, table_name: str = None, 
                record_id: Any = None, data: Dict[str, Any] = None, 
                user_id: str = None) -> None:
    """Create and notify a database event"""
    event = DatabaseEvent(
        event_type=event_type,
        table_name=table_name,
        record_id=record_id,
        data=data or {},
        user_id=user_id
    )
    event_manager.notify(event)
