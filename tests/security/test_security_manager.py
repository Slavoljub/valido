"""
Tests for Security Manager
TDD approach for comprehensive security testing
"""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from src.ai_local_models.security_manager import (
    SecurityManager,
    CookieProtector,
    ScriptValidator,
    DataSanitizer,
    SecurityError
)


class TestCookieProtector:
    """Test cases for CookieProtector following TDD principles"""

    def setup_method(self):
        """Setup test fixtures"""
        self.protector = CookieProtector()

    def test_initialization(self):
        """Test CookieProtector initialization"""
        assert self.protector is not None
        assert hasattr(self.protector, 'encryption_key')
        assert hasattr(self.protector, 'cipher')

    def test_protect_cookie(self):
        """Test cookie protection"""
        value = "test_session_id"
        user_id = "user123"

        protected = self.protector.protect_cookie(value, user_id)

        assert protected is not None
        assert protected != value
        assert isinstance(protected, str)

    def test_unprotect_cookie(self):
        """Test cookie unprotection"""
        value = "test_session_id"
        user_id = "user123"

        # Protect first
        protected = self.protector.protect_cookie(value, user_id)

        # Unprotect
        unprotected = self.protector.unprotect_cookie(protected, user_id)

        assert unprotected == value

    def test_unprotect_invalid_cookie(self):
        """Test unprotecting invalid cookie"""
        invalid_cookie = "invalid_cookie_data"
        user_id = "user123"

        result = self.protector.unprotect_cookie(invalid_cookie, user_id)
        assert result is None

    def test_create_signature(self):
        """Test HMAC signature creation"""
        value = "test_value"
        user_id = "test_user"

        signature1 = self.protector._create_signature(value, user_id)
        signature2 = self.protector._create_signature(value, user_id)

        # Same inputs should produce same signature
        assert signature1 == signature2
        assert isinstance(signature1, str)
        assert len(signature1) == 64  # SHA256 hex length


class TestScriptValidator:
    """Test cases for ScriptValidator following TDD principles"""

    def setup_method(self):
        """Setup test fixtures"""
        self.validator = ScriptValidator()

    def test_initialization(self):
        """Test ScriptValidator initialization"""
        assert self.validator is not None
        assert hasattr(self.validator, 'dangerous_patterns')
        assert hasattr(self.validator, 'allowed_modules')

    def test_validate_safe_script(self):
        """Test validation of safe script"""
        safe_script = """
import math
import datetime
result = math.sqrt(16)
current_time = datetime.datetime.now()
"""

        is_valid = self.validator.validate_script(safe_script)
        assert is_valid is True

    def test_validate_dangerous_script(self):
        """Test validation of dangerous script"""
        dangerous_script = """
import os
import subprocess
os.system('rm -rf /')
subprocess.call(['rm', '-rf', '/'])
"""

        is_valid = self.validator.validate_script(dangerous_script)
        assert is_valid is False

    def test_sanitize_dangerous_script(self):
        """Test script sanitization"""
        dangerous_script = "import os\nos.system('dangerous_command')"

        sanitized = self.validator.sanitize_script(dangerous_script)

        assert 'import os' not in sanitized
        assert 'os.system' not in sanitized
        assert '# REMOVED:' in sanitized

    def test_validate_unsafe_imports(self):
        """Test validation of unsafe module imports"""
        unsafe_script = "import os\nimport sys\nresult = 1 + 1"

        is_valid = self.validator.validate_script(unsafe_script)
        assert is_valid is False

    def test_validate_safe_imports(self):
        """Test validation of safe module imports"""
        safe_script = "import math\nimport json\nresult = math.pi"

        is_valid = self.validator.validate_script(safe_script)
        assert is_valid is True


