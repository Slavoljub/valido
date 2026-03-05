"""
ValidoAI Core Package
====================

Main package for ValidoAI - Advanced Business Management System.

This package provides a comprehensive suite of tools for:
- AI-powered business intelligence
- Advanced analytics and forecasting
- Content management and file processing
- Enterprise-grade security and authentication
- Modern web interfaces and APIs
- Multi-database support
- Real-time dashboards and reporting

Package Structure:
├── core/           # Core functionality and utilities
├── api/            # API endpoints and routing
├── auth/           # Authentication and authorization
├── models/         # Data models and database schemas
├── controllers/    # Business logic controllers
├── services/       # Business services layer
├── utils/          # Utility functions and helpers
├── config/         # Configuration management
├── extensions/     # Flask extensions and plugins
├── assets/         # Static assets and resource management
├── database/       # Database connectivity and operations
├── ai/             # AI and machine learning functionality
├── content/        # Content management and file processing
├── analytics/      # Analytics, reporting, and forecasting
├── integrations/   # External service integrations
└── web/            # Web interface components

Quick Start:
    from src import create_app
    app = create_app('development')
"""

__version__ = "1.0.0"
__author__ = "ValidoAI Team"
__description__ = "Advanced Business Management System with AI"

# Core imports for easy access (commented out to avoid circular imports)
# from .core import *
# from .config import *
# from .utils import *

# Version info
VERSION = __version__

def get_version():
    """Get the current version of ValidoAI"""
    return VERSION

def get_info():
    """Get system information"""
    return {
        'name': 'ValidoAI',
        'version': VERSION,
        'author': __author__,
        'description': __description__,
        'features': [
            'AI-powered analytics',
            'Business intelligence',
            'Content management',
            'Real-time dashboards',
            'Enterprise security',
            'Multi-database support',
            'API-first architecture'
        ]
    }