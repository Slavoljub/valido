"""
Two-Factor Authentication (2FA) System for ValidoAI

This module provides comprehensive 2FA functionality including:
- TOTP (Time-based One-Time Password) generation
- QR code generation for authenticator apps
- Backup codes for account recovery
- 2FA setup and verification
- Session management with 2FA
"""

import base64
import hashlib
import secrets
import time
from typing import List, Optional, Tuple
import qrcode
from io import BytesIO
import pyotp
from flask import current_app, session
from flask_login import current_user
from src.extensions import db
from src.models.database_models import User, TwoFactorAuth


class TwoFactorAuthManager:
    """Manages Two-Factor Authentication for users"""
    
    def __init__(self):
        self.totp_window = 1  # Allow 1 time step tolerance
    
    def generate_secret(self) -> str:
        """Generate a new TOTP secret key"""
        return pyotp.random_base32()
    
    def generate_qr_code(self, secret: str, username: str, issuer: str = "ValidoAI") -> str:
        """Generate QR code for authenticator app setup"""
        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=username,
            issuer_name=issuer
        )
        
        # Create QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(totp_uri)
        qr.make(fit=True)
        
        # Create image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
    
    def generate_backup_codes(self, count: int = 10) -> List[str]:
        """Generate backup codes for account recovery"""
        codes = []
        for _ in range(count):
            # Generate 8-character alphanumeric codes
            code = secrets.token_hex(4).upper()
            codes.append(code)
        return codes
    
    def verify_totp(self, secret: str, token: str) -> bool:
        """Verify a TOTP token"""
        try:
            totp = pyotp.TOTP(secret)
            return totp.verify(token, valid_window=self.totp_window)
        except Exception:
            return False
    
    def verify_backup_code(self, user_id: int, code: str) -> bool:
        """Verify a backup code and mark it as used"""
        try:
            # Get user's 2FA record
            two_factor = TwoFactorAuth.query.filter_by(user_id=user_id).first()
            if not two_factor or not two_factor.backup_codes:
                return False
            
            # Check if code exists and hasn't been used
            backup_codes = two_factor.backup_codes.split(',')
            if code in backup_codes:
                # Remove used code
                backup_codes.remove(code)
                two_factor.backup_codes = ','.join(backup_codes)
                db.session.commit()
                return True
            
            return False
        except Exception:
            return False
    
    def setup_2fa(self, user_id: int) -> Tuple[str, str, List[str]]:
        """Setup 2FA for a user"""
        try:
            # Generate new secret
            secret = self.generate_secret()
            
            # Generate backup codes
            backup_codes = self.generate_backup_codes()
            
            # Get user
            user = User.query.get(user_id)
            if not user:
                raise ValueError("User not found")
            
            # Create or update 2FA record
            two_factor = TwoFactorAuth.query.filter_by(user_id=user_id).first()
            if not two_factor:
                two_factor = TwoFactorAuth(
                    user_id=user_id,
                    secret=secret,
                    backup_codes=','.join(backup_codes),
                    is_enabled=False
                )
                db.session.add(two_factor)
            else:
                two_factor.secret = secret
                two_factor.backup_codes = ','.join(backup_codes)
                two_factor.is_enabled = False
            
            db.session.commit()
            
            # Generate QR code
            qr_code = self.generate_qr_code(secret, user.username)
            
            return secret, qr_code, backup_codes
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error setting up 2FA: {str(e)}")
            raise
    
    def enable_2fa(self, user_id: int, token: str) -> bool:
        """Enable 2FA after verification"""
        try:
            two_factor = TwoFactorAuth.query.filter_by(user_id=user_id).first()
            if not two_factor:
                return False
            
            # Verify token
            if not self.verify_totp(two_factor.secret, token):
                return False
            
            # Enable 2FA
            two_factor.is_enabled = True
            db.session.commit()
            
            return True
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error enabling 2FA: {str(e)}")
            return False
    
    def disable_2fa(self, user_id: int, token: str) -> bool:
        """Disable 2FA after verification"""
        try:
            two_factor = TwoFactorAuth.query.filter_by(user_id=user_id).first()
            if not two_factor:
                return False
            
            # Verify token
            if not self.verify_totp(two_factor.secret, token):
                return False
            
            # Disable 2FA
            two_factor.is_enabled = False
            db.session.commit()
            
            return True
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error disabling 2FA: {str(e)}")
            return False
    
    def verify_2fa_login(self, user_id: int, token: str) -> bool:
        """Verify 2FA token during login"""
        try:
            two_factor = TwoFactorAuth.query.filter_by(user_id=user_id).first()
            if not two_factor or not two_factor.is_enabled:
                return False
            
            # Try TOTP first
            if self.verify_totp(two_factor.secret, token):
                return True
            
            # Try backup code
            if self.verify_backup_code(user_id, token):
                return True
            
            return False
            
        except Exception as e:
            current_app.logger.error(f"Error verifying 2FA login: {str(e)}")
            return False
    
    def is_2fa_enabled(self, user_id: int) -> bool:
        """Check if 2FA is enabled for user"""
        try:
            two_factor = TwoFactorAuth.query.filter_by(user_id=user_id).first()
            return two_factor and two_factor.is_enabled
        except Exception:
            return False
    
    def get_remaining_backup_codes(self, user_id: int) -> int:
        """Get number of remaining backup codes"""
        try:
            two_factor = TwoFactorAuth.query.filter_by(user_id=user_id).first()
            if not two_factor or not two_factor.backup_codes:
                return 0
            
            return len(two_factor.backup_codes.split(','))
        except Exception:
            return 0
    
    def regenerate_backup_codes(self, user_id: int) -> List[str]:
        """Regenerate backup codes for user"""
        try:
            two_factor = TwoFactorAuth.query.filter_by(user_id=user_id).first()
            if not two_factor:
                raise ValueError("2FA not set up for user")
            
            # Generate new backup codes
            backup_codes = self.generate_backup_codes()
            two_factor.backup_codes = ','.join(backup_codes)
            db.session.commit()
            
            return backup_codes
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error regenerating backup codes: {str(e)}")
            raise


# Global instance
two_factor_manager = TwoFactorAuthManager()


def require_2fa_setup(f):
    """Decorator to require 2FA setup for certain routes"""
    from functools import wraps
    from flask import redirect, url_for, flash
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            if not two_factor_manager.is_2fa_enabled(current_user.id):
                flash('Two-factor authentication is required for this action.', 'warning')
                return redirect(url_for('auth.setup_2fa'))
        return f(*args, **kwargs)
    return decorated_function


def require_2fa_verification(f):
    """Decorator to require 2FA verification for certain routes"""
    from functools import wraps
    from flask import redirect, url_for, flash
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            # Check if 2FA verification is required in session
            if session.get('require_2fa_verification', False):
                flash('Two-factor authentication verification required.', 'warning')
                return redirect(url_for('auth.verify_2fa'))
        return f(*args, **kwargs)
    return decorated_function
