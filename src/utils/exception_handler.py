import logging
import traceback
from typing import Dict, Any, Optional, Union
from functools import wraps
from flask import jsonify, request
from werkzeug.exceptions import HTTPException
import json
from .error_logger import error_logger, handle_application_error

logger = logging.getLogger(__name__)

class ValidoAIException(Exception):
    """Base exception class for ValidoAI application"""
    
    def __init__(self, message: str, error_code: str = "INTERNAL_ERROR", 
                 status_code: int = 500, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for JSON response"""
        return {
            "success": False,
            "error": {
                "code": self.error_code,
                "message": self.message,
                "details": self.details,
                "timestamp": self.details.get("timestamp"),
                "request_id": self.details.get("request_id")
            }
        }

class ValidationError(ValidoAIException):
    """Exception for validation errors"""
    
    def __init__(self, message: str, field: Optional[str] = None, 
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "VALIDATION_ERROR", 400, details)
        if field:
            self.details["field"] = field

class AuthenticationError(ValidoAIException):
    """Exception for authentication errors"""
    
    def __init__(self, message: str = "Authentication required", 
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "AUTHENTICATION_ERROR", 401, details)

class AuthorizationError(ValidoAIException):
    """Exception for authorization errors"""
    
    def __init__(self, message: str = "Insufficient permissions", 
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "AUTHORIZATION_ERROR", 403, details)

class NotFoundError(ValidoAIException):
    """Exception for resource not found errors"""
    
    def __init__(self, message: str = "Resource not found", 
                 resource_type: Optional[str] = None,
                 resource_id: Optional[str] = None,
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "NOT_FOUND_ERROR", 404, details)
        if resource_type:
            self.details["resource_type"] = resource_type
        if resource_id:
            self.details["resource_id"] = resource_id

class ConflictError(ValidoAIException):
    """Exception for resource conflict errors"""
    
    def __init__(self, message: str = "Resource conflict", 
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "CONFLICT_ERROR", 409, details)

class RateLimitError(ValidoAIException):
    """Exception for rate limiting errors"""
    
    def __init__(self, message: str = "Rate limit exceeded", 
                 retry_after: Optional[int] = None,
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "RATE_LIMIT_ERROR", 429, details)
        if retry_after:
            self.details["retry_after"] = retry_after

class ExternalServiceError(ValidoAIException):
    """Exception for external service errors"""
    
    def __init__(self, message: str, service: str, 
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "EXTERNAL_SERVICE_ERROR", 502, details)
        self.details["service"] = service

class DatabaseError(ValidoAIException):
    """Exception for database errors"""
    
    def __init__(self, message: str, operation: Optional[str] = None,
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "DATABASE_ERROR", 500, details)
        if operation:
            self.details["operation"] = operation

class ConfigurationError(ValidoAIException):
    """Exception for configuration errors"""
    
    def __init__(self, message: str, config_key: Optional[str] = None,
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "CONFIGURATION_ERROR", 500, details)
        if config_key:
            self.details["config_key"] = config_key

class FileProcessingError(ValidoAIException):
    """Exception for file processing errors"""
    
    def __init__(self, message: str, file_path: Optional[str] = None,
                 operation: Optional[str] = None,
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "FILE_PROCESSING_ERROR", 500, details)
        if file_path:
            self.details["file_path"] = file_path
        if operation:
            self.details["operation"] = operation

class AIModelError(ValidoAIException):
    """Exception for AI model errors"""
    
    def __init__(self, message: str, model_name: Optional[str] = None,
                 operation: Optional[str] = None,
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "AI_MODEL_ERROR", 500, details)
        if model_name:
            self.details["model_name"] = model_name
        if operation:
            self.details["operation"] = operation

def create_error_response(error: Exception, include_details: bool = False) -> Dict[str, Any]:
    """
    Create a standardized error response
    
    Args:
        error: The exception that occurred
        include_details: Whether to include detailed error information
        
    Returns:
        Dict containing the error response
    """
    # Log the error and get UUID
    error_uuid = error_logger.log_error(error, {
        'include_details': include_details,
        'request_path': request.path if request else None,
        'request_method': request.method if request else None
    })
    
    # Get error summary for user display
    error_summary = error_logger.get_error_summary(error_uuid)
    
    # Base error response
    response = {
        "success": False,
        "error": {
            "message": "An error occurred while processing your request.",
            "error_id": error_uuid,
            "type": error_summary.get('error_type', 'Unknown Error') if error_summary else 'Unknown Error',
            "timestamp": error_summary.get('created_at') if error_summary else None
        }
    }
    
    # Add detailed information for debugging (only for admins or in debug mode)
    if include_details and error_summary:
        response["error"]["details"] = {
            "error_code": error_summary.get('error_code'),
            "status_code": error_summary.get('status_code'),
            "request_path": error_summary.get('request_path')
        }
    
    # Handle specific exception types
    if isinstance(error, ValidoAIException):
        response["error"]["message"] = error.message
        response["error"]["code"] = error.error_code
        response["error"]["details"] = error.details
    
    return response

def handle_exceptions(func):
    """Decorator to handle exceptions and log them"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # Log the error
            error_uuid = error_logger.log_error(e, {
                'function': func.__name__,
                'args': str(args),
                'kwargs': str(kwargs)
            })
            
            # Create error response
            error_response = create_error_response(e, include_details=False)
            
            # Return JSON response
            return jsonify(error_response), 500
    
    return wrapper

def handle_validation_errors(func):
    """Decorator to handle validation errors specifically"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValidationError as e:
            # Log validation errors
            error_uuid = error_logger.log_error(e, {
                'function': func.__name__,
                'error_type': 'validation'
            })
            
            response = {
                "success": False,
                "error": {
                    "message": e.message,
                    "error_id": error_uuid,
                    "code": "VALIDATION_ERROR",
                    "field": e.details.get("field"),
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            return jsonify(response), 400
        except Exception as e:
            # Handle other errors
            return handle_application_error(e)
    
    return wrapper

def handle_database_errors(func):
    """Decorator to handle database errors specifically"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except DatabaseError as e:
            # Log database errors
            error_uuid = error_logger.log_error(e, {
                'function': func.__name__,
                'error_type': 'database',
                'operation': e.details.get("operation")
            })
            
            response = {
                "success": False,
                "error": {
                    "message": "A database error occurred. Please try again later.",
                    "error_id": error_uuid,
                    "code": "DATABASE_ERROR",
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            return jsonify(response), 500
        except Exception as e:
            # Handle other errors
            return handle_application_error(e)
    
    return wrapper

def handle_ai_model_errors(func):
    """Decorator to handle AI model errors specifically"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except AIModelError as e:
            # Log AI model errors
            error_uuid = error_logger.log_error(e, {
                'function': func.__name__,
                'error_type': 'ai_model',
                'model_name': e.details.get("model_name"),
                'operation': e.details.get("operation")
            })
            
            response = {
                "success": False,
                "error": {
                    "message": "An AI model error occurred. Please try again later.",
                    "error_id": error_uuid,
                    "code": "AI_MODEL_ERROR",
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            return jsonify(response), 500
        except Exception as e:
            # Handle other errors
            return handle_application_error(e)
    
    return wrapper

def create_success_response(data: Any = None, message: str = "Success") -> Dict[str, Any]:
    """
    Create a standardized success response
    
    Args:
        data: The data to include in the response
        message: Success message
        
    Returns:
        Dict containing the success response
    """
    response = {
        "success": True,
        "message": message,
        "timestamp": datetime.now().isoformat()
    }
    
    if data is not None:
        response["data"] = data
    
    return response

def validate_required_fields(data: Dict[str, Any], required_fields: list) -> None:
    """
    Validate that required fields are present in the data
    
    Args:
        data: The data to validate
        required_fields: List of required field names
        
    Raises:
        ValidationError: If any required field is missing
    """
    missing_fields = []
    
    for field in required_fields:
        if field not in data or data[field] is None or data[field] == "":
            missing_fields.append(field)
    
    if missing_fields:
        raise ValidationError(
            f"Missing required fields: {', '.join(missing_fields)}",
            details={"missing_fields": missing_fields}
        )

def validate_field_type(data: Dict[str, Any], field: str, expected_type: type) -> None:
    """
    Validate that a field has the expected type
    
    Args:
        data: The data to validate
        field: The field name to validate
        expected_type: The expected type
        
    Raises:
        ValidationError: If the field has the wrong type
    """
    if field in data and not isinstance(data[field], expected_type):
        raise ValidationError(
            f"Field '{field}' must be of type {expected_type.__name__}",
            field=field,
            details={"expected_type": expected_type.__name__, "actual_type": type(data[field]).__name__}
        )

def validate_field_range(data: Dict[str, Any], field: str, min_value: Any = None, max_value: Any = None) -> None:
    """
    Validate that a field is within the specified range
    
    Args:
        data: The data to validate
        field: The field name to validate
        min_value: Minimum allowed value
        max_value: Maximum allowed value
        
    Raises:
        ValidationError: If the field is outside the allowed range
    """
    if field in data:
        value = data[field]
        
        if min_value is not None and value < min_value:
            raise ValidationError(
                f"Field '{field}' must be at least {min_value}",
                field=field,
                details={"min_value": min_value, "actual_value": value}
            )
        
        if max_value is not None and value > max_value:
            raise ValidationError(
                f"Field '{field}' must be at most {max_value}",
                field=field,
                details={"max_value": max_value, "actual_value": value}
            )

def sanitize_input(data: str) -> str:
    """
    Sanitize user input to prevent injection attacks
    
    Args:
        data: The input string to sanitize
        
    Returns:
        Sanitized string
    """
    if not isinstance(data, str):
        return str(data)
    
    # Remove potentially dangerous characters
    dangerous_chars = ['<', '>', '"', "'", '&', ';', '(', ')', '{', '}', '[', ']']
    sanitized = data
    
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, '')
    
    return sanitized.strip()

def validate_email(email: str) -> bool:
    """
    Validate email format
    
    Args:
        email: Email address to validate
        
    Returns:
        True if email is valid, False otherwise
    """
    import re
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone: str) -> bool:
    """
    Validate phone number format
    
    Args:
        phone: Phone number to validate
        
    Returns:
        True if phone is valid, False otherwise
    """
    import re
    
    # Remove all non-digit characters
    digits_only = re.sub(r'\D', '', phone)
    
    # Check if it's a valid length (7-15 digits)
    return 7 <= len(digits_only) <= 15

def validate_url(url: str) -> bool:
    """
    Validate URL format
    
    Args:
        url: URL to validate
        
    Returns:
        True if URL is valid, False otherwise
    """
    import re
    
    pattern = r'^https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?$'
    return re.match(pattern, url) is not None

# Import datetime for timestamp
from datetime import datetime
