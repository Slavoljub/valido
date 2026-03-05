"""
Error Handling Utilities for ValidoAI
====================================
Centralized error handling functions to apply DRY principle
"""

import logging
import uuid
from datetime import datetime
from flask import render_template, jsonify
from typing import Optional, Dict, Any, Union

logger = logging.getLogger(__name__)


def handle_controller_import_error(
    controller_name: str,
    error: Exception,
    error_title: str = None,
    error_message_prefix: str = None,
    is_api_route: bool = False,
    custom_logger: Optional[logging.Logger] = None
) -> Union[str, tuple]:
    """
    Handle ImportError for controller loading with DRY principle
    
    Args:
        controller_name: Name of the controller that failed to import
        error: The ImportError exception
        error_title: Custom error title (defaults to "{Controller} Unavailable")
        error_message_prefix: Custom error message prefix (defaults to "The {controller} is not available.")
        is_api_route: Whether this is an API route (returns JSON) or page route (returns HTML)
        custom_logger: Optional custom logger instance
    
    Returns:
        Flask response (HTML template or JSON)
    """
    # Use custom logger if provided, otherwise use default
    log = custom_logger or logger
    
    # Generate default values if not provided
    if not error_title:
        error_title = f"{controller_name} Unavailable"
    
    if not error_message_prefix:
        error_message_prefix = f"The {controller_name.lower()} is not available."
    
    # Log the error
    log.error(f"{controller_name} not available: {error}")
    
    if is_api_route:
        # Return JSON response for API routes
        return jsonify({'error': f'{error_message_prefix}'}), 500
    else:
        # Return HTML template for page routes
        return render_template('errors/error.html', 
                             error_code=500,
                             error_title=error_title,
                             error_message=error_message_prefix,
                             error_stack_trace=str(error),
                             timestamp=datetime.now().isoformat(),
                             error_uuid=f"e500_{uuid.uuid4().hex[:8]}",
                             request_id=str(uuid.uuid4())), 500


def handle_generic_import_error(
    module_name: str,
    error: Exception,
    fallback_response: Any = None,
    custom_logger: Optional[logging.Logger] = None
) -> Any:
    """
    Handle generic ImportError with optional fallback
    
    Args:
        module_name: Name of the module that failed to import
        error: The ImportError exception
        fallback_response: Optional fallback response to return
        custom_logger: Optional custom logger instance
    
    Returns:
        Fallback response if provided, otherwise None
    """
    log = custom_logger or logger
    log.warning(f"{module_name} not available: {error}")
    
    return fallback_response


def create_error_response(
    error_code: int,
    error_title: str,
    error_message: str,
    stack_trace: str = None,
    is_api_route: bool = False
) -> Union[str, tuple]:
    """
    Create standardized error responses
    
    Args:
        error_code: HTTP error code
        error_title: Error title
        error_message: Error message
        stack_trace: Optional stack trace
        is_api_route: Whether this is an API route
    
    Returns:
        Flask response
    """
    if is_api_route:
        response_data = {
            'error': error_title,
            'message': error_message
        }
        if stack_trace:
            response_data['stack_trace'] = stack_trace
        return jsonify(response_data), error_code
    else:
        return render_template('errors/error.html',
                             error_code=error_code,
                             error_title=error_title,
                             error_message=error_message,
                             error_stack_trace=stack_trace,
                             timestamp=datetime.now().isoformat(),
                             error_uuid=f"e{error_code}_{uuid.uuid4().hex[:8]}",
                             request_id=str(uuid.uuid4())), error_code