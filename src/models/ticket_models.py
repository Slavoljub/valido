"""
Ticket Models
Database models for the ticketing system
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()

class TicketPriority(enum.Enum):
    """Ticket priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class TicketStatus(enum.Enum):
    """Ticket status levels"""
    OPEN = "open"
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    WAITING_FOR_CUSTOMER = "waiting_for_customer"
    WAITING_FOR_THIRD_PARTY = "waiting_for_third_party"
    RESOLVED = "resolved"
    CLOSED = "closed"
    CANCELLED = "cancelled"

class TicketType(enum.Enum):
    """Ticket types"""
    QUESTION = "question"
    BUG = "bug"
    FEATURE_REQUEST = "feature_request"
    SUPPORT = "support"
    BILLING = "billing"
    TECHNICAL = "technical"
    GENERAL = "general"

class Ticket(Base):
    """Main ticket model"""
    __tablename__ = 'tickets'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticket_id = Column(String(20), unique=True, nullable=False, index=True)  # Human-readable ID like #1846325
    subject = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(Enum(TicketPriority), default=TicketPriority.MEDIUM, nullable=False)
    status = Column(Enum(TicketStatus), default=TicketStatus.OPEN, nullable=False)
    ticket_type = Column(Enum(TicketType), default=TicketType.GENERAL, nullable=False)
    
    # Relationships
    requester_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    agent_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    follower_ids = Column(String(500), nullable=True)  # Comma-separated user IDs
    
    # Metadata
    tags = Column(String(500), nullable=True)  # Comma-separated tags
    source = Column(String(50), default='web', nullable=False)  # web, email, phone, etc.
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    resolved_at = Column(DateTime, nullable=True)
    closed_at = Column(DateTime, nullable=True)
    
    # SLA and time tracking
    due_date = Column(DateTime, nullable=True)
    first_response_at = Column(DateTime, nullable=True)
    resolution_time = Column(Integer, nullable=True)  # in minutes
    
    # Relationships
    requester = relationship("User", foreign_keys=[requester_id], back_populates="requested_tickets")
    agent = relationship("User", foreign_keys=[agent_id], back_populates="assigned_tickets")
    messages = relationship("TicketMessage", back_populates="ticket", cascade="all, delete-orphan")
    attachments = relationship("TicketAttachment", back_populates="ticket", cascade="all, delete-orphan")
    activities = relationship("TicketActivity", back_populates="ticket", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Ticket(id={self.ticket_id}, subject='{self.subject}', status={self.status})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert ticket to dictionary"""
        return {
            'id': self.ticket_id,
            'subject': self.subject,
            'description': self.description,
            'priority': self.priority.value,
            'status': self.status.value,
            'type': self.ticket_type.value,
            'requester_id': self.requester_id,
            'agent_id': self.agent_id,
            'follower_ids': self.follower_ids,
            'tags': self.tags,
            'source': self.source,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'closed_at': self.closed_at.isoformat() if self.closed_at else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'first_response_at': self.first_response_at.isoformat() if self.first_response_at else None,
            'resolution_time': self.resolution_time,
            'requester_name': self.requester.full_name if self.requester else None,
            'agent_name': self.agent.full_name if self.agent else None,
            'message_count': len(self.messages),
            'last_message_at': max([msg.created_at for msg in self.messages]).isoformat() if self.messages else None
        }

class TicketMessage(Base):
    """Ticket message model"""
    __tablename__ = 'ticket_messages'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticket_id = Column(Integer, ForeignKey('tickets.id'), nullable=False)
    sender_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    sender_type = Column(String(20), nullable=False)  # 'requester', 'agent', 'system'
    message = Column(Text, nullable=False)
    is_internal = Column(Boolean, default=False, nullable=False)  # Internal notes not visible to requester
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    ticket = relationship("Ticket", back_populates="messages")
    sender = relationship("User", back_populates="sent_messages")
    attachments = relationship("MessageAttachment", back_populates="message", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<TicketMessage(id={self.id}, ticket_id={self.ticket_id}, sender_type={self.sender_type})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary"""
        return {
            'id': self.id,
            'ticket_id': self.ticket_id,
            'sender_id': self.sender_id,
            'sender_type': self.sender_type,
            'message': self.message,
            'is_internal': self.is_internal,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'sender_name': self.sender.full_name if self.sender else None,
            'sender_email': self.sender.email if self.sender else None
        }

class TicketAttachment(Base):
    """Ticket attachment model"""
    __tablename__ = 'ticket_attachments'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticket_id = Column(Integer, ForeignKey('tickets.id'), nullable=False)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)  # in bytes
    mime_type = Column(String(100), nullable=False)
    uploaded_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    ticket = relationship("Ticket", back_populates="attachments")
    uploader = relationship("User", back_populates="uploaded_attachments")
    
    def __repr__(self):
        return f"<TicketAttachment(id={self.id}, filename='{self.filename}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert attachment to dictionary"""
        return {
            'id': self.id,
            'ticket_id': self.ticket_id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'mime_type': self.mime_type,
            'uploaded_by': self.uploaded_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'uploader_name': self.uploader.full_name if self.uploader else None
        }

