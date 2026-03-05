#!/usr/bin/env python3
"""
TDD Tests for Database Connection Management
Tests for all database types including Supabase and MS SQL Server
"""

import os
import pytest
import sqlite3
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from src.database.unified_db_manager import UnifiedDatabaseManager, db
from src.ai_local_models.env_loader import EnvironmentLoader


class TestDatabaseConnections:
    """Comprehensive tests for database connection management"""

    @pytest.fixture
    def db_manager(self):
        """Create database manager instance"""
        return UnifiedDatabaseManager()

    @pytest.fixture
    def mock_redis(self):
        """Mock Redis client"""
        with patch('src.ai_local_models.redis_cache_manager.redis') as mock_redis:
            mock_client = MagicMock()
            mock_client.ping.return_value = True
            mock_redis.Redis.return_value = mock_client
            yield mock_client

    def test_database_manager_initialization(self, db_manager):
        """Test database manager initialization"""
        assert db_manager is not None
        assert hasattr(db_manager, 'configs')
        assert hasattr(db_manager, 'connections')
        assert isinstance(db_manager.configs, dict)

    def test_sqlite_database_config(self, db_manager):
        """Test SQLite database configuration"""
        assert 'main' in db_manager.configs
        main_config = db_manager.configs['main']
        assert main_config.type == 'sqlite'
        assert 'data/sqlite/app.db' in main_config.database or main_config.database == 'data/sqlite/app.db'

    def test_postgresql_database_config(self, db_manager):
        """Test PostgreSQL database configuration"""
        assert 'postgresql' in db_manager.configs
        pg_config = db_manager.configs['postgresql']
        assert pg_config.type == 'postgresql'
        assert pg_config.port == 5432

    def test_mysql_database_config(self, db_manager):
        """Test MySQL database configuration"""
        assert 'mysql' in db_manager.configs
        mysql_config = db_manager.configs['mysql']
        assert mysql_config.type == 'mysql'
        assert mysql_config.port == 3306

    def test_mongodb_database_config(self, db_manager):
        """Test MongoDB database configuration"""
        assert 'mongodb' in db_manager.configs
        mongo_config = db_manager.configs['mongodb']
        assert mongo_config.type == 'mongodb'
        assert mongo_config.port == 27017

    def test_mssql_database_config(self, db_manager):
        """Test Microsoft SQL Server database configuration"""
        assert 'mssql' in db_manager.configs
        mssql_config = db_manager.configs['mssql']
        assert mssql_config.type == 'mssql'
        assert mssql_config.port == 1433
        assert mssql_config.username == 'sa'

    def test_supabase_database_config(self, db_manager):
        """Test Supabase database configuration"""
        assert 'supabase' in db_manager.configs
        supabase_config = db_manager.configs['supabase']
        assert supabase_config.type == 'supabase'
        assert supabase_config.port == 5432
        assert supabase_config.enable_ssl == True

    def test_database_config_creation(self):
        """Test creating new database configuration"""
        config = DatabaseConfig(
            type='test',
            host='localhost',
            port=1234,
            database='test_db',
            username='test_user',
            password='test_pass'
        )

        assert config.type == 'test'
        assert config.host == 'localhost'
        assert config.port == 1234
        assert config.database == 'test_db'
        assert config.username == 'test_user'
        assert config.password == 'test_pass'

    def test_database_connection_string_generation(self):
        """Test connection string generation"""
        # SQLite connection string
        sqlite_config = DatabaseConfig(
            type='sqlite',
            database='data/test.db'
        )
        assert sqlite_config.get_connection_string() == 'data/test.db'

        # PostgreSQL connection string
        pg_config = DatabaseConfig(
            type='postgresql',
            host='localhost',
            port=5432,
            database='test_db',
            username='user',
            password='pass'
        )
        expected_pg = 'postgresql://user:pass@localhost:5432/test_db'
        assert pg_config.get_connection_string() == expected_pg

        # MySQL connection string
        mysql_config = DatabaseConfig(
            type='mysql',
            host='localhost',
            port=3306,
            database='test_db',
            username='user',
            password='pass'
        )
        expected_mysql = 'mysql://user:pass@localhost:3306/test_db'
        assert mysql_config.get_connection_string() == expected_mysql

    def test_database_health_check(self, db_manager):
        """Test database health check functionality"""
        health = db_manager.health_check()

        assert isinstance(health, dict)
        assert len(health) > 0  # Should have at least some databases

        # Each health entry should have status and other info
        for db_name, db_health in health.items():
            assert 'status' in db_health
            assert db_health['status'] in ['healthy', 'unhealthy', 'unknown', 'disconnected']

    def test_database_connection_with_sqlite(self, db_manager, tmp_path):
        """Test actual SQLite database connection"""
        # Create a temporary database file
        test_db_path = tmp_path / "test.db"

        # Create test config
        test_config = DatabaseConfig(
            type='sqlite',
            database=str(test_db_path)
        )

        db_manager.add_database('test_sqlite', test_config)

        # Test connection
        connection = db_manager.get_connection('test_sqlite')
        assert connection is not None

        # Test basic query
        result = connection.query("SELECT 1 as test")
        assert result == [(1,)] or result == [{'test': 1}]

    def test_database_connection_error_handling(self, db_manager):
        """Test error handling for invalid database connections"""
        # Create invalid config
        invalid_config = DatabaseConfig(
            type='invalid_type',
            host='invalid_host',
            port=9999,
            database='invalid_db',
            username='invalid_user',
            password='invalid_pass'
        )

        db_manager.add_database('invalid_db', invalid_config)

        # Connection should fail gracefully
        connection = db_manager.get_connection('invalid_db')
        assert connection is None

    def test_supabase_connection_setup(self, db_manager):
        """Test Supabase-specific connection setup"""
        supabase_config = db_manager.configs.get('supabase')
        assert supabase_config is not None
        assert supabase_config.type == 'supabase'
        assert supabase_config.enable_ssl == True
        assert supabase_config.pool_size == 10

    def test_mssql_connection_setup(self, db_manager):
        """Test MS SQL Server-specific connection setup"""
        mssql_config = db_manager.configs.get('mssql')
        assert mssql_config is not None
        assert mssql_config.type == 'mssql'
        assert mssql_config.username == 'sa'
        assert mssql_config.pool_size == 5

    def test_environment_variable_loading(self, db_manager):
        """Test that environment variables are properly loaded"""
        # Check that database configurations use environment variables
        main_config = db_manager.configs['main']
        assert main_config.database is not None

        # Check embeddings config uses environment variables
        embeddings_config = db_manager.configs['embeddings']
        assert embeddings_config.type == 'postgresql'

    def test_database_connection_pooling(self, db_manager):
        """Test database connection pooling settings"""
        # Check that different databases have appropriate pool settings
        main_config = db_manager.configs['main']
        assert hasattr(main_config, 'pool_size')

        embeddings_config = db_manager.configs['embeddings']
        assert hasattr(embeddings_config, 'pool_size')
        assert embeddings_config.pool_size == 3  # Lower for embeddings

        supabase_config = db_manager.configs['supabase']
        assert hasattr(supabase_config, 'pool_size')
        assert supabase_config.pool_size == 10  # Higher for Supabase

    def test_database_ssl_configuration(self, db_manager):
        """Test SSL configuration for databases"""
        # Supabase should have SSL enabled by default
        supabase_config = db_manager.configs['supabase']
        assert supabase_config.enable_ssl == True

        # Embeddings database should have SSL
        embeddings_config = db_manager.configs['embeddings']
        assert embeddings_config.enable_ssl == True

        # SQLite doesn't need SSL
        main_config = db_manager.configs['main']
        assert main_config.enable_ssl == False

    def test_database_timeout_settings(self, db_manager):
        """Test timeout settings for databases"""
        # Different databases should have appropriate timeouts
        embeddings_config = db_manager.configs['embeddings']
        assert embeddings_config.timeout == 60  # Longer for embeddings

        main_config = db_manager.configs['main']
        assert main_config.timeout == 30  # Standard for main DB

        supabase_config = db_manager.configs['supabase']
        assert supabase_config.timeout == 30  # Standard for Supabase


