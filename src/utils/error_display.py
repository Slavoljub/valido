"""
Error Display Utility for ValidoAI
Handles error message display and formatting
"""

from typing import Dict, List, Optional, Any
from flask import flash, session
import json
from datetime import datetime

class ErrorDisplay:
    """Utility for displaying error messages on pages"""
    
    @staticmethod
    def flash_error(message: str, category: str = 'error', title: str = None):
        """Flash an error message to the user"""
        if title:
            flash(f"{title}: {message}", category)
        else:
            flash(message, category)
    
    @staticmethod
    def flash_success(message: str, title: str = None):
        """Flash a success message to the user"""
        if title:
            flash(f"{title}: {message}", 'success')
        else:
            flash(message, 'success')
    
    @staticmethod
    def flash_warning(message: str, title: str = None):
        """Flash a warning message to the user"""
        if title:
            flash(f"{title}: {message}", 'warning')
        else:
            flash(message, 'warning')
    
    @staticmethod
    def flash_info(message: str, title: str = None):
        """Flash an info message to the user"""
        if title:
            flash(f"{title}: {message}", 'info')
        else:
            flash(message, 'info')
    
    @staticmethod
    def set_page_error(error_data: Dict[str, Any]):
        """Set error data for page display"""
        session['page_error'] = {
            'title': error_data.get('title', 'Error'),
            'message': error_data.get('message', 'An error occurred'),
            'details': error_data.get('details', {}),
            'timestamp': datetime.utcnow().isoformat(),
            'type': error_data.get('type', 'error'),
            'code': error_data.get('code', 'UNKNOWN')
        }
    
    @staticmethod
    def get_page_error() -> Optional[Dict[str, Any]]:
        """Get page error data and clear it"""
        error_data = session.pop('page_error', None)
        return error_data
    
    @staticmethod
    def format_validation_errors(errors: List[Dict[str, str]]) -> str:
        """Format validation errors for display"""
        if not errors:
            return "Validation failed"
        
        error_messages = []
        for error in errors:
            field = error.get('field', 'Unknown field')
            message = error.get('message', 'Invalid value')
            error_messages.append(f"{field}: {message}")
        
        return "; ".join(error_messages)
    
    @staticmethod
    def format_api_error(response_data: Dict[str, Any]) -> str:
        """Format API error response for display"""
        if isinstance(response_data, dict):
            if 'message' in response_data:
                return response_data['message']
            elif 'error' in response_data:
                return response_data['error']
            elif 'errors' in response_data:
                errors = response_data['errors']
                if isinstance(errors, list):
                    return ErrorDisplay.format_validation_errors(errors)
                elif isinstance(errors, dict):
                    return "; ".join([f"{k}: {v}" for k, v in errors.items()])
        
        return str(response_data)
    
    @staticmethod
    def create_error_context(error: Exception, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create error context for display"""
        return {
            'error_type': type(error).__name__,
            'error_message': str(error),
            'error_code': getattr(error, 'code', 'UNKNOWN'),
            'context': context or {},
            'timestamp': datetime.utcnow().isoformat()
        }

# Global instance
error_display = ErrorDisplay()