class MessageAttachment(Base):
    """Message attachment model"""
    __tablename__ = 'message_attachments'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    message_id = Column(Integer, ForeignKey('ticket_messages.id'), nullable=False)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)  # in bytes
    mime_type = Column(String(100), nullable=False)
    uploaded_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    message = relationship("TicketMessage", back_populates="attachments")
    uploader = relationship("User", back_populates="uploaded_message_attachments")
    
    def __repr__(self):
        return f"<MessageAttachment(id={self.id}, filename='{self.filename}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message attachment to dictionary"""
        return {
            'id': self.id,
            'message_id': self.message_id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'mime_type': self.mime_type,
            'uploaded_by': self.uploaded_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'uploader_name': self.uploader.full_name if self.uploader else None
        }

class TicketActivity(Base):
    """Ticket activity log model"""
    __tablename__ = 'ticket_activities'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticket_id = Column(Integer, ForeignKey('tickets.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)  # Can be null for system activities
    activity_type = Column(String(50), nullable=False)  # created, updated, assigned, status_changed, etc.
    description = Column(Text, nullable=False)
    old_value = Column(String(255), nullable=True)
    new_value = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    ticket = relationship("Ticket", back_populates="activities")
    user = relationship("User", back_populates="ticket_activities")
    
    def __repr__(self):
        return f"<TicketActivity(id={self.id}, ticket_id={self.ticket_id}, activity_type={self.activity_type})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert activity to dictionary"""
        return {
            'id': self.id,
            'ticket_id': self.ticket_id,
            'user_id': self.user_id,
            'activity_type': self.activity_type,
            'description': self.description,
            'old_value': self.old_value,
            'new_value': self.new_value,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'user_name': self.user.full_name if self.user else 'System'
        }

class TicketTemplate(Base):
    """Ticket template model for quick responses"""
    __tablename__ = 'ticket_templates'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    subject = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String(50), nullable=True)  # general, technical, billing, etc.
    is_active = Column(Boolean, default=True, nullable=False)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    creator = relationship("User", back_populates="created_templates")
    
    def __repr__(self):
        return f"<TicketTemplate(id={self.id}, name='{self.name}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert template to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'subject': self.subject,
            'content': self.content,
            'category': self.category,
            'is_active': self.is_active,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'creator_name': self.creator.full_name if self.creator else None
        }

class TicketSLA(Base):
    """Service Level Agreement model"""
    __tablename__ = 'ticket_slas'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    priority = Column(Enum(TicketPriority), nullable=False)
    first_response_time = Column(Integer, nullable=False)  # in minutes
    resolution_time = Column(Integer, nullable=False)  # in minutes
    business_hours_only = Column(Boolean, default=True, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<TicketSLA(id={self.id}, name='{self.name}', priority={self.priority})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert SLA to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'priority': self.priority.value,
            'first_response_time': self.first_response_time,
            'resolution_time': self.resolution_time,
            'business_hours_only': self.business_hours_only,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

# Update User model relationships (assuming User model exists)
# These would be added to the existing User model:

"""
class User(Base):
    # ... existing fields ...
    
    # Ticket relationships
    requested_tickets = relationship("Ticket", foreign_keys="Ticket.requester_id", back_populates="requester")
    assigned_tickets = relationship("Ticket", foreign_keys="Ticket.agent_id", back_populates="agent")
    sent_messages = relationship("TicketMessage", back_populates="sender")
    uploaded_attachments = relationship("TicketAttachment", back_populates="uploader")
    uploaded_message_attachments = relationship("MessageAttachment", back_populates="uploader")
    ticket_activities = relationship("TicketActivity", back_populates="user")
    created_templates = relationship("TicketTemplate", back_populates="creator")
"""
