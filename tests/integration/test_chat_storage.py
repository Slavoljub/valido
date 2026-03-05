#!/usr/bin/env python3
"""
Test suite for Chat Artifact Storage System
Tests artifact-based chat storage functionality
"""

import unittest
import tempfile
import os
from pathlib import Path
from src.ai_local_models.chat_storage import ChatArtifactStorage, ChatArtifact


class TestChatArtifactStorage(unittest.TestCase):
    """Test cases for ChatArtifactStorage"""

    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_chat.db")
        self.storage = ChatArtifactStorage(db_path=self.db_path)

        # Create the required tables in the test database
        import sqlite3
        with sqlite3.connect(self.db_path) as conn:
            # Create chat_sessions table for tests
            conn.execute("""
                CREATE TABLE IF NOT EXISTS chat_sessions (
                    id INTEGER PRIMARY KEY,
                    session_uuid TEXT NOT NULL UNIQUE,
                    user_id INTEGER,
                    model_name VARCHAR(255) NOT NULL,
                    model_provider VARCHAR(100) NOT NULL,
                    session_name VARCHAR(255),
                    session_type VARCHAR(50) DEFAULT 'conversation',
                    context_data TEXT,
                    settings_data TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    message_count INTEGER DEFAULT 0
                )
            """)
            conn.commit()

    def tearDown(self):
        """Clean up test environment"""
        # Close the storage to ensure database connections are closed
        if hasattr(self, 'storage'):
            self.storage.close()

        # Try to remove the database file with retries (Windows file locking)
        import time
        max_retries = 5
        for attempt in range(max_retries):
            try:
                if os.path.exists(self.db_path):
                    os.remove(self.db_path)
                break
            except PermissionError:
                if attempt < max_retries - 1:
                    time.sleep(0.1)  # Wait a bit before retrying
                else:
                    # If we still can't delete it, just leave it (test cleanup)
                    print(f"Warning: Could not delete {self.db_path} (file in use)")

        # Clean up temp directory
        try:
            os.rmdir(self.temp_dir)
        except OSError:
            pass  # Directory might not be empty, that's OK

    def test_create_session(self):
        """Test session creation"""
        session_id = self.storage.create_session(
            session_id="test_session_1",
            user_id="user123",
            title="Test Session",
            model_name="llama2-7b"
        )

        self.assertEqual(session_id, "test_session_1")

        # Verify session was created
        sessions = self.storage.get_sessions()
        self.assertEqual(len(sessions), 1)
        self.assertEqual(sessions[0]["session_id"], "test_session_1")
        self.assertEqual(sessions[0]["title"], "Test Session")

    def test_save_and_get_messages(self):
        """Test saving and retrieving messages"""
        session_id = "test_session_1"
        self.storage.create_session(session_id, model_name="test-model")

        # Save a message
        message_id = self.storage.save_message(
            session_id=session_id,
            role="user",
            content="Hello, AI!",
            metadata={"tokens": 3}
        )

        self.assertIsNotNone(message_id)

        # Get chat history
        messages = self.storage.get_chat_history(session_id)
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0]["role"], "user")
        self.assertEqual(messages[0]["content"], "Hello, AI!")
        self.assertEqual(messages[0]["metadata"]["tokens"], 3)

    def test_create_and_get_artifact(self):
        """Test artifact creation and retrieval"""
        session_id = "test_session_1"
        self.storage.create_session(session_id, model_name="test-model")

        # Create artifact
        artifact = self.storage.create_artifact(
            session_id=session_id,
            title="Test Conversation",
            content="This is a test conversation artifact",
            artifact_type="conversation",
            metadata={"importance": "high"}
        )

        self.assertIsNotNone(artifact.artifact_id)
        self.assertEqual(artifact.session_id, session_id)
        self.assertEqual(artifact.title, "Test Conversation")
        self.assertEqual(artifact.content, "This is a test conversation artifact")

        # Get artifact
        retrieved = self.storage.get_artifact(artifact.artifact_id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.artifact_id, artifact.artifact_id)
        self.assertEqual(retrieved.title, "Test Conversation")

    def test_update_artifact(self):
        """Test artifact updating with versioning"""
        session_id = "test_session_1"
        self.storage.create_session(session_id, model_name="test-model")

        # Create artifact
        artifact = self.storage.create_artifact(
            session_id=session_id,
            title="Original Title",
            content="Original content"
        )

        original_version = artifact.version

        # Update artifact
        updated = self.storage.update_artifact(
            artifact_id=artifact.artifact_id,
            content="Updated content",
            title="Updated Title"
        )

        self.assertEqual(updated.title, "Updated Title")
        self.assertEqual(updated.content, "Updated content")
        self.assertEqual(updated.version, original_version + 1)

    def test_search_artifacts(self):
        """Test artifact search functionality"""
        session_id = "test_session_1"
        self.storage.create_session(session_id, model_name="test-model")

        # Create multiple artifacts
        self.storage.create_artifact(
            session_id=session_id,
            title="Python Tutorial",
            content="Learn Python programming"
        )

        self.storage.create_artifact(
            session_id=session_id,
            title="JavaScript Guide",
            content="Master JavaScript development"
        )

        # Search for Python-related content
        results = self.storage.search_artifacts("Python")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].title, "Python Tutorial")

    def test_get_session_artifacts(self):
        """Test getting all artifacts for a session"""
        session_id = "test_session_1"
        self.storage.create_session(session_id, model_name="test-model")

        # Create multiple artifacts
        self.storage.create_artifact(
            session_id=session_id,
            title="Artifact 1",
            content="Content 1"
        )

        self.storage.create_artifact(
            session_id=session_id,
            title="Artifact 2",
            content="Content 2"
        )

        artifacts = self.storage.get_session_artifacts(session_id)
        self.assertEqual(len(artifacts), 2)

        titles = [a.title for a in artifacts]
        self.assertIn("Artifact 1", titles)
        self.assertIn("Artifact 2", titles)

    def test_delete_artifact(self):
        """Test artifact deletion"""
        session_id = "test_session_1"
        self.storage.create_session(session_id, model_name="test-model")

        # Create artifact
        artifact = self.storage.create_artifact(
            session_id=session_id,
            title="Test Artifact",
            content="Test content"
        )

        # Verify it exists
        self.assertIsNotNone(self.storage.get_artifact(artifact.artifact_id))

        # Delete artifact
        success = self.storage.delete_artifact(artifact.artifact_id)
        self.assertTrue(success)

        # Verify it's gone
        self.assertIsNone(self.storage.get_artifact(artifact.artifact_id))

    def test_artifact_to_dict_from_dict(self):
        """Test artifact serialization"""
        artifact = ChatArtifact(
            artifact_id="test_id",
            session_id="test_session",
            title="Test Title",
            content="Test Content",
            metadata={"key": "value"}
        )

        # Convert to dict
        artifact_dict = artifact.to_dict()
        self.assertEqual(artifact_dict["artifact_id"], "test_id")
        self.assertEqual(artifact_dict["title"], "Test Title")
        self.assertEqual(artifact_dict["metadata"], '{"key": "value"}')

        # Convert back from dict
        restored = ChatArtifact.from_dict(artifact_dict)
        self.assertEqual(restored.artifact_id, artifact.artifact_id)
        self.assertEqual(restored.title, artifact.title)
        self.assertEqual(restored.metadata, {"key": "value"})


if __name__ == '__main__':
    unittest.main()
