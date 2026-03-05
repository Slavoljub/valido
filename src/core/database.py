"""
ValidoAI Core Database Module
==============================

Database connectivity and operations for ValidoAI core functionality.
This module provides unified database access functions.
"""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

def get_db_connection():
    """
    Get database connection.

    Returns:
        Database connection object
    """
    try:
        from database import connection_manager
        return connection_manager.get_connection()
    except ImportError:
        return None

def close_db_connection():
    """
    Close database connection.
    """
    try:
        from database import connection_manager
        connection_manager.close_all_connections()
    except ImportError:
        pass

# Export functions
__all__ = ['get_db_connection', 'close_db_connection']
