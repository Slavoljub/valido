#!/usr/bin/env python3
"""
Settings Controller
Handles application settings and configuration
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class SettingsController:
    """Controller for managing application settings and configuration"""
    
    def __init__(self):
        self.settings_file = os.path.join(os.getcwd(), 'data', 'settings.json')
        self.env_file = os.path.join(os.getcwd(), '.env')
        self.data_dir = os.path.join(os.getcwd(), 'data')
        
        # Ensure data directory exists
        os.makedirs(self.data_dir, exist_ok=True)
    
    def load_settings(self) -> Dict[str, Any]:
        """Load application settings from file"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    return json.load(f)
            else:
                # Return default settings
                return self._get_default_settings()
        except Exception as e:
            logger.error(f"Error loading settings: {e}")
            return self._get_default_settings()
    
    def save_settings(self, settings: Dict[str, Any]) -> bool:
        """Save application settings to file"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
            logger.info("Settings saved successfully")
            return True
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
            return False
    
    def _get_default_settings(self) -> Dict[str, Any]:
        """Get default application settings"""
        return {
            'localModels': [
                {
                    'name': 'Llama2-7B',
                    'description': 'Meta\'s Llama2 7B parameter model',
                    'enabled': True,
                    'available': False,
                    'path': 'models/llama2-7b'
                },
                {
                    'name': 'Mistral-7B',
                    'description': 'Mistral AI 7B parameter model',
                    'enabled': True,
                    'available': False,
                    'path': 'models/mistral-7b'
                },
                {
                    'name': 'Phi-2',
                    'description': 'Microsoft Phi-2 2.7B parameter model',
                    'enabled': True,
                    'available': False,
                    'path': 'models/phi-2'
                }
            ],
            'externalModels': [
                {
                    'name': 'GPT-3.5',
                    'description': 'OpenAI GPT-3.5 Turbo',
                    'enabled': False,
                    'available': False,
                    'api_key': '',
                    'api_key_placeholder': 'sk-...'
                },
                {
                    'name': 'GPT-4',
                    'description': 'OpenAI GPT-4',
                    'enabled': False,
                    'available': False,
                    'api_key': '',
                    'api_key_placeholder': 'sk-...'
                },
                {
                    'name': 'Cohere Command',
                    'description': 'Cohere Command model',
                    'enabled': False,
                    'available': False,
                    'api_key': '',
                    'api_key_placeholder': 'cohere-api-key'
                }
            ],
            'dbConfig': {
                'postgresql': {
                    'host': 'localhost',
                    'port': 5432,
                    'database': 'ai_valido_online',
                    'username': 'postgres',
                    'password': 'postgres'
                },
                'sqlite': {
                    'database': 'data/sqlite/app.db'
                }
            },
            'serverConfig': {
                'host': '0.0.0.0',
                'http_port': 5000,
                'https_port': 5001,
                'ssl_cert_file': 'certs/cert.pem',
                'ssl_key_file': 'certs/key.pem',
                'use_https': True,
                'debug': True
            },
            'securityConfig': {
                'secret_key': '',
                'session_timeout': 30,
                'enable_csrf': True,
                'enable_rate_limiting': True
            }
        }
    
    def test_model(self, model_name: str) -> bool:
        """Test if a model is available and working"""
        try:
            # Check if transformers is available
            try:
                import torch
                from transformers import AutoTokenizer, AutoModelForCausalLM
                transformers_available = True
            except ImportError:
                transformers_available = False
            
            # Check if model files exist
            model_path = f"models/{model_name.lower()}"
            model_exists = os.path.exists(model_path)
            
            # For external models, check if API key is configured
            if model_name in ['GPT-3.5', 'GPT-4', 'Cohere Command']:
                settings = self.load_settings()
                for model in settings.get('externalModels', []):
                    if model['name'] == model_name:
                        return bool(model.get('api_key', '').strip())
                return False
            
            # For local models, check if transformers is available and model exists
            return transformers_available and model_exists
            
        except Exception as e:
            logger.error(f"Error testing model {model_name}: {e}")
            return False
    
    def load_env_file(self) -> str:
        """Load content of .env file"""
        try:
            if os.path.exists(self.env_file):
                with open(self.env_file, 'r') as f:
                    return f.read()
            else:
                # Return default .env content
                return self._get_default_env_content()
        except Exception as e:
            logger.error(f"Error loading .env file: {e}")
            return self._get_default_env_content()
    
    def save_env_file(self, content: str) -> bool:
        """Save content to .env file"""
        try:
            with open(self.env_file, 'w') as f:
                f.write(content)
            logger.info(".env file saved successfully")
            return True
        except Exception as e:
            logger.error(f"Error saving .env file: {e}")
            return False
    
    def _get_default_env_content(self) -> str:
        """Get default .env file content"""
        return """# ValidoAI Environment Configuration