class TestDataSanitizer:
    """Test cases for DataSanitizer following TDD principles"""

    def setup_method(self):
        """Setup test fixtures"""
        self.sanitizer = DataSanitizer()

    def test_initialization(self):
        """Test DataSanitizer initialization"""
        assert self.sanitizer is not None
        assert hasattr(self.sanitizer, 'allowed_tags')
        assert hasattr(self.sanitizer, 'allowed_attributes')

    def test_sanitize_html_safe(self):
        """Test sanitizing safe HTML"""
        safe_html = '<p>Hello <strong>world</strong>!</p>'

        sanitized = self.sanitizer.sanitize_html(safe_html)
        assert sanitized == safe_html

    def test_sanitize_html_unsafe(self):
        """Test sanitizing unsafe HTML"""
        unsafe_html = '<p>Hello <script>alert("xss")</script>world!</p>'

        sanitized = self.sanitizer.sanitize_html(unsafe_html)
        assert 'script' not in sanitized
        # Note: bleach might not remove script content, just the tags
        assert '<script>' not in sanitized

    def test_sanitize_filename_safe(self):
        """Test sanitizing safe filename"""
        safe_filename = "document.pdf"

        sanitized = self.sanitizer.sanitize_filename(safe_filename)
        assert sanitized == safe_filename

    def test_sanitize_filename_unsafe(self):
        """Test sanitizing unsafe filename"""
        unsafe_filename = "../../../etc/passwd"

        sanitized = self.sanitizer.sanitize_filename(unsafe_filename)
        # Check that dangerous characters are replaced/removed
        assert '/' not in sanitized
        # The regex removes non-word chars, so we get dots and word chars
        assert sanitized.replace('.', '').replace('_', '').replace('-', '').isalnum()
        assert len(sanitized) <= 255  # Length limit

    def test_sanitize_sql_safe(self):
        """Test sanitizing safe SQL"""
        safe_sql = "SELECT * FROM users WHERE id = 1"

        sanitized = self.sanitizer.sanitize_sql(safe_sql)
        assert sanitized == safe_sql

    def test_sanitize_sql_unsafe(self):
        """Test sanitizing unsafe SQL"""
        unsafe_sql = "SELECT * FROM users WHERE id = 1; DROP TABLE users;--"

        sanitized = self.sanitizer.sanitize_sql(unsafe_sql)
        # Check that dangerous keywords are replaced
        assert 'BLOCKED' in sanitized
        assert sanitized != unsafe_sql  # Should be modified


