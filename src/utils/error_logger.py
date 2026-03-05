"""
Error Logging System for ValidoAI
Comprehensive error tracking with file and database logging
"""

import logging
import uuid
import json
import traceback
import sqlite3
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path
import os
from functools import wraps
from flask import request, g, current_app
import hashlib

class ErrorLogger:
    """Centralized error logging system"""
    
    def __init__(self, app=None):
        self.app = app
        self.logger = logging.getLogger(__name__)
        self.errors_logger = None
        self.db_path = None
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize the error logger with Flask app"""
        self.app = app
        self.db_path = app.config.get('DATABASE', 'data/sqlite/app.db')
        
        # Create logs directory if it doesn't exist
        logs_dir = Path('logs')
        logs_dir.mkdir(exist_ok=True)
        
        # Setup file logging for errors only
        self._setup_file_logging()
        
        # Setup database logging
        self._setup_database_logging()
    
    def _setup_file_logging(self):
        """Setup file logging for errors"""
        # Create error-specific logger
        self.errors_logger = logging.getLogger('validoai.errors')
        self.errors_logger.setLevel(logging.ERROR)
        
        # Prevent duplicate handlers
        if not self.errors_logger.handlers:
            # File handler for errors
            error_handler = logging.FileHandler('logs/errors.log')
            error_handler.setLevel(logging.ERROR)
            
            # Formatter for error logs
            error_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            error_handler.setFormatter(error_formatter)
            
            self.errors_logger.addHandler(error_handler)
    
    def _setup_database_logging(self):
        """Setup database tables for error logging"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.executescript('''
                    CREATE TABLE IF NOT EXISTS error_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        error_uuid TEXT UNIQUE NOT NULL,
                        error_hash TEXT NOT NULL,
                        error_type TEXT NOT NULL,
                        error_message TEXT NOT NULL,
                        error_code TEXT,
                        status_code INTEGER,
                        severity TEXT NOT NULL DEFAULT 'ERROR',
                        user_id INTEGER,
                        session_id TEXT,
                        request_path TEXT,
                        request_method TEXT,
                        request_ip TEXT,
                        user_agent TEXT,
                        stack_trace TEXT,
                        error_details TEXT,
                        context_data TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        resolved_at TIMESTAMP NULL,
                        resolution_notes TEXT,
                        FOREIGN KEY (user_id) REFERENCES users(id)
                    );
                    
                    CREATE INDEX IF NOT EXISTS idx_error_logs_uuid ON error_logs(error_uuid);
                    CREATE INDEX IF NOT EXISTS idx_error_logs_hash ON error_logs(error_hash);
                    CREATE INDEX IF NOT EXISTS idx_error_logs_type ON error_logs(error_type);
                    CREATE INDEX IF NOT EXISTS idx_error_logs_created_at ON error_logs(created_at);
                    CREATE INDEX IF NOT EXISTS idx_error_logs_severity ON error_logs(severity);
                    CREATE INDEX IF NOT EXISTS idx_error_logs_user_id ON error_logs(user_id);
                ''')
        except Exception as e:
            print(f"Error setting up database logging: {e}")
    
    def log_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Log an error to both file and database
        
        Args:
            error: The exception to log
            context: Additional context data
            
        Returns:
            str: The UUID of the logged error
        """
        error_uuid = str(uuid.uuid4())
        error_hash = self._generate_error_hash(error)
        
        # Prepare error data
        error_data = self._prepare_error_data(error, error_uuid, error_hash, context)
        
        # Log to file
        self._log_to_file(error_data)
        
        # Log to database
        self._log_to_database(error_data)
        
        return error_uuid
    
    def _generate_error_hash(self, error: Exception) -> str:
        """Generate a hash for the error to identify duplicates"""
        error_info = f"{type(error).__name__}:{str(error)}"
        return hashlib.md5(error_info.encode()).hexdigest()
    
    def _prepare_error_data(self, error: Exception, error_uuid: str, 
                           error_hash: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Prepare error data for logging"""
        # Get request information
        request_info = self._get_request_info()
        
        # Get user information
        user_info = self._get_user_info()
        
        # Prepare error details
        error_details = {
            'error_type': type(error).__name__,
            'error_message': str(error),
            'error_code': getattr(error, 'error_code', None),
            'status_code': getattr(error, 'status_code', 500),
            'stack_trace': traceback.format_exc(),
            'context': context or {}
        }
        
        return {
            'error_uuid': error_uuid,
            'error_hash': error_hash,
            'error_type': error_details['error_type'],
            'error_message': error_details['error_message'],
            'error_code': error_details['error_code'],
            'status_code': error_details['status_code'],
            'severity': 'ERROR',
            'user_id': user_info.get('user_id'),
            'session_id': user_info.get('session_id'),
            'request_path': request_info.get('path'),
            'request_method': request_info.get('method'),
            'request_ip': request_info.get('ip'),
            'user_agent': request_info.get('user_agent'),
            'stack_trace': error_details['stack_trace'],
            'error_details': json.dumps(error_details),
            'context_data': json.dumps(context or {}),
            'created_at': datetime.now().isoformat()
        }
    
    def _get_request_info(self) -> Dict[str, Any]:
        """Get current request information"""
        try:
            if request:
                return {
                    'path': request.path,
                    'method': request.method,
                    'ip': request.remote_addr,
                    'user_agent': request.headers.get('User-Agent', ''),
                    'headers': dict(request.headers),
                    'args': dict(request.args),
                    'form': dict(request.form) if request.form else {}
                }
        except Exception:
            pass
        return {}
    
    def _get_user_info(self) -> Dict[str, Any]:
        """Get current user information"""
        try:
            # Check if user is authenticated
            if hasattr(g, 'user') and g.user:
                return {
                    'user_id': g.user.get('id'),
                    'session_id': g.session_id if hasattr(g, 'session_id') else None
                }
        except Exception:
            pass
        return {}
    
    def _log_to_file(self, error_data: Dict[str, Any]):
        """Log error to file"""
        try:
            if self.errors_logger:
                log_message = (
                    f"Error UUID: {error_data['error_uuid']} | "
                    f"Type: {error_data['error_type']} | "
                    f"Message: {error_data['error_message']} | "
                    f"Path: {error_data.get('request_path', 'N/A')} | "
                    f"User: {error_data.get('user_id', 'Anonymous')}"
                )
                self.errors_logger.error(log_message)
        except Exception as e:
            print(f"Error logging to file: {e}")
    
    def _log_to_database(self, error_data: Dict[str, Any]):
        """Log error to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO error_logs (
                        error_uuid, error_hash, error_type, error_message, 
                        error_code, status_code, severity, user_id, session_id,
                        request_path, request_method, request_ip, user_agent,
                        stack_trace, error_details, context_data, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    error_data['error_uuid'],
                    error_data['error_hash'],
                    error_data['error_type'],
                    error_data['error_message'],
                    error_data['error_code'],
                    error_data['status_code'],
                    error_data['severity'],
                    error_data['user_id'],
                    error_data['session_id'],
                    error_data['request_path'],
                    error_data['request_method'],
                    error_data['request_ip'],
                    error_data['user_agent'],
                    error_data['stack_trace'],
                    error_data['error_details'],
                    error_data['context_data'],
                    error_data['created_at']
                ))
                conn.commit()
        except Exception as e:
            print(f"Error logging to database: {e}")
    
    def get_error_summary(self, error_uuid: str) -> Optional[Dict[str, Any]]:
        """Get error summary for user display"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute('''
                    SELECT error_uuid, error_type, error_message, error_code,
                           status_code, severity, request_path, created_at
                    FROM error_logs 
                    WHERE error_uuid = ?
                ''', (error_uuid,))
                
                row = cursor.fetchone()
                if row:
                    return dict(row)
        except Exception as e:
            print(f"Error getting error summary: {e}")
        return None
    
    def get_error_details(self, error_uuid: str) -> Optional[Dict[str, Any]]:
        """Get full error details for admin/debugging"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute('''
                    SELECT * FROM error_logs WHERE error_uuid = ?
                ''', (error_uuid,))
                
                row = cursor.fetchone()
                if row:
                    data = dict(row)
                    # Parse JSON fields
                    if data.get('error_details'):
                        data['error_details'] = json.loads(data['error_details'])
                    if data.get('context_data'):
                        data['context_data'] = json.loads(data['context_data'])
                    return data
        except Exception as e:
            print(f"Error getting error details: {e}")
        return None
    
    def get_recent_errors(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent errors for admin dashboard"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute('''
                    SELECT error_uuid, error_type, error_message, error_code,
                           status_code, severity, request_path, user_id, created_at
                    FROM error_logs 
                    ORDER BY created_at DESC 
                    LIMIT ?
                ''', (limit,))
                
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error getting recent errors: {e}")
        return []
    
    def resolve_error(self, error_uuid: str, resolution_notes: str = None):
        """Mark an error as resolved"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    UPDATE error_logs 
                    SET resolved_at = ?, resolution_notes = ?, updated_at = ?
                    WHERE error_uuid = ?
                ''', (datetime.now().isoformat(), resolution_notes, 
                     datetime.now().isoformat(), error_uuid))
                conn.commit()
        except Exception as e:
            print(f"Error resolving error: {e}")
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics for dashboard"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Total errors
                total_errors = conn.execute('''
                    SELECT COUNT(*) FROM error_logs
                ''').fetchone()[0]
                
                # Errors by type
                errors_by_type = conn.execute('''
                    SELECT error_type, COUNT(*) as count 
                    FROM error_logs 
                    GROUP BY error_type 
                    ORDER BY count DESC
                ''').fetchall()
                
                # Errors by status code
                errors_by_status = conn.execute('''
                    SELECT status_code, COUNT(*) as count 
                    FROM error_logs 
                    GROUP BY status_code 
                    ORDER BY count DESC
                ''').fetchall()
                
                # Recent errors (last 24 hours)
                recent_errors = conn.execute('''
                    SELECT COUNT(*) FROM error_logs 
                    WHERE created_at >= datetime('now', '-1 day')
                ''').fetchone()[0]
                
                return {
                    'total_errors': total_errors,
                    'recent_errors': recent_errors,
                    'errors_by_type': [dict(zip(['type', 'count'], row)) for row in errors_by_type],
                    'errors_by_status': [dict(zip(['status', 'count'], row)) for row in errors_by_status]
                }
        except Exception as e:
            print(f"Error getting error statistics: {e}")
        return {}

# Global error logger instance
error_logger = ErrorLogger()

def log_error_decorator(func):
    """Decorator to automatically log errors"""
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
            
            # Re-raise the exception
            raise e
    return wrapper

def handle_application_error(error: Exception) -> Dict[str, Any]:
    """Handle application errors and return user-friendly response"""
    # Log the error
    error_uuid = error_logger.log_error(error)
    
    # Get error summary for user
    error_summary = error_logger.get_error_summary(error_uuid)
    
    # Return user-friendly error response
    return {
        'success': False,
        'error': {
            'message': 'An error occurred while processing your request.',
            'error_id': error_uuid,
            'type': error_summary.get('error_type', 'Unknown Error') if error_summary else 'Unknown Error',
            'timestamp': error_summary.get('created_at') if error_summary else datetime.now().isoformat()
        }
    }
