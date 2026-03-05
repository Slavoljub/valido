#!/usr/bin/env python3
"""
Environment Loader with Python-dotenv Support
Provides centralized environment variable loading with validation and type conversion
"""

import os
import logging
from typing import Dict, Any, Optional, Union, List
from pathlib import Path
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class EnvConfig:
    """Environment configuration with validation"""

    # Basic Flask configuration
    flask_app: str = "app.py"
    flask_env: str = "development"
    flask_debug: bool = True
    secret_key: str = "your-secret-key-change-in-production"
    app_name: str = "AI Valido Online"
    app_version: str = "2.0.0"

    # Server configuration
    host: str = "0.0.0.0"
    http_port: int = 5000
    https_port: int = 5001
    use_https: bool = True
    ssl_enabled: bool = True

    # Database configurations
    database_type: str = "sqlite"
    db_type: str = "sqlite"
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "data/sqlite/app.db"
    db_user: str = ""
    db_password: str = ""

    # PostgreSQL configurations
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_name: str = "ai_valido_online"
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"

    # MySQL configurations
    mysql_host: str = "localhost"
    mysql_port: int = 3306
    mysql_name: str = "ai_valido_online"
    mysql_user: str = "root"
    mysql_password: str = "root"

    # Redis configuration
    redis_enabled: bool = True
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str = ""
    redis_url: str = "redis://localhost:6379/0"

    # Vector database configurations
    pinecone_api_key: str = ""
    pinecone_environment: str = ""
    pinecone_index_name: str = "valido-ai-embeddings"
    pinecone_dimension: int = 384

    weaviate_url: str = "http://localhost:8080"
    weaviate_api_key: str = ""
    weaviate_class_name: str = "ValidoEmbeddings"
    weaviate_vector_dimension: int = 384

    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str = ""
    qdrant_collection_name: str = "valido_embeddings"
    qdrant_vector_size: int = 384

    chroma_host: str = "localhost"
    chroma_port: int = 8000
    chroma_collection_name: str = "valido_embeddings"

    # AI Safety configuration
    ai_safety_enabled: bool = True
    ai_guard_rails_enabled: bool = True
    ai_data_isolation_enabled: bool = True
    ai_prompt_injection_protection: bool = True
    ai_content_filtering: bool = True

    # Default AI configurations
    default_prompt: str = "You are a helpful AI assistant specialized in financial analysis and business intelligence for Serbian businesses. You have access to company-specific data and can provide insights, analysis, and recommendations based on the available information. Always maintain confidentiality and provide accurate, relevant information only."
    default_greeting: str = "👋 Hello! I'm your AI financial assistant, powered by local LLM models. I'm here to help you with financial analysis, business insights, and data-driven recommendations. What would you like to explore today?"
    ai_rules: str = "Be helpful and accurate, maintain data privacy, provide relevant financial insights, use available data sources, protect sensitive information, give actionable recommendations, explain complex topics clearly, ask for clarification when needed, respect Serbian business context and regulations."
    ai_max_response_length: int = 2048
    ai_temperature: float = 0.7

    # Chat configuration
    chat_enabled: bool = True
    chat_history_enabled: bool = True
    chat_history_limit: int = 100
    chat_session_timeout: int = 3600
    chat_auto_save: bool = True
    chat_redis_caching: bool = True

    # Theme configuration
    available_themes: List[str] = field(default_factory=lambda: ["light", "dark", "blue", "green", "purple", "orange", "red", "auto"])
    default_theme: str = "auto"
    theme_change_enabled: bool = True
    theme_persistence: bool = True

    # Python-dotenv configuration
    python_dotenv_enabled: bool = True
    env_file_path: str = ".env"
    env_file_encoding: str = "utf-8"
    env_file_override: bool = False
    env_load_priority: int = 1  # 1=System env, 2=.env file, 3=Both with .env override
    env_auto_reload: bool = False
    env_reload_interval: int = 300

