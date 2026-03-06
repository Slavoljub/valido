"""
ValidoAI - Simplified Routes (Development Mode)
==============================================
Only / and /settings routes active for testing
All other routes commented out for now
"""

import logging
import uuid
from datetime import datetime, timezone
from flask import Blueprint, render_template, jsonify, request, redirect, url_for, flash, abort, send_from_directory, current_app
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from pathlib import Path

# Import the centralized config manager
from src.config import config_manager
from src.database import database_manager

# Import DRY error handling utilities
from src.core.error_handling import handle_controller_import_error

logger = logging.getLogger(__name__)

# ============================================================================
# BLUEPRINTS (Simplified)
# ============================================================================

main_bp = Blueprint('main', __name__)
api_bp = Blueprint('api', __name__)    # UNCOMMENTED FOR SETTINGS API
# auth_bp = Blueprint('auth', __name__)  # COMMENTED OUT
# admin_bp = Blueprint('admin', __name__) # COMMENTED OUT

# Docs blueprint serving static MkDocs site
# docs_bp = Blueprint("docs", __name__, url_prefix="/docs")  # COMMENTED OUT

# @docs_bp.route("/", defaults={"path": "index.html"})
# @docs_bp.route("/<path:path>")
# def serve_docs(path):
#     docs_root = Path(current_app.root_path) / "static" / "docs_site"
#     return send_from_directory(docs_root, path)

# ============================================================================
# MAIN ROUTES
# ============================================================================

# Home route - simplified without complex dependencies
# from src.controllers.home_controller import HomeController  # COMMENTED OUT
# from src.controllers.example_controller import ExampleController  # COMMENTED OUT

# Factory mapping helper dictionary (simplified)
# _controller_actions = {
#     'home_index': HomeController.index,
#     # 'example_show': ExampleController.show,  # COMMENTED OUT
# }


# Generic dispatcher to keep registrations DRY
# def _dispatch(action_key, **kwargs):
#     func = _controller_actions.get(action_key)
#     if not func:
#         abort(500)
#     return func(**kwargs)


@main_bp.route('/')
def home_index():
    """Simple home route that works without complex dependencies"""
    return render_template('home/index.html',
                         pages=[],
                         dashboard_data={
                             'notifications': [],
                             'recent_activities': [],
                             'stats': {
                                 'total_users': 0,
                                 'total_projects': 0,
                                 'total_sales': 0,
                                 'total_revenue': 0
                             }
                         })

@main_bp.route('/dashboard')
def dashboard_index():
    """Dashboard route"""
    return render_template('dashboard/index.html',
                         pages=[],
                         dashboard_data={
                             'notifications': [],
                             'recent_activities': [],
                             'stats': {
                                 'total_users': 0,
                                 'total_projects': 0,
                                 'total_sales': 0,
                                 'total_revenue': 0
                             }
                         })

@main_bp.route('/chat')
def chat_index():
    """Chat route"""
    return render_template('chat/index.html',
                         pages=[],
                         dashboard_data={
                             'notifications': [],
                             'recent_activities': [],
                             'stats': {
                                 'total_users': 0,
                                 'total_projects': 0,
                                 'total_sales': 0,
                                 'total_revenue': 0
                             }
                         })

@main_bp.route('/settings')
def settings_index():
    """Settings route"""
    return render_template('settings/index.html',
                         pages=[],
                         dashboard_data={
                             'notifications': [],
                             'recent_activities': [],
                             'stats': {
                                 'total_users': 0,
                                 'total_projects': 0,
                                 'total_sales': 0,
                                 'total_revenue': 0
                             }
                         })

@main_bp.route('/test')
def test_route():
    """Simple test route to verify Flask is working"""
    return jsonify({
        "status": "success",
        "message": "Flask application is working!",
        "timestamp": datetime.now(timezone.utc).isoformat()
    })

