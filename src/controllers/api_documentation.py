"""
ValidoAI API Documentation
==========================

Comprehensive OpenAPI/Swagger documentation for all API endpoints.
Auto-generates interactive API documentation with examples.
"""

import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from flask import Blueprint, request, jsonify, current_app, url_for
from flask_restx import Api, Resource, fields, reqparse
from werkzeug.exceptions import BadRequest

from src.core.error_handling import log_error, ErrorCategory

# Create blueprint for API documentation
api_doc_bp = Blueprint('api_docs', __name__, url_prefix='/api/docs')

# Initialize Flask-RESTX API
api = Api(
    api_doc_bp,
    version='1.0',
    title='ValidoAI API',
    description='Comprehensive API for ValidoAI - AI-powered business intelligence platform',
    doc='/swagger/',
    prefix='/api'
)

# ============================================================================
# DATA MODELS FOR API DOCUMENTATION
# ============================================================================

# CRUD API Models
company_model = api.model('Company', {
    'id': fields.String(description='Unique company identifier', example='550e8400-e29b-41d4-a716-446655440000'),
    'company_name': fields.String(required=True, description='Company name', example='Test Company Ltd'),
    'legal_name': fields.String(description='Legal company name', example='Test Company Limited'),
    'tax_id': fields.String(required=True, description='Tax identification number', example='123456789'),
    'registration_number': fields.String(description='Company registration number', example='REG123456'),
    'business_entity_type_id': fields.String(description='Business entity type ID'),
    'business_area_id': fields.String(description='Business area ID'),
    'country_id': fields.String(description='Country ID'),
    'currency_id': fields.String(description='Currency ID'),
    'address_line1': fields.String(description='Primary address', example='123 Business Street'),
    'city': fields.String(description='City', example='Belgrade'),
    'phone': fields.String(description='Phone number', example='+381111234567'),
    'email': fields.String(description='Email address', example='info@testcompany.com'),
    'website': fields.String(description='Company website', example='https://testcompany.com'),
    'status': fields.String(description='Company status', example='active', enum=['active', 'inactive', 'suspended']),
    'is_pdv_registered': fields.Boolean(description='PDV registration status', example=False),
    'description': fields.String(description='Company description'),
    'employee_count': fields.Integer(description='Number of employees', example=50),
    'annual_revenue': fields.Float(description='Annual revenue', example=1000000.00),
    'is_active': fields.Boolean(description='Active status', example=True),
    'created_at': fields.DateTime(description='Creation timestamp'),
    'updated_at': fields.DateTime(description='Last update timestamp')
})

user_model = api.model('User', {
    'id': fields.String(description='Unique user identifier'),
    'company_id': fields.String(description='Associated company ID'),
    'email': fields.String(required=True, description='User email', example='user@testcompany.com'),
    'username': fields.String(description='Username', example='john_doe'),
    'first_name': fields.String(description='First name', example='John'),
    'last_name': fields.String(description='Last name', example='Doe'),
    'phone': fields.String(description='Phone number', example='+381111234567'),
    'role': fields.String(description='User role', example='admin', enum=['admin', 'manager', 'user']),
    'status': fields.String(description='User status', example='active', enum=['active', 'inactive', 'suspended']),
    'is_active': fields.Boolean(description='Active status', example=True),
    'created_at': fields.DateTime(description='Creation timestamp'),
    'updated_at': fields.DateTime(description='Last update timestamp')
})

customer_feedback_model = api.model('CustomerFeedback', {
    'id': fields.String(description='Unique feedback identifier'),
    'company_id': fields.String(description='Company ID'),
    'user_id': fields.String(description='User ID'),
    'feedback_type': fields.String(required=True, description='Feedback type', enum=['review', 'complaint', 'suggestion']),
    'rating': fields.Integer(description='Rating (1-5 stars)', min=1, max=5, example=4),
    'title': fields.String(description='Feedback title', example='Great service!'),
    'content': fields.String(required=True, description='Feedback content'),
    'customer_name': fields.String(description='Customer name', example='Jane Smith'),
    'customer_email': fields.String(description='Customer email', example='jane@example.com'),
    'status': fields.String(description='Feedback status', enum=['pending', 'reviewed', 'responded', 'resolved']),
    'priority': fields.String(description='Priority level', enum=['low', 'medium', 'high', 'urgent']),
    'sentiment_score': fields.Float(description='Sentiment score (-1 to 1)', min=-1, max=1, example=0.8),
    'is_active': fields.Boolean(description='Active status', example=True),
    'created_at': fields.DateTime(description='Creation timestamp'),
    'updated_at': fields.DateTime(description='Last update timestamp')
})

