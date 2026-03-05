#!/usr/bin/env python3
"""
Lazy Importer System for ValidoAI
=================================
Dynamic import system that loads modules only when needed
Optimizes memory usage and startup time
"""

import importlib
import sys
from typing import Dict, Any, Optional, Callable, List
import logging
from pathlib import Path
import time

logger = logging.getLogger(__name__)

class LazyImporter:
    """
    Lazy importer that loads modules on-demand
    Provides performance optimization through deferred imports
    """

    def __init__(self):
        self._cache: Dict[str, Any] = {}
        self._import_times: Dict[str, float] = {}
        self._failed_imports: List[str] = []

    def lazy_import(self, module_name: str, attribute: str = None, fallback: Any = None) -> Any:
        """
        Lazy import a module or attribute

        Args:
            module_name: Name of the module to import
            attribute: Specific attribute to import from the module
            fallback: Fallback value if import fails

        Returns:
            Imported module/attribute or fallback
        """
        cache_key = f"{module_name}.{attribute}" if attribute else module_name

        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]

        try:
            start_time = time.time()

            # Import the module
            module = importlib.import_module(module_name)

            # Get specific attribute if requested
            if attribute:
                result = getattr(module, attribute, fallback)
            else:
                result = module

            # Cache the result
            self._cache[cache_key] = result

            # Track import time
            self._import_times[cache_key] = time.time() - start_time

            logger.debug(f"Lazy imported: {cache_key} in {self._import_times[cache_key]:.4f}s")
            return result

        except ImportError as e:
            logger.warning(f"Failed to import {cache_key}: {e}")
            self._failed_imports.append(cache_key)
            return fallback
        except Exception as e:
            logger.error(f"Error importing {cache_key}: {e}")
            self._failed_imports.append(cache_key)
            return fallback

    def bulk_import(self, imports: Dict[str, Any]) -> Dict[str, Any]:
        """
        Bulk import multiple modules/attributes

        Args:
            imports: Dict mapping alias to module/attribute specification

        Returns:
            Dict mapping alias to imported objects
        """
        results = {}

        for alias, spec in imports.items():
            if isinstance(spec, dict):
                module_name = spec.get('module', '')
                attribute = spec.get('attribute')
                fallback = spec.get('fallback')
            else:
                module_name = spec
                attribute = None
                fallback = None

            results[alias] = self.lazy_import(module_name, attribute, fallback)

        return results

    def get_import_stats(self) -> Dict[str, Any]:
        """Get statistics about lazy imports"""
        return {
            'cached_imports': len(self._cache),
            'failed_imports': len(self._failed_imports),
            'total_import_time': sum(self._import_times.values()),
            'average_import_time': sum(self._import_times.values()) / len(self._import_times) if self._import_times else 0,
            'import_times': self._import_times,
            'failed_imports_list': self._failed_imports
        }

    def clear_cache(self):
        """Clear the import cache"""
        self._cache.clear()
        self._import_times.clear()
        self._failed_imports.clear()

# Global lazy importer instance
lazy_importer = LazyImporter()

# Convenience functions for common imports
def lazy_flask_import(attribute: str = None):
    """Lazy import Flask components"""
    return lazy_importer.lazy_import('flask', attribute)

def lazy_sqlalchemy_import(attribute: str = None):
    """Lazy import SQLAlchemy components"""
    return lazy_importer.lazy_import('flask_sqlalchemy', attribute)

def lazy_login_import(attribute: str = None):
    """Lazy import Flask-Login components"""
    return lazy_importer.lazy_import('flask_login', attribute)

def lazy_werkzeug_import(attribute: str = None):
    """Lazy import Werkzeug components"""
    return lazy_importer.lazy_import('werkzeug.security', attribute)

def lazy_ai_import(module: str, attribute: str = None):
    """Lazy import AI/ML components"""
    return lazy_importer.lazy_import(f'src.ai.{module}', attribute)

def lazy_config_import(attribute: str = None):
    """Lazy import configuration components"""
    return lazy_importer.lazy_import('src.config.master_config', attribute)

def lazy_database_import(attribute: str = None):
    """Lazy import database components"""
    return lazy_importer.lazy_import('src.database', attribute)

def lazy_model_import(attribute: str = None):
    """Lazy import model components"""
    return lazy_importer.lazy_import('src.models.unified_models', attribute)