@main_bp.route('/test-suite')
def test_suite():
    """Comprehensive test suite interface with categories and real-time execution"""
    try:
        # Simple test suite that works without complex dependencies
        test_categories = {
            'unit': {'description': 'Unit tests for individual components', 'path': 'tests/unit', 'priority': 1},
            'integration': {'description': 'Integration tests for system interactions', 'path': 'tests/integration', 'priority': 2},
            'e2e': {'description': 'End-to-end user workflow tests', 'path': 'tests/e2e', 'priority': 3},
            'performance': {'description': 'Performance and load testing', 'path': 'tests/performance', 'priority': 4},
            'security': {'description': 'Security and vulnerability testing', 'path': 'tests/security', 'priority': 5},
            'functional': {'description': 'Functional feature testing', 'path': 'tests/functional', 'priority': 6},
            'routes': {'description': 'Route and API endpoint testing', 'path': 'tests/routes', 'priority': 7},
            'database': {'description': 'Database and data layer testing', 'path': 'tests/database', 'priority': 8},
            'ai_ml': {'description': 'AI and machine learning testing', 'path': 'tests/ai_ml', 'priority': 9},
            'imports': {'description': 'Import and dependency testing', 'path': 'tests/imports', 'priority': 10}
        }
        
        return render_template('test_suite/index.html',
                             categories=test_categories,
                             recent_results=[],
                             test_categories=test_categories)
    except Exception as e:
        logger.error(f"Error rendering test suite: {e}")
        return render_template('errors/error.html',
                             error_code=500,
                             error_title="Test Suite Error",
                             error_message="Failed to load test suite interface.",
                             stack_trace=str(e),
                             timestamp=datetime.now().isoformat(),
                             error_uuid=f"e500_{uuid.uuid4().hex[:8]}",
                             request_id=str(uuid.uuid4())), 500

@main_bp.route('/api/test-suite/run', methods=['POST'])
def run_test_suite():
    """API endpoint to run tests with specific categories"""
    try:
        from src.controllers.test_suite_controller import TestSuiteController
        controller = TestSuiteController()
        return controller.run_tests()
    except ImportError as e:
        return handle_controller_import_error(
            controller_name="TestSuiteController",
            error=e,
            error_title="Test Suite Unavailable",
            error_message_prefix="Test suite controller not available",
            is_api_route=True,
            custom_logger=logger
        )

@main_bp.route('/api/test-suite/status')
def test_suite_status():
    """Get test suite status and available categories"""
    try:
        from src.controllers.test_suite_controller import TestSuiteController
        controller = TestSuiteController()
        return controller.get_status()
    except ImportError as e:
        return handle_controller_import_error(
            controller_name="TestSuiteController",
            error=e,
            error_title="Test Suite Unavailable",
            error_message_prefix="Test suite controller not available",
            is_api_route=True,
            custom_logger=logger
        )

# Performance monitoring routes
@main_bp.route('/performance')
def performance():
    """Performance monitoring dashboard"""
    try:
        from src.controllers.performance_controller import PerformanceController
        controller = PerformanceController()
        return controller.show()
    except ImportError as e:
        return handle_controller_import_error(
            controller_name="PerformanceController",
            error=e,
            error_title="Performance Monitoring Unavailable",
            error_message_prefix="The performance monitoring controller is not available.",
            is_api_route=False,
            custom_logger=logger
        )

@main_bp.route('/api/performance/start', methods=['POST'])
def start_performance_monitoring():
    """Start performance monitoring"""
    try:
        from src.controllers.performance_controller import PerformanceController
        controller = PerformanceController()
        return controller.start_monitoring()
    except ImportError as e:
        return handle_controller_import_error(
            controller_name="PerformanceController",
            error=e,
            error_title="Performance Monitoring Unavailable",
            error_message_prefix="Performance monitoring not available",
            is_api_route=True,
            custom_logger=logger
        )

@main_bp.route('/api/performance/stop', methods=['POST'])
def stop_performance_monitoring():
    """Stop performance monitoring"""
    try:
        from src.controllers.performance_controller import PerformanceController
        controller = PerformanceController()
        return controller.stop_monitoring()
    except ImportError as e:
        return handle_controller_import_error(
            controller_name="PerformanceController",
            error=e,
            error_title="Performance Monitoring Unavailable",
            error_message_prefix="Performance monitoring not available",
            is_api_route=True,
            custom_logger=logger
        )

@main_bp.route('/api/performance/system-info')
def get_system_info():
    """Get system information"""
    try:
        from src.controllers.performance_controller import PerformanceController
        return PerformanceController.get_system_info()
    except ImportError as e:
        return handle_controller_import_error(
            controller_name="PerformanceController",
            error=e,
            error_title="Performance Monitoring Unavailable",
            error_message_prefix="Performance monitoring not available",
            is_api_route=True,
            custom_logger=logger
        )