class TestSupabaseIntegration:
    """Tests for Supabase-specific functionality"""

    def test_supabase_config_validation(self):
        """Test Supabase configuration validation"""
        config = DatabaseConfig(
            type='supabase',
            host='db.supabase.co',
            port=5432,
            database='postgres',
            username='postgres',
            password='test_password',
            enable_ssl=True
        )

        assert config.type == 'supabase'
        assert config.host == 'db.supabase.co'
        assert config.enable_ssl == True

    def test_supabase_connection_string(self):
        """Test Supabase connection string generation"""
        config = DatabaseConfig(
            type='supabase',
            host='db.supabase.co',
            port=5432,
            database='postgres',
            username='postgres',
            password='test_password'
        )

        connection_string = config.get_connection_string()
        assert 'postgresql://postgres:test_password@db.supabase.co:5432/postgres' in connection_string


class TestMSSQLIntegration:
    """Tests for Microsoft SQL Server-specific functionality"""

    def test_mssql_config_validation(self):
        """Test MS SQL Server configuration validation"""
        config = DatabaseConfig(
            type='mssql',
            host='localhost',
            port=1433,
            database='test_db',
            username='sa',
            password='test_password',
            enable_ssl=False
        )

        assert config.type == 'mssql'
        assert config.username == 'sa'
        assert config.port == 1433

    def test_mssql_connection_string(self):
        """Test MS SQL Server connection string generation"""
        config = DatabaseConfig(
            type='mssql',
            host='localhost',
            port=1433,
            database='test_db',
            username='sa',
            password='test_password'
        )

        connection_string = config.get_connection_string()
        assert 'mssql+pyodbc://sa:test_password@localhost:1433/test_db' in connection_string


class TestEnvironmentLoaderIntegration:
    """Tests for Environment Loader with database configurations"""

    def test_environment_loader_initialization(self):
        """Test environment loader initialization"""
        loader = EnvironmentLoader()
        assert loader is not None
        assert loader.config_class is not None

    def test_environment_config_loading(self):
        """Test loading environment configuration"""
        loader = EnvironmentLoader()
        config = loader.load_config()

        assert config is not None
        assert hasattr(config, 'database_type')
        assert hasattr(config, 'redis_enabled')

    def test_available_databases_list(self):
        """Test getting list of available databases"""
        loader = EnvironmentLoader()
        config = loader.load_config()

        available_dbs = [
            'sqlite', 'postgresql', 'mysql', 'mongodb',
            'redis', 'elasticsearch', 'cassandra', 'neo4j',
            'mssql', 'supabase'
        ]

        for db in available_dbs:
            assert db in loader.get_available_databases()

    def test_vector_databases_list(self):
        """Test getting list of vector databases"""
        loader = EnvironmentLoader()
        config = loader.load_config()

        vector_dbs = [
            'pinecone', 'weaviate', 'qdrant', 'milvus',
            'chromadb', 'faiss', 'elasticsearch'
        ]

        for db in vector_dbs:
            assert db in loader.get_vector_databases()


if __name__ == '__main__':
    pytest.main([__file__])
