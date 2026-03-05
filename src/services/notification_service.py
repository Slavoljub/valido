"""
Notification Service for ValidoAI
Handles notification business logic and operations
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import sqlite3
import json
from src.models.notification_models import NotificationManager, Notification, NotificationType, NotificationPriority, NotificationStatus


class NotificationService:
    """Service for managing notifications"""
    
    def __init__(self, db_path: str = "data/sqlite/app.db"):
        self.db_path = db_path
        self._init_manager()
    
    def _init_manager(self):
        """Initialize notification manager with database connection"""
        self.db_conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.db_conn.row_factory = sqlite3.Row
        self.manager = NotificationManager(self.db_conn)
    
    def create_notification(self,
                          title: str,
                          message: str,
                          notification_type: str = "info",
                          priority: str = "normal",
                          user_id: Optional[str] = None,
                          icon: Optional[str] = None,
                          actions: List[Dict] = None,
                          metadata: Dict = None,
                          expires_at: Optional[datetime] = None) -> str:
        """Create a new notification"""
        return self.manager.create_notification(
            title=title,
            message=message,
            notification_type=notification_type,
            priority=priority,
            user_id=user_id,
            icon=icon,
            actions=actions,
            metadata=metadata,
            expires_at=expires_at
        )
    
    def get_user_notifications(self,
                             user_id: str,
                             status: Optional[str] = None,
                             limit: int = 50,
                             offset: int = 0) -> List[Dict]:
        """Get notifications for a specific user"""
        notifications = self.manager.get_user_notifications(
            user_id=user_id,
            status=status,
            limit=limit,
            offset=offset
        )
        return [notification.to_dict() for notification in notifications]
    
    def get_all_notifications(self,
                            status: Optional[str] = None,
                            notification_type: Optional[str] = None,
                            limit: int = 100,
                            offset: int = 0) -> List[Dict]:
        """Get all notifications with optional filtering"""
        notifications = self.manager.get_all_notifications(
            status=status,
            notification_type=notification_type,
            limit=limit,
            offset=offset
        )
        return [notification.to_dict() for notification in notifications]
    
    def get_notification(self, notification_id: str) -> Optional[Dict]:
        """Get a specific notification"""
        notification = self.manager.get_notification(notification_id)
        return notification.to_dict() if notification else None
    
    def mark_as_read(self, notification_id: str) -> bool:
        """Mark notification as read"""
        return self.manager.mark_as_read(notification_id)
    
    def mark_as_archived(self, notification_id: str) -> bool:
        """Mark notification as archived"""
        return self.manager.mark_as_archived(notification_id)
    
    def delete_notification(self, notification_id: str) -> bool:
        """Delete notification"""
        return self.manager.delete_notification(notification_id)
    
    def get_unread_count(self, user_id: Optional[str] = None) -> int:
        """Get count of unread notifications"""
        return self.manager.get_unread_count(user_id)
    
    def cleanup_expired(self) -> int:
        """Remove expired notifications"""
        return self.manager.cleanup_expired()
    
    # Convenience methods for common notification types
    def create_success_notification(self, title: str, message: str, user_id: Optional[str] = None, **kwargs) -> str:
        """Create a success notification"""
        return self.create_notification(
            title=title,
            message=message,
            notification_type="success",
            icon="fas fa-check-circle",
            user_id=user_id,
            **kwargs
        )
    
    def create_error_notification(self, title: str, message: str, user_id: Optional[str] = None, **kwargs) -> str:
        """Create an error notification"""
        return self.create_notification(
            title=title,
            message=message,
            notification_type="error",
            icon="fas fa-exclamation-circle",
            user_id=user_id,
            **kwargs
        )
    
    def create_warning_notification(self, title: str, message: str, user_id: Optional[str] = None, **kwargs) -> str:
        """Create a warning notification"""
        return self.create_notification(
            title=title,
            message=message,
            notification_type="warning",
            icon="fas fa-exclamation-triangle",
            user_id=user_id,
            **kwargs
        )
    
    def create_info_notification(self, title: str, message: str, user_id: Optional[str] = None, **kwargs) -> str:
        """Create an info notification"""
        return self.create_notification(
            title=title,
            message=message,
            notification_type="info",
            icon="fas fa-info-circle",
            user_id=user_id,
            **kwargs
        )
    
    def create_system_notification(self, title: str, message: str, user_id: Optional[str] = None, **kwargs) -> str:
        """Create a system notification"""
        return self.create_notification(
            title=title,
            message=message,
            notification_type="system",
            icon="fas fa-cog",
            user_id=user_id,
            **kwargs
        )
    
    def create_security_notification(self, title: str, message: str, user_id: Optional[str] = None, **kwargs) -> str:
        """Create a security notification"""
        return self.create_notification(
            title=title,
            message=message,
            notification_type="security",
            icon="fas fa-shield-alt",
            user_id=user_id,
            priority="high",
            **kwargs
        )
    
    def create_financial_notification(self, title: str, message: str, user_id: Optional[str] = None, **kwargs) -> str:
        """Create a financial notification"""
        return self.create_notification(
            title=title,
            message=message,
            notification_type="financial",
            icon="fas fa-dollar-sign",
            user_id=user_id,
            **kwargs
        )
    
    def create_ai_notification(self, title: str, message: str, user_id: Optional[str] = None, **kwargs) -> str:
        """Create an AI-related notification"""
        return self.create_notification(
            title=title,
            message=message,
            notification_type="ai",
            icon="fas fa-brain",
            user_id=user_id,
            **kwargs
        )
    
    def create_ticket_notification(self, title: str, message: str, user_id: Optional[str] = None, **kwargs) -> str:
        """Create a ticket-related notification"""
        return self.create_notification(
            title=title,
            message=message,
            notification_type="ticket",
            icon="fas fa-ticket-alt",
            user_id=user_id,
            **kwargs
        )
    
    def create_user_notification(self, title: str, message: str, user_id: Optional[str] = None, **kwargs) -> str:
        """Create a user-related notification"""
        return self.create_notification(
            title=title,
            message=message,
            notification_type="user",
            icon="fas fa-user",
            user_id=user_id,
            **kwargs
        )
    
    # Bulk operations
    def mark_all_as_read(self, user_id: str) -> int:
        """Mark all notifications as read for a user"""
        notifications = self.manager.get_user_notifications(user_id, status="unread")
        count = 0
        for notification in notifications:
            if self.manager.mark_as_read(notification.id):
                count += 1
        return count
    
    def mark_all_as_archived(self, user_id: str) -> int:
        """Mark all notifications as archived for a user"""
        notifications = self.manager.get_user_notifications(user_id, status="read")
        count = 0
        for notification in notifications:
            if self.manager.mark_as_archived(notification.id):
                count += 1
        return count
    
    def delete_all_archived(self, user_id: str) -> int:
        """Delete all archived notifications for a user"""
        notifications = self.manager.get_user_notifications(user_id, status="archived")
        count = 0
        for notification in notifications:
            if self.manager.delete_notification(notification.id):
                count += 1
        return count
    
    # Statistics and analytics
    def get_notification_statistics(self, user_id: Optional[str] = None) -> Dict:
        """Get notification statistics"""
        if user_id:
            all_notifications = self.manager.get_user_notifications(user_id, limit=1000)
        else:
            all_notifications = self.manager.get_all_notifications(limit=1000)
        
        stats = {
            'total': len(all_notifications),
            'unread': 0,
            'read': 0,
            'archived': 0,
            'by_type': {},
            'by_priority': {},
            'recent_activity': []
        }
        
        for notification in all_notifications:
            # Count by status
            if notification.status == 'unread':
                stats['unread'] += 1
            elif notification.status == 'read':
                stats['read'] += 1
            elif notification.status == 'archived':
                stats['archived'] += 1
            
            # Count by type
            notification_type = notification.type
            if notification_type not in stats['by_type']:
                stats['by_type'][notification_type] = 0
            stats['by_type'][notification_type] += 1
            
            # Count by priority
            priority = notification.priority
            if priority not in stats['by_priority']:
                stats['by_priority'][priority] = 0
            stats['by_priority'][priority] += 1
            
            # Recent activity (last 7 days)
            if notification.created_at > datetime.utcnow() - timedelta(days=7):
                stats['recent_activity'].append({
                    'id': notification.id,
                    'title': notification.title,
                    'type': notification.type,
                    'status': notification.status,
                    'created_at': notification.created_at.isoformat()
                })
        
        return stats
    
    def get_notification_trends(self, days: int = 30, user_id: Optional[str] = None) -> Dict:
        """Get notification trends over time"""
        if user_id:
            all_notifications = self.manager.get_user_notifications(user_id, limit=1000)
        else:
            all_notifications = self.manager.get_all_notifications(limit=1000)
        
        trends = {
            'daily_counts': {},
            'type_trends': {},
            'priority_trends': {}
        }
        
        for notification in all_notifications:
            date_str = notification.created_at.strftime('%Y-%m-%d')
            
            # Daily counts
            if date_str not in trends['daily_counts']:
                trends['daily_counts'][date_str] = 0
            trends['daily_counts'][date_str] += 1
            
            # Type trends
            notification_type = notification.type
            if notification_type not in trends['type_trends']:
                trends['type_trends'][notification_type] = {}
            if date_str not in trends['type_trends'][notification_type]:
                trends['type_trends'][notification_type][date_str] = 0
            trends['type_trends'][notification_type][date_str] += 1
            
            # Priority trends
            priority = notification.priority
            if priority not in trends['priority_trends']:
                trends['priority_trends'][priority] = {}
            if date_str not in trends['priority_trends'][priority]:
                trends['priority_trends'][priority][date_str] = 0
            trends['priority_trends'][priority][date_str] += 1
        
        return trends
    
    def close(self):
        """Close database connection"""
        if hasattr(self, 'db_conn'):
            self.db_conn.close()


# Global notification service instance
notification_service = NotificationService()
