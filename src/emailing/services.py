import os
import json
from datetime import datetime
from typing import List, Dict, Optional
from flask import current_app, render_template_string
from sqlalchemy.orm import Session
from src.models.database_models import db
from .models import EmailTemplate, EmailCampaign, EmailRecipient, EmailAttachment, EmailLog

class EmailTemplateManager:
    """Manage email templates"""
    
    def __init__(self):
        self.templates_dir = 'templates/email'
        self.assets_dir = 'static/email'
    
    def create_template(self, name: str, subject: str, content: str, category: str = 'business') -> EmailTemplate:
        """Create new email template"""
        template = EmailTemplate(
            name=name,
            subject=subject,
            content=content,
            category=category
        )
        db.session.add(template)
        db.session.commit()
        return template
    
    def get_template(self, template_id: int) -> Optional[EmailTemplate]:
        """Get template by ID"""
        return EmailTemplate.query.get(template_id)
    
    def get_templates_by_category(self, category: str) -> List[EmailTemplate]:
        """Get templates by category"""
        return EmailTemplate.query.filter_by(category=category, is_active=True).all()
    
    def update_template(self, template_id: int, **kwargs) -> Optional[EmailTemplate]:
        """Update template"""
        template = self.get_template(template_id)
        if template:
            for key, value in kwargs.items():
                if hasattr(template, key):
                    setattr(template, key, value)
            template.updated_at = datetime.utcnow()
            db.session.commit()
        return template
    
    def delete_template(self, template_id: int) -> bool:
        """Delete template"""
        template = self.get_template(template_id)
        if template:
            db.session.delete(template)
            db.session.commit()
            return True
        return False
    
    def preview_template(self, template_id: int, data: Dict = None) -> str:
        """Generate email preview"""
        template = self.get_template(template_id)
        if not template:
            return ""
        
        # Default data
        if data is None:
            data = {
                'recipient_name': 'Test User',
                'company_name': 'ValidoAI',
                'logo_url': '/static/images/logo.png',
                'unsubscribe_url': '#',
                'current_date': datetime.now().strftime('%d.%m.%Y')
            }
        
        # Render template with data
        try:
            return render_template_string(template.content, **data)
        except Exception as e:
            current_app.logger.error(f"Error rendering template: {e}")
            return template.content

class EmailCampaignManager:
    """Manage email campaigns"""
    
    def create_campaign(self, name: str, template_id: int, scheduled_at: datetime = None) -> EmailCampaign:
        """Create new email campaign"""
        campaign = EmailCampaign(
            name=name,
            template_id=template_id,
            scheduled_at=scheduled_at
        )
        db.session.add(campaign)
        db.session.commit()
        return campaign
    
    def get_campaign(self, campaign_id: int) -> Optional[EmailCampaign]:
        """Get campaign by ID"""
        return EmailCampaign.query.get(campaign_id)
    
    def get_campaigns_by_status(self, status: str) -> List[EmailCampaign]:
        """Get campaigns by status"""
        return EmailCampaign.query.filter_by(status=status).all()
    
    def update_campaign_status(self, campaign_id: int, status: str) -> bool:
        """Update campaign status"""
        campaign = self.get_campaign(campaign_id)
        if campaign:
            campaign.status = status
            if status == 'completed':
                campaign.sent_at = datetime.utcnow()
            db.session.commit()
            return True
        return False
    
    def add_recipients(self, campaign_id: int, recipients: List[Dict]) -> bool:
        """Add recipients to campaign"""
        campaign = self.get_campaign(campaign_id)
        if not campaign:
            return False
        
        for recipient_data in recipients:
            recipient = EmailRecipient(
                campaign_id=campaign_id,
                email=recipient_data['email'],
                name=recipient_data.get('name', '')
            )
            db.session.add(recipient)
        
        campaign.total_recipients = len(recipients)
        db.session.commit()
        return True

class EmailSender:
    """Send emails using templates"""
    
    def __init__(self):
        self.template_manager = EmailTemplateManager()
    
    def send_email(self, template_id: int, recipients: List[str], data: Dict = None) -> bool:
        """Send email using template"""
        template = self.template_manager.get_template(template_id)
        if not template:
            return False
        
        # Generate email content
        content = self.template_manager.preview_template(template_id, data)
        
        # Here you would integrate with your email service (SMTP, SendGrid, etc.)
        # For now, we'll just log the email
        current_app.logger.info(f"Sending email to {len(recipients)} recipients")
        current_app.logger.info(f"Subject: {template.subject}")
        current_app.logger.info(f"Content: {content[:200]}...")
        
        return True
    
    def send_campaign(self, campaign_id: int) -> bool:
        """Send email campaign"""
        campaign = EmailCampaign.query.get(campaign_id)
        if not campaign:
            return False
        
        # Get recipients
        recipients = EmailRecipient.query.filter_by(campaign_id=campaign_id).all()
        
        # Send emails
        success_count = 0
        for recipient in recipients:
            if self.send_email(campaign.template_id, [recipient.email]):
                recipient.status = 'sent'
                recipient.sent_at = datetime.utcnow()
                success_count += 1
        
        # Update campaign statistics
        campaign.sent_count = success_count
        campaign.status = 'completed'
        campaign.sent_at = datetime.utcnow()
        
        db.session.commit()
        return True