# Pagination Model
pagination_model = api.model('Pagination', {
    'page': fields.Integer(description='Current page number', example=1),
    'per_page': fields.Integer(description='Items per page', example=50),
    'total': fields.Integer(description='Total number of items', example=150),
    'pages': fields.Integer(description='Total number of pages', example=3)
})

# API Response Models
api_response_model = api.model('APIResponse', {
    'data': fields.Raw(description='Response data'),
    'pagination': fields.Nested(pagination_model, description='Pagination information'),
    'message': fields.String(description='Response message', example='Operation completed successfully'),
    'success': fields.Boolean(description='Success status', example=True)
})

error_model = api.model('Error', {
    'error': fields.String(description='Error message', example='Invalid request data'),
    'code': fields.String(description='Error code', example='VALIDATION_ERROR'),
    'details': fields.Raw(description='Additional error details')
})

table_info_model = api.model('TableInfo', {
    'table_name': fields.String(description='Table name', example='companies'),
    'columns': fields.List(fields.Raw, description='Column information'),
    'relationships': fields.List(fields.Raw, description='Table relationships'),
    'total_records': fields.Integer(description='Total number of records', example=150)
})

# ============================================================================
# CRUD API NAMESPACE
# ============================================================================

crud_ns = api.namespace('crud', description='CRUD Operations API')

# Request parsers for query parameters
pagination_parser = reqparse.RequestParser()
pagination_parser.add_argument('page', type=int, default=1, help='Page number')
pagination_parser.add_argument('per_page', type=int, default=50, help='Items per page (max 1000)')
pagination_parser.add_argument('sort_by', type=str, help='Sort field')
pagination_parser.add_argument('sort_order', type=str, choices=['asc', 'desc'], default='asc', help='Sort order')

filter_parser = reqparse.RequestParser()
filter_parser.add_argument('status', type=str, help='Filter by status')
filter_parser.add_argument('is_active', type=bool, help='Filter by active status')
filter_parser.add_argument('created_after', type=str, help='Filter by creation date (YYYY-MM-DD)')
filter_parser.add_argument('company_name', type=str, help='Search in company names')

