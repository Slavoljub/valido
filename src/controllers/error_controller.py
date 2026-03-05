"""
Error Controller for ValidoAI
Handles error management operations following MVVM pattern
"""

from typing import Dict, Any, List, Optional
from flask import jsonify, request, render_template
from src.utils.error_logger import error_logger
from src.utils.exception_handler import create_success_response, create_error_response
from src.utils.exception_handler import handle_exceptions, ValidationError
from src.core.controller_loader import api_get, api_post, get_route
import json

class ErrorController:
    """Controller for error management operations"""
    
    def __init__(self):
        self.error_logger = error_logger
    
    @api_get('/errors/summary/<error_uuid>')
    @handle_exceptions
    def get_error_summary(self, error_uuid: str) -> Dict[str, Any]:
        """
        Get error summary for user display
        
        Args:
            error_uuid: The UUID of the error
            
        Returns:
            Dict containing error summary
        """
        error_summary = self.error_logger.get_error_summary(error_uuid)
        
        if not error_summary:
            raise ValidationError(f"Error with UUID {error_uuid} not found")
        
        return create_success_response(
            data=error_summary,
            message="Error summary retrieved successfully"
        )
    
    @api_get('/errors/details/<error_uuid>')
    @handle_exceptions
    def get_error_details(self, error_uuid: str) -> Dict[str, Any]:
        """
        Get full error details for admin/debugging
        
        Args:
            error_uuid: The UUID of the error
            
        Returns:
            Dict containing full error details
        """
        error_details = self.error_logger.get_error_details(error_uuid)
        
        if not error_details:
            raise ValidationError(f"Error with UUID {error_uuid} not found")
        
        return create_success_response(
            data=error_details,
            message="Error details retrieved successfully"
        )
    
    @api_get('/errors/recent')
    @handle_exceptions
    def get_recent_errors(self) -> Dict[str, Any]:
        """
        Get recent errors for admin dashboard
        
        Returns:
            Dict containing recent errors
        """
        limit = request.args.get('limit', 50, type=int)
        
        # Validate limit parameter
        if not isinstance(limit, int) or limit < 1 or limit > 1000:
            raise ValidationError("Limit must be an integer between 1 and 1000")
        
        recent_errors = self.error_logger.get_recent_errors(limit)
        
        return create_success_response(
            data={
                'errors': recent_errors,
                'count': len(recent_errors),
                'limit': limit
            },
            message="Recent errors retrieved successfully"
        )
    
    @api_get('/errors/statistics')
    @handle_exceptions
    def get_error_statistics(self) -> Dict[str, Any]:
        """
        Get error statistics for dashboard
        
        Returns:
            Dict containing error statistics
        """
        statistics = self.error_logger.get_error_statistics()
        
        return create_success_response(
            data=statistics,
            message="Error statistics retrieved successfully"
        )
    
    @api_post('/errors/<error_uuid>/resolve')
    @handle_exceptions
    def resolve_error(self, error_uuid: str) -> Dict[str, Any]:
        """
        Mark an error as resolved
        
        Args:
            error_uuid: The UUID of the error
            
        Returns:
            Dict containing resolution status
        """
        data = request.get_json() or {}
        resolution_notes = data.get('resolution_notes')
        
        # Validate error UUID exists
        error_summary = self.error_logger.get_error_summary(error_uuid)
        if not error_summary:
            raise ValidationError(f"Error with UUID {error_uuid} not found")
        
        # Resolve the error
        self.error_logger.resolve_error(error_uuid, resolution_notes)
        
        return create_success_response(
            data={'error_uuid': error_uuid, 'resolved': True},
            message="Error marked as resolved successfully"
        )
    
    @api_post('/errors/search')
    @handle_exceptions
    def search_errors(self) -> Dict[str, Any]:
        """
        Search errors based on criteria
        
        Returns:
            Dict containing matching errors
        """
        search_params = request.get_json() or {}
        
        # Validate search parameters
        allowed_params = ['error_type', 'status_code', 'severity', 'user_id', 'date_from', 'date_to']
        
        for param in search_params:
            if param not in allowed_params:
                raise ValidationError(f"Invalid search parameter: {param}")
        
        # Get all recent errors and filter them
        # Note: For production, this should be implemented in the database layer
        recent_errors = self.error_logger.get_recent_errors(1000)
        
        # Apply filters
        filtered_errors = []
        for error in recent_errors:
            match = True
            
            if 'error_type' in search_params and error.get('error_type') != search_params['error_type']:
                match = False
            
            if 'status_code' in search_params and error.get('status_code') != search_params['status_code']:
                match = False
            
            if 'severity' in search_params and error.get('severity') != search_params['severity']:
                match = False
            
            if 'user_id' in search_params and error.get('user_id') != search_params['user_id']:
                match = False
            
            if match:
                filtered_errors.append(error)
        
        return create_success_response(
            data={
                'errors': filtered_errors,
                'count': len(filtered_errors),
                'search_params': search_params
            },
            message="Error search completed successfully"
        )
    
    @api_get('/errors/export')
    @handle_exceptions
    def export_errors(self) -> Dict[str, Any]:
        """
        Export errors in specified format
        
        Returns:
            Dict containing exported data
        """
        format_type = request.args.get('format', 'json')
        limit = request.args.get('limit', 1000, type=int)
        
        # Validate format
        if format_type not in ['json', 'csv']:
            raise ValidationError("Format must be 'json' or 'csv'")
        
        # Validate limit
        if not isinstance(limit, int) or limit < 1 or limit > 10000:
            raise ValidationError("Limit must be an integer between 1 and 10000")
        
        # Get errors
        errors = self.error_logger.get_recent_errors(limit)
        
        if format_type == 'json':
            export_data = json.dumps(errors, indent=2, default=str)
        else:  # csv
            import csv
            import io
            
            output = io.StringIO()
            if errors:
                writer = csv.DictWriter(output, fieldnames=errors[0].keys())
                writer.writeheader()
                writer.writerows(errors)
            export_data = output.getvalue()
        
        return create_success_response(
            data={
                'format': format_type,
                'count': len(errors),
                'data': export_data
            },
            message=f"Errors exported successfully in {format_type.upper()} format"
        )
    
    @api_get('/errors/trends')
    @handle_exceptions
    def get_error_trends(self) -> Dict[str, Any]:
        """
        Get error trends over time
        
        Returns:
            Dict containing error trends
        """
        days = request.args.get('days', 30, type=int)
        
        # Validate days parameter
        if not isinstance(days, int) or days < 1 or days > 365:
            raise ValidationError("Days must be an integer between 1 and 365")
        
        # Get recent errors
        recent_errors = self.error_logger.get_recent_errors(10000)
        
        # Group by date
        from datetime import datetime, timedelta
        from collections import defaultdict
        
        trends = defaultdict(int)
        error_types = defaultdict(int)
        status_codes = defaultdict(int)
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        for error in recent_errors:
            try:
                error_date = datetime.fromisoformat(error.get('created_at', ''))
                if error_date >= cutoff_date:
                    # Count by date
                    date_key = error_date.strftime('%Y-%m-%d')
                    trends[date_key] += 1
                    
                    # Count by type
                    error_types[error.get('error_type', 'Unknown')] += 1
                    
                    # Count by status code
                    status_codes[str(error.get('status_code', 500))] += 1
            except:
                continue
        
        # Convert to sorted lists
        trend_data = sorted(trends.items())
        type_data = sorted(error_types.items(), key=lambda x: x[1], reverse=True)
        status_data = sorted(status_codes.items(), key=lambda x: x[1], reverse=True)
        
        return create_success_response(
            data={
                'trends': trend_data,
                'error_types': type_data,
                'status_codes': status_data,
                'total_errors': sum(trends.values()),
                'days_analyzed': days
            },
            message="Error trends retrieved successfully"
        )
    
    @get_route('/dashboard')
    def error_dashboard(self):
        """Error management dashboard page"""
        return render_template('errors/dashboard.html')

# Global error controller instance
error_controller = ErrorController()
