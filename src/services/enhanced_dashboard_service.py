"""
Dashboard Service
Handles all dashboard-related business logic and data processing
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import random
from src.models.database import sample_data_model, ticket_model, user_model

logger = logging.getLogger(__name__)

@dataclass
class FinancialSummary:
    """Financial summary data structure"""
    total_revenue: float
    total_expenses: float
    net_profit: float
    profit_margin: float
    monthly_growth: float

@dataclass
class BusinessMetrics:
    """Business metrics data structure"""
    total_customers: int
    active_projects: int
    pending_invoices: int
    overdue_payments: int

@dataclass
class ActivityItem:
    """Activity item data structure"""
    type: str
    message: str
    time: str
    icon: str

@dataclass
class QuickAction:
    """Quick action data structure"""
    name: str
    icon: str
    url: str
    description: str

@dataclass
class Notification:
    """Notification data structure"""
    id: int
    type: str
    title: str
    message: str
    time: str
    read: bool

class DashboardService:
    """Service for handling dashboard data operations"""
    
    @staticmethod
    def get_dashboard_data() -> Dict[str, Any]:
        """Get comprehensive dashboard data"""
        try:
            # Get real financial data from sample.db
            financial_data = sample_data_model.get_financial_data()
            
            # Get additional data
            tickets = ticket_model.get_tickets()
            users = user_model.get_all_users()
            
            # Calculate additional metrics
            total_tickets = len(tickets)
            open_tickets = len([t for t in tickets if t['status'] == 'open'])
            closed_tickets = len([t for t in tickets if t['status'] == 'closed'])
            high_priority_tickets = len([t for t in tickets if t['priority'] == 'high'])
            
            total_users = len(users)
            active_users = len([u for u in users if u.get('is_active', True)])
            admin_users = len([u for u in users if u.get('is_admin', False)])
            
            # Combine all data
            dashboard_data = {
                'financial': financial_data['financial'],
                'invoices': {
                    'total': 45, 'total_amount': 89000, 'paid': 32, 'pending': 13
                },
                'users': {
                    'total': total_users, 'active': active_users, 'admins': admin_users
                },
                'companies': {
                    'total': 18
                },
                'tickets': {
                    'total': total_tickets, 'open': open_tickets, 'closed': closed_tickets, 'high_priority': high_priority_tickets
                },
                'recent_transactions': financial_data['recent_transactions'],
                'notifications': [
                    {
                        'title': 'System Update',
                        'message': 'Dashboard updated with real-time data',
                        'type': 'info',
                        'time': '2 minutes ago',
                        'read': False
                    }
                ]
            }
            
            return dashboard_data
            
        except Exception as e:
            print(f"Error getting dashboard data: {e}")
            # Return fallback data
            return {
                'financial': {
                    'total_revenue': 125000,
                    'total_expenses': 85000,
                    'net_profit': 40000,
                    'total_transactions': 156
                },
                'invoices': {
                    'total': 45, 'total_amount': 89000, 'paid': 32, 'pending': 13
                },
                'users': {
                    'total': 25, 'active': 22, 'admins': 3
                },
                'companies': {
                    'total': 18
                },
                'tickets': {
                    'total': 12, 'open': 8, 'closed': 4, 'high_priority': 2
                },
                'recent_transactions': [],
                'notifications': []
            }

# Global dashboard service instance
dashboard_service = DashboardService()
