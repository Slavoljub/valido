"""
Unified Route System for ValidoAI
Centralized route definitions for all application modules

CONSOLIDATED FROM:
- routes.py (main application routes)
- src/api/routes.py (API endpoints)
- src/auth/routes.py (authentication routes)
- src/ai_local_models/routes.py (AI model routes)
- src/scraping/routes.py (web scraping routes)
"""

from typing import Dict, List, Any, Optional, Callable, Union
from flask import Blueprint, current_app, request, session, g, render_template, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash, generate_password_hash
from datetime import datetime, timedelta
import json
import os
import logging
import uuid
from functools import wraps

# Import existing modules with fallbacks
try:
    from src.utils.error_logger import error_logger
except ImportError:
    error_logger = None

try:
    from src.crud.crud_registry import crud_registry
except ImportError:
    crud_registry = None

logger = logging.getLogger(__name__)

class RouteManager:
    """Centralized route management system"""

    def __init__(self):
        self.routes: Dict[str, Dict[str, Any]] = {}
        self.modules: Dict[str, List[str]] = {}
        self.blueprints: Dict[str, Blueprint] = {}

    def register_route(self, path: str, methods: List[str], handler: Callable,
                      module: str = 'main', **kwargs):
        """Register a route with metadata"""
        route_key = f"{methods[0]}_{path}"

        self.routes[route_key] = {
            'path': path,
            'methods': methods,
            'handler': handler,
            'module': module,
            'requires_auth': kwargs.get('requires_auth', True),
            'permissions': kwargs.get('permissions', []),
            'rate_limit': kwargs.get('rate_limit', None),
            'cache_timeout': kwargs.get('cache_timeout', None),
            'menu_title': kwargs.get('menu_title', ''),
            'menu_icon': kwargs.get('menu_icon', ''),
            'menu_order': kwargs.get('menu_order', 999),
            'description': kwargs.get('description', ''),
            'tags': kwargs.get('tags', []),
            'is_active': kwargs.get('is_active', True)
        }

        if module not in self.modules:
            self.modules[module] = []
        if path not in self.modules[module]:
            self.modules[module].append(path)

    def get_routes_for_module(self, module: str) -> List[Dict[str, Any]]:
        """Get all routes for a specific module"""
        return [route for route in self.routes.values() if route['module'] == module]

    def get_menu_routes(self) -> List[Dict[str, Any]]:
        """Get routes that should appear in navigation menu"""
        menu_routes = [route for route in self.routes.values()
                      if route['menu_title'] and route['is_active']]
        return sorted(menu_routes, key=lambda x: x['menu_order'])

    def get_route_by_path(self, path: str, method: str = 'GET') -> Optional[Dict[str, Any]]:
        """Get route by path and method"""
        route_key = f"{method}_{path}"
        return self.routes.get(route_key)

    def get_all_routes(self) -> List[Dict[str, Any]]:
        """Get all registered routes"""
        return list(self.routes.values())

    def get_route_stats(self) -> Dict[str, Any]:
        """Get statistics about registered routes"""
        total_routes = len(self.routes)
        modules_count = len(self.modules)
        menu_routes = len([r for r in self.routes.values() if r['menu_title']])

        routes_by_method = {}
        for route in self.routes.values():
            for method in route['methods']:
                routes_by_method[method] = routes_by_method.get(method, 0) + 1

        return {
            'total_routes': total_routes,
            'modules': modules_count,
            'menu_routes': menu_routes,
            'routes_by_method': routes_by_method,
            'modules_list': list(self.modules.keys())
        }

    def register_with_app(self, app):
        """Register all routes with Flask application"""
        logger.info("Registering unified routes with Flask application...")

        for route_config in self.routes.values():
            try:
                path = route_config['path']
                methods = route_config.get('methods', ['GET'])
                handler = route_config['handler']
                module = route_config.get('module', 'unknown')

                # Create endpoint name
                endpoint_name = f"{module}_{path.replace('/', '_').replace('-', '_').strip('_')}"

                # Register the route
                app.add_url_rule(
                    path,
                    endpoint=endpoint_name,
                    view_func=handler,
                    methods=methods
                )

                logger.debug(f"✅ Registered route: {methods} {path} -> {endpoint_name}")

            except Exception as e:
                logger.error(f"❌ Failed to register route {route_config.get('path', 'unknown')}: {e}")

        logger.info(f"✅ Successfully registered {len(self.routes)} unified routes with Flask application")

