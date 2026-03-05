"""
SQLite Connection Manager
========================

Properly manages SQLite database connections to prevent resource warnings.
Provides context managers and connection pooling for SQLite databases.
"""

import sqlite3
import threading
from typing import Optional, Any, Dict
from contextlib import contextmanager
import warnings

# Import standard logging to avoid conflicts
import logging as std_logging
logger = std_logging.getLogger(__name__)

class SQLiteConnectionManager:
    """Thread-safe SQLite connection manager"""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._connections = {}
                    cls._instance._connection_count = 0
        return cls._instance

    def __init__(self):
        # Only initialize once
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self._connections: Dict[str, sqlite3.Connection] = {}
            self._connection_count = 0
            self.max_connections = 10

            # Suppress SQLite resource warnings
            warnings.filterwarnings("ignore", category=ResourceWarning, module="sqlite3")

    @contextmanager
    def get_connection(self, db_path: str = "data/sqlite/app.db"):
        """Get a SQLite connection with automatic cleanup"""
        connection = None
        try:
            # Create connection with proper configuration
            connection = sqlite3.connect(
                db_path,
                check_same_thread=False,  # Allow multi-thread access
                isolation_level=None,    # Autocommit mode
                cached_statements=100,   # Cache prepared statements
                timeout=20.0             # Connection timeout
            )

            # Enable foreign key support
            connection.execute("PRAGMA foreign_keys = ON")

            # Enable WAL mode for better concurrency
            connection.execute("PRAGMA journal_mode = WAL")

            # Set synchronous mode for better performance
            connection.execute("PRAGMA synchronous = NORMAL")

            # Enable memory-mapped I/O for better performance
            connection.execute("PRAGMA mmap_size = 268435456")  # 256MB

            # Set cache size
            connection.execute("PRAGMA cache_size = -64000")  # 64MB cache

            logger.debug(f"✅ SQLite connection established: {db_path}")

            yield connection

        except Exception as e:
            logger.error(f"❌ SQLite connection error: {e}")
            raise
        finally:
            if connection:
                try:
                    connection.close()
                    logger.debug(f"✅ SQLite connection closed: {db_path}")
                except Exception as e:
                    logger.warning(f"⚠️ Error closing SQLite connection: {e}")

    def execute_query(self, query: str, params: tuple = (), db_path: str = "data/sqlite/app.db") -> list:
        """Execute a query with automatic connection management"""
        with self.get_connection(db_path) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(query, params)
                if query.strip().upper().startswith(('SELECT', 'PRAGMA')):
                    return cursor.fetchall()
                else:
                    conn.commit()
                    return []
            except Exception as e:
                logger.error(f"❌ Query execution error: {e}")
                conn.rollback()
                raise
            finally:
                cursor.close()

    def execute_many(self, query: str, params_list: list, db_path: str = "data/sqlite/app.db") -> None:
        """Execute multiple queries with automatic connection management"""
        with self.get_connection(db_path) as conn:
            cursor = conn.cursor()
            try:
                cursor.executemany(query, params_list)
                conn.commit()
            except Exception as e:
                logger.error(f"❌ Batch execution error: {e}")
                conn.rollback()
                raise
            finally:
                cursor.close()

    def create_tables(self, schema_sql: str, db_path: str = "data/sqlite/app.db") -> None:
        """Create database tables with proper error handling"""
        try:
            # Split schema into individual statements
            statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]

            for statement in statements:
                if statement.upper().startswith(('CREATE', 'INSERT', 'UPDATE', 'DELETE')):
                    self.execute_query(statement, db_path=db_path)

            logger.info(f"✅ Database tables created successfully: {db_path}")

        except Exception as e:
            logger.error(f"❌ Error creating database tables: {e}")
            raise

    def backup_database(self, db_path: str = "data/sqlite/app.db", backup_path: str = None) -> str:
        """Create a backup of the database"""
        if not backup_path:
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"{db_path}.backup_{timestamp}"

        try:
            with self.get_connection(db_path) as source_conn:
                # Create backup using SQLite backup API
                backup_conn = sqlite3.connect(backup_path)
                with backup_conn:
                    source_conn.backup(backup_conn)
                backup_conn.close()

            logger.info(f"✅ Database backup created: {backup_path}")
            return backup_path

        except Exception as e:
            logger.error(f"❌ Database backup failed: {e}")
            raise

    def optimize_database(self, db_path: str = "data/sqlite/app.db") -> None:
        """Optimize database performance"""
        try:
            # Vacuum database to reclaim space
            self.execute_query("VACUUM;", db_path=db_path)

            # Analyze database for query optimization
            self.execute_query("ANALYZE;", db_path=db_path)

            # Rebuild indexes
            self.execute_query("REINDEX;", db_path=db_path)

            logger.info(f"✅ Database optimized: {db_path}")

        except Exception as e:
            logger.error(f"❌ Database optimization failed: {e}")
            raise

    def get_database_stats(self, db_path: str = "data/sqlite/app.db") -> Dict[str, Any]:
        """Get database statistics"""
        stats = {}

        try:
            # Get table information
            tables = self.execute_query(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';",
                db_path=db_path
            )
            stats['tables'] = [table[0] for table in tables]

            # Get database size
            import os
            if os.path.exists(db_path):
                stats['size_bytes'] = os.path.getsize(db_path)
                stats['size_mb'] = stats['size_bytes'] / (1024 * 1024)
            else:
                stats['size_bytes'] = 0
                stats['size_mb'] = 0

            # Get row counts for each table
            table_counts = {}
            for table in stats['tables']:
                try:
                    count = self.execute_query(f"SELECT COUNT(*) FROM {table};", db_path=db_path)
                    table_counts[table] = count[0][0] if count else 0
                except Exception:
                    table_counts[table] = 0

            stats['table_counts'] = table_counts
            stats['total_rows'] = sum(table_counts.values())

            logger.info(f"✅ Database stats retrieved: {stats['total_rows']} total rows")

        except Exception as e:
            logger.error(f"❌ Error getting database stats: {e}")
            stats['error'] = str(e)

        return stats

