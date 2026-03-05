"""
ValidoAI Test Configuration and Fixtures
Following Cursor Rules for comprehensive test coverage
"""

import pytest
import os
import sys
import tempfile
import sqlite3
from unittest.mock import Mock, MagicMock
from pathlib import Path

# Add src to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
sys.path.insert(0, str(Path(__file__).parent.parent))

@pytest.fixture(scope="session")
def test_app():
    """Create test Flask application instance"""
    from src.core.app import create_app

    # Create test app with test configuration
    app = create_app('testing')

    # Configure test-specific settings
    app.config.update({
        'TESTING': True,
        'SECRET_KEY': 'test-secret-key',
        'WTF_CSRF_ENABLED': False,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'DEBUG': False,
        'PRESERVE_CONTEXT_ON_EXCEPTION': False
    })

    return app

@pytest.fixture(scope="session")
def test_client(test_app):
    """Create test client for making requests"""
    return test_app.test_client()

@pytest.fixture(scope="session")
def test_db(test_app):
    """Create test database"""
    from src.database.unified_db import DatabaseManager

    db_manager = DatabaseManager()
    db_manager.init_database()

    yield db_manager

    # Cleanup after tests
    db_manager.close_connections()

@pytest.fixture
def mock_postgres():
    """Mock PostgreSQL connection for testing"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.__enter__ = Mock(return_value=mock_cursor)
    mock_cursor.__exit__ = Mock(return_value=None)

    return mock_conn

@pytest.fixture
def mock_mysql():
    """Mock MySQL connection for testing"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.__enter__ = Mock(return_value=mock_cursor)
    mock_cursor.__exit__ = Mock(return_value=None)

    return mock_conn

@pytest.fixture
def sample_user_data():
    """Sample user data for testing"""
    return {
        'id': 1,
        'username': 'testuser',
        'email': 'test@example.com',
        'first_name': 'Test',
        'last_name': 'User',
        'role': 'user',
        'is_active': True
    }

@pytest.fixture
def sample_company_data():
    """Sample company data for testing"""
    return {
        'companies_id': 1,
        'company_name': 'Test Company',
        'legal_name': 'Test Company Legal',
        'tax_id': '123456789',
        'industry': 'Technology',
        'company_type': 'Corporation',
        'status': 'active'
    }

@pytest.fixture
def mock_ai_model():
    """Mock AI model for testing"""
    mock_model = MagicMock()
    mock_model.generate_response.return_value = "This is a test AI response"
    mock_model.get_model_info.return_value = {
        'name': 'test-model',
        'type': 'local',
        'status': 'loaded'
    }

    return mock_model

@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing"""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Mocked AI response"
    mock_client.chat.completions.create.return_value = mock_response

    return mock_client

@pytest.fixture
def temp_directory():
    """Create temporary directory for file operations"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir

@pytest.fixture
def mock_request_context(test_app):
    """Mock Flask request context"""
    with test_app.app_context():
        with test_app.test_request_context():
            yield

@pytest.fixture
def mock_session():
    """Mock Flask session"""
    return {}

@pytest.fixture
def mock_current_user(sample_user_data):
    """Mock current user"""
    user = MagicMock()
    user.__dict__.update(sample_user_data)
    user.is_authenticated = True
    user.is_active = True

    return user

@pytest.fixture
def mock_redis():
    """Mock Redis client"""
    mock_redis = MagicMock()
    mock_redis.get.return_value = None
    mock_redis.set.return_value = True
    mock_redis.setex.return_value = True
    mock_redis.delete.return_value = 1
    mock_redis.exists.return_value = False

    return mock_redis

@pytest.fixture
def mock_cache():
    """Mock cache manager"""
    mock_cache = MagicMock()
    mock_cache.get.return_value = None
    mock_cache.set.return_value = True
    mock_cache.delete.return_value = True
    mock_cache.clear.return_value = True

    return mock_cache

@pytest.fixture
def mock_websocket():
    """Mock WebSocket connection"""
    mock_ws = MagicMock()
    mock_ws.send.return_value = None
    mock_ws.receive.return_value = '{"type": "test", "data": "test_data"}'
    mock_ws.close.return_value = None

    return mock_ws

@pytest.fixture
def mock_file_upload():
    """Mock file upload for testing"""
    mock_file = MagicMock()
    mock_file.filename = 'test_file.txt'
    mock_file.content_type = 'text/plain'
    mock_file.read.return_value = b'Test file content'
    mock_file.seek.return_value = None

    return mock_file

