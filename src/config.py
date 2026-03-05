"""
ValidoAI - Unified Configuration System
=======================================
Centralized configuration management following Cursor Rules
All configuration in one place with proper MVC/MVVM patterns
"""

import os
import pymysql
import json
import logging
from typing import Dict, Any, Optional, List, Union
from urllib.parse import urlparse
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION CLASSES (Following OOP Patterns)
# ============================================================================

@dataclass
class DatabaseConfig:
    """Database configuration following factory pattern"""
    type: str
    database: str
    host: str = "localhost"
    port: int = 5432
    username: str = ""
    password: str = ""
    connection_string: str = ""
    ssl_mode: str = "require"
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30

    @classmethod
    def from_env(cls, db_type: str) -> 'DatabaseConfig':
        """Factory method to create config from environment variables"""
        base_config = {
            'postgresql': {
                'host': os.environ.get('POSTGRES_HOST', 'localhost'),
                'port': int(os.environ.get('POSTGRES_PORT', '5432')),
                'database': os.environ.get('POSTGRES_DB', 'validoai'),
                'username': os.environ.get('POSTGRES_USER', 'postgres'),
                'password': os.environ.get('POSTGRES_PASSWORD', ''),
                'ssl_mode': os.environ.get('POSTGRES_SSL_MODE', 'require')
            },
            'mysql': {
                'host': os.environ.get('MYSQL_HOST', 'localhost'),
                'port': int(os.environ.get('MYSQL_PORT', '3306')),
                'database': os.environ.get('MYSQL_DB', 'validoai'),
                'username': os.environ.get('MYSQL_USER', 'root'),
                'password': os.environ.get('MYSQL_PASSWORD', ''),
                'ssl_mode': os.environ.get('MYSQL_SSL_MODE', 'required')
            },
            'sqlite': {
                'database': os.environ.get('SQLITE_DB', 'data/sqlite/validoai.db'),
                'connection_string': f"sqlite:///{os.environ.get('SQLITE_DB', 'data/sqlite/validoai.db')}"
            }
        }

        config_data = base_config.get(db_type, base_config['sqlite'])
        return cls(type=db_type, **config_data)

    def get_connection_string(self) -> str:
        """Get database connection string"""
        if self.connection_string:
            return self.connection_string

        if self.type == 'postgresql':
            return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
        elif self.type == 'mysql':
            return f"mysql+pymysql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
        elif self.type == 'sqlite':
            return f"sqlite:///{self.database}"
        else:
            return f"sqlite:///data/sqlite/validoai.db"

@dataclass
class AIConfig:
    """AI configuration following factory pattern"""
    models_path: str
    default_model: str
    temperature: float
    max_tokens: int
    api_keys: Dict[str, str]
    local_models_config: str

    @classmethod
    def from_env(cls) -> 'AIConfig':
        """Factory method to create AI config from environment"""
        return cls(
            models_path=os.environ.get('AI_MODELS_PATH', 'src/ai_local_models'),
            default_model=os.environ.get('DEFAULT_AI_MODEL', 'gpt-3.5-turbo'),
            temperature=float(os.environ.get('AI_TEMPERATURE', '0.7')),
            max_tokens=int(os.environ.get('AI_MAX_TOKENS', '1000')),
            api_keys={
                'openai': os.environ.get('OPENAI_API_KEY', ''),
                'cohere': os.environ.get('COHERE_API_KEY', ''),
                'huggingface': os.environ.get('HUGGINGFACE_API_KEY', '')
            },
            local_models_config=os.environ.get('LOCAL_MODELS_CONFIG', 'src/ai_local_models/config.json')
        )

@dataclass
class ServerConfig:
    """Server configuration following factory pattern"""
    host: str
    http_port: int
    https_port: int
    use_https: bool
    ssl_cert_file: str
    ssl_key_file: str
    debug: bool

    @classmethod
    def from_env(cls) -> 'ServerConfig':
        """Factory method to create server config from environment"""
        return cls(
            host=os.environ.get('SERVER_HOST', '0.0.0.0'),
            http_port=int(os.environ.get('HTTP_PORT', '5000')),
            https_port=int(os.environ.get('HTTPS_PORT', '5001')),
            use_https=os.environ.get('USE_HTTPS', 'false').lower() == 'true',
            ssl_cert_file=os.environ.get('SSL_CERT_FILE', 'certs/cert.pem'),
            ssl_key_file=os.environ.get('SSL_KEY_FILE', 'certs/key.pem'),
            debug=os.environ.get('DEBUG', 'true').lower() == 'true'
        )

