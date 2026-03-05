#!/usr/bin/env python3
"""
Unified Database Manager
Consolidates all database connection patterns into a single manager
"""

import sqlite3
import logging
import time
import threading
from typing import Dict, Any, Optional, List, Tuple
from contextlib import contextmanager
from pathlib import Path

from ..config.unified_config import config

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseConnectionPool:
    """Thread-safe connection pool for SQLite with proper waiting"""

    def __init__(self, db_path: str, max_connections: int = 10, timeout: float = 30.0):
        self.db_path = db_path
        self.max_connections = max_connections
        self.timeout = timeout
        self.connections = []  # List of [connection, in_use, last_used]
        self._lock = threading.Lock()
        self._available = threading.Condition(self._lock)

    def get_connection(self) -> sqlite3.Connection:
        """Get a database connection from the pool with proper waiting"""
        start_time = time.time()

        with self._lock:
            while True:
                # Try to find an available connection
                for conn_info in self.connections:
                    if not conn_info[1]:  # Not in use
                        conn_info[1] = True  # Mark as in use
                        conn_info[2] = time.time()  # Update last used time
                        return conn_info[0]

                # If we haven't reached max connections, create a new one
                if len(self.connections) < self.max_connections:
                    try:
                        conn = sqlite3.connect(self.db_path)
                        conn.row_factory = sqlite3.Row
                        # Enable WAL mode for better concurrency
                        conn.execute("PRAGMA journal_mode=WAL")
                        conn.execute("PRAGMA synchronous=NORMAL")
                        conn.execute("PRAGMA cache_size=10000")
                        conn.execute("PRAGMA foreign_keys=ON")

                        self.connections.append([conn, True, time.time()])
                        return conn
                    except Exception as e:
                        logger.error(f"Failed to create new connection: {e}")
                        raise

                # Wait for an available connection
                elapsed_time = time.time() - start_time
                if elapsed_time >= self.timeout:
                    raise Exception(f"Connection pool timeout after {elapsed_time:.1f}s")

                remaining_time = self.timeout - elapsed_time
                self._available.wait(timeout=remaining_time)

    def return_connection(self, connection: sqlite3.Connection):
        """Return connection to pool"""
        with self._lock:
            for conn_info in self.connections:
                if conn_info[0] == connection:
                    conn_info[1] = False  # Mark as available
                    self._available.notify()  # Wake up waiting threads
                    break

    def close_all(self):
        """Close all connections"""
        with self._lock:
            for conn_info in self.connections:
                try:
                    conn_info[0].close()
                except Exception as e:
                    logger.error(f"Error closing connection: {e}")
            self.connections.clear()

    def get_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics"""
        with self._lock:
            total = len(self.connections)
            available = sum(1 for conn in self.connections if not conn[1])
            in_use = total - available

            return {
                'total_connections': total,
                'available_connections': available,
                'in_use_connections': in_use,
                'max_connections': self.max_connections,
                'utilization_percent': (in_use / self.max_connections * 100) if self.max_connections > 0 else 0
            }

class UnifiedDatabaseManager:
    """Unified database manager for all database operations"""

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.db_path = config.database.path
            self.connection_pool = DatabaseConnectionPool(self.db_path, config.database.max_connections)
            self._initialized = True

            # Ensure database directory exists
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

            # Skip table creation for PostgreSQL - tables are created via SQL scripts
            pass

            logger.info(f"✅ Database manager initialized: {self.db_path}")

    def get_connection_stats(self) -> Dict[str, Any]:
        """Get database connection statistics"""
        return self.connection_pool.get_stats()

    def create_cursor(self, connection: sqlite3.Connection):
        """Create a cursor with appropriate settings based on database type"""
        from ..config.unified_config import config

        if config.database.type == "postgresql":
            try:
                import psycopg2.extras
                return connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            except ImportError:
                logger.warning("psycopg2 not available, falling back to regular cursor")
                return connection.cursor()
        else:
            # For SQLite and other databases, use regular cursor
            return connection.cursor()

    @contextmanager
    def get_connection(self):
        """Get database connection with context manager"""

        conn = self.connection_pool.get_connection()
        try:
            yield conn
        finally:
            self.connection_pool.return_connection(conn)

    def execute_query(self, query: str, params: Tuple = (), fetch: str = "all") -> Any:
        """Execute database query"""

        with self.get_connection() as conn:
            try:
                cursor = self.create_cursor(conn)
                cursor.execute(query, params)

                if query.strip().upper().startswith(("INSERT", "UPDATE", "DELETE")):
                    conn.commit()
                    if fetch == "lastrowid":
                        return cursor.lastrowid
                    return cursor.rowcount

                if fetch == "one":
                    return cursor.fetchone()
                elif fetch == "all":
                    return cursor.fetchall()
                else:
                    return cursor.fetchall()

            except Exception as e:
                logger.error(f"Database query error: {e}")
                conn.rollback()
                raise

    def create_tables(self):
        """Create all necessary database tables"""

        tables = {
            'users': """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username VARCHAR(100) UNIQUE NOT NULL,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    first_name VARCHAR(100),
                    last_name VARCHAR(100),
                    avatar_url VARCHAR(255),
                    is_active BOOLEAN DEFAULT TRUE,
                    is_admin BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP NULL
                )
            """,

            'companies': '''
                CREATE TABLE IF NOT EXISTS companies (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    tax_number TEXT,
                    address TEXT,
                    phone TEXT,
                    email TEXT,
                    website TEXT,
                    registration_date DATE,
                    status TEXT DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''',

            'support_tickets': '''
                CREATE TABLE IF NOT EXISTS support_tickets (
                    id TEXT PRIMARY KEY,
                    ticket_number TEXT UNIQUE,
                    subject TEXT NOT NULL,
                    description TEXT NOT NULL,
                    requester_id TEXT,
                    agent_id TEXT,
                    priority TEXT DEFAULT 'medium',
                    status TEXT DEFAULT 'open',
                    type TEXT DEFAULT 'question',
                    tags TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    closed_at TIMESTAMP,
                    FOREIGN KEY (requester_id) REFERENCES users (id),
                    FOREIGN KEY (agent_id) REFERENCES users (id)
                )
            ''',

            'ticket_messages': '''
                CREATE TABLE IF NOT EXISTS ticket_messages (
                    id TEXT PRIMARY KEY,
                    ticket_id TEXT NOT NULL,
                    sender_id TEXT NOT NULL,
                    message TEXT NOT NULL,
                    message_type TEXT DEFAULT 'public',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (ticket_id) REFERENCES support_tickets (id),
                    FOREIGN KEY (sender_id) REFERENCES users (id)
                )
            ''',

            'chat_sessions': '''
                CREATE TABLE IF NOT EXISTS chat_sessions (
                    id TEXT PRIMARY KEY,
                    session_uuid TEXT UNIQUE,
                    session_name TEXT,
                    model_name TEXT DEFAULT 'qwen3-4b-gguf',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    message_count INTEGER DEFAULT 0,
                    company_id TEXT,
                    user_id TEXT NOT NULL,
                    FOREIGN KEY (company_id) REFERENCES companies (id),
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''',

            'chat_messages': '''
                CREATE TABLE IF NOT EXISTS chat_messages (
                    id TEXT PRIMARY KEY,
                    session_uuid TEXT NOT NULL,
                    message_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_uuid) REFERENCES chat_sessions (session_uuid)
                )
            ''',

            'ai_response_logs': '''
                CREATE TABLE IF NOT EXISTS ai_response_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    user_id TEXT,
                    company_id TEXT,
                    model_used TEXT NOT NULL,
                    prompt_tokens INTEGER NOT NULL,
                    response_tokens INTEGER NOT NULL,
                    total_tokens INTEGER NOT NULL,
                    response_time REAL NOT NULL,
                    safety_checks_passed BOOLEAN DEFAULT 1,
                    violations_found TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (company_id) REFERENCES companies (id)
                )
            ''',

            'error_logs': '''
                CREATE TABLE IF NOT EXISTS error_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    error_uuid TEXT,
                    error_hash TEXT,
                    error_type TEXT,
                    error_message TEXT,
                    error_code TEXT,
                    status_code INTEGER,
                    severity TEXT DEFAULT 'ERROR',
                    user_id TEXT,
                    session_id TEXT,
                    request_path TEXT,
                    request_method TEXT,
                    request_ip TEXT,
                    user_agent TEXT,
                    stack_trace TEXT,
                    error_details TEXT,
                    context_data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    resolved_at TIMESTAMP,
                    resolution_notes TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            '''
        }

        for table_name, create_query in tables.items():
            try:
                self.execute_query(create_query)
                logger.info(f"✅ Created/verified table: {table_name}")
            except Exception as e:
                logger.error(f"❌ Error creating table {table_name}: {e}")

    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""

        result = self.execute_query(
            "SELECT * FROM users WHERE id = ?",
            (user_id,),
            fetch="one"
        )

        if result:
            return dict(result)
        return None

    def get_users(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get list of users"""

        results = self.execute_query(
            "SELECT * FROM users ORDER BY created_at DESC LIMIT ?",
            (limit,),
            fetch="all"
        )

        return [dict(row) for row in results]

    def create_user(self, user_data: Dict[str, Any]) -> int:
        """Create new user"""

        query = """
            INSERT INTO users (
                id, username, email, password_hash, first_name, last_name, role
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """

        params = (
            user_data['id'],
            user_data.get('username'),
            user_data['email'],
            user_data['password_hash'],
            user_data.get('first_name'),
            user_data.get('last_name'),
            user_data.get('role', 'user')
        )

        return self.execute_query(query, params, fetch="lastrowid")

    def get_company(self, company_id: str) -> Optional[Dict[str, Any]]:
        """Get company by ID"""

        result = self.execute_query(
            "SELECT * FROM companies WHERE id = ?",
            (company_id,),
            fetch="one"
        )

        if result:
            return dict(result)
        return None

    def create_ticket(self, ticket_data: Dict[str, Any]) -> int:
        """Create support ticket"""

        query = """
            INSERT INTO support_tickets (
                id, ticket_number, subject, description, requester_id, agent_id, priority, status, type, tags
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        params = (
            ticket_data['id'],
            ticket_data.get('ticket_number'),
            ticket_data['subject'],
            ticket_data['description'],
            ticket_data.get('requester_id'),
            ticket_data.get('agent_id'),
            ticket_data.get('priority', 'medium'),
            ticket_data.get('status', 'open'),
            ticket_data.get('type', 'question'),
            ticket_data.get('tags')
        )

        return self.execute_query(query, params, fetch="lastrowid")

    def get_tickets(self, status: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get support tickets"""

        query = "SELECT * FROM support_tickets"
        params = []

        if status:
            query += " WHERE status = ?"
            params.append(status)

        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)

        results = self.execute_query(query, tuple(params), fetch="all")
        return [dict(row) for row in results]

    def log_error(self, error_data: Dict[str, Any]):
        """Log application error"""

        query = """
            INSERT INTO error_logs (
                error_uuid, error_hash, error_type, error_message, error_code, status_code,
                severity, user_id, session_id, request_path, request_method, request_ip,
                user_agent, stack_trace, error_details, context_data
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        params = (
            error_data.get('error_uuid'),
            error_data.get('error_hash'),
            error_data.get('error_type'),
            error_data.get('error_message'),
            error_data.get('error_code'),
            error_data.get('status_code'),
            error_data.get('severity', 'ERROR'),
            error_data.get('user_id'),
            error_data.get('session_id'),
            error_data.get('request_path'),
            error_data.get('request_method'),
            error_data.get('request_ip'),
            error_data.get('user_agent'),
            error_data.get('stack_trace'),
            error_data.get('error_details'),
            error_data.get('context_data')
        )

        self.execute_query(query, params)

    def log_ai_response(self, response_data: Dict[str, Any]):
        """Log AI model response"""

        query = """
            INSERT INTO ai_response_logs (
                session_id, user_id, company_id, model_used, prompt_tokens,
                response_tokens, total_tokens, response_time, safety_checks_passed, violations_found
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        params = (
            response_data.get('session_id'),
            response_data.get('user_id'),
            response_data.get('company_id'),
            response_data.get('model_used'),
            response_data.get('prompt_tokens'),
            response_data.get('response_tokens'),
            response_data.get('total_tokens'),
            response_data.get('response_time'),
            response_data.get('safety_checks_passed', True),
            response_data.get('violations_found')
        )

        self.execute_query(query, params)

    def get_statistics(self) -> Dict[str, int]:
        """Get database statistics"""

        stats = {}

        tables = ['users', 'companies', 'support_tickets', 'ticket_messages', 'chat_sessions', 'error_logs', 'ai_response_logs']

        for table in tables:
            try:
                result = self.execute_query(f"SELECT COUNT(*) as count FROM {table}", fetch="one")
                stats[table] = result['count']
            except:
                stats[table] = 0

        return stats

    def create_tables(self):
        """Create all database tables and insert default data"""

        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Settings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key VARCHAR(255) UNIQUE NOT NULL,
                    value TEXT,
                    category VARCHAR(100),
                    description TEXT,
                    is_public BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    deleted_at TIMESTAMP NULL
                )
            """)

            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username VARCHAR(100) UNIQUE NOT NULL,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    first_name VARCHAR(100),
                    last_name VARCHAR(100),
                    avatar_url VARCHAR(255),
                    is_active BOOLEAN DEFAULT TRUE,
                    is_admin BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP NULL
                )
            """)

            # Tickets table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tickets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title VARCHAR(255) NOT NULL,
                    description TEXT,
                    status VARCHAR(50) DEFAULT 'open',
                    priority VARCHAR(50) DEFAULT 'medium',
                    category VARCHAR(100),
                    assigned_to INTEGER,
                    created_by INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    deleted_at TIMESTAMP NULL,
                    FOREIGN KEY (assigned_to) REFERENCES users(id),
                    FOREIGN KEY (created_by) REFERENCES users(id)
                )
            """)

            # Chat messages table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    session_id VARCHAR(255),
                    message TEXT NOT NULL,
                    response TEXT,
                    model_used VARCHAR(100),
                    context_data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)

            # Insert default settings
            self._insert_default_settings(cursor)

            # Insert demo user
            self._insert_demo_user(cursor)

            conn.commit()
            logger.info("✅ Database tables created successfully")

    def _insert_default_settings(self, cursor):
        """Insert default application settings"""

        default_settings = [
            ('app_name', 'ValidoAI', 'general', 'Application name', True),
            ('app_description', 'AI-powered financial analysis system', 'general', 'Application description', True),
            ('company_name', 'ValidoAI Ltd.', 'general', 'Company name', True),
            ('company_email', 'info@valido.online', 'email', 'Company email address', True),
            ('smtp_host', 'smtp.gmail.com', 'email', 'SMTP server host', False),
            ('smtp_port', '587', 'email', 'SMTP server port', False),
            ('smtp_username', '', 'email', 'SMTP username', False),
            ('smtp_password', '', 'email', 'SMTP password', False),
            ('default_theme', 'valido-white', 'theme', 'Default application theme', True),
            ('enable_registration', 'true', 'security', 'Enable user registration', False),
            ('enable_file_upload', 'true', 'security', 'Enable file upload', False),
            ('max_file_size', '10485760', 'upload', 'Maximum file size in bytes', True),
            ('allowed_extensions', 'pdf,doc,docx,txt,csv,xlsx', 'upload', 'Allowed file extensions', True),
            ('default_language', 'sr', 'localization', 'Default application language', True),
            ('supported_languages', 'sr,en,de,fr,it', 'localization', 'Supported languages', True),
            ('timezone', 'Europe/Belgrade', 'localization', 'Default timezone', True),
            ('date_format', 'DD.MM.YYYY', 'localization', 'Date format', True),
            ('number_format', 'comma', 'localization', 'Number format (comma or dot)', True),
        ]

        for setting in default_settings:
            cursor.execute("""
                INSERT OR IGNORE INTO settings (key, value, category, description, is_public)
                VALUES (?, ?, ?, ?, ?)
            """, setting)

    def _insert_demo_user(self, cursor):
        """Insert demo user for testing"""

        import hashlib

        # Create demo user with hashed password
        demo_password = hashlib.sha256("demo123".encode()).hexdigest()

        # Skip demo user creation for now since we're using PostgreSQL
        # The demo user will be created through the PostgreSQL schema
        pass

    def health_check(self) -> Dict[str, Any]:
        """Database health check"""

        try:
            # Test basic query
            self.execute_query("SELECT 1", fetch="one")

            stats = self.get_statistics()

            return {
                'status': 'healthy',
                'connection': 'ok',
                'statistics': stats
            }

        except Exception as e:
            return {
                'status': 'unhealthy',
                'connection': 'failed',
                'error': str(e)
            }

    def backup_database(self, backup_path: str):
        """Create database backup"""

        try:
            import shutil
            shutil.copy2(self.db_path, backup_path)
            logger.info(f"✅ Database backed up to {backup_path}")
            return True
        except Exception as e:
            logger.error(f"❌ Backup failed: {e}")
            return False

    def cleanup(self):
        """Cleanup database manager"""

        self.connection_pool.close_all()
        logger.info("✅ Database manager cleaned up")

# Global database manager instance
db = UnifiedDatabaseManager()

def get_db():
    """Get database manager instance"""
    return db

if __name__ == "__main__":
    # Test the unified database manager
    print("🗄️ Unified Database Manager Test")
    print("=" * 40)

    # Create tables
    db.create_tables()

    # Get statistics
    stats = db.get_statistics()
    print("Database Statistics:")
    for table, count in stats.items():
        print(f"  {table}: {count} records")

    # Health check
    health = db.health_check()
    print(f"\nHealth Status: {health['status']}")
    print(f"Connection: {health['connection']}")

    print("\n✅ Database manager test completed")
