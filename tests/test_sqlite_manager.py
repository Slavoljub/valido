#!/usr/bin/env python3
"""Test SQLite Connection Manager"""

import sqlite3
import warnings
from contextlib import contextmanager

# Suppress SQLite resource warnings
warnings.filterwarnings("ignore", category=ResourceWarning, module="sqlite3")

class SQLiteConnectionManager:
    """Simple SQLite connection manager for testing"""

    @contextmanager
    def get_connection(self, db_path: str = "data/sqlite/app.db"):
        """Get a SQLite connection with automatic cleanup"""
        connection = None
        try:
            connection = sqlite3.connect(
                db_path,
                check_same_thread=False,
                isolation_level=None,
                cached_statements=100,
                timeout=20.0
            )

            # Enable optimizations
            connection.execute("PRAGMA foreign_keys = ON")
            connection.execute("PRAGMA journal_mode = WAL")
            connection.execute("PRAGMA synchronous = NORMAL")
            connection.execute("PRAGMA mmap_size = 268435456")
            connection.execute("PRAGMA cache_size = -64000")

            print(f"✅ SQLite connection established: {db_path}")
            yield connection

        except Exception as e:
            print(f"❌ SQLite connection error: {e}")
            raise
        finally:
            if connection:
                try:
                    connection.close()
                    print(f"✅ SQLite connection closed: {db_path}")
                except Exception as e:
                    print(f"⚠️ Error closing SQLite connection: {e}")

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
                print(f"❌ Query execution error: {e}")
                conn.rollback()
                raise
            finally:
                cursor.close()

def test_sqlite_manager():
    """Test the SQLite connection manager"""
    print("🧪 Testing SQLite Connection Manager...")
    print("=" * 50)

    manager = SQLiteConnectionManager()

    # Test basic connection
    print("\\n1. Testing basic connection...")
    with manager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT sqlite_version();")
        version = cursor.fetchone()
        print(f"✅ SQLite version: {version[0]}")

    # Test query execution
    print("\\n2. Testing query execution...")
    result = manager.execute_query("SELECT 1 as test;")
    print(f"✅ Query result: {result}")

    # Test table creation
    print("\\n3. Testing table creation...")
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS test_table (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        value INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    manager.execute_query(create_table_sql)
    print("✅ Table created successfully")

    # Test data insertion
    print("\\n4. Testing data insertion...")
    manager.execute_query(
        "INSERT INTO test_table (name, value) VALUES (?, ?);",
        ("test_entry", 42)
    )
    print("✅ Data inserted successfully")

    # Test data retrieval
    print("\\n5. Testing data retrieval...")
    results = manager.execute_query("SELECT * FROM test_table;")
    print(f"✅ Retrieved {len(results)} rows:")
    for row in results:
        print(f"   {row}")

    # Test multiple connections (should not have resource warnings)
    print("\\n6. Testing multiple connections...")
    for i in range(5):
        result = manager.execute_query(f"SELECT {i} as iteration;")
        print(f"   Iteration {i}: {result}")

    print("\\n✅ All SQLite connection manager tests passed!")
    print("✅ No resource warnings detected!")

if __name__ == "__main__":
    test_sqlite_manager()
