"""
Auto-Loading Controller System for ValidoAI
Automatically discovers and registers all controllers with their routes
"""

import os
import importlib
import inspect
from typing import Dict, Any, List, Optional, Callable
from flask import Flask, Blueprint
from functools import wraps
import logging

logger = logging.getLogger(__name__)

class ControllerLoader:
    """Auto-loading controller system"""
    
    def __init__(self, app: Flask):
        self.app = app
        self.controllers: Dict[str, Any] = {}
        self.blueprints: Dict[str, Blueprint] = {}
        self.routes_registered = False
        
    def discover_controllers(self, controllers_dir: str = "src/controllers") -> List[str]:
        """
        Discover all controller files in the controllers directory
        
        Args:
            controllers_dir: Path to controllers directory
            
        Returns:
            List of controller module names
        """
        controller_files = []
        
        try:
            if os.path.exists(controllers_dir):
                for filename in os.listdir(controllers_dir):
                    if filename.endswith('.py') and not filename.startswith('__'):
                        module_name = filename[:-3]  # Remove .py extension
                        controller_files.append(module_name)
                        
        except Exception as e:
            logger.error(f"Error discovering controllers: {e}")
            
        return controller_files
    
    def load_controller(self, module_name: str) -> Optional[Any]:
        """
        Load a controller module
        
        Args:
            module_name: Name of the controller module
            
        Returns:
            Controller module or None if loading fails
        """
        try:
            module_path = f"src.controllers.{module_name}"
            module = importlib.import_module(module_path)
            
            # Find controller classes in the module
            controller_classes = []
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    hasattr(obj, '__module__') and 
                    obj.__module__.startswith('src.controllers')):
                    controller_classes.append(obj)
            
            return module, controller_classes
            
        except Exception as e:
            logger.error(f"Error loading controller {module_name}: {e}")
            return None
    
    def create_blueprint(self, controller_name: str) -> Blueprint:
        """
        Create a blueprint for a controller
        
        Args:
            controller_name: Name of the controller
            
        Returns:
            Flask Blueprint
        """
        return Blueprint(
            f"{controller_name}_bp",
            __name__,
            url_prefix=f"/{controller_name.replace('_', '-')}"
        )
    
    def register_controller_routes(self, blueprint: Blueprint, controller_instance: Any):
        """
        Register routes for a controller instance
        
        Args:
            blueprint: Flask Blueprint
            controller_instance: Controller instance
        """
        # Get all methods from the controller
        methods = inspect.getmembers(controller_instance, inspect.ismethod)
        
        for method_name, method in methods:
            # Skip private methods and special methods
            if method_name.startswith('_'):
                continue
                
            # Check if method has route decorator
            if hasattr(method, '_route_info'):
                route_info = method._route_info
                self._register_route(blueprint, method, route_info)
    
    def _register_route(self, blueprint: Blueprint, method: Callable, route_info: Dict[str, Any]):
        """
        Register a single route
        
        Args:
            blueprint: Flask Blueprint
            method: Controller method
            route_info: Route information
        """
        route_path = route_info.get('path', '')
        methods = route_info.get('methods', ['GET'])
        
        # Create route function
        @blueprint.route(route_path, methods=methods)
        @wraps(method)
        def route_handler(*args, **kwargs):
            try:
                return method(*args, **kwargs)
            except Exception as e:
                # Use error logger if available
                from src.utils.error_logger import error_logger
                error_uuid = error_logger.log_error(e, {
                    'controller': method.__self__.__class__.__name__,
                    'method': method.__name__,
                    'route': route_path
                })
                
                # Return error response
                from src.utils.exception_handler import create_error_response
                return create_error_response(e)
        
        # Store route information
        route_handler._route_info = route_info
        route_handler._controller_method = method
    
    def auto_register_routes(self):
        """Automatically register all controller routes"""
        if self.routes_registered:
            return
            
        # Discover and load all controllers
        controller_files = self.discover_controllers()
        
        for controller_name in controller_files:
            result = self.load_controller(controller_name)
            if result:
                module, controller_classes = result
                
                for controller_class in controller_classes:
                    # Create controller instance
                    controller_instance = controller_class()
                    
                    # Create blueprint
                    blueprint_name = f"{controller_name}_bp"
                    blueprint = self.create_blueprint(controller_name)
                    
                    # Register routes
                    self.register_controller_routes(blueprint, controller_instance)
                    
                    # Register blueprint with app
                    self.app.register_blueprint(blueprint)
                    
                    # Store controller and blueprint
                    self.controllers[controller_name] = controller_instance
                    self.blueprints[blueprint_name] = blueprint
                    
                    logger.info(f"Registered controller: {controller_name}")
        
        self.routes_registered = True
        logger.info(f"Auto-registered {len(self.controllers)} controllers")

def route(path: str = '', methods: List[str] = None):
    """
    Decorator to mark controller methods as routes
    
    Args:
        path: Route path
        methods: HTTP methods
    """
    def decorator(func):
        func._route_info = {
            'path': path,
            'methods': methods or ['GET']
        }
        return func
    return decorator

def api_route(path: str = '', methods: List[str] = None, version: str = 'v1'):
    """
    Decorator to mark controller methods as API routes
    
    Args:
        path: Route path
        methods: HTTP methods
        version: API version
    """
    def decorator(func):
        api_path = f"/api/{version}{path}"
        func._route_info = {
            'path': api_path,
            'methods': methods or ['GET'],
            'api_version': version
        }
        return func
    return decorator

def get_route(path: str = ''):
    """Decorator for GET routes"""
    return route(path, ['GET'])

def post_route(path: str = ''):
    """Decorator for POST routes"""
    return route(path, ['POST'])

def put_route(path: str = ''):
    """Decorator for PUT routes"""
    return route(path, ['PUT'])

def delete_route(path: str = ''):
    """Decorator for DELETE routes"""
    return route(path, ['DELETE'])

def api_get(path: str = '', version: str = 'v1'):
    """Decorator for API GET routes"""
    return api_route(path, ['GET'], version)

def api_post(path: str = '', version: str = 'v1'):
    """Decorator for API POST routes"""
    return api_route(path, ['POST'], version)

def api_put(path: str = '', version: str = 'v1'):
    """Decorator for API PUT routes"""
    return api_route(path, ['PUT'], version)

def api_delete(path: str = '', version: str = 'v1'):
    """Decorator for API DELETE routes"""
    return api_route(path, ['DELETE'], version)

# Global controller loader instance
controller_loader = None

def init_controller_loader(app: Flask):
    """Initialize the global controller loader"""
    global controller_loader
    controller_loader = ControllerLoader(app)
    return controller_loader

def get_controller_loader() -> ControllerLoader:
    """Get the global controller loader instance"""
    return controller_loader
