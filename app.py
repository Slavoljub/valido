"""
ValidoAI - Universal Multi-Database Platform
===========================================
A comprehensive AI-powered database platform supporting:
- SQLite (development/lightweight)
- PostgreSQL (production/enterprise)
- MySQL (legacy/compatibility)
- Advanced materialized views for analytics
- Semantic search with embeddings
- Automated workflows and monitoring
- Real-time dashboard and reporting
- Full CRUD operations with modern UI
- Serbian business compliance

Following Cursor Rules:
- Essential imports only in app.py (needed by all parts)
- Feature-specific imports moved to controllers
- All routes in /routes.py
- Models following MVC/MVVM/OOP patterns
"""

# ============================================================================
# OPTIMIZED IMPORTS - Essential Dependencies Only
# ============================================================================

"""
Import Strategy:
1. Standard Library (built-in modules)
2. Core Flask dependencies (always required)
3. Essential database and configuration
4. Lazy loading system for optional dependencies
5. Feature-specific imports moved to controllers
"""

# ============================================================================
# 1. STANDARD LIBRARY IMPORTS (Always Available)
# ============================================================================

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

# Suppress benign SSL warning from Windows certificate store
warnings.filterwarnings("ignore", message="Bad certificate in Windows certificate store")
sys.path.insert(0, "src")

# ============================================================================
# 2. CORE FLASK DEPENDENCIES (Always Required)
# ============================================================================

# Flask Core (Required)
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

# Load environment variables at the top to avoid conflicts with lazy-loaded modules
load_dotenv()

# Disable colorama to avoid conflicts
os.environ['NO_COLOR'] = '1'

# ============================================================================
# 3. LAZY LOADING SYSTEM FOR OPTIONAL DEPENDENCIES
# ============================================================================

class LazyModuleLoader:
    """Advanced lazy loading system for optional dependencies"""
    
    def __init__(self):
        self._modules: Dict[str, Any] = {}
        self._availability: Dict[str, bool] = {}
        self._logger = logging.getLogger(__name__)
    
    def _check_availability(self, module_name: str) -> bool:
        """Check if a module is available without importing it"""
        if module_name not in self._availability:
            try:
                importlib.util.find_spec(module_name)
                self._availability[module_name] = True
            except (ImportError, ModuleNotFoundError):
                self._availability[module_name] = False
        return self._availability[module_name]
    
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
    
    def get_attr(self, module_name: str, attr_name: str, fallback=None):
        """Get an attribute from a lazily loaded module"""
        module = self.load_module(module_name, fallback)
        if module is None:
            return fallback
        return getattr(module, attr_name, fallback)
    
    def is_available(self, module_name: str) -> bool:
        """Check if a module is available"""
        return self._check_availability(module_name)

# Initialize the lazy loader
lazy_loader = LazyModuleLoader()

# ============================================================================
# 4. ESSENTIAL LAZY LOADING FUNCTIONS (Core Application Needs)
# ============================================================================

def get_socketio():
    """Get Flask-SocketIO for WebSocket support"""
    return lazy_loader.load_module('flask_socketio')

def get_cors():
    """Get Flask-CORS for cross-origin support"""
    return lazy_loader.load_module('flask_cors')

def get_migrate():
    """Get Flask-Migrate for database migrations"""
    return lazy_loader.load_module('flask_migrate')

def get_session():
    """Get Flask-Session for session management"""
    return lazy_loader.load_module('flask_session')

def get_mail():
    """Get Flask-Mail for email functionality"""
    return lazy_loader.load_module('flask_mail')

def get_cache():
    """Get Flask-Caching for caching support"""
    return lazy_loader.load_module('flask_caching')

def get_asgi_components():
    """Get ASGI components for production server"""
    wsgi_to_asgi = lazy_loader.load_module('asgiref.wsgi')
    hypercorn = lazy_loader.load_module('hypercorn')
    return wsgi_to_asgi, hypercorn

# ============================================================================
# 5. LOCAL IMPORTS (Project Modules)
# ============================================================================

