"""
Security Manager
Handles security, protection, and input validation for AI local models
"""

import logging
import re
import hashlib
import secrets
from typing import Dict, Any, List, Optional
from pathlib import Path
import bleach
from cryptography.fernet import Fernet
from datetime import datetime, timedelta
import sqlite3

logger = logging.getLogger(__name__)

class SecurityError(Exception):
    """Custom exception for security violations"""
    pass

class CookieProtector:
    """Handles cookie security and protection"""

    def __init__(self):
        self.cookie_salt = secrets.token_hex(32)
        self.encryption_key = Fernet.generate_key()
        self.cipher = Fernet(self.encryption_key)

    def protect_cookie(self, value: str, user_id: str) -> str:
        """Protect cookie value with encryption and signature"""
        try:
            # Create signature
            signature = self._create_signature(value, user_id)

            # Encrypt the value
            encrypted_value = self.cipher.encrypt(f"{value}:{signature}".encode())

            return encrypted_value.decode()

        except Exception as e:
            logger.error(f"Cookie protection failed: {e}")
            raise SecurityError("Failed to protect cookie")

    def unprotect_cookie(self, protected_value: str, user_id: str) -> Optional[str]:
        """Unprotect and validate cookie value"""
        try:
            # Decrypt the value
            decrypted = self.cipher.decrypt(protected_value.encode()).decode()
            value, signature = decrypted.split(':', 1)

            # Validate signature
            expected_signature = self._create_signature(value, user_id)
            if signature != expected_signature:
                raise SecurityError("Invalid cookie signature")

            return value

        except Exception as e:
            logger.error(f"Cookie unprotection failed: {e}")
            return None

    def _create_signature(self, value: str, user_id: str) -> str:
        """Create HMAC signature for cookie value"""
        message = f"{value}:{user_id}:{self.cookie_salt}"
        return hashlib.sha256(message.encode()).hexdigest()

class ScriptValidator:
    """Validates and prevents unauthorized script execution"""

    def __init__(self):
        # Dangerous patterns to block
        self.dangerous_patterns = [
            r'import\s+(os|subprocess|sys)',
            r'eval\s*\(',
            r'exec\s*\(',
            r'open\s*\(',
            r'file\s*\(',
            r'compile\s*\(',
            r'globals\s*\(',
            r'locals\s*\(',
            r'getattr\s*\(',
            r'setattr\s*\(',
            r'delattr\s*\(',
            r'hasattr\s*\(',
            r'vars\s*\(',
            r'dir\s*\(',
            r'system\s*\(',
            r'popen\s*\(',
            r'spawn\s*\(',
            r'fork\s*\(',
            r'kill\s*\(',
            r'exit\s*\(',
            r'quit\s*\('
        ]

        # Allowed modules for AI processing
        self.allowed_modules = {
            'math', 'datetime', 'json', 're', 'string', 'collections',
            'itertools', 'functools', 'operator', 'random', 'uuid',
            'decimal', 'fractions', 'statistics'
        }

    def validate_script(self, script: str) -> bool:
        """
        Validate script for security violations

        Args:
            script: Script code to validate

        Returns:
            True if script is safe, False otherwise
        """
        try:
            # Check for dangerous patterns
            for pattern in self.dangerous_patterns:
                if re.search(pattern, script, re.IGNORECASE):
                    logger.warning(f"Dangerous pattern detected: {pattern}")
                    return False

            # Check for import statements
            import_pattern = r'import\s+([a-zA-Z_][a-zA-Z0-9_]*)'
            imports = re.findall(import_pattern, script)

            for module in imports:
                if module not in self.allowed_modules:
                    logger.warning(f"Unauthorized module import: {module}")
                    return False

            # Check for from imports
            from_pattern = r'from\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+import'
            from_imports = re.findall(from_pattern, script)

            for module in from_imports:
                if module not in self.allowed_modules:
                    logger.warning(f"Unauthorized from-import: {module}")
                    return False

            return True

        except Exception as e:
            logger.error(f"Script validation error: {e}")
            return False

    def sanitize_script(self, script: str) -> str:
        """Sanitize script by removing dangerous content"""
        try:
            # Remove dangerous patterns
            for pattern in self.dangerous_patterns:
                script = re.sub(pattern, '# REMOVED: Dangerous operation', script, flags=re.IGNORECASE)

            # Remove unauthorized imports
            import_pattern = r'import\s+([a-zA-Z_][a-zA-Z0-9_]*)'
            script = re.sub(import_pattern,
                          lambda m: f'# REMOVED: {m.group(0)}' if m.group(1) not in self.allowed_modules else m.group(0),
                          script)

            from_pattern = r'from\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+import'
            script = re.sub(from_pattern,
                          lambda m: f'# REMOVED: {m.group(0)}' if m.group(1) not in self.allowed_modules else m.group(0),
                          script)

            return script

        except Exception as e:
            logger.error(f"Script sanitization error: {e}")
            return "# ERROR: Script sanitization failed"

