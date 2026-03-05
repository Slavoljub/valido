"""
Ticket Email Service
Handles all email functionality for the ticketing system
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class TicketEmailService:
    """Email service for ticket notifications and communications"""
    
    def __init__(self):
        """Initialize email service with configuration"""
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_username = os.getenv('SMTP_USERNAME', 'support@valido.online')
        self.smtp_password = os.getenv('SMTP_PASSWORD', '')
        self.support_email = 'support@valido.online'
        self.from_name = 'ValidoAI Support'
        
    def send_ticket_created_notification(self, ticket_data: Dict[str, Any]) -> bool:
        """Send notification when a new ticket is created"""
        try:
            subject = f"New Ticket Created - #{ticket_data['id']}"
            
            # Email to requester
            requester_email = ticket_data.get('requester_email')
            if requester_email:
                self._send_email(
                    to_email=requester_email,
                    subject=subject,
                    template='ticket_created_requester',
                    context=ticket_data
                )
            
            # Email to assigned agent
            agent_email = ticket_data.get('agent_email')
            if agent_email:
                self._send_email(
                    to_email=agent_email,
                    subject=subject,
                    template='ticket_created_agent',
                    context=ticket_data
                )
            
            # Email to support team
            self._send_email(
                to_email=self.support_email,
                subject=subject,
                template='ticket_created_support',
                context=ticket_data
            )
            
            logger.info(f"Ticket created notifications sent for ticket #{ticket_data['id']}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send ticket created notification: {e}")
            return False
    
    def send_ticket_reply_notification(self, ticket_data: Dict[str, Any], reply_data: Dict[str, Any]) -> bool:
        """Send notification when a reply is added to a ticket"""
        try:
            subject = f"New Reply - Ticket #{ticket_data['id']}"
            
            # Email to requester if reply is from agent
            if reply_data.get('sender_type') == 'agent':
                requester_email = ticket_data.get('requester_email')
                if requester_email:
                    self._send_email(
                        to_email=requester_email,
                        subject=subject,
                        template='ticket_reply_requester',
                        context={**ticket_data, **reply_data}
                    )
            
            # Email to agent if reply is from requester
            elif reply_data.get('sender_type') == 'requester':
                agent_email = ticket_data.get('agent_email')
                if agent_email:
                    self._send_email(
                        to_email=agent_email,
                        subject=subject,
                        template='ticket_reply_agent',
                        context={**ticket_data, **reply_data}
                    )
            
            logger.info(f"Ticket reply notification sent for ticket #{ticket_data['id']}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send ticket reply notification: {e}")
            return False
    
    def send_ticket_status_update(self, ticket_data: Dict[str, Any], old_status: str, new_status: str) -> bool:
        """Send notification when ticket status is updated"""
        try:
            subject = f"Ticket Status Updated - #{ticket_data['id']} - {new_status}"
            
            # Email to requester
            requester_email = ticket_data.get('requester_email')
            if requester_email:
                self._send_email(
                    to_email=requester_email,
                    subject=subject,
                    template='ticket_status_update',
                    context={**ticket_data, 'old_status': old_status, 'new_status': new_status}
                )
            
            logger.info(f"Ticket status update notification sent for ticket #{ticket_data['id']}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send ticket status update notification: {e}")
            return False
    
    def send_internal_email(self, from_user: str, to_emails: List[str], subject: str, message: str, 
                          attachments: Optional[List[str]] = None) -> bool:
        """Send email from internal users to other users"""
        try:
            msg = MIMEMultipart()
            msg['From'] = f"{from_user} <{self.smtp_username}>"
            msg['To'] = ', '.join(to_emails)
            msg['Subject'] = subject
            
            # Add message body
            msg.attach(MIMEText(message, 'html'))
            
            # Add attachments if any
            if attachments:
                for filepath in attachments:
                    if os.path.exists(filepath):
                        with open(filepath, "rb") as attachment:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(attachment.read())
                        
                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename= {os.path.basename(filepath)}'
                        )
                        msg.attach(part)
            
            # Send email
            self._send_raw_email(msg, to_emails)
            
            logger.info(f"Internal email sent from {from_user} to {to_emails}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send internal email: {e}")
            return False
    
    def send_support_email(self, from_email: str, from_name: str, subject: str, message: str,
                          ticket_id: Optional[str] = None) -> bool:
        """Send email to support team"""
        try:
            msg = MIMEMultipart()
            msg['From'] = f"{from_name} <{from_email}>"
            msg['To'] = self.support_email
            msg['Subject'] = f"Support Request: {subject}"
            
            # Add ticket ID to subject if provided
            if ticket_id:
                msg['Subject'] = f"Support Request: {subject} (Ticket #{ticket_id})"
            
            # Format message
            formatted_message = f"""
            <h3>Support Request</h3>
            <p><strong>From:</strong> {from_name} ({from_email})</p>
            <p><strong>Subject:</strong> {subject}</p>
            <p><strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <hr>
            <div>{message}</div>
            """
            
            msg.attach(MIMEText(formatted_message, 'html'))
            
            # Send email
            self._send_raw_email(msg, [self.support_email])
            
            logger.info(f"Support email sent from {from_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send support email: {e}")
            return False
    
    def _send_email(self, to_email: str, subject: str, template: str, context: Dict[str, Any]) -> bool:
        """Send email using template"""
        try:
            msg = MIMEMultipart()
            msg['From'] = f"{self.from_name} <{self.smtp_username}>"
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Get email template
            email_content = self._get_email_template(template, context)
            msg.attach(MIMEText(email_content, 'html'))
            
            # Send email
            self._send_raw_email(msg, [to_email])
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
    
    def _send_raw_email(self, msg: MIMEMultipart, to_emails: List[str]) -> bool:
        """Send raw email message"""
        try:
            context = ssl.create_default_context()
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg, from_addr=self.smtp_username, to_addrs=to_emails)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send raw email: {e}")
            return False
    
    def _get_email_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """Get email template content"""
        templates = {
            'ticket_created_requester': self._ticket_created_requester_template,
            'ticket_created_agent': self._ticket_created_agent_template,
            'ticket_created_support': self._ticket_created_support_template,
            'ticket_reply_requester': self._ticket_reply_requester_template,
            'ticket_reply_agent': self._ticket_reply_agent_template,
            'ticket_status_update': self._ticket_status_update_template,
        }
        
        template_func = templates.get(template_name)
        if template_func:
            return template_func(context)
        else:
            return f"<p>Email content for {template_name}</p>"
    
    def _ticket_created_requester_template(self, context: Dict[str, Any]) -> str:
        """Template for ticket created notification to requester"""
        return f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #3B82F6;">Ticket Created Successfully</h2>
            <p>Dear {context.get('requester_name', 'User')},</p>
            <p>Your support ticket has been created successfully.</p>
            
            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <h3>Ticket Details:</h3>
                <p><strong>Ticket ID:</strong> #{context.get('id')}</p>
                <p><strong>Subject:</strong> {context.get('subject')}</p>
                <p><strong>Priority:</strong> {context.get('priority')}</p>
                <p><strong>Status:</strong> {context.get('status')}</p>
                <p><strong>Assigned Agent:</strong> {context.get('agent_name')}</p>
            </div>
            
            <p>We will review your request and get back to you as soon as possible.</p>
            <p>Best regards,<br>ValidoAI Support Team</p>
        </div>
        """
    
    def _ticket_created_agent_template(self, context: Dict[str, Any]) -> str:
        """Template for ticket created notification to agent"""
        return f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #3B82F6;">New Ticket Assigned</h2>
            <p>Dear {context.get('agent_name', 'Agent')},</p>
            <p>A new support ticket has been assigned to you.</p>
            
            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <h3>Ticket Details:</h3>
                <p><strong>Ticket ID:</strong> #{context.get('id')}</p>
                <p><strong>Requester:</strong> {context.get('requester_name')}</p>
                <p><strong>Subject:</strong> {context.get('subject')}</p>
                <p><strong>Priority:</strong> {context.get('priority')}</p>
                <p><strong>Message:</strong> {context.get('message', '')[:200]}...</p>
            </div>
            
            <p>Please review and respond to this ticket as soon as possible.</p>
            <p>Best regards,<br>ValidoAI Support Team</p>
        </div>
        """
    
    def _ticket_created_support_template(self, context: Dict[str, Any]) -> str:
        """Template for ticket created notification to support team"""
        return f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #3B82F6;">New Support Ticket</h2>
            <p>A new support ticket has been created in the system.</p>
            
            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <h3>Ticket Details:</h3>
                <p><strong>Ticket ID:</strong> #{context.get('id')}</p>
                <p><strong>Requester:</strong> {context.get('requester_name')}</p>
                <p><strong>Subject:</strong> {context.get('subject')}</p>
                <p><strong>Priority:</strong> {context.get('priority')}</p>
                <p><strong>Assigned Agent:</strong> {context.get('agent_name')}</p>
                <p><strong>Created:</strong> {context.get('created_at', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}</p>
            </div>
            
            <p>Please monitor this ticket and ensure timely resolution.</p>
        </div>
        """
    
    def _ticket_reply_requester_template(self, context: Dict[str, Any]) -> str:
        """Template for ticket reply notification to requester"""
        return f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #3B82F6;">New Reply to Your Ticket</h2>
            <p>Dear {context.get('requester_name', 'User')},</p>
            <p>You have received a new reply to your support ticket.</p>
            
            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <h3>Ticket Details:</h3>
                <p><strong>Ticket ID:</strong> #{context.get('id')}</p>
                <p><strong>Subject:</strong> {context.get('subject')}</p>
                <p><strong>From:</strong> {context.get('agent_name')}</p>
                <p><strong>Reply:</strong></p>
                <div style="background-color: white; padding: 10px; border-left: 3px solid #3B82F6;">
                    {context.get('reply_message', '')}
                </div>
            </div>
            
            <p>You can view the full conversation and reply directly from your ticket dashboard.</p>
            <p>Best regards,<br>ValidoAI Support Team</p>
        </div>
        """
    
    def _ticket_reply_agent_template(self, context: Dict[str, Any]) -> str:
        """Template for ticket reply notification to agent"""
        return f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #3B82F6;">New Reply from Requester</h2>
            <p>Dear {context.get('agent_name', 'Agent')},</p>
            <p>The requester has added a new reply to the ticket assigned to you.</p>
            
            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <h3>Ticket Details:</h3>
                <p><strong>Ticket ID:</strong> #{context.get('id')}</p>
                <p><strong>Subject:</strong> {context.get('subject')}</p>
                <p><strong>Requester:</strong> {context.get('requester_name')}</p>
                <p><strong>New Reply:</strong></p>
                <div style="background-color: white; padding: 10px; border-left: 3px solid #3B82F6;">
                    {context.get('reply_message', '')}
                </div>
            </div>
            
            <p>Please review and respond to this reply as soon as possible.</p>
            <p>Best regards,<br>ValidoAI Support Team</p>
        </div>
        """
    
    def _ticket_status_update_template(self, context: Dict[str, Any]) -> str:
        """Template for ticket status update notification"""
        return f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #3B82F6;">Ticket Status Updated</h2>
            <p>Dear {context.get('requester_name', 'User')},</p>
            <p>The status of your support ticket has been updated.</p>
            
            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <h3>Ticket Details:</h3>
                <p><strong>Ticket ID:</strong> #{context.get('id')}</p>
                <p><strong>Subject:</strong> {context.get('subject')}</p>
                <p><strong>Previous Status:</strong> {context.get('old_status')}</p>
                <p><strong>New Status:</strong> <span style="color: #10B981; font-weight: bold;">{context.get('new_status')}</span></p>
            </div>
            
            <p>We will continue to work on resolving your issue.</p>
            <p>Best regards,<br>ValidoAI Support Team</p>
        </div>
        """
