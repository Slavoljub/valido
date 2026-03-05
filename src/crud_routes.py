"""
CRUD Routes for ValidoAI application
Provides RESTful CRUD operations for various models
"""

from flask import Blueprint, render_template, request, jsonify, current_app, abort
from functools import wraps
import logging
import time
from sqlalchemy.exc import SQLAlchemyError

# Setup logging
logger = logging.getLogger(__name__)

# Create blueprint
crud_bp = Blueprint('crud', __name__, url_prefix='/crud-operations')

# Decorator for error handling
def handle_errors(f):
    """Error handling decorator"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except SQLAlchemyError as e:
            logger.error(f"Database error in {f.__name__}: {str(e)}")
            return jsonify({
                'error': 'Database error',
                'status': 'error',
                'message': str(e) if current_app.debug else 'A database error occurred'
            }), 500
        except Exception as e:
            logger.error(f"Error in {f.__name__}: {str(e)}")
            return jsonify({
                'error': 'Internal server error',
                'status': 'error',
                'message': str(e) if current_app.debug else 'An error occurred'
            }), 500
    return decorated_function

# Company CRUD routes
@crud_bp.route('/companies')
@handle_errors
def companies_index():
    """List all companies"""
    return render_template('crud-operations/companies/index.html')

@crud_bp.route('/companies/create')
@handle_errors
def companies_create():
    """Create new company form"""
    return render_template('crud-operations/companies/create.html')

@crud_bp.route('/companies/<int:company_id>')
@handle_errors
def companies_view(company_id):
    """View company details"""
    try:
        from src.database_adapter import get_database_adapter
        
        db = get_database_adapter()
        
        # Get company by ID
        query = f"SELECT * FROM companies WHERE company_id = %s" if db.db_type == 'mysql' else "SELECT * FROM companies WHERE company_id = ?"
        companies = db.execute_query(query, (company_id,))
        
        if not companies:
            abort(404)
        
        company = companies[0]
        return render_template('crud-operations/companies/view.html', company=company)
    except Exception as e:
        logger.error(f"Error viewing company {company_id}: {e}")
        abort(500)

@crud_bp.route('/companies/<int:company_id>/edit')
@handle_errors
def companies_edit(company_id):
    """Edit company form"""
    try:
        from src.database_adapter import get_database_adapter
        
        db = get_database_adapter()
        
        # Get company by ID
        query = f"SELECT * FROM companies WHERE company_id = %s" if db.db_type == 'mysql' else "SELECT * FROM companies WHERE company_id = ?"
        companies = db.execute_query(query, (company_id,))
        
        if not companies:
            abort(404)
        
        company = companies[0]
        return render_template('crud-operations/companies/edit.html', company=company)
    except Exception as e:
        logger.error(f"Error editing company {company_id}: {e}")
        abort(500)

# API endpoints for companies
@crud_bp.route('/api/companies', methods=['GET'])
@handle_errors
def api_companies_list():
    """Get all companies"""
    try:
        from src.database_adapter import get_database_adapter
        
        db = get_database_adapter()
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '')
        sort_by = request.args.get('sort_by', 'company_id')
        sort_order = request.args.get('sort_order', 'asc')
        
        # Build query
        base_query = "SELECT * FROM companies"
        where_clause = ""
        params = []
        
        # Apply search filter
        if search:
            if db.db_type == 'mysql':
                where_clause = " WHERE name LIKE %s OR tax_id LIKE %s OR registration_number LIKE %s"
            else:
                where_clause = " WHERE name LIKE ? OR tax_id LIKE ? OR registration_number LIKE ?"
            params = [f'%{search}%', f'%{search}%', f'%{search}%']
        
        # Apply sorting
        order_clause = f" ORDER BY {sort_by} {sort_order.upper()}"
        
        # Apply pagination
        if db.db_type == 'mysql':
            limit_clause = f" LIMIT {per_page} OFFSET {(page - 1) * per_page}"
        else:
            limit_clause = f" LIMIT {per_page} OFFSET {(page - 1) * per_page}"
        
        # Execute query
        query = base_query + where_clause + order_clause + limit_clause
        companies = db.execute_query(query, tuple(params) if params else None)
        
        # Get total count
        count_query = "SELECT COUNT(*) as count FROM companies" + where_clause
        count_result = db.execute_query(count_query, tuple(params) if params else None)
        total_count = count_result[0]['count'] if count_result else 0
        
        # Calculate pagination info
        total_pages = (total_count + per_page - 1) // per_page
        
        return jsonify({
            'status': 'success',
            'data': companies,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total_count,
                'pages': total_pages
            }
        })
    except Exception as e:
        logger.error(f"Error listing companies: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e) if current_app.debug else 'An error occurred'
        }), 500

@crud_bp.route('/api/companies/<int:company_id>', methods=['GET'])
@handle_errors
def api_companies_get(company_id):
    """Get company by ID"""
    try:
        from src.database_adapter import get_database_adapter
        
        db = get_database_adapter()
        
        # Get company by ID
        query = f"SELECT * FROM companies WHERE company_id = %s" if db.db_type == 'mysql' else "SELECT * FROM companies WHERE company_id = ?"
        companies = db.execute_query(query, (company_id,))
        
        if not companies:
            return jsonify({
                'status': 'error',
                'message': f'Company with ID {company_id} not found'
            }), 404
        
        return jsonify({
            'status': 'success',
            'data': companies[0]
        })
    except Exception as e:
        logger.error(f"Error getting company {company_id}: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e) if current_app.debug else 'An error occurred'
        }), 500

@crud_bp.route('/api/companies', methods=['POST'])
@handle_errors
def api_companies_create():
    """Create new company"""
    try:
        from src.database_adapter import get_database_adapter
        
        if not request.is_json:
            return jsonify({
                'status': 'error',
                'message': 'Content-Type must be application/json'
            }), 400
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'tax_id', 'registration_number']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({
                'status': 'error',
                'message': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
        
        # Create new company
        db = get_database_adapter()
        success = db.insert_record('companies', data)
        
        if not success:
            return jsonify({
                'status': 'error',
                'message': 'Failed to create company'
            }), 500
        
        # Get the created company
        query = f"SELECT * FROM companies WHERE tax_id = %s ORDER BY company_id DESC LIMIT 1" if db.db_type == 'mysql' else "SELECT * FROM companies WHERE tax_id = ? ORDER BY company_id DESC LIMIT 1"
        companies = db.execute_query(query, (data['tax_id'],))
        
        return jsonify({
            'status': 'success',
            'message': 'Company created successfully',
            'data': companies[0] if companies else data
        }), 201
    except Exception as e:
        logger.error(f"Error creating company: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e) if current_app.debug else 'An error occurred'
        }), 500

@crud_bp.route('/api/companies/<int:company_id>', methods=['PUT'])
@handle_errors
def api_companies_update(company_id):
    """Update company"""
    try:
        from src.database_adapter import get_database_adapter
        
        if not request.is_json:
            return jsonify({
                'status': 'error',
                'message': 'Content-Type must be application/json'
            }), 400
        
        data = request.get_json()
        
        # Find company
        db = get_database_adapter()
        query = f"SELECT * FROM companies WHERE company_id = %s" if db.db_type == 'mysql' else "SELECT * FROM companies WHERE company_id = ?"
        companies = db.execute_query(query, (company_id,))
        
        if not companies:
            return jsonify({
                'status': 'error',
                'message': f'Company with ID {company_id} not found'
            }), 404
        
        # Update company
        success = db.update_record('companies', company_id, data, 'company_id')
        
        if not success:
            return jsonify({
                'status': 'error',
                'message': 'Failed to update company'
            }), 500
        
        # Get updated company
        updated_companies = db.execute_query(query, (company_id,))
        
        return jsonify({
            'status': 'success',
            'message': 'Company updated successfully',
            'data': updated_companies[0] if updated_companies else data
        })
    except Exception as e:
        logger.error(f"Error updating company {company_id}: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e) if current_app.debug else 'An error occurred'
        }), 500

@crud_bp.route('/api/companies/<int:company_id>', methods=['DELETE'])
@handle_errors
def api_companies_delete(company_id):
    """Delete company"""
    try:
        from src.database_adapter import get_database_adapter
        
        # Find company
        db = get_database_adapter()
        query = f"SELECT * FROM companies WHERE company_id = %s" if db.db_type == 'mysql' else "SELECT * FROM companies WHERE company_id = ?"
        companies = db.execute_query(query, (company_id,))
        
        if not companies:
            return jsonify({
                'status': 'error',
                'message': f'Company with ID {company_id} not found'
            }), 404
        
        # Delete company
        success = db.delete_record('companies', company_id, 'company_id')
        
        if not success:
            return jsonify({
                'status': 'error',
                'message': 'Failed to delete company'
            }), 500
        
        return jsonify({
            'status': 'success',
            'message': f'Company with ID {company_id} deleted successfully'
        })
    except Exception as e:
        logger.error(f"Error deleting company {company_id}: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e) if current_app.debug else 'An error occurred'
        }), 500

# Database status endpoint
@crud_bp.route('/api/database/status', methods=['GET'])
@handle_errors
def api_database_status():
    """Get database status"""
    try:
        from src.database_adapter import get_database_adapter
        
        db = get_database_adapter()
        
        # Get database info
        info = db.get_database_info()
        
        # Get table counts
        tables = db.get_tables()
        table_counts = {}
        
        for table in tables:
            count = db.get_record_count(table)
            table_counts[table] = count
        
        return jsonify({
            'status': 'success',
            'data': {
                'database_info': info,
                'table_counts': table_counts,
                'total_tables': len(tables),
                'total_records': sum(table_counts.values())
            }
        })
    except Exception as e:
        logger.error(f"Error getting database status: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e) if current_app.debug else 'An error occurred'
        }), 500

# Database test endpoint
@crud_bp.route('/api/database/test', methods=['GET'])
@handle_errors
def api_database_test():
    """Test database connection"""
    try:
        from src.database_adapter import get_database_adapter
        
        db = get_database_adapter()
        
        # Test connection
        connection_ok = db.test_connection()
        
        # Test basic operations
        tables = db.get_tables()
        
        return jsonify({
            'status': 'success',
            'data': {
                'connection_ok': connection_ok,
                'database_type': db.db_type,
                'tables_available': len(tables),
                'tables': tables
            }
        })
    except Exception as e:
        logger.error(f"Error testing database: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e) if current_app.debug else 'An error occurred'
        }), 500

# Function to register CRUD routes
def register_crud_routes(app):
    """Register CRUD routes with the Flask app"""
    app.register_blueprint(crud_bp)
    logger.info("CRUD routes registered successfully")
