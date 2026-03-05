"""
Database Manager for AI Local Models
Handles database operations for AI models and configurations
"""

import logging
import sqlite3
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class DatabaseConfig:
    """Database configuration class"""
    type: str = "sqlite"
    host: str = "localhost"
    port: int = 5432
    database: str = "data/ai_local_models.db"
    username: str = ""
    password: str = ""
    ssl: bool = False
    timeout: int = 30

    def get_connection_string(self) -> str:
        """Get connection string for the database"""
        if self.type == "sqlite":
            return f"sqlite:///{self.database}"
        else:
            return f"{self.type}://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"

class AILocalDatabaseManager:
    """Database manager for AI local models"""

    def __init__(self, db_path: str = "data/ai_local_models.db"):
        """Initialize database manager"""
        self.db_path = db_path
        self._ensure_db_exists()

    def _ensure_db_exists(self):
        """Ensure database and tables exist"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Create models table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ai_models (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    model_name TEXT UNIQUE NOT NULL,
                    model_type TEXT NOT NULL,
                    model_path TEXT,
                    config JSON,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create model performance table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS model_performance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    model_id INTEGER,
                    metric_name TEXT NOT NULL,
                    metric_value REAL,
                    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (model_id) REFERENCES ai_models (id)
                )
            """)

            # Create downloads table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS model_downloads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    model_name TEXT NOT NULL,
                    download_url TEXT,
                    download_path TEXT,
                    status TEXT DEFAULT 'pending',
                    progress INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.commit()

    def get_model_config(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Get model configuration"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT config FROM ai_models WHERE model_name = ? AND is_active = 1",
                    (model_name,)
                )
                result = cursor.fetchone()
                return eval(result[0]) if result else None
        except Exception as e:
            logger.error(f"Error getting model config for {model_name}: {e}")
            return None

    def save_model_config(self, model_name: str, model_type: str, config: Dict[str, Any]):
        """Save model configuration"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO ai_models (model_name, model_type, config, updated_at)
                    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                """, (model_name, model_type, str(config)))
                conn.commit()
        except Exception as e:
            logger.error(f"Error saving model config for {model_name}: {e}")

    def get_all_models(self) -> List[Dict[str, Any]]:
        """Get all active models"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT model_name, model_type, config FROM ai_models WHERE is_active = 1"
                )
                results = cursor.fetchall()
                return [
                    {
                        'model_name': row[0],
                        'model_type': row[1],
                        'config': eval(row[2])
                    }
                    for row in results
                ]
        except Exception as e:
            logger.error(f"Error getting all models: {e}")
            return []

    def update_model_performance(self, model_name: str, metric_name: str, metric_value: float):
        """Update model performance metrics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO model_performance (model_id, metric_name, metric_value)
                    SELECT id, ?, ? FROM ai_models WHERE model_name = ?
                """, (metric_name, metric_value, model_name))
                conn.commit()
        except Exception as e:
            logger.error(f"Error updating performance for {model_name}: {e}")

    def start_download(self, model_name: str, download_url: str, download_path: str):
        """Start model download tracking"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO model_downloads (model_name, download_url, download_path)
                    VALUES (?, ?, ?)
                """, (model_name, download_url, download_path))
                conn.commit()
        except Exception as e:
            logger.error(f"Error starting download for {model_name}: {e}")

    def update_download_progress(self, model_name: str, progress: int, status: str = 'downloading'):
        """Update download progress"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE model_downloads
                    SET progress = ?, status = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE model_name = ?
                """, (progress, status, model_name))
                conn.commit()
        except Exception as e:
            logger.error(f"Error updating download progress for {model_name}: {e}")


# Global instance
ai_local_db = AILocalDatabaseManager()

# Alias for backward compatibility
GlobalDatabaseManager = AILocalDatabaseManager

# Create db_manager alias for compatibility with routes.py
db_manager = ai_local_db

# Export all public classes
__all__ = [
    'DatabaseConfig',
    'AILocalDatabaseManager',
    'GlobalDatabaseManager',
    'ai_local_db',
    'db_manager'
]
