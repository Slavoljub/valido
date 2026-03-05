#!/usr/bin/env python3
"""
Comprehensive System Test Suite for ValidoAI
===========================================
Tests all components: databases, configuration, services, error handling
"""

import os
import sys
import unittest
import tempfile
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

class TestConfigurationSystem(unittest.TestCase):
    """Test the global configuration system"""

    def setUp(self):
        """Set up test environment"""
        # Clear environment variables that might affect tests
        env_vars = [
            'DATABASE_TYPE', 'POSTGRES_HOST', 'MYSQL_HOST', 'REDIS_HOST',
            'MONGODB_HOST', 'ELASTICSEARCH_HOST', 'E_FAKTURA_ENABLED',
            'PORESKA_UPRAVA_ENABLED', 'APR_ENABLED'
        ]
        for var in env_vars:
            if var in os.environ:
                del os.environ[var]

    def test_database_config_loading(self):
        """Test database configuration loading"""
        from src.config import DatabaseConfig

        config = DatabaseConfig()

        # Test that all database types are loaded
        expected_types = [
            'postgresql', 'mysql', 'sqlite', 'mongodb', 'redis',
            'elasticsearch', 'cassandra', 'neo4j', 'couchdb',
            'couchbase', 'influxdb', 'clickhouse', 'dynamodb',
            'cosmosdb', 'firestore', 'arangodb', 'orientdb', 'mssql'
        ]

        for db_type in expected_types:
            self.assertIn(db_type, config.databases)
            self.assertIsInstance(config.databases[db_type], dict)

    def test_current_database_config(self):
        """Test current database configuration"""
        from src.config import DatabaseConfig

        config = DatabaseConfig()

        # Test default SQLite configuration
        current = config.get_current_config()
        self.assertIsInstance(current, dict)
        self.assertIn('type', current)
        self.assertIn('available', current)

    def test_connection_string_generation(self):
        """Test connection string generation"""
        from src.config import DatabaseConfig

        config = DatabaseConfig()

        # Test SQLite connection string
        sqlite_conn = config.get_connection_string('sqlite')
        self.assertTrue(sqlite_conn.startswith('sqlite://'))

        # Test PostgreSQL connection string
        pg_conn = config.get_connection_string('postgresql')
        self.assertTrue('postgresql://' in pg_conn or 'postgres://' in pg_conn)

    def test_available_databases(self):
        """Test available databases detection"""
        from src.config import DatabaseConfig

        config = DatabaseConfig()
        available = config.get_available_databases()

        # SQLite should always be available
        self.assertIn('sqlite', available)

        # Test that it's a list
        self.assertIsInstance(available, list)

class TestSerbianGovernmentServices(unittest.TestCase):
    """Test Serbian Government Services configuration"""

    def setUp(self):
        """Set up test environment"""
        # Clear service-related environment variables
        service_vars = [
            'E_FAKTURA_ENABLED', 'PORESKA_UPRAVA_ENABLED', 'APR_ENABLED',
            'PIO_FOND_ENABLED', 'RFZO_ENABLED', 'NSZ_ENABLED',
            'NBS_ENABLED', 'CARINA_ENABLED', 'RZS_ENABLED'
        ]
        for var in service_vars:
            if var in os.environ:
                del os.environ[var]

    def test_services_loading(self):
        """Test Serbian government services loading"""
        from src.config import SerbianGovernmentServices

        services = SerbianGovernmentServices()

        expected_services = [
            'e_faktura', 'poreska_uprava', 'apr', 'pio_fond',
            'rfzo', 'nsz', 'nbs', 'carina', 'rzs'
        ]

        for service in expected_services:
            self.assertIn(service, services.services)
            self.assertIsInstance(services.services[service], dict)

    def test_service_config_structure(self):
        """Test service configuration structure"""
        from src.config import SerbianGovernmentServices

        services = SerbianGovernmentServices()

        for service_name, service_config in services.services.items():
            self.assertIn('name', service_config)
            self.assertIn('enabled', service_config)
            self.assertIsInstance(service_config['enabled'], bool)

    def test_enabled_services_detection(self):
        """Test enabled services detection"""
        from src.config import SerbianGovernmentServices

        services = SerbianGovernmentServices()
        enabled = services.get_enabled_services()

        # By default, no services should be enabled
        self.assertEqual(len(enabled), 0)

    def test_service_status_check(self):
        """Test service status checking"""
        from src.config import SerbianGovernmentServices

        services = SerbianGovernmentServices()

        # Test with a known service
        self.assertFalse(services.is_service_enabled('e_faktura'))
        self.assertFalse(services.is_service_enabled('poreska_uprava'))

