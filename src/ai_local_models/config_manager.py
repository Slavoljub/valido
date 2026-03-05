#!/usr/bin/env python3
"""
Unified Configuration Manager
Consolidates all configuration files into a single, well-organized system
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import threading

logger = logging.getLogger(__name__)

@dataclass
class ModelConfig:
    """Configuration for a single AI model"""
    name: str
    display_name: str
    model_id: str
    type: str  # llm, embedding, classification, etc.
    format: str  # gguf, ggml, pytorch, tensorflow, etc.
    size: str  # 7b, 13b, etc.
    language: str = "multilingual"
    provider: str = "Local"
    description: str = ""
    download_url: str = ""
    local_path: str = ""
    memory_required: int = 4096  # MB
    cpu_threads: int = 4
    temperature: float = 0.7
    max_tokens: int = 2048
    context_length: int = 4096
    supported_tasks: List[str] = None
    tags: List[str] = None
    is_downloaded: bool = False
    is_loaded: bool = False
    download_progress: float = 0.0
    last_used: Optional[str] = None
    performance_score: float = 0.0
    requirements: Optional[Dict[str, str]] = None

    def __post_init__(self):
        if self.supported_tasks is None:
            self.supported_tasks = []
        if self.tags is None:
            self.tags = []

@dataclass
class SystemConfig:
    """System-wide configuration"""
    models_directory: str = "local_llm_models"
    cache_directory: str = "cache"
    temp_directory: str = "temp"
    database_path: str = "data/sqlite/app.db"
    embeddings_db_url: str = "postgresql://localhost:5432/ai_embeddings"
    max_memory_usage: int = 80  # percentage
    enable_gpu: bool = True
    enable_embeddings: bool = True
    embedding_model: str = "all-MiniLM-L6-v2"
    log_level: str = "INFO"
    enable_caching: bool = True
    cache_size_mb: int = 1024

class UnifiedConfigManager:
    """Unified configuration manager for all AI models and system settings"""

    def __init__(self, config_dir: str = "src/ai_local_models"):
        self.config_dir = Path(config_dir)
        self._lock = threading.Lock()
        self._models_cache = {}
        self._config_cache = {}

        # Initialize configuration
        self.system_config = SystemConfig()
        self.models_config = {}

        # Load all configurations
        self._load_system_config()
        self._load_models_config()
        self._migrate_legacy_configs()

    def _load_system_config(self):
        """Load system configuration from environment and defaults"""
        try:
            # Load from environment variables
            self.system_config.models_directory = os.getenv(
                'AI_MODELS_DIRECTORY', self.system_config.models_directory
            )
            self.system_config.database_path = os.getenv(
                'AI_DATABASE_PATH', self.system_config.database_path
            )
            self.system_config.embeddings_db_url = os.getenv(
                'AI_EMBEDDINGS_DB_URL', self.system_config.embeddings_db_url
            )
            self.system_config.log_level = os.getenv(
                'AI_LOG_LEVEL', self.system_config.log_level
            )

            # Convert string values to appropriate types
            self.system_config.max_memory_usage = int(os.getenv(
                'AI_MAX_MEMORY_USAGE', self.system_config.max_memory_usage
            ))
            self.system_config.enable_gpu = os.getenv(
                'AI_ENABLE_GPU', 'true'
            ).lower() == 'true'
            self.system_config.enable_embeddings = os.getenv(
                'AI_ENABLE_EMBEDDINGS', 'true'
            ).lower() == 'true'

            logger.info("✅ System configuration loaded successfully")

        except Exception as e:
            logger.error(f"❌ Error loading system config: {e}")
            # Continue with defaults

    def _load_models_config(self):
        """Load models configuration from JSON files"""
        try:
            # List of potential config files to try
            config_files = [
                "local_llm_models_config.json",
                "local_models_config.json",
                "models_config.json"
            ]

            models_data = {}

            for config_file in config_files:
                config_path = self.config_dir / config_file
                if config_path.exists():
                    try:
                        with open(config_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)

                        # Merge models data
                        if 'models' in data:
                            models_data.update(data['models'])

                        logger.info(f"✅ Loaded models from {config_file}")

                    except Exception as e:
                        logger.warning(f"⚠️ Error loading {config_file}: {e}")

            # Convert to ModelConfig objects
            for model_id, model_data in models_data.items():
                try:
                    # Ensure model_id is in the data
                    model_data['model_id'] = model_id

                    # Handle missing optional fields with defaults
                    if 'display_name' not in model_data:
                        model_data['display_name'] = model_data.get('name', model_id)

                    if 'supported_tasks' not in model_data:
                        model_data['supported_tasks'] = []

                    if 'tags' not in model_data:
                        model_data['tags'] = []

                    if 'last_used' not in model_data:
                        model_data['last_used'] = None

                    if 'requirements' not in model_data:
                        model_data['requirements'] = None

                    if 'download_progress' not in model_data:
                        model_data['download_progress'] = 0.0

                    model_config = ModelConfig(**model_data)
                    self.models_config[model_id] = model_config
                except Exception as e:
                    logger.error(f"❌ Error creating ModelConfig for {model_id}: {e}")
                    logger.error(f"   Model data keys: {list(model_data.keys())}")

            logger.info(f"✅ Loaded {len(self.models_config)} model configurations")

        except Exception as e:
            logger.error(f"❌ Error loading models config: {e}")

    def _migrate_legacy_configs(self):
        """Migrate legacy configuration files to unified system"""
        try:
            # Check for legacy files and backup them
            legacy_files = [
                "local_model_config_cache.json",
                "local_models_config.py",
                "model_config.py"
            ]

            for legacy_file in legacy_files:
                legacy_path = self.config_dir / legacy_file
                if legacy_path.exists():
                    backup_path = legacy_path.with_suffix('.bak')
                    if not backup_path.exists():
                        import shutil
                        shutil.copy2(legacy_path, backup_path)
                        logger.info(f"📦 Backed up legacy config: {legacy_file}")

        except Exception as e:
            logger.warning(f"⚠️ Error during legacy config migration: {e}")

    # Model Management Methods
    def get_model_config(self, model_id: str) -> Optional[ModelConfig]:
        """Get configuration for a specific model"""
        return self.models_config.get(model_id)

    def get_all_models(self) -> Dict[str, ModelConfig]:
        """Get all model configurations"""
        return self.models_config.copy()

    def get_models_by_type(self, model_type: str) -> Dict[str, ModelConfig]:
        """Get models by type (llm, embedding, etc.)"""
        return {
            model_id: config
            for model_id, config in self.models_config.items()
            if config.type == model_type
        }

    def get_models_by_format(self, format_type: str) -> Dict[str, ModelConfig]:
        """Get models by format (gguf, pytorch, etc.)"""
        return {
            model_id: config
            for model_id, config in self.models_config.items()
            if config.format == format_type
        }

    def get_downloaded_models(self) -> Dict[str, ModelConfig]:
        """Get models that are marked as downloaded"""
        return {
            model_id: config
            for model_id, config in self.models_config.items()
            if config.is_downloaded
        }

    def update_model_status(self, model_id: str, is_downloaded: bool = None,
                           is_loaded: bool = None, download_progress: float = None):
        """Update model status"""
        with self._lock:
            if model_id in self.models_config:
                if is_downloaded is not None:
                    self.models_config[model_id].is_downloaded = is_downloaded
                if is_loaded is not None:
                    self.models_config[model_id].is_loaded = is_loaded
                if download_progress is not None:
                    self.models_config[model_id].download_progress = download_progress

                # Save to cache file
                self._save_config_cache()

    def add_model_config(self, model_config: ModelConfig):
        """Add a new model configuration"""
        with self._lock:
            self.models_config[model_config.model_id] = model_config
            self._save_config_cache()

    def remove_model_config(self, model_id: str):
        """Remove a model configuration"""
        with self._lock:
            if model_id in self.models_config:
                del self.models_config[model_id]
                self._save_config_cache()

    def _save_config_cache(self):
        """Save current configuration to cache file"""
        try:
            cache_path = self.config_dir / "unified_config_cache.json"
            cache_data = {
                'system_config': asdict(self.system_config),
                'models_config': {
                    model_id: asdict(config)
                    for model_id, config in self.models_config.items()
                }
            }

            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            logger.error(f"❌ Error saving config cache: {e}")

    def load_config_cache(self):
        """Load configuration from cache file"""
        try:
            cache_path = self.config_dir / "unified_config_cache.json"
            if cache_path.exists():
                with open(cache_path, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)

                # Load system config
                if 'system_config' in cache_data:
                    for key, value in cache_data['system_config'].items():
                        if hasattr(self.system_config, key):
                            setattr(self.system_config, key, value)

                # Load models config
                if 'models_config' in cache_data:
                    for model_id, model_data in cache_data['models_config'].items():
                        try:
                            self.models_config[model_id] = ModelConfig(**model_data)
                        except Exception as e:
                            logger.warning(f"⚠️ Error loading cached model {model_id}: {e}")

                logger.info("✅ Configuration cache loaded")

        except Exception as e:
            logger.warning(f"⚠️ Error loading config cache: {e}")

    # Utility Methods
    def get_models_for_task(self, task: str) -> List[ModelConfig]:
        """Get models suitable for a specific task"""
        suitable_models = []

        for config in self.models_config.values():
            if task in config.supported_tasks:
                suitable_models.append(config)

        # Sort by memory requirement (prefer smaller models first)
        suitable_models.sort(key=lambda x: x.memory_required)
        return suitable_models

    def get_recommended_models(self, max_memory_mb: int = None) -> List[ModelConfig]:
        """Get recommended models based on system capabilities"""
        if max_memory_mb is None:
            # Estimate available memory (simple heuristic)
            max_memory_mb = 8192  # 8GB default

        recommended = []

        for config in self.models_config.values():
            if config.memory_required <= max_memory_mb:
                recommended.append(config)

        return recommended

    def get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        return {
            'total_models': len(self.models_config),
            'downloaded_models': len(self.get_downloaded_models()),
            'system_config': asdict(self.system_config),
            'models_directory': self.system_config.models_directory,
            'cache_directory': self.system_config.cache_directory
        }

    def cleanup_cache(self):
        """Clean up cache files"""
        try:
            cache_path = self.config_dir / "unified_config_cache.json"
            if cache_path.exists():
                cache_path.unlink()
                logger.info("🧹 Cache cleaned up")

        except Exception as e:
            logger.error(f"❌ Error cleaning cache: {e}")

# Global instance
config_manager = UnifiedConfigManager()

# Backwards compatibility aliases
ModelConfigManager = UnifiedConfigManager
LocalModelsConfig = UnifiedConfigManager
