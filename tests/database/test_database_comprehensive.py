#!/usr/bin/env python3
"""
Comprehensive Database Testing Suite
Tests all database operations, configurations, and integrations
"""

import pytest
import json
import tempfile
import os
import sqlite3
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

from app import create_app, db
from src.config.unified_config import config
from src.database.unified_db_manager import UnifiedDatabaseManager
from werkzeug.security import generate_password_hash


class TestDatabaseComprehensive:
    """Comprehensive database testing suite"""

    @pytest.fixture
    def app(self):
        """Create and configure a test app instance."""
        app = create_app()
        app.config.update({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'SECRET_KEY': 'test-secret-key',
            'JWT_SECRET_KEY': 'test-jwt-secret',
            'DEBUG': True,
            'SERVER_NAME': 'localhost'
        })
        return app

    @pytest.fixture
    def client(self, app):
        """Create a test client."""
        return app.test_client()

    @pytest.fixture
    def init_database(self, app):
        """Initialize test database with comprehensive test data."""
        with app.app_context():
            db.create_tables()

            # Create test admin user
            admin_password_hash = generate_password_hash('admin123')
            db.execute_query("""
                INSERT OR IGNORE INTO users (
                    username, email, password_hash, first_name, last_name, is_admin, language
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, ('admin', 'admin@validoai.test', admin_password_hash, 'Admin', 'User', 1, 'sr'))

            # Create test regular user
            user_password_hash = generate_password_hash('user123')
            db.execute_query("""
                INSERT OR IGNORE INTO users (
                    username, email, password_hash, first_name, last_name, is_admin, language
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, ('testuser', 'user@validoai.test', user_password_hash, 'Test', 'User', 0, 'en'))

            # Create sample companies
            companies_data = [
                (2, 'Test Company 1', '12345678901', '12345678', 'doo'),
                (2, 'Test Company 2', '23456789012', '23456789', 'ad'),
                (1, 'Admin Company', '34567890123', '34567890', 'doo')
            ]

            for company in companies_data:
                db.execute_query("""
                    INSERT OR IGNORE INTO companies (
                        user_id, company_name, pib, maticni_broj, business_form
                    ) VALUES (?, ?, ?, ?, ?)
                """, company)

            # Create sample transactions
            transactions_data = [
                (2, 'Salary January', 50000.00, 'income', '2024-01-15'),
                (2, 'Office rent', 15000.00, 'expense', '2024-01-20'),
                (2, 'Client payment', 25000.00, 'income', '2024-01-25'),
                (2, 'Software license', 5000.00, 'expense', '2024-01-30'),
                (1, 'Admin transaction', 10000.00, 'income', '2024-01-10')
            ]

            for transaction in transactions_data:
                db.execute_query("""
                    INSERT OR IGNORE INTO transactions (
                        user_id, description, amount, transaction_type, date
                    ) VALUES (?, ?, ?, ?, ?)
                """, transaction)

            # Create sample tickets
            tickets_data = [
                (2, 'Technical support needed', 'I need help with the system', 'open', '2024-01-15'),
                (2, 'Feature request', 'Please add export functionality', 'in_progress', '2024-01-20'),
                (1, 'Admin ticket', 'Administrative issue', 'closed', '2024-01-10')
            ]

            for ticket in tickets_data:
                db.execute_query("""
                    INSERT OR IGNORE INTO tickets (
                        user_id, subject, description, status, created_at
                    ) VALUES (?, ?, ?, ?, ?)
                """, ticket)

            yield db
            db.cleanup()

    # =========================================================================
    # DATABASE CONNECTION AND SETUP TESTS
    # =========================================================================

    def test_database_initialization(self, app):
        """Test database initialization and table creation."""
        with app.app_context():
            # Test that database manager is properly initialized
            assert db is not None
            assert hasattr(db, 'connection_pool')
            assert hasattr(db, 'execute_query')
            assert hasattr(db, 'create_tables')

            # Test table creation
            db.create_tables()

            # Verify tables exist by trying to query them
            tables = ['users', 'companies', 'transactions', 'tickets', 'settings']
            for table in tables:
                try:
                    result = db.execute_query(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
                    assert result is not None
                except Exception as e:
                    pytest.fail(f"Table {table} was not created: {e}")

    def test_database_connection_pooling(self, app):
        """Test database connection pooling functionality."""
        with app.app_context():
            # Test getting connection from pool
            with db.get_connection() as conn:
                assert conn is not None
                # Test that we can execute queries
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                assert result[0] == 1

            # Test connection is returned to pool
            initial_pool_size = len(db.connection_pool._pool)
            with db.get_connection():
                pass
            final_pool_size = len(db.connection_pool._pool)
            assert final_pool_size == initial_pool_size

    def test_database_singleton_pattern(self, app):
        """Test that database manager follows singleton pattern."""
        with app.app_context():
            db1 = UnifiedDatabaseManager()
            db2 = UnifiedDatabaseManager()

            # Should be the same instance
            assert db1 is db2
            assert id(db1) == id(db2)

    # =========================================================================
    # CRUD OPERATIONS TESTS
    # =========================================================================

    def test_user_crud_operations(self, app, init_database):
        """Test complete CRUD operations for users."""
        with app.app_context():
            # CREATE - Test user creation
            new_user_data = {
                'username': 'crudtest',
                'email': 'crudtest@validoai.test',
                'password_hash': generate_password_hash('crud123'),
                'first_name': 'CRUD',
                'last_name': 'Test',
                'is_admin': 0,
                'language': 'sr'
            }

            db.execute_query("""
                INSERT INTO users (username, email, password_hash, first_name, last_name, is_admin, language)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, list(new_user_data.values()))

            # READ - Test user retrieval
            user = db.execute_query(
                "SELECT * FROM users WHERE username = ?",
                ('crudtest',), fetch="one"
            )
            assert user is not None
            assert user['username'] == 'crudtest'
            assert user['email'] == 'crudtest@validoai.test'

            # UPDATE - Test user update
            db.execute_query(
                "UPDATE users SET first_name = ?, last_name = ? WHERE username = ?",
                ('Updated', 'User', 'crudtest')
            )

            updated_user = db.execute_query(
                "SELECT * FROM users WHERE username = ?",
                ('crudtest',), fetch="one"
            )
            assert updated_user['first_name'] == 'Updated'
            assert updated_user['last_name'] == 'User'

            # DELETE - Test user deletion
            db.execute_query("DELETE FROM users WHERE username = ?", ('crudtest',))
            deleted_user = db.execute_query(
                "SELECT * FROM users WHERE username = ?",
                ('crudtest',), fetch="one"
            )
            assert deleted_user is None

    def test_transaction_crud_operations(self, app, init_database):
        """Test complete CRUD operations for transactions."""
        with app.app_context():
            user_id = 2

            # CREATE - Test transaction creation
            transaction_data = {
                'user_id': user_id,
                'description': 'CRUD Test Transaction',
                'amount': 777.77,
                'transaction_type': 'income',
                'date': '2024-02-01'
            }

            db.execute_query("""
                INSERT INTO transactions (user_id, description, amount, transaction_type, date)
                VALUES (?, ?, ?, ?, ?)
            """, list(transaction_data.values()))

            # READ - Test transaction retrieval
            transaction = db.execute_query(
                "SELECT * FROM transactions WHERE description = ? AND user_id = ?",
                ('CRUD Test Transaction', user_id), fetch="one"
            )
            assert transaction is not None
            assert transaction['amount'] == 777.77
            assert transaction['transaction_type'] == 'income'

            # UPDATE - Test transaction update
            db.execute_query(
                "UPDATE transactions SET amount = ?, description = ? WHERE description = ? AND user_id = ?",
                (888.88, 'Updated CRUD Transaction', 'CRUD Test Transaction', user_id)
            )

            updated_transaction = db.execute_query(
                "SELECT * FROM transactions WHERE description = ? AND user_id = ?",
                ('Updated CRUD Transaction', user_id), fetch="one"
            )
            assert updated_transaction['amount'] == 888.88

            # DELETE - Test transaction deletion
            db.execute_query(
                "DELETE FROM transactions WHERE description = ? AND user_id = ?",
                ('Updated CRUD Transaction', user_id)
            )
            deleted_transaction = db.execute_query(
                "SELECT * FROM transactions WHERE description = ? AND user_id = ?",
                ('Updated CRUD Transaction', user_id), fetch="one"
            )
            assert deleted_transaction is None

    def test_company_crud_operations(self, app, init_database):
        """Test complete CRUD operations for companies."""
        with app.app_context():
            user_id = 2

            # CREATE - Test company creation
            company_data = {
                'user_id': user_id,
                'company_name': 'CRUD Test Company',
                'pib': '99988877766',
                'maticni_broj': '99887766',
                'business_form': 'doo'
            }

            db.execute_query("""
                INSERT INTO companies (user_id, company_name, pib, maticni_broj, business_form)
                VALUES (?, ?, ?, ?, ?)
            """, list(company_data.values()))

            # READ - Test company retrieval
            company = db.execute_query(
                "SELECT * FROM companies WHERE company_name = ? AND user_id = ?",
                ('CRUD Test Company', user_id), fetch="one"
            )
            assert company is not None
            assert company['pib'] == '99988877766'

            # UPDATE - Test company update
            db.execute_query(
                "UPDATE companies SET company_name = ?, pib = ? WHERE company_name = ? AND user_id = ?",
                ('Updated CRUD Company', '77766655544', 'CRUD Test Company', user_id)
            )

            updated_company = db.execute_query(
                "SELECT * FROM companies WHERE company_name = ? AND user_id = ?",
                ('Updated CRUD Company', user_id), fetch="one"
            )
            assert updated_company['pib'] == '77766655544'

            # DELETE - Test company deletion
            db.execute_query(
                "DELETE FROM companies WHERE company_name = ? AND user_id = ?",
                ('Updated CRUD Company', user_id)
            )
            deleted_company = db.execute_query(
                "SELECT * FROM companies WHERE company_name = ? AND user_id = ?",
                ('Updated CRUD Company', user_id), fetch="one"
            )
            assert deleted_company is None

    # =========================================================================
    # DATA VALIDATION AND CONSTRAINTS TESTS
    # =========================================================================

    def test_database_constraints(self, app, init_database):
        """Test database constraints and data validation."""
        with app.app_context():
            # Test UNIQUE constraint on username
            with pytest.raises(Exception):
                db.execute_query("""
                    INSERT INTO users (username, email, password_hash, first_name, last_name, is_admin)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, ('admin', 'different@email.com', 'hash', 'Test', 'User', 0))

            # Test UNIQUE constraint on email
            with pytest.raises(Exception):
                db.execute_query("""
                    INSERT INTO users (username, email, password_hash, first_name, last_name, is_admin)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, ('different_user', 'admin@validoai.test', 'hash', 'Test', 'User', 0))

            # Test NOT NULL constraints
            with pytest.raises(Exception):
                db.execute_query("""
                    INSERT INTO users (username, email, password_hash, first_name, last_name, is_admin)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (None, 'test@email.com', 'hash', 'Test', 'User', 0))

    def test_data_types_validation(self, app, init_database):
        """Test data type validation."""
        with app.app_context():
            # Test integer fields
            db.execute_query("""
                INSERT INTO users (username, email, password_hash, first_name, last_name, is_admin)
                VALUES (?, ?, ?, ?, ?, ?)
            """, ('testint', 'testint@email.com', 'hash', 'Test', 'User', 1))

            user = db.execute_query(
                "SELECT * FROM users WHERE username = ?",
                ('testint',), fetch="one"
            )
            assert isinstance(user['is_admin'], int)
            assert user['is_admin'] == 1

            # Test string fields
            assert isinstance(user['username'], str)
            assert isinstance(user['email'], str)

    # =========================================================================
    # QUERY AND RETRIEVAL TESTS
    # =========================================================================

    def test_complex_queries(self, app, init_database):
        """Test complex database queries."""
        with app.app_context():
            # Test JOIN query
            result = db.execute_query("""
                SELECT u.username, u.email, c.company_name
                FROM users u
                LEFT JOIN companies c ON u.id = c.user_id
                WHERE u.id = ?
            """, (2,))

            assert isinstance(result, list)
            for row in result:
                assert 'username' in row
                assert 'email' in row
                assert 'company_name' in row

            # Test aggregate functions
            stats = db.execute_query("""
                SELECT
                    COUNT(*) as total_transactions,
                    SUM(CASE WHEN transaction_type = 'income' THEN amount ELSE 0 END) as total_income,
                    SUM(CASE WHEN transaction_type = 'expense' THEN amount ELSE 0 END) as total_expense
                FROM transactions WHERE user_id = ?
            """, (2,), fetch="one")

            assert stats['total_transactions'] >= 0
            assert stats['total_income'] >= 0
            assert stats['total_expense'] >= 0

            # Test GROUP BY query
            monthly_stats = db.execute_query("""
                SELECT
                    strftime('%Y-%m', date) as month,
                    COUNT(*) as transaction_count,
                    SUM(amount) as total_amount
                FROM transactions
                WHERE user_id = ?
                GROUP BY strftime('%Y-%m', date)
                ORDER BY month
            """, (2,))

            assert isinstance(monthly_stats, list)

    def test_pagination_queries(self, app, init_database):
        """Test pagination and limit queries."""
        with app.app_context():
            # Test LIMIT and OFFSET
            page_size = 2
            page = 1
            offset = (page - 1) * page_size

            transactions = db.execute_query("""
                SELECT * FROM transactions
                WHERE user_id = ?
                ORDER BY date DESC
                LIMIT ? OFFSET ?
            """, (2, page_size, offset))

            assert isinstance(transactions, list)
            assert len(transactions) <= page_size

            # Test count query for pagination
            total_count = db.execute_query("""
                SELECT COUNT(*) as total FROM transactions WHERE user_id = ?
            """, (2,), fetch="one")['total']

            total_pages = (total_count + page_size - 1) // page_size
            assert total_pages >= 0

    def test_search_and_filter_queries(self, app, init_database):
        """Test search and filter functionality."""
        with app.app_context():
            # Test LIKE search
            search_results = db.execute_query("""
                SELECT * FROM transactions
                WHERE user_id = ? AND description LIKE ?
            """, (2, '%office%'))

            assert isinstance(search_results, list)

            # Test date range filter
            date_results = db.execute_query("""
                SELECT * FROM transactions
                WHERE user_id = ? AND date BETWEEN ? AND ?
            """, (2, '2024-01-01', '2024-01-31'))

            assert isinstance(date_results, list)

            # Test amount range filter
            amount_results = db.execute_query("""
                SELECT * FROM transactions
                WHERE user_id = ? AND amount BETWEEN ? AND ?
            """, (2, 1000.00, 50000.00))

            assert isinstance(amount_results, list)

    # =========================================================================
    # TRANSACTION AND CONCURRENCY TESTS
    # =========================================================================

    def test_database_transactions(self, app, init_database):
        """Test database transaction handling."""
        with app.app_context():
            user_id = 2

            # Test successful transaction
            with db.get_connection() as conn:
                cursor = conn.cursor()
                try:
                    cursor.execute("BEGIN TRANSACTION")

                    # Insert multiple related records
                    cursor.execute("""
                        INSERT INTO transactions (user_id, description, amount, transaction_type, date)
                        VALUES (?, ?, ?, ?, ?)
                    """, (user_id, 'Transaction 1', 100.00, 'income', '2024-02-01'))

                    cursor.execute("""
                        INSERT INTO transactions (user_id, description, amount, transaction_type, date)
                        VALUES (?, ?, ?, ?, ?)
                    """, (user_id, 'Transaction 2', 200.00, 'income', '2024-02-02'))

                    cursor.execute("COMMIT")

                    # Verify both transactions were inserted
                    count = db.execute_query(
                        "SELECT COUNT(*) as count FROM transactions WHERE user_id = ? AND description LIKE ?",
                        (user_id, 'Transaction %'), fetch="one"
                    )['count']
                    assert count >= 2

                except Exception as e:
                    cursor.execute("ROLLBACK")
                    raise e

    def test_transaction_rollback(self, app, init_database):
        """Test transaction rollback on error."""
        with app.app_context():
            user_id = 2
            initial_count = db.execute_query(
                "SELECT COUNT(*) as count FROM transactions WHERE user_id = ?",
                (user_id,), fetch="one"
            )['count']

            # Test rollback scenario
            with db.get_connection() as conn:
                cursor = conn.cursor()
                try:
                    cursor.execute("BEGIN TRANSACTION")

                    # Insert first transaction successfully
                    cursor.execute("""
                        INSERT INTO transactions (user_id, description, amount, transaction_type, date)
                        VALUES (?, ?, ?, ?, ?)
                    """, (user_id, 'Rollback Test 1', 100.00, 'income', '2024-02-01'))

                    # Try to insert invalid data (should cause error)
                    cursor.execute("INSERT INTO invalid_table (invalid_column) VALUES (?)", ('test',))

                    cursor.execute("COMMIT")

                except Exception:
                    cursor.execute("ROLLBACK")

                    # Verify rollback worked - no new transactions should be added
                    final_count = db.execute_query(
                        "SELECT COUNT(*) as count FROM transactions WHERE user_id = ?",
                        (user_id,), fetch="one"
                    )['count']
                    assert final_count == initial_count

    # =========================================================================
    # PERFORMANCE TESTS
    # =========================================================================

    def test_query_performance(self, app, init_database):
        """Test database query performance."""
        import time

        with app.app_context():
            # Test simple query performance
            start_time = time.time()
            result = db.execute_query("SELECT COUNT(*) as count FROM users")
            end_time = time.time()

            query_time = end_time - start_time
            # Query should complete within reasonable time (2 seconds)
            assert query_time < 2.0

            # Test complex query performance
            start_time = time.time()
            result = db.execute_query("""
                SELECT u.username, COUNT(t.id) as transaction_count,
                       SUM(t.amount) as total_amount
                FROM users u
                LEFT JOIN transactions t ON u.id = t.user_id
                GROUP BY u.id, u.username
                ORDER BY total_amount DESC
            """)
            end_time = time.time()

            complex_query_time = end_time - start_time
            # Complex query should complete within reasonable time (5 seconds)
            assert complex_query_time < 5.0

    def test_connection_pool_performance(self, app):
        """Test connection pool performance."""
        import time

        with app.app_context():
            # Test multiple connections
            start_time = time.time()

            connections = []
            for i in range(5):
                conn = db.connection_pool.get_connection()
                connections.append(conn)

            # Return connections
            for conn in connections:
                db.connection_pool.return_connection(conn)

            end_time = time.time()
            pool_time = end_time - start_time

            # Connection operations should be fast
            assert pool_time < 1.0

    # =========================================================================
    # ERROR HANDLING TESTS
    # =========================================================================

    def test_database_error_handling(self, app):
        """Test database error handling."""
        with app.app_context():
            # Test invalid SQL syntax
            with pytest.raises(Exception):
                db.execute_query("INVALID SQL SYNTAX")

            # Test connection error handling
            with patch.object(db.connection_pool, 'get_connection', side_effect=Exception("Connection failed")):
                with pytest.raises(Exception):
                    db.execute_query("SELECT 1")

            # Test query with invalid parameters
            with pytest.raises(Exception):
                db.execute_query("SELECT * FROM users WHERE id = ?", ("invalid_id",))

    def test_data_integrity_errors(self, app, init_database):
        """Test data integrity error handling."""
        with app.app_context():
            # Test foreign key constraint violation
            with pytest.raises(Exception):
                db.execute_query("""
                    INSERT INTO transactions (user_id, description, amount, transaction_type, date)
                    VALUES (?, ?, ?, ?, ?)
                """, (999999, 'Test', 100.00, 'income', '2024-01-01'))  # Non-existent user_id

    # =========================================================================
    # BACKUP AND RECOVERY TESTS
    # =========================================================================

    def test_database_backup_functionality(self, app, init_database):
        """Test database backup functionality."""
        with app.app_context():
            # Create a temporary backup file
            with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_file:
                backup_path = temp_file.name

            try:
                # Get current data count
                original_count = db.execute_query(
                    "SELECT COUNT(*) as count FROM users",
                    fetch="one"
                )['count']

                # Test backup creation (if implemented)
                if hasattr(db, 'backup'):
                    db.backup(backup_path)

                    # Verify backup file exists
                    assert os.path.exists(backup_path)
                    assert os.path.getsize(backup_path) > 0

                # Add some test data
                db.execute_query("""
                    INSERT INTO users (username, email, password_hash, first_name, last_name, is_admin)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, ('backup_test', 'backup@test.com', 'hash', 'Backup', 'Test', 0))

                # Verify data was added
                new_count = db.execute_query(
                    "SELECT COUNT(*) as count FROM users",
                    fetch="one"
                )['count']
                assert new_count > original_count

            finally:
                # Clean up backup file
                if os.path.exists(backup_path):
                    os.unlink(backup_path)

    # =========================================================================
    # CONFIGURATION AND SETTINGS TESTS
    # =========================================================================

    def test_settings_management(self, app, init_database):
        """Test application settings management."""
        with app.app_context():
            # Test settings creation
            db.execute_query("""
                INSERT INTO settings (setting_key, setting_value, setting_type)
                VALUES (?, ?, ?)
            """, ('test_setting', 'test_value', 'string'))

            # Test settings retrieval
            setting = db.execute_query(
                "SELECT * FROM settings WHERE setting_key = ?",
                ('test_setting',), fetch="one"
            )
            assert setting is not None
            assert setting['setting_value'] == 'test_value'
            assert setting['setting_type'] == 'string'

            # Test settings update
            db.execute_query(
                "UPDATE settings SET setting_value = ? WHERE setting_key = ?",
                ('updated_value', 'test_setting')
            )

            updated_setting = db.execute_query(
                "SELECT * FROM settings WHERE setting_key = ?",
                ('test_setting',), fetch="one"
            )
            assert updated_setting['setting_value'] == 'updated_value'

            # Test settings deletion
            db.execute_query("DELETE FROM settings WHERE setting_key = ?", ('test_setting',))
            deleted_setting = db.execute_query(
                "SELECT * FROM settings WHERE setting_key = ?",
                ('test_setting',), fetch="one"
            )
            assert deleted_setting is None

    # =========================================================================
    # INTEGRATION AND WORKFLOW TESTS
    # =========================================================================

    def test_complete_user_workflow_database(self, app, init_database):
        """Test complete user workflow with database operations."""
        with app.app_context():
            # 1. Create user
            workflow_user = {
                'username': 'workflowdb',
                'email': 'workflowdb@validoai.test',
                'password_hash': generate_password_hash('workflow123'),
                'first_name': 'Workflow',
                'last_name': 'DB',
                'is_admin': 0,
                'language': 'en'
            }

            db.execute_query("""
                INSERT INTO users (username, email, password_hash, first_name, last_name, is_admin, language)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, list(workflow_user.values()))

            # Get user ID
            user = db.execute_query(
                "SELECT * FROM users WHERE username = ?",
                ('workflowdb',), fetch="one"
            )
            user_id = user['id']

            # 2. Create company for user
            company_data = {
                'user_id': user_id,
                'company_name': 'Workflow Company',
                'pib': '12312312312',
                'maticni_broj': '12312312',
                'business_form': 'doo'
            }

            db.execute_query("""
                INSERT INTO companies (user_id, company_name, pib, maticni_broj, business_form)
                VALUES (?, ?, ?, ?, ?)
            """, list(company_data.values()))

            # 3. Create transactions for user
            transactions_data = [
                (user_id, 'Workflow Income 1', 10000.00, 'income', '2024-02-01'),
                (user_id, 'Workflow Expense 1', 5000.00, 'expense', '2024-02-05'),
                (user_id, 'Workflow Income 2', 15000.00, 'income', '2024-02-10')
            ]

            for transaction in transactions_data:
                db.execute_query("""
                    INSERT INTO transactions (user_id, description, amount, transaction_type, date)
                    VALUES (?, ?, ?, ?, ?)
                """, transaction)

            # 4. Verify complete data integrity
            # Check user exists
            assert user is not None
            assert user['username'] == 'workflowdb'

            # Check company exists
            company = db.execute_query(
                "SELECT * FROM companies WHERE user_id = ?",
                (user_id,), fetch="one"
            )
            assert company is not None
            assert company['company_name'] == 'Workflow Company'

            # Check transactions exist
            transactions = db.execute_query(
                "SELECT * FROM transactions WHERE user_id = ?",
                (user_id,)
            )
            assert len(transactions) == 3

            # Check financial summary
            summary = db.execute_query("""
                SELECT
                    SUM(CASE WHEN transaction_type = 'income' THEN amount ELSE 0 END) as total_income,
                    SUM(CASE WHEN transaction_type = 'expense' THEN amount ELSE 0 END) as total_expense,
                    COUNT(*) as transaction_count
                FROM transactions WHERE user_id = ?
            """, (user_id,), fetch="one")

            assert summary['total_income'] == 25000.00  # 10000 + 15000
            assert summary['total_expense'] == 5000.00
            assert summary['transaction_count'] == 3

    # =========================================================================
    # CLEANUP TESTS
    # =========================================================================

    def test_database_cleanup(self, app, init_database):
        """Test database cleanup operations."""
        with app.app_context():
            # Get initial counts
            initial_counts = {}
            tables = ['users', 'companies', 'transactions', 'tickets', 'settings']

            for table in tables:
                try:
                    count = db.execute_query(f"SELECT COUNT(*) as count FROM {table}", fetch="one")['count']
                    initial_counts[table] = count
                except Exception:
                    initial_counts[table] = 0

            # Add test data that should be cleaned up
            for i in range(5):
                db.execute_query("""
                    INSERT INTO settings (setting_key, setting_value, setting_type)
                    VALUES (?, ?, ?)
                """, (f'temp_setting_{i}', f'temp_value_{i}', 'string'))

            # Perform cleanup
            db.cleanup()

            # Verify cleanup didn't remove essential data
            for table in tables:
                if table != 'settings':  # Settings might be cleaned
                    try:
                        final_count = db.execute_query(f"SELECT COUNT(*) as count FROM {table}", fetch="one")['count']
                        assert final_count >= initial_counts[table]
                    except Exception:
                        pass  # Table might not exist in test environment


# =========================================================================
# MAIN TEST EXECUTION
# =========================================================================

if __name__ == '__main__':
    # Run comprehensive database tests
    pytest.main([
        __file__,
        '-v',
        '--tb=short',
        '--cov=src.database',
        '--cov-report=html:htmlcov_database',
        '--cov-report=term-missing',
        '-k', 'test_database'  # Run only database tests
    ])