class RouteBuilder:
    """Helper class to build CRUD routes for any table"""

    def __init__(self, route_manager: RouteManager):
        self.route_manager = route_manager

    def build_crud_routes(self, table_name: str, controller_class: Any,
                         module: str = 'main', prefix: str = None):
        """Build standard CRUD routes for a table"""
        if prefix is None:
            prefix = f'/{table_name}'

        # Get CRUD instance
        crud_instance = crud_registry.get_crud(table_name)
        if not crud_instance:
            logger.warning(f"No CRUD instance found for table: {table_name}")
            return

        # Create controller instance
        controller = controller_class()

        # Define route configurations
        route_configs = [
            {
                'path': prefix,
                'methods': ['GET'],
                'handler': controller.get_list,
                'menu_title': f'{table_name.replace("_", " ").title()}',
                'menu_icon': 'list',
                'menu_order': 100,
                'description': f'List all {table_name}',
                'tags': ['crud', 'list']
            },
            {
                'path': f'{prefix}/create',
                'methods': ['GET', 'POST'],
                'handler': controller.create,
                'description': f'Create new {table_name} record',
                'tags': ['crud', 'create']
            },
            {
                'path': f'{prefix}/<record_id>',
                'methods': ['GET'],
                'handler': controller.get_detail,
                'description': f'Get {table_name} record details',
                'tags': ['crud', 'detail']
            },
            {
                'path': f'{prefix}/<record_id>/edit',
                'methods': ['GET', 'PUT'],
                'handler': controller.edit,
                'description': f'Edit {table_name} record',
                'tags': ['crud', 'edit']
            },
            {
                'path': f'{prefix}/<record_id>/delete',
                'methods': ['DELETE'],
                'handler': controller.delete,
                'description': f'Delete {table_name} record',
                'tags': ['crud', 'delete']
            },
            {
                'path': f'{prefix}/search',
                'methods': ['GET'],
                'handler': controller.search,
                'description': f'Search {table_name} records',
                'tags': ['crud', 'search']
            },
            {
                'path': f'{prefix}/bulk',
                'methods': ['POST'],
                'handler': controller.bulk_operations,
                'description': f'Bulk operations for {table_name}',
                'tags': ['crud', 'bulk']
            },
            {
                'path': f'{prefix}/export',
                'methods': ['GET'],
                'handler': controller.export,
                'description': f'Export {table_name} data',
                'tags': ['crud', 'export']
            },
            {
                'path': f'{prefix}/import',
                'methods': ['POST'],
                'handler': controller.import_data,
                'description': f'Import {table_name} data',
                'tags': ['crud', 'import']
            }
        ]

        # Register routes
        for config in route_configs:
            self.route_manager.register_route(
                module=module,
                **config
            )

    def build_dashboard_routes(self, module: str = 'dashboard'):
        """Build dashboard-related routes"""
        dashboard_routes = [
            {
                'path': '/dashboard',
                'methods': ['GET'],
                'handler': 'dashboard.index',
                'menu_title': 'Dashboard',
                'menu_icon': 'dashboard',
                'menu_order': 1,
                'description': 'Main dashboard',
                'tags': ['dashboard']
            },
            {
                'path': '/dashboard/analytics',
                'methods': ['GET'],
                'handler': 'dashboard.analytics',
                'menu_title': 'Analytics',
                'menu_icon': 'chart',
                'menu_order': 2,
                'description': 'Analytics and reporting',
                'tags': ['dashboard', 'analytics']
            },
            {
                'path': '/dashboard/reports',
                'methods': ['GET'],
                'handler': 'dashboard.reports',
                'menu_title': 'Reports',
                'menu_icon': 'report',
                'menu_order': 3,
                'description': 'Generate reports',
                'tags': ['dashboard', 'reports']
            }
        ]

        for config in dashboard_routes:
            self.route_manager.register_route(module=module, **config)

    def build_system_routes(self, module: str = 'system'):
        """Build system-related routes"""
        system_routes = [
            {
                'path': '/system/settings',
                'methods': ['GET', 'POST'],
                'handler': 'system.settings',
                'menu_title': 'Settings',
                'menu_icon': 'settings',
                'menu_order': 90,
                'description': 'System settings',
                'tags': ['system']
            },
            {
                'path': '/system/users',
                'methods': ['GET'],
                'handler': 'system.users',
                'menu_title': 'Users',
                'menu_icon': 'users',
                'menu_order': 91,
                'description': 'User management',
                'tags': ['system', 'users']
            },
            {
                'path': '/system/logs',
                'methods': ['GET'],
                'handler': 'system.logs',
                'menu_title': 'System Logs',
                'menu_icon': 'logs',
                'menu_order': 92,
                'description': 'View system logs',
                'tags': ['system', 'logs']
            },
            {
                'path': '/recycle-bin',
                'methods': ['GET'],
                'handler': 'recycle_bin.index',
                'menu_title': 'Recycle Bin',
                'menu_icon': 'trash',
                'menu_order': 95,
                'description': 'Manage deleted records',
                'tags': ['system', 'recycle_bin']
            },
            {
                'path': '/ui-examples',
                'methods': ['GET'],
                'handler': 'ui_examples.index',
                'menu_title': 'UI Examples',
                'menu_icon': 'palette',
                'menu_order': 96,
                'description': 'Component library and examples',
                'tags': ['system', 'ui', 'examples']
            }
        ]

        for config in system_routes:
            self.route_manager.register_route(module=module, **config)

