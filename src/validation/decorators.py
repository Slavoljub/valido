"""
Validation Decorators for Flask Routes and API Endpoints
Provides decorators for input validation, CSRF protection, and rate limiting
"""

import functools
import time
from typing import Dict, List, Any, Optional, Callable
from flask import request, jsonify, current_app, g
from werkzeug.exceptions import BadRequest, Unauthorized, TooManyRequests
import hashlib
import hmac
import secrets
import logging

from .validators import ValidationManager, ValidatorFactory, ValidationError

logger = logging.getLogger(__name__)

# Rate limiting storage (in production, use Redis or database)
rate_limit_storage = {}

def validate_input(validation_rules: Dict[str, Dict], language: str = 'en'):
    """
    Decorator for validating request input
    
    Args:
        validation_rules: Dictionary of field names and their validation rules
        language: Language for error messages ('en' or 'sr')
    
    Example:
        @validate_input({
            'email': {'type': 'email', 'required': True},
            'password': {'type': 'password', 'min_length': 8},
            'amount': {'type': 'currency', 'min_amount': 0}
        })
        def create_user():
            # Validated data available in g.validated_data
            pass
    """
    def decorator(f: Callable) -> Callable:
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            # Create validation manager
            validation_manager = ValidationManager()
            
            # Get request data
            if request.is_json:
                data = request.get_json() or {}
            elif request.form:
                data = request.form.to_dict()
            else:
                data = request.args.to_dict()
            
            # Add file data if present
            if request.files:
                for field_name, file in request.files.items():
                    data[field_name] = file
            
            # Create validators based on rules
            for field_name, rules in validation_rules.items():
                data_type = rules.get('type', 'string')
                validator_kwargs = {k: v for k, v in rules.items() if k != 'type'}
                
                try:
                    validator = ValidatorFactory.create_validator(data_type, **validator_kwargs)
                    validation_manager.add_validator(field_name, validator)
                except ValueError as e:
                    logger.error(f"Invalid validation rule for field {field_name}: {e}")
                    return jsonify({'error': f'Invalid validation rule for field {field_name}'}), 400
            
            # Validate data
            validated_data, errors = validation_manager.validate_data(data, language)
            
            if errors:
                error_response = {
                    'error': 'Validation failed',
                    'errors': errors,
                    'language': language
                }
                return jsonify(error_response), 400
            
            # Store validated data in Flask g object
            g.validated_data = validated_data
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def require_csrf_token():
    """
    Decorator for CSRF protection
    
    Requires a valid CSRF token in the request headers or form data
    """
    def decorator(f: Callable) -> Callable:
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            # Skip CSRF check for GET requests
            if request.method == 'GET':
                return f(*args, **kwargs)
            
            # Get CSRF token from headers or form
            csrf_token = request.headers.get('X-CSRF-Token') or request.form.get('csrf_token')
            
            if not csrf_token:
                logger.warning("CSRF token missing")
                return jsonify({'error': 'CSRF token required'}), 403
            
            # Validate CSRF token (implement your token validation logic here)
            if not validate_csrf_token(csrf_token):
                logger.warning("Invalid CSRF token")
                return jsonify({'error': 'Invalid CSRF token'}), 403
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def rate_limit(requests_per_minute: int = 60, key_func: Optional[Callable] = None):
    """
    Decorator for rate limiting
    
    Args:
        requests_per_minute: Maximum requests per minute
        key_func: Function to generate rate limit key (defaults to IP address)
    
    Example:
        @rate_limit(requests_per_minute=30)
        def api_endpoint():
            pass
    """
    def decorator(f: Callable) -> Callable:
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            # Generate rate limit key
            if key_func:
                key = key_func()
            else:
                key = request.remote_addr
            
            current_time = time.time()
            window_start = current_time - 60  # 1 minute window
            
            # Clean old entries
            if key in rate_limit_storage:
                rate_limit_storage[key] = [t for t in rate_limit_storage[key] if t > window_start]
            else:
                rate_limit_storage[key] = []
            
            # Check rate limit
            if len(rate_limit_storage[key]) >= requests_per_minute:
                logger.warning(f"Rate limit exceeded for {key}")
                return jsonify({'error': 'Rate limit exceeded'}), 429
            
            # Add current request
            rate_limit_storage[key].append(current_time)
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def sanitize_input():
    """
    Decorator for input sanitization
    
    Sanitizes request data to prevent XSS attacks
    """
    def decorator(f: Callable) -> Callable:
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            # Get request data
            if request.is_json:
                data = request.get_json() or {}
                sanitized_data = sanitize_dict(data)
                request._cached_json = sanitized_data
            elif request.form:
                data = request.form.to_dict()
                sanitized_data = sanitize_dict(data)
                # Update form data (this is a simplified approach)
                for key, value in sanitized_data.items():
                    if key in request.form:
                        request.form[key] = value
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def require_authentication():
    """
    Decorator for requiring authentication
    
    Checks if user is authenticated before allowing access
    """
    def decorator(f: Callable) -> Callable:
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            # Check if user is authenticated (implement your auth logic here)
            if not is_authenticated():
                logger.warning("Authentication required")
                return jsonify({'error': 'Authentication required'}), 401
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def require_permission(permission: str):
    """
    Decorator for requiring specific permissions
    
    Args:
        permission: Required permission string
    
    Example:
        @require_permission('admin')
        def admin_only():
            pass
    """
    def decorator(f: Callable) -> Callable:
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            # Check if user has required permission (implement your permission logic here)
            if not has_permission(permission):
                logger.warning(f"Permission '{permission}' required")
                return jsonify({'error': f'Permission {permission} required'}), 403
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def validate_file_upload(allowed_types: List[str], max_size: int):
    """
    Decorator for file upload validation
    
    Args:
        allowed_types: List of allowed MIME types
        max_size: Maximum file size in bytes
    
    Example:
        @validate_file_upload(['image/jpeg', 'image/png'], 5 * 1024 * 1024)
        def upload_image():
            pass
    """
    def decorator(f: Callable) -> Callable:
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            if 'file' not in request.files:
                return jsonify({'error': 'No file provided'}), 400
            
            file = request.files['file']
            
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            
            # Check file type
            if file.content_type not in allowed_types:
                return jsonify({'error': f'File type must be one of: {", ".join(allowed_types)}'}), 400
            
            # Check file size
            file.seek(0, 2)  # Seek to end
            file_size = file.tell()
            file.seek(0)  # Reset to beginning
            
            if file_size > max_size:
                return jsonify({'error': f'File size must be at most {max_size} bytes'}), 400
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def log_validation_errors():
    """
    Decorator for logging validation errors
    
    Logs validation errors for monitoring and debugging
    """
    def decorator(f: Callable) -> Callable:
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except ValidationError as e:
                logger.error(f"Validation error in {f.__name__}: {e}")
                raise
            except Exception as e:
                logger.error(f"Unexpected error in {f.__name__}: {e}")
                raise
        
        return decorated_function
    return decorator