@main_bp.route('/api/performance/processes')
def get_process_list():
    """Get list of running processes"""
    try:
        from src.controllers.performance_controller import PerformanceController
        return PerformanceController.get_process_list()
    except ImportError as e:
        return handle_controller_import_error(
            controller_name="PerformanceController",
            error=e,
            error_title="Performance Monitoring Unavailable",
            error_message_prefix="Performance monitoring not available",
            is_api_route=True,
            custom_logger=logger
        )

@main_bp.route('/api/performance/optimize', methods=['POST'])
def optimize_performance():
    """Perform performance optimization"""
    try:
        from src.controllers.performance_controller import PerformanceController
        return PerformanceController.optimize_performance()
    except ImportError as e:
        return handle_controller_import_error(
            controller_name="PerformanceController",
            error=e,
            error_title="Performance Monitoring Unavailable",
            error_message_prefix="Performance monitoring not available",
            is_api_route=True,
            custom_logger=logger
        )

@main_bp.route('/api/performance/report')
def get_performance_report():
    """Get comprehensive performance report"""
    try:
        from src.controllers.performance_controller import PerformanceController
        return PerformanceController.get_performance_report()
    except ImportError as e:
        return handle_controller_import_error(
            controller_name="PerformanceController",
            error=e,
            error_title="Performance Monitoring Unavailable",
            error_message_prefix="Performance monitoring not available",
            is_api_route=True,
            custom_logger=logger
        )

@main_bp.route('/healthz')
@main_bp.route('/readyz')
def health_checks():
    """Kubernetes-style liveness / readiness probe (no heavy deps)"""
    return jsonify({
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }), 200

# @main_bp.route('/dashboard')  # COMMENTED OUT
# def dashboard():
#     """Main dashboard page"""
#     return render_template('dashboard/index.html',
#                          current_user={'id': 'demo_user', 'name': 'Demo User'})

# ============================================================================
# SCRAPING ROUTES (Placeholder implementations) - COMMENTED OUT
# ============================================================================

# @main_bp.route('/scraping')  # COMMENTED OUT
# def scraping_index():
#     """Scraping dashboard placeholder"""
#     return render_template('scraping/index.html')

# @main_bp.route('/scraping/config')  # COMMENTED OUT
# def scraping_config():
#     """Scraping configuration placeholder"""
#     return render_template('scraping/config.html')

# @main_bp.route('/scraping/test-url', methods=['POST'])  # COMMENTED OUT
# def scraping_test_url():
#     """Test URL scraping placeholder"""
#     data = request.json or {}
#     url = data.get('url', 'https://example.com')
#     # For now, just echo back the URL
#     return jsonify({'status': 'success', 'url': url, 'message': 'Scraping simulation complete'})

# ============================================================================
# SAMPLE API ROUTES FOR DASHBOARD DATA - COMMENTED OUT
# ============================================================================

# @api_bp.route('/dashboard/data')  # COMMENTED OUT
# def api_dashboard_data():
#     """Sample dashboard data API"""
#     sample = {
#         'metrics': {
#             'sales': 12345,
#             'users': 678,
#             'growth': 12.3
#         },
#         'timestamp': datetime.now(timezone.utc).isoformat()
#     }
#     return jsonify(sample)

# @api_bp.route('/predictive/data')  # COMMENTED OUT
# def api_predictive_data():
#     """Sample predictive analytics data API"""
#     sample = {
#         'forecast': {
#             'next_month_sales': 15000,
#             'confidence': 0.85
#         },
#         'timestamp': datetime.now(timezone.utc).isoformat()
#     }
#     return jsonify(sample)

# @main_bp.route('/dashboard/business-intelligence')  # COMMENTED OUT
# def business_intelligence_dashboard():
#     """Business Intelligence Dashboard"""
#     try:
#         # Try to import predictive engine if available
#         try:
#             from src.analytics.predictive import start_predictive_engine
#             start_predictive_engine()
#         except ImportError:
#             logger.info("Predictive engine not available, proceeding without it")
#
#         return render_template('dashboard/business_intelligence.html',
#                              current_user={'id': 'demo_user', 'name': 'Demo User'})
#     except Exception as e:
#         logger.error(f"Error loading BI dashboard: {e}")
#         return render_template('dashboard/business_intelligence.html',
#                              current_user={'id': 'demo_user', 'name': 'Demo User'},
#                              error=str(e))

