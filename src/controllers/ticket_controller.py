#!/usr/bin/env python3
"""
Ticket Controller
Handles all ticket-related HTTP requests and responses
"""

from flask import jsonify, request, render_template
from src.services.ticket_service import TicketService
from datetime import datetime

class TicketController:
    def __init__(self):
        self.ticket_service = TicketService()
    
    def tickets_page(self):
        """Render the main tickets page"""
        try:
            # Get ticket statistics for the dashboard
            stats = self.ticket_service.get_ticket_statistics()
            
            # Get recent tickets for the table
            tickets_data = self.ticket_service.get_tickets(page=1, per_page=10)
            tickets = tickets_data.get('tickets', []) if tickets_data else []
            
            # Get agents for the create ticket form
            agents = self.ticket_service.get_agents()
            
            return render_template('tickets/index.html', 
                                 stats=stats, 
                                 tickets=tickets,
                                 agents=agents)
        except Exception as e:
            return jsonify({
                'error': 'Failed to load tickets page',
                'details': str(e)
            }), 500
    
    def create_ticket(self):
        """Handle ticket creation"""
        try:
            if request.method == 'GET':
                # Return the create ticket form
                agents = self.ticket_service.get_agents()
                users = self.ticket_service.get_users()
                return render_template('tickets/create.html', agents=agents, users=users)
            
            elif request.method == 'POST':
                # Handle ticket creation
                data = request.get_json() if request.is_json else request.form.to_dict()
                
                # Validate required fields
                required_fields = ['subject', 'requester_id']
                for field in required_fields:
                    if not data.get(field):
                        return jsonify({
                            'error': f'Missing required field: {field}'
                        }), 400
                
                # Create the ticket
                ticket = self.ticket_service.create_ticket(data)
                
                return jsonify({
                    'success': True,
                    'message': 'Ticket created successfully',
                    'ticket': ticket
                }), 201
                
        except Exception as e:
            return jsonify({
                'error': 'Failed to create ticket',
                'details': str(e)
            }), 500
    
    def view_ticket(self, ticket_id):
        """View a specific ticket"""
        try:
            # Get ticket details
            ticket = self.ticket_service.get_ticket(ticket_id)
            if not ticket:
                return jsonify({
                    'error': 'Ticket not found'
                }), 404
            
            # Get ticket messages
            messages = self.ticket_service.get_ticket_messages(ticket_id)
            
            # Get ticket activity
            activity = self.ticket_service.get_ticket_activity(ticket_id)
            
            # Get agents for assignment
            agents = self.ticket_service.get_agents()
            
            return render_template('tickets/detail.html',
                                 ticket=ticket,
                                 messages=messages,
                                 activity=activity,
                                 agents=agents)
                                 
        except Exception as e:
            return jsonify({
                'error': 'Failed to load ticket',
                'details': str(e)
            }), 500
    
    def update_ticket(self, ticket_id):
        """Update a ticket"""
        try:
            data = request.get_json() if request.is_json else request.form.to_dict()
            
            # Add user_id for activity logging (in real app, get from session)
            data['user_id'] = data.get('user_id', 1)  # Default to user ID 1 for now
            
            # Update the ticket
            ticket = self.ticket_service.update_ticket(ticket_id, data)
            
            if not ticket:
                return jsonify({
                    'error': 'Ticket not found'
                }), 404
            
            return jsonify({
                'success': True,
                'message': 'Ticket updated successfully',
                'ticket': ticket
            })
            
        except Exception as e:
            return jsonify({
                'error': 'Failed to update ticket',
                'details': str(e)
            }), 500
    
    def close_ticket(self, ticket_id):
        """Close a ticket"""
        try:
            data = request.get_json() if request.is_json else request.form.to_dict()
            
            # Get user_id and resolution notes
            user_id = data.get('user_id', 1)  # Default to user ID 1 for now
            resolution_notes = data.get('resolution_notes')
            
            # Close the ticket
            ticket = self.ticket_service.close_ticket(ticket_id, user_id, resolution_notes)
            
            if not ticket:
                return jsonify({
                    'error': 'Ticket not found'
                }), 404
            
            return jsonify({
                'success': True,
                'message': 'Ticket closed successfully',
                'ticket': ticket
            })
            
        except Exception as e:
            return jsonify({
                'error': 'Failed to close ticket',
                'details': str(e)
            }), 500
    
    def list_tickets(self):
        """List tickets with filtering and pagination"""
        try:
            # Get query parameters
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 20))
            status = request.args.get('status')
            priority = request.args.get('priority')
            search = request.args.get('search')
            
            # Build filters
            filters = {}
            if status:
                filters['status'] = status
            if priority:
                filters['priority'] = priority
            if search:
                filters['search'] = search
            
            # Get tickets
            tickets_data = self.ticket_service.get_tickets(filters=filters, page=page, per_page=per_page)
            
            return jsonify({
                'success': True,
                'data': tickets_data
            })
            
        except Exception as e:
            return jsonify({
                'error': 'Failed to list tickets',
                'details': str(e)
            }), 500
    
    def get_ticket_messages(self, ticket_id):
        """Get messages for a ticket"""
        try:
            messages = self.ticket_service.get_ticket_messages(ticket_id)
            
            return jsonify({
                'success': True,
                'messages': messages
            })
            
        except Exception as e:
            return jsonify({
                'error': 'Failed to get messages',
                'details': str(e)
            }), 500
    
    def add_message(self, ticket_id):
        """Add a message to a ticket"""
        try:
            data = request.get_json() if request.is_json else request.form.to_dict()
            
            # Validate required fields
            if not data.get('message'):
                return jsonify({
                    'error': 'Message is required'
                }), 400
            
            # Get sender_id (in real app, get from session)
            sender_id = data.get('sender_id', 1)  # Default to user ID 1 for now
            message = data['message']
            message_type = data.get('message_type', 'public')
            
            # Add the message
            new_message = self.ticket_service.add_message(ticket_id, sender_id, message, message_type)
            
            return jsonify({
                'success': True,
                'message': 'Message added successfully',
                'data': new_message
            })
            
        except Exception as e:
            return jsonify({
                'error': 'Failed to add message',
                'details': str(e)
            }), 500
    
    def get_ticket_statistics(self):
        """Get ticket statistics"""
        try:
            stats = self.ticket_service.get_ticket_statistics()
            
            return jsonify({
                'success': True,
                'statistics': stats
            })
            
        except Exception as e:
            return jsonify({
                'error': 'Failed to get statistics',
                'details': str(e)
            }), 500
    
    def search_tickets(self):
        """Search tickets"""
        try:
            search_term = request.args.get('q', '')
            if not search_term:
                return jsonify({
                    'error': 'Search term is required'
                }), 400
            
            # Get additional filters
            status = request.args.get('status')
            priority = request.args.get('priority')
            
            filters = {}
            if status:
                filters['status'] = status
            if priority:
                filters['priority'] = priority
            
            # Search tickets
            tickets = self.ticket_service.search_tickets(search_term, filters)
            
            return jsonify({
                'success': True,
                'tickets': tickets,
                'search_term': search_term,
                'total': len(tickets)
            })
            
        except Exception as e:
            return jsonify({
                'error': 'Failed to search tickets',
                'details': str(e)
            }), 500
    
    def get_agents(self):
        """Get all agents"""
        try:
            agents = self.ticket_service.get_agents()
            
            return jsonify({
                'success': True,
                'agents': agents
            })
            
        except Exception as e:
            return jsonify({
                'error': 'Failed to get agents',
                'details': str(e)
            }), 500
    
    def get_users(self):
        """Get all users"""
        try:
            users = self.ticket_service.get_users()
            
            return jsonify({
                'success': True,
                'users': users
            })
            
        except Exception as e:
            return jsonify({
                'error': 'Failed to get users',
                'details': str(e)
            }), 500
