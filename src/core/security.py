"""
ValidoAI Core Security Module
==============================

Security functions for ValidoAI core functionality.
"""

import hashlib
import secrets
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

def hash_password(password: str, salt: str = None) -> str:
    """Hash a password with salt."""
    if salt is None:
        salt = secrets.token_hex(16)
    return hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()

def verify_password(password: str, hashed_password: str, salt: str) -> bool:
    """Verify a password against its hash."""
    return hash_password(password, salt) == hashed_password

def generate_token(length: int = 32) -> str:
    """Generate a secure random token."""
    return secrets.token_urlsafe(length)

# Export functions
__all__ = ['hash_password', 'verify_password', 'generate_token']