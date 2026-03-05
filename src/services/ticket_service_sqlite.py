"""
SQLite-based Ticket Service
Business logic for the ticketing system using SQLite
"""

import sqlite3
import os
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
import uuid

logger = logging.getLogger(__name__)

@dataclass
class Ticket:
    """Ticket data class"""
    id: int
    ticket_id: str
    subject: str
    requester_name: str
    requester_email: str
    status: str
    priority: str
    type: str
    assigned_agent_id: Optional[int]
    assigned_agent_name: Optional[str]
    tags: Optional[str]
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime]
    closed_at: Optional[datetime]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'ticket_id': self.ticket_id,
            'subject': self.subject,
            'requester_name': self.requester_name,
            'requester_email': self.requester_email,
            'status': self.status,
            'priority': self.priority,
            'type': self.type,
            'assigned_agent_id': self.assigned_agent_id,
            'assigned_agent_name': self.assigned_agent_name,
            'tags': self.tags,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'closed_at': self.closed_at.isoformat() if self.closed_at else None
        }

@dataclass
class TicketMessage:
    """Ticket message data class"""
    id: int
    ticket_id: int
    author_name: str
    author_email: str
    content: str
    is_internal: bool
    created_at: datetime
    attachments: List[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'ticket_id': self.ticket_id,
            'author_name': self.author_name,
            'author_email': self.author_email,
            'content': self.content,
            'is_internal': self.is_internal,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'attachments': self.attachments or []
        }

