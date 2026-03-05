"""
Unified Route Generator for ValidoAI
Automatically generates CRUD routes based on configuration
"""

import logging
from typing import Dict, List, Any, Optional, Callable
from flask import Blueprint, render_template, jsonify, request, current_app, g, Response, url_for
from functools import wraps
from ..crud.unified_crud_operations import unified_crud_registry
from ..crud.unified_crud_config import CRUDConfig, crud_config_registry

logger = logging.getLogger(__name__)


def handle_template_errors(f):
    """Decorator to handle template errors"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"Template error in {f.__name__}: {e}")
            return render_template('errors/error.html', error=str(e)), 500
    return decorated_function


class UnifiedRouteGenerator:
    """Unified route generator for CRUD operations"""
    
    def __init__(self, app=None):
        self.app = app
        self.blueprints: Dict[str, Blueprint] = {}
        self.route_handlers: Dict[str, Dict[str, Callable]] = {}
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize with Flask app"""
        self.app = app
    
    def generate_routes(self, table_name: str, config: CRUDConfig) -> Blueprint:
        """Generate all CRUD routes for a table"""
        
        # Create blueprint
        blueprint_name = f"{table_name}_bp"
        blueprint = Blueprint(table_name, __name__, url_prefix=f'/{table_name}')
        
        # Get CRUD instance
        crud = unified_crud_registry.get_crud(table_name, config)
        
        # Generate route handlers
        self._generate_list_route(blueprint, crud, config, table_name)
        self._generate_show_route(blueprint, crud, config, table_name)
        self._generate_create_routes(blueprint, crud, config, table_name)
        self._generate_edit_routes(blueprint, crud, config, table_name)
        self._generate_delete_routes(blueprint, crud, config, table_name)
        self._generate_export_routes(blueprint, crud, config, table_name)
        self._generate_bulk_routes(blueprint, crud, config, table_name)
        self._generate_api_routes(blueprint, crud, config, table_name)
        
        # Store blueprint
        self.blueprints[table_name] = blueprint
        
        return blueprint
    
    def _generate_list_route(self, blueprint: Blueprint, crud, config: CRUDConfig, table_name: str):
        """Generate list/index route"""
        
        @blueprint.route('/')
        @handle_template_errors
        def index():
            """List all records with filtering and pagination"""
            
            # Get query parameters
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', config.page_size, type=int)
            sort_by = request.args.get('sort_by', config.default_sort)
            sort_order = request.args.get('sort_order', config.default_order)
            search = request.args.get('search', '')
            
            # Get filters from request
            filters = {}
            for filter_config in config.filters:
                value = request.args.get(filter_config.field)
                if value is not None and value != '':
                    filters[filter_config.field] = value
            
            # Get data
            data = crud.get_list_data(
                page=page,
                per_page=per_page,
                sort_by=sort_by,
                sort_order=sort_order,
                filters=filters,
                search=search
            )
            
            # Get statistics
            stats = crud.get_statistics()
            
            return render_template(
                f'{table_name}/index.html',
                records=data['records'],
                pagination=data['pagination'],
                sorting=data['sorting'],
                filters=data['filters'],
                search=data['search'],
                config=config,
                stats=stats,
                table_name=config.table_name,
                display_name=config.display_name,
                url_for=url_for
            )
    
    def _generate_show_route(self, blueprint: Blueprint, crud, config: CRUDConfig, table_name: str):
        """Generate show/view route"""
        
        @blueprint.route('/<id>')
        @handle_template_errors
        def show(id):
            """Show single record with related data"""
            
            # Get record
            success, record = crud.read(id)
            if not success:
                return render_template('errors/404.html'), 404
            
            # Get related data for tabs
            related_data = {}
            if config.ui_components.get('tabs', False):
                for tab_config in config.tabs:
                    tab_data = crud.get_related_data(id, tab_config)
                    related_data[tab_config.name] = tab_data
            
            return render_template(
                f'{table_name}/show.html',
                record=record,
                related_data=related_data,
                config=config,
                table_name=config.table_name,
                display_name=config.display_name,
                url_for=url_for
            )
    
    def _generate_create_routes(self, blueprint: Blueprint, crud, config: CRUDConfig, table_name: str):
        """Generate create routes"""
        
        @blueprint.route('/create')
        @handle_template_errors
        def create_form():
            """Show create form"""
            
            return render_template(
                f'{table_name}/create.html',
                config=config,
                table_name=config.table_name,
                display_name=config.display_name,
                url_for=url_for
            )
        
        @blueprint.route('/', methods=['POST'])
        @handle_template_errors
        def create():
            """Create new record"""
            
            # Get form data
            data = request.form.to_dict()
            
            # Validate data
            is_valid, errors = crud.validate_data(data, "create")
            if not is_valid:
                return jsonify({'success': False, 'errors': errors}), 400
            
            # Create record
            success, result = crud.create(data)
            if not success:
                return jsonify({'success': False, 'error': result}), 400
            
            return jsonify({'success': True, 'id': result})
    
    def _generate_edit_routes(self, blueprint: Blueprint, crud, config: CRUDConfig, table_name: str):
        """Generate edit routes"""
        
        @blueprint.route('/<id>/edit')
        @handle_template_errors
        def edit_form(id):
            """Show edit form"""
            
            # Get record
            success, record = crud.read(id)
            if not success:
                return render_template('errors/404.html'), 404
            
            return render_template(
                f'{table_name}/edit.html',
                record=record,
                config=config,
                table_name=config.table_name,
                display_name=config.display_name,
                url_for=url_for
            )
        
        @blueprint.route('/<id>', methods=['PUT', 'PATCH'])
        @handle_template_errors
        def update(id):
            """Update record"""
            
            # Get form data
            data = request.form.to_dict()
            
            # Validate data
            is_valid, errors = crud.validate_data(data, "update")
            if not is_valid:
                return jsonify({'success': False, 'errors': errors}), 400
            
            # Update record
            success, result = crud.update(id, data)
            if not success:
                return jsonify({'success': False, 'error': result}), 400
            
            return jsonify({'success': True})
    
    def _generate_delete_routes(self, blueprint: Blueprint, crud, config: CRUDConfig, table_name: str):
        """Generate delete routes"""
        
        @blueprint.route('/<id>', methods=['DELETE'])
        @handle_template_errors
        def delete(id):
            """Delete record"""
            
            # Check if soft delete is available
            if hasattr(crud, 'soft_delete'):
                success, result = crud.soft_delete(id)
            else:
                success, result = crud.delete(id)
            
            if not success:
                return jsonify({'success': False, 'error': result}), 400
            
            return jsonify({'success': True})
    
    def _generate_export_routes(self, blueprint: Blueprint, crud, config: CRUDConfig, table_name: str):
        """Generate export routes"""
        
        @blueprint.route('/export')
        @handle_template_errors
        def export():
            """Export data"""
            
            if not config.ui_components.get('export', True):
                return jsonify({'success': False, 'error': 'Export not enabled'}), 403
            
            # Get parameters
            format_type = request.args.get('format', 'csv')
            filters = request.args.to_dict()
            
            # Remove non-filter parameters
            for key in ['format', 'page', 'per_page', 'sort_by', 'sort_order']:
                filters.pop(key, None)
            
            # Export data
            success, result = crud.export_data(
                format_type=format_type,
                filters=filters
            )
            
            if not success:
                return jsonify({'success': False, 'error': result}), 400
            
            # Return file
            if format_type == 'csv':
                return Response(
                    result,
                    mimetype='text/csv',
                    headers={'Content-Disposition': f'attachment;filename={config.table_name}.csv'}
                )
            elif format_type == 'excel':
                return Response(
                    result,
                    mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    headers={'Content-Disposition': f'attachment;filename={config.table_name}.xlsx'}
                )
            elif format_type == 'json':
                return Response(
                    result,
                    mimetype='application/json',
                    headers={'Content-Disposition': f'attachment;filename={config.table_name}.json'}
                )
            else:
                return jsonify({'success': False, 'error': 'Unsupported format'}), 400
    
    def _generate_bulk_routes(self, blueprint: Blueprint, crud, config: CRUDConfig, table_name: str):
        """Generate bulk operation routes"""
        
        @blueprint.route('/bulk', methods=['POST'])
        @handle_template_errors
        def bulk_operations():
            """Perform bulk operations"""
            
            if not config.ui_components.get('bulk_operations', False):
                return jsonify({'success': False, 'error': 'Bulk operations not enabled'}), 403
            
            # Get request data
            data = request.get_json()
            operation = data.get('operation')
            record_ids = data.get('record_ids', [])
            update_data = data.get('data')
            
            if not operation or not record_ids:
                return jsonify({'success': False, 'error': 'Missing operation or record IDs'}), 400
            
            # Perform bulk operation
            success, result = crud.bulk_operations(
                operation=operation,
                record_ids=record_ids,
                data=update_data
            )
            
            if not success:
                return jsonify({'success': False, 'error': result}), 400
            
            return jsonify({'success': True, 'message': result})
    
    def _generate_api_routes(self, blueprint: Blueprint, crud, config: CRUDConfig, table_name: str):
        """Generate API routes"""
        
        @blueprint.route('/api/list')
        def api_list():
            """API endpoint for list data"""
            
            # Get query parameters
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', config.page_size, type=int)
            sort_by = request.args.get('sort_by', config.default_sort)
            sort_order = request.args.get('sort_order', config.default_order)
            search = request.args.get('search', '')
            
            # Get filters
            filters = {}
            for filter_config in config.filters:
                value = request.args.get(filter_config.field)
                if value is not None and value != '':
                    filters[filter_config.field] = value
            
            # Get data
            data = crud.get_list_data(
                page=page,
                per_page=per_page,
                sort_by=sort_by,
                sort_order=sort_order,
                filters=filters,
                search=search
            )
            
            return jsonify(data)
        
        @blueprint.route('/api/<id>')
        def api_show(id):
            """API endpoint for single record"""
            
            success, record = crud.read(id)
            if not success:
                return jsonify({'success': False, 'error': 'Record not found'}), 404
            
            return jsonify({'success': True, 'record': record})
        
        @blueprint.route('/api/stats')
        def api_stats():
            """API endpoint for statistics"""
            
            stats = crud.get_statistics()
            return jsonify(stats)
    
    def register_all_routes(self, app):
        """Register all generated routes with Flask app"""
        
        for table_name, blueprint in self.blueprints.items():
            app.register_blueprint(blueprint)
            logger.info(f"Registered routes for table: {table_name}")
    
    def generate_all_routes(self, configs: Dict[str, CRUDConfig]):
        """Generate routes for all configurations"""
        
        for table_name, config in configs.items():
            self.generate_routes(table_name, config)
    
    def get_blueprint(self, table_name: str) -> Optional[Blueprint]:
        """Get blueprint for table"""
        return self.blueprints.get(table_name)


# Global route generator instance
unified_route_generator = UnifiedRouteGenerator()