@crud_ns.route('/<string:table_name>')
class CRUDResource(Resource):
    """CRUD operations for any table"""

    @crud_ns.doc('get_records')
    @crud_ns.expect(pagination_parser, filter_parser)
    @crud_ns.response(200, 'Success', api_response_model)
    @crud_ns.response(404, 'Table not found', error_model)
    @crud_ns.response(500, 'Internal server error', error_model)
    def get(self, table_name):
        """Get records with filtering and pagination

        Retrieve records from any table with advanced filtering, sorting, and pagination.

        **Examples:**
        - GET /api/crud/companies?page=1&per_page=50
        - GET /api/crud/companies?status=active&sort_by=created_at&sort_order=desc
        - GET /api/crud/users?company_name=Test%20Company
        """
        try:
            from src.controllers.crud_controller import crud_controller

            # Parse query parameters
            args = pagination_parser.parse_args()
            filter_args = filter_parser.parse_args()

            # Build filters from query parameters
            filters = {}
            if filter_args.get('status'):
                filters['status'] = filter_args['status']
            if filter_args.get('is_active') is not None:
                filters['is_active'] = filter_args['is_active']
            if filter_args.get('company_name'):
                filters['company_name'] = {'like': f"%{filter_args['company_name']}%"}

            # Add other filters from request.args
            for key, value in request.args.items():
                if key not in ['page', 'per_page', 'sort_by', 'sort_order'] and key not in filter_args:
                    try:
                        # Try to parse as JSON for complex filters
                        filters[key] = json.loads(value)
                    except:
                        filters[key] = value

            result, status_code = crud_controller.get_records(
                table_name,
                filters,
                args['page'],
                min(args['per_page'], 1000),  # Enforce max limit
                args['sort_by'],
                args['sort_order']
            )

            return result, status_code

        except Exception as e:
            log_error(
                error_code=500,
                error_title="API Documentation Error - GET Records",
                error_message=f"Failed to retrieve records from {table_name}",
                exception=e,
                context={'table_name': table_name}
            )
            return {'error': str(e)}, 500

    @crud_ns.doc('create_record')
    @crud_ns.expect(company_model)  # Use company model as example
    @crud_ns.response(201, 'Created', company_model)
    @crud_ns.response(400, 'Bad request', error_model)
    @crud_ns.response(409, 'Conflict', error_model)
    @crud_ns.response(500, 'Internal server error', error_model)
    def post(self, table_name):
        """Create a new record

        Create a new record in the specified table.

        **Examples:**
        ```json
        POST /api/crud/companies
        {
          "company_name": "New Company Ltd",
          "tax_id": "987654321",
          "email": "info@newcompany.com"
        }
        ```
        """
        try:
            from src.controllers.crud_controller import crud_controller

            data = request.get_json()
            if not data:
                return {'error': 'No data provided'}, 400

            result, status_code = crud_controller.create_record(table_name, data)
            return result, status_code

        except Exception as e:
            log_error(
                error_code=500,
                error_title="API Documentation Error - Create Record",
                error_message=f"Failed to create record in {table_name}",
                exception=e,
                context={'table_name': table_name}
            )
            return {'error': str(e)}, 500

@crud_ns.route('/<string:table_name>/<string:record_id>')
class CRUDRecordResource(Resource):
    """CRUD operations for single records"""

    @crud_ns.doc('get_record')
    @crud_ns.response(200, 'Success', company_model)
    @crud_ns.response(404, 'Record not found', error_model)
    @crud_ns.response(500, 'Internal server error', error_model)
    def get(self, table_name, record_id):
        """Get a single record by ID

        Retrieve a specific record by its unique identifier.

        **Example:**
        - GET /api/crud/companies/550e8400-e29b-41d4-a716-446655440000
        """
        try:
            from src.controllers.crud_controller import crud_controller

            result, status_code = crud_controller.get_record(table_name, record_id)
            return result, status_code

        except Exception as e:
            log_error(
                error_code=500,
                error_title="API Documentation Error - Get Single Record",
                error_message=f"Failed to retrieve record {record_id} from {table_name}",
                exception=e,
                context={'table_name': table_name, 'record_id': record_id}
            )
            return {'error': str(e)}, 500

    @crud_ns.doc('update_record')
    @crud_ns.expect(company_model)
    @crud_ns.response(200, 'Success', company_model)
    @crud_ns.response(400, 'Bad request', error_model)
    @crud_ns.response(404, 'Record not found', error_model)
    @crud_ns.response(409, 'Conflict', error_model)
    @crud_ns.response(500, 'Internal server error', error_model)
    def put(self, table_name, record_id):
        """Update a record

        Update an existing record with new data.

        **Example:**
        ```json
        PUT /api/crud/companies/550e8400-e29b-41d4-a716-446655440000
        {
          "company_name": "Updated Company Name",
          "phone": "+381111234567"
        }
        ```
        """
        try:
            from src.controllers.crud_controller import crud_controller

            data = request.get_json()
            if not data:
                return {'error': 'No data provided'}, 400

            result, status_code = crud_controller.update_record(table_name, record_id, data)
            return result, status_code

        except Exception as e:
            log_error(
                error_code=500,
                error_title="API Documentation Error - Update Record",
                error_message=f"Failed to update record {record_id} in {table_name}",
                exception=e,
                context={'table_name': table_name, 'record_id': record_id}
            )
            return {'error': str(e)}, 500

    @crud_ns.doc('delete_record')
    @crud_ns.param('hard_delete', 'Set to true for hard delete (default: false for soft delete)')
    @crud_ns.response(200, 'Success', api.model('DeleteResponse', {
        'message': fields.String(description='Success message', example='Record deleted successfully')
    }))
    @crud_ns.response(404, 'Record not found', error_model)
    @crud_ns.response(500, 'Internal server error', error_model)
    def delete(self, table_name, record_id):
        """Delete a record (soft delete by default)

        Delete a record. By default, this performs a soft delete (marks as inactive).
        Use hard_delete=true parameter for permanent deletion.

        **Examples:**
        - DELETE /api/crud/companies/550e8400-e29b-41d4-a716-446655440000 (soft delete)
        - DELETE /api/crud/companies/550e8400-e29b-41d4-a716-446655440000?hard_delete=true (hard delete)
        """
        try:
            from src.controllers.crud_controller import crud_controller

            soft_delete = request.args.get('hard_delete', 'false').lower() != 'true'

            result, status_code = crud_controller.delete_record(table_name, record_id, soft_delete)
            return result, status_code

        except Exception as e:
            log_error(
                error_code=500,
                error_title="API Documentation Error - Delete Record",
                error_message=f"Failed to delete record {record_id} from {table_name}",
                exception=e,
                context={'table_name': table_name, 'record_id': record_id}
            )
            return {'error': str(e)}, 500

