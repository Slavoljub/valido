"""
ValidoAI Models Package
=======================

Unified models system for database, AI, and business logic models.

This package provides:
- Unified database models using SQLAlchemy
- AI model management system
- Email and communication models
- Model management and statistics
"""

from .unified_models import *

# Export all unified models for easy import
__all__ = [
    'db',
    'Company',
    'User',
    'Invoice',
    'InvoiceItem',
    'EmailTemplate',
    'EmailCampaign',
    'EmailRecipient',
    'AIModel',
    'AIInsight',
    'LocalModelManager',
    'UnifiedModelManager',
    'model_manager',
    'local_model_manager'
]

print("✅ ValidoAI Models Package initialized")