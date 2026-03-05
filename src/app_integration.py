"""
App Integration Module
Integrates all components of the ValidoAI application
"""

import logging
from flask import Flask, session, g, request, render_template

# Setup logging
logger = logging.getLogger(__name__)

class AppIntegration:
    """Class to integrate all components of the ValidoAI application"""
    
    @staticmethod
    def create_app(config=None):
        """
        Create and configure Flask application
        
        Args:
            config: Configuration object or dictionary
            
        Returns:
            Flask: Configured Flask application
        """
        app = Flask(__name__, template_folder='../templates', static_folder='../static')
        
        # Load configuration
        AppIntegration.configure_app(app, config)
        
        # Register extensions
        AppIntegration.register_extensions(app)
        
        # Register blueprints
        AppIntegration.register_blueprints(app)
        
        # Register error handlers
        AppIntegration.register_error_handlers(app)
        
        # Register context processors
        AppIntegration.register_context_processors(app)
        
        # Register before/after request handlers
        AppIntegration.register_request_handlers(app)
        
        return app
    
    @staticmethod
    def configure_app(app, config=None):
        """
        Configure Flask application
        
        Args:
            app: Flask application
            config: Configuration object or dictionary
        """
        try:
            # Load environment variables
            from src.core_config.env_loader import env_loader
            env_loader.configure_flask_app(app)
            
            # Load configuration
            if config:
                if isinstance(config, dict):
                    app.config.update(config)
                else:
                    app.config.from_object(config)
            
            # Set default SQLAlchemy configuration if not already set
            if not app.config.get('SQLALCHEMY_DATABASE_URI'):
                import os
                db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'sqlite', 'app.db')
                app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
            
            if not app.config.get('SQLALCHEMY_TRACK_MODIFICATIONS'):
                app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
            
            # Configure logging
            if not app.debug:
                import logging
                from logging.handlers import RotatingFileHandler
                import os
                
                if not os.path.exists('logs'):
                    os.mkdir('logs')
                
                file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
                file_handler.setFormatter(logging.Formatter(
                    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
                ))
                file_handler.setLevel(logging.INFO)
                app.logger.addHandler(file_handler)
                app.logger.setLevel(logging.INFO)
                app.logger.info('ValidoAI startup')
            
            logger.info("Flask app configured successfully")
            
        except Exception as e:
            logger.error(f"Error configuring Flask app: {e}")
    
    @staticmethod
    def register_extensions(app):
        """
        Register Flask extensions
        
        Args:
            app: Flask application
        """
        try:
            # Import extensions
            from src.extensions import db, migrate, cache, babel, csrf, login_manager
            from src.functions import mail
            
            # Initialize extensions
            db.init_app(app)
            migrate.init_app(app, db)
            cache.init_app(app)
            mail.init_app(app)
            babel.init_app(app)
            csrf.init_app(app)
            login_manager.init_app(app)
            
            # Set up user loader for Flask-Login
            @login_manager.user_loader
            def load_user(user_id):
                from src.models.database_models import User
                return User.query.get(int(user_id))
            
            # Initialize debug bar if in debug mode
            if app.debug:
                try:
                    from src.debug_bar import init_debug_bar
                    init_debug_bar(app)
                    logger.info("Debug bar initialized")
                except ImportError:
                    logger.warning("Debug bar not available")
            
            logger.info("Flask extensions registered successfully")
            
        except Exception as e:
            logger.error(f"Error registering Flask extensions: {e}")
    
    @staticmethod
    def register_blueprints(app):
        """
        Register Flask blueprints
        
        Args:
            app: Flask application
        """
        try:
            # Import blueprints
            from src.routes import register_blueprints
            from src.crud_routes import register_crud_routes
            from src.auth.routes import auth_bp
            from src.ecommerce.routes import ecommerce_bp
            from src.scraping.routes import scraping_bp
            
            # Register blueprints
            register_blueprints(app)
            register_crud_routes(app)
            app.register_blueprint(auth_bp)
            app.register_blueprint(ecommerce_bp)
            app.register_blueprint(scraping_bp)
            
            logger.info("Flask blueprints registered successfully")
            
        except Exception as e:
            logger.error(f"Error registering Flask blueprints: {e}")
    
    @staticmethod
    def register_error_handlers(app):
        """
        Register error handlers
        
        Args:
            app: Flask application
        """
        try:
            @app.errorhandler(404)
            def page_not_found(e):
                return render_template('errors/show.html', error=e, code=404, title="Page Not Found"), 404
            
            @app.errorhandler(500)
            def internal_server_error(e):
                return render_template('errors/show.html', error=e, code=500, title="Internal Server Error"), 500
            
            @app.errorhandler(403)
            def forbidden(e):
                return render_template('errors/show.html', error=e, code=403, title="Forbidden"), 403
            
            @app.errorhandler(400)
            def bad_request(e):
                return render_template('errors/show.html', error=e, code=400, title="Bad Request"), 400
            
            logger.info("Error handlers registered successfully")
            
        except Exception as e:
            logger.error(f"Error registering error handlers: {e}")
    
    @staticmethod
    def register_context_processors(app):
        """
        Register context processors
        
        Args:
            app: Flask application
        """
        try:
            @app.context_processor
            def inject_global_vars():
                """Inject global variables into templates"""
                from flask_login import current_user
                from src.utils.menu_generator import main_menu_sidebar, main_menu
                return {
                    'app_name': 'ValidoAI',
                    'app_version': '1.0.0',
                    'current_year': '2024',
                    'current_user': current_user,
                    'selected_ai_model': session.get('selected_ai_model', app.config.get('DEFAULT_AI_MODEL', 'gpt-3.5-turbo')),
                    'language': session.get('language', app.config.get('LANGUAGE', 'sr')),
                    'main_menu_sidebar': main_menu_sidebar,
                    'main_menu': main_menu
                }
            
            logger.info("Context processors registered successfully")
            
        except Exception as e:
            logger.error(f"Error registering context processors: {e}")
    
    @staticmethod
    def register_request_handlers(app):
        """
        Register before/after request handlers
        
        Args:
            app: Flask application
        """
        try:
            @app.before_request
            def before_request():
                """Before request handler"""
                # Set default AI model if not in session
                if 'selected_ai_model' not in session:
                    session['selected_ai_model'] = app.config.get('DEFAULT_AI_MODEL', 'gpt-3.5-turbo')
                
                # Set default language if not in session
                if 'language' not in session:
                    session['language'] = app.config.get('LANGUAGE', 'sr')
                
                # Make models integration available to all routes
                from src.models_integration import models
                g.models = models
            
            logger.info("Request handlers registered successfully")
            
        except Exception as e:
            logger.error(f"Error registering request handlers: {e}")

# Function to create and configure Flask application
def create_app(config=None):
    """
    Create and configure Flask application
    
    Args:
        config: Configuration object or dictionary
        
    Returns:
        Flask: Configured Flask application
    """
    return AppIntegration.create_app(config)