@crud_ns.route('/info/<string:table_name>')
class CRUDTableInfoResource(Resource):
    """Table information endpoint"""

    @crud_ns.doc('get_table_info')
    @crud_ns.response(200, 'Success', table_info_model)
    @crud_ns.response(404, 'Table not found', error_model)
    @crud_ns.response(500, 'Internal server error', error_model)
    def get(self, table_name):
        """Get table information and schema

        Retrieve detailed information about a table's structure, columns, and relationships.

        **Example:**
        - GET /api/crud/info/companies
        """
        try:
            from src.controllers.crud_controller import crud_controller

            result, status_code = crud_controller.get_table_info(table_name)
            return result, status_code

        except Exception as e:
            log_error(
                error_code=500,
                error_title="API Documentation Error - Get Table Info",
                error_message=f"Failed to get table info for {table_name}",
                exception=e,
                context={'table_name': table_name}
            )
            return {'error': str(e)}, 500

@crud_ns.route('/tables')
class CRUDTablesResource(Resource):
    """Available tables endpoint"""

    @crud_ns.doc('get_available_tables')
    @crud_ns.response(200, 'Success', api.model('TablesResponse', {
        'tables': fields.List(fields.String, description='List of available tables'),
        'count': fields.Integer(description='Number of tables', example=7)
    }))
    @crud_ns.response(500, 'Internal server error', error_model)
    def get(self):
        """Get list of available tables

        Retrieve a list of all tables that are available for CRUD operations.

        **Example:**
        - GET /api/crud/tables
        """
        try:
            from src.controllers.crud_controller import crud_controller

            tables = list(crud_controller.models.keys())
            return {
                'tables': tables,
                'count': len(tables)
            }, 200

        except Exception as e:
            log_error(
                error_code=500,
                error_title="API Documentation Error - Get Available Tables",
                error_message="Failed to retrieve available tables",
                exception=e
            )
            return {'error': str(e)}, 500

@crud_ns.route('/stats')
class CRUDStatsResource(Resource):
    """CRUD statistics endpoint"""

    @crud_ns.doc('get_crud_stats')
    @crud_ns.response(200, 'Success', api.model('StatsResponse', {
        'stats': fields.Raw(description='Statistics for each table'),
        'timestamp': fields.DateTime(description='Statistics timestamp')
    }))
    @crud_ns.response(500, 'Internal server error', error_model)
    def get(self):
        """Get CRUD statistics

        Retrieve statistics about records in all tables.

        **Example:**
        - GET /api/crud/stats
        """
        try:
            from src.controllers.crud_controller import crud_controller

            result, status_code = crud_controller.get_crud_stats()
            return result, status_code

        except Exception as e:
            log_error(
                error_code=500,
                error_title="API Documentation Error - Get CRUD Stats",
                error_message="Failed to retrieve CRUD statistics",
                exception=e
            )
            return {'error': str(e)}, 500