# @main_bp.route('/dashboard/predictive-analytics')  # COMMENTED OUT
# def predictive_analytics_dashboard():
#     """Predictive Analytics Dashboard with AI forecasting"""
#     try:
#         # Try to import predictive engine if available
#         try:
#             from src.analytics.predictive import start_predictive_engine
#             start_predictive_engine()
#         except ImportError:
#             logger.info("Predictive engine not available, proceeding without it")
#
#         return render_template('dashboard/predictive_analytics.html',
#                              current_user={'id': 'demo_user', 'name': 'Demo User'})
#     except Exception as e:
#         logger.error(f"Error loading predictive dashboard: {e}")
#         return render_template('dashboard/predictive_analytics.html',
#                              current_user={'id': 'demo_user', 'name': 'Demo User'},
#                              error=str(e))

# ============================================================================
# CONTENT MANAGEMENT ROUTES - COMMENTED OUT
# ============================================================================

# @main_bp.route('/content/management')  # COMMENTED OUT
# def content_management():
#     """Content Management System"""
#     try:
#         # Try to import content manager if available
#         try:
#             from src.content_manager import content_manager
#         except ImportError:
#             logger.info("Content manager not available, proceeding without it")
#
#         return render_template('content/management.html',
#                              current_user={'id': 'demo_user', 'name': 'Demo User'})
#     except Exception as e:
#         logger.error(f"Error loading content management: {e}")
#         return render_template('content/management.html',
#                              current_user={'id': 'demo_user', 'name': 'Demo User'},
#                              error=str(e))

# ============================================================================
# AI ANALYSIS ROUTES - COMMENTED OUT
# ============================================================================

# @main_bp.route('/ai/sentiment-analysis')  # COMMENTED OUT
# def sentiment_analysis():
#     """Sentiment Analysis Dashboard"""
#     try:
#         # Try to import sentiment analyzer if available
#         try:
#             from src.ai.sentiment import sentiment_analyzer
#         except ImportError:
#             logger.info("Sentiment analyzer not available, proceeding without it")
#
#         return render_template('ai/sentiment_analysis.html',
#                              current_user={'id': 'demo_user', 'name': 'Demo User'})
#     except Exception as e:
#         logger.error(f"Error loading sentiment analysis: {e}")
#         return render_template('ai/sentiment_analysis.html',
#                              current_user={'id': 'demo_user', 'name': 'Demo User'},
#                              error=str(e))

# ============================================================================
# SETTINGS ROUTES
# ============================================================================

# @main_bp.route('/settings')
# def settings():
#     """Centralized settings page to manage all configurations."""
#     try:
#         # Fetch all configurations from the unified manager
#         all_configs = config_manager.get_all_configurations()

#         # Get database connection status from the database manager if available
#         db_status = {}
#         try:
#             from src.database import database_manager
#             # Check if the method exists before calling it
#             if hasattr(database_manager, 'get_status'):
#                 db_status = database_manager.get_status()
#             else:
#                 # Fallback: create basic status
#                 db_status = {
#                     'postgresql': {'status': 'unknown', 'message': 'Status not available'},
#                     'mysql': {'status': 'unknown', 'message': 'Status not available'},
#                     'mongodb': {'status': 'unknown', 'message': 'Status not available'},
#                     'redis': {'status': 'unknown', 'message': 'Status not available'}
#                 }
#         except ImportError:
#             logger.warning("Database manager not available for status check.")

#         # Prepare context for the template
#         context = {
#             'all_configs': all_configs,
#             'db_status': db_status,
#             'active_tab': request.args.get('tab', 'database')  # Default to database tab
#         }
#         return render_template('settings/index.html', **context)
#     except Exception as e:
#         logger.error(f"Error loading settings page: {e}", exc_info=True)
#         abort(500)

# ============================================================================
# API ROUTES
# ============================================================================

# @api_bp.route('/settings/database/test', methods=['POST'])
# def test_database_connection():
#     """API endpoint to test a database connection."""
#     data = request.json
#     db_type = data.get('db_type')