class WYSIWYGEditor:
    """WYSIWYG editor for email templates"""
    
    def __init__(self):
        self.editor_config = {
            'height': 400,
            'plugins': ['link', 'image', 'table', 'lists', 'code'],
            'toolbar': 'formatselect | bold italic underline | alignleft aligncenter alignright | bullist numlist | link image table | code',
            'content_css': '/static/css/email-editor.css',
            'images_upload_url': '/emailing/upload-image',
            'file_picker_types': 'image',
            'relative_urls': False,
            'remove_script_host': False,
            'convert_urls': True
        }
    
    def get_editor_config(self) -> Dict:
        """Get editor configuration"""
        return self.editor_config
    
    def render_editor(self, element_id: str, content: str = '') -> str:
        """Generate editor HTML"""
        config_json = json.dumps(self.editor_config)
        return f"""
        <div class="email-editor">
            <div class="editor-toolbar">
                <button class="btn btn-sm btn-outline-secondary" data-command="bold" title="Bold">
                    <i class="bi bi-type-bold"></i>
                </button>
                <button class="btn btn-sm btn-outline-secondary" data-command="italic" title="Italic">
                    <i class="bi bi-type-italic"></i>
                </button>
                <button class="btn btn-sm btn-outline-secondary" data-command="underline" title="Underline">
                    <i class="bi bi-type-underline"></i>
                </button>
                <div class="btn-group" role="group">
                    <button class="btn btn-sm btn-outline-secondary" data-command="alignleft" title="Align Left">
                        <i class="bi bi-text-left"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-secondary" data-command="aligncenter" title="Align Center">
                        <i class="bi bi-text-center"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-secondary" data-command="alignright" title="Align Right">
                        <i class="bi bi-text-right"></i>
                    </button>
                </div>
                <button class="btn btn-sm btn-outline-secondary" data-command="insertUnorderedList" title="Bullet List">
                    <i class="bi bi-list-ul"></i>
                </button>
                <button class="btn btn-sm btn-outline-secondary" data-command="insertOrderedList" title="Numbered List">
                    <i class="bi bi-list-ol"></i>
                </button>
                <button class="btn btn-sm btn-outline-secondary" data-command="createLink" title="Insert Link">
                    <i class="bi bi-link-45deg"></i>
                </button>
                <button class="btn btn-sm btn-outline-secondary" data-command="insertImage" title="Insert Image">
                    <i class="bi bi-image"></i>
                </button>
                <button class="btn btn-sm btn-outline-secondary" data-command="insertTable" title="Insert Table">
                    <i class="bi bi-table"></i>
                </button>
            </div>
            <div id="{element_id}" class="editor-content" contenteditable="true">
                {content}
            </div>
        </div>
        <script>
            // Initialize WYSIWYG editor
            document.addEventListener('DOMContentLoaded', function() {{
                const editor = document.getElementById('{element_id}');
                const toolbar = editor.parentElement.querySelector('.editor-toolbar');
                
                // Toolbar functionality
                toolbar.addEventListener('click', function(e) {{
                    if (e.target.closest('button')) {{
                        e.preventDefault();
                        const button = e.target.closest('button');
                        const command = button.dataset.command;
                        
                        if (command === 'createLink') {{
                            const url = prompt('Enter URL:');
                            if (url) {{
                                document.execCommand(command, false, url);
                            }}
                        }} else if (command === 'insertImage') {{
                            const url = prompt('Enter image URL:');
                            if (url) {{
                                document.execCommand(command, false, url);
                            }}
                        }} else {{
                            document.execCommand(command, false, null);
                        }}
                        
                        editor.focus();
                    }}
                }});
                
                // Auto-save functionality
                let saveTimeout;
                editor.addEventListener('input', function() {{
                    clearTimeout(saveTimeout);
                    saveTimeout = setTimeout(function() {{
                        // Auto-save content
                        const content = editor.innerHTML;
                        localStorage.setItem('email_editor_draft', content);
                    }}, 1000);
                }});
                
                // Load draft if exists
                const draft = localStorage.getItem('email_editor_draft');
                if (draft && !editor.innerHTML.trim()) {{
                    editor.innerHTML = draft;
                }}
            }});
        </script>
        """
    
    def get_content(self, element_id: str) -> str:
        """Get editor content (this would be called via JavaScript)"""
        # In a real implementation, this would be called via AJAX
        return f"document.getElementById('{element_id}').innerHTML"