@pytest.fixture
def mock_email_service():
    """Mock email service for testing"""
    mock_email = MagicMock()
    mock_email.send_email.return_value = True
    mock_email.send_verification.return_value = True
    mock_email.send_password_reset.return_value = True

    return mock_email

@pytest.fixture
def mock_payment_service():
    """Mock payment service for testing"""
    mock_payment = MagicMock()
    mock_payment.create_payment.return_value = {'id': 'test_payment', 'status': 'pending'}
    mock_payment.confirm_payment.return_value = {'status': 'completed'}
    mock_payment.refund_payment.return_value = {'status': 'refunded'}

    return mock_payment

@pytest.fixture
def mock_notification_service():
    """Mock notification service for testing"""
    mock_notification = MagicMock()
    mock_notification.send_notification.return_value = True
    mock_notification.send_email_notification.return_value = True
    mock_notification.send_sms_notification.return_value = True

    return mock_notification

# Configuration for different test types
@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Setup test environment before running tests"""
    # Set test environment variables
    os.environ['FLASK_ENV'] = 'testing'
    os.environ['SECRET_KEY'] = 'test-secret-key'
    os.environ['DATABASE_URL'] = 'sqlite:///:memory:'

    yield

    # Cleanup after all tests
    for key in ['FLASK_ENV', 'SECRET_KEY', 'DATABASE_URL']:
        if key in os.environ:
            del os.environ[key]

# Database fixtures for different database types
@pytest.fixture
def sqlite_db():
    """SQLite database for testing"""
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()

    # Create basic test tables
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE,
            email TEXT UNIQUE,
            password_hash TEXT,
            first_name TEXT,
            last_name TEXT,
            role TEXT DEFAULT 'user',
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE companies (
            companies_id INTEGER PRIMARY KEY,
            company_name TEXT,
            legal_name TEXT,
            tax_id TEXT,
            industry TEXT,
            company_type TEXT,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    yield conn

    conn.close()

# Performance testing fixtures
@pytest.fixture
def performance_timer():
    """Timer fixture for performance testing"""
    import time
    start_time = time.time()

    yield

    end_time = time.time()
    duration = end_time - start_time
    print(f"Test duration: {duration:.4f} seconds")

# Security testing fixtures
@pytest.fixture
def security_headers():
    """Common security headers for testing"""
    return {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Content-Security-Policy': "default-src 'self'"
    }

# API testing fixtures
@pytest.fixture
def api_headers():
    """Common API headers for testing"""
    return {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': 'Bearer test-token'
    }

@pytest.fixture
def form_headers():
    """Common form headers for testing"""
    return {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

@pytest.fixture
def multipart_headers():
    """Common multipart form headers for testing"""
    return {
        'Content-Type': 'multipart/form-data'
    }

# Error handling fixtures
@pytest.fixture
def error_scenarios():
    """Common error scenarios for testing"""
    return {
        'validation_error': {'field': 'email', 'message': 'Invalid email format'},
        'permission_error': {'error': 'Insufficient permissions'},
        'not_found_error': {'error': 'Resource not found'},
        'database_error': {'error': 'Database connection failed'},
        'timeout_error': {'error': 'Request timeout'}
    }

# Cleanup fixture
@pytest.fixture(autouse=True)
def cleanup_after_test():
    """Cleanup after each test"""
    yield

    # Any cleanup logic here
    pass

# Test data generators
@pytest.fixture
def user_data_generator():
    """Generate test user data"""
    def _generate_user(overrides=None):
        base_data = {
            'username': f'testuser_{hash(str(overrides)) % 1000}',
            'email': f'test_{hash(str(overrides)) % 1000}@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'role': 'user',
            'is_active': True
        }

        if overrides:
            base_data.update(overrides)

        return base_data

    return _generate_user

@pytest.fixture
def company_data_generator():
    """Generate test company data"""
    def _generate_company(overrides=None):
        base_data = {
            'company_name': f'Test Company {hash(str(overrides)) % 100}',
            'legal_name': f'Test Company Legal {hash(str(overrides)) % 100}',
            'tax_id': f'TAX{hash(str(overrides)) % 1000:06d}',
            'industry': 'Technology',
            'company_type': 'Corporation',
            'status': 'active'
        }

        if overrides:
            base_data.update(overrides)

        return base_data

    return _generate_company

print("✅ ValidoAI test configuration loaded successfully")
print("📊 Test fixtures ready for execution")
print("🎯 Following Cursor Rules for comprehensive coverage")