@dataclass
class SecurityConfig:
    """Security configuration following factory pattern"""
    secret_key: str
    password_min_length: int
    max_login_attempts: int
    session_timeout: int

    @classmethod
    def from_env(cls) -> 'SecurityConfig':
        """Factory method to create security config from environment"""
        return cls(
            secret_key=os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production'),
            password_min_length=int(os.environ.get('PASSWORD_MIN_LENGTH', '8')),
            max_login_attempts=int(os.environ.get('MAX_LOGIN_ATTEMPTS', '5')),
            session_timeout=int(os.environ.get('SESSION_TIMEOUT', '1800'))
        )

@dataclass
class EmailConfig:
    """Email configuration following factory pattern"""
    smtp_server: str
    smtp_port: int
    smtp_username: str
    smtp_password: str
    use_tls: bool

    @classmethod
    def from_env(cls) -> 'EmailConfig':
        """Factory method to create email config from environment"""
        return cls(
            smtp_server=os.environ.get('SMTP_SERVER', 'smtp.gmail.com'),
            smtp_port=int(os.environ.get('SMTP_PORT', '587')),
            smtp_username=os.environ.get('SMTP_USERNAME', ''),
            smtp_password=os.environ.get('SMTP_PASSWORD', ''),
            use_tls=os.environ.get('SMTP_USE_TLS', 'true').lower() == 'true'
        )

@dataclass
class ThemeConfig:
    """Theme configuration following factory pattern"""
    primary_color: str
    secondary_color: str
    dark_mode: bool

    @classmethod
    def from_env(cls) -> 'ThemeConfig':
        """Factory method to create theme config from environment"""
        return cls(
            primary_color=os.environ.get('PRIMARY_COLOR', '#3B82F6'),
            secondary_color=os.environ.get('SECONDARY_COLOR', '#1F2937'),
            dark_mode=os.environ.get('DARK_MODE', 'false').lower() == 'true'
        )

@dataclass
class FileUploadConfig:
    """File upload configuration following factory pattern"""
    upload_folder: str
    max_file_size: int
    allowed_extensions: List[str]

    @classmethod
    def from_env(cls) -> 'FileUploadConfig':
        """Factory method to create file upload config from environment"""
        return cls(
            upload_folder=os.environ.get('UPLOAD_FOLDER', 'uploads'),
            max_file_size=int(os.environ.get('MAX_FILE_SIZE', '10485760')),  # 10MB
            allowed_extensions=os.environ.get('ALLOWED_EXTENSIONS', 'jpg,jpeg,png,gif,pdf,doc,docx').split(',')
        )

