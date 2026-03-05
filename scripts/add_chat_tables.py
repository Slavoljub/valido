#!/usr/bin/env python3
"""
Add Chat Sessions and Artifacts Tables to ValidoAI Database
"""

import sqlite3
import os
from pathlib import Path

def add_chat_tables():
    """Add chat sessions and artifacts tables to app.db"""
    
    db_path = Path("data/sqlite/app.db")
    
    if not db_path.exists():
        print(f"Database not found: {db_path}")
        return
    
    # Create uploads directory structure
    uploads_dir = Path("uploads")
    uploads_dir.mkdir(exist_ok=True)
    
    chat_uploads_dir = uploads_dir / "chat"
    chat_uploads_dir.mkdir(exist_ok=True)
    
    print(f"Adding chat tables to {db_path}")
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Create chat_sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_uuid TEXT UNIQUE NOT NULL,
                    user_id INTEGER,
                    model_name VARCHAR(255) NOT NULL,
                    model_provider VARCHAR(100) NOT NULL,
                    session_name VARCHAR(255),
                    session_type VARCHAR(50) DEFAULT 'conversation',
                    context_data TEXT,
                    settings_data TEXT,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    message_count INTEGER DEFAULT 0,
                    total_tokens INTEGER DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            
            # Create chat_messages table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message_uuid TEXT UNIQUE NOT NULL,
                    session_id INTEGER NOT NULL,
                    role VARCHAR(50) NOT NULL,
                    content TEXT NOT NULL,
                    message_type VARCHAR(50) DEFAULT 'text',
                    tokens_used INTEGER DEFAULT 0,
                    response_time_ms INTEGER,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES chat_sessions(id)
                )
            """)
            
            # Create artifacts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS artifacts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    artifact_uuid TEXT UNIQUE NOT NULL,
                    session_id INTEGER,
                    message_id INTEGER,
                    artifact_type VARCHAR(100) NOT NULL,
                    artifact_name VARCHAR(255) NOT NULL,
                    file_path VARCHAR(500),
                    file_size INTEGER,
                    mime_type VARCHAR(100),
                    metadata TEXT,
                    is_public BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NULL,
                    FOREIGN KEY (session_id) REFERENCES chat_sessions(id),
                    FOREIGN KEY (message_id) REFERENCES chat_messages(id)
                )
            """)
            
            # Create indexes
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_chat_sessions_uuid ON chat_sessions(session_uuid)",
                "CREATE INDEX IF NOT EXISTS idx_chat_sessions_user_id ON chat_sessions(user_id)",
                "CREATE INDEX IF NOT EXISTS idx_chat_sessions_model ON chat_sessions(model_name)",
                "CREATE INDEX IF NOT EXISTS idx_chat_sessions_created_at ON chat_sessions(created_at)",
                "CREATE INDEX IF NOT EXISTS idx_chat_messages_uuid ON chat_messages(message_uuid)",
                "CREATE INDEX IF NOT EXISTS idx_chat_messages_session_id ON chat_messages(session_id)",
                "CREATE INDEX IF NOT EXISTS idx_chat_messages_role ON chat_messages(role)",
                "CREATE INDEX IF NOT EXISTS idx_chat_messages_created_at ON chat_messages(created_at)",
                "CREATE INDEX IF NOT EXISTS idx_artifacts_uuid ON artifacts(artifact_uuid)",
                "CREATE INDEX IF NOT EXISTS idx_artifacts_session_id ON artifacts(session_id)",
                "CREATE INDEX IF NOT EXISTS idx_artifacts_type ON artifacts(artifact_type)",
                "CREATE INDEX IF NOT EXISTS idx_artifacts_created_at ON artifacts(created_at)"
            ]
            
            for index in indexes:
                cursor.execute(index)
            
            conn.commit()
            print("Chat tables created successfully!")
            
            # Verify tables exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('chat_sessions', 'chat_messages', 'artifacts')")
            tables = cursor.fetchall()
            print(f"Created tables: {[table[0] for table in tables]}")
            
    except Exception as e:
        print(f"Error creating chat tables: {e}")

if __name__ == "__main__":
    add_chat_tables()
