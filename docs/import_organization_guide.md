# Import Organization and Best Practices Guide

## Overview

This guide explains the import organization strategy implemented in the ValidoAI project, following best practices for Python applications with multiple optional dependencies.

## Import Strategy

### 1. Core Imports (app.py)

**Location**: `app.py` - Top of the file

**Purpose**: Imports that are needed by every part of the project

**What goes here**:
- Standard library imports
- Core Flask dependencies (always required)
- Environment variable loading
- Lazy loading system initialization
- Core project modules

```python
# Standard Library Imports (Always Available)
import warnings
import os
import sys
import json
import logging
import uuid
import asyncio
import tempfile
import importlib
from datetime import datetime, timedelta
from functools import wraps
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable, Union, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

# Core Flask Dependencies (Always Required)
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, g, session, current_app, send_file, make_response
from flask_login import LoginManager, login_required, current_user, login_user, logout_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

# Database Core (Required)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey, UUID, JSON, Index, create_engine
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Environment Variables Support (Required)
from dotenv import load_dotenv
```

### 2. Lazy Loading System

**Purpose**: Import optional dependencies only when needed

**Implementation**: `LazyModuleLoader` class in `app.py`

```python
class LazyModuleLoader:
    """Advanced lazy loading system for optional dependencies"""
    
    def __init__(self):
        self._modules: Dict[str, Any] = {}
        self._availability: Dict[str, bool] = {}
        self._logger = logging.getLogger(__name__)
    
    def load_module(self, module_name: str, fallback=None):
        """Load a module lazily, returning fallback if not available"""
        if not self._check_availability(module_name):
            return fallback
        
        if module_name not in self._modules:
            try:
                self._modules[module_name] = importlib.import_module(module_name)
            except (ImportError, ModuleNotFoundError) as e:
                self._logger.debug(f"Failed to import {module_name}: {e}")
                self._modules[module_name] = fallback
        
        return self._modules[module_name]
```

### 3. Controller-Specific Imports

**Purpose**: Import dependencies only when specific features are used

**Examples**:

#### Database Controller (`src/controllers/database_controller.py`)
```python
def _get_postgresql_connection(self):
    """Get PostgreSQL connection with lazy loading."""
    if 'postgresql' not in self._databases:
        try:
            import psycopg2  # Only imported when needed
            from psycopg2.extras import RealDictCursor
            
            # Connection logic here
            self._databases['postgresql'] = {
                'connection': conn,
                'driver': psycopg2,
                'version': psycopg2.__version__
            }
            
        except ImportError:
            logger.error("❌ PostgreSQL driver (psycopg2) not available")
            raise ImportError("PostgreSQL driver not available. Install with: pip install psycopg2")
```

#### AI/ML Controller (`src/controllers/ai_ml_controller.py`)
```python
def _get_tensorflow_model(self, model_type: str = 'simple'):
    """Get TensorFlow model with lazy loading."""
    if f'tensorflow_{model_type}' not in self._ai_models:
        try:
            import tensorflow as tf  # Only imported when needed
            
            # Model creation logic here
            self._ai_models[f'tensorflow_{model_type}'] = {
                'model': model,
                'framework': tf,
                'version': tf.__version__,
                'type': 'tensorflow'
            }
            
        except ImportError:
            logger.error("❌ TensorFlow not available")
            raise ImportError("TensorFlow not available. Install with: pip install tensorflow")
```

## Best Practices

### 1. Import Organization

**Rule**: Imports should be organized in this order:
1. Standard library imports
2. Third-party library imports
3. Local application imports
4. Relative imports

**Example**:
```python
# 1. Standard library
import os
import sys
from typing import Dict, List

# 2. Third-party libraries
from flask import Flask, jsonify
import requests

# 3. Local application imports
from src.config import config_manager
from src.database import database_manager

# 4. Relative imports (if any)
from .models import User
```

### 2. Lazy Loading Patterns

**Pattern 1**: Try-Except Import
```python
def use_feature():
    try:
        import heavy_library
        return heavy_library.do_something()
    except ImportError:
        logger.warning("Heavy library not available")
        return fallback_implementation()
```

**Pattern 2**: Cached Lazy Loading
```python
class FeatureController:
    def __init__(self):
        self._cache = {}
    
    def get_feature(self, feature_name):
        if feature_name not in self._cache:
            try:
                module = importlib.import_module(feature_name)
                self._cache[feature_name] = module
            except ImportError:
                self._cache[feature_name] = None
        return self._cache[feature_name]
```

### 3. Error Handling

**Always provide helpful error messages**:
```python
try:
    import tensorflow as tf
except ImportError:
    raise ImportError(
        "TensorFlow not available. Install with: pip install tensorflow"
    )
```

### 4. Testing Imports

