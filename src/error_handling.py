"""
ValidoAI - Comprehensive Error Handling & Debugging System
==========================================================
Advanced error handling, logging, monitoring, and debugging capabilities
"""

import os
import sys
import logging
import traceback
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Callable
from functools import wraps
from contextlib import contextmanager
import threading
from dataclasses import dataclass, field
from enum import Enum

# Module-level logger
logger = logging.getLogger('validoai_error_handler')

class ErrorSeverity(Enum):
    """Error severity levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class ErrorCategory(Enum):
    """Error categories for classification"""
    DATABASE = "DATABASE"
    NETWORK = "NETWORK"
    SECURITY = "SECURITY"
    BUSINESS_LOGIC = "BUSINESS_LOGIC"
    EXTERNAL_SERVICE = "EXTERNAL_SERVICE"
    CONFIGURATION = "CONFIGURATION"
    FILE_SYSTEM = "FILE_SYSTEM"
    MEMORY = "MEMORY"
    PERFORMANCE = "PERFORMANCE"
    VALIDATION = "VALIDATION"
    AUTHENTICATION = "AUTHENTICATION"
    AUTHORIZATION = "AUTHORIZATION"
    UNKNOWN = "UNKNOWN"

@dataclass
class ErrorContext:
    """Error context information"""
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    endpoint: Optional[str] = None
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    method: Optional[str] = None
    url: Optional[str] = None
    headers: Dict[str, Any] = field(default_factory=dict)
    params: Dict[str, Any] = field(default_factory=dict)
    environment: str = os.environ.get('FLASK_ENV', 'development')
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class ErrorInfo:
    """Comprehensive error information"""
    severity: ErrorSeverity
    category: ErrorCategory
    message: str
    exception: Optional[Exception] = None
    context: Optional[ErrorContext] = None
    stack_trace: Optional[str] = None
    error_code: Optional[str] = None
    suggestions: List[str] = field(default_factory=list)
    recovery_actions: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None

class ErrorHandler:
    """Advanced error handler with monitoring and recovery"""

    def __init__(self):
        self.logger = self._setup_logging()
        self.error_history: List[ErrorInfo] = []
        self.error_stats: Dict[str, int] = {}
        self.max_history_size = int(os.environ.get('ERROR_HISTORY_SIZE', '1000'))
        self.alert_thresholds = self._load_alert_thresholds()
        self.recovery_strategies = self._load_recovery_strategies()

    def _setup_logging(self) -> logging.Logger:
        """Set up comprehensive logging"""
        logger = logging.getLogger('validoai_error_handler')
        logger.setLevel(logging.DEBUG)

        # Create logs directory if it doesn't exist
        os.makedirs('logs', exist_ok=True)

        # File handler for all logs
        file_handler = logging.FileHandler('logs/error_handler.log')
        file_handler.setLevel(logging.DEBUG)

        # Error file handler
        error_handler = logging.FileHandler('logs/errors.log')
        error_handler.setLevel(logging.ERROR)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        simple_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )

        file_handler.setFormatter(detailed_formatter)
        error_handler.setFormatter(detailed_formatter)
        console_handler.setFormatter(simple_formatter)

        logger.addHandler(file_handler)
        logger.addHandler(error_handler)
        logger.addHandler(console_handler)

        return logger

    def _load_alert_thresholds(self) -> Dict[str, int]:
        """Load alert thresholds from configuration"""
        return {
            'database_errors_per_hour': int(os.environ.get('ALERT_DB_ERRORS_PER_HOUR', '10')),
            'security_errors_per_hour': int(os.environ.get('ALERT_SECURITY_ERRORS_PER_HOUR', '5')),
            'external_service_errors_per_hour': int(os.environ.get('ALERT_EXTERNAL_ERRORS_PER_HOUR', '20')),
            'memory_errors_per_hour': int(os.environ.get('ALERT_MEMORY_ERRORS_PER_HOUR', '3')),
            'performance_errors_per_hour': int(os.environ.get('ALERT_PERFORMANCE_ERRORS_PER_HOUR', '15'))
        }

    def _load_recovery_strategies(self) -> Dict[str, List[str]]:
        """Load recovery strategies for different error types"""
        return {
            'database_connection': [
                'Retry connection with exponential backoff',
                'Check database server status',
                'Verify connection string and credentials',
                'Switch to backup database if available',
                'Restart database connection pool'
            ],
            'network_timeout': [
                'Retry request with increased timeout',
                'Check network connectivity',
                'Verify service availability',
                'Use cached data if available',
                'Implement circuit breaker pattern'
            ],
            'memory_error': [
                'Clear memory cache',
                'Reduce batch size',
                'Implement memory-efficient algorithms',
                'Monitor memory usage continuously',
                'Restart service if memory usage is critical'
            ],
            'external_service_unavailable': [
                'Retry with exponential backoff',
                'Use fallback service if available',
                'Queue request for later processing',
                'Return cached data if acceptable',
                'Notify service administrators'
            ],
            'authentication_failure': [
                'Verify credentials format',
                'Check if account is locked',
                'Reset authentication cache',
                'Verify token validity',
                'Redirect to login page'
            ]
        }

    def handle_error(self, error: Exception, context: Optional[ErrorContext] = None,
                    severity: ErrorSeverity = ErrorSeverity.ERROR,
                    category: ErrorCategory = ErrorCategory.UNKNOWN) -> ErrorInfo:
        """Handle an error with comprehensive logging and analysis"""

        # Create error info
        error_info = ErrorInfo(
            severity=severity,
            category=category,
            message=str(error),
            exception=error,
            context=context,
            stack_trace=traceback.format_exc()
        )

        # Analyze error and provide suggestions
        error_info = self._analyze_error(error_info)

        # Log error
        self._log_error(error_info)

        # Store in history
        self._store_error(error_info)

        # Check if alert should be triggered
        self._check_alert_thresholds(error_info)

        # Attempt recovery if possible
        self._attempt_recovery(error_info)

        return error_info

    def _analyze_error(self, error_info: ErrorInfo) -> ErrorInfo:
        """Analyze error and provide suggestions"""

        error_message = error_info.message.lower()
        error_type = type(error_info.exception).__name__ if error_info.exception else ''

        # Database errors
        if any(keyword in error_message or keyword in error_type.lower() for keyword in
               ['connection', 'timeout', 'unreachable', 'refused', 'psycopg2', 'pymysql']):
            error_info.category = ErrorCategory.DATABASE
            error_info.error_code = 'DB_001'
            error_info.suggestions = [
                'Check database server status',
                'Verify connection credentials',
                'Ensure database server is running',
                'Check network connectivity to database',
                'Verify database name and port'
            ]
            error_info.recovery_actions = self.recovery_strategies.get('database_connection', [])

        # Network errors
        elif any(keyword in error_message for keyword in ['timeout', 'connection', 'network', 'dns']):
            error_info.category = ErrorCategory.NETWORK
            error_info.error_code = 'NET_001'
            error_info.suggestions = [
                'Check network connectivity',
                'Verify service endpoints',
                'Check DNS resolution',
                'Review firewall settings',
                'Monitor network latency'
            ]
            error_info.recovery_actions = self.recovery_strategies.get('network_timeout', [])

        # Security errors
        elif any(keyword in error_message for keyword in ['unauthorized', 'forbidden', 'permission', 'authentication']):
            error_info.category = ErrorCategory.SECURITY
            error_info.error_code = 'SEC_001'
            error_info.suggestions = [
                'Verify user credentials',
                'Check user permissions',
                'Review authentication token',
                'Check if account is locked',
                'Verify API key validity'
            ]
            error_info.recovery_actions = self.recovery_strategies.get('authentication_failure', [])

        # Memory errors
        elif any(keyword in error_message for keyword in ['memory', 'outofmemory', 'memoryerror']):
            error_info.category = ErrorCategory.MEMORY
            error_info.error_code = 'MEM_001'
            error_info.suggestions = [
                'Monitor memory usage',
                'Implement memory-efficient algorithms',
                'Clear memory caches',
                'Reduce data processing batch size',
                'Check for memory leaks'
            ]
            error_info.recovery_actions = self.recovery_strategies.get('memory_error', [])

        # External service errors
        elif any(keyword in error_message for keyword in ['service unavailable', '502', '503', '504', 'external']):
            error_info.category = ErrorCategory.EXTERNAL_SERVICE
            error_info.error_code = 'EXT_001'
            error_info.suggestions = [
                'Check external service status',
                'Verify API endpoints',
                'Review service credentials',
                'Check service rate limits',
                'Implement retry logic'
            ]
            error_info.recovery_actions = self.recovery_strategies.get('external_service_unavailable', [])

        # Validation errors
        elif any(keyword in error_message for keyword in ['validation', 'invalid', 'required', 'format']):
            error_info.category = ErrorCategory.VALIDATION
            error_info.error_code = 'VAL_001'
            error_info.suggestions = [
                'Review input validation rules',
                'Check data format requirements',
                'Verify required fields',
                'Validate data types',
                'Review business rules'
            ]

        return error_info

    def _log_error(self, error_info: ErrorInfo):
        """Log error with appropriate level"""
        log_message = self._format_log_message(error_info)

        if error_info.severity == ErrorSeverity.DEBUG:
            self.logger.debug(log_message)
        elif error_info.severity == ErrorSeverity.INFO:
            self.logger.info(log_message)
        elif error_info.severity == ErrorSeverity.WARNING:
            self.logger.warning(log_message)
        elif error_info.severity == ErrorSeverity.ERROR:
            self.logger.error(log_message)
        elif error_info.severity == ErrorSeverity.CRITICAL:
            self.logger.critical(log_message)

    def _format_log_message(self, error_info: ErrorInfo) -> str:
        """Format error message for logging"""
        parts = [
            f"[{error_info.severity.value}]",
            f"[{error_info.category.value}]",
            f"Error: {error_info.message}"
        ]

        if error_info.error_code:
            parts.append(f"Code: {error_info.error_code}")

        if error_info.context:
            if error_info.context.user_id:
                parts.append(f"User: {error_info.context.user_id}")
            if error_info.context.endpoint:
                parts.append(f"Endpoint: {error_info.context.endpoint}")
            if error_info.context.request_id:
                parts.append(f"Request: {error_info.context.request_id}")

        if error_info.suggestions:
            parts.append(f"Suggestions: {'; '.join(error_info.suggestions)}")

        return " | ".join(parts)

    def _store_error(self, error_info: ErrorInfo):
        """Store error in history with size limit"""
        self.error_history.append(error_info)

        # Maintain max history size
        if len(self.error_history) > self.max_history_size:
            self.error_history = self.error_history[-self.max_history_size:]

        # Update error statistics
        category_key = f"{error_info.category.value}_{error_info.severity.value}"
        self.error_stats[category_key] = self.error_stats.get(category_key, 0) + 1

    def _check_alert_thresholds(self, error_info: ErrorInfo):
        """Check if error thresholds are exceeded"""
        # This would integrate with monitoring systems
        # For now, just log warning if critical errors occur
        if error_info.severity == ErrorSeverity.CRITICAL:
            self.logger.warning(f"Critical error occurred: {error_info.message}")

        if error_info.category == ErrorCategory.SECURITY:
            self.logger.warning(f"Security error detected: {error_info.message}")

    def _attempt_recovery(self, error_info: ErrorInfo):
        """Attempt automatic recovery for certain error types"""
        if error_info.category == ErrorCategory.DATABASE and error_info.recovery_actions:
            self.logger.info(f"Attempting database recovery for: {error_info.message}")

        # Recovery logic would be implemented here based on error type

    def get_error_statistics(self, hours: int = 1) -> Dict[str, Any]:
        """Get error statistics for the specified time period"""
        cutoff_time = datetime.now() - timedelta(hours=hours)

        recent_errors = [e for e in self.error_history if e.timestamp > cutoff_time]

        stats = {
            'total_errors': len(recent_errors),
            'by_severity': {},
            'by_category': {},
            'top_errors': [],
            'time_range_hours': hours
        }

        # Group by severity
        for error in recent_errors:
            severity = error.severity.value
            stats['by_severity'][severity] = stats['by_severity'].get(severity, 0) + 1

        # Group by category
        for error in recent_errors:
            category = error.category.value
            stats['by_category'][category] = stats['by_category'].get(category, 0) + 1

        return stats

    def get_recent_errors(self, limit: int = 10) -> List[ErrorInfo]:
        """Get recent errors"""
        return sorted(self.error_history[-limit:], key=lambda x: x.timestamp, reverse=True)

    def resolve_error(self, error_index: int, resolved_by: str):
        """Mark an error as resolved"""
        if 0 <= error_index < len(self.error_history):
            self.error_history[error_index].resolved = True
            self.error_history[error_index].resolved_at = datetime.now()
            self.error_history[error_index].resolved_by = resolved_by

# Global error handler instance
error_handler = ErrorHandler()

# Decorators for error handling
def handle_errors(severity: ErrorSeverity = ErrorSeverity.ERROR,
                 category: ErrorCategory = ErrorCategory.UNKNOWN):
    """Decorator to handle errors in functions"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Create error context from function arguments
                context = ErrorContext()
                if hasattr(func, '__name__'):
                    context.endpoint = func.__name__

                error_info = error_handler.handle_error(
                    error=e,
                    severity=severity,
                    category=category,
                    context=context
                )
                raise e
        return wrapper
    return decorator

