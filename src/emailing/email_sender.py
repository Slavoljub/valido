import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Dict, Optional
from datetime import datetime
import os
from flask import current_app
from src.models.database_models import db
from .models import EmailTemplate, EmailCampaign, EmailRecipient, EmailLog

class EmailSender:
    """Real email sender with SMTP integration"""
    
    def __init__(self):
        self.smtp_config = self.get_smtp_config()
        self.sender_email = os.getenv('SMTP_SENDER_EMAIL', 'noreply@validoai.com')
        self.sender_name = os.getenv('SMTP_SENDER_NAME', 'ValidoAI')
    
    def get_smtp_config(self) -> Dict:
        """Get SMTP configuration from environment variables"""
        return {
            'host': os.getenv('SMTP_HOST', 'smtp.gmail.com'),
            'port': int(os.getenv('SMTP_PORT', '587')),
            'username': os.getenv('SMTP_USERNAME', ''),
            'password': os.getenv('SMTP_PASSWORD', ''),
            'use_tls': os.getenv('SMTP_USE_TLS', 'true').lower() == 'true',
            'use_ssl': os.getenv('SMTP_USE_SSL', 'false').lower() == 'true'
        }
    
    def send_email(self, template_id: int, recipients: List[str], data: Dict = None, attachments: List[str] = None) -> bool:
        """Send email using template"""
        try:
            # Get template
            template = EmailTemplate.query.get(template_id)
            if not template:
                current_app.logger.error(f"Template {template_id} not found")
                return False
            
            # Generate email content
            content = self.render_template(template.content, data or {})
            
            # Send to each recipient
            success_count = 0
            for recipient_email in recipients:
                if self.send_single_email(recipient_email, template.subject, content, attachments):
                    success_count += 1
                    self.log_email_sent(template_id, recipient_email, 'sent')
                else:
                    self.log_email_sent(template_id, recipient_email, 'failed')
            
            current_app.logger.info(f"Sent {success_count}/{len(recipients)} emails successfully")
            return success_count > 0
            
        except Exception as e:
            current_app.logger.error(f"Error sending email: {e}")
            return False
    
    def send_single_email(self, recipient_email: str, subject: str, content: str, attachments: List[str] = None) -> bool:
        """Send single email to recipient"""
        try:
            # Create message
            message = MIMEMultipart('alternative')
            message['From'] = f"{self.sender_name} <{self.sender_email}>"
            message['To'] = recipient_email
            message['Subject'] = subject
            
            # Add HTML content
            html_part = MIMEText(content, 'html')
            message.attach(html_part)
            
            # Add attachments
            if attachments:
                for attachment_path in attachments:
                    if os.path.exists(attachment_path):
                        self.add_attachment(message, attachment_path)
            
            # Send email
            return self.send_via_smtp(message)
            
        except Exception as e:
            current_app.logger.error(f"Error sending email to {recipient_email}: {e}")
            return False
    
    def send_via_smtp(self, message: MIMEMultipart) -> bool:
        """Send email via SMTP"""
        try:
            if self.smtp_config['use_ssl']:
                server = smtplib.SMTP_SSL(self.smtp_config['host'], self.smtp_config['port'])
            else:
                server = smtplib.SMTP(self.smtp_config['host'], self.smtp_config['port'])
                if self.smtp_config['use_tls']:
                    server.starttls(context=ssl.create_default_context())
            
            # Login if credentials provided
            if self.smtp_config['username'] and self.smtp_config['password']:
                server.login(self.smtp_config['username'], self.smtp_config['password'])
            
            # Send email
            server.send_message(message)
            server.quit()
            
            return True
            
        except Exception as e:
            current_app.logger.error(f"SMTP error: {e}")
            return False
    
    def add_attachment(self, message: MIMEMultipart, file_path: str):
        """Add attachment to email"""
        try:
            with open(file_path, "rb") as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {os.path.basename(file_path)}'
            )
            message.attach(part)
            
        except Exception as e:
            current_app.logger.error(f"Error adding attachment {file_path}: {e}")
    
    def render_template(self, template_content: str, data: Dict) -> str:
        """Render email template with data"""
        try:
            # Add default data
            default_data = {
                'company_name': 'ValidoAI',
                'logo_url': '/static/images/logo.png',
                'unsubscribe_url': '#',
                'current_date': datetime.now().strftime('%d.%m.%Y'),
                'year': datetime.now().year
            }
            
            # Merge with provided data
            render_data = {**default_data, **data}
            
            # Simple template rendering (replace placeholders)
            content = template_content
            for key, value in render_data.items():
                placeholder = f'{{{{ {key} }}}}'
                content = content.replace(placeholder, str(value))
            
            return content
            
        except Exception as e:
            current_app.logger.error(f"Error rendering template: {e}")
            return template_content
    
    def log_email_sent(self, template_id: int, recipient_email: str, status: str):
        """Log email sending activity"""
        try:
            log = EmailLog(
                campaign_id=None,  # Will be set when campaign is created
                recipient_id=None,  # Will be set when recipient is created
                action=status,
                timestamp=datetime.utcnow(),
                details=f"Template {template_id} sent to {recipient_email}"
            )
            db.session.add(log)
            db.session.commit()
            
        except Exception as e:
            current_app.logger.error(f"Error logging email: {e}")
    
    def send_campaign(self, campaign_id: int) -> bool:
        """Send email campaign"""
        try:
            campaign = EmailCampaign.query.get(campaign_id)
            if not campaign:
                current_app.logger.error(f"Campaign {campaign_id} not found")
                return False
            
            # Get recipients
            recipients = EmailRecipient.query.filter_by(campaign_id=campaign_id).all()
            
            # Update campaign status
            campaign.status = 'sending'
            db.session.commit()
            
            # Send emails
            success_count = 0
            for recipient in recipients:
                if self.send_single_email(recipient.email, campaign.template.subject, campaign.template.content):
                    recipient.status = 'sent'
                    recipient.sent_at = datetime.utcnow()
                    success_count += 1
                else:
                    recipient.status = 'failed'
                
                db.session.commit()
            
            # Update campaign statistics
            campaign.sent_count = success_count
            campaign.status = 'completed'
            campaign.sent_at = datetime.utcnow()
            db.session.commit()
            
            current_app.logger.info(f"Campaign {campaign_id} completed: {success_count}/{len(recipients)} sent")
            return True
            
        except Exception as e:
            current_app.logger.error(f"Error sending campaign {campaign_id}: {e}")
            return False