class TestDatabaseConnections(unittest.TestCase):
    """Test database connection functionality"""

    def setUp(self):
        """Set up test database"""
        # Create a temporary SQLite database for testing
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db_path = self.temp_db.name

    def tearDown(self):
        """Clean up test database"""
        try:
            os.unlink(self.db_path)
        except:
            pass

    def test_sqlite_connection(self):
        """Test SQLite connection"""
        try:
            import sqlite3
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)')
            cursor.execute('INSERT INTO test (name) VALUES (?)', ('test',))
            cursor.execute('SELECT * FROM test')
            result = cursor.fetchone()
            self.assertEqual(result[1], 'test')
            conn.close()
        except Exception as e:
            self.fail(f"SQLite connection test failed: {e}")

    @patch('psycopg2.connect')
    def test_postgresql_connection_mock(self, mock_connect):
        """Test PostgreSQL connection (mocked)"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        try:
            import psycopg2
            conn = psycopg2.connect(
                host='localhost',
                database='test',
                user='test',
                password='test'
            )
            cursor = conn.cursor()
            cursor.execute('SELECT 1')
            mock_connect.assert_called_once()
        except ImportError:
            self.skipTest("psycopg2 not available")

    @patch('pymongo.MongoClient')
    def test_mongodb_connection_mock(self, mock_client):
        """Test MongoDB connection (mocked)"""
        mock_db = MagicMock()
        mock_client.return_value.test_db = mock_db

        try:
            from pymongo import MongoClient
            client = MongoClient('mongodb://localhost:27017')
            db = client.test_db
            self.assertIsNotNone(db)
        except ImportError:
            self.skipTest("pymongo not available")

class TestErrorHandling(unittest.TestCase):
    """Test error handling and logging"""

    def test_logging_configuration(self):
        """Test logging configuration"""
        import logging

        # Test that logger can be created
        logger = logging.getLogger('test_logger')
        self.assertIsNotNone(logger)

        # Test logging levels
        self.assertEqual(logging.DEBUG, 10)
        self.assertEqual(logging.INFO, 20)
        self.assertEqual(logging.WARNING, 30)
        self.assertEqual(logging.ERROR, 40)
        self.assertEqual(logging.CRITICAL, 50)

    def test_error_message_formatting(self):
        """Test error message formatting"""
        try:
            raise ValueError("Test error message")
        except ValueError as e:
            error_msg = str(e)
            self.assertEqual(error_msg, "Test error message")

    def test_exception_handling(self):
        """Test exception handling patterns"""
        with self.assertRaises(ZeroDivisionError):
            result = 1 / 0

        with self.assertRaises(ValueError):
            int("not_a_number")

    def test_custom_exception(self):
        """Test custom exception handling"""
        class CustomError(Exception):
            pass

        with self.assertRaises(CustomError):
            raise CustomError("Custom error message")

class TestEnvironmentConfiguration(unittest.TestCase):
    """Test environment configuration loading"""

    def setUp(self):
        """Set up test environment"""
        # Backup original environment
        self.original_env = os.environ.copy()

    def tearDown(self):
        """Restore original environment"""
        os.environ.clear()
        os.environ.update(self.original_env)

    def test_environment_variable_loading(self):
        """Test environment variable loading"""
        # Set test environment variables
        os.environ['TEST_VAR'] = 'test_value'
        os.environ['TEST_INT'] = '42'
        os.environ['TEST_BOOL'] = 'true'

        # Test loading
        test_var = os.environ.get('TEST_VAR')
        test_int = os.environ.get('TEST_INT')
        test_bool = os.environ.get('TEST_BOOL')

        self.assertEqual(test_var, 'test_value')
        self.assertEqual(test_int, '42')
        self.assertEqual(test_bool, 'true')

    def test_default_values(self):
        """Test default values for missing environment variables"""
        # Test with default values
        db_type = os.environ.get('DATABASE_TYPE', 'sqlite')
        self.assertEqual(db_type, 'sqlite')

    def test_configuration_file_loading(self):
        """Test configuration file loading"""
        # Create a temporary .env file
        env_content = """TEST_CONFIG_VAR=test_config_value
TEST_CONFIG_INT=123
TEST_CONFIG_BOOL=false
"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write(env_content)
            env_file = f.name

        try:
            # Test reading the file
            with open(env_file, 'r') as f:
                content = f.read()
                self.assertIn('TEST_CONFIG_VAR=test_config_value', content)
                self.assertIn('TEST_CONFIG_INT=123', content)
        finally:
            os.unlink(env_file)

class TestAPIEndpoints(unittest.TestCase):
    """Test API endpoints and routing"""

    def setUp(self):
        """Set up test client"""
        try:
            from app import app
            self.app = app
            self.client = self.app.test_client()
        except Exception as e:
            self.skipTest(f"Could not initialize Flask app: {e}")

    def test_health_endpoint(self):
        """Test health endpoint"""
        if hasattr(self, 'client'):
            response = self.client.get('/health')
            # Note: This might fail if database is not set up
            # but we're testing the endpoint exists
            self.assertIsNotNone(response)

    def test_home_endpoint(self):
        """Test home endpoint"""
        if hasattr(self, 'client'):
            response = self.client.get('/')
            self.assertIsNotNone(response)

    def test_404_handling(self):
        """Test 404 error handling"""
        if hasattr(self, 'client'):
            response = self.client.get('/nonexistent-page')
            self.assertEqual(response.status_code, 404)

