"""
API Integration Module for ValidoAI
This module shows how to integrate the API endpoints with the main Flask application
"""

def integrate_api_endpoints(app):
    """
    Integrate API endpoints with the main Flask application
    
    Args:
        app: Flask application instance
    """
    # Import the register_api_endpoints function
    from src.api_endpoints import register_api_endpoints
    
    # Register API endpoints
    register_api_endpoints(app)
    
    # Log successful integration
    app.logger.info("API endpoints integrated successfully")

def integrate_with_existing_routes(app):
    """
    Alternative integration method that preserves existing routes
    
    Args:
        app: Flask application instance
    """
    # Import blueprints from api_endpoints
    from src.api_endpoints import api_bp, cache, limiter
    
    # Register blueprint with app
    app.register_blueprint(api_bp)
    
    # Initialize extensions if not already initialized
    if not hasattr(app, 'extensions') or 'cache' not in app.extensions:
        cache.init_app(app)
    
    if not hasattr(app, 'extensions') or 'limiter' not in app.extensions:
        limiter.init_app(app)
    
    # Log successful integration
    app.logger.info("API endpoints integrated with existing routes successfully")
