"""
Authentication Package for ValidoAI

This package provides comprehensive authentication functionality including:
- Two-Factor Authentication (2FA)
- User authentication and authorization
- Session management
- Security features
"""

from .two_factor import two_factor_manager, require_2fa_setup, require_2fa_verification
from .routes import auth_bp

__all__ = [
    'two_factor_manager',
    'require_2fa_setup', 
    'require_2fa_verification',
    'auth_bp'
]