# ============================================================================
# CONSOLIDATED ROUTE FUNCTIONS FROM ALL MODULES
# ============================================================================

# Main Dashboard Routes (from src/api/routes.py)
def index():
    """Main dashboard"""
    try:
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error loading index: {e}")
        return render_template('dashboard/index.html')

def health():
    """Health check endpoint for monitoring"""
    try:
        # Check database connectivity
        db_status = "healthy"
        try:
            from src.models.unified_models import db
            db.session.execute('SELECT 1')
        except Exception as e:
            db_status = f"unhealthy: {str(e)}"

        # Check AI/ML status (lazy loaded)
        ai_status = "healthy"
        gpu_available = False
        gpu_count = 0

        try:
            from src.core.lazy_loader import get_torch
            torch = get_torch()
            gpu_available = torch.cuda.is_available()
            gpu_count = torch.cuda.device_count() if gpu_available else 0
        except Exception as e:
            ai_status = f"unhealthy: {str(e)}"

        # System metrics
        import psutil
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        health_data = {
            "status": "healthy" if db_status == "healthy" and ai_status == "healthy" else "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "database": {
                "status": db_status,
                "type": "PostgreSQL/SQLite"
            },
            "ai_ml": {
                "status": ai_status,
                "gpu_available": gpu_available,
                "gpu_count": gpu_count
            },
            "system": {
                "memory_usage_percent": memory.percent,
                "memory_used_gb": round(memory.used / (1024**3), 2),
                "memory_total_gb": round(memory.total / (1024**3), 2),
                "disk_usage_percent": disk.percent,
                "disk_free_gb": round(disk.free / (1024**3), 2)
            },
            "services": {
                "web_server": "running",
                "api": "running",
                "websocket": "enabled"
            }
        }

        status_code = 200 if health_data["status"] == "healthy" else 503
        return jsonify(health_data), status_code

    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }), 500

def dashboard():
    """Main dashboard page"""
    return render_template('dashboard.html',
                         current_user={'id': 'demo_user', 'name': 'Demo User'})

def business_intelligence_dashboard():
    """Business Intelligence Dashboard"""
    try:
        from src.analytics.predictive import start_predictive_engine
        start_predictive_engine()
        return render_template('dashboard/business_intelligence.html',
                             current_user={'id': 'demo_user', 'name': 'Demo User'})
    except Exception as e:
        logger.error(f"Error loading BI dashboard: {e}")
        return redirect(url_for('dashboard'))

def predictive_analytics_dashboard():
    """Predictive Analytics Dashboard with AI forecasting"""
    try:
        from src.analytics.predictive import start_predictive_engine
        start_predictive_engine()
        return render_template('dashboard/predictive_analytics.html',
                             current_user={'id': 'demo_user', 'name': 'Demo User'})
    except Exception as e:
        logger.error(f"Error loading predictive dashboard: {e}")
        return redirect(url_for('dashboard'))

# Content Management Routes
def content_management():
    """Content Management System"""
    try:
        from src.content_manager import content_manager
        return render_template('content/management.html',
                             current_user={'id': 'demo_user', 'name': 'Demo User'})
    except Exception as e:
        logger.error(f"Error loading content management: {e}")
        return redirect(url_for('dashboard'))

# AI Analysis Routes
def sentiment_analysis():
    """Sentiment Analysis Dashboard"""
    try:
        from src.ai.sentiment import sentiment_analyzer
        return render_template('ai/sentiment_analysis.html',
                             current_user={'id': 'demo_user', 'name': 'Demo User'})
    except Exception as e:
        logger.error(f"Error loading sentiment analysis: {e}")
        return redirect(url_for('dashboard'))

# Settings Routes
def settings():
    """Settings page with tabs"""
    return render_template('settings.html')

# Authentication Routes (from src/auth/routes.py)
def auth_login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        # Handle login logic here
        flash('Login functionality to be implemented', 'info')
        return redirect(url_for('dashboard'))

    return render_template('auth/login.html')