#     if not db_type:
#         return jsonify({'status': 'error', 'message': 'Database type not specified.'}), 400

#     try:
#         result = database_manager.test_database_connection(db_type)
#         if result.get('status') == 'success':
#             return jsonify({
#                 'status': 'success',
#                 'message': f'{db_type.title()} connection test successful: {result.get("message")}'
#             })
#         else:
#             return jsonify({
#                 'status': 'error',
#                 'message': f'{db_type.title()} connection test failed: {result.get("message")}'
#             }), 500
#     except Exception as e:
#         logger.error(f"Error testing {db_type} connection: {e}", exc_info=True)
#         return jsonify({'status': 'error', 'message': str(e)}), 500

# ============================================================================
# AUTHENTICATION ROUTES - COMMENTED OUT
# ============================================================================

# @auth_bp.route('/login', methods=['GET', 'POST'])  # COMMENTED OUT
# def login():
#     """User login"""
#     if request.method == 'POST':
#         # Handle login logic here
#         pass
#     return render_template('auth/login.html')

# @auth_bp.route('/register', methods=['GET', 'POST'])  # COMMENTED OUT
# def register():
#     """User registration"""
#     if request.method == 'POST':
#         # Handle registration logic here
#         pass
#     return render_template('auth/register.html')

# @auth_bp.route('/logout')  # COMMENTED OUT
# @login_required
# def logout():
#     """User logout"""
#     # Handle logout logic here
#     return redirect(url_for('main.index'))

# ============================================================================
# AUTH ALIAS ROUTES FOR TEST COMPATIBILITY - COMMENTED OUT
# ============================================================================

# Alias routes to maintain backward compatibility with older tests expecting top-level auth paths

# @main_bp.route('/login')  # COMMENTED OUT
# def login_redirect():
#     """Redirect /login to updated /auth/login"""
#     return redirect(url_for('auth.login'))

# @main_bp.route('/register')  # COMMENTED OUT
# def register_redirect():
#     """Redirect /register to updated /auth/register"""
#     return redirect(url_for('auth.register'))

# @main_bp.route('/logout')  # COMMENTED OUT
# def logout_redirect():
#     """Redirect /logout to updated /auth.logout"""
#     return redirect(url_for('auth.logout'))

# ============================================================================
# API ROUTES - COMMENTED OUT
# ============================================================================

# @api_bp.route('/api/health')  # COMMENTED OUT
# def api_health():
#     """API health check"""
#     return jsonify({
#         "status": "healthy",
#         "timestamp": datetime.now(timezone.utc).isoformat(),
#         "version": "1.0.0"
#     })

# @api_bp.route('/api/status')  # COMMENTED OUT
# def api_status():
#     """API status endpoint"""
#     return jsonify({
#         "status": "running",
#         "services": {
#             "database": "connected",
#             "ai": "available",
#             "cache": "connected"
#         }
#     })

# ============================================================================
# ADMIN ROUTES - COMMENTED OUT
# ============================================================================

# @admin_bp.route('/admin')  # COMMENTED OUT
# @login_required
# def admin_dashboard():
#     """Admin dashboard"""
#     return render_template('admin/dashboard.html')

# @admin_bp.route('/admin/users')  # COMMENTED OUT
# @login_required
# def admin_users():
#     """User management"""
#     return render_template('admin/users.html')

# ============================================================================
# MISSING ROUTES - ADDING PLACEHOLDER ROUTES FOR TEMPLATES - COMMENTED OUT
# ============================================================================

# @main_bp.route('/profile')  # COMMENTED OUT
# @login_required
# def profile_index():
#     """User profile page"""
#     return render_template('profile/index.html')

# @main_bp.route('/chat')  # COMMENTED OUT
# def chat_chat_local():
#     """AI Chat page"""
#     return render_template('chat/chat_local.html')

# @main_bp.route('/ticketing')  # COMMENTED OUT
# def ticketing_index():
#     """Ticketing system"""
#     return render_template('ticketing/index.html')

# @main_bp.route('/companies')  # COMMENTED OUT
# def companies_index():
#     """Companies management"""
#     return render_template('companies/index.html')

# ============================================================================
# BLUEPRINT REGISTRATION (Simplified)
# ============================================================================

