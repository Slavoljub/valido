"""
Notification Models for ValidoAI
Handles notification storage, retrieval, and management
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import uuid
import json
from enum import Enum


class NotificationType(Enum):
    """Notification types"""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    SYSTEM = "system"
    SECURITY = "security"
    FINANCIAL = "financial"
    AI = "ai"
    TICKET = "ticket"
    USER = "user"


class NotificationPriority(Enum):
    """Notification priorities"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class NotificationStatus(Enum):
    """Notification status"""
    UNREAD = "unread"
    READ = "read"
    ARCHIVED = "archived"
    DELETED = "deleted"


@dataclass
class Notification:
    """Notification data model"""
    id: Optional[str] = None
    user_id: Optional[str] = None
    type: str = "info"
    priority: str = "normal"
    status: str = "unread"
    title: str = ""
    message: str = ""
    icon: Optional[str] = None
    actions: List[Dict] = None
    metadata: Dict = None
    expires_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()
        if self.actions is None:
            self.actions = []
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        if self.expires_at:
            data['expires_at'] = self.expires_at.isoformat()
        if self.read_at:
            data['read_at'] = self.read_at.isoformat()
        return data
    
    def mark_as_read(self):
        """Mark notification as read"""
        self.status = NotificationStatus.READ.value
        self.read_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def mark_as_archived(self):
        """Mark notification as archived"""
        self.status = NotificationStatus.ARCHIVED.value
        self.updated_at = datetime.utcnow()
    
    def is_expired(self) -> bool:
        """Check if notification is expired"""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at
    
    def is_read(self) -> bool:
        """Check if notification is read"""
        return self.status == NotificationStatus.READ.value
    
    def get_age(self) -> str:
        """Get human-readable age of notification"""
        now = datetime.utcnow()
        diff = now - self.created_at
        
        if diff.days > 0:
            return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        else:
            return "Just now"


class NotificationManager:
    """Manages notifications in the database"""
    
    def __init__(self, db_connection):
        self.db = db_connection
        self._ensure_table_exists()
    
    def _ensure_table_exists(self):
        """Ensure notifications table exists"""
        self.db.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                type TEXT NOT NULL,
                priority TEXT NOT NULL DEFAULT 'normal',
                status TEXT NOT NULL DEFAULT 'unread',
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                icon TEXT,
                actions TEXT,
                metadata TEXT,
                expires_at TEXT,
                read_at TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        self.db.commit()
    
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
        
        notification = Notification(
            title=title,
            message=message,
            type=notification_type,
            priority=priority,
            user_id=user_id,
            icon=icon,
            actions=actions or [],
            metadata=metadata or {},
            expires_at=expires_at
        )
        
        # Insert into database
        self.db.execute('''
            INSERT INTO notifications 
            (id, user_id, type, priority, status, title, message, icon, actions, metadata, expires_at, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            notification.id,
            notification.user_id,
            notification.type,
            notification.priority,
            notification.status,
            notification.title,
            notification.message,
            notification.icon,
            json.dumps(notification.actions),
            json.dumps(notification.metadata),
            notification.expires_at.isoformat() if notification.expires_at else None,
            notification.created_at.isoformat(),
            notification.updated_at.isoformat()
        ))
        
        self.db.commit()
        return notification.id
    
    def get_notification(self, notification_id: str) -> Optional[Notification]:
        """Get a specific notification"""
        cursor = self.db.execute('''
            SELECT * FROM notifications WHERE id = ?
        ''', (notification_id,))
        
        row = cursor.fetchone()
        if row:
            return self._row_to_notification(row)
        return None
    
    def get_user_notifications(self, 
                             user_id: str, 
                             status: Optional[str] = None,
                             limit: int = 50,
                             offset: int = 0) -> List[Notification]:
        """Get notifications for a specific user"""
        
        query = '''
            SELECT * FROM notifications 
            WHERE user_id = ?
        '''
        params = [user_id]
        
        if status:
            query += ' AND status = ?'
            params.append(status)
        
        query += ' ORDER BY created_at DESC LIMIT ? OFFSET ?'
        params.extend([limit, offset])
        
        cursor = self.db.execute(query, params)
        return [self._row_to_notification(row) for row in cursor.fetchall()]
    
    def get_all_notifications(self, 
                            status: Optional[str] = None,
                            notification_type: Optional[str] = None,
                            limit: int = 100,
                            offset: int = 0) -> List[Notification]:
        """Get all notifications with optional filtering"""
        
        query = 'SELECT * FROM notifications WHERE 1=1'
        params = []
        
        if status:
            query += ' AND status = ?'
            params.append(status)
        
        if notification_type:
            query += ' AND type = ?'
            params.append(notification_type)
        
        query += ' ORDER BY created_at DESC LIMIT ? OFFSET ?'
        params.extend([limit, offset])
        
        cursor = self.db.execute(query, params)
        return [self._row_to_notification(row) for row in cursor.fetchall()]
    
    def mark_as_read(self, notification_id: str) -> bool:
        """Mark notification as read"""
        now = datetime.utcnow().isoformat()
        cursor = self.db.execute('''
            UPDATE notifications 
            SET status = ?, read_at = ?, updated_at = ?
            WHERE id = ?
        ''', (NotificationStatus.READ.value, now, now, notification_id))
        
        self.db.commit()
        return cursor.rowcount > 0
    
    def mark_as_archived(self, notification_id: str) -> bool:
        """Mark notification as archived"""
        now = datetime.utcnow().isoformat()
        cursor = self.db.execute('''
            UPDATE notifications 
            SET status = ?, updated_at = ?
            WHERE id = ?
        ''', (NotificationStatus.ARCHIVED.value, now, notification_id))
        
        self.db.commit()
        return cursor.rowcount > 0
    
    def delete_notification(self, notification_id: str) -> bool:
        """Delete notification"""
        cursor = self.db.execute('''
            DELETE FROM notifications WHERE id = ?
        ''', (notification_id,))
        
        self.db.commit()
        return cursor.rowcount > 0
    
    def get_unread_count(self, user_id: Optional[str] = None) -> int:
        """Get count of unread notifications"""
        if user_id:
            cursor = self.db.execute('''
                SELECT COUNT(*) FROM notifications 
                WHERE user_id = ? AND status = ?
            ''', (user_id, NotificationStatus.UNREAD.value))
        else:
            cursor = self.db.execute('''
                SELECT COUNT(*) FROM notifications 
                WHERE status = ?
            ''', (NotificationStatus.UNREAD.value,))
        
        return cursor.fetchone()[0]
    
    def cleanup_expired(self) -> int:
        """Remove expired notifications"""
        cursor = self.db.execute('''
            DELETE FROM notifications 
            WHERE expires_at IS NOT NULL AND expires_at < ?
        ''', (datetime.utcnow().isoformat(),))
        
        self.db.commit()
        return cursor.rowcount
    
    def _row_to_notification(self, row) -> Notification:
        """Convert database row to Notification object"""
        return Notification(
            id=row[0],
            user_id=row[1],
            type=row[2],
            priority=row[3],
            status=row[4],
            title=row[5],
            message=row[6],
            icon=row[7],
            actions=json.loads(row[8]) if row[8] else [],
            metadata=json.loads(row[9]) if row[9] else {},
            expires_at=datetime.fromisoformat(row[10]) if row[10] else None,
            read_at=datetime.fromisoformat(row[11]) if row[11] else None,
            created_at=datetime.fromisoformat(row[12]),
            updated_at=datetime.fromisoformat(row[13])
        )
