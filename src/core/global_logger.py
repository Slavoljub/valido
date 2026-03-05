"""
ValidoAI Global Logger System
=============================

Comprehensive logging system that can display errors in:
- Terminal/Console
- Web pages (as notifications/toasts)
- Database (for historical analysis)
- Files (structured logs)
- External services (optional)

Features:
- Multiple output channels
- Error categorization and severity levels
- Context-aware logging
- Real-time error display
- Historical error tracking
- Performance monitoring integration
"""

import logging
import json
import time
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import traceback
import sys
from pathlib import Path
import threading
from queue import Queue
import uuid

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

class ErrorSeverity(Enum):
    """Error severity levels"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class ErrorCategory(Enum):
    """Error categories for better organization"""
    DATABASE = "database"
    AI_MODEL = "ai_model"
    NETWORK = "network"
    SECURITY = "security"
    VALIDATION = "validation"
    CONFIGURATION = "configuration"
    FILESYSTEM = "filesystem"
    EXTERNAL_SERVICE = "external_service"
    USER_INTERFACE = "user_interface"
    PERFORMANCE = "performance"
    SYSTEM = "system"
    BUSINESS_LOGIC = "business_logic"
    HTTP_ERROR = "http_error"

@dataclass
class ErrorContext:
    """Context information for errors"""
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    url: Optional[str] = None
    method: Optional[str] = None
    component: Optional[str] = None
    function: Optional[str] = None
    module: Optional[str] = None
    line_number: Optional[int] = None
    additional_data: Optional[Dict[str, Any]] = None

@dataclass
class ErrorRecord:
    """Complete error record"""
    id: str
    timestamp: datetime
    severity: ErrorSeverity
    category: ErrorCategory
    message: str
    exception_type: Optional[str]
    exception_message: Optional[str]
    traceback: Optional[str]
    context: ErrorContext
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    resolution_notes: Optional[str] = None
    tags: List[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.metadata is None:
            self.metadata = {}

class GlobalLogger:
    """Global logging system with multiple output channels"""

    def __init__(self):
        self._setup_base_logger()
        self.error_queue = Queue()
        self.error_history: List[ErrorRecord] = []
        self.max_history = 1000
        self.output_channels: Dict[str, Callable] = {}
        self._setup_output_channels()
        self._start_error_processor()

    def _setup_base_logger(self):
        """Setup the base Python logger"""
        self.logger = logging.getLogger('validoai_global')
        self.logger.setLevel(logging.DEBUG)

        # Clear existing handlers
        self.logger.handlers.clear()

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

        # File handler for structured logs
        log_file = Path("logs/validoai_errors.log")
        log_file.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_formatter = logging.Formatter(
            '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}'
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)

    def _setup_output_channels(self):
        """Setup various output channels for errors"""
        self.output_channels = {
            'console': self._output_to_console,
            'web': self._output_to_web,
            'database': self._output_to_database,
            'file': self._output_to_file,
            'notification': self._output_to_notification
        }

    def _start_error_processor(self):
        """Start the error processing thread"""
        def process_errors():
            while True:
                try:
                    error_record = self.error_queue.get(timeout=1)
                    self._process_error_record(error_record)
                except:
                    continue

        processor_thread = threading.Thread(target=process_errors, daemon=True)
        processor_thread.start()

    def _process_error_record(self, error_record: ErrorRecord):
        """Process a single error record"""
        # Add to history
        self.error_history.append(error_record)
        if len(self.error_history) > self.max_history:
            self.error_history.pop(0)

        # Output to all enabled channels
        for channel_name, channel_func in self.output_channels.items():
            try:
                channel_func(error_record)
            except Exception as e:
                print(f"Error in {channel_name} channel: {e}")

    def log_error(self,
                  message: str,
                  severity: ErrorSeverity = ErrorSeverity.ERROR,
                  category: ErrorCategory = ErrorCategory.SYSTEM,
                  exception: Exception = None,
                  context: ErrorContext = None,
                  tags: List[str] = None) -> str:
        """Log an error with full context"""

        if context is None:
            context = ErrorContext()

        # Get traceback if exception provided
        traceback_str = None
        exception_type = None
        exception_message = None

        if exception:
            traceback_str = traceback.format_exc()
            exception_type = type(exception).__name__
            exception_message = str(exception)

        # Add calling context if not provided
        if not context.module or not context.function or not context.line_number:
            try:
                frame = sys._getframe(1)
                context.module = frame.f_globals.get('__name__', 'unknown')
                context.function = frame.f_code.co_name
                context.line_number = frame.f_lineno
            except:
                pass

        # Create error record
        error_record = ErrorRecord(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            severity=severity,
            category=category,
            message=message,
            exception_type=exception_type,
            exception_message=exception_message,
            traceback=traceback_str,
            context=context,
            tags=tags or []
        )

        # Queue for processing
        self.error_queue.put(error_record)

        # Also log to Python logger
        log_message = f"[{category.value}] {message}"
        if exception:
            log_message += f" | {exception_type}: {exception_message}"

        log_level = {
            ErrorSeverity.DEBUG: logging.DEBUG,
            ErrorSeverity.INFO: logging.INFO,
            ErrorSeverity.WARNING: logging.WARNING,
            ErrorSeverity.ERROR: logging.ERROR,
            ErrorSeverity.CRITICAL: logging.CRITICAL
        }[severity]

        self.logger.log(log_level, log_message, extra={'error_id': error_record.id})

        return error_record.id

    def log_database_error(self, operation: str, error: Exception, context: ErrorContext = None):
        """Log database-related errors"""
        message = f"Database error during {operation}"
        self.log_error(message, ErrorSeverity.ERROR, ErrorCategory.DATABASE, error, context,
                      tags=['database', operation])

    def log_ai_error(self, model_name: str, operation: str, error: Exception, context: ErrorContext = None):
        """Log AI model-related errors"""
        message = f"AI error in {model_name} during {operation}"
        self.log_error(message, ErrorSeverity.ERROR, ErrorCategory.AI_MODEL, error, context,
                      tags=['ai', 'model', model_name, operation])

    def log_network_error(self, url: str, operation: str, error: Exception, context: ErrorContext = None):
        """Log network-related errors"""
        message = f"Network error accessing {url} during {operation}"
        if context is None:
            context = ErrorContext()
        context.url = url
        self.log_error(message, ErrorSeverity.ERROR, ErrorCategory.NETWORK, error, context,
                      tags=['network', operation])

    def log_validation_error(self, field: str, value: str, error: Exception, context: ErrorContext = None):
        """Log validation errors"""
        message = f"Validation error for field '{field}' with value '{value}'"
        self.log_error(message, ErrorSeverity.WARNING, ErrorCategory.VALIDATION, error, context,
                      tags=['validation', field])

    def log_security_error(self, action: str, user_id: str = None, error: Exception = None, context: ErrorContext = None):
        """Log security-related errors"""
        message = f"Security error during {action}"
        if context is None:
            context = ErrorContext()
        context.user_id = user_id
        self.log_error(message, ErrorSeverity.ERROR, ErrorCategory.SECURITY, error, context,
                      tags=['security', action])

    def _output_to_console(self, error_record: ErrorRecord):
        """Output error to console with color coding"""
        colors = {
            ErrorSeverity.DEBUG: '\033[36m',  # Cyan
            ErrorSeverity.INFO: '\033[32m',   # Green
            ErrorSeverity.WARNING: '\033[33m', # Yellow
            ErrorSeverity.ERROR: '\033[31m',   # Red
            ErrorSeverity.CRITICAL: '\033[35m' # Magenta
        }

        color = colors.get(error_record.severity, '\033[0m')
        reset = '\033[0m'

        print(f"{color}[{error_record.severity.value.upper()}] {error_record.category.value}: {error_record.message}{reset}")

        if error_record.exception_type:
            print(f"{color}  Exception: {error_record.exception_type}: {error_record.exception_message}{reset}")

        if error_record.context.component:
            print(f"{color}  Component: {error_record.context.component}{reset}")

        print(f"{color}  ID: {error_record.id} | Time: {error_record.timestamp.strftime('%Y-%m-%d %H:%M:%S')}{reset}")
        print()

    def _output_to_web(self, error_record: ErrorRecord):
        """Store error for web display (can be retrieved via API)"""
        # This would be implemented to store errors in a way that can be displayed on web pages
        # For now, we'll just mark it as processed
        pass

    def _output_to_database(self, error_record: ErrorRecord):
        """Store error in database for historical analysis"""
        try:
            # This would store the error in a database table
            # For now, we'll implement it when the database is fully set up
            pass
        except Exception as e:
            print(f"Failed to store error in database: {e}")

    def _output_to_file(self, error_record: ErrorRecord):
        """Output error to structured log file"""
        try:
            log_file = Path("logs/structured_errors.jsonl")
            log_file.parent.mkdir(parents=True, exist_ok=True)

            with open(log_file, 'a', encoding='utf-8') as f:
                json.dump(asdict(error_record), f, default=str, ensure_ascii=False)
                f.write('\n')
        except Exception as e:
            print(f"Failed to write error to file: {e}")

    def _output_to_notification(self, error_record: ErrorRecord):
        """Send error notification (email, webhook, etc.)"""
        # This would send notifications for critical errors
        # For now, we'll just handle critical errors
        if error_record.severity == ErrorSeverity.CRITICAL:
            print(f"🚨 CRITICAL ERROR: {error_record.message}")

    def get_recent_errors(self, limit: int = 50, severity: ErrorSeverity = None,
                         category: ErrorCategory = None) -> List[ErrorRecord]:
        """Get recent errors with optional filtering"""
        errors = self.error_history[-limit:] if limit > 0 else self.error_history

        if severity:
            errors = [e for e in errors if e.severity == severity]
        if category:
            errors = [e for e in errors if e.category == category]

        return errors

    def get_error_by_id(self, error_id: str) -> Optional[ErrorRecord]:
        """Get error by ID"""
        for error in self.error_history:
            if error.id == error_id:
                return error
        return None

    def get_error_summary(self) -> Dict[str, Any]:
        """Get error summary statistics"""
        total_errors = len(self.error_history)

        severity_counts = {severity.value: 0 for severity in ErrorSeverity}
        category_counts = {category.value: 0 for category in ErrorCategory}

        for error in self.error_history:
            severity_counts[error.severity.value] += 1
            category_counts[error.category.value] += 1

        return {
            'total_errors': total_errors,
            'severity_distribution': severity_counts,
            'category_distribution': category_counts,
            'most_recent_error': self.error_history[-1] if self.error_history else None,
            'critical_errors_count': severity_counts['critical']
        }

    def clear_error_history(self):
        """Clear error history"""
        self.error_history.clear()

    def resolve_error(self, error_id: str, resolved_by: str = None, notes: str = None):
        """Mark an error as resolved"""
        error = self.get_error_by_id(error_id)
        if error:
            error.resolved = True
            error.resolved_at = datetime.now()
            error.resolved_by = resolved_by
            error.resolution_notes = notes

    def get_errors_by_component(self, component: str) -> List[ErrorRecord]:
        """Get errors by component"""
        return [e for e in self.error_history if e.context.component == component]

    def get_errors_by_user(self, user_id: str) -> List[ErrorRecord]:
        """Get errors by user"""
        return [e for e in self.error_history if e.context.user_id == user_id]

# Global logger instance
global_logger = GlobalLogger()

# Convenience functions for easy access
def log_error(message: str, severity: ErrorSeverity = ErrorSeverity.ERROR,
              category: ErrorCategory = ErrorCategory.SYSTEM, exception: Exception = None,
              context: ErrorContext = None, tags: List[str] = None) -> str:
    """Convenience function for logging errors"""
    return global_logger.log_error(message, severity, category, exception, context, tags)

def log_database_error(operation: str, error: Exception, context: ErrorContext = None):
    """Convenience function for database errors"""
    global_logger.log_database_error(operation, error, context)

def log_ai_error(model_name: str, operation: str, error: Exception, context: ErrorContext = None):
    """Convenience function for AI errors"""
    global_logger.log_ai_error(model_name, operation, error, context)

def log_network_error(url: str, operation: str, error: Exception, context: ErrorContext = None):
    """Convenience function for network errors"""
    global_logger.log_network_error(url, operation, error, context)

def log_validation_error(field: str, value: str, error: Exception, context: ErrorContext = None):
    """Convenience function for validation errors"""
    global_logger.log_validation_error(field, value, error, context)

def log_security_error(action: str, user_id: str = None, error: Exception = None, context: ErrorContext = None):
    """Convenience function for security errors"""
    global_logger.log_security_error(action, user_id, error, context)

# Export key components
__all__ = [
    'GlobalLogger',
    'ErrorRecord',
    'ErrorContext',
    'ErrorSeverity',
    'ErrorCategory',
    'global_logger',
    'log_error',
    'log_database_error',
    'log_ai_error',
    'log_network_error',
    'log_validation_error',
    'log_security_error'
]
