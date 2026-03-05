#!/usr/bin/env python3
"""
Singleton Pattern Implementation
Ensures a single instance of a class (e.g., database connections, LLM models)
"""

import threading
import sqlite3
import logging
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class Singleton(ABC):
    """Abstract base class for Singleton pattern"""
    
    _instances = {}
    _lock = threading.Lock()
    
    def __new__(cls, *args, **kwargs):
        if cls not in cls._instances:
            with cls._lock:
                if cls not in cls._instances:
                    cls._instances[cls] = super().__new__(cls)
        return cls._instances[cls]

class DatabaseConnection(Singleton):
    """Singleton database connection manager"""
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._connections = {}
            self._initialized = True
    
    def get_connection(self, db_path: str) -> sqlite3.Connection:
        """Get or create database connection"""
        if db_path not in self._connections:
            try:
                self._connections[db_path] = sqlite3.connect(db_path)
                logger.info(f"Created new database connection: {db_path}")
            except Exception as e:
                logger.error(f"Failed to create database connection: {e}")
                raise
        
        return self._connections[db_path]
    
    def close_connection(self, db_path: str):
        """Close specific database connection"""
        if db_path in self._connections:
            try:
                self._connections[db_path].close()
                del self._connections[db_path]
                logger.info(f"Closed database connection: {db_path}")
            except Exception as e:
                logger.error(f"Failed to close database connection: {e}")
    
    def close_all_connections(self):
        """Close all database connections"""
        for db_path in list(self._connections.keys()):
            self.close_connection(db_path)

class LLMModelManager(Singleton):
    """Singleton LLM model manager for memory-intensive models"""
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._models = {}
            self._model_configs = {}
            self._initialized = True
    
    def load_model(self, model_id: str, model_config: Dict[str, Any]) -> Any:
        """Load and cache LLM model"""
        if model_id not in self._models:
            try:
                # Simulate model loading (replace with actual model loading)
                logger.info(f"Loading model: {model_id}")
                self._models[model_id] = {
                    "model": f"Loaded model: {model_id}",
                    "config": model_config,
                    "loaded_at": "2024-01-01T00:00:00Z"
                }
                self._model_configs[model_id] = model_config
            except Exception as e:
                logger.error(f"Failed to load model {model_id}: {e}")
                raise
        
        return self._models[model_id]["model"]
    
    def get_model(self, model_id: str) -> Optional[Any]:
        """Get loaded model"""
        return self._models.get(model_id, {}).get("model")
    
    def unload_model(self, model_id: str):
        """Unload model to free memory"""
        if model_id in self._models:
            try:
                # Simulate model unloading
                logger.info(f"Unloading model: {model_id}")
                del self._models[model_id]
                if model_id in self._model_configs:
                    del self._model_configs[model_id]
            except Exception as e:
                logger.error(f"Failed to unload model {model_id}: {e}")
    
    def list_loaded_models(self) -> Dict[str, Any]:
        """List all loaded models"""
        return {
            model_id: {
                "config": config,
                "loaded_at": self._models[model_id]["loaded_at"]
            }
            for model_id, config in self._model_configs.items()
        }

class ConfigManager(Singleton):
    """Singleton configuration manager"""
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._config = {}
            self._initialized = True
    
    def set_config(self, key: str, value: Any):
        """Set configuration value"""
        self._config[key] = value
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self._config.get(key, default)
    
    def get_all_config(self) -> Dict[str, Any]:
        """Get all configuration"""
        return self._config.copy()