# Configuration and Core Modules
from src.config import UnifiedConfigManager
# Error handling is now handled by the DRY functions in routes.py
from src.core import setup_logging

# Database Management
from src.database import database_manager

# Controllers (lazy loaded when needed)
# Note: Controllers handle their own imports for feature-specific functionality

# ============================================================================
# 6. APPLICATION CONFIGURATION
# ============================================================================

# Initialize configuration
config_manager = UnifiedConfigManager()
all_configs = {
    'flask': config_manager.get_flask_config(),
    'server': config_manager.get_server_config().__dict__,
    'database': config_manager.get_database_config().__dict__,
    'ai': config_manager.get_ai_config().__dict__,
    'security': config_manager.get_security_config().__dict__
}

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# ============================================================================
# 7. FLASK APPLICATION FACTORY
# ============================================================================

def create_app(config_name='development'):
    """Application factory pattern for Flask app creation"""
    
    # Create Flask app
    app = Flask(__name__)
    
    # Configure app
    app.config.update(all_configs['flask'])
    
    # Initialize extensions
    _initialize_extensions(app)
    
    # Setup error handlers
    # Error handling is now handled by the DRY functions in routes.py
    
    # Register blueprints
    _register_blueprints(app)
    
    # Database initialization is handled separately when needed
    
    logger.info(f"Flask application created with config: {config_name}")
    return app

def _initialize_extensions(app):
    """Initialize Flask extensions with lazy loading"""
    
    # CORS (if available)
    cors_module = get_cors()
    if cors_module:
        cors_module.CORS(app, resources={r"/api/*": {"origins": "*"}})
        logger.info("CORS extension initialized")
    
    # Session management (if available)
    session_module = get_session()
    if session_module:
        # Configure session before initializing
        app.config['SESSION_TYPE'] = 'filesystem'
        app.config['SESSION_FILE_DIR'] = 'flask_session'
        app.config['SESSION_PERMANENT'] = False
        app.config['PERMANENT_SESSION_LIFETIME'] = 3600
        session_module.Session(app)
        logger.info("Session extension initialized")
    
    # Login manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    @login_manager.user_loader
    def load_user(user_id):
        # Lazy load user model when needed
        try:
            from src.models.user import User
            return User.query.get(int(user_id))
        except ImportError:
            logger.warning("User model not available")
            return None
    
    logger.info("Login manager initialized")

def _register_blueprints(app):
    """Register Flask blueprints"""
    
    # Import routes (routes.py handles all route registration)
    from routes import main_bp, api_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    logger.info("Blueprints registered")

# ============================================================================
# 8. ASGI APPLICATION WRAPPER
# ============================================================================

class ValidoAsgiApp:
    """ASGI wrapper for Flask application with production features"""
    
    def __init__(self, flask_app):
        self.flask_app = flask_app
        self._asgi_app = None
        self._setup_asgi()
    
    def _setup_asgi(self):
        """Setup ASGI application with WebSocket support"""
        try:
            wsgi_to_asgi, hypercorn = get_asgi_components()
            if wsgi_to_asgi and hypercorn:
                # Add WebSocket support if available
                socketio_module = get_socketio()
                if socketio_module:
                    try:
                        socketio = socketio_module.SocketIO(self.flask_app, cors_allowed_origins="*")
                        # Check if asgi_app attribute exists before using it
                        if hasattr(socketio, 'asgi_app'):
                            self._asgi_app = socketio.asgi_app
                            logger.info("ASGI app with WebSocket support initialized")
                        else:
                            # Fallback to WSGI to ASGI conversion
                            self._asgi_app = wsgi_to_asgi.WsgiToAsgi(self.flask_app)
                            logger.info("ASGI app with WSGI to ASGI conversion initialized")
                    except Exception as e:
                        logger.warning(f"SocketIO setup failed: {e}")
                        self._asgi_app = wsgi_to_asgi.WsgiToAsgi(self.flask_app)
                        logger.info("ASGI app with WSGI to ASGI conversion initialized")
                else:
                    self._asgi_app = wsgi_to_asgi.WsgiToAsgi(self.flask_app)
                    logger.info("ASGI app without WebSocket support initialized")
            else:
                self._asgi_app = self.flask_app
                logger.warning("ASGI components not available, using Flask app directly")
        except Exception as e:
            logger.error(f"Error setting up ASGI app: {e}")
            self._asgi_app = self.flask_app
    
    def __call__(self, *args, **kwargs):
        """Universal callable interface that handles both WSGI and ASGI"""
        if len(args) == 2:  # WSGI call: (environ, start_response)
            return self.flask_app(*args, **kwargs)
        elif len(args) == 3:  # ASGI call: (scope, receive, send)
            scope, receive, send = args
            if self._asgi_app:
                return self._asgi_app(scope, receive, send)
            else:
                # Fallback to WSGI
                return self.flask_app(scope, receive, send)
        else:
            raise TypeError(f"Invalid number of arguments: {len(args)}")

