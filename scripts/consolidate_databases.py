#!/usr/bin/env python3
"""
Database Consolidation Script for ValidoAI
Consolidates all database files into app.db and keeps only sample.db separate
"""

import sqlite3
import os
import shutil
from pathlib import Path

def consolidate_databases():
    """Consolidate all databases into app.db"""
    
    # Define paths
    data_dir = Path("data/sqlite")
    app_db_path = data_dir / "app.db"
    ticketing_db_path = data_dir / "ticketing.db"
    sample_db_path = data_dir / "sample.db"
    
    # Backup original app.db
    if app_db_path.exists():
        backup_path = data_dir / "app.db.backup"
        shutil.copy2(app_db_path, backup_path)
        print(f"Backed up app.db to {backup_path}")
    
    # Connect to main app.db
    app_conn = sqlite3.connect(app_db_path)
    app_cursor = app_conn.cursor()
    
    # Consolidate ticketing.db if it exists
    if ticketing_db_path.exists():
        print(f"Consolidating {ticketing_db_path} into {app_db_path}")
        
        # Connect to ticketing.db
        ticketing_conn = sqlite3.connect(ticketing_db_path)
        ticketing_cursor = ticketing_conn.cursor()
        
        # Get all tables from ticketing.db
        ticketing_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = ticketing_cursor.fetchall()
        
        for table in tables:
            table_name = table[0]
            print(f"  Processing table: {table_name}")
            
            # Get table schema
            ticketing_cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}';")
            schema = ticketing_cursor.fetchone()[0]
            
            # Create table in app.db if it doesn't exist
            try:
                app_cursor.execute(schema)
                print(f"    Created table: {table_name}")
            except sqlite3.OperationalError as e:
                if "already exists" not in str(e):
                    print(f"    Warning: {e}")
            
            # Copy data
            ticketing_cursor.execute(f"SELECT * FROM {table_name}")
            rows = ticketing_cursor.fetchall()
            
            if rows:
                # Get column count
                ticketing_cursor.execute(f"PRAGMA table_info({table_name})")
                columns = ticketing_cursor.fetchall()
                placeholders = ','.join(['?' for _ in columns])
                
                # Insert data
                app_cursor.executemany(f"INSERT OR IGNORE INTO {table_name} VALUES ({placeholders})", rows)
                print(f"    Copied {len(rows)} rows to {table_name}")
        
        # Close ticketing connection
        ticketing_conn.close()
        
        # Remove ticketing.db
        os.remove(ticketing_db_path)
        print(f"Removed {ticketing_db_path}")
    
    # Ensure error_logs table exists in app.db
    app_cursor.execute("""
        CREATE TABLE IF NOT EXISTS error_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            error_uuid TEXT UNIQUE NOT NULL,
            error_hash TEXT NOT NULL,
            error_type TEXT NOT NULL,
            error_message TEXT NOT NULL,
            error_code TEXT,
            status_code INTEGER,
            severity TEXT NOT NULL DEFAULT 'ERROR',
            user_id INTEGER,
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
            resolved_at TIMESTAMP NULL,
            resolution_notes TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    # Create indexes for error_logs
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_error_logs_uuid ON error_logs(error_uuid)",
        "CREATE INDEX IF NOT EXISTS idx_error_logs_hash ON error_logs(error_hash)",
        "CREATE INDEX IF NOT EXISTS idx_error_logs_type ON error_logs(error_type)",
        "CREATE INDEX IF NOT EXISTS idx_error_logs_created_at ON error_logs(created_at)",
        "CREATE INDEX IF NOT EXISTS idx_error_logs_severity ON error_logs(severity)",
        "CREATE INDEX IF NOT EXISTS idx_error_logs_user_id ON error_logs(user_id)"
    ]
    
    for index in indexes:
        app_cursor.execute(index)
    
    # Ensure settings table exists
    app_cursor.execute("""
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
    
    # Ensure users table exists
    app_cursor.execute("""
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
    
    # Ensure tickets table exists
    app_cursor.execute("""
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
    
    # Commit changes
    app_conn.commit()
    app_conn.close()
    
    print(f"Database consolidation completed successfully!")
    print(f"Main database: {app_db_path}")
    print(f"Sample database: {sample_db_path}")
    
    # List remaining database files
    remaining_dbs = [f for f in data_dir.glob("*.db")]
    print(f"Remaining database files: {[f.name for f in remaining_dbs]}")

if __name__ == "__main__":
    consolidate_databases()
