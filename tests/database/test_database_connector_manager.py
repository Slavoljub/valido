"""
Test Database Connector Manager
TDD approach for testing database connectivity and operations
"""

import pytest
import pandas as pd
import sqlite3
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Import the modules to test
from src.ai_local_models.database_connector_manager import (
    DatabaseConnectorManager,
    ConnectionConfig,
    database_connector_manager
)


class TestConnectionConfig:
    """Test ConnectionConfig dataclass"""

    def test_connection_config_creation(self):
        """Test creating a connection config"""
        config = ConnectionConfig(
            db_type='sqlite',
            database='test.db',
            host='localhost',
            port=3306,
            user='root',
            password='password'
        )

        assert config.db_type == 'sqlite'
        assert config.database == 'test.db'
        assert config.host == 'localhost'
        assert config.port == 3306
        assert config.user == 'root'
        assert config.password == 'password'

    def test_connection_config_defaults(self):
        """Test default values in connection config"""
        config = ConnectionConfig(db_type='mysql')

        assert config.db_type == 'mysql'
        assert config.host == 'localhost'
        assert config.port == 3306
        assert config.database == 'validoai'
        assert config.user == 'root'
        assert config.password == 'root'


class TestDatabaseConnectorManager:
    """Test DatabaseConnectorManager functionality"""

    def setup_method(self):
        """Setup test environment"""
        self.manager = DatabaseConnectorManager()

    def teardown_method(self):
        """Clean up test environment"""
        self.manager.close_all_connections()

    def test_manager_initialization(self):
        """Test manager initialization"""
        assert isinstance(self.manager, DatabaseConnectorManager)
        assert hasattr(self.manager, 'connections')
        assert hasattr(self.manager, 'existing_adapter')
        assert hasattr(self.manager, 'database_factory')
        assert hasattr(self.manager, 'database_manager')

    @patch('src.ai_local_models.database_connector_manager.sqlite3')
    def test_sqlite_connection(self, mock_sqlite):
        """Test SQLite connection"""
        # Mock SQLite connection
        mock_conn = MagicMock()
        mock_sqlite.connect.return_value = mock_conn
        mock_conn.row_factory = sqlite3.Row

        config = ConnectionConfig(db_type='sqlite', database='test.db')
        result = self.manager.connect(config)

        assert result is True
        mock_sqlite.connect.assert_called_once()
        assert 'sqlite_test.db_localhost' in self.manager.connections

    def test_mysql_connection_missing_driver(self):
        """Test MySQL connection when driver is not available"""
        config = ConnectionConfig(
            db_type='mysql',
            host='localhost',
            database='test'
        )

        # Mock import error for pymysql
        with patch.dict('sys.modules', {'pymysql': None}):
            result = self.manager.connect(config)
            assert result is False

    def test_postgresql_connection_missing_driver(self):
        """Test PostgreSQL connection when driver is not available"""
        config = ConnectionConfig(
            db_type='postgresql',
            host='localhost',
            database='test'
        )

        # Mock import error for psycopg2
        with patch.dict('sys.modules', {'psycopg2': None}):
            result = self.manager.connect(config)
            assert result is False

    def test_mongodb_connection_missing_driver(self):
        """Test MongoDB connection when driver is not available"""
        config = ConnectionConfig(
            db_type='mongodb',
            database='test'
        )

        # Mock import error for pymongo
        with patch.dict('sys.modules', {'pymongo': None}):
            result = self.manager.connect(config)
            assert result is False

    def test_unsupported_database_type(self):
        """Test connection with unsupported database type"""
        config = ConnectionConfig(db_type='unsupported_db')
        result = self.manager.connect(config)
        assert result is False

    def test_sqlite_query_execution(self):
        """Test query execution on SQLite"""
        # Create temporary SQLite database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_db:
            temp_path = temp_db.name

        try:
            # Create test table
            conn = sqlite3.connect(temp_path)
            conn.execute("""
                CREATE TABLE test_table (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    value INTEGER
                )
            """)
            conn.execute("INSERT INTO test_table (name, value) VALUES (?, ?)", ('test', 42))
            conn.commit()
            conn.close()

            # Test query execution
            config = ConnectionConfig(
                db_type='sqlite',
                database='test',
                connection_string=f'sqlite:///{temp_path}'
            )

            result = self.manager.execute_query(config, "SELECT * FROM test_table")

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 1
            assert result.iloc[0]['name'] == 'test'
            assert result.iloc[0]['value'] == 42

        finally:
            # Cleanup
            os.unlink(temp_path)
            self.manager.close_all_connections()

    def test_get_table_names_sqlite(self):
        """Test getting table names from SQLite"""
        # Create temporary SQLite database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_db:
            temp_path = temp_db.name

        try:
            # Create test table
            conn = sqlite3.connect(temp_path)
            conn.execute("CREATE TABLE test_table (id INTEGER)")
            conn.commit()
            conn.close()

            config = ConnectionConfig(
                db_type='sqlite',
                database='test',
                connection_string=f'sqlite:///{temp_path}'
            )

            tables = self.manager.get_table_names(config)
            assert 'test_table' in tables

        finally:
            os.unlink(temp_path)
            self.manager.close_all_connections()

    def test_get_table_schema_sqlite(self):
        """Test getting table schema from SQLite"""
        # Create temporary SQLite database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_db:
            temp_path = temp_db.name

        try:
            # Create test table
            conn = sqlite3.connect(temp_path)
            conn.execute("""
                CREATE TABLE test_table (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    value INTEGER DEFAULT 0
                )
            """)
            conn.commit()
            conn.close()

            config = ConnectionConfig(
                db_type='sqlite',
                database='test',
                connection_string=f'sqlite:///{temp_path}'
            )

            schema = self.manager.get_table_schema(config, 'test_table')
            assert schema['table_name'] == 'test_table'
            assert len(schema['columns']) == 3

        finally:
            os.unlink(temp_path)
            self.manager.close_all_connections()

    def test_connection_context_manager(self):
        """Test database connection context manager"""
        # Create temporary SQLite database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_db:
            temp_path = temp_db.name

        try:
            config = ConnectionConfig(
                db_type='sqlite',
                database='test',
                connection_string=f'sqlite:///{temp_path}'
            )

            # Test context manager
            with self.manager.get_connection(config) as conn:
                assert conn is not None
                # Connection should be active within context

            # Connection should be closed after context

        finally:
            os.unlink(temp_path)
            self.manager.close_all_connections()

    def test_test_connection(self):
        """Test connection testing functionality"""
        # Test with valid SQLite connection
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_db:
            temp_path = temp_db.name

        try:
            config = ConnectionConfig(
                db_type='sqlite',
                database='test',
                connection_string=f'sqlite:///{temp_path}'
            )

            result = self.manager.test_connection(config)
            assert result['status'] == 'connected'
            assert result['database_type'] == 'sqlite'
            assert 'table_count' in result
            assert 'connection_time_ms' in result

        finally:
            os.unlink(temp_path)
            self.manager.close_all_connections()

    def test_test_connection_failure(self):
        """Test connection testing with invalid connection"""
        config = ConnectionConfig(
            db_type='sqlite',
            database='nonexistent',
            connection_string='sqlite:///nonexistent.db'
        )

        result = self.manager.test_connection(config)
        assert result['status'] in ['failed', 'error']
        assert result['database_type'] == 'sqlite'

    def test_close_connection(self):
        """Test closing specific connection"""
        # Create a temporary connection
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_db:
            temp_path = temp_db.name

        try:
            config = ConnectionConfig(
                db_type='sqlite',
                database='test',
                connection_string=f'sqlite:///{temp_path}'
            )

            # Connect first
            self.manager.connect(config)
            connection_key = f"sqlite_test_localhost"
            assert connection_key in self.manager.connections

            # Close connection
            self.manager.close_connection(config)
            assert connection_key not in self.manager.connections

        finally:
            os.unlink(temp_path)
            self.manager.close_all_connections()

    def test_close_all_connections(self):
        """Test closing all connections"""
        # Create multiple connections
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_db1:
            temp_path1 = temp_db1.name

        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_db2:
            temp_path2 = temp_db2.name

        try:
            config1 = ConnectionConfig(
                db_type='sqlite',
                database='test1',
                connection_string=f'sqlite:///{temp_path1}'
            )
            config2 = ConnectionConfig(
                db_type='sqlite',
                database='test2',
                connection_string=f'sqlite:///{temp_path2}'
            )

            # Connect to both
            self.manager.connect(config1)
            self.manager.connect(config2)

            # Verify connections exist
            assert len(self.manager.connections) >= 2

            # Close all connections
            self.manager.close_all_connections()

            # Verify all connections are closed
            assert len(self.manager.connections) == 0

        finally:
            os.unlink(temp_path1)
            os.unlink(temp_path2)


