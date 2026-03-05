"""
ValidoAI Core Decorators Module
================================

Decorators for ValidoAI core functionality.
"""

from functools import wraps
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

def handle_template_errors(func):
    """Decorator to handle template errors."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return f"Template error: {e}"
    return wrapper

def require_auth(func):
    """Decorator to require authentication."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Add authentication logic here
        return func(*args, **kwargs)
    return wrapper

# Export decorators
__all__ = ['handle_template_errors', 'require_auth']