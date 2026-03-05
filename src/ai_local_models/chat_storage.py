#!/usr/bin/env python3
"""
Artifact-based Chat Storage System
Handles storage and retrieval of chat conversations using artifact-based approach
"""

import logging
import sqlite3
import json
import uuid
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path
import hashlib

logger = logging.getLogger(__name__)

class ChatArtifact:
    """Represents a chat artifact with metadata"""

    def __init__(self, artifact_id: str = None, session_id: str = None,
                 artifact_type: str = "conversation", title: str = None,
                 content: str = None, metadata: Dict[str, Any] = None):
        self.artifact_id = artifact_id or str(uuid.uuid4())
        self.session_id = session_id
        self.artifact_type = artifact_type
        self.title = title or f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        self.content = content or ""
        self.metadata = metadata or {}
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
        self.version = 1

    def to_dict(self) -> Dict[str, Any]:
        """Convert artifact to dictionary"""
        return {
            "artifact_id": self.artifact_id,
            "session_id": self.session_id,
            "artifact_type": self.artifact_type,
            "title": self.title,
            "content": self.content,
            "metadata": json.dumps(self.metadata),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "version": self.version
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChatArtifact':
        """Create artifact from dictionary"""
        artifact = cls(
            artifact_id=data.get("artifact_id"),
            session_id=data.get("session_id"),
            artifact_type=data.get("artifact_type", "conversation"),
            title=data.get("title"),
            content=data.get("content"),
            metadata=json.loads(data.get("metadata", "{}"))
        )
        artifact.created_at = data.get("created_at", datetime.now().isoformat())
        artifact.updated_at = data.get("updated_at", datetime.now().isoformat())
        artifact.version = data.get("version", 1)
        return artifact


class ChatArtifactStorage:
    """Artifact-based storage system for chat conversations"""

    def __init__(self, db_path: str = "data/sqlite/app.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()

    def _init_database(self):
        """Initialize database with artifact tables"""
        with sqlite3.connect(self.db_path) as conn:
            # Create artifact tables with different names to avoid conflicts
            conn.execute("""
                CREATE TABLE IF NOT EXISTS ai_chat_artifacts (
                    artifact_id TEXT PRIMARY KEY,
                    session_uuid TEXT NOT NULL,
                    artifact_type TEXT NOT NULL DEFAULT 'conversation',
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    metadata TEXT DEFAULT '{}',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    version INTEGER DEFAULT 1
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS ai_chat_messages (
                    message_id TEXT PRIMARY KEY,
                    session_uuid TEXT NOT NULL,
                    artifact_id TEXT,
                    role TEXT NOT NULL, -- 'user', 'assistant', 'system'
                    content TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    token_count INTEGER DEFAULT 0,
                    metadata TEXT DEFAULT '{}'
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS ai_artifact_versions (
                    version_id TEXT PRIMARY KEY,
                    artifact_id TEXT NOT NULL,
                    version_number INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    metadata TEXT DEFAULT '{}',
                    created_at TEXT NOT NULL
                )
            """)

            # Create indexes for better performance
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_ai_session_uuid ON ai_chat_artifacts(session_uuid)",
                "CREATE INDEX IF NOT EXISTS idx_ai_artifact_type ON ai_chat_artifacts(artifact_type)",
                "CREATE INDEX IF NOT EXISTS idx_ai_created_at ON ai_chat_artifacts(created_at)",
                "CREATE INDEX IF NOT EXISTS idx_ai_session_messages ON ai_chat_messages(session_uuid)",
                "CREATE INDEX IF NOT EXISTS idx_ai_artifact_messages ON ai_chat_messages(artifact_id)"
            ]

            for index_sql in indexes:
                try:
                    conn.execute(index_sql)
                except sqlite3.OperationalError as e:
                    logger.warning(f"Index creation failed (this is usually OK): {e}")

            conn.commit()

    def create_session(self, session_id: str, user_id: str = None,
                      title: str = None, model_name: str = None) -> str:
        """Create a new chat session"""
        session_id = session_id or str(uuid.uuid4())
        title = title or f"Chat Session {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        with sqlite3.connect(self.db_path) as conn:
            # Use the existing chat_sessions table structure with all required fields
            conn.execute("""
                INSERT INTO chat_sessions (
                    session_uuid, user_id, model_name, model_provider, session_name,
                    session_type, context_data, settings_data, created_at, updated_at, last_activity
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (session_id, user_id, model_name, "local", title,
                  "conversation", "{}", "{}", datetime.now().isoformat(),
                  datetime.now().isoformat(), datetime.now().isoformat()))
            conn.commit()

        logger.info(f"Created chat session: {session_id}")
        return session_id

    def save_message(self, session_id: str, role: str, content: str,
                    artifact_id: str = None, metadata: Dict[str, Any] = None) -> str:
        """Save a chat message"""
        message_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        metadata = metadata or {}

        # Ensure session exists
        self._ensure_session_exists(session_id)

        with sqlite3.connect(self.db_path) as conn:
            # Save to AI-specific messages table
            conn.execute("""
                INSERT INTO ai_chat_messages (message_id, session_uuid, artifact_id, role, content, timestamp, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (message_id, session_id, artifact_id, role, content, timestamp, json.dumps(metadata)))

            # Update session timestamp
            conn.execute("""
                UPDATE chat_sessions
                SET updated_at = ?
                WHERE session_uuid = ?
            """, (timestamp, session_id))

            conn.commit()

        logger.info(f"Saved message: {message_id} in session: {session_id}")
        return message_id

    def create_artifact(self, session_id: str, title: str, content: str,
                       artifact_type: str = "conversation",
                       metadata: Dict[str, Any] = None) -> ChatArtifact:
        """Create a new chat artifact"""
        artifact = ChatArtifact(
            session_id=session_id,
            artifact_type=artifact_type,
            title=title,
            content=content,
            metadata=metadata
        )

        # Ensure session exists
        self._ensure_session_exists(session_id)

        with sqlite3.connect(self.db_path) as conn:
            artifact_data = artifact.to_dict()
            conn.execute("""
                INSERT INTO ai_chat_artifacts
                (artifact_id, session_uuid, artifact_type, title, content, metadata, created_at, updated_at, version)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (artifact_data["artifact_id"], session_id,
                  artifact_data["artifact_type"], artifact_data["title"],
                  artifact_data["content"], artifact_data["metadata"],
                  artifact_data["created_at"], artifact_data["updated_at"],
                  artifact_data["version"]))
            conn.commit()

        logger.info(f"Created artifact: {artifact.artifact_id}")
        return artifact

    def update_artifact(self, artifact_id: str, content: str,
                       title: str = None, metadata: Dict[str, Any] = None) -> ChatArtifact:
        """Update an existing artifact"""
        with sqlite3.connect(self.db_path) as conn:
            # Get current artifact
            cursor = conn.execute("""
                SELECT * FROM ai_chat_artifacts WHERE artifact_id = ?
            """, (artifact_id,))
            row = cursor.fetchone()

            if not row:
                raise ValueError(f"Artifact not found: {artifact_id}")

            # Create new version
            version_number = row[8] + 1  # version is at index 8
            version_id = str(uuid.uuid4())

            conn.execute("""
                INSERT INTO ai_artifact_versions
                (version_id, artifact_id, version_number, content, metadata, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (version_id, artifact_id, version_number, row[4],  # content is at index 4
                  row[5], datetime.now().isoformat()))  # metadata is at index 5

            # Update artifact
            new_title = title or row[3]  # title is at index 3
            new_metadata = json.dumps(metadata or json.loads(row[5]))  # metadata is at index 5
            updated_at = datetime.now().isoformat()

            conn.execute("""
                UPDATE ai_chat_artifacts
                SET title = ?, content = ?, metadata = ?, updated_at = ?, version = ?
                WHERE artifact_id = ?
            """, (new_title, content, new_metadata, updated_at, version_number, artifact_id))

            conn.commit()

            # Return updated artifact
            cursor = conn.execute("""
                SELECT * FROM ai_chat_artifacts WHERE artifact_id = ?
            """, (artifact_id,))
            row = cursor.fetchone()

            columns = [desc[0] for desc in cursor.description]
            artifact_data = dict(zip(columns, row))
            # Convert session_uuid back to session_id for the artifact object
            artifact_data["session_id"] = artifact_data.pop("session_uuid")
            artifact = ChatArtifact.from_dict(artifact_data)

        logger.info(f"Updated artifact: {artifact_id} to version {version_number}")
        return artifact

    def get_artifact(self, artifact_id: str) -> Optional[ChatArtifact]:
        """Get an artifact by ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT * FROM ai_chat_artifacts WHERE artifact_id = ?
            """, (artifact_id,))
            row = cursor.fetchone()

            if row:
                columns = [desc[0] for desc in cursor.description]
                artifact_data = dict(zip(columns, row))
                # Convert session_uuid back to session_id for the artifact object
                artifact_data["session_id"] = artifact_data.pop("session_uuid")
                return ChatArtifact.from_dict(artifact_data)

        return None

    def get_session_artifacts(self, session_id: str) -> List[ChatArtifact]:
        """Get all artifacts for a session"""
        artifacts = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT * FROM ai_chat_artifacts
                WHERE session_uuid = ?
                ORDER BY created_at DESC
            """, (session_id,))

            columns = [desc[0] for desc in cursor.description]
            for row in cursor.fetchall():
                artifact_data = dict(zip(columns, row))
                # Convert session_uuid back to session_id for the artifact object
                artifact_data["session_id"] = artifact_data.pop("session_uuid")
                artifacts.append(ChatArtifact.from_dict(artifact_data))

        return artifacts

    def get_chat_history(self, session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get chat history for a session"""
        messages = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT message_id, role, content, timestamp, metadata
                FROM ai_chat_messages
                WHERE session_uuid = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (session_id, limit))

            for row in cursor.fetchall():
                messages.append({
                    "message_id": row[0],
                    "role": row[1],
                    "content": row[2],
                    "timestamp": row[3],
                    "metadata": json.loads(row[4])
                })

        return list(reversed(messages))  # Return oldest first

    def search_artifacts(self, query: str, session_id: str = None,
                        artifact_type: str = None, limit: int = 20) -> List[ChatArtifact]:
        """Search artifacts by content or title"""
        artifacts = []
        sql = """
            SELECT * FROM ai_chat_artifacts
            WHERE (title LIKE ? OR content LIKE ?)
        """
        params = [f"%{query}%", f"%{query}%"]

        if session_id:
            sql += " AND session_uuid = ?"
            params.append(session_id)

        if artifact_type:
            sql += " AND artifact_type = ?"
            params.append(artifact_type)

        sql += " ORDER BY updated_at DESC LIMIT ?"
        params.append(limit)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(sql, params)
            columns = [desc[0] for desc in cursor.description]

            for row in cursor.fetchall():
                artifact_data = dict(zip(columns, row))
                # Convert session_uuid back to session_id for the artifact object
                artifact_data["session_id"] = artifact_data.pop("session_uuid")
                artifacts.append(ChatArtifact.from_dict(artifact_data))

        return artifacts

    def get_sessions(self, user_id: str = None, limit: int = 20) -> List[Dict[str, Any]]:
        """Get chat sessions"""
        sessions = []
        with sqlite3.connect(self.db_path) as conn:
            sql = """
                SELECT s.session_uuid, s.user_id, s.session_name, s.model_name,
                       s.created_at, s.updated_at, s.is_active,
                       COUNT(m.message_id) as message_count
                FROM chat_sessions s
                LEFT JOIN ai_chat_messages m ON s.session_uuid = m.session_uuid
            """
            params = []

            if user_id:
                sql += " WHERE s.user_id = ?"
                params.append(user_id)

            sql += " GROUP BY s.session_uuid ORDER BY s.updated_at DESC LIMIT ?"
            params.append(limit)

            cursor = conn.execute(sql, params)

            for row in cursor.fetchall():
                sessions.append({
                    "session_id": row[0],
                    "user_id": row[1],
                    "title": row[2],
                    "model_name": row[3],
                    "created_at": row[4],
                    "updated_at": row[5],
                    "is_active": bool(row[6]),
                    "message_count": row[7]
                })

        return sessions

    def delete_artifact(self, artifact_id: str) -> bool:
        """Delete an artifact"""
        with sqlite3.connect(self.db_path) as conn:
            # Delete artifact versions first
            conn.execute("DELETE FROM ai_artifact_versions WHERE artifact_id = ?", (artifact_id,))

            # Delete associated messages
            conn.execute("UPDATE ai_chat_messages SET artifact_id = NULL WHERE artifact_id = ?", (artifact_id,))

            # Delete artifact
            cursor = conn.execute("DELETE FROM ai_chat_artifacts WHERE artifact_id = ?", (artifact_id,))
            conn.commit()

            return cursor.rowcount > 0

    def _ensure_session_exists(self, session_id: str):
        """Ensure a session exists, create if not"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT session_uuid FROM chat_sessions WHERE session_uuid = ?", (session_id,))
            if not cursor.fetchone():
                self.create_session(session_id)

    def close(self):
        """Close any open connections (for testing)"""
        # SQLite connections are automatically closed when using 'with' statements
        # This method exists for compatibility and future use
        pass


# Global instance - only create when needed
_chat_storage_instance = None

def get_chat_storage() -> ChatArtifactStorage:
    """Get the global chat storage instance"""
    global _chat_storage_instance
    if _chat_storage_instance is None:
        _chat_storage_instance = ChatArtifactStorage()
    return _chat_storage_instance

# For backward compatibility
chat_storage = get_chat_storage()
