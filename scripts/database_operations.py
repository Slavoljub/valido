#!/usr/bin/env python3
"""
ValidoAI Database Operations (DRY Implementation)
Consolidated database management, migrations, and operations
"""

import os
import sys
import sqlite3
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

try:
    from config.unified_config import config
    from database.unified_db_manager import db
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure you're running from the project root")
    sys.exit(1)

class DatabaseOperations:
    """Consolidated database operations"""

    def __init__(self):
        self.db_path = config.database.path
        self.connection_pool = db.connection_pool if hasattr(db, 'connection_pool') else None

    def get_connection(self):
        """Get database connection"""
        if self.connection_pool:
            return self.connection_pool.get_connection()
        return sqlite3.connect(self.db_path)

    def execute_query(self, query: str, params: tuple = (), fetch: str = "all") -> Any:
        """Execute database query with proper connection management"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)

            if fetch == "one":
                result = cursor.fetchone()
            elif fetch == "all":
                result = cursor.fetchall()
            elif fetch == "none":
                result = None
                conn.commit()
            else:
                result = cursor.fetchall()

            return result
        finally:
            if self.connection_pool:
                self.connection_pool.return_connection(conn)
            else:
                conn.close()

    def create_tables(self):
        """Create all necessary database tables"""
        print("Creating database tables...")

        # Users table
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                first_name TEXT,
                last_name TEXT,
                is_admin BOOLEAN DEFAULT 0,
                is_active BOOLEAN DEFAULT 1,
                language TEXT DEFAULT 'sr',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """, fetch="none")

        # Settings table
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                setting_key TEXT UNIQUE NOT NULL,
                setting_value TEXT,
                setting_type TEXT DEFAULT 'string',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """, fetch="none")

        # Tickets table
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'open',
                priority TEXT DEFAULT 'medium',
                category TEXT,
                user_id INTEGER,
                assigned_to INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (assigned_to) REFERENCES users (id)
            )
        """, fetch="none")

        # Chat messages table
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                message TEXT NOT NULL,
                response TEXT,
                model_used TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """, fetch="none")

        print("✅ Database tables created successfully")

    def insert_default_data(self):
        """Insert default data"""
        print("Inserting default data...")

        # Insert default admin user if not exists
        try:
            from werkzeug.security import generate_password_hash
            admin_hash = generate_password_hash('admin123')
            self.execute_query("""
                INSERT OR IGNORE INTO users (
                    username, email, password_hash, first_name, last_name, is_admin, language
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, ('admin', 'admin@validoai.test', admin_hash, 'Admin', 'User', 1, 'sr'), fetch="none")
        except ImportError:
            print("Warning: Could not import werkzeug.security, skipping admin user creation")

        # Insert default settings
        default_settings = [
            ('app_name', 'ValidoAI', 'string'),
            ('app_version', '1.0.0', 'string'),
            ('default_language', 'sr', 'string'),
            ('timezone', 'Europe/Belgrade', 'string'),
            ('debug_mode', 'false', 'boolean'),
            ('maintenance_mode', 'false', 'boolean'),
        ]

        for key, value, setting_type in default_settings:
            self.execute_query("""
                INSERT OR IGNORE INTO settings (setting_key, setting_value, setting_type)
                VALUES (?, ?, ?)
            """, (key, value, setting_type), fetch="none")

        print("✅ Default data inserted successfully")

    def show_database_info(self):
        """Show database information and statistics"""
        print("📊 Database Information")
        print("=" * 50)

        # Table counts
        tables = ['users', 'settings', 'tickets', 'chat_messages']
        for table in tables:
            try:
                count = self.execute_query(f"SELECT COUNT(*) FROM {table}", fetch="one")[0]
                print("<20")
            except:
                print("<20")

        print("\n📈 Recent Activity")

        # Recent users
        recent_users = self.execute_query("""
            SELECT username, email, created_at
            FROM users
            ORDER BY created_at DESC
            LIMIT 5
        """, fetch="all")

        if recent_users:
            print("\nRecent Users:")
            for user in recent_users:
                print(f"  - {user[0]} ({user[1]}) - {user[2]}")

        # Recent tickets
        recent_tickets = self.execute_query("""
            SELECT title, status, created_at
            FROM tickets
            ORDER BY created_at DESC
            LIMIT 5
        """, fetch="all")

        if recent_tickets:
            print("\nRecent Tickets:")
            for ticket in recent_tickets:
                print(f"  - {ticket[0]} [{ticket[1]}] - {ticket[2]}")

    def backup_database(self, backup_path: Optional[str] = None):
        """Create database backup"""
        if backup_path is None:
            backup_dir = Path(self.db_path).parent / 'backups'
            backup_dir.mkdir(exist_ok=True)
            backup_path = backup_dir / f"backup_{Path(self.db_path).stem}_{self.get_timestamp()}.db"

        print(f"Creating backup: {backup_path}")

        # For SQLite, we can just copy the file
        import shutil
        shutil.copy2(self.db_path, backup_path)

        print(f"✅ Database backup created: {backup_path}")
        return backup_path

    def get_timestamp(self) -> str:
        """Get current timestamp for backup naming"""
        from datetime import datetime
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    def cleanup_old_backups(self, keep_days: int = 30):
        """Clean up old backup files"""
        backup_dir = Path(self.db_path).parent / 'backups'
        if not backup_dir.exists():
            return

        from datetime import datetime, timedelta
        cutoff_date = datetime.now() - timedelta(days=keep_days)

        deleted_count = 0
        for backup_file in backup_dir.glob("*.db"):
            file_date = datetime.fromtimestamp(backup_file.stat().st_mtime)
            if file_date < cutoff_date:
                backup_file.unlink()
                deleted_count += 1

        if deleted_count > 0:
            print(f"🧹 Cleaned up {deleted_count} old backup files")

def main():
    parser = argparse.ArgumentParser(description='ValidoAI Database Operations')
    parser.add_argument('action', choices=[
        'create', 'info', 'backup', 'cleanup', 'migrate'
    ], help='Action to perform')
    parser.add_argument('--backup-path', help='Custom backup path')
    parser.add_argument('--keep-days', type=int, default=30, help='Days to keep backups')

    args = parser.parse_args()

    db_ops = DatabaseOperations()

    try:
        if args.action == 'create':
            db_ops.create_tables()
            db_ops.insert_default_data()

        elif args.action == 'info':
            db_ops.show_database_info()

        elif args.action == 'backup':
            db_ops.backup_database(args.backup_path)

        elif args.action == 'cleanup':
            db_ops.cleanup_old_backups(args.keep_days)

        elif args.action == 'migrate':
            print("Running database migrations...")
            db_ops.create_tables()
            print("✅ Database migrations completed")

        print("🎉 Operation completed successfully!")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