def handle_database_errors():
    """Decorator specifically for database errors"""
    return handle_errors(severity=ErrorSeverity.ERROR, category=ErrorCategory.DATABASE)

def handle_security_errors():
    """Decorator specifically for security errors"""
    return handle_errors(severity=ErrorSeverity.WARNING, category=ErrorCategory.SECURITY)

@contextmanager
def error_context(**kwargs):
    """Context manager for adding error context"""
    context = ErrorContext(**kwargs)
    try:
        yield context
    except Exception as e:
        error_handler.handle_error(error=e, context=context)
        raise

# Utility functions
def log_performance(operation: str, duration: float, threshold: float = 1.0):
    """Log performance metrics"""
    if duration > threshold:
        error_handler.logger.warning(
            f"Performance issue: {operation} took {duration:.2f}s (threshold: {threshold}s)"
        )

def log_memory_usage():
    """Log current memory usage"""
    try:
        import psutil
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        error_handler.logger.debug(f"Memory usage: {memory_mb:.1f} MB")
    except ImportError:
        pass

def create_error_report(hours: int = 24) -> Dict[str, Any]:
    """Create comprehensive error report"""
    stats = error_handler.get_error_statistics(hours)
    recent_errors = error_handler.get_recent_errors(20)

    report = {
        'generated_at': datetime.now().isoformat(),
        'period_hours': hours,
        'statistics': stats,
        'recent_errors': [
            {
                'timestamp': e.timestamp.isoformat(),
                'severity': e.severity.value,
                'category': e.category.value,
                'message': e.message,
                'error_code': e.error_code,
                'resolved': e.resolved
            } for e in recent_errors
        ],
        'system_info': {
            'python_version': sys.version,
            'platform': sys.platform,
            'environment': os.environ.get('FLASK_ENV', 'unknown')
        }
    }

    return report