# Server Configuration
SERVER_HOST=0.0.0.0
HTTP_PORT=5000
HTTPS_PORT=5001
USE_HTTPS=true
DEBUG=true

# Database Configuration
DATABASE_TYPE=sqlite
DATABASE_URL=sqlite:///data/sqlite/app.db

# PostgreSQL Configuration (if using PostgreSQL)
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=ai_valido_online
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

# AI Model Configuration
OPENAI_API_KEY=your_openai_key_here
COHERE_API_KEY=your_cohere_key_here

# Security
SECRET_KEY=your_secret_key_here
SESSION_TIMEOUT=30

# SSL Configuration
SSL_CERT_FILE=certs/cert.pem
SSL_KEY_FILE=certs/key.pem

# Performance
WORKERS=4
MAX_REQUESTS=1000
KEEP_ALIVE_TIMEOUT=30
READ_TIMEOUT=30

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# Features
ENABLE_CSRF=true
ENABLE_RATE_LIMITING=true
ENABLE_GPU_ACCELERATION=true
"""
    
    def test_database_connection(self, db_type: str, config: Dict[str, Any]) -> bool:
        """Test database connection"""
        try:
            if db_type == 'postgresql':
                return self._test_postgresql_connection(config)
            elif db_type == 'sqlite':
                return self._test_sqlite_connection(config)
            else:
                logger.error(f"Unsupported database type: {db_type}")
                return False
        except Exception as e:
            logger.error(f"Error testing database connection: {e}")
            return False
    
    def _test_postgresql_connection(self, config: Dict[str, Any]) -> bool:
        """Test PostgreSQL connection"""
        try:
            import psycopg2
            
            conn = psycopg2.connect(
                host=config.get('host', 'localhost'),
                port=config.get('port', 5432),
                database=config.get('database', 'ai_valido_online'),
                user=config.get('username', 'postgres'),
                password=config.get('password', 'postgres')
            )
            conn.close()
            return True
        except ImportError:
            logger.error("psycopg2 not installed")
            return False
        except Exception as e:
            logger.error(f"PostgreSQL connection failed: {e}")
            return False
    
    def _test_sqlite_connection(self, config: Dict[str, Any]) -> bool:
        """Test SQLite connection"""
        try:
            import sqlite3
            
            db_path = config.get('database', 'data/sqlite/app.db')
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            
            # Test connection
            conn = sqlite3.connect(db_path)
            conn.close()
            return True
        except Exception as e:
            logger.error(f"SQLite connection failed: {e}")
            return False
    
    def update_model_availability(self) -> Dict[str, bool]:
        """Update model availability status"""
        try:
            settings = self.load_settings()
            
            # Update local models
            for model in settings.get('localModels', []):
                model['available'] = self.test_model(model['name'])
            
            # Update external models
            for model in settings.get('externalModels', []):
                model['available'] = self.test_model(model['name'])
            
            # Save updated settings
            self.save_settings(settings)
            
            # Return availability status
            availability = {}
            for model in settings.get('localModels', []):
                availability[model['name']] = model['available']
            for model in settings.get('externalModels', []):
                availability[model['name']] = model['available']
            
            return availability
        except Exception as e:
            logger.error(f"Error updating model availability: {e}")
            return {}
    
    def get_model_config(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific model"""
        try:
            settings = self.load_settings()
            
            # Check local models
            for model in settings.get('localModels', []):
                if model['name'] == model_name:
                    return model
            
            # Check external models
            for model in settings.get('externalModels', []):
                if model['name'] == model_name:
                    return model
            
            return None
        except Exception as e:
            logger.error(f"Error getting model config for {model_name}: {e}")
            return None
    
    def update_model_config(self, model_name: str, config: Dict[str, Any]) -> bool:
        """Update configuration for a specific model"""
        try:
            settings = self.load_settings()
            
            # Update local models
            for model in settings.get('localModels', []):
                if model['name'] == model_name:
                    model.update(config)
                    self.save_settings(settings)
                    return True
            
            # Update external models
            for model in settings.get('externalModels', []):
                if model['name'] == model_name:
                    model.update(config)
                    self.save_settings(settings)
                    return True
            
            return False
        except Exception as e:
            logger.error(f"Error updating model config for {model_name}: {e}")
            return False
