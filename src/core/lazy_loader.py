"""
Lazy Loading System for Memory Optimization
==========================================

Implements lazy loading for heavy dependencies to reduce memory footprint.
Only loads heavy ML libraries when actually needed.
"""

import sys
import logging
from typing import Dict, Any, Optional, Callable

logger = logging.getLogger(__name__)

class LazyLoader:
    """Lazy loading system for memory optimization"""

    def __init__(self):
        self._loaded_modules: Dict[str, Any] = {}
        self._load_functions: Dict[str, Callable] = {}

    def register_module(self, name: str, import_function: Callable):
        """Register a module for lazy loading"""
        self._load_functions[name] = import_function
        logger.info(f"✅ Registered lazy module: {name}")

    def get_module(self, name: str) -> Any:
        """Get a module, loading it if necessary"""
        if name not in self._loaded_modules:
            if name in self._load_functions:
                try:
                    logger.info(f"🔄 Lazy loading module: {name}")
                    self._loaded_modules[name] = self._load_functions[name]()
                    logger.info(f"✅ Successfully loaded: {name}")
                except Exception as e:
                    logger.error(f"❌ Failed to load {name}: {e}")
                    raise
            else:
                raise ImportError(f"Module {name} not registered for lazy loading")

        return self._loaded_modules[name]

    def is_loaded(self, name: str) -> bool:
        """Check if a module is already loaded"""
        return name in self._loaded_modules

# Global lazy loader instance
lazy_loader = LazyLoader()

# Register heavy ML modules for lazy loading
def _load_torch():
    """Lazy load PyTorch"""
    import torch
    return torch

def _load_transformers():
    """Lazy load transformers"""
    import transformers
    return transformers

def _load_sentence_transformers():
    """Lazy load sentence transformers"""
    import sentence_transformers
    return sentence_transformers

def _load_openai():
    """Lazy load OpenAI"""
    import openai
    return openai

def _load_cohere():
    """Lazy load Cohere"""
    import cohere
    return cohere

# Register all heavy modules
lazy_loader.register_module('torch', _load_torch)
lazy_loader.register_module('transformers', _load_transformers)
lazy_loader.register_module('sentence_transformers', _load_sentence_transformers)
lazy_loader.register_module('openai', _load_openai)
lazy_loader.register_module('cohere', _load_cohere)

def get_torch():
    """Get PyTorch with lazy loading"""
    return lazy_loader.get_module('torch')

def get_transformers():
    """Get transformers with lazy loading"""
    return lazy_loader.get_module('transformers')

def get_sentence_transformers():
    """Get sentence transformers with lazy loading"""
    return lazy_loader.get_module('sentence_transformers')

def get_openai():
    """Get OpenAI with lazy loading"""
    return lazy_loader.get_module('openai')

def get_cohere():
    """Get Cohere with lazy loading"""
    return lazy_loader.get_module('cohere')
