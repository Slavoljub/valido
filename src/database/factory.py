"""
Database Factory Pattern Implementation
Provides a factory for creating database connections
"""

from abc import ABC, abstractmethod
import os
from typing import Dict, Any, Optional

# Database imports with fallbacks
try:
    import pymysql
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

try:
    from pymongo import MongoClient
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

try:
    import sqlite3
    SQLITE_AVAILABLE = True
except ImportError:
    SQLITE_AVAILABLE = False

class DatabaseConnection(ABC):
    """Abstract base class for database connections"""
    
    @abstractmethod
    def connect(self):
        """Establish connection to the database"""
        pass
    
    @abstractmethod
    def disconnect(self):
        """Close the database connection"""
        pass
    
    @abstractmethod
    def execute_query(self, query, params=None):
        """Execute a query on the database"""
        pass
    
    @abstractmethod
    def fetch_all(self, query, params=None):
        """Fetch all results from a query"""
        pass
    
    @abstractmethod
    def fetch_one(self, query, params=None):
        """Fetch one result from a query"""
        pass
    
    @abstractmethod
    def insert(self, table, data):
        """Insert data into a table"""
        pass
    
    @abstractmethod
    def update(self, table, data, condition):
        """Update data in a table"""
        pass
    
    @abstractmethod
    def delete(self, table, condition):
        """Delete data from a table"""
        pass

class MySQLConnection(DatabaseConnection):
    """MySQL database connection implementation"""
    
    def __init__(self, config):
        self.config = config
        self.connection = None
        self.cursor = None
    
    def connect(self):
        if not MYSQL_AVAILABLE:
            raise ImportError("PyMySQL is not installed")
        
        self.connection = pymysql.connect(
            host=self.config.get('host', 'localhost'),
            port=int(self.config.get('port', 3306)),
            user=self.config.get('user', 'root'),
            password=self.config.get('password', 'root'),
            database=self.config.get('database', 'valido'),
            charset=self.config.get('charset', 'utf8mb4'),
            cursorclass=pymysql.cursors.DictCursor
        )
        return self.connection
    
    def disconnect(self):
        if self.connection:
            self.connection.close()
    
    def execute_query(self, query, params=None):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params or ())
                self.connection.commit()
                return cursor.lastrowid
        except Exception as e:
            self.connection.rollback()
            raise e
    
    def fetch_all(self, query, params=None):
        with self.connection.cursor() as cursor:
            cursor.execute(query, params or ())
            return cursor.fetchall()
    
    def fetch_one(self, query, params=None):
        with self.connection.cursor() as cursor:
            cursor.execute(query, params or ())
            return cursor.fetchone()
    
    def insert(self, table, data):
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['%s'] * len(data))
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        return self.execute_query(query, list(data.values()))
    
    def update(self, table, data, condition):
        set_clause = ', '.join([f"{k} = %s" for k in data.keys()])
        where_clause = ' AND '.join([f"{k} = %s" for k in condition.keys()])
        query = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
        params = list(data.values()) + list(condition.values())
        return self.execute_query(query, params)
    
    def delete(self, table, condition):
        where_clause = ' AND '.join([f"{k} = %s" for k in condition.keys()])
        query = f"DELETE FROM {table} WHERE {where_clause}"
        return self.execute_query(query, list(condition.values()))

