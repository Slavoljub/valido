"""
CRUD Route Generator for ValidoAI
Automatically generates CRUD routes for all database tables
"""

from typing import Dict, List, Any, Optional, Callable
from flask import Blueprint, request, jsonify, current_app, session, g
from src.routes.unified_routes import route_manager, route_builder
from src.crud.crud_registry import crud_registry
from src.components.component_system import component_registry
from src.utils.error_logger import error_logger
import logging

logger = logging.getLogger(__name__)

class CRUDRouteGenerator:
    """Generates CRUD routes for database tables"""

    def __init__(self):
        self.generated_controllers: Dict[str, Any] = {}

    def generate_crud_routes(self, table_name: str, module: str = 'crud') -> Dict[str, Any]:
        """Generate CRUD routes for a specific table"""
        try:
            # Get CRUD instance
            crud_instance = crud_registry.get_crud(table_name)
            if not crud_instance:
                logger.warning(f"No CRUD instance found for table: {table_name}")
                return {}

            # Create controller class dynamically
            controller_class = self._create_controller_class(table_name, crud_instance)
            self.generated_controllers[table_name] = controller_class

            # Generate routes using route builder
            route_builder.build_crud_routes(
                table_name=table_name,
                controller_class=controller_class,
                module=module
            )

            logger.info(f"Generated CRUD routes for table: {table_name}")
            return {
                'table_name': table_name,
                'controller_class': controller_class,
                'module': module,
                'routes_count': len([r for r in route_manager.routes.values() if r['module'] == module])
            }

        except Exception as e:
            logger.error(f"Error generating CRUD routes for {table_name}: {e}")
            return {'error': str(e)}

    def generate_all_crud_routes(self) -> Dict[str, Any]:
        """Generate CRUD routes for all tables in the registry"""
        results = {}
        all_tables = crud_registry.get_all_tables()

        for table_name in all_tables:
            results[table_name] = self.generate_crud_routes(table_name)

        return {
            'total_tables': len(all_tables),
            'generated_routes': results,
            'total_routes': len(route_manager.get_all_routes())
        }

    def _create_controller_class(self, table_name: str, crud_instance: Any) -> type:
        """Create a controller class for a table"""

        class GeneratedController:
            """Dynamically generated controller for CRUD operations"""

            def __init__(self):
                self.crud = crud_instance
                self.table_name = table_name

            def get_list(self) -> Dict[str, Any]:
                """Get list of records with filtering and pagination"""
                try:
                    # Get query parameters
                    filters = request.args.get('filters')
                    limit = int(request.args.get('limit', 50))
                    offset = int(request.args.get('offset', 0))
                    search = request.args.get('search', '').strip()

                    # Parse filters
                    filter_dict = {}
                    if filters:
                        try:
                            import json
                            filter_dict = json.loads(filters)
                        except json.JSONDecodeError:
                            raise ValueError("Invalid filters format")

                    # Add search filter
                    if search:
                        filter_dict['search'] = search

                    # Get records
                    success, result = self.crud.read(
                        filters=filter_dict,
                        limit=limit,
                        offset=offset
                    )

                    if not success:
                        raise ValueError(result)

                    records = result or []

                    # Get total count
                    count_success, total_count = self.crud.count(filters=filter_dict)

                    return {
                        'success': True,
                        'data': records,
                        'meta': {
                            'total': total_count if count_success else len(records),
                            'limit': limit,
                            'offset': offset,
                            'has_more': len(records) == limit
                        }
                    }

                except Exception as e:
                    error_logger.log_error(
                        error=str(e),
                        error_type=f'{table_name.upper()}_LIST_ERROR',
                        context={'request_args': dict(request.args)}
                    )
                    raise

            def get_detail(self, record_id: str) -> Dict[str, Any]:
                """Get a specific record"""
                try:
                    success, record = self.crud.read(record_id)

                    if not success:
                        raise ValueError("Record not found")
                    if not record:
                        raise ValueError("Record not found")

                    return {
                        'success': True,
                        'data': record
                    }

                except Exception as e:
                    error_logger.log_error(
                        error=str(e),
                        error_type=f'{table_name.upper()}_GET_ERROR',
                        context={'record_id': record_id}
                    )
                    raise

            def create(self) -> Dict[str, Any]:
                """Create a new record"""
                try:
                    data = request.get_json()
                    if not data:
                        raise ValueError("No data provided")

                    # Add audit fields
                    data['created_by'] = session.get('user_id', 'system')

                    success, result = self.crud.create(data)

                    if not success:
                        raise ValueError(result)

                    # Get created record
                    record_id = result
                    get_success, record = self.crud.read(record_id)

                    return {
                        'success': True,
                        'message': f'{table_name.title()} created successfully',
                        'data': record if get_success else None,
                        'record_id': record_id
                    }

                except Exception as e:
                    error_logger.log_error(
                        error=str(e),
                        error_type=f'{table_name.upper()}_CREATE_ERROR',
                        context={'request_data': request.get_json()}
                    )
                    raise

            def edit(self, record_id: str) -> Dict[str, Any]:
                """Update a record"""
                try:
                    data = request.get_json()
                    if not data:
                        raise ValueError("No data provided")

                    # Add audit fields
                    data['updated_by'] = session.get('user_id', 'system')

                    success, result = self.crud.update(record_id, data)

                    if not success:
                        raise ValueError(result)

                    # Get updated record
                    get_success, record = self.crud.read(record_id)

                    return {
                        'success': True,
                        'message': f'{table_name.title()} updated successfully',
                        'data': record if get_success else None
                    }

                except Exception as e:
                    error_logger.log_error(
                        error=str(e),
                        error_type=f'{table_name.upper()}_UPDATE_ERROR',
                        context={'record_id': record_id, 'request_data': request.get_json()}
                    )
                    raise

            def delete(self, record_id: str) -> Dict[str, Any]:
                """Delete a record (soft delete)"""
                try:
                    # Get deletion metadata
                    data = request.get_json() or {}
                    deleted_by = data.get('deleted_by', session.get('user_id', 'system'))
                    deleted_reason = data.get('deleted_reason', 'Deleted via API')

                    success, result = self.crud.delete(record_id, deleted_by, deleted_reason)

                    if not success:
                        raise ValueError(result)

                    return {
                        'success': True,
                        'message': f'{table_name.title()} moved to recycle bin successfully'
                    }

                except Exception as e:
                    error_logger.log_error(
                        error=str(e),
                        error_type=f'{table_name.upper()}_DELETE_ERROR',
                        context={'record_id': record_id}
                    )
                    raise

            def search(self) -> Dict[str, Any]:
                """Search records"""
                try:
                    query = request.args.get('q', '').strip()
                    limit = int(request.args.get('limit', 20))
                    fields = request.args.getlist('fields')

                    if not query:
                        raise ValueError("Search query is required")

                    if len(query) < 2:
                        raise ValueError("Search query must be at least 2 characters")

                    # Use default searchable fields if not specified
                    if not fields:
                        fields = self._get_searchable_fields()

                    success, results = self.crud.search(query, fields)

                    if not success:
                        raise ValueError(results)

                    # Limit results
                    limited_results = results[:limit] if results else []

                    return {
                        'success': True,
                        'data': limited_results,
                        'meta': {
                            'query': query,
                            'total': len(results) if results else 0,
                            'limit': limit,
                            'has_more': len(results) > limit if results else False
                        }
                    }

                except Exception as e:
                    error_logger.log_error(
                        error=str(e),
                        error_type=f'{table_name.upper()}_SEARCH_ERROR',
                        context={'query': request.args.get('q')}
                    )
                    raise

            def bulk_operations(self) -> Dict[str, Any]:
                """Handle bulk operations"""
                try:
                    data = request.get_json()
                    operation = data.get('operation')
                    record_ids = data.get('record_ids', [])

                    if not operation or not record_ids:
                        raise ValueError("Operation and record_ids are required")

                    results = []
                    success_count = 0
                    error_count = 0

                    if operation == 'delete':
                        deleted_by = data.get('deleted_by', session.get('user_id', 'system'))
                        deleted_reason = data.get('deleted_reason', 'Bulk deleted via API')

                        for record_id in record_ids:
                            try:
                                success, result = self.crud.delete(record_id, deleted_by, deleted_reason)
                                if success:
                                    success_count += 1
                                    results.append({'record_id': record_id, 'success': True})
                                else:
                                    error_count += 1
                                    results.append({'record_id': record_id, 'success': False, 'error': result})
                            except Exception as e:
                                error_count += 1
                                results.append({'record_id': record_id, 'success': False, 'error': str(e)})

                    elif operation == 'update':
                        update_data = data.get('update_data', {})
                        if not update_data:
                            raise ValueError("update_data is required for update operation")

                        update_data['updated_by'] = session.get('user_id', 'system')

                        for record_id in record_ids:
                            try:
                                success, result = self.crud.update(record_id, update_data)
                                if success:
                                    success_count += 1
                                    results.append({'record_id': record_id, 'success': True})
                                else:
                                    error_count += 1
                                    results.append({'record_id': record_id, 'success': False, 'error': result})
                            except Exception as e:
                                error_count += 1
                                results.append({'record_id': record_id, 'success': False, 'error': str(e)})

                    else:
                        raise ValueError(f"Unsupported operation: {operation}")

                    return {
                        'success': True,
                        'data': {
                            'operation': operation,
                            'total': len(record_ids),
                            'successful': success_count,
                            'failed': error_count,
                            'results': results
                        }
                    }

                except Exception as e:
                    error_logger.log_error(
                        error=str(e),
                        error_type=f'{table_name.upper()}_BULK_ERROR',
                        context={'operation': data.get('operation') if 'data' in locals() else None}
                    )
                    raise

            def export(self) -> Any:
                """Export records"""
                try:
                    format_type = request.args.get('format', 'json')
                    filters = {}

                    # Add filters from query params
                    for key, value in request.args.items():
                        if key not in ['format'] and value:
                            filters[key] = value

                    success, records = self.crud.read(filters=filters)

                    if success:
                        if format_type == 'csv':
                            import csv
                            import io
                            output = io.StringIO()
                            if records:
                                writer = csv.DictWriter(output, fieldnames=records[0].keys())
                                writer.writeheader()
                                writer.writerows(records)
                            from flask import Response
                            return Response(
                                output.getvalue(),
                                mimetype='text/csv',
                                headers={'Content-Disposition': f'attachment; filename={table_name}.csv'}
                            )
                        else:
                            return jsonify({'success': True, 'data': records})
                    else:
                        return jsonify({'success': False, 'error': records}), 400

                except Exception as e:
                    error_logger.log_error(
                        error=str(e),
                        error_type=f'{table_name.upper()}_EXPORT_ERROR',
                        context={'format': request.args.get('format')}
                    )
                    raise

            def import_data(self) -> Dict[str, Any]:
                """Import records from file"""
                try:
                    if 'file' not in request.files:
                        raise ValueError("No file provided")

                    file = request.files['file']
                    if file.filename == '':
                        raise ValueError("No file selected")

                    imported = 0
                    errors = []

                    if file.filename.endswith('.csv'):
                        import csv
                        import io
                        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
                        csv_reader = csv.DictReader(stream)

                        for row_num, row in enumerate(csv_reader, 2):  # Start at 2 to account for header
                            try:
                                row['created_by'] = session.get('user_id', 'system')
                                success, result = self.crud.create(row)
                                if success:
                                    imported += 1
                                else:
                                    errors.append(f"Row {row_num}: {result}")
                            except Exception as e:
                                errors.append(f"Row {row_num}: {str(e)}")

                    elif file.filename.endswith('.json'):
                        import json
                        data = json.load(file.stream)
                        if isinstance(data, list):
                            for item in data:
                                try:
                                    item['created_by'] = session.get('user_id', 'system')
                                    success, result = self.crud.create(item)
                                    if success:
                                        imported += 1
                                    else:
                                        errors.append(f"Item: {result}")
                                except Exception as e:
                                    errors.append(f"Item: {str(e)}")

                    return {
                        'success': True,
                        'data': {
                            'imported': imported,
                            'errors': errors
                        }
                    }

                except Exception as e:
                    error_logger.log_error(
                        error=str(e),
                        error_type=f'{table_name.upper()}_IMPORT_ERROR',
                        context={'filename': file.filename if 'file' in locals() else None}
                    )
                    raise

            def _get_searchable_fields(self) -> List[str]:
                """Get searchable fields for the table"""
                # This could be enhanced to read from table schema
                return ['name', 'title', 'description', 'email', 'phone', 'address']

        # Set the class name dynamically
        GeneratedController.__name__ = f"{table_name.title()}Controller"
        GeneratedController.__qualname__ = f"{table_name.title()}Controller"

        return GeneratedController

    def get_controller(self, table_name: str) -> Optional[Any]:
        """Get a controller instance for a table"""
        return self.generated_controllers.get(table_name)

    def get_all_controllers(self) -> Dict[str, Any]:
        """Get all generated controllers"""
        return self.generated_controllers.copy()

    def get_route_statistics(self) -> Dict[str, Any]:
        """Get statistics about generated routes"""
        routes = route_manager.get_all_routes()
        modules = {}

        for route in routes:
            module = route.get('module', 'unknown')
            if module not in modules:
                modules[module] = 0
            modules[module] += 1

        return {
            'total_routes': len(routes),
            'modules': modules,
            'tables_with_controllers': len(self.generated_controllers),
            'generated_controllers': list(self.generated_controllers.keys())
        }

# Global instance
crud_route_generator = CRUDRouteGenerator()

# Utility functions
def generate_routes_for_table(table_name: str, module: str = 'crud') -> Dict[str, Any]:
    """Utility function to generate routes for a single table"""
    return crud_route_generator.generate_crud_routes(table_name, module)

def generate_all_routes() -> Dict[str, Any]:
    """Utility function to generate routes for all tables"""
    return crud_route_generator.generate_all_crud_routes()

def get_controller_for_table(table_name: str) -> Optional[Any]:
    """Get controller instance for a table"""
    return crud_route_generator.get_controller(table_name)

def get_route_statistics() -> Dict[str, Any]:
    """Get route statistics"""
    return crud_route_generator.get_route_statistics()