@api_bp.route('/kpr/analyze', methods=['POST'])
def kpr_analyze():
    """KPR GPT analysis endpoint"""
    try:
        from scripts.kpr_gpt_analysis import pozovi_kpr_gpt_analizu

        data = request.get_json(silent=True) or {}
        mod = data.get("mod", "kombinovano")
        pitanje = data.get("pitanje", "")

        if mod not in {"dobavljac", "mesec", "kombinovano"}:
            return jsonify({
                "success": False,
                "error": "Invalid 'mod'. Use: dobavljac | mesec | kombinovano"
            }), 400

        rezultat = pozovi_kpr_gpt_analizu(mod=mod, pitanje=pitanje)

        return jsonify({
            "success": True,
            "data": rezultat
        }), 200

    except Exception as e:
        logger.error(f"Error in /api/kpr/analyze: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
##########################################################################################################################################################

##########################################################################################################################################################
# Chat API Routes
@api_bp.route('/chat/models', methods=['GET'])
def get_available_models():
    """Get available AI models"""
    try:
        # Import AI models controller
        from src.controllers.ai_models_controller import AIModelsController
        controller = AIModelsController()
        models = controller.get_available_models()
        return jsonify({
            'success': True,
            'models': models
        })
    except ImportError as e:
        return handle_controller_import_error(
            'AIModelsController',
            e,
            'AI Models Controller',
            'Failed to load AI models controller',
            is_api_route=True
        )
    except Exception as e:
        logger.error(f"Error getting available models: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/chat/load-model', methods=['POST'])
def load_model():
    """Load a specific AI model"""
    try:
        data = request.get_json()
        model_name = data.get('model_name')
        
        if not model_name:
            return jsonify({
                'success': False,
                'error': 'Model name is required'
            }), 400
        
        # Import AI models controller
        from src.controllers.ai_models_controller import AIModelsController
        controller = AIModelsController()
        result = controller.load_model(model_name)
        
        return jsonify({
            'success': True,
            'model_loaded': result,
            'model_name': model_name
        })
    except ImportError as e:
        return handle_controller_import_error(
            'AIModelsController',
            e,
            'AI Models Controller',
            'Failed to load AI models controller',
            is_api_route=True
        )
    except Exception as e:
        logger.error(f"Error loading model {model_name}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/chat/send', methods=['POST'])
def send_chat_message():
    """Send a message to the AI chat"""
    try:
        data = request.get_json()
        message = data.get('message')
        model_name = data.get('model_name')
        conversation_id = data.get('conversation_id')
        
        if not message:
            return jsonify({
                'success': False,
                'error': 'Message is required'
            }), 400
        
        # Import chat controller
        from src.controllers.chat_controller import ChatController
        controller = ChatController()
        
        # Send message and get response
        response = controller.send_message(
            message=message,
            model_name=model_name,
            conversation_id=conversation_id
        )
        
        return jsonify({
            'success': True,
            'response': response,
            'conversation_id': response.get('conversation_id')
        })
    except ImportError as e:
        return handle_controller_import_error(
            'ChatController',
            e,
            'Chat Controller',
            'Failed to load chat controller',
            is_api_route=True
        )
    except Exception as e:
        logger.error(f"Error sending chat message: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/chat/conversations', methods=['GET'])
def get_conversations():
    """Get user conversations"""
    try:
        # Import chat controller
        from src.controllers.chat_controller import ChatController
        controller = ChatController()
        conversations = controller.get_conversations()
        
        return jsonify({
            'success': True,
            'conversations': conversations
        })
    except ImportError as e:
        return handle_controller_import_error(
            'ChatController',
            e,
            'Chat Controller',
            'Failed to load chat controller',
            is_api_route=True
        )
    except Exception as e:
        logger.error(f"Error getting conversations: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/chat/conversation/<conversation_id>', methods=['GET'])
def get_conversation(conversation_id):
    """Get specific conversation messages"""
    try:
        # Import chat controller
        from src.controllers.chat_controller import ChatController
        controller = ChatController()
        messages = controller.get_conversation_messages(conversation_id)
        
        return jsonify({
            'success': True,
            'messages': messages,
            'conversation_id': conversation_id
        })
    except ImportError as e:
        return handle_controller_import_error(
            'ChatController',
            e,
            'Chat Controller',
            'Failed to load chat controller',
            is_api_route=True
        )
    except Exception as e:
        logger.error(f"Error getting conversation {conversation_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Settings API Routes
@api_bp.route('/settings/load', methods=['GET'])
def load_settings():
    """Load application settings"""
    try:
        from src.controllers.settings_controller import SettingsController
        controller = SettingsController()
        settings = controller.load_settings()
        return jsonify({'success': True, 'settings': settings})
    except ImportError as e:
        return handle_controller_import_error(
            'SettingsController',
            e,
            'Settings Controller',
            'Failed to load settings controller',
            is_api_route=True
        )
    except Exception as e:
        logger.error(f"Error loading settings: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/settings/save', methods=['POST'])
def save_settings():
    """Save application settings"""
    try:
        from src.controllers.settings_controller import SettingsController
        controller = SettingsController()
        data = request.get_json()
        success = controller.save_settings(data)
        return jsonify({'success': success})
    except ImportError as e:
        return handle_controller_import_error(
            'SettingsController',
            e,
            'Settings Controller',
            'Failed to load settings controller',
            is_api_route=True
        )
    except Exception as e:
        logger.error(f"Error saving settings: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/settings/test-model', methods=['POST'])
def test_model():
    """Test AI model configuration"""
    try:
        from src.controllers.settings_controller import SettingsController
        controller = SettingsController()
        data = request.get_json()
        model_name = data.get('model_name')
        success = controller.test_model(model_name)
        return jsonify({'success': success})
    except ImportError as e:
        return handle_controller_import_error(
            'SettingsController',
            e,
            'Settings Controller',
            'Failed to load settings controller',
            is_api_route=True
        )
    except Exception as e:
        logger.error(f"Error testing model: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/settings/env/load', methods=['GET'])
def load_env_file():
    """Load .env file content"""
    try:
        from src.controllers.settings_controller import SettingsController
        controller = SettingsController()
        content = controller.load_env_file()
        return jsonify({'success': True, 'content': content})
    except ImportError as e:
        return handle_controller_import_error(
            'SettingsController',
            e,
            'Settings Controller',
            'Failed to load settings controller',
            is_api_route=True
        )
    except Exception as e:
        logger.error(f"Error loading .env file: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/settings/env/save', methods=['POST'])
def save_env_file():
    """Save .env file content"""
    try:
        from src.controllers.settings_controller import SettingsController
        controller = SettingsController()
        data = request.get_json()
        content = data.get('content')
        success = controller.save_env_file(content)
        return jsonify({'success': success})
    except ImportError as e:
        return handle_controller_import_error(
            'SettingsController',
            e,
            'Settings Controller',
            'Failed to load settings controller',
            is_api_route=True
        )
    except Exception as e:
        logger.error(f"Error saving .env file: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/settings/test-database', methods=['POST'])
def test_database_connection():
    """Test database connection"""
    try:
        from src.controllers.settings_controller import SettingsController
        controller = SettingsController()
        data = request.get_json()
        db_type = data.get('db_type')
        config = data.get('config')
        success = controller.test_database_connection(db_type, config)
        return jsonify({'success': success})
    except ImportError as e:
        return handle_controller_import_error(
            'SettingsController',
            e,
            'Settings Controller',
            'Failed to load settings controller',
            is_api_route=True
        )
    except Exception as e:
        logger.error(f"Error testing database connection: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def register_blueprints(app):
    """Register only main blueprint for simplified development"""
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')        # UNCOMMENTED FOR SETTINGS API
    # app.register_blueprint(auth_bp, url_prefix='/auth')      # COMMENTED OUT
    # app.register_blueprint(admin_bp, url_prefix='/admin')    # COMMENTED OUT
    # app.register_blueprint(docs_bp)                          # COMMENTED OUT

# Export blueprints for use in app.py (simplified)
__all__ = ['main_bp', 'register_blueprints']

# EXAMPLE PAGE ROUTE - COMMENTED OUT
# from src.controllers.example_controller import ExampleController

# Route definition centralised here – calls controller logic
# @main_bp.route('/examples/<slug>')  # COMMENTED OUT
# def examples_show(slug):
#     return _dispatch('example_show', slug=slug)