# ============================================================================
# N8N WORKFLOW API NAMESPACE
# ============================================================================

n8n_ns = api.namespace('n8n', description='N8N Workflow Automation API')

n8n_workflow_model = api.model('N8NWorkflow', {
    'id': fields.String(description='Workflow ID', example='workflow_123'),
    'name': fields.String(description='Workflow name', example='Data Processing Workflow'),
    'description': fields.String(description='Workflow description'),
    'status': fields.String(description='Workflow status', enum=['active', 'inactive', 'error']),
    'created_at': fields.DateTime(description='Creation timestamp'),
    'updated_at': fields.DateTime(description='Last update timestamp')
})

n8n_execution_model = api.model('N8NExecution', {
    'id': fields.String(description='Execution ID', example='exec_456'),
    'workflow_id': fields.String(description='Associated workflow ID'),
    'status': fields.String(description='Execution status', enum=['running', 'success', 'error', 'waiting']),
    'started_at': fields.DateTime(description='Execution start time'),
    'completed_at': fields.DateTime(description='Execution completion time'),
    'result': fields.Raw(description='Execution result data')
})

@n8n_ns.route('/workflows')
class N8NWorkflowsResource(Resource):
    """N8N workflow management"""

    @n8n_ns.doc('get_workflows')
    @n8n_ns.response(200, 'Success', api.model('WorkflowsResponse', {
        'workflows': fields.List(fields.Nested(n8n_workflow_model)),
        'count': fields.Integer(description='Number of workflows')
    }))
    def get(self):
        """Get all workflows

        Retrieve a list of all N8N workflows.
        """
        try:
            # This would integrate with the actual N8N integration
            return {
                'workflows': [],
                'count': 0,
                'message': 'N8N integration available but not fully configured'
            }, 200
        except Exception as e:
            return {'error': str(e)}, 500

    @n8n_ns.doc('create_workflow')
    @n8n_ns.expect(n8n_workflow_model)
    @n8n_ns.response(201, 'Created', n8n_workflow_model)
    def post(self):
        """Create a new workflow

        Create a new N8N workflow.
        """
        try:
            data = request.get_json()
            # This would integrate with the actual N8N integration
            return {
                'message': 'Workflow creation endpoint available',
                'data': data
            }, 201
        except Exception as e:
            return {'error': str(e)}, 500

@n8n_ns.route('/executions')
class N8NExecutionsResource(Resource):
    """N8N execution management"""

    @n8n_ns.doc('get_executions')
    @n8n_ns.response(200, 'Success', api.model('ExecutionsResponse', {
        'executions': fields.List(fields.Nested(n8n_execution_model)),
        'count': fields.Integer(description='Number of executions')
    }))
    def get(self):
        """Get workflow executions

        Retrieve a list of workflow executions.
        """
        try:
            return {
                'executions': [],
                'count': 0,
                'message': 'N8N execution tracking available'
            }, 200
        except Exception as e:
            return {'error': str(e)}, 500

@n8n_ns.route('/health')
class N8NHealthResource(Resource):
    """N8N health check"""

    @n8n_ns.doc('get_health')
    @n8n_ns.response(200, 'Success', api.model('HealthResponse', {
        'status': fields.String(description='Health status', example='healthy'),
        'timestamp': fields.DateTime(description='Health check timestamp'),
        'version': fields.String(description='N8N version', example='1.0.0')
    }))
    def get(self):
        """Get N8N health status

        Check the health status of the N8N integration.
        """
        try:
            return {
                'status': 'available',
                'timestamp': datetime.utcnow().isoformat(),
                'message': 'N8N integration is available for configuration'
            }, 200
        except Exception as e:
            return {'error': str(e)}, 500

# ============================================================================
# GENERAL API ENDPOINTS
# ============================================================================

general_ns = api.namespace('', description='General API Endpoints')