class TestDataIntegratorIntegration:
    """Test DataIntegrator integration with DatabaseConnectorManager"""

    def test_data_integrator_uses_db_manager(self):
        """Test that DataIntegrator uses the unified database connector manager"""
        from src.ai_local_models.data_integrator import DataIntegrator

        integrator = DataIntegrator()
        assert hasattr(integrator, 'db_manager')
        assert integrator.db_manager is not None

    def test_sqlite_data_loading_integration(self):
        """Test SQLite data loading through DataIntegrator"""
        # Create temporary SQLite database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_db:
            temp_path = temp_db.name

        try:
            # Create test data
            conn = sqlite3.connect(temp_path)
            conn.execute("""
                CREATE TABLE test_data (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    value INTEGER
                )
            """)
            conn.execute("INSERT INTO test_data (name, value) VALUES (?, ?)", ('test_record', 123))
            conn.commit()
            conn.close()

            # Test through DataIntegrator
            from src.ai_local_models.data_integrator import DataIntegrator
            integrator = DataIntegrator()

            result = integrator.load_data_source(temp_path, 'sqlite', query='SELECT * FROM test_data')

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 1
            assert result.iloc[0]['name'] == 'test_record'
            assert result.iloc[0]['value'] == 123

        finally:
            os.unlink(temp_path)