def auth_register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        # Handle registration logic here
        flash('Registration functionality to be implemented', 'info')
        return redirect(url_for('dashboard'))

    return render_template('auth/register.html')

def setup_2fa():
    """Setup 2FA for the current user"""
    try:
        from src.auth.two_factor import two_factor_manager
        if two_factor_manager.is_2fa_enabled(current_user.id):
            flash('Two-factor authentication is already enabled.', 'info')
            return redirect(url_for('settings'))

        # Setup 2FA
        secret, qr_code, backup_codes = two_factor_manager.setup_2fa(current_user.id)
        return render_template('auth/setup_2fa.html',
                             qr_code=qr_code,
                             secret=secret,
                             backup_codes=backup_codes)
    except Exception as e:
        flash(f'Error setting up 2FA: {str(e)}', 'error')
        return redirect(url_for('settings'))

# AI Local Models Routes (from src/ai_local_models/routes.py)
def ai_models_status():
    """Get status of all AI models"""
    try:
        from src.ai_local_models.model_manager import model_manager
        from src.ai_local_models.config_manager import UnifiedConfigManager

        config_manager = UnifiedConfigManager()
        models = config_manager.get_all_models() if hasattr(config_manager, 'get_all_models') else {}

        status_data = []
        for model_id, model_info in models.items():
            status_data.append({
                'id': model_id,
                'name': getattr(model_info, 'name', 'Unknown'),
                'description': getattr(model_info, 'description', ''),
                'status': 'available'
            })

        return jsonify({'models': status_data})
    except Exception as e:
        logger.error(f"Error getting AI models status: {e}")
        return jsonify({'error': str(e)}), 500

def download_model():
    """Download AI model"""
    try:
        model_id = request.args.get('model_id')
        if not model_id:
            return jsonify({'error': 'model_id is required'}), 400

        from src.ai_local_models.model_manager import model_manager
        result = model_manager.download_model(model_id)

        return jsonify(result)
    except Exception as e:
        logger.error(f"Error downloading model: {e}")
        return jsonify({'error': str(e)}), 500

# Web Scraping Routes (from src/scraping/routes.py)
def scraping_dashboard():
    """Scraping dashboard"""
    return render_template('scraping/index.html')

def scraping_config():
    """Scraping configuration interface"""
    return render_template('scraping/config.html')

def test_url():
    """Test scraping a single URL"""
    url = request.form.get('url')
    if not url:
        return jsonify({'success': False, 'message': 'URL is required'})

    try:
        from src.scraping.scraper import WebScraper
        scraper = WebScraper()
        result = scraper.scrape_url(url)

        return jsonify({
            'success': True,
            'data': result,
            'url': url
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })

