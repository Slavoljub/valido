"""
ValidoAI Analytics Package
=========================

Analytics, reporting, and business intelligence for ValidoAI.

This package includes:
- Dashboard analytics
- Predictive analytics
- Business intelligence
- Reporting systems
- KPI calculations
- Trend analysis
"""

from .dashboard import *
from .predictive import *

__all__ = [
    'get_dashboard_data',
    'get_revenue_forecast',
    'get_customer_insights',
    'get_inventory_optimization',
    'start_predictive_engine'
]