# Integration tests
class TestDatabaseConnectorIntegration:
    """Integration tests for database connectivity"""

    def test_full_sqlite_workflow(self):
        """Test complete SQLite workflow"""
        # Create temporary database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_db:
            temp_path = temp_db.name

        try:
            config = ConnectionConfig(
                db_type='sqlite',
                database='integration_test',
                connection_string=f'sqlite:///{temp_path}'
            )

            # 1. Connect
            success = database_connector_manager.connect(config)
            assert success

            # 2. Create table
            create_query = """
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY,
                    username TEXT UNIQUE,
                    email TEXT UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            database_connector_manager.execute_query(config, create_query)

            # 3. Insert data
            insert_query = """
                INSERT INTO users (username, email) VALUES (?, ?)
            """
            database_connector_manager.execute_query(config, insert_query, ('testuser', 'test@example.com'))

            # 4. Query data
            result = database_connector_manager.execute_query(config, "SELECT * FROM users")

            assert len(result) == 1
            assert result.iloc[0]['username'] == 'testuser'
            assert result.iloc[0]['email'] == 'test@example.com'

            # 5. Get table names
            tables = database_connector_manager.get_table_names(config)
            assert 'users' in tables

            # 6. Get schema
            schema = database_connector_manager.get_table_schema(config, 'users')
            assert schema['table_name'] == 'users'
            assert len(schema['columns']) == 4

        finally:
            os.unlink(temp_path)
            database_connector_manager.close_all_connections()

    def test_connection_reuse(self):
        """Test connection reuse functionality"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_db:
            temp_path = temp_db.name

        try:
            config = ConnectionConfig(
                db_type='sqlite',
                database='reuse_test',
                connection_string=f'sqlite:///{temp_path}'
            )

            # First connection
            success1 = database_connector_manager.connect(config)
            assert success1
            first_conn = database_connector_manager.connections.get(f"sqlite_reuse_test_localhost")

            # Second connection attempt (should reuse)
            success2 = database_connector_manager.connect(config)
            assert success2
            second_conn = database_connector_manager.connections.get(f"sqlite_reuse_test_localhost")

            # Should be the same connection object
            assert first_conn is second_conn

        finally:
            os.unlink(temp_path)
            database_connector_manager.close_all_connections()


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])
