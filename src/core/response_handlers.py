"""
ValidoAI Core Response Handlers Module
=======================================

Response handling utilities for ValidoAI core.
"""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

def success_response(data=None, message="Success", status_code=200):
    """Create a success response."""
    return {
        "status": "success",
        "message": message,
        "data": data,
        "status_code": status_code
    }

def error_response(message="Error", status_code=400, error_details=None):
    """Create an error response."""
    return {
        "status": "error",
        "message": message,
        "error_details": error_details,
        "status_code": status_code
    }

# Export functions
__all__ = ['success_response', 'error_response']