# ============================================================================
# 9. PRODUCTION SERVER CONFIGURATION
# ============================================================================

def _cpu_workers():
    """Calculate optimal number of workers based on CPU cores"""
    import multiprocessing
    return max(1, multiprocessing.cpu_count() - 1)

def build_hypercorn_config():
    """Build Hypercorn configuration for production"""
    try:
        from hypercorn.config import Config
        
        config = Config()
        
        # Server settings
        config.bind = [f"{all_configs['server']['host']}:{all_configs['server']['http_port']}"]
        config.workers = all_configs['server'].get('workers', _cpu_workers())
        
        # Timeout settings
        config.keep_alive_timeout = all_configs['server'].get('keepalive_timeout', 30)
        config.read_timeout = all_configs['server'].get('read_timeout', 30)
        config.write_timeout = all_configs['server'].get('write_timeout', 30)
        
        # Request limits
        config.max_requests = all_configs['server'].get('max_requests', 1000)
        config.max_requests_jitter = all_configs['server'].get('max_requests_jitter', 100)
        
        # SSL/TLS settings
        if all_configs['server'].get('ssl_enabled', False):
            cert_file = all_configs['server'].get('ssl_cert_file')
            key_file = all_configs['server'].get('ssl_key_file')
            if cert_file and key_file and os.path.exists(cert_file) and os.path.exists(key_file):
                config.certfile = cert_file
                config.keyfile = key_file
                logger.info("SSL/TLS enabled")
        
        # HTTP/2 and HTTP/3
        config.http = "h2" if all_configs['server'].get('http2_enabled', True) else "1"
        
        logger.info(f"Hypercorn config built: {config.bind}, workers: {config.workers}")
        return config
        
    except Exception as e:
        logger.error(f"Error building Hypercorn config: {e}")
        return None

def run_asgi_server():
    """Run the application using Hypercorn ASGI server"""
    try:
        from hypercorn.config import Config
        from hypercorn.asyncio import serve
        
        config = build_hypercorn_config()
        if not config:
            logger.error("Failed to build Hypercorn configuration")
            return False
        
        # Create Flask app
        app = create_app()
        
        # Create ASGI app
        asgi_app = ValidoAsgiApp(app)
        
        # Run server
        logger.info("Starting Hypercorn ASGI server...")
        import asyncio
        asyncio.run(serve(asgi_app, config))
        return True
        
    except Exception as e:
        logger.error(f"Error running ASGI server: {e}")
        return False

# ============================================================================
# 10. APPLICATION INSTANCES
# ============================================================================

# Create Flask app instance
app = create_app()

# Create ASGI app instance
asgi_app = ValidoAsgiApp(app)

# ============================================================================
# 11. MAIN EXECUTION
# ============================================================================

import threading
import time

def run_http_server(app, host, port, debug):
    """Run HTTP server in a separate thread"""
    try:
        logger.info(f"Starting HTTP server on {host}:{port}")
        # Disable colorama to avoid conflicts
        os.environ['NO_COLOR'] = '1'
        app.run(host=host, port=port, debug=False, use_reloader=False)
    except Exception as e:
        logger.error(f"HTTP server error: {e}")

