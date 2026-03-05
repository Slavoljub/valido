#!/usr/bin/env python3
"""
Ticket Service
Handles all business logic for the ticketing system
"""

import sqlite3
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import uuid

class TicketService:
    def __init__(self, db_path: str = "data/sqlite/ticketing.db"):
        self.db_path = db_path
        self.ensure_database_exists()
    
    def ensure_database_exists(self):
        """Ensure the database and tables exist"""
        if not os.path.exists(self.db_path):
            # Import and run the database creation script
            from scripts.create_ticketing_db import create_database
            create_database()
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def get_ticket_statistics(self) -> Dict[str, int]:
        """Get ticket statistics for dashboard"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Total tickets
            cursor.execute('SELECT COUNT(*) FROM tickets')
            total_tickets = cursor.fetchone()[0]
            
            # Pending tickets
            cursor.execute('SELECT COUNT(*) FROM tickets WHERE status = "pending"')
            pending_tickets = cursor.fetchone()[0]
            
            # In progress tickets
            cursor.execute('SELECT COUNT(*) FROM tickets WHERE status = "in_progress"')
            in_progress_tickets = cursor.fetchone()[0]
            
            # Solved tickets (resolved + closed)
            cursor.execute('SELECT COUNT(*) FROM tickets WHERE status IN ("resolved", "closed")')
            solved_tickets = cursor.fetchone()[0]
            
            # Deleted tickets (simulated)
            deleted_tickets = 0
            
            return {
                'total_tickets': total_tickets,
                'pending_tickets': pending_tickets,
                'in_progress_tickets': in_progress_tickets,
                'solved_tickets': solved_tickets,
                'deleted_tickets': deleted_tickets
            }
        except Exception as e:
            # Return default values if there's an error
            return {
                'total_tickets': 0,
                'pending_tickets': 0,
                'in_progress_tickets': 0,
                'solved_tickets': 0,
                'deleted_tickets': 0
            }
        finally:
            conn.close()
    
    def get_tickets(self, filters: Dict = None, page: int = 1, per_page: int = 20) -> Dict:
        """Get tickets with filtering and pagination"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Build query with filters
            query = """
                SELECT t.*, 
                       r.name as requester_name, r.avatar_url as requester_avatar,
                       a.name as agent_name, a.avatar_url as agent_avatar
                FROM tickets t
                LEFT JOIN users r ON t.requester_id = r.id
                LEFT JOIN users a ON t.agent_id = a.id
                WHERE 1=1
            """
            params = []
            
            if filters:
                if filters.get('status'):
                    query += " AND t.status = ?"
                    params.append(filters['status'])
                
                if filters.get('priority'):
                    query += " AND t.priority = ?"
                    params.append(filters['priority'])
                
                if filters.get('type'):
                    query += " AND t.type = ?"
                    params.append(filters['type'])
                
                if filters.get('search'):
                    search_term = f"%{filters['search']}%"
                    query += " AND (t.subject LIKE ? OR t.description LIKE ? OR r.name LIKE ?)"
                    params.extend([search_term, search_term, search_term])
            
            # Add ordering
            query += " ORDER BY t.created_at DESC"
            
            # Add pagination
            offset = (page - 1) * per_page
            query += " LIMIT ? OFFSET ?"
            params.extend([per_page, offset])
            
            cursor.execute(query, params)
            tickets = cursor.fetchall()
            
            # Get total count for pagination
            count_query = """
                SELECT COUNT(*) FROM tickets t
                LEFT JOIN users r ON t.requester_id = r.id
                WHERE 1=1
            """
            count_params = []
            
            if filters:
                if filters.get('status'):
                    count_query += " AND t.status = ?"
                    count_params.append(filters['status'])
                
                if filters.get('priority'):
                    count_query += " AND t.priority = ?"
                    count_params.append(filters['priority'])
                
                if filters.get('type'):
                    count_query += " AND t.type = ?"
                    count_params.append(filters['type'])
                
                if filters.get('search'):
                    search_term = f"%{filters['search']}%"
                    count_query += " AND (t.subject LIKE ? OR t.description LIKE ? OR r.name LIKE ?)"
                    count_params.extend([search_term, search_term, search_term])
            
            cursor.execute(count_query, count_params)
            total_count = cursor.fetchone()[0]
            
            # Format tickets
            formatted_tickets = []
            for ticket in tickets:
                # Convert datetime strings to datetime objects
                created_at = datetime.fromisoformat(ticket[11]) if ticket[11] else None
                updated_at = datetime.fromisoformat(ticket[12]) if ticket[12] else None
                closed_at = datetime.fromisoformat(ticket[13]) if ticket[13] else None
                
                formatted_tickets.append({
                    'id': ticket[0],
                    'ticket_number': ticket[1],
                    'subject': ticket[2],
                    'description': ticket[3],
                    'requester_id': ticket[4],
                    'agent_id': ticket[5],
                    'follower_id': ticket[6],
                    'priority': ticket[7],
                    'status': ticket[8],
                    'type': ticket[9],
                    'tags': ticket[10],
                    'created_at': created_at,
                    'updated_at': updated_at,
                    'closed_at': closed_at,
                    'requester_name': ticket[14],
                    'requester_avatar': ticket[15],
                    'agent_name': ticket[16],
                    'agent_avatar': ticket[17]
                })
            
            return {
                'tickets': formatted_tickets,
                'total': total_count,
                'page': page,
                'per_page': per_page,
                'total_pages': (total_count + per_page - 1) // per_page
            }
        finally:
            conn.close()
    
    def get_ticket(self, ticket_id: int) -> Optional[Dict]:
        """Get a specific ticket by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT t.*, 
                       r.name as requester_name, r.avatar_url as requester_avatar,
                       a.name as agent_name, a.avatar_url as agent_avatar
                FROM tickets t
                LEFT JOIN users r ON t.requester_id = r.id
                LEFT JOIN users a ON t.agent_id = a.id
                WHERE t.id = ?
            """, (ticket_id,))
            
            ticket = cursor.fetchone()
            if not ticket:
                return None
            
            return {
                'id': ticket[0],
                'ticket_number': ticket[1],
                'subject': ticket[2],
                'description': ticket[3],
                'requester_id': ticket[4],
                'agent_id': ticket[5],
                'follower_id': ticket[6],
                'priority': ticket[7],
                'status': ticket[8],
                'type': ticket[9],
                'tags': ticket[10],
                'created_at': ticket[11],
                'updated_at': ticket[12],
                'closed_at': ticket[13],
                'requester_name': ticket[14],
                'requester_avatar': ticket[15],
                'agent_name': ticket[16],
                'agent_avatar': ticket[17]
            }
        finally:
            conn.close()
    
    def create_ticket(self, ticket_data: Dict) -> Dict:
        """Create a new ticket"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Generate ticket number
            ticket_number = f"#{datetime.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:4]}"
            
            cursor.execute("""
                INSERT INTO tickets (ticket_number, subject, description, requester_id, 
                                   agent_id, priority, status, type, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                ticket_number,
                ticket_data['subject'],
                ticket_data.get('description', ''),
                ticket_data.get('requester_id'),
                ticket_data.get('agent_id'),
                ticket_data.get('priority', 'medium'),
                ticket_data.get('status', 'open'),
                ticket_data.get('type', 'question'),
                ticket_data.get('tags', '')
            ))
            
            ticket_id = cursor.lastrowid
            
            # Log activity
            cursor.execute("""
                INSERT INTO ticket_activity (ticket_id, user_id, action, details)
                VALUES (?, ?, ?, ?)
            """, (ticket_id, ticket_data.get('requester_id'), 'created', 'Ticket created'))
            
            conn.commit()
            
            return self.get_ticket(ticket_id)
        finally:
            conn.close()
    
    def update_ticket(self, ticket_id: int, update_data: Dict) -> Optional[Dict]:
        """Update a ticket"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Build update query dynamically
            update_fields = []
            params = []
            
            for field, value in update_data.items():
                if field in ['subject', 'description', 'agent_id', 'priority', 'status', 'type', 'tags']:
                    update_fields.append(f"{field} = ?")
                    params.append(value)
            
            if not update_fields:
                return self.get_ticket(ticket_id)
            
            update_fields.append("updated_at = ?")
            params.append(datetime.now().isoformat())
            params.append(ticket_id)
            
            query = f"UPDATE tickets SET {', '.join(update_fields)} WHERE id = ?"
            cursor.execute(query, params)
            
            # Log activity
            cursor.execute("""
                INSERT INTO ticket_activity (ticket_id, user_id, action, details)
                VALUES (?, ?, ?, ?)
            """, (ticket_id, update_data.get('user_id'), 'updated', 'Ticket updated'))
            
            conn.commit()
            
            return self.get_ticket(ticket_id)
        finally:
            conn.close()
    
    def close_ticket(self, ticket_id: int, user_id: int, resolution_notes: str = None) -> Optional[Dict]:
        """Close a ticket"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE tickets SET status = 'closed', closed_at = ?, updated_at = ?
                WHERE id = ?
            """, (datetime.now().isoformat(), datetime.now().isoformat(), ticket_id))
            
            # Log activity
            details = 'Ticket closed'
            if resolution_notes:
                details += f': {resolution_notes}'
            
            cursor.execute("""
                INSERT INTO ticket_activity (ticket_id, user_id, action, details)
                VALUES (?, ?, ?, ?)
            """, (ticket_id, user_id, 'closed', details))
            
            conn.commit()
            
            return self.get_ticket(ticket_id)
        finally:
            conn.close()
    
    def get_ticket_messages(self, ticket_id: int) -> List[Dict]:
        """Get messages for a ticket"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT m.*, u.name as sender_name, u.avatar_url as sender_avatar
                FROM ticket_messages m
                LEFT JOIN users u ON m.sender_id = u.id
                WHERE m.ticket_id = ?
                ORDER BY m.created_at ASC
            """, (ticket_id,))
            
            messages = cursor.fetchall()
            
            formatted_messages = []
            for message in messages:
                formatted_messages.append({
                    'id': message[0],
                    'ticket_id': message[1],
                    'sender_id': message[2],
                    'message': message[3],
                    'message_type': message[4],
                    'created_at': message[5],
                    'sender_name': message[6],
                    'sender_avatar': message[7]
                })
            
            return formatted_messages
        finally:
            conn.close()
    
    def add_message(self, ticket_id: int, sender_id: int, message: str, message_type: str = 'public') -> Dict:
        """Add a message to a ticket"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO ticket_messages (ticket_id, sender_id, message, message_type)
                VALUES (?, ?, ?, ?)
            """, (ticket_id, sender_id, message, message_type))
            
            message_id = cursor.lastrowid
            
            # Update ticket updated_at
            cursor.execute("""
                UPDATE tickets SET updated_at = ? WHERE id = ?
            """, (datetime.now().isoformat(), ticket_id))
            
            # Log activity
            cursor.execute("""
                INSERT INTO ticket_activity (ticket_id, user_id, action, details)
                VALUES (?, ?, ?, ?)
            """, (ticket_id, sender_id, 'message_added', 'Message added to ticket'))
            
            conn.commit()
            
            # Return the created message
            cursor.execute("""
                SELECT m.*, u.name as sender_name, u.avatar_url as sender_avatar
                FROM ticket_messages m
                LEFT JOIN users u ON m.sender_id = u.id
                WHERE m.id = ?
            """, (message_id,))
            
            message_data = cursor.fetchone()
            return {
                'id': message_data[0],
                'ticket_id': message_data[1],
                'sender_id': message_data[2],
                'message': message_data[3],
                'message_type': message_data[4],
                'created_at': message_data[5],
                'sender_name': message_data[6],
                'sender_avatar': message_data[7]
            }
        finally:
            conn.close()
    
    def get_users(self, role: str = None) -> List[Dict]:
        """Get users, optionally filtered by role"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            if role:
                cursor.execute("""
                    SELECT id, name, email, role, avatar_url, is_active, created_at
                    FROM users WHERE role = ? AND is_active = 1
                    ORDER BY name
                """, (role,))
            else:
                cursor.execute("""
                    SELECT id, name, email, role, avatar_url, is_active, created_at
                    FROM users WHERE is_active = 1
                    ORDER BY name
                """)
            
            users = cursor.fetchall()
            
            formatted_users = []
            for user in users:
                formatted_users.append({
                    'id': user[0],
                    'name': user[1],
                    'email': user[2],
                    'role': user[3],
                    'avatar_url': user[4],
                    'is_active': user[5],
                    'created_at': user[6]
                })
            
            return formatted_users
        finally:
            conn.close()
    
    def get_agents(self) -> List[Dict]:
        """Get all agents"""
        return self.get_users(role='agent')
    
    def get_ticket_activity(self, ticket_id: int) -> List[Dict]:
        """Get activity log for a ticket"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT a.*, u.name as user_name, u.avatar_url as user_avatar
                FROM ticket_activity a
                LEFT JOIN users u ON a.user_id = u.id
                WHERE a.ticket_id = ?
                ORDER BY a.created_at DESC
            """, (ticket_id,))
            
            activities = cursor.fetchall()
            
            formatted_activities = []
            for activity in activities:
                formatted_activities.append({
                    'id': activity[0],
                    'ticket_id': activity[1],
                    'user_id': activity[2],
                    'action': activity[3],
                    'details': activity[4],
                    'created_at': activity[5],
                    'user_name': activity[6],
                    'user_avatar': activity[7]
                })
            
            return formatted_activities
        finally:
            conn.close()
    
    def search_tickets(self, search_term: str, filters: Dict = None) -> List[Dict]:
        """Search tickets by term and filters"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            query = """
                SELECT t.*, 
                       r.name as requester_name, r.avatar_url as requester_avatar,
                       a.name as agent_name, a.avatar_url as agent_avatar
                FROM tickets t
                LEFT JOIN users r ON t.requester_id = r.id
                LEFT JOIN users a ON t.agent_id = a.id
                WHERE (t.subject LIKE ? OR t.description LIKE ? OR r.name LIKE ? OR t.ticket_number LIKE ?)
            """
            search_pattern = f"%{search_term}%"
            params = [search_pattern, search_pattern, search_pattern, search_pattern]
            
            if filters:
                if filters.get('status'):
                    query += " AND t.status = ?"
                    params.append(filters['status'])
                
                if filters.get('priority'):
                    query += " AND t.priority = ?"
                    params.append(filters['priority'])
            
            query += " ORDER BY t.created_at DESC"
            
            cursor.execute(query, params)
            tickets = cursor.fetchall()
            
            formatted_tickets = []
            for ticket in tickets:
                formatted_tickets.append({
                    'id': ticket[0],
                    'ticket_number': ticket[1],
                    'subject': ticket[2],
                    'description': ticket[3],
                    'requester_id': ticket[4],
                    'agent_id': ticket[5],
                    'follower_id': ticket[6],
                    'priority': ticket[7],
                    'status': ticket[8],
                    'type': ticket[9],
                    'tags': ticket[10],
                    'created_at': ticket[11],
                    'updated_at': ticket[12],
                    'closed_at': ticket[13],
                    'requester_name': ticket[14],
                    'requester_avatar': ticket[15],
                    'agent_name': ticket[16],
                    'agent_avatar': ticket[17]
                })
            
            return formatted_tickets
        finally:
            conn.close()
