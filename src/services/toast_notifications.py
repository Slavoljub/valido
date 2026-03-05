# src/services/toast_notifications.py
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
import uuid
from flask import session, request, current_app
from dataclasses import dataclass, asdict

@dataclass
class ToastNotification:
    id: str
    type: str  # success, error, warning, info
    title: str
    message: str
    duration: int = 5000  # milliseconds
    position: str = 'top-right'  # top-right, top-left, bottom-right, bottom-left, top-center, bottom-center
    icon: Optional[str] = None
    actions: List[Dict] = None
    created_at: datetime = None
    expires_at: Optional[datetime] = None
    persistent: bool = False
    dismissible: bool = True
    theme: str = 'default'
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.expires_at is None and not self.persistent:
            self.expires_at = self.created_at + timedelta(seconds=self.duration / 1000)
        if self.actions is None:
            self.actions = []
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        if self.expires_at:
            data['expires_at'] = self.expires_at.isoformat()
        return data
    
    def is_expired(self) -> bool:
        """Check if notification is expired"""
        if self.persistent:
            return False
        return self.expires_at and datetime.utcnow() > self.expires_at

class ToastManager:
    """Manages toast notifications for the application"""
    
    def __init__(self):
        self.notifications: List[ToastNotification] = []
        self.max_notifications = 10
        self.default_duration = 5000
        self.default_position = 'top-right'
    
    def add_notification(self, 
                        type: str,
                        title: str,
                        message: str,
                        duration: int = None,
                        position: str = None,
                        icon: str = None,
                        actions: List[Dict] = None,
                        persistent: bool = False,
                        dismissible: bool = True,
                        theme: str = None) -> str:
        """Add a new toast notification"""
        
        # Generate unique ID
        notification_id = str(uuid.uuid4())
        
        # Set defaults
        if duration is None:
            duration = self.default_duration
        if position is None:
            position = self.default_position
        if theme is None:
            theme = session.get('theme', 'light')
        
        # Create notification
        notification = ToastNotification(
            id=notification_id,
            type=type,
            title=title,
            message=message,
            duration=duration,
            position=position,
            icon=icon or self._get_default_icon(type),
            actions=actions or [],
            persistent=persistent,
            dismissible=dismissible,
            theme=theme
        )
        
        # Add to list
        self.notifications.append(notification)
        
        # Clean up old notifications
        self._cleanup_expired()
        
        # Limit number of notifications
        if len(self.notifications) > self.max_notifications:
            self.notifications = self.notifications[-self.max_notifications:]
        
        return notification_id
    
    def success(self, title: str, message: str, **kwargs) -> str:
        """Add success notification"""
        return self.add_notification('success', title, message, **kwargs)
    
    def error(self, title: str, message: str, **kwargs) -> str:
        """Add error notification"""
        return self.add_notification('error', title, message, **kwargs)
    
    def warning(self, title: str, message: str, **kwargs) -> str:
        """Add warning notification"""
        return self.add_notification('warning', title, message, **kwargs)
    
    def info(self, title: str, message: str, **kwargs) -> str:
        """Add info notification"""
        return self.add_notification('info', title, message, **kwargs)
    
    def remove_notification(self, notification_id: str) -> bool:
        """Remove a specific notification"""
        for i, notification in enumerate(self.notifications):
            if notification.id == notification_id:
                del self.notifications[i]
                return True
        return False
    
    def clear_all(self):
        """Clear all notifications"""
        self.notifications.clear()
    
    def get_notifications(self, include_expired: bool = False) -> List[ToastNotification]:
        """Get all notifications"""
        if include_expired:
            return self.notifications.copy()
        else:
            return [n for n in self.notifications if not n.is_expired()]
    
    def get_notifications_for_position(self, position: str) -> List[ToastNotification]:
        """Get notifications for specific position"""
        notifications = self.get_notifications()
        return [n for n in notifications if n.position == position]
    
    def _cleanup_expired(self):
        """Remove expired notifications"""
        self.notifications = [n for n in self.notifications if not n.is_expired()]
    
    def _get_default_icon(self, type: str) -> str:
        """Get default icon for notification type"""
        icons = {
            'success': 'check-circle',
            'error': 'x-circle',
            'warning': 'exclamation-triangle',
            'info': 'information-circle'
        }
        return icons.get(type, 'bell')
    
    def to_json(self) -> str:
        """Convert notifications to JSON"""
        notifications = [n.to_dict() for n in self.get_notifications()]
        return json.dumps(notifications)

# Global toast manager instance
toast_manager = ToastManager()

# Convenience functions
def show_success(title: str, message: str, **kwargs) -> str:
    """Show success toast"""
    return toast_manager.success(title, message, **kwargs)

def show_error(title: str, message: str, **kwargs) -> str:
    """Show error toast"""
    return toast_manager.error(title, message, **kwargs)

def show_warning(title: str, message: str, **kwargs) -> str:
    """Show warning toast"""
    return toast_manager.warning(title, message, **kwargs)

def show_info(title: str, message: str, **kwargs) -> str:
    """Show info toast"""
    return toast_manager.info(title, message, **kwargs)

def remove_toast(notification_id: str) -> bool:
    """Remove specific toast"""
    return toast_manager.remove_notification(notification_id)

def clear_toasts():
    """Clear all toasts"""
    toast_manager.clear_all()