# Global instance
sqlite_manager = SQLiteConnectionManager()

# Convenience functions
@contextmanager
def get_sqlite_connection(db_path: str = "data/sqlite/app.db"):
    """Context manager for SQLite connections"""
    yield sqlite_manager.get_connection(db_path)

def execute_sqlite_query(query: str, params: tuple = (), db_path: str = "data/sqlite/app.db") -> list:
    """Execute SQLite query with automatic connection management"""
    return sqlite_manager.execute_query(query, params, db_path)

def execute_sqlite_many(query: str, params_list: list, db_path: str = "data/sqlite/app.db") -> None:
    """Execute multiple SQLite queries"""
    sqlite_manager.execute_many(query, params_list, db_path)

def create_sqlite_tables(schema_sql: str, db_path: str = "data/sqlite/app.db") -> None:
    """Create SQLite database tables"""
    sqlite_manager.create_tables(schema_sql, db_path)

def backup_sqlite_database(db_path: str = "data/sqlite/app.db", backup_path: str = None) -> str:
    """Create SQLite database backup"""
    return sqlite_manager.backup_database(db_path, backup_path)

def optimize_sqlite_database(db_path: str = "data/sqlite/app.db") -> None:
    """Optimize SQLite database"""
    sqlite_manager.optimize_database(db_path)

def get_sqlite_stats(db_path: str = "data/sqlite/app.db") -> Dict[str, Any]:
    """Get SQLite database statistics"""
    return sqlite_manager.get_database_stats(db_path)

if __name__ == "__main__":
    # Test the connection manager
    print("🧪 Testing SQLite Connection Manager...")

    # Test basic connection
    with get_sqlite_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT sqlite_version();")
        version = cursor.fetchone()
        print(f"✅ SQLite version: {version[0]}")

    # Test query execution
    result = execute_sqlite_query("SELECT 1 as test;")
    print(f"✅ Query result: {result}")

    # Test database stats
    stats = get_sqlite_stats()
    print(f"✅ Database stats: {stats}")

    print("✅ All SQLite connection manager tests passed!")