# Bulk import definitions for common use cases
COMMON_FLASK_IMPORTS = {
    'Flask': {'module': 'flask', 'attribute': 'Flask'},
    'request': {'module': 'flask', 'attribute': 'request'},
    'jsonify': {'module': 'flask', 'attribute': 'jsonify'},
    'render_template': {'module': 'flask', 'attribute': 'render_template'},
    'redirect': {'module': 'flask', 'attribute': 'redirect'},
    'url_for': {'module': 'flask', 'attribute': 'url_for'},
    'flash': {'module': 'flask', 'attribute': 'flash'},
    'session': {'module': 'flask', 'attribute': 'session'},
    'current_app': {'module': 'flask', 'attribute': 'current_app'},
    'g': {'module': 'flask', 'attribute': 'g'},
    'send_file': {'module': 'flask', 'attribute': 'send_file'},
    'make_response': {'module': 'flask', 'attribute': 'make_response'},
}

COMMON_SQLALCHEMY_IMPORTS = {
    'SQLAlchemy': {'module': 'flask_sqlalchemy', 'attribute': 'SQLAlchemy'},
    'db': {'module': 'src.models.unified_models', 'attribute': 'db'},
    'Company': {'module': 'src.models.unified_models', 'attribute': 'Company'},
    'User': {'module': 'src.models.unified_models', 'attribute': 'User'},
}

COMMON_AI_IMPORTS = {
    'SentimentAnalyzer': {'module': 'src.ai.sentiment', 'attribute': 'SentimentAnalyzer'},
    'LocalModelManager': {'module': 'src.models.unified_models', 'attribute': 'LocalModelManager'},
    'UnifiedModelManager': {'module': 'src.models.unified_models', 'attribute': 'UnifiedModelManager'},
}

class LazyControllerMixin:
    """
    Mixin class for controllers that use lazy imports
    Provides common functionality and lazy-loaded dependencies
    """

    def __init__(self):
        self._imports_loaded = False
        self._flask_imports = {}
        self._ai_imports = {}
        self._db_imports = {}

    def ensure_imports_loaded(self):
        """Ensure all necessary imports are loaded"""
        if not self._imports_loaded:
            self._load_common_imports()
            self._imports_loaded = True

    def _load_common_imports(self):
        """Load common imports used by controllers"""
        try:
            # Load Flask imports
            self._flask_imports = lazy_importer.bulk_import(COMMON_FLASK_IMPORTS)

            # Load AI imports
            self._ai_imports = lazy_importer.bulk_import(COMMON_AI_IMPORTS)

            # Load database imports
            self._db_imports = lazy_importer.bulk_import(COMMON_SQLALCHEMY_IMPORTS)

            logger.debug("Common imports loaded successfully")

        except Exception as e:
            logger.error(f"Error loading common imports: {e}")

    def get_flask_component(self, name: str):
        """Get Flask component with lazy loading"""
        self.ensure_imports_loaded()
        return self._flask_imports.get(name)

    def get_ai_component(self, name: str):
        """Get AI component with lazy loading"""
        self.ensure_imports_loaded()
        return self._ai_imports.get(name)

    def get_db_component(self, name: str):
        """Get database component with lazy loading"""
        self.ensure_imports_loaded()
        return self._db_imports.get(name)

# Utility functions for performance monitoring
def get_lazy_import_stats():
    """Get global lazy import statistics"""
    return lazy_importer.get_import_stats()

def clear_lazy_import_cache():
    """Clear global lazy import cache"""
    lazy_importer.clear_cache()

def create_lazy_controller_class(base_class=None):
    """
    Create a controller class with lazy loading capabilities

    Args:
        base_class: Base class to inherit from (optional)

    Returns:
        Controller class with lazy loading
    """
    if base_class:
        class LazyController(base_class, LazyControllerMixin):
            def __init__(self, *args, **kwargs):
                if base_class:
                    base_class.__init__(self, *args, **kwargs)
                LazyControllerMixin.__init__(self)
    else:
        class LazyController(LazyControllerMixin):
            def __init__(self, *args, **kwargs):
                LazyControllerMixin.__init__(self)

    return LazyController

if __name__ == "__main__":
    # Test the lazy importer
    print("Testing Lazy Importer System...")

    # Test basic import
    flask_app = lazy_importer.lazy_import('flask', 'Flask')
    print(f"Flask imported: {flask_app is not None}")

    # Test statistics
    stats = get_lazy_import_stats()
    print(f"Import stats: {stats}")

    print("✅ Lazy importer test completed")