def run_https_server(app, host, port, debug, ssl_context):
    """Run HTTPS server in a separate thread"""
    try:
        logger.info(f"Starting HTTPS server on {host}:{port}")
        # Disable colorama to avoid conflicts
        os.environ['NO_COLOR'] = '1'
        app.run(host=host, port=port, debug=False, use_reloader=False, ssl_context=ssl_context)
    except Exception as e:
        logger.error(f"HTTPS server error: {e}")

def run_hypercorn_dual_server():
    """Run Hypercorn ASGI server with dual HTTP/HTTPS support"""
    try:
        # Use the existing Flask app instance
        global app
        
        # Get server configuration
        host = all_configs['server']['host']
        http_port = all_configs['server']['http_port']
        https_port = all_configs['server']['https_port']
        debug = all_configs['flask']['debug']
        
        # Setup SSL context for HTTPS
        ssl_context = None
        if all_configs['server'].get('use_https', False):
            cert_file = all_configs['server'].get('ssl_cert_file', 'certs/cert.pem')
            key_file = all_configs['server'].get('ssl_key_file', 'certs/key.pem')
            
            # Try alternative certificate paths
            if not os.path.exists(cert_file):
                cert_file = 'certs/localhost-cert.crt'
            if not os.path.exists(key_file):
                key_file = 'certs/localhost-key.key'
            
            if os.path.exists(cert_file) and os.path.exists(key_file):
                ssl_context = (cert_file, key_file)
                logger.info(f"SSL context configured: {cert_file}, {key_file}")
            else:
                logger.warning(f"SSL certificate files not found: {cert_file}, {key_file}")
                logger.info("HTTPS will not be available")
        
        # Create ASGI app
        asgi_app = ValidoAsgiApp(app)
        
        # Build Hypercorn configuration for dual protocol
        from hypercorn.config import Config
        from hypercorn.asyncio import serve
        
        config = Config()
        
        # Configure bind addresses for both HTTP and HTTPS
        bind_addresses = [f"{host}:{http_port}"]
        if ssl_context:
            bind_addresses.append(f"{host}:{https_port}")
        
        config.bind = bind_addresses
        
        # Server settings
        config.workers = all_configs['server'].get('workers', _cpu_workers())
        
        # Timeout settings
        config.keep_alive_timeout = all_configs['server'].get('keepalive_timeout', 30)
        config.read_timeout = all_configs['server'].get('read_timeout', 30)
        config.write_timeout = all_configs['server'].get('write_timeout', 30)
        
        # Request limits
        config.max_requests = all_configs['server'].get('max_requests', 1000)
        config.max_requests_jitter = all_configs['server'].get('max_requests_jitter', 100)
        
        # SSL/TLS settings for HTTPS
        if ssl_context:
            config.certfile = ssl_context[0]
            config.keyfile = ssl_context[1]
            logger.info("SSL/TLS enabled for HTTPS")
        
        # HTTP/2 and HTTP/3
        config.http = "h2" if all_configs['server'].get('http2_enabled', True) else "1"
        
        # Development settings
        if debug:
            config.access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
            config.access_logger = logging.getLogger("hypercorn.access")
        
        logger.info(f"Starting Hypercorn dual protocol server on: {', '.join(bind_addresses)}")
        logger.info(f"Workers: {config.workers}, HTTP/2: {config.http}")
        
        # Run the server
        import asyncio
        asyncio.run(serve(asgi_app, config))
        
    except Exception as e:
        logger.error(f"Error in Hypercorn dual server setup: {e}")
        return False

if __name__ == "__main__":
    logger.info("Starting ValidoAI application...")
    
    # Check if running in production mode
    if os.getenv('FLASK_ENV') == 'production':
        run_asgi_server()
    else:
        # Development mode with Hypercorn dual protocol server
        # Default to HTTPS enabled
        if all_configs['server'].get('use_https', True):
            # Run Hypercorn with dual HTTP/HTTPS support
            run_hypercorn_dual_server()
        else:
            # Run only HTTP server with Hypercorn
            run_hypercorn_dual_server()