# Flask integration
def init_error_handling(app):
    """Initialize error handling for Flask app"""

    @app.errorhandler(400)
    def handle_bad_request(error):
        error_info = error_handler.handle_error(
            error=error,
            severity=ErrorSeverity.WARNING,
            category=ErrorCategory.VALIDATION
        )
        return {'error': 'Bad Request', 'message': str(error)}, 400

    @app.errorhandler(401)
    def handle_unauthorized(error):
        error_info = error_handler.handle_error(
            error=error,
            severity=ErrorSeverity.WARNING,
            category=ErrorCategory.AUTHENTICATION
        )
        return {'error': 'Unauthorized', 'message': str(error)}, 401

    @app.errorhandler(403)
    def handle_forbidden(error):
        error_info = error_handler.handle_error(
            error=error,
            severity=ErrorSeverity.WARNING,
            category=ErrorCategory.AUTHORIZATION
        )
        return {'error': 'Forbidden', 'message': str(error)}, 403

    @app.errorhandler(404)
    def handle_not_found(error):
        error_info = error_handler.handle_error(
            error=error,
            severity=ErrorSeverity.INFO,
            category=ErrorCategory.BUSINESS_LOGIC
        )
        return {'error': 'Not Found', 'message': str(error)}, 404

    @app.errorhandler(500)
    def handle_internal_error(error):
        error_info = error_handler.handle_error(
            error=error,
            severity=ErrorSeverity.ERROR,
            category=ErrorCategory.UNKNOWN
        )
        return {'error': 'Internal Server Error', 'message': str(error)}, 500

    error_handler.logger.info("✅ Error handling system initialized for Flask app")

# Export key components
__all__ = [
    'ErrorHandler',
    'ErrorInfo',
    'ErrorContext',
    'ErrorSeverity',
    'ErrorCategory',
    'error_handler',
    'handle_errors',
    'handle_database_errors',
    'handle_security_errors',
    'error_context',
    'log_performance',
    'log_memory_usage',
    'create_error_report',
    'init_error_handling'
]
