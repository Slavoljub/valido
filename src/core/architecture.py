"""
Core Architecture Module
Implements OOP, MVC, and ELM architecture patterns
"""

import os
import importlib.util
from typing import Optional, Dict, Any
from dataclasses import dataclass
from flask import Flask

from .logging import LoggerFactory

logger = LoggerFactory.create_logger(__name__)

@dataclass
class ApplicationConfig:
    """Application configuration data class"""
    secret_key: str
    debug: bool
    host: str
    http_port: int
    https_port: int
    use_https: bool
    enable_dual_server: bool
    cert_file: str
    key_file: str
    default_theme: str = 'auto'
    enable_theme_switcher: bool = True
    full_screen_mode: bool = True
    sidebar_collapsible: bool = True

class ApplicationFactory:
    """Factory class for creating Flask applications"""
    
    def __init__(self):
        self.logger = LoggerFactory.create_logger(__name__)
    
    def create_application(self, config: ApplicationConfig) -> Flask:
        """Create and configure Flask application"""
        try:
            # Get the root directory (where templates are located)
            root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            
            # Create Flask app with correct template folder
            app = Flask(__name__, 
                       template_folder=os.path.join(root_dir, 'templates'),
                       static_folder=os.path.join(root_dir, 'static'))
            
            # Basic configuration
            app.config['SECRET_KEY'] = config.secret_key
            app.config['DEBUG'] = config.debug
            
            # Store config in app
            app.config_obj = config
            
            # Register routes using centralized routes.py
            self._register_routes(app)
            
            self.logger.info("Application created successfully")
            return app
            
        except Exception as e:
            self.logger.error(f"Failed to create application: {e}")
            raise
    
    def _register_routes(self, app: Flask):
        """Register all routes using centralized routes.py"""
        try:
            # Prefer root-level routes.py via explicit file load
            root_routes_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'routes.py')
            if os.path.exists(root_routes_path):
                spec = importlib.util.spec_from_file_location('root_routes', root_routes_path)
                root_routes = importlib.util.module_from_spec(spec)
                assert spec and spec.loader
                spec.loader.exec_module(root_routes)
                root_routes.register_all_routes(app)
                self.logger.info("Routes registered from root routes.py")
            else:
                # Fallback to src.routes
                from ..routes import register_all_routes
                register_all_routes(app)
                self.logger.info("Routes registered from src.routes")
        except Exception as e:
            self.logger.warning(f"Could not register routes: {e}")
            # Ultimate fallback
            try:
                from ..routes import register_all_routes
                register_all_routes(app)
                self.logger.info("Routes registered from fallback")
            except Exception as fallback_error:
                self.logger.error(f"Failed to register routes: {fallback_error}")
                raise