class TicketService:
    """Service class for ticket operations using SQLite"""
    
    def __init__(self, db_path: str = 'data/sqlite/tickets.db'):
        """Initialize ticket service with database path"""
        self.db_path = db_path
        self._ensure_db_exists()
    
    def _ensure_db_exists(self):
        """Ensure database and tables exist"""
        if not os.path.exists(self.db_path):
            # Initialize the database with required tables
            self._initialize_database()
    
    def _get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def _parse_datetime(self, dt_str: str) -> datetime:
        """Parse datetime string from SQLite"""
        if dt_str:
            try:
                return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
            except:
                return datetime.now()
        return datetime.now()
    
    def get_tickets(self, status: Optional[str] = None, priority: Optional[str] = None, 
                   search: Optional[str] = None, page: int = 1, per_page: int = 20) -> List[Ticket]:
        """Get tickets with filtering and pagination"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Build query
            query = "SELECT * FROM tickets WHERE 1=1"
            params = []
            
            if status and status != 'all':
                query += " AND status = ?"
                params.append(status)
            
            if priority and priority != 'all':
                query += " AND priority = ?"
                params.append(priority)
            
            if search:
                query += " AND (subject LIKE ? OR requester_name LIKE ? OR requester_email LIKE ?)"
                search_param = f"%{search}%"
                params.extend([search_param, search_param, search_param])
            
            # Add ordering and pagination
            query += " ORDER BY created_at DESC"
            query += " LIMIT ? OFFSET ?"
            params.extend([per_page, (page - 1) * per_page])
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            tickets = []
            for row in cursor.fetchall():
                ticket = Ticket(
                    id=row[0],
                    ticket_id=row[1],
                    subject=row[2],
                    requester_name=row[3],
                    requester_email=row[4],
                    status=row[5],
                    priority=row[6],
                    type=row[7],
                    assigned_agent_id=row[8],
                    assigned_agent_name=row[9],
                    tags=row[10],
                    created_at=self._parse_datetime(row[11]),
                    updated_at=self._parse_datetime(row[12]),
                    resolved_at=self._parse_datetime(row[13]) if row[13] else None,
                    closed_at=self._parse_datetime(row[14]) if row[14] else None
                )
                tickets.append(ticket)
            
            conn.close()
            return tickets
            
        except Exception as e:
            logger.error(f"Error getting tickets: {e}")
            return []
    
    def get_ticket_by_id(self, ticket_id: int) -> Optional[Ticket]:
        """Get ticket by ID"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,))
            row = cursor.fetchone()
            
            if row:
                ticket = Ticket(
                    id=row[0],
                    ticket_id=row[1],
                    subject=row[2],
                    requester_name=row[3],
                    requester_email=row[4],
                    status=row[5],
                    priority=row[6],
                    type=row[7],
                    assigned_agent_id=row[8],
                    assigned_agent_name=row[9],
                    tags=row[10],
                    created_at=self._parse_datetime(row[11]),
                    updated_at=self._parse_datetime(row[12]),
                    resolved_at=self._parse_datetime(row[13]) if row[13] else None,
                    closed_at=self._parse_datetime(row[14]) if row[14] else None
                )
                
                # Get messages for this ticket
                cursor.execute("SELECT * FROM ticket_messages WHERE ticket_id = ? ORDER BY created_at ASC", (ticket_id,))
                messages = []
                for msg_row in cursor.fetchall():
                    message = TicketMessage(
                        id=msg_row[0],
                        ticket_id=msg_row[1],
                        author_name=msg_row[2],
                        author_email=msg_row[3],
                        content=msg_row[4],
                        is_internal=bool(msg_row[5]),
                        created_at=self._parse_datetime(msg_row[6])
                    )
                    
                    # Get attachments for this message
                    cursor.execute("SELECT * FROM ticket_attachments WHERE message_id = ?", (message.id,))
                    attachments = []
                    for att_row in cursor.fetchall():
                        attachment = {
                            'id': att_row[0],
                            'filename': att_row[2],
                            'file_path': att_row[3],
                            'file_size': att_row[4],
                            'mime_type': att_row[5]
                        }
                        attachments.append(attachment)
                    
                    message.attachments = attachments
                    messages.append(message)
                
                # Add messages to ticket
                ticket.messages = messages
                
                conn.close()
                return ticket
            
            conn.close()
            return None
            
        except Exception as e:
            logger.error(f"Error getting ticket {ticket_id}: {e}")
            return None
    
    def create_ticket(self, ticket_data: Dict[str, Any]) -> Optional[Ticket]:
        """Create a new ticket"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Generate unique ticket ID
            ticket_id = f"TKT-{datetime.now().strftime('%Y')}-{str(uuid.uuid4())[:8].upper()}"
            
            # Insert ticket
            cursor.execute('''
                INSERT INTO tickets 
                (ticket_id, subject, requester_name, requester_email, status, priority, type, assigned_agent_name, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                ticket_id,
                ticket_data['subject'],
                ticket_data['requester_name'],
                ticket_data['requester_email'],
                ticket_data.get('status', 'open'),
                ticket_data.get('priority', 'medium'),
                ticket_data.get('type', 'support'),
                ticket_data.get('assigned_agent_name'),
                ','.join(ticket_data.get('tags', [])) if ticket_data.get('tags') else None
            ))
            
            ticket_db_id = cursor.lastrowid
            
            # Add initial message if provided
            if ticket_data.get('message'):
                cursor.execute('''
                    INSERT INTO ticket_messages 
                    (ticket_id, author_name, author_email, content, is_internal)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    ticket_db_id,
                    ticket_data['requester_name'],
                    ticket_data['requester_email'],
                    ticket_data['message'],
                    False
                ))
            
            conn.commit()
            conn.close()
            
            # Return the created ticket
            return self.get_ticket_by_id(ticket_db_id)
            
        except Exception as e:
            logger.error(f"Error creating ticket: {e}")
            return None
    
    def update_ticket(self, ticket_id: int, update_data: Dict[str, Any]) -> Optional[Ticket]:
        """Update a ticket"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Build update query
            set_clauses = []
            params = []
            
            allowed_fields = ['status', 'priority', 'assigned_agent_id', 'assigned_agent_name', 'subject', 'tags']
            for field, value in update_data.items():
                if field in allowed_fields:
                    set_clauses.append(f"{field} = ?")
                    params.append(value)
            
            if set_clauses:
                set_clauses.append("updated_at = CURRENT_TIMESTAMP")
                params.append(ticket_id)
                
                query = f"UPDATE tickets SET {', '.join(set_clauses)} WHERE id = ?"
                cursor.execute(query, params)
                
                # Update resolved_at or closed_at if status is changing
                if 'status' in update_data:
                    if update_data['status'] == 'resolved':
                        cursor.execute("UPDATE tickets SET resolved_at = CURRENT_TIMESTAMP WHERE id = ?", (ticket_id,))
                    elif update_data['status'] == 'closed':
                        cursor.execute("UPDATE tickets SET closed_at = CURRENT_TIMESTAMP WHERE id = ?", (ticket_id,))
                
                conn.commit()
            
            conn.close()
            
            # Return the updated ticket
            return self.get_ticket_by_id(ticket_id)
            
        except Exception as e:
            logger.error(f"Error updating ticket {ticket_id}: {e}")
            return None
    
    def add_message_to_ticket(self, message_data: Dict[str, Any]) -> Optional[TicketMessage]:
        """Add a message to a ticket"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Insert message
            cursor.execute('''
                INSERT INTO ticket_messages 
                (ticket_id, author_name, author_email, content, is_internal)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                message_data['ticket_id'],
                message_data['author_name'],
                message_data['author_email'],
                message_data['content'],
                message_data.get('is_internal', False)
            ))
            
            message_id = cursor.lastrowid
            
            # Add attachments if provided
            if message_data.get('attachments'):
                for attachment in message_data['attachments']:
                    cursor.execute('''
                        INSERT INTO ticket_attachments 
                        (message_id, filename, file_path, file_size, mime_type)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (
                        message_id,
                        attachment['filename'],
                        attachment['file_path'],
                        attachment.get('file_size', 0),
                        attachment.get('mime_type', 'application/octet-stream')
                    ))
            
            # Update ticket timestamp
            cursor.execute("UPDATE tickets SET updated_at = CURRENT_TIMESTAMP WHERE id = ?", (message_data['ticket_id'],))
            
            conn.commit()
            conn.close()
            
            # Return the created message
            return self._get_message_by_id(message_id)
            
        except Exception as e:
            logger.error(f"Error adding message to ticket: {e}")
            return None
    
    def _get_message_by_id(self, message_id: int) -> Optional[TicketMessage]:
        """Get message by ID"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM ticket_messages WHERE id = ?", (message_id,))
            row = cursor.fetchone()
            
            if row:
                message = TicketMessage(
                    id=row[0],
                    ticket_id=row[1],
                    author_name=row[2],
                    author_email=row[3],
                    content=row[4],
                    is_internal=bool(row[5]),
                    created_at=self._parse_datetime(row[6])
                )
                
                # Get attachments
                cursor.execute("SELECT * FROM ticket_attachments WHERE message_id = ?", (message_id,))
                attachments = []
                for att_row in cursor.fetchall():
                    attachment = {
                        'id': att_row[0],
                        'filename': att_row[2],
                        'file_path': att_row[3],
                        'file_size': att_row[4],
                        'mime_type': att_row[5]
                    }
                    attachments.append(attachment)
                
                message.attachments = attachments
                
                conn.close()
                return message
            
            conn.close()
            return None
            
        except Exception as e:
            logger.error(f"Error getting message {message_id}: {e}")
            return None
    
    def get_ticket_statistics(self) -> Dict[str, int]:
        """Get ticket statistics"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Get total tickets
            cursor.execute("SELECT COUNT(*) FROM tickets")
            total = cursor.fetchone()[0]
            
            # Get pending tickets
            cursor.execute("SELECT COUNT(*) FROM tickets WHERE status = 'pending'")
            pending = cursor.fetchone()[0]
            
            # Get resolved tickets
            cursor.execute("SELECT COUNT(*) FROM tickets WHERE status = 'resolved'")
            resolved = cursor.fetchone()[0]
            
            # Get closed tickets
            cursor.execute("SELECT COUNT(*) FROM tickets WHERE status = 'closed'")
            closed = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'total': total,
                'pending': pending,
                'resolved': resolved,
                'closed': closed
            }
            
        except Exception as e:
            logger.error(f"Error getting ticket statistics: {e}")
            return {'total': 0, 'pending': 0, 'resolved': 0, 'closed': 0}