class EmailTemplateRenderer:
    """Advanced email template renderer with dynamic content"""
    
    def __init__(self):
        self.default_templates = {
            'newsletter': self.get_newsletter_template(),
            'promotion': self.get_promotion_template(),
            'notification': self.get_notification_template(),
            'welcome': self.get_welcome_template()
        }
    
    def get_newsletter_template(self) -> str:
        """Get newsletter template"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{{ subject }}</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; text-align: center; border-radius: 10px 10px 0 0;">
                <img src="{{ logo_url }}" alt="{{ company_name }}" style="max-width: 200px; height: auto;">
                <h1 style="color: white; margin: 10px 0;">{{ company_name }}</h1>
            </div>
            
            <div style="background: white; padding: 30px; border-radius: 0 0 10px 10px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                <h2 style="color: #2d3748; margin-bottom: 20px;">{{ title }}</h2>
                
                <div style="margin-bottom: 30px;">
                    {{ content }}
                </div>
                
                <div style="background: #f7fafc; padding: 20px; border-radius: 8px; margin: 30px 0;">
                    <h3 style="color: #4a5568; margin-top: 0;">Ključne informacije</h3>
                    <ul style="color: #2d3748;">
                        <li>Datum: {{ current_date }}</li>
                        <li>Godina: {{ year }}</li>
                        <li>Kontakt: info@validoai.com</li>
                    </ul>
                </div>
                
                <div style="text-align: center; margin-top: 30px;">
                    <a href="{{ cta_url }}" style="background: #4299e1; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">{{ cta_text }}</a>
                </div>
            </div>
            
            <div style="text-align: center; margin-top: 20px; color: #718096; font-size: 14px;">
                <p>© {{ year }} {{ company_name }}. Sva prava zadržana.</p>
                <p><a href="{{ unsubscribe_url }}" style="color: #4299e1;">Odjavi se</a></p>
            </div>
        </body>
        </html>
        """
    
    def get_promotion_template(self) -> str:
        """Get promotion template"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{{ subject }}</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 20px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="color: white; margin: 0; font-size: 28px;">🔥 Specijalna ponuda!</h1>
                <p style="color: white; margin: 10px 0; font-size: 18px;">{{ discount_text }}</p>
            </div>
            
            <div style="background: white; padding: 30px; border-radius: 0 0 10px 10px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                <h2 style="color: #2d3748; margin-bottom: 20px;">{{ title }}</h2>
                
                <div style="margin-bottom: 30px;">
                    {{ content }}
                </div>
                
                <div style="background: #fed7d7; border: 2px solid #f56565; padding: 20px; border-radius: 8px; margin: 30px 0; text-align: center;">
                    <h3 style="color: #c53030; margin-top: 0;">Posebna cena: {{ special_price }}</h3>
                    <p style="color: #2d3748; margin-bottom: 0;">Ova ponuda važi do {{ valid_until }}</p>
                </div>
                
                <div style="text-align: center; margin-top: 30px;">
                    <a href="{{ cta_url }}" style="background: #e53e3e; color: white; padding: 15px 40px; text-decoration: none; border-radius: 5px; display: inline-block; font-size: 18px; font-weight: bold;">{{ cta_text }}</a>
                </div>
            </div>
            
            <div style="text-align: center; margin-top: 20px; color: #718096; font-size: 14px;">
                <p>© {{ year }} {{ company_name }}. Sva prava zadržana.</p>
                <p><a href="{{ unsubscribe_url }}" style="color: #4299e1;">Odjavi se</a></p>
            </div>
        </body>
        </html>
        """
    
    def get_notification_template(self) -> str:
        """Get notification template"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{{ subject }}</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); padding: 20px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="color: white; margin: 0; font-size: 24px;">🔔 Obaveštenje</h1>
            </div>
            
            <div style="background: white; padding: 30px; border-radius: 0 0 10px 10px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                <h2 style="color: #2d3748; margin-bottom: 20px;">{{ title }}</h2>
                
                <div style="margin-bottom: 30px;">
                    {{ content }}
                </div>
                
                <div style="background: #ebf8ff; border-left: 4px solid #4299e1; padding: 20px; margin: 30px 0;">
                    <h3 style="color: #2b6cb0; margin-top: 0;">Važne informacije:</h3>
                    <ul style="color: #2d3748;">
                        <li>Datum: {{ current_date }}</li>
                        <li>Vreme: {{ notification_time }}</li>
                        <li>Prioritet: {{ priority }}</li>
                    </ul>
                </div>
                
                <div style="text-align: center; margin-top: 30px;">
                    <a href="{{ cta_url }}" style="background: #4299e1; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">{{ cta_text }}</a>
                </div>
            </div>
            
            <div style="text-align: center; margin-top: 20px; color: #718096; font-size: 14px;">
                <p>© {{ year }} {{ company_name }}. Sva prava zadržana.</p>
                <p><a href="{{ unsubscribe_url }}" style="color: #4299e1;">Odjavi se</a></p>
            </div>
        </body>
        </html>
        """
    
    def get_welcome_template(self) -> str:
        """Get welcome template"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{{ subject }}</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); padding: 20px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="color: #2d3748; margin: 0; font-size: 28px;">🎉 Dobrodošli!</h1>
                <p style="color: #4a5568; margin: 10px 0; font-size: 18px;">Drago nam je što ste se pridružili {{ company_name }}</p>
            </div>
            
            <div style="background: white; padding: 30px; border-radius: 0 0 10px 10px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                <h2 style="color: #2d3748; margin-bottom: 20px;">Zdravo {{ recipient_name }}!</h2>
                
                <div style="margin-bottom: 30px;">
                    {{ content }}
                </div>
                
                <div style="background: #f0fff4; border: 2px solid #68d391; padding: 20px; border-radius: 8px; margin: 30px 0;">
                    <h3 style="color: #38a169; margin-top: 0;">Vaš nalog je uspešno kreiran!</h3>
                    <p style="color: #2d3748; margin-bottom: 0;">Možete početi sa korišćenjem naših usluga odmah.</p>
                </div>
                
                <div style="text-align: center; margin-top: 30px;">
                    <a href="{{ cta_url }}" style="background: #48bb78; color: white; padding: 15px 40px; text-decoration: none; border-radius: 5px; display: inline-block; font-size: 18px; font-weight: bold;">{{ cta_text }}</a>
                </div>
            </div>
            
            <div style="text-align: center; margin-top: 20px; color: #718096; font-size: 14px;">
                <p>© {{ year }} {{ company_name }}. Sva prava zadržana.</p>
                <p><a href="{{ unsubscribe_url }}" style="color: #4299e1;">Odjavi se</a></p>
            </div>
        </body>
        </html>
        """