def cache_response(timeout: int = 300):
    """
    Decorator for response caching
    
    Args:
        timeout: Cache timeout in seconds
    
    Example:
        @cache_response(timeout=600)
        def expensive_operation():
            pass
    """
    def decorator(f: Callable) -> Callable:
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            # Generate cache key
            cache_key = f"{f.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Check cache (implement your cache logic here)
            cached_response = get_cached_response(cache_key)
            if cached_response:
                return cached_response
            
            # Execute function
            response = f(*args, **kwargs)
            
            # Cache response
            cache_response_data(cache_key, response, timeout)
            
            return response
        
        return decorated_function
    return decorator

# Helper functions

def validate_csrf_token(token: str) -> bool:
    """
    Validate CSRF token
    
    Args:
        token: CSRF token to validate
    
    Returns:
        True if token is valid, False otherwise
    """
    # Implement your CSRF token validation logic here
    # This is a simplified example
    if not token:
        return False
    
    # Check if token exists in session or database
    # For now, just check if it's not empty
    return len(token) > 0

def sanitize_dict(data: Dict) -> Dict:
    """
    Sanitize dictionary data to prevent XSS
    
    Args:
        data: Dictionary to sanitize
    
    Returns:
        Sanitized dictionary
    """
    sanitized = {}
    
    for key, value in data.items():
        if isinstance(value, str):
            # Basic XSS prevention
            sanitized_value = value.replace('<script', '&lt;script')
            sanitized_value = sanitized_value.replace('javascript:', '')
            sanitized_value = sanitized_value.replace('onerror', '')
            sanitized_value = sanitized_value.replace('onload', '')
            sanitized[key] = sanitized_value
        elif isinstance(value, dict):
            sanitized[key] = sanitize_dict(value)
        elif isinstance(value, list):
            sanitized[key] = [sanitize_dict(item) if isinstance(item, dict) else item for item in value]
        else:
            sanitized[key] = value
    
    return sanitized