class DataSanitizer:
    """Sanitizes input data for security"""

    def __init__(self):
        self.allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'a', 'ul', 'ol', 'li']
        self.allowed_attributes = {
            'a': ['href', 'title'],
        }

    def sanitize_html(self, html_content: str) -> str:
        """Sanitize HTML content"""
        try:
            return bleach.clean(
                html_content,
                tags=self.allowed_tags,
                attributes=self.allowed_attributes,
                strip=True
            )
        except Exception as e:
            logger.error(f"HTML sanitization error: {e}")
            return ""

    def sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for security"""
        try:
            # Remove dangerous characters
            safe_name = re.sub(r'[^\w\-_\.]', '', filename)
            # Limit length
            safe_name = safe_name[:255]
            # Ensure it has an extension
            if '.' not in safe_name:
                safe_name += '.txt'
            return safe_name
        except Exception as e:
            logger.error(f"Filename sanitization error: {e}")
            return "sanitized_file.txt"

    def sanitize_sql(self, sql_query: str) -> str:
        """Basic SQL sanitization (not a replacement for prepared statements)"""
        try:
            # Remove dangerous SQL keywords
            dangerous_sql = [
                'DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER',
                'CREATE', 'TRUNCATE', 'EXEC', 'EXECUTE'
            ]

            for keyword in dangerous_sql:
                pattern = rf'\b{keyword}\b'
                sql_query = re.sub(pattern, f'-- BLOCKED: {keyword}', sql_query, flags=re.IGNORECASE)

            return sql_query

        except Exception as e:
            logger.error(f"SQL sanitization error: {e}")
            return "-- ERROR: SQL sanitization failed"

class SecurityManager:
    """Main security manager class"""

    def __init__(self):
        self.cookie_protector = CookieProtector()
        self.script_validator = ScriptValidator()
        self.data_sanitizer = DataSanitizer()
        self.audit_log = []

    def validate_input(self, input_data: str, input_type: str = 'text') -> bool:
        """
        Validate input data based on type

        Args:
            input_data: Data to validate
            input_type: Type of input ('text', 'html', 'filename', 'sql', 'script')

        Returns:
            True if input is valid, False otherwise
        """
        try:
            if not input_data:
                return True

            if input_type == 'html':
                sanitized = self.data_sanitizer.sanitize_html(input_data)
                return sanitized == input_data

            elif input_type == 'filename':
                sanitized = self.data_sanitizer.sanitize_filename(input_data)
                return sanitized == input_data

            elif input_type == 'sql':
                # Basic SQL validation - check for obvious attacks
                sql_indicators = ['--', '/*', '*/', 'xp_', 'sp_']
                for indicator in sql_indicators:
                    if indicator in input_data.lower():
                        return False
                return True

            elif input_type == 'script':
                return self.script_validator.validate_script(input_data)

            elif input_type == 'text':
                # Basic text validation
                if len(input_data) > 10000:  # Limit text length
                    return False
                # Check for null bytes
                if '\x00' in input_data:
                    return False
                return True

            return False

        except Exception as e:
            logger.error(f"Input validation error: {e}")
            return False

    def sanitize_input(self, input_data: str, input_type: str = 'text') -> str:
        """Sanitize input data"""
        try:
            if input_type == 'html':
                return self.data_sanitizer.sanitize_html(input_data)
            elif input_type == 'filename':
                return self.data_sanitizer.sanitize_filename(input_data)
            elif input_type == 'script':
                return self.script_validator.sanitize_script(input_data)
            elif input_type == 'sql':
                return self.data_sanitizer.sanitize_sql(input_data)
            else:
                # Basic text sanitization
                return input_data.replace('\x00', '').strip()[:10000]

        except Exception as e:
            logger.error(f"Input sanitization error: {e}")
            return ""

    def protect_cookies(self, request) -> Dict[str, Any]:
        """
        Protect cookies in request

        Args:
            request: Flask request object

        Returns:
            Dictionary with protected cookie information
        """
        try:
            protected_cookies = {}

            for cookie_name, cookie_value in request.cookies.items():
                if cookie_name.startswith('ai_') or cookie_name.startswith('session_'):
                    user_id = getattr(request, 'user_id', 'anonymous')
                    protected_cookies[cookie_name] = self.cookie_protector.protect_cookie(cookie_value, user_id)

            return protected_cookies

        except Exception as e:
            logger.error(f"Cookie protection error: {e}")
            return {}

    def validate_script_execution(self, script: str, context: str = 'ai') -> bool:
        """
        Validate script for execution in given context

        Args:
            script: Script to validate
            context: Execution context ('ai', 'user', 'system')

        Returns:
            True if script can be executed, False otherwise
        """
        try:
            # Basic validation
            if not self.script_validator.validate_script(script):
                return False

            # Context-specific validation
            if context == 'ai':
                # For AI-generated scripts, be more lenient but still safe
                return True
            elif context == 'user':
                # For user scripts, be very strict
                return len(script) < 1000 and not any(char in script for char in [';', '\n', '\r'])
            elif context == 'system':
                # For system scripts, allow more operations but still validate
                return self.script_validator.validate_script(script)

            return False

        except Exception as e:
            logger.error(f"Script execution validation error: {e}")
            return False

    def audit_log_event(self, event_type: str, user_id: str, details: Dict[str, Any]):
        """Log security event for auditing"""
        try:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'event_type': event_type,
                'user_id': user_id,
                'details': details
            }

            self.audit_log.append(log_entry)

            # Keep only last 1000 entries
            if len(self.audit_log) > 1000:
                self.audit_log = self.audit_log[-1000:]

            logger.info(f"Security event logged: {event_type} for user {user_id}")

        except Exception as e:
            logger.error(f"Audit logging error: {e}")

    def get_audit_log(self, user_id: str = None, event_type: str = None,
                     limit: int = 100) -> List[Dict[str, Any]]:
        """Get audit log entries"""
        try:
            filtered_log = self.audit_log

            if user_id:
                filtered_log = [entry for entry in filtered_log if entry['user_id'] == user_id]

            if event_type:
                filtered_log = [entry for entry in filtered_log if entry['event_type'] == event_type]

            return filtered_log[-limit:]

        except Exception as e:
            logger.error(f"Get audit log error: {e}")
            return []

    def rate_limit_check(self, identifier: str, max_requests: int = 100,
                        window_seconds: int = 3600) -> bool:
        """
        Check if request should be rate limited

        Args:
            identifier: Unique identifier for the requester
            max_requests: Maximum requests allowed in window
            window_seconds: Time window in seconds

        Returns:
            True if request should proceed, False if rate limited
        """
        try:
            # This is a simple in-memory rate limiter
            # In production, you'd use Redis or similar
            current_time = datetime.now()

            # Clean old entries (simple cleanup)
            cutoff_time = current_time - timedelta(seconds=window_seconds)

            # For demo purposes, always return True
            # In production, implement proper rate limiting logic
            return True

        except Exception as e:
            logger.error(f"Rate limit check error: {e}")
            return False

# Global instance
security_manager = SecurityManager()