@dataclass
class LoggingConfig:
    """Logging configuration following factory pattern"""
    level: str
    format: str
    file: str

    @classmethod
    def from_env(cls) -> 'LoggingConfig':
        """Factory method to create logging config from environment"""
        return cls(
            level=os.environ.get('LOG_LEVEL', 'INFO'),
            format=os.environ.get('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
            file=os.environ.get('LOG_FILE', 'logs/app.log')
        )

@dataclass
class VectorDatabaseConfig:
    """Vector database configuration following factory pattern"""
    type: str
    host: str
    port: int
    database: str
    username: str
    password: str

    @classmethod
    def from_env(cls) -> 'VectorDatabaseConfig':
        """Factory method to create vector database config from environment"""
        return cls(
            type=os.environ.get('VECTOR_DB_TYPE', 'pinecone'),
            host=os.environ.get('VECTOR_DB_HOST', 'localhost'),
            port=int(os.environ.get('VECTOR_DB_PORT', '8000')),
            database=os.environ.get('VECTOR_DB_NAME', 'validoai_vectors'),
            username=os.environ.get('VECTOR_DB_USER', ''),
            password=os.environ.get('VECTOR_DB_PASSWORD', '')
        )

@dataclass
class CacheConfig:
    """Cache configuration following factory pattern"""
    type: str
    host: str
    port: int
    database: int
    password: str

    @classmethod
    def from_env(cls) -> 'CacheConfig':
        """Factory method to create cache config from environment"""
        return cls(
            type=os.environ.get('CACHE_TYPE', 'redis'),
            host=os.environ.get('CACHE_HOST', 'localhost'),
            port=int(os.environ.get('CACHE_PORT', '6379')),
            database=int(os.environ.get('CACHE_DB', '0')),
            password=os.environ.get('CACHE_PASSWORD', '')
        )

@dataclass
class PerformanceConfig:
    """Performance configuration following factory pattern"""
    max_workers: int
    timeout: int
    retry_attempts: int

    @classmethod
    def from_env(cls) -> 'PerformanceConfig':
        """Factory method to create performance config from environment"""
        return cls(
            max_workers=int(os.environ.get('MAX_WORKERS', '4')),
            timeout=int(os.environ.get('TIMEOUT', '30')),
            retry_attempts=int(os.environ.get('RETRY_ATTEMPTS', '3'))
        )

@dataclass
class PaginationConfig:
    """Pagination configuration following factory pattern"""
    default_page_size: int
    max_page_size: int

    @classmethod
    def from_env(cls) -> 'PaginationConfig':
        """Factory method to create pagination config from environment"""
        return cls(
            default_page_size=int(os.environ.get('DEFAULT_PAGE_SIZE', '20')),
            max_page_size=int(os.environ.get('MAX_PAGE_SIZE', '100'))
        )

@dataclass
class SerbianServicesConfig:
    """Serbian services configuration following factory pattern"""
    api_base_url: str
    api_key: str
    timeout: int

    @classmethod
    def from_env(cls) -> 'SerbianServicesConfig':
        """Factory method to create Serbian services config from environment"""
        return cls(
            api_base_url=os.environ.get('SERBIAN_API_BASE_URL', 'https://api.serbian.services'),
            api_key=os.environ.get('SERBIAN_API_KEY', ''),
            timeout=int(os.environ.get('SERBIAN_API_TIMEOUT', '30'))
        )

@dataclass
class N8NConfig:
    """N8N configuration following factory pattern"""
    base_url: str
    api_key: str
    webhook_url: str

    @classmethod
    def from_env(cls) -> 'N8NConfig':
        """Factory method to create N8N config from environment"""
        return cls(
            base_url=os.environ.get('N8N_BASE_URL', 'http://localhost:5678'),
            api_key=os.environ.get('N8N_API_KEY', ''),
            webhook_url=os.environ.get('N8N_WEBHOOK_URL', '')
        )

# ============================================================================
# UNIFIED CONFIGURATION MANAGER
# ============================================================================

class UnifiedConfigManager:
    """Unified configuration manager following singleton pattern"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(UnifiedConfigManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self._config = {}
            self._load_configuration()

    def _load_configuration(self):
        """Load all configuration following factory pattern"""
        try:
            # Determine database type
            db_type = os.environ.get('DATABASE_TYPE', 'sqlite').lower()

            # Load configurations using factory methods
            self._config = {
                'database': DatabaseConfig.from_env(db_type),
                'ai': AIConfig.from_env(),
                'server': ServerConfig.from_env(),
                'security': SecurityConfig.from_env(),
                'email': EmailConfig.from_env(),
                'theme': ThemeConfig.from_env(),
                'file_upload': FileUploadConfig.from_env(),
                'logging': LoggingConfig.from_env(),
                'vector_database': VectorDatabaseConfig.from_env(),
                'cache': CacheConfig.from_env(),
                'performance': PerformanceConfig.from_env(),
                'pagination': PaginationConfig.from_env(),
                'serbian_services': SerbianServicesConfig.from_env(),
                'n8n': N8NConfig.from_env()
            }

            logger.info("✅ Unified configuration loaded successfully")
            logger.info(f"📊 Database: {self._config['database'].type}")
            logger.info(f"🤖 AI Model: {self._config['ai'].default_model}")
            logger.info(f"🌐 Server: {self._config['server'].host}:{self._config['server'].http_port}")

        except Exception as e:
            logger.error(f"❌ Configuration loading error: {e}")
            # Fallback to minimal config
            self._config = self._get_fallback_config()

    def _get_fallback_config(self) -> Dict[str, Any]:
        """Get fallback configuration when loading fails"""
        return {
            'database': DatabaseConfig.from_env('sqlite'),
            'ai': AIConfig.from_env(),
            'server': ServerConfig.from_env(),
            'security': SecurityConfig.from_env(),
            'email': EmailConfig.from_env(),
            'theme': ThemeConfig.from_env(),
            'file_upload': FileUploadConfig.from_env(),
            'logging': LoggingConfig.from_env(),
            'vector_database': VectorDatabaseConfig.from_env(),
            'cache': CacheConfig.from_env(),
            'performance': PerformanceConfig.from_env(),
            'pagination': PaginationConfig.from_env(),
            'serbian_services': SerbianServicesConfig.from_env(),
            'n8n': N8NConfig.from_env()
        }

    def get_database_config(self) -> DatabaseConfig:
        """Get database configuration"""
        return self._config.get('database', DatabaseConfig.from_env('sqlite'))

    def get_ai_config(self) -> AIConfig:
        """Get AI configuration"""
        return self._config.get('ai', AIConfig.from_env())

    def get_server_config(self) -> ServerConfig:
        """Get server configuration"""
        return self._config.get('server', ServerConfig.from_env())

    def get_flask_config(self) -> Dict[str, Any]:
        """Get Flask configuration dict"""
        return {
            'secret_key': self._config.get('security', SecurityConfig.from_env()).secret_key,
            'debug': self._config.get('server', ServerConfig.from_env()).debug,
            'testing': os.environ.get('FLASK_ENV', 'development') == 'testing',
            'server_name': os.environ.get('SERVER_NAME', 'localhost:5000'),
            'application_root': '/',
            'preferred_url_scheme': 'https' if self._config.get('server', ServerConfig.from_env()).use_https else 'http',
            'session_type': 'filesystem',
            'session_permanent': False,
            'permanent_session_lifetime': 3600,
            'sqlalchemy_track_modifications': False
        }

    def get_security_config(self) -> SecurityConfig:
        """Get security configuration"""
        return self._config.get('security', SecurityConfig.from_env())

    def get_email_config(self) -> EmailConfig:
        """Get email configuration"""
        return self._config.get('email', EmailConfig.from_env())

    def get_theme_config(self) -> ThemeConfig:
        """Get theme configuration"""
        return self._config.get('theme', ThemeConfig.from_env())

    def get_file_upload_config(self) -> FileUploadConfig:
        """Get file upload configuration"""
        return self._config.get('file_upload', FileUploadConfig.from_env())

    def get_logging_config(self) -> LoggingConfig:
        """Get logging configuration"""
        return self._config.get('logging', LoggingConfig.from_env())

    def get_vector_database_config(self) -> VectorDatabaseConfig:
        """Get vector database configuration"""
        return self._config.get('vector_database', VectorDatabaseConfig.from_env())

    def get_cache_config(self) -> CacheConfig:
        """Get cache configuration"""
        return self._config.get('cache', CacheConfig.from_env())

    def get_performance_config(self) -> PerformanceConfig:
        """Get performance configuration"""
        return self._config.get('performance', PerformanceConfig.from_env())

    def get_pagination_config(self) -> PaginationConfig:
        """Get pagination configuration"""
        return self._config.get('pagination', PaginationConfig.from_env())

    def get_serbian_services_config(self) -> SerbianServicesConfig:
        """Get Serbian services configuration"""
        return self._config.get('serbian_services', SerbianServicesConfig.from_env())

    def get_n8n_config(self) -> N8NConfig:
        """Get N8N configuration"""
        return self._config.get('n8n', N8NConfig.from_env())

    def get_all_configurations(self) -> Dict[str, Any]:
        """Get all configurations as a dictionary"""
        return {
            'database': self.get_database_config(),
            'ai': self.get_ai_config(),
            'server': self.get_server_config(),
            'security': self.get_security_config(),
            'email': self.get_email_config(),
            'theme': self.get_theme_config(),
            'file_upload': self.get_file_upload_config(),
            'logging': self.get_logging_config(),
            'vector_database': self.get_vector_database_config(),
            'cache': self.get_cache_config(),
            'performance': self.get_performance_config(),
            'pagination': self.get_pagination_config(),
            'serbian_services': self.get_serbian_services_config(),
            'n8n': self.get_n8n_config()
        }

    def get_configuration_schema(self, category: str) -> Dict[str, Any]:
        """Get configuration schema for a specific category"""
        schemas = {
            'database': {
                'type': 'object',
                'properties': {
                    'type': {'type': 'string', 'enum': ['postgresql', 'mysql', 'sqlite']},
                    'host': {'type': 'string'},
                    'port': {'type': 'integer'},
                    'database': {'type': 'string'},
                    'username': {'type': 'string'},
                    'password': {'type': 'string', 'format': 'password'}
                }
            },
            'ai': {
                'type': 'object',
                'properties': {
                    'default_model': {'type': 'string'},
                    'temperature': {'type': 'number'},
                    'max_tokens': {'type': 'integer'},
                    'models_path': {'type': 'string'}
                }
            },
            'server': {
                'type': 'object',
                'properties': {
                    'host': {'type': 'string'},
                    'http_port': {'type': 'integer'},
                    'https_port': {'type': 'integer'},
                    'use_https': {'type': 'boolean'},
                    'debug': {'type': 'boolean'}
                }
            }
        }
        return schemas.get(category, {})

    def get(self, section: str, key: Optional[str] = None, default: Any = None) -> Any:
        """Get configuration value"""
        if section not in self._config:
            return default
        
        config_section = self._config[section]
        
        if key is None:
            return config_section
        
        if hasattr(config_section, key):
            return getattr(config_section, key)
        
        return default

    def set(self, section: str, key: str, value: Any):
        """Set configuration value"""
        if section not in self._config:
            return
        
        config_section = self._config[section]
        
        if hasattr(config_section, key):
            setattr(config_section, key, value)

    def reload(self):
        """Reload configuration"""
        self._load_configuration()
        logger.info("🔄 Configuration reloaded")

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary (excluding sensitive data)"""
        safe_config = {}
        for section, config in self._config.items():
            if hasattr(config, '__dict__'):
                safe_config[section] = config.__dict__
            else:
                safe_config[section] = config

        # Remove sensitive information
        if 'database' in safe_config:
            safe_config['database'].pop('password', None)
        if 'email' in safe_config:
            safe_config['email'].pop('smtp_password', None)

        return safe_config

    def validate(self) -> List[str]:
        """Validate configuration and return list of issues"""
        issues = []

        try:
            # Check database configuration
            db_config = self.get_database_config()
            if not db_config.database:
                issues.append("Database name is required")

            # Check AI configuration
            ai_config = self.get_ai_config()
            if not ai_config.default_model:
                issues.append("Default AI model is required")

            # Check server configuration
            server_config = self.get_server_config()
            if server_config.http_port <= 0 or server_config.http_port > 65535:
                issues.append("HTTP port must be between 1 and 65535")

            # Check SSL configuration
            if server_config.use_https:
                if not os.path.exists(server_config.ssl_cert_file):
                    issues.append(f"SSL certificate file not found: {server_config.ssl_cert_file}")
                if not os.path.exists(server_config.ssl_key_file):
                    issues.append(f"SSL key file not found: {server_config.ssl_key_file}")

        except Exception as e:
            issues.append(f"Configuration validation error: {e}")

        return issues

# ============================================================================
# GLOBAL CONFIGURATION INSTANCE
# ============================================================================

# Create global configuration instance (singleton)
config_manager = UnifiedConfigManager()

# Export commonly used configurations for backward compatibility
database_config = config_manager.get_database_config()
ai_config = config_manager.get_ai_config()
server_config = config_manager.get_server_config()
security_config = config_manager.get_security_config()
email_config = config_manager.get_email_config()
theme_config = config_manager.get_theme_config()
file_upload_config = config_manager.get_file_upload_config()
logging_config = config_manager.get_logging_config()
vector_database_config = config_manager.get_vector_database_config()
cache_config = config_manager.get_cache_config()
performance_config = config_manager.get_performance_config()
pagination_config = config_manager.get_pagination_config()
serbian_services = config_manager.get_serbian_services_config()
n8n_config = config_manager.get_n8n_config()

# Export functions for easy access
get_config = config_manager.get
set_config = config_manager.set

logger.info("✅ Unified configuration system initialized successfully")
logger.info(f"📊 Total configuration sections: {len(config_manager._config)}")

if __name__ == "__main__":
    # Test the unified configuration
    print("🔧 Unified Configuration System Test")
    print("=" * 40)

    print(f"Database Type: {database_config.type}")
    print(f"Database Name: {database_config.database}")
    print(f"Default AI Model: {ai_config.default_model}")
    print(f"Server Host: {server_config.host}")
    print(f"Server Port: {server_config.http_port}")
    print(f"Debug Mode: {server_config.debug}")

    # Test configuration validation
    issues = config_manager.validate()
    if issues:
        print("⚠️ Configuration issues found:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("✅ Configuration validation passed")

    # Test configuration to dict
    config_dict = config_manager.to_dict()
    print(f"📊 Configuration sections: {list(config_dict.keys())}")