# API Routes (from routes.py)
def api_health():
    """API health check"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

def get_dashboard_data():
    """Get business intelligence dashboard data"""
    try:
        from src.dashboard_analytics import get_dashboard_data, get_kpi_cards

        user_id = request.args.get('user_id', 'demo-user')
        dashboard_data = get_dashboard_data(user_id)
        kpi_cards = get_kpi_cards()

        return jsonify({
            'dashboard_data': dashboard_data,
            'kpi_cards': kpi_cards,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error getting dashboard data: {e}")
        return jsonify({'error': str(e)}), 500

def get_predictive_data():
    """Get predictive analytics data"""
    try:
        from src.predictive_analytics import get_business_intelligence_report

        user_id = request.args.get('user_id', 'demo-user')
        predictive_data = get_business_intelligence_report()

        return jsonify({
            'predictive_data': predictive_data,
            'user_id': user_id,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error getting predictive data: {e}")
        return jsonify({'error': str(e)}), 500

# Global instances
route_manager = RouteManager()
route_builder = RouteBuilder(route_manager)

# Initialize with consolidated routes
def initialize_consolidated_routes():
    """Initialize consolidated routes from all modules"""

    logger.info("🚀 Initializing consolidated routes from all modules...")

    # Main Application Routes
    route_manager.register_route(
        path='/',
        methods=['GET'],
        handler=index,
        module='main',
        requires_auth=False,
        menu_title='Home',
        menu_icon='home',
        menu_order=1,
        description='Main dashboard'
    )

    route_manager.register_route(
        path='/health',
        methods=['GET'],
        handler=health,
        module='system',
        requires_auth=False,
        description='Health check endpoint for monitoring'
    )

    route_manager.register_route(
        path='/dashboard',
        methods=['GET'],
        handler=dashboard,
        module='main',
        menu_title='Dashboard',
        menu_icon='dashboard',
        menu_order=2,
        description='Main dashboard page'
    )

    # Business Intelligence Routes
    route_manager.register_route(
        path='/dashboard/business-intelligence',
        methods=['GET'],
        handler=business_intelligence_dashboard,
        module='dashboard',
        menu_title='Business Intelligence',
        menu_icon='chart-line',
        menu_order=3,
        description='Business Intelligence Dashboard'
    )

    route_manager.register_route(
        path='/dashboard/predictive-analytics',
        methods=['GET'],
        handler=predictive_analytics_dashboard,
        module='dashboard',
        menu_title='Predictive Analytics',
        menu_icon='brain',
        menu_order=4,
        description='Predictive Analytics Dashboard'
    )

    # Content Management
    route_manager.register_route(
        path='/content/management',
        methods=['GET'],
        handler=content_management,
        module='content',
        menu_title='Content Management',
        menu_icon='file-alt',
        menu_order=5,
        description='Content Management System'
    )

    # AI Analysis
    route_manager.register_route(
        path='/ai/sentiment-analysis',
        methods=['GET'],
        handler=sentiment_analysis,
        module='ai',
        menu_title='Sentiment Analysis',
        menu_icon='comment-alt',
        menu_order=6,
        description='AI-powered text analysis'
    )

    # Settings
    route_manager.register_route(
        path='/settings',
        methods=['GET'],
        handler=settings,
        module='system',
        menu_title='Settings',
        menu_icon='cog',
        menu_order=90,
        description='System settings'
    )

    # Authentication Routes
    route_manager.register_route(
        path='/auth/login',
        methods=['GET', 'POST'],
        handler=auth_login,
        module='auth',
        requires_auth=False,
        description='User login'
    )

    route_manager.register_route(
        path='/auth/register',
        methods=['GET', 'POST'],
        handler=auth_register,
        module='auth',
        requires_auth=False,
        description='User registration'
    )

    route_manager.register_route(
        path='/auth/setup-2fa',
        methods=['GET', 'POST'],
        handler=setup_2fa,
        module='auth',
        requires_auth=True,
        description='Setup two-factor authentication'
    )

    # AI Local Models API Routes
    route_manager.register_route(
        path='/api/ai-models/status',
        methods=['GET'],
        handler=ai_models_status,
        module='ai',
        requires_auth=True,
        description='Get AI models status'
    )

    route_manager.register_route(
        path='/api/ai-models/download',
        methods=['POST'],
        handler=download_model,
        module='ai',
        requires_auth=True,
        description='Download AI model'
    )

    # Web Scraping Routes
    route_manager.register_route(
        path='/scraping',
        methods=['GET'],
        handler=scraping_dashboard,
        module='scraping',
        menu_title='Web Scraping',
        menu_icon='spider',
        menu_order=7,
        description='Web scraping dashboard'
    )

    route_manager.register_route(
        path='/scraping/config',
        methods=['GET'],
        handler=scraping_config,
        module='scraping',
        description='Scraping configuration'
    )

    route_manager.register_route(
        path='/scraping/test-url',
        methods=['POST'],
        handler=test_url,
        module='scraping',
        description='Test URL scraping'
    )

    # API Health and Analytics
    route_manager.register_route(
        path='/api/health',
        methods=['GET'],
        handler=api_health,
        module='api',
        requires_auth=False,
        description='API health check'
    )

    route_manager.register_route(
        path='/api/dashboard/data',
        methods=['GET'],
        handler=get_dashboard_data,
        module='api',
        description='Get dashboard data'
    )

    route_manager.register_route(
        path='/api/predictive/data',
        methods=['GET'],
        handler=get_predictive_data,
        module='api',
        description='Get predictive analytics data'
    )

    # System routes
    route_manager.register_route(
        path='/system/settings',
        methods=['GET', 'POST'],
        handler=settings,
        module='system',
        menu_title='System Settings',
        menu_icon='cogs',
        menu_order=91,
        description='System settings and configuration'
    )

    # Additional utility routes
    route_manager.register_route(
        path='/recycle-bin',
        methods=['GET'],
        handler=lambda: render_template('recycle_bin/index.html'),
        module='system',
        menu_title='Recycle Bin',
        menu_icon='trash',
        menu_order=95,
        description='Manage deleted records'
    )

    route_manager.register_route(
        path='/ui-examples',
        methods=['GET'],
        handler=lambda: render_template('ui-examples/index.html'),
        module='system',
        menu_title='UI Examples',
        menu_icon='palette',
        menu_order=96,
        description='Component library and examples'
    )

    logger.info(f"✅ Successfully consolidated {len(route_manager.routes)} routes from all modules")

# Auto-initialize consolidated routes
initialize_consolidated_routes()
