"""
ValidoAI Core Application
=========================

Core application module for ValidoAI.
This module provides the main Flask application factory function.
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

def create_app(config_name='development'):
    """
    Application factory function.

    Args:
        config_name (str): Configuration environment name

    Returns:
        Flask: Configured Flask application instance
    """
    try:
        # Import the main app factory from the root app.py
        from app import create_app as root_create_app
        return root_create_app(config_name)
    except ImportError as e:
        raise ImportError(f"Failed to import main app factory: {e}")

# Export the create_app function for backward compatibility
__all__ = ['create_app']