class EnvironmentLoader:
    """Advanced environment loader with python-dotenv support"""

    def __init__(self, config_class: type = EnvConfig):
        self.config_class = config_class
        self._config: Optional[EnvConfig] = None
        self._loaded = False

    def load_config(self, env_file: Optional[str] = None) -> EnvConfig:
        """Load environment configuration with validation"""

        if self._loaded and self._config:
            return self._config

        # Try to load python-dotenv
        dotenv_available = self._try_load_dotenv()

        # Determine env file path
        env_file_path = env_file or os.getenv('ENV_FILE_PATH', '.env')

        # Load .env file if python-dotenv is available and enabled
        if dotenv_available and os.getenv('PYTHON_DOTENV_ENABLED', 'true').lower() == 'true':
            self._load_env_file(env_file_path)

        # Create configuration from environment variables
        config = self._create_config_from_env()

        # Validate configuration
        self._validate_config(config)

        self._config = config
        self._loaded = True

        logger.info("✅ Environment configuration loaded successfully")
        return config

    def _try_load_dotenv(self) -> bool:
        """Try to import and load python-dotenv"""
        try:
            import dotenv
            logger.info("✅ python-dotenv library found")
            return True
        except ImportError:
            logger.warning("⚠️  python-dotenv library not available, using system environment variables only")
            return False

    def _load_env_file(self, env_file_path: str):
        """Load environment variables from .env file"""
        try:
            import dotenv

            env_path = Path(env_file_path)
            if env_path.exists():
                dotenv.load_dotenv(env_path, override=self._get_override_setting())
                logger.info(f"✅ Loaded environment from {env_file_path}")
            else:
                logger.warning(f"⚠️  .env file not found at {env_file_path}")

        except Exception as e:
            logger.error(f"❌ Error loading .env file: {e}")

    def _get_override_setting(self) -> bool:
        """Get override setting from environment"""
        override = os.getenv('ENV_FILE_OVERRIDE', 'false').lower()
        return override in ['true', '1', 'yes', 'on']

    def _create_config_from_env(self) -> EnvConfig:
        """Create configuration object from environment variables"""
        return EnvConfig(
            # Basic Flask configuration
            flask_app=self._get_env_str('FLASK_APP', 'app.py'),
            flask_env=self._get_env_str('FLASK_ENV', 'development'),
            flask_debug=self._get_env_bool('FLASK_DEBUG', True),
            secret_key=self._get_env_str('SECRET_KEY', 'your-secret-key-change-in-production'),
            app_name=self._get_env_str('APP_NAME', 'AI Valido Online'),
            app_version=self._get_env_str('APP_VERSION', '2.0.0'),

            # Server configuration
            host=self._get_env_str('HOST', '0.0.0.0'),
            http_port=self._get_env_int('HTTP_PORT', 5000),
            https_port=self._get_env_int('HTTPS_PORT', 5001),
            use_https=self._get_env_bool('USE_HTTPS', True),
            ssl_enabled=self._get_env_bool('SSL_ENABLED', True),

            # Database configurations
            database_type=self._get_env_str('DATABASE_TYPE', 'sqlite'),
            db_type=self._get_env_str('DB_TYPE', 'sqlite'),
            db_host=self._get_env_str('DB_HOST', 'localhost'),
            db_port=self._get_env_int('DB_PORT', 5432),
            db_name=self._get_env_str('DB_NAME', 'data/sqlite/app.db'),
            db_user=self._get_env_str('DB_USER', ''),
            db_password=self._get_env_str('DB_PASSWORD', ''),

            # PostgreSQL configurations
            postgres_host=self._get_env_str('POSTGRES_HOST', 'localhost'),
            postgres_port=self._get_env_int('POSTGRES_PORT', 5432),
            postgres_name=self._get_env_str('POSTGRES_NAME', 'ai_valido_online'),
            postgres_user=self._get_env_str('POSTGRES_USER', 'postgres'),
            postgres_password=self._get_env_str('POSTGRES_PASSWORD', 'postgres'),

            # MySQL configurations
            mysql_host=self._get_env_str('MYSQL_HOST', 'localhost'),
            mysql_port=self._get_env_int('MYSQL_PORT', 3306),
            mysql_name=self._get_env_str('MYSQL_NAME', 'ai_valido_online'),
            mysql_user=self._get_env_str('MYSQL_USER', 'root'),
            mysql_password=self._get_env_str('MYSQL_PASSWORD', 'root'),

            # Redis configuration
            redis_enabled=self._get_env_bool('REDIS_ENABLED', True),
            redis_host=self._get_env_str('REDIS_HOST', 'localhost'),
            redis_port=self._get_env_int('REDIS_PORT', 6379),
            redis_db=self._get_env_int('REDIS_DB', 0),
            redis_password=self._get_env_str('REDIS_PASSWORD', ''),
            redis_url=self._get_env_str('REDIS_URL', 'redis://localhost:6379/0'),

            # Vector database configurations
            pinecone_api_key=self._get_env_str('PINECONE_API_KEY', ''),
            pinecone_environment=self._get_env_str('PINECONE_ENVIRONMENT', ''),
            pinecone_index_name=self._get_env_str('PINECONE_INDEX_NAME', 'valido-ai-embeddings'),
            pinecone_dimension=self._get_env_int('PINECONE_DIMENSION', 384),

            weaviate_url=self._get_env_str('WEAVIATE_URL', 'http://localhost:8080'),
            weaviate_api_key=self._get_env_str('WEAVIATE_API_KEY', ''),
            weaviate_class_name=self._get_env_str('WEAVIATE_CLASS_NAME', 'ValidoEmbeddings'),
            weaviate_vector_dimension=self._get_env_int('WEAVIATE_VECTOR_DIMENSION', 384),

            qdrant_url=self._get_env_str('QDRANT_URL', 'http://localhost:6333'),
            qdrant_api_key=self._get_env_str('QDRANT_API_KEY', ''),
            qdrant_collection_name=self._get_env_str('QDRANT_COLLECTION_NAME', 'valido_embeddings'),
            qdrant_vector_size=self._get_env_int('QDRANT_VECTOR_SIZE', 384),

            chroma_host=self._get_env_str('CHROMA_HOST', 'localhost'),
            chroma_port=self._get_env_int('CHROMA_PORT', 8000),
            chroma_collection_name=self._get_env_str('CHROMA_COLLECTION_NAME', 'valido_embeddings'),

            # AI Safety configuration
            ai_safety_enabled=self._get_env_bool('AI_SAFETY_ENABLED', True),
            ai_guard_rails_enabled=self._get_env_bool('AI_GUARD_RAILS_ENABLED', True),
            ai_data_isolation_enabled=self._get_env_bool('AI_DATA_ISOLATION_ENABLED', True),
            ai_prompt_injection_protection=self._get_env_bool('AI_PROMPT_INJECTION_PROTECTION', True),
            ai_content_filtering=self._get_env_bool('AI_CONTENT_FILTERING', True),

            # Default AI configurations
            default_prompt=self._get_env_str('DEFAULT_PROMPT',
                'You are a helpful AI assistant specialized in financial analysis and business intelligence for Serbian businesses. You have access to company-specific data and can provide insights, analysis, and recommendations based on the available information. Always maintain confidentiality and provide accurate, relevant information only.'),
            default_greeting=self._get_env_str('DEFAULT_GREETING',
                '👋 Hello! I\'m your AI financial assistant, powered by local LLM models. I\'m here to help you with financial analysis, business insights, and data-driven recommendations. What would you like to explore today?'),
            ai_rules=self._get_env_str('AI_RULES',
                'Be helpful and accurate, maintain data privacy, provide relevant financial insights, use available data sources, protect sensitive information, give actionable recommendations, explain complex topics clearly, ask for clarification when needed, respect Serbian business context and regulations.'),
            ai_max_response_length=self._get_env_int('AI_MAX_RESPONSE_LENGTH', 2048),
            ai_temperature=self._get_env_float('AI_TEMPERATURE', 0.7),

            # Chat configuration
            chat_enabled=self._get_env_bool('CHAT_ENABLED', True),
            chat_history_enabled=self._get_env_bool('CHAT_HISTORY_ENABLED', True),
            chat_history_limit=self._get_env_int('CHAT_HISTORY_LIMIT', 100),
            chat_session_timeout=self._get_env_int('CHAT_SESSION_TIMEOUT', 3600),
            chat_auto_save=self._get_env_bool('CHAT_AUTO_SAVE', True),
            chat_redis_caching=self._get_env_bool('CHAT_REDIS_CACHING', True),

            # Theme configuration
            available_themes=self._get_env_list('AVAILABLE_THEMES', ['light', 'dark', 'blue', 'green', 'purple', 'orange', 'red', 'auto']),
            default_theme=self._get_env_str('DEFAULT_THEME', 'auto'),
            theme_change_enabled=self._get_env_bool('THEME_CHANGE_ENABLED', True),
            theme_persistence=self._get_env_bool('THEME_PERSISTENCE', True),

            # Python-dotenv configuration
            python_dotenv_enabled=self._get_env_bool('PYTHON_DOTENV_ENABLED', True),
            env_file_path=self._get_env_str('ENV_FILE_PATH', '.env'),
            env_file_encoding=self._get_env_str('ENV_FILE_ENCODING', 'utf-8'),
            env_file_override=self._get_env_bool('ENV_FILE_OVERRIDE', False),
            env_load_priority=self._get_env_int('ENV_LOAD_PRIORITY', 1),
            env_auto_reload=self._get_env_bool('ENV_AUTO_RELOAD', False),
            env_reload_interval=self._get_env_int('ENV_RELOAD_INTERVAL', 300)
        )

    def _get_env_str(self, key: str, default: str = '') -> str:
        """Get environment variable as string"""
        return os.getenv(key, default)

    def _get_env_int(self, key: str, default: int = 0) -> int:
        """Get environment variable as integer"""
        try:
            return int(os.getenv(key, str(default)))
        except (ValueError, TypeError):
            return default

    def _get_env_float(self, key: str, default: float = 0.0) -> float:
        """Get environment variable as float"""
        try:
            return float(os.getenv(key, str(default)))
        except (ValueError, TypeError):
            return default

    def _get_env_bool(self, key: str, default: bool = False) -> bool:
        """Get environment variable as boolean"""
        value = os.getenv(key, str(default)).lower()
        return value in ['true', '1', 'yes', 'on', 'enabled']

    def _get_env_list(self, key: str, default: List[str] = None) -> List[str]:
        """Get environment variable as list"""
        if default is None:
            default = []

        value = os.getenv(key, '')
        if not value:
            return default

        # Try to parse comma-separated list
        if ',' in value:
            return [item.strip() for item in value.split(',') if item.strip()]

        return default

    def _validate_config(self, config: EnvConfig):
        """Validate configuration values"""
        errors = []

        # Validate ports
        if not (1 <= config.http_port <= 65535):
            errors.append(f"Invalid HTTP port: {config.http_port}")

        if not (1 <= config.https_port <= 65535):
            errors.append(f"Invalid HTTPS port: {config.https_port}")

        if not (1 <= config.db_port <= 65535):
            errors.append(f"Invalid database port: {config.db_port}")

        if not (1 <= config.redis_port <= 65535):
            errors.append(f"Invalid Redis port: {config.redis_port}")

        # Validate vector dimensions
        if config.pinecone_dimension <= 0:
            errors.append(f"Invalid Pinecone dimension: {config.pinecone_dimension}")

        if config.weaviate_vector_dimension <= 0:
            errors.append(f"Invalid Weaviate dimension: {config.weaviate_vector_dimension}")

        if config.qdrant_vector_size <= 0:
            errors.append(f"Invalid Qdrant vector size: {config.qdrant_vector_size}")

        # Validate chat settings
        if config.chat_history_limit <= 0:
            errors.append(f"Invalid chat history limit: {config.chat_history_limit}")

        if config.chat_session_timeout <= 0:
            errors.append(f"Invalid chat session timeout: {config.chat_session_timeout}")

        # Validate theme settings
        if config.default_theme not in config.available_themes:
            errors.append(f"Default theme '{config.default_theme}' not in available themes: {config.available_themes}")

        if errors:
            error_message = "Environment configuration errors:\n" + "\n".join(f"  - {error}" for error in errors)
            logger.error(error_message)
            raise ValueError(error_message)

    def reload_config(self) -> EnvConfig:
        """Reload configuration from environment"""
        self._loaded = False
        return self.load_config()

    def get_config_dict(self) -> Dict[str, Any]:
        """Get configuration as dictionary"""
        if not self._config:
            self.load_config()

        if self._config:
            return {k: v for k, v in self._config.__dict__.items() if not k.startswith('_')}
        return {}

    def get_available_databases(self) -> List[str]:
        """Get list of available database types"""
        return ['sqlite', 'postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch', 'cassandra', 'neo4j']

    def get_vector_databases(self) -> List[str]:
        """Get list of supported vector databases"""
        return ['pinecone', 'weaviate', 'qdrant', 'milvus', 'chromadb', 'faiss', 'elasticsearch']

    def create_env_file(self, env_file_path: str = '.env'):
        """Create a new .env file with default values"""
        try:
            config = self._create_config_from_env()
            env_content = self._generate_env_file_content(config)

            with open(env_file_path, 'w', encoding='utf-8') as f:
                f.write(env_content)

            logger.info(f"✅ Created .env file at {env_file_path}")
            return True

        except Exception as e:
            logger.error(f"❌ Error creating .env file: {e}")
            return False

    def _generate_env_file_content(self, config: EnvConfig) -> str:
        """Generate .env file content from configuration"""
        content = [
            "# AI Valido Online Environment Configuration",
            "# Generated automatically - Update with your actual values",
            "",
            "# =============================================================================",
            "# APPLICATION CONFIGURATION",
            "# =============================================================================",
            f"FLASK_APP={config.flask_app}",
            f"FLASK_ENV={config.flask_env}",
            f"FLASK_DEBUG={config.flask_debug}",
            f"SECRET_KEY={config.secret_key}",
            f"APP_NAME={config.app_name}",
            f"APP_VERSION={config.app_version}",
            "",
            "# =============================================================================",
            "# SERVER CONFIGURATION",
            "# =============================================================================",
            f"HOST={config.host}",
            f"HTTP_PORT={config.http_port}",
            f"HTTPS_PORT={config.https_port}",
            f"USE_HTTPS={config.use_https}",
            f"SSL_ENABLED={config.ssl_enabled}",
            "",
            "# =============================================================================",
            "# DATABASE CONFIGURATION",
            "# =============================================================================",
            f"DATABASE_TYPE={config.database_type}",
            f"DB_TYPE={config.db_type}",
            f"DB_HOST={config.db_host}",
            f"DB_PORT={config.db_port}",
            f"DB_NAME={config.db_name}",
            f"DB_USER={config.db_user}",
            f"DB_PASSWORD={config.db_password}",
            "",
            "# PostgreSQL Configuration",
            f"POSTGRES_HOST={config.postgres_host}",
            f"POSTGRES_PORT={config.postgres_port}",
            f"POSTGRES_NAME={config.postgres_name}",
            f"POSTGRES_USER={config.postgres_user}",
            f"POSTGRES_PASSWORD={config.postgres_password}",
            "",
            "# MySQL Configuration",
            f"MYSQL_HOST={config.mysql_host}",
            f"MYSQL_PORT={config.mysql_port}",
            f"MYSQL_NAME={config.mysql_name}",
            f"MYSQL_USER={config.mysql_user}",
            f"MYSQL_PASSWORD={config.mysql_password}",
            "",
            "# Redis Configuration",
            f"REDIS_ENABLED={config.redis_enabled}",
            f"REDIS_HOST={config.redis_host}",
            f"REDIS_PORT={config.redis_port}",
            f"REDIS_DB={config.redis_db}",
            f"REDIS_PASSWORD={config.redis_password}",
            f"REDIS_URL={config.redis_url}",
            "",
            "# =============================================================================",
            "# AI SAFETY & CONTEXT CONFIGURATION",
            "# =============================================================================",
            f"AI_SAFETY_ENABLED={config.ai_safety_enabled}",
            f"AI_GUARD_RAILS_ENABLED={config.ai_guard_rails_enabled}",
            f"AI_DATA_ISOLATION_ENABLED={config.ai_data_isolation_enabled}",
            f"AI_PROMPT_INJECTION_PROTECTION={config.ai_prompt_injection_protection}",
            f"AI_CONTENT_FILTERING={config.ai_content_filtering}",
            "",
            f"DEFAULT_PROMPT={config.default_prompt}",
            f"DEFAULT_GREETING={config.default_greeting}",
            f"AI_RULES={config.ai_rules}",
            f"AI_MAX_RESPONSE_LENGTH={config.ai_max_response_length}",
            f"AI_TEMPERATURE={config.ai_temperature}",
            "",
            "# =============================================================================",
            "# CHAT CONFIGURATION",
            "# =============================================================================",
            f"CHAT_ENABLED={config.chat_enabled}",
            f"CHAT_HISTORY_ENABLED={config.chat_history_enabled}",
            f"CHAT_HISTORY_LIMIT={config.chat_history_limit}",
            f"CHAT_SESSION_TIMEOUT={config.chat_session_timeout}",
            f"CHAT_AUTO_SAVE={config.chat_auto_save}",
            f"CHAT_REDIS_CACHING={config.chat_redis_caching}",
            "",
            "# =============================================================================",
            "# THEME CONFIGURATION",
            "# =============================================================================",
            f"DEFAULT_THEME={config.default_theme}",
            f"THEME_CHANGE_ENABLED={config.theme_change_enabled}",
            f"THEME_PERSISTENCE={config.theme_persistence}",
            "",
            "# =============================================================================",
            "# PYTHON-DOTENV CONFIGURATION",
            "# =============================================================================",
            f"PYTHON_DOTENV_ENABLED={config.python_dotenv_enabled}",
            f"ENV_FILE_PATH={config.env_file_path}",
            f"ENV_FILE_ENCODING={config.env_file_encoding}",
            f"ENV_FILE_OVERRIDE={config.env_file_override}",
            f"ENV_LOAD_PRIORITY={config.env_load_priority}",
            f"ENV_AUTO_RELOAD={config.env_auto_reload}",
            f"ENV_RELOAD_INTERVAL={config.env_reload_interval}",
            ""
        ]

        return '\n'.join(content)

# Global instance
env_loader = EnvironmentLoader()

def get_env_config() -> EnvConfig:
    """Get the global environment configuration"""
    return env_loader.load_config()

def reload_env_config() -> EnvConfig:
    """Reload the environment configuration"""
    return env_loader.reload_config()

def create_env_file(env_file_path: str = '.env') -> bool:
    """Create a new .env file with default values"""
    return env_loader.create_env_file(env_file_path)

# Backwards compatibility
def load_environment():
    """Legacy function for backwards compatibility"""
    return get_env_config()
