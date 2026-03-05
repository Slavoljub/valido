"""
AI Local Models Package - Consolidated & Optimized
Provides unified local AI model management, ML capabilities, and database integration
"""

# Core AI Components - Consolidated
from .chat_engine import AdvancedChatEngine
from .chat_storage import ChatArtifactStorage, chat_storage

# Configuration Management - Unified
from .config_manager import UnifiedConfigManager, ModelConfig, config_manager

# Database Management - Global with PostgreSQL support
from .database_manager import GlobalDatabaseManager, DatabaseConfig, db_manager

# Database Configuration Interface
from .database_config import DatabaseConfigInterface, database_config_bp, db_config_interface

# Redis Cache Manager
from .redis_cache_manager import RedisCacheManager, redis_cache

# AI Safety Manager
from .ai_safety_manager import AISafetyManager, ai_safety_manager

# Supporting Components
from .model_downloader import ModelDownloader
from .inference_engine import InferenceEngine
from .financial_analyzer import FinancialAnalyzer
from .gpu_detector import GPUDetector, gpu_detector
from .model_manager import LocalModelManager as ModelManager
from .data_integrator import DataIntegrator, data_integrator
from .security_manager import SecurityManager, security_manager

# CLI Components (optional - may not be available on all platforms)
try:
    from .cli_enhanced import EnhancedCLI, CommunicationMode
    CLI_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  CLI components not available: {e}")
    CLI_AVAILABLE = False
    EnhancedCLI = None
    CommunicationMode = None

# Backwards compatibility aliases
ChatEngine = AdvancedChatEngine
ModelConfigManager = UnifiedConfigManager
DatabaseConnectorManager = GlobalDatabaseManager
database_connector_manager = db_manager

__all__ = [
    # Core AI Components
    'AdvancedChatEngine',
    'ChatEngine',  # Backwards compatibility

    # Configuration Management
    'UnifiedConfigManager',
    'ModelConfigManager',  # Backwards compatibility
    'ModelConfig',
    'config_manager',

    # Database Management
    'GlobalDatabaseManager',
    'DatabaseConnectorManager',  # Backwards compatibility
    'DatabaseConfig',
    'db_manager',
    'database_connector_manager',  # Backwards compatibility

    # Database Configuration
    'DatabaseConfigInterface',
    'database_config_bp',
    'db_config_interface',

    # Redis Cache Management
    'RedisCacheManager',
    'redis_cache',

    # AI Safety Management
    'AISafetyManager',
    'ai_safety_manager',

    # Supporting Components
    'ModelDownloader',
    'InferenceEngine',
    'FinancialAnalyzer',
    'GPUDetector',
    'gpu_detector',
    'ModelManager',
    'DataIntegrator',
    'data_integrator',
    'SecurityManager',
    'security_manager',

    # Chat & Storage
    'ChatArtifactStorage',
    'chat_storage',

    # CLI Components
    'EnhancedCLI',
    'CommunicationMode'
]