class TestSecurityManager:
    """Test cases for SecurityManager following TDD principles"""

    def setup_method(self):
        """Setup test fixtures"""
        self.security_manager = SecurityManager()

    def test_initialization(self):
        """Test SecurityManager initialization"""
        assert self.security_manager is not None
        assert hasattr(self.security_manager, 'cookie_protector')
        assert hasattr(self.security_manager, 'script_validator')
        assert hasattr(self.security_manager, 'data_sanitizer')
        assert hasattr(self.security_manager, 'audit_log')

    def test_validate_input_text_valid(self):
        """Test validating valid text input"""
        valid_text = "Hello, this is a normal message!"

        is_valid = self.security_manager.validate_input(valid_text, 'text')
        assert is_valid is True

    def test_validate_input_text_invalid(self):
        """Test validating invalid text input"""
        invalid_text = "Normal text\x00with null bytes"

        is_valid = self.security_manager.validate_input(invalid_text, 'text')
        assert is_valid is False

    def test_validate_input_text_too_long(self):
        """Test validating text that's too long"""
        long_text = "a" * 10001  # Exceeds 10,000 limit

        is_valid = self.security_manager.validate_input(long_text, 'text')
        assert is_valid is False

    def test_validate_input_script_dangerous(self):
        """Test validating dangerous script"""
        dangerous_script = "import os\nos.system('rm -rf /')"

        is_valid = self.security_manager.validate_input(dangerous_script, 'script')
        assert is_valid is False

    def test_validate_input_script_safe(self):
        """Test validating safe script"""
        safe_script = "import math\nresult = math.sqrt(16)"

        is_valid = self.security_manager.validate_input(safe_script, 'script')
        assert is_valid is True

    def test_sanitize_input_text(self):
        """Test sanitizing text input"""
        text_with_nulls = "Hello\x00World"

        sanitized = self.security_manager.sanitize_input(text_with_nulls, 'text')
        assert '\x00' not in sanitized
        assert sanitized == "HelloWorld"

    def test_sanitize_input_html(self):
        """Test sanitizing HTML input"""
        html_input = '<p>Hello <script>alert("xss")</script>World</p>'

        sanitized = self.security_manager.sanitize_input(html_input, 'html')
        assert 'script' not in sanitized
        assert '<script>' not in sanitized
        assert '<p>' in sanitized  # Safe tags should remain

    def test_protect_cookies(self):
        """Test cookie protection"""
        # Create a mock request object
        mock_request = Mock()
        mock_request.cookies = {
            'ai_session': 'session123',
            'session_token': 'token456',
            'user_pref': 'theme_dark'  # This won't be protected
        }
        mock_request.user_id = 'user123'

        protected_cookies = self.security_manager.protect_cookies(mock_request)

        # Only cookies starting with 'ai_' or 'session_' are protected
        assert 'ai_session' in protected_cookies
        assert 'session_token' in protected_cookies
        assert 'user_pref' not in protected_cookies  # Should not be protected
        assert protected_cookies['ai_session'] != 'session123'
        assert protected_cookies['session_token'] != 'token456'

    def test_validate_script_execution_ai_context(self):
        """Test script execution validation for AI context"""
        safe_script = "import math\nresult = math.sqrt(16)"

        is_valid = self.security_manager.validate_script_execution(safe_script, 'ai')
        assert is_valid is True

    def test_validate_script_execution_user_context_strict(self):
        """Test script execution validation for user context (strict)"""
        simple_script = "result = 1 + 1"
        dangerous_script = "import os; os.system('ls')"

        # Simple script should be valid for user context
        is_valid_simple = self.security_manager.validate_script_execution(simple_script, 'user')
        assert is_valid_simple is True

        # Dangerous script should be invalid for user context
        is_valid_dangerous = self.security_manager.validate_script_execution(dangerous_script, 'user')
        assert is_valid_dangerous is False

    def test_audit_log_event(self):
        """Test audit logging"""
        initial_log_count = len(self.security_manager.audit_log)

        self.security_manager.audit_log_event(
            event_type='test_event',
            user_id='test_user',
            details={'action': 'test', 'result': 'success'}
        )

        assert len(self.security_manager.audit_log) == initial_log_count + 1
        last_log = self.security_manager.audit_log[-1]
        assert last_log['event_type'] == 'test_event'
        assert last_log['user_id'] == 'test_user'
        assert last_log['details']['action'] == 'test'

    def test_get_audit_log(self):
        """Test getting audit log"""
        # Add some test logs
        self.security_manager.audit_log_event('event1', 'user1', {'test': 'data1'})
        self.security_manager.audit_log_event('event2', 'user2', {'test': 'data2'})
        self.security_manager.audit_log_event('event1', 'user1', {'test': 'data3'})

        # Test getting all logs
        all_logs = self.security_manager.get_audit_log()
        assert len(all_logs) >= 3

        # Test filtering by user
        user_logs = self.security_manager.get_audit_log(user_id='user1')
        assert len(user_logs) >= 2
        for log in user_logs:
            assert log['user_id'] == 'user1'

        # Test filtering by event type
        event_logs = self.security_manager.get_audit_log(event_type='event1')
        assert len(event_logs) >= 2
        for log in event_logs:
            assert log['event_type'] == 'event1'

    def test_rate_limit_check(self):
        """Test rate limiting"""
        identifier = "test_user"

        # First few requests should be allowed
        for i in range(50):
            result = self.security_manager.rate_limit_check(identifier)
            assert result is True

    def test_audit_log_size_limit(self):
        """Test audit log size limiting"""
        # Add more than 1000 log entries
        for i in range(1100):
            self.security_manager.audit_log_event(
                event_type=f'event_{i}',
                user_id=f'user_{i % 10}',
                details={'index': i}
            )

        # Should only keep last 1000 entries
        assert len(self.security_manager.audit_log) <= 1000

        # Should have the most recent entries
        recent_entries = self.security_manager.audit_log[-10:]
        for entry in recent_entries:
            assert entry['details']['index'] >= 1000