class PostgreSQLConnection(DatabaseConnection):
    """PostgreSQL database connection implementation"""
    
    def __init__(self, config):
        self.config = config
        self.connection = None
        self.cursor = None
    
    def connect(self):
        if not POSTGRES_AVAILABLE:
            raise ImportError("psycopg2 is not installed")
        
        self.connection = psycopg2.connect(
            host=self.config.get('host', 'localhost'),
            port=int(self.config.get('port', 5432)),
            user=self.config.get('user', 'postgres'),
            password=self.config.get('password', 'postgres'),
            database=self.config.get('database', 'valido')
        )
        return self.connection
    
    def disconnect(self):
        if self.connection:
            self.connection.close()
    
    def execute_query(self, query, params=None):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params or ())
                self.connection.commit()
                try:
                    return cursor.fetchone()[0]  # Return ID for INSERT operations
                except:
                    return None
        except Exception as e:
            self.connection.rollback()
            raise e
    
    def fetch_all(self, query, params=None):
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, params or ())
            return cursor.fetchall()
    
    def fetch_one(self, query, params=None):
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, params or ())
            return cursor.fetchone()
    
    def insert(self, table, data):
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['%s'] * len(data))
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders}) RETURNING id"
        return self.execute_query(query, list(data.values()))
    
    def update(self, table, data, condition):
        set_clause = ', '.join([f"{k} = %s" for k in data.keys()])
        where_clause = ' AND '.join([f"{k} = %s" for k in condition.keys()])
        query = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
        params = list(data.values()) + list(condition.values())
        return self.execute_query(query, params)
    
    def delete(self, table, condition):
        where_clause = ' AND '.join([f"{k} = %s" for k in condition.keys()])
        query = f"DELETE FROM {table} WHERE {where_clause}"
        return self.execute_query(query, list(condition.values()))

class SQLiteConnection(DatabaseConnection):
    """SQLite database connection implementation"""
    
    def __init__(self, config):
        self.config = config
        self.connection = None
        self.cursor = None
    
    def connect(self):
        if not SQLITE_AVAILABLE:
            raise ImportError("sqlite3 is not available")
        
        self.connection = sqlite3.connect(self.config.get('database', 'valido.db'))
        self.connection.row_factory = sqlite3.Row
        return self.connection
    
    def disconnect(self):
        if self.connection:
            self.connection.close()
    
    def execute_query(self, query, params=None):
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params or ())
            self.connection.commit()
            return cursor.lastrowid
        except Exception as e:
            self.connection.rollback()
            raise e
    
    def fetch_all(self, query, params=None):
        cursor = self.connection.cursor()
        cursor.execute(query, params or ())
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def fetch_one(self, query, params=None):
        cursor = self.connection.cursor()
        cursor.execute(query, params or ())
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def insert(self, table, data):
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?'] * len(data))
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        return self.execute_query(query, list(data.values()))
    
    def update(self, table, data, condition):
        set_clause = ', '.join([f"{k} = ?" for k in data.keys()])
        where_clause = ' AND '.join([f"{k} = ?" for k in condition.keys()])
        query = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
        params = list(data.values()) + list(condition.values())
        return self.execute_query(query, params)
    
    def delete(self, table, condition):
        where_clause = ' AND '.join([f"{k} = ?" for k in condition.keys()])
        query = f"DELETE FROM {table} WHERE {where_clause}"
        return self.execute_query(query, list(condition.values()))

class MongoDBConnection(DatabaseConnection):
    """MongoDB database connection implementation"""
    
    def __init__(self, config):
        self.config = config
        self.client = None
        self.db = None
    
    def connect(self):
        if not MONGODB_AVAILABLE:
            raise ImportError("PyMongo is not installed")
        
        host = self.config.get('host', 'localhost')
        port = int(self.config.get('port', 27017))
        username = self.config.get('username')
        password = self.config.get('password')
        database = self.config.get('database', 'valido')
        
        if username and password:
            uri = f"mongodb://{username}:{password}@{host}:{port}/{database}"
        else:
            uri = f"mongodb://{host}:{port}/{database}"
        
        self.client = MongoClient(uri)
        self.db = self.client[database]
        return self.client
    
    def disconnect(self):
        if self.client:
            self.client.close()
    
    def execute_query(self, query, params=None):
        # MongoDB doesn't use SQL queries, so this is a placeholder
        raise NotImplementedError("MongoDB doesn't support SQL queries")
    
    def fetch_all(self, collection, query=None):
        return list(self.db[collection].find(query or {}))
    
    def fetch_one(self, collection, query=None):
        return self.db[collection].find_one(query or {})
    
    def insert(self, collection, data):
        result = self.db[collection].insert_one(data)
        return str(result.inserted_id)
    
    def update(self, collection, data, condition):
        result = self.db[collection].update_one(condition, {"$set": data})
        return result.modified_count
    
    def delete(self, collection, condition):
        result = self.db[collection].delete_one(condition)
        return result.deleted_count

