import sqlite3
import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

class SettingCategory(Enum):
    GENERAL = "general"
    EMAIL = "email"
    SECURITY = "security"
    THEME = "theme"
    UPLOAD = "upload"
    AI_MODELS = "ai_models"

@dataclass
class Setting:
    id: Optional[int]
    key: str
    value: str
    category: str
    description: str
    is_public: bool
    created_at: datetime
    updated_at: datetime

@dataclass
class AIModel:
    name: str
    status: str
    size: str
    provider: str
    model_id: str
    config_path: str
    download_url: str
    is_downloaded: bool
    last_updated: Optional[datetime]

class SettingsModel:
    """Settings model following MVVM pattern with real data handling"""
    
    def __init__(self, db_path: str = "data/sqlite/app.db"):
        self.db_path = db_path
        self.ensure_database_exists()
        self.initialize_default_settings()
    
    def ensure_database_exists(self):
        """Ensure database and tables exist"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key VARCHAR(255) UNIQUE NOT NULL,
                    value TEXT,
                    category VARCHAR(100) NOT NULL,
                    description TEXT,
                    is_public BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create AI models configuration table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS ai_models (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(255) NOT NULL,
                    model_id VARCHAR(255) UNIQUE NOT NULL,
                    provider VARCHAR(100) NOT NULL,
                    status VARCHAR(50) DEFAULT 'not_installed',
                    size VARCHAR(50),
                    config_path TEXT,
                    download_url TEXT,
                    is_downloaded BOOLEAN DEFAULT FALSE,
                    last_updated TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
    
    def initialize_default_settings(self):
        """Initialize default settings if they don't exist"""
        default_settings = [
            # General Settings
            ("app_name", "ValidoAI", SettingCategory.GENERAL.value, "Application name"),
            ("app_version", "1.0.0", SettingCategory.GENERAL.value, "Application version"),
            ("timezone", "Europe/Belgrade", SettingCategory.GENERAL.value, "Default timezone"),
            ("language", "en", SettingCategory.GENERAL.value, "Default language"),
            ("debug_mode", "false", SettingCategory.GENERAL.value, "Debug mode"),
            
            # Email Settings
            ("smtp_host", "localhost", SettingCategory.EMAIL.value, "SMTP server host"),
            ("smtp_port", "587", SettingCategory.EMAIL.value, "SMTP server port"),
            ("smtp_username", "", SettingCategory.EMAIL.value, "SMTP username"),
            ("smtp_password", "", SettingCategory.EMAIL.value, "SMTP password"),
            ("smtp_use_tls", "true", SettingCategory.EMAIL.value, "Use TLS for SMTP"),
            
            # Security Settings
            ("session_timeout", "3600", SettingCategory.SECURITY.value, "Session timeout in seconds"),
            ("max_login_attempts", "5", SettingCategory.SECURITY.value, "Maximum login attempts"),
            ("password_min_length", "8", SettingCategory.SECURITY.value, "Minimum password length"),
            ("require_2fa", "false", SettingCategory.SECURITY.value, "Require two-factor authentication"),
            
            # Theme Settings
            ("default_theme", "valido-white", SettingCategory.THEME.value, "Default theme"),
            ("enable_dark_mode", "true", SettingCategory.THEME.value, "Enable dark mode"),
            ("custom_css", "", SettingCategory.THEME.value, "Custom CSS"),
            
            # Upload Settings
            ("max_file_size", "10485760", SettingCategory.UPLOAD.value, "Maximum file size in bytes"),
            ("allowed_extensions", "jpg,jpeg,png,gif,pdf,doc,docx", SettingCategory.UPLOAD.value, "Allowed file extensions"),
            ("upload_path", "uploads", SettingCategory.UPLOAD.value, "Upload directory"),
        ]
        
        with sqlite3.connect(self.db_path) as conn:
            for key, value, category, description in default_settings:
                conn.execute("""
                    INSERT OR IGNORE INTO settings (key, value, category, description)
                    VALUES (?, ?, ?, ?)
                """, (key, value, category, description))
    
    def get_settings_by_category(self, category: str) -> List[Setting]:
        """Get settings by category"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM settings 
                WHERE category = ? 
                ORDER BY key
            """, (category,))
            
            return [Setting(
                id=row['id'],
                key=row['key'],
                value=row['value'],
                category=row['category'],
                description=row['description'],
                is_public=bool(row['is_public']),
                created_at=datetime.fromisoformat(row['created_at']),
                updated_at=datetime.fromisoformat(row['updated_at'])
            ) for row in cursor.fetchall()]
    
    def get_setting(self, key: str) -> Optional[Setting]:
        """Get a specific setting by key"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM settings WHERE key = ?", (key,))
            row = cursor.fetchone()
            
            if row:
                return Setting(
                    id=row['id'],
                    key=row['key'],
                    value=row['value'],
                    category=row['category'],
                    description=row['description'],
                    is_public=bool(row['is_public']),
                    created_at=datetime.fromisoformat(row['created_at']),
                    updated_at=datetime.fromisoformat(row['updated_at'])
                )
            return None
    
    def set_setting(self, key: str, value: str, category: str = "general") -> bool:
        """Set or update a setting"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO settings (key, value, category, updated_at)
                    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                """, (key, value, category))
                return True
        except Exception as e:
            print(f"Error setting setting {key}: {e}")
            return False
    
    def delete_setting(self, key: str) -> bool:
        """Soft delete a setting (mark as not public)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE settings 
                    SET is_public = FALSE, updated_at = CURRENT_TIMESTAMP
                    WHERE key = ?
                """, (key,))
                return True
        except Exception as e:
            print(f"Error deleting setting {key}: {e}")
            return False
    
    def get_ai_models(self) -> List[AIModel]:
        """Get AI models from database and local config"""
        models = []
        
        # Get models from database
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM ai_models ORDER BY name")
            
            for row in cursor.fetchall():
                models.append(AIModel(
                    name=row['name'],
                    status=row['status'],
                    size=row['size'] or "Unknown",
                    provider=row['provider'],
                    model_id=row['model_id'],
                    config_path=row['config_path'] or "",
                    download_url=row['download_url'] or "",
                    is_downloaded=bool(row['is_downloaded']),
                    last_updated=datetime.fromisoformat(row['last_updated']) if row['last_updated'] else None
                ))
        
        # If no models in database, load from local config
        if not models:
            models = self.load_models_from_config()
        
        return models
    
    def load_models_from_config(self) -> List[AIModel]:
        """Load AI models from local configuration file"""
        config_path = "src/ai_local_models/local_model_config.json"
        models = []
        
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = json.load(f)
                
                for model_config in config.get('models', []):
                    model = AIModel(
                        name=model_config.get('name', 'Unknown'),
                        status='not_installed',
                        size=model_config.get('size', 'Unknown'),
                        provider=model_config.get('provider', 'Local'),
                        model_id=model_config.get('model_id', ''),
                        config_path=model_config.get('config_path', ''),
                        download_url=model_config.get('download_url', ''),
                        is_downloaded=False,
                        last_updated=None
                    )
                    models.append(model)
                    
                    # Save to database for future use
                    self.save_model_to_db(model)
        except Exception as e:
            print(f"Error loading models from config: {e}")
        
        return models
    
    def save_model_to_db(self, model: AIModel):
        """Save AI model to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO ai_models 
                    (name, model_id, provider, status, size, config_path, download_url, is_downloaded, last_updated)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    model.name, model.model_id, model.provider, model.status,
                    model.size, model.config_path, model.download_url,
                    model.is_downloaded, model.last_updated
                ))
        except Exception as e:
            print(f"Error saving model to database: {e}")
    
    def update_model_status(self, model_id: str, status: str, is_downloaded: bool = False):
        """Update AI model status"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE ai_models 
                    SET status = ?, is_downloaded = ?, last_updated = CURRENT_TIMESTAMP
                    WHERE model_id = ?
                """, (status, is_downloaded, model_id))
                return True
        except Exception as e:
            print(f"Error updating model status: {e}")
            return False
    
    def get_all_settings(self) -> Dict[str, List[Setting]]:
        """Get all settings organized by category"""
        settings = {}
        for category in SettingCategory:
            settings[category.value] = self.get_settings_by_category(category.value)
        return settings
