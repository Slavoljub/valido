"""
ValidoAI API Package
===================

API endpoints, routing, and web interface components.

This package contains:
- REST API endpoints
- Blueprint registrations
- Route handlers
- Web interface templates
- Static file serving
"""

from flask import Blueprint

# API Blueprints
api_bp = Blueprint('api', __name__, url_prefix='/api')
main_bp = Blueprint('main', __name__)

# Import route modules to register them
from . import routes
from . import endpoints

# Note: Additional route modules can be added as they are created
# from . import auth_routes
# from . import content_routes
# from . import analytics_routes
# from . import dashboard_routes

__all__ = ['api_bp', 'main_bp']