def is_authenticated() -> bool:
    """
    Check if user is authenticated
    
    Returns:
        True if user is authenticated, False otherwise
    """
    # Implement your authentication logic here
    # This is a placeholder
    return hasattr(g, 'user') and g.user is not None

def has_permission(permission: str) -> bool:
    """
    Check if user has required permission
    
    Args:
        permission: Permission to check
    
    Returns:
        True if user has permission, False otherwise
    """
    # Implement your permission logic here
    # This is a placeholder
    if not is_authenticated():
        return False
    
    # Check user permissions
    user_permissions = getattr(g.user, 'permissions', [])
    return permission in user_permissions

def get_cached_response(cache_key: str) -> Optional[Any]:
    """
    Get cached response
    
    Args:
        cache_key: Cache key
    
    Returns:
        Cached response or None
    """
    # Implement your cache logic here
    # This is a placeholder
    return None

def cache_response_data(cache_key: str, response: Any, timeout: int):
    """
    Cache response data
    
    Args:
        cache_key: Cache key
        response: Response to cache
        timeout: Cache timeout in seconds
    """
    # Implement your cache logic here
    # This is a placeholder
    pass

# Combined decorators for common use cases

def secure_api_endpoint(validation_rules: Dict = None, rate_limit_requests: int = 60):
    """
    Combined decorator for secure API endpoints
    
    Includes validation, CSRF protection, rate limiting, and input sanitization
    
    Args:
        validation_rules: Validation rules for input
        rate_limit_requests: Rate limit requests per minute
    
    Example:
        @secure_api_endpoint({
            'email': {'type': 'email', 'required': True},
            'password': {'type': 'password', 'min_length': 8}
        }, rate_limit_requests=30)
        def login():
            pass
    """
    def decorator(f: Callable) -> Callable:
        if validation_rules:
            f = validate_input(validation_rules)(f)
        
        f = require_csrf_token()(f)
        f = rate_limit(rate_limit_requests)(f)
        f = sanitize_input()(f)
        f = log_validation_errors()(f)
        
        return f
    return decorator

def authenticated_endpoint(validation_rules: Dict = None, permission: str = None):
    """
    Combined decorator for authenticated endpoints
    
    Includes authentication, validation, and optional permission checking
    
    Args:
        validation_rules: Validation rules for input
        permission: Required permission
    
    Example:
        @authenticated_endpoint({
            'amount': {'type': 'currency', 'min_amount': 0}
        }, permission='admin')
        def create_transaction():
            pass
    """
    def decorator(f: Callable) -> Callable:
        if validation_rules:
            f = validate_input(validation_rules)(f)
        
        f = require_authentication()(f)
        
        if permission:
            f = require_permission(permission)(f)
        
        f = log_validation_errors()(f)
        
        return f
    return decorator

def file_upload_endpoint(allowed_types: List[str], max_size: int, validation_rules: Dict = None):
    """
    Combined decorator for file upload endpoints
    
    Includes file validation, input validation, and rate limiting
    
    Args:
        allowed_types: Allowed file types
        max_size: Maximum file size
        validation_rules: Additional validation rules
    
    Example:
        @file_upload_endpoint(['image/jpeg', 'image/png'], 5 * 1024 * 1024, {
            'description': {'type': 'string', 'max_length': 500}
        })
        def upload_image():
            pass
    """
    def decorator(f: Callable) -> Callable:
        f = validate_file_upload(allowed_types, max_size)(f)
        
        if validation_rules:
            f = validate_input(validation_rules)(f)
        
        f = rate_limit(10)(f)  # Lower rate limit for file uploads
        f = log_validation_errors()(f)
        
        return f
    return decorator