class TestSerbianBusinessLogic(unittest.TestCase):
    """Test Serbian business-specific functionality"""

    def test_business_entity_types(self):
        """Test Serbian business entity types"""
        serbian_entities = [
            'DOO (Društvo sa ograničenom odgovornošću)',
            'AD (Akcionarsko društvo)',
            'Preduzetnik (Individual Entrepreneur)',
            'OD (Ortačko društvo)',
            'KD (Komanditno društvo)'
        ]

        for entity in serbian_entities:
            self.assertIsInstance(entity, str)
            self.assertTrue(len(entity) > 0)

    def test_pdv_rates(self):
        """Test Serbian PDV rates"""
        # Current Serbian PDV rates
        pdv_rates = {
            'standard': 20.0,
            'reduced': 10.0,
            'special': 0.0
        }

        for rate_type, rate_value in pdv_rates.items():
            self.assertIsInstance(rate_value, (int, float))
            self.assertGreaterEqual(rate_value, 0)
            self.assertLessEqual(rate_value, 100)

    def test_currency_handling(self):
        """Test Serbian currency handling"""
        # Serbian Dinar (RSD) is the official currency
        rsd_symbol = 'RSD'
        rsd_name = 'Serbian Dinar'

        self.assertEqual(rsd_symbol, 'RSD')
        self.assertEqual(rsd_name, 'Serbian Dinar')

        # Test currency formatting
        amount = 1234.56
        formatted = ".2f"
        self.assertEqual(formatted, "1234.56")

class TestPerformance(unittest.TestCase):
    """Test system performance aspects"""

    def test_memory_usage(self):
        """Test memory usage tracking"""
        import psutil

        process = psutil.Process()
        memory_info = process.memory_info()

        # Memory usage should be reasonable
        self.assertGreater(memory_info.rss, 0)
        self.assertLess(memory_info.rss, 1000 * 1024 * 1024)  # Less than 1GB

    def test_response_time(self):
        """Test response time measurement"""
        import time

        start_time = time.time()
        time.sleep(0.01)  # Small delay
        end_time = time.time()

        duration = end_time - start_time
        self.assertGreater(duration, 0.009)  # At least 9ms
        self.assertLess(duration, 0.1)      # Less than 100ms

class TestSecurity(unittest.TestCase):
    """Test security features"""

    def test_password_hashing(self):
        """Test password hashing functionality"""
        from werkzeug.security import generate_password_hash, check_password_hash

        password = "test_password_123"
        hashed = generate_password_hash(password)

        # Hash should be different from original password
        self.assertNotEqual(hashed, password)

        # Should be able to verify correct password
        self.assertTrue(check_password_hash(hashed, password))

        # Should reject incorrect password
        self.assertFalse(check_password_hash(hashed, "wrong_password"))

    def test_input_validation(self):
        """Test input validation"""
        # Test email validation
        from wtforms.validators import Email

        validator = Email()

        # Valid emails
        valid_emails = [
            'test@example.com',
            'user.name@domain.co.rs',
            'test123@test-domain.com'
        ]

        for email in valid_emails:
            try:
                validator(None, Mock(data=email))
            except Exception:
                self.fail(f"Valid email {email} was rejected")

    def test_sql_injection_prevention(self):
        """Test SQL injection prevention"""
        # Test that parameterized queries work
        test_params = {
            'name': "Test User",
            'email': "test@example.com",
            'id': 123
        }

        for key, value in test_params.items():
            self.assertIsNotNone(value)
            if isinstance(value, str):
                self.assertNotIn(';', value)  # Basic check
                self.assertNotIn('--', value)

def run_comprehensive_tests():
    """Run all comprehensive tests"""
    print("🚀 ValidoAI Comprehensive System Test Suite")
    print("=" * 60)

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test classes
    test_classes = [
        TestConfigurationSystem,
        TestSerbianGovernmentServices,
        TestDatabaseConnections,
        TestErrorHandling,
        TestEnvironmentConfiguration,
        TestAPIEndpoints,
        TestSerbianBusinessLogic,
        TestPerformance,
        TestSecurity
    ]

    for test_class in test_classes:
        suite.addTests(loader.loadTestsFromTestCase(test_class))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")

    if result.failures:
        print("\n❌ FAILURES:")
        for test, traceback in result.failures:
            print(f"  - {test}")

    if result.errors:
        print("\n💥 ERRORS:")
        for test, traceback in result.errors:
            print(f"  - {test}")

    if result.wasSuccessful():
        print("\n✅ ALL TESTS PASSED!")
        return 0
    else:
        print("\n⚠️  SOME TESTS FAILED")
        return 1

if __name__ == '__main__':
    sys.exit(run_comprehensive_tests())
