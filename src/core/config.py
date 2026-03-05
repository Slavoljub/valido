"""
Configuration Management
=======================

Configuration management for ValidoAI.
"""

import os
from typing import Dict, Any

class Config:
    """Base configuration class"""

    # Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = False
    TESTING = False

    # Server configuration
    SERVER_NAME = os.environ.get('SERVER_NAME', 'localhost:5000')
    APPLICATION_ROOT = '/'
    PREFERRED_URL_SCHEME = 'http'

    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///validoai.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Session configuration
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = False
    PERMANENT_SESSION_LIFETIME = 3600

    # Upload configuration
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS = {
        'documents': ['pdf', 'doc', 'docx', 'txt', 'rtf', 'odt'],
        'images': ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg'],
        'videos': ['mp4', 'avi', 'mov', 'wmv', 'flv', 'webm'],
        'audio': ['mp3', 'wav', 'ogg', 'm4a', 'flac'],
        'spreadsheets': ['xls', 'xlsx', 'csv', 'ods'],
        'presentations': ['ppt', 'pptx', 'odp'],
        'archives': ['zip', 'rar', '7z', 'tar', 'gz']
    }

    # AI Configuration
    AI_MODELS_PATH = 'src/ai_local_models'
    DEFAULT_AI_MODEL = 'gpt-3.5-turbo'
    AI_TEMPERATURE = 0.7
    AI_MAX_TOKENS = 1000

    # Security configuration
    BCRYPT_ROUNDS = 12
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key')
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hour
    JWT_REFRESH_TOKEN_EXPIRES = 604800  # 7 days

    # Email configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'False').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@validoai.com')

    # Redis configuration
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    CACHE_TYPE = 'redis'
    CACHE_REDIS_URL = REDIS_URL

    # External APIs
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')

    @classmethod
    def get_config(cls, config_name: str):
        """Get configuration class based on environment"""
        configs = {
            'development': DevelopmentConfig,
            'production': ProductionConfig,
            'testing': TestingConfig
        }
        return configs.get(config_name, DevelopmentConfig)

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_ECHO = True
    CACHE_TYPE = 'simple'

    # Development server settings
    SERVER_NAME = 'localhost:5000'
    APPLICATION_ROOT = '/'
    PREFERRED_URL_SCHEME = 'http'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False

    # Production-specific settings
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_HTTPONLY = True

    # SSL/TLS settings
    PREFERRED_URL_SCHEME = 'https'

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    CACHE_TYPE = 'simple'

# Global configuration instance
config = Config()

def get_config_value(key: str, default: Any = None) -> Any:
    """Get configuration value by key"""
    return getattr(config, key, default)

def set_config_value(key: str, value: Any):
    """Set configuration value"""
    setattr(config, key, value)

def get_allowed_extensions() -> Dict[str, list]:
    """Get all allowed file extensions"""
    return config.ALLOWED_EXTENSIONS

def is_allowed_extension(filename: str, category: str = None) -> bool:
    """Check if file extension is allowed"""
    if not filename:
        return False

    extension = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''

    if category and category in config.ALLOWED_EXTENSIONS:
        return extension in config.ALLOWED_EXTENSIONS[category]

    # Check all categories
    for extensions in config.ALLOWED_EXTENSIONS.values():
        if extension in extensions:
            return True

    return False

def get_upload_config() -> Dict[str, Any]:
    """Get upload configuration"""
    return {
        'folder': config.UPLOAD_FOLDER,
        'max_size': config.MAX_CONTENT_LENGTH,
        'allowed_extensions': config.ALLOWED_EXTENSIONS
    }

def get_ai_config() -> Dict[str, Any]:
    """Get AI configuration"""
    return {
        'models_path': config.AI_MODELS_PATH,
        'default_model': config.DEFAULT_AI_MODEL,
        'temperature': config.AI_TEMPERATURE,
        'max_tokens': config.AI_MAX_TOKENS
    }

def get_security_config() -> Dict[str, Any]:
    """Get security configuration"""
    return {
        'bcrypt_rounds': config.BCRYPT_ROUNDS,
        'jwt_secret': config.JWT_SECRET_KEY,
        'jwt_access_expires': config.JWT_ACCESS_TOKEN_EXPIRES,
        'jwt_refresh_expires': config.JWT_REFRESH_TOKEN_EXPIRES
    }