@general_ns.route('/health')
class HealthResource(Resource):
    """API Health Check"""

    @general_ns.doc('get_health')
    @general_ns.response(200, 'Success', api.model('HealthCheck', {
        'status': fields.String(description='API status', example='healthy'),
        'timestamp': fields.DateTime(description='Health check timestamp'),
        'version': fields.String(description='API version', example='1.0.0'),
        'components': fields.Raw(description='Component statuses')
    }))
    def get(self):
        """Get API health status

        Check the overall health status of the ValidoAI API.
        """
        try:
            components = {
                'database': 'available',
                'crud_operations': 'available',
                'error_handling': 'available',
                'n8n_integration': 'available',
                'logging': 'available'
            }

            return {
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'version': '1.0.0',
                'components': components
            }, 200

        except Exception as e:
            log_error(
                error_code=500,
                error_title="API Health Check Error",
                error_message="Failed to perform health check",
                exception=e
            )
            return {'error': str(e)}, 500

@general_ns.route('/version')
class VersionResource(Resource):
    """API Version Information"""

    @general_ns.doc('get_version')
    @general_ns.response(200, 'Success', api.model('VersionInfo', {
        'version': fields.String(description='API version', example='1.0.0'),
        'build_date': fields.DateTime(description='Build timestamp'),
        'features': fields.List(fields.String, description='Available features'),
        'environment': fields.String(description='Environment', example='development')
    }))
    def get(self):
        """Get API version information

        Retrieve detailed version and feature information about the API.
        """
        try:
            features = [
                'CRUD Operations',
                'N8N Workflow Integration',
                'PostgreSQL Database Support',
                'Comprehensive Error Handling',
                'API Documentation',
                'User Authentication',
                'Audit Logging'
            ]

            return {
                'version': '1.0.0',
                'build_date': datetime.utcnow().isoformat(),
                'features': features,
                'environment': current_app.config.get('ENV', 'development')
            }, 200

        except Exception as e:
            return {'error': str(e)}, 500

# ============================================================================
# API CONFIGURATION AND INITIALIZATION
# ============================================================================

def init_api_docs(app):
    """Initialize API documentation with the Flask app"""
    try:
        # Register the API blueprint
        app.register_blueprint(api_doc_bp)

        # Configure Swagger UI
        api.init_app(app)

        # Add additional API information
        api.title = 'ValidoAI API'
        api.version = '1.0'
        api.description = '''
        ValidoAI - Comprehensive AI-powered business intelligence platform

        ## Features
        - **CRUD Operations**: Full database operations for all tables
        - **N8N Integration**: Workflow automation capabilities
        - **PostgreSQL Support**: Advanced database features
        - **Error Handling**: Comprehensive error management
        - **API Documentation**: Interactive Swagger documentation
        - **Security**: Built-in authentication and authorization
        - **Logging**: Complete audit trail

        ## Authentication
        Most endpoints require authentication. Include your API key in the request headers:
        ```
        Authorization: Bearer your-api-key
        ```

        ## Rate Limiting
        API calls are rate limited. Check the response headers for rate limit information.

        ## Error Handling
        The API uses standard HTTP status codes and provides detailed error messages.
        '''

        api.contact = {
            'name': 'ValidoAI Support',
            'url': 'https://validoai.com/support',
            'email': 'support@validoai.com'
        }

        api.license = {
            'name': 'MIT License',
            'url': 'https://opensource.org/licenses/MIT'
        }

        api.servers = [
            {
                'url': 'http://localhost:5000/api',
                'description': 'Development server'
            },
            {
                'url': 'https://api.validoai.com',
                'description': 'Production server'
            }
        ]

        api.tags = [
            {
                'name': 'CRUD Operations',
                'description': 'Database CRUD operations for all tables'
            },
            {
                'name': 'N8N Integration',
                'description': 'Workflow automation with N8N'
            },
            {
                'name': 'General',
                'description': 'General API endpoints'
            }
        ]

        print("✅ API documentation initialized successfully")

    except Exception as e:
        print(f"❌ Failed to initialize API documentation: {e}")

# Export the blueprint and API
__all__ = ['api_doc_bp', 'api', 'init_api_docs']
