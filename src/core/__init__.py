"""
ValidoAI Core Package
====================

Core functionality and utilities for ValidoAI.

This package provides the foundation for:
- Application initialization
- Configuration management
- Error handling and logging
- Database connections
- Security and authentication
- Common utilities and helpers
"""

# Core imports
from .app import create_app
from .config import Config
from .validoai_logging import LoggerFactory
from .error_handling import handle_controller_import_error, handle_generic_import_error, create_error_response
from .decorators import handle_template_errors, require_auth
from .response_handlers import success_response, error_response
from .system_info import get_system_info

# Database
from .database import get_db_connection, close_db_connection

# Security
from .security import hash_password, verify_password, generate_token

# Utilities
from .utils import format_datetime, format_file_size, validate_email

# Backward compatibility functions
def get_logger(name: str):
    """Get a logger instance (backward compatibility)"""
    return LoggerFactory.get_logger(name)

def setup_logging():
    """Setup logging (backward compatibility)"""
    LoggerFactory.initialize()

__all__ = [
    # App
    'create_app',

    # Config
    'Config',

    # Logging
    'LoggerFactory',
    'get_logger',
    'setup_logging',

    # Error Handling
    'handle_controller_import_error',
    'handle_generic_import_error',
    'create_error_response',
    'handle_template_errors',
    'require_auth',

    # Responses
    'success_response',
    'error_response',

    # System Info
    'get_system_info',

    # Database
    'get_db_connection',
    'close_db_connection',

    # Security
    'hash_password',
    'verify_password',
    'generate_token',

    # Utils
    'format_datetime',
    'format_file_size',
    'validate_email'
]