#!/usr/bin/env python3
"""
Create Sample Notifications Script
Adds sample notifications to test the notification system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.notification_service import notification_service
from datetime import datetime, timedelta
import random

def create_sample_notifications():
    """Create sample notifications for testing"""
    
    # Sample notification data
    sample_notifications = [
        # Success notifications
        {
            'title': 'Login Successful',
            'message': 'You have successfully logged into ValidoAI system.',
            'type': 'success',
            'priority': 'normal',
            'icon': 'fas fa-sign-in-alt'
        },
        {
            'title': 'Data Export Complete',
            'message': 'Financial report has been exported successfully to PDF format.',
            'type': 'success',
            'priority': 'normal',
            'icon': 'fas fa-file-export'
        },
        {
            'title': 'Backup Completed',
            'message': 'System backup has been completed successfully. All data is secure.',
            'type': 'success',
            'priority': 'high',
            'icon': 'fas fa-database'
        },
        
        # Error notifications
        {
            'title': 'Connection Error',
            'message': 'Failed to connect to external API service. Please check your internet connection.',
            'type': 'error',
            'priority': 'high',
            'icon': 'fas fa-wifi'
        },
        {
            'title': 'Database Error',
            'message': 'Database connection timeout. Please contact system administrator.',
            'type': 'error',
            'priority': 'urgent',
            'icon': 'fas fa-exclamation-triangle'
        },
        
        # Warning notifications
        {
            'title': 'Low Disk Space',
            'message': 'System disk space is running low. Consider cleaning up temporary files.',
            'type': 'warning',
            'priority': 'high',
            'icon': 'fas fa-hdd'
        },
        {
            'title': 'Password Expiry',
            'message': 'Your password will expire in 7 days. Please update it soon.',
            'type': 'warning',
            'priority': 'normal',
            'icon': 'fas fa-key'
        },
        
        # Info notifications
        {
            'title': 'System Maintenance',
            'message': 'Scheduled maintenance will occur tonight at 2:00 AM. Service may be temporarily unavailable.',
            'type': 'info',
            'priority': 'normal',
            'icon': 'fas fa-tools'
        },
        {
            'title': 'New Feature Available',
            'message': 'AI-powered financial analysis feature is now available. Try it out!',
            'type': 'info',
            'priority': 'low',
            'icon': 'fas fa-star'
        },
        
        # System notifications
        {
            'title': 'System Update',
            'message': 'System has been updated to version 2.1.0. New features and bug fixes included.',
            'type': 'system',
            'priority': 'normal',
            'icon': 'fas fa-download'
        },
        {
            'title': 'Performance Optimization',
            'message': 'Database queries have been optimized for better performance.',
            'type': 'system',
            'priority': 'low',
            'icon': 'fas fa-tachometer-alt'
        },
        
        # Security notifications
        {
            'title': 'Suspicious Login Attempt',
            'message': 'Multiple failed login attempts detected from IP 192.168.1.100.',
            'type': 'security',
            'priority': 'urgent',
            'icon': 'fas fa-shield-alt'
        },
        {
            'title': 'Two-Factor Authentication',
            'message': 'Two-factor authentication has been enabled for your account.',
            'type': 'security',
            'priority': 'high',
            'icon': 'fas fa-mobile-alt'
        },
        
        # Financial notifications
        {
            'title': 'Invoice Generated',
            'message': 'Invoice #INV-2024-001 has been generated for client ABC Company.',
            'type': 'financial',
            'priority': 'normal',
            'icon': 'fas fa-file-invoice-dollar'
        },
        {
            'title': 'Payment Received',
            'message': 'Payment of $1,500.00 received for invoice #INV-2024-001.',
            'type': 'financial',
            'priority': 'normal',
            'icon': 'fas fa-credit-card'
        },
        
        # AI notifications
        {
            'title': 'AI Model Training Complete',
            'message': 'Machine learning model training has completed successfully. Accuracy: 94.2%.',
            'type': 'ai',
            'priority': 'normal',
            'icon': 'fas fa-brain'
        },
        {
            'title': 'AI Prediction Available',
            'message': 'New AI-powered financial predictions are available for your analysis.',
            'type': 'ai',
            'priority': 'low',
            'icon': 'fas fa-chart-line'
        },
        
        # Ticket notifications
        {
            'title': 'New Support Ticket',
            'message': 'Support ticket #TKT-2024-001 has been created by user john.doe.',
            'type': 'ticket',
            'priority': 'normal',
            'icon': 'fas fa-ticket-alt'
        },
        {
            'title': 'Ticket Assigned',
            'message': 'Support ticket #TKT-2024-001 has been assigned to you.',
            'type': 'ticket',
            'priority': 'high',
            'icon': 'fas fa-user-check'
        },
        
        # User notifications
        {
            'title': 'Profile Updated',
            'message': 'Your profile information has been updated successfully.',
            'type': 'user',
            'priority': 'low',
            'icon': 'fas fa-user-edit'
        },
        {
            'title': 'Account Created',
            'message': 'New user account has been created for jane.smith@company.com.',
            'type': 'user',
            'priority': 'normal',
            'icon': 'fas fa-user-plus'
        }
    ]
    
    # Create notifications with different timestamps
    created_count = 0
    user_id = 'default_user'  # Default user for testing
    
    for i, notification_data in enumerate(sample_notifications):
        # Create notifications with different timestamps (spread over the last 30 days)
        days_ago = random.randint(0, 30)
        hours_ago = random.randint(0, 23)
        minutes_ago = random.randint(0, 59)
        
        created_at = datetime.utcnow() - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)
        
        # Some notifications should be read
        is_read = random.choice([True, False]) if i > 5 else False
        
        # Create the notification
        notification_id = notification_service.create_notification(
            title=notification_data['title'],
            message=notification_data['message'],
            notification_type=notification_data['type'],
            priority=notification_data['priority'],
            user_id=user_id,
            icon=notification_data['icon'],
            metadata={
                'sample': True,
                'created_for_testing': True
            }
        )
        
        # If it should be read, mark it as read
        if is_read:
            notification_service.mark_as_read(notification_id)
        
        created_count += 1
        print(f"Created notification {created_count}: {notification_data['title']}")
    
    print(f"\n✅ Successfully created {created_count} sample notifications!")
    print(f"User ID: {user_id}")
    print(f"Access notifications at: /notifications")

def cleanup_sample_notifications():
    """Clean up sample notifications"""
    try:
        # Get all notifications with sample metadata
        notifications = notification_service.get_all_notifications(limit=1000)
        
        cleaned_count = 0
        for notification in notifications:
            if notification.get('metadata', {}).get('sample'):
                notification_service.delete_notification(notification['id'])
                cleaned_count += 1
        
        print(f"✅ Cleaned up {cleaned_count} sample notifications!")
        
    except Exception as e:
        print(f"❌ Error cleaning up sample notifications: {e}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Create sample notifications for testing')
    parser.add_argument('--cleanup', action='store_true', help='Clean up sample notifications instead of creating them')
    
    args = parser.parse_args()
    
    if args.cleanup:
        cleanup_sample_notifications()
    else:
        create_sample_notifications()