**Use the comprehensive test suite**:
```bash
# Run comprehensive dependency test
python tests/test_imports_and_dependencies.py

# Run quick test
python tests/run_tests.py
```

## Dependency Categories

### Core Dependencies (Always Required)
- `flask`
- `flask_sqlalchemy`
- `flask_login`
- `werkzeug`
- `sqlalchemy`
- `dotenv`

### Database Dependencies (Optional)
- `psycopg2` (PostgreSQL)
- `pymysql` (MySQL)
- `pymongo` (MongoDB)
- `redis` (Redis)
- `cassandra` (Cassandra)
- `neo4j` (Neo4j)
- `elasticsearch` (Elasticsearch)

### Vector Database Dependencies (Optional)
- `pinecone`
- `weaviate`
- `qdrant_client`
- `chromadb`
- `milvus`
- `faiss`

### AI/ML Dependencies (Optional)
- `tensorflow`
- `torch`
- `sentence_transformers`
- `openai`
- `cohere`
- `transformers`
- `scikit-learn`
- `pandas`
- `numpy`

### Flask Extensions (Optional)
- `flask_socketio`
- `flask_wtf`
- `flask_migrate`
- `flask_session`
- `flask_cors`

### ASGI/Production Dependencies (Optional)
- `asgiref`
- `hypercorn`
- `aioquic`

### Monitoring Dependencies (Optional)
- `prometheus_client`
- `psutil`

### Utility Dependencies (Optional)
- `requests`
- `aiohttp`
- `celery`

## Testing Strategy

### 1. Comprehensive Test Suite
**File**: `tests/test_imports_and_dependencies.py`

**Features**:
- Tests all dependencies for availability
- Checks project module imports
- Validates controller instantiation
- Tests database connections
- Generates detailed reports

### 2. Quick Test Runner
**File**: `tests/run_tests.py`

**Features**:
- Fast validation of core functionality
- Tests basic imports
- Validates lazy loading system
- Checks controller functionality
- Tests app creation

### 3. Running Tests

```bash
# Comprehensive test
python tests/test_imports_and_dependencies.py

# Quick test
python tests/run_tests.py

# Individual controller tests
python -c "from src.controllers.example_controller import ExampleController; print('✅ ExampleController works')"
```

## Benefits of This Approach

### 1. Performance
- **Faster startup**: Only loads what's needed
- **Reduced memory usage**: Heavy libraries loaded on demand
- **Better resource utilization**: Avoids loading unused dependencies

### 2. Flexibility
- **Optional features**: Can run without heavy dependencies
- **Gradual adoption**: Add features as needed
- **Environment-specific**: Different setups for different environments

### 3. Maintainability
- **Clear dependencies**: Easy to see what's required vs optional
- **Better error handling**: Graceful degradation when dependencies missing
- **Easier testing**: Can test with minimal dependencies

### 4. Development Experience
- **Faster development**: Quick feedback on missing dependencies
- **Better debugging**: Clear error messages for missing packages
- **Comprehensive testing**: Automated validation of all components

## Migration Guide

### From Traditional Imports to Lazy Loading

**Before**:
```python
import tensorflow as tf
import torch
import openai

class MyController:
    def __init__(self):
        self.tf_model = tf.keras.Sequential()
        self.torch_model = torch.nn.Sequential()
```

**After**:
```python
class MyController:
    def __init__(self):
        self._models = {}
    
    def get_tensorflow_model(self):
        if 'tensorflow' not in self._models:
            try:
                import tensorflow as tf
                self._models['tensorflow'] = tf.keras.Sequential()
            except ImportError:
                raise ImportError("TensorFlow not available")
        return self._models['tensorflow']
```

## Troubleshooting

### Common Issues

1. **ImportError for optional dependencies**
   - Install the missing package: `pip install package_name`
   - Or handle gracefully in your code

2. **Performance issues with lazy loading**
   - Cache frequently used modules
   - Use connection pooling for databases

3. **Testing failures**
   - Run `python tests/run_tests.py` to identify issues
   - Check the comprehensive test report

### Debugging Tips

1. **Check dependency availability**:
   ```python
   from app import is_available
   print(is_available('tensorflow'))
   ```

2. **Test specific features**:
   ```python
   from src.controllers.example_controller import ExampleController
   controller = ExampleController()
   print(controller.features)
   ```

3. **Monitor import times**:
   ```python
   import time
   start = time.time()
   import heavy_library
   print(f"Import time: {time.time() - start}")
   ```

## Conclusion

This import organization strategy provides:
- **Optimal performance** through lazy loading
- **Maximum flexibility** with optional dependencies
- **Clear separation** of concerns
- **Comprehensive testing** capabilities
- **Easy maintenance** and debugging

Follow these patterns to ensure your code is efficient, maintainable, and robust.
