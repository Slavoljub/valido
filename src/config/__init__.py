"""Package initialization for src/config"""

# Import main configuration functionality directly from the config module
import sys
import os
from pathlib import Path

# Get the parent directory and add to path
parent_dir = Path(__file__).parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

# Import directly from the config.py file to avoid circular imports
try:
    # Import the config.py file directly using exec to avoid circular imports
    config_file = Path(__file__).parent.parent / 'config.py'
    with open(config_file, 'r', encoding='utf-8') as f:
        config_code = f.read()
    
    # Create a new namespace for the config module
    config_namespace = {}
    exec(config_code, config_namespace)
    
    # Extract the objects we need
    DatabaseConfig = config_namespace.get('DatabaseConfig')
    ServerConfig = config_namespace.get('ServerConfig')
    SecurityConfig = config_namespace.get('SecurityConfig')
    EmailConfig = config_namespace.get('EmailConfig')
    ThemeConfig = config_namespace.get('ThemeConfig')
    FileUploadConfig = config_namespace.get('FileUploadConfig')
    LoggingConfig = config_namespace.get('LoggingConfig')
    AIConfig = config_namespace.get('AIConfig')
    VectorDatabaseConfig = config_namespace.get('VectorDatabaseConfig')
    CacheConfig = config_namespace.get('CacheConfig')
    PerformanceConfig = config_namespace.get('PerformanceConfig')
    PaginationConfig = config_namespace.get('PaginationConfig')
    SerbianServicesConfig = config_namespace.get('SerbianServicesConfig')
    N8NConfig = config_namespace.get('N8NConfig')
    UnifiedConfigManager = config_namespace.get('UnifiedConfigManager')
    
    # Get the global instances
    config_manager = config_namespace.get('config_manager')
    database_config = config_namespace.get('database_config')
    ai_config = config_namespace.get('ai_config')
    server_config = config_namespace.get('server_config')
    security_config = config_namespace.get('security_config')
    email_config = config_namespace.get('email_config')
    theme_config = config_namespace.get('theme_config')
    file_upload_config = config_namespace.get('file_upload_config')
    logging_config = config_namespace.get('logging_config')
    vector_database_config = config_namespace.get('vector_database_config')
    cache_config = config_namespace.get('cache_config')
    performance_config = config_namespace.get('performance_config')
    pagination_config = config_namespace.get('pagination_config')
    serbian_services = config_namespace.get('serbian_services')
    n8n_config = config_namespace.get('n8n_config')
    get_config = config_namespace.get('get_config')
    set_config = config_namespace.get('set_config')
    
    # Create aliases for backward compatibility
    db_config = database_config
    get_db_config = get_config
    
except Exception as e:
    print(f"Import error in src/config/__init__.py: {e}")
    # Fallback for import issues
    DatabaseConfig = None
    ServerConfig = None
    SecurityConfig = None
    EmailConfig = None
    ThemeConfig = None
    FileUploadConfig = None
    LoggingConfig = None
    AIConfig = None
    VectorDatabaseConfig = None
    CacheConfig = None
    PerformanceConfig = None
    PaginationConfig = None
    SerbianServicesConfig = None
    N8NConfig = None
    UnifiedConfigManager = None
    db_config = None
    get_db_config = None
    serbian_services = None
    config_manager = None
    database_config = None
    ai_config = None
    server_config = None
    security_config = None
    email_config = None
    theme_config = None
    file_upload_config = None
    logging_config = None
    vector_database_config = None
    cache_config = None
    performance_config = None
    pagination_config = None
    n8n_config = None
    get_config = None
    set_config = None

# Export all configuration classes and functions
__all__ = [
    'DatabaseConfig',
    'ServerConfig',
    'SecurityConfig',
    'EmailConfig',
    'ThemeConfig',
    'FileUploadConfig',
    'LoggingConfig',
    'AIConfig',
    'VectorDatabaseConfig',
    'CacheConfig',
    'PerformanceConfig',
    'PaginationConfig',
    'SerbianServicesConfig',
    'N8NConfig',
    'UnifiedConfigManager',
    'db_config',
    'get_db_config',
    'serbian_services',
    'config_manager',
    'database_config',
    'ai_config',
    'server_config',
    'security_config',
    'email_config',
    'theme_config',
    'file_upload_config',
    'logging_config',
    'vector_database_config',
    'cache_config',
    'performance_config',
    'pagination_config',
    'n8n_config',
    'get_config',
    'set_config'
]