class RedisConnection(DatabaseConnection):
    """Redis database connection implementation"""
    
    def __init__(self, config):
        self.config = config
        self.connection = None
    
    def connect(self):
        if not REDIS_AVAILABLE:
            raise ImportError("Redis is not installed")
        
        self.connection = redis.Redis(
            host=self.config.get('host', 'localhost'),
            port=int(self.config.get('port', 6379)),
            password=self.config.get('password'),
            db=int(self.config.get('db', 0))
        )
        return self.connection
    
    def disconnect(self):
        if self.connection:
            self.connection.close()
    
    def execute_query(self, query, params=None):
        # Redis doesn't use SQL queries, so this is a placeholder
        raise NotImplementedError("Redis doesn't support SQL queries")
    
    def fetch_all(self, pattern="*"):
        keys = self.connection.keys(pattern)
        result = {}
        for key in keys:
            result[key.decode('utf-8')] = self.connection.get(key).decode('utf-8')
        return result
    
    def fetch_one(self, key):
        value = self.connection.get(key)
        return value.decode('utf-8') if value else None
    
    def insert(self, key, data):
        if isinstance(data, dict):
            return self.connection.hset(key, mapping=data)
        else:
            return self.connection.set(key, data)
    
    def update(self, key, data, condition=None):
        # Redis doesn't support conditions in updates
        if isinstance(data, dict):
            return self.connection.hset(key, mapping=data)
        else:
            return self.connection.set(key, data)
    
    def delete(self, key, condition=None):
        # Redis doesn't support conditions in deletes
        return self.connection.delete(key)

class DatabaseFactory:
    """Factory for creating database connections"""
    
    @staticmethod
    def get_connection(db_type: str, config: Optional[Dict[str, Any]] = None) -> DatabaseConnection:
        """
        Get a database connection based on type
        
        Args:
            db_type: Type of database (mysql, postgres, sqlite, mongodb, redis)
            config: Configuration for the database connection
            
        Returns:
            DatabaseConnection: The database connection object
        """
        if config is None:
            config = DatabaseFactory.get_default_config(db_type)
        
        if db_type == 'mysql':
            connection = MySQLConnection(config)
        elif db_type == 'postgres':
            connection = PostgreSQLConnection(config)
        elif db_type == 'sqlite':
            connection = SQLiteConnection(config)
        elif db_type == 'mongodb':
            connection = MongoDBConnection(config)
        elif db_type == 'redis':
            connection = RedisConnection(config)
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
        
        connection.connect()
        return connection
    
    @staticmethod
    def get_default_config(db_type: str) -> Dict[str, Any]:
        """Get default configuration for database type"""
        configs = {
            'mysql': {
                'host': os.getenv('MYSQL_HOST', 'localhost'),
                'port': int(os.getenv('MYSQL_PORT', 3306)),
                'user': os.getenv('MYSQL_USER', 'root'),
                'password': os.getenv('MYSQL_PASSWORD', 'root'),
                'database': os.getenv('MYSQL_DATABASE', 'valido'),
                'charset': 'utf8mb4'
            },
            'postgres': {
                'host': os.getenv('POSTGRES_HOST', 'localhost'),
                'port': int(os.getenv('POSTGRES_PORT', 5432)),
                'user': os.getenv('POSTGRES_USER', 'postgres'),
                'password': os.getenv('POSTGRES_PASSWORD', 'postgres'),
                'database': os.getenv('POSTGRES_DATABASE', 'valido')
            },
            'mongodb': {
                'host': os.getenv('MONGODB_HOST', 'localhost'),
                'port': int(os.getenv('MONGODB_PORT', 27017)),
                'username': os.getenv('MONGODB_USERNAME'),
                'password': os.getenv('MONGODB_PASSWORD'),
                'database': os.getenv('MONGODB_DATABASE', 'valido')
            },
            'redis': {
                'host': os.getenv('REDIS_HOST', 'localhost'),
                'port': int(os.getenv('REDIS_PORT', 6379)),
                'password': os.getenv('REDIS_PASSWORD'),
                'db': int(os.getenv('REDIS_DB', 0))
            },
            'sqlite': {
                'database': os.getenv('SQLITE_DATABASE', 'data/sqlite/valido.db')
            }
        }
        return configs.get(db_type, configs['sqlite'])
