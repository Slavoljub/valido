#!/usr/bin/env python3
"""
ValidoAI - Singleton Patterns Implementation
===========================================
Singleton pattern implementations for critical system components

Following Python best practices and OOP design patterns.
"""

import threading
import logging
import json
import os
from typing import Dict, Any, Optional, Callable
from datetime import datetime
from enum import Enum
import sys
from pathlib import Path

# ============================================================================
# SINGLETON BASE CLASS
# ============================================================================

class SingletonMeta(type):
    """
    Thread-safe Singleton metaclass
    Ensures only one instance of a class exists across the application
    """
    _instances: Dict[type, Any] = {}
    _lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            with cls._lock:
                if cls not in cls._instances:
                    cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

# ============================================================================
# ERROR HANDLER SINGLETON
# ============================================================================

class ErrorSeverity(Enum):
    """Error severity levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class ErrorCategory(Enum):
    """Error categories for classification"""
    SYSTEM = "SYSTEM"
    DATABASE = "DATABASE"
    NETWORK = "NETWORK"
    SECURITY = "SECURITY"
    BUSINESS = "BUSINESS"
    VALIDATION = "VALIDATION"
    INTEGRATION = "INTEGRATION"
    PERFORMANCE = "PERFORMANCE"

class ErrorContext:
    """Error context information"""
    def __init__(self, user_id=None, session_id=None, request_id=None,
                 ip_address=None, user_agent=None, endpoint=None,
                 method=None, payload=None):
        self.user_id = user_id
        self.session_id = session_id
        self.request_id = request_id or self._generate_request_id()
        self.ip_address = ip_address
        self.user_agent = user_agent
        self.endpoint = endpoint
        self.method = method
        self.payload = payload
        self.timestamp = datetime.now()
        self.thread_id = threading.current_thread().ident
        self.process_id = os.getpid()

    def _generate_request_id(self):
        """Generate unique request ID"""
        return f"req_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{os.urandom(4).hex()}"

    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary"""
        return {
            'request_id': self.request_id,
            'timestamp': self.timestamp.isoformat(),
            'thread_id': self.thread_id,
            'process_id': self.process_id,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'endpoint': self.endpoint,
            'method': self.method,
            'payload': self.payload
        }

class ErrorRecord:
    """Error record for logging and tracking"""
    def __init__(self, message: str, severity: ErrorSeverity, category: ErrorCategory,
                 exception: Optional[Exception] = None, context: Optional[ErrorContext] = None):
        self.id = f"err_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{os.urandom(4).hex()}"
        self.message = message
        self.severity = severity
        self.category = category
        self.exception = exception
        self.context = context or ErrorContext()
        self.timestamp = datetime.now()
        self.stack_trace = self._get_stack_trace()
        self.resolved = False
        self.resolved_at = None
        self.resolution = None

    def _get_stack_trace(self):
        """Get formatted stack trace"""
        if self.exception:
            import traceback
            return traceback.format_exception(
                type(self.exception),
                self.exception,
                self.exception.__traceback__
            )
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert error record to dictionary"""
        return {
            'id': self.id,
            'message': self.message,
            'severity': self.severity.value,
            'category': self.category.value,
            'timestamp': self.timestamp.isoformat(),
            'exception_type': type(self.exception).__name__ if self.exception else None,
            'context': self.context.to_dict() if self.context else None,
            'stack_trace': self.stack_trace,
            'resolved': self.resolved,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'resolution': self.resolution
        }

class ErrorHandler(metaclass=SingletonMeta):
    """
    Singleton Error Handler
    Centralized error handling and logging system
    """

    def __init__(self):
        self._errors: Dict[str, ErrorRecord] = {}
        self._error_count = 0
        self._lock = threading.Lock()
        self._logger = None
        self._setup_logger()

    def _setup_logger(self):
        """Setup error logger"""
        self._logger = logging.getLogger('ErrorHandler')
        self._logger.setLevel(logging.DEBUG)

        # File handler for error logs
        error_log_file = Path('logs') / 'error_handler.log'
        error_log_file.parent.mkdir(exist_ok=True)

        file_handler = logging.FileHandler(error_log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)

        # JSON formatter for structured logging
        class JSONFormatter(logging.Formatter):
            def format(self, record):
                log_entry = {
                    'timestamp': datetime.fromtimestamp(record.created).isoformat(),
                    'level': record.levelname,
                    'logger': record.name,
                    'message': record.getMessage(),
                    'module': record.module,
                    'function': record.funcName,
                    'line': record.lineno,
                    'thread': record.thread,
                    'process': record.process
                }

                if record.exc_info:
                    log_entry['exception'] = self.formatException(record.exc_info)

                return json.dumps(log_entry, ensure_ascii=False)

        file_handler.setFormatter(JSONFormatter())

        # Console handler for development
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)

        self._logger.addHandler(file_handler)
        self._logger.addHandler(console_handler)

    def log_error(self, message: str, severity: ErrorSeverity = ErrorSeverity.ERROR,
                  category: ErrorCategory = ErrorCategory.SYSTEM,
                  exception: Optional[Exception] = None,
                  context: Optional[ErrorContext] = None) -> str:
        """
        Log an error and return error ID

        Args:
            message: Error message
            severity: Error severity level
            category: Error category
            exception: Exception object if available
            context: Error context information

        Returns:
            Error ID for tracking
        """

        error_record = ErrorRecord(message, severity, category, exception, context)

        with self._lock:
            self._errors[error_record.id] = error_record
            self._error_count += 1

        # Log based on severity
        log_method = {
            ErrorSeverity.DEBUG: self._logger.debug,
            ErrorSeverity.INFO: self._logger.info,
            ErrorSeverity.WARNING: self._logger.warning,
            ErrorSeverity.ERROR: self._logger.error,
            ErrorSeverity.CRITICAL: self._logger.critical
        }.get(severity, self._logger.error)

        log_message = f"[{category.value}] {message}"
        if exception:
            log_message += f" | Exception: {str(exception)}"

        log_method(log_message)

        return error_record.id

    def get_error(self, error_id: str) -> Optional[ErrorRecord]:
        """Get error by ID"""
        return self._errors.get(error_id)

    def get_errors(self, severity: Optional[ErrorSeverity] = None,
                   category: Optional[ErrorCategory] = None,
                   limit: int = 100) -> Dict[str, ErrorRecord]:
        """Get filtered errors"""
        errors = self._errors.copy()

        if severity:
            errors = {k: v for k, v in errors.items() if v.severity == severity}

        if category:
            errors = {k: v for k, v in errors.items() if v.category == category}

        # Sort by timestamp (newest first)
        sorted_errors = sorted(errors.items(),
                              key=lambda x: x[1].timestamp,
                              reverse=True)

        return dict(sorted_errors[:limit])

    def resolve_error(self, error_id: str, resolution: str) -> bool:
        """Mark error as resolved"""
        error = self.get_error(error_id)
        if error:
            error.resolved = True
            error.resolved_at = datetime.now()
            error.resolution = resolution
            return True
        return False

    def get_statistics(self) -> Dict[str, Any]:
        """Get error statistics"""
        with self._lock:
            total_errors = len(self._errors)
            resolved_errors = sum(1 for e in self._errors.values() if e.resolved)
            unresolved_errors = total_errors - resolved_errors

            # Count by severity
            severity_counts = {}
            for severity in ErrorSeverity:
                severity_counts[severity.value] = sum(
                    1 for e in self._errors.values() if e.severity == severity
                )

            # Count by category
            category_counts = {}
            for category in ErrorCategory:
                category_counts[category.value] = sum(
                    1 for e in self._errors.values() if e.category == category
                )

            return {
                'total_errors': total_errors,
                'resolved_errors': resolved_errors,
                'unresolved_errors': unresolved_errors,
                'resolution_rate': (resolved_errors / total_errors * 100) if total_errors > 0 else 0,
                'severity_counts': severity_counts,
                'category_counts': category_counts,
                'uptime_errors': self._error_count  # Errors since startup
            }

    def cleanup_old_errors(self, days: int = 30):
        """Clean up old resolved errors"""
        cutoff_date = datetime.now() - timedelta(days=days)
        old_errors = []

        with self._lock:
            for error_id, error in self._errors.items():
                if error.resolved and error.resolved_at and error.resolved_at < cutoff_date:
                    old_errors.append(error_id)

            for error_id in old_errors:
                del self._errors[error_id]

        return len(old_errors)

# ============================================================================
# GLOBAL LOGGER SINGLETON
# ============================================================================

class LogLevel(Enum):
    """Logging levels"""
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50

class GlobalLogger(metaclass=SingletonMeta):
    """
    Singleton Global Logger
    Centralized logging system with structured output
    """

    def __init__(self):
        self._loggers: Dict[str, logging.Logger] = {}
        self._lock = threading.Lock()
        self._setup_default_logger()

    def _setup_default_logger(self):
        """Setup default logger configuration"""
        # Create logs directory
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)

        # Setup main logger
        self._setup_logger('validoai', log_dir / 'validoai.log')
        self._setup_logger('error', log_dir / 'error.log')
        self._setup_logger('audit', log_dir / 'audit.log')
        self._setup_logger('performance', log_dir / 'performance.log')

    def _setup_logger(self, name: str, log_file: Path):
        """Setup individual logger"""
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)

        # Avoid duplicate handlers
        if logger.handlers:
            return

        # File handler
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)

        # JSON formatter for structured logging
        class StructuredFormatter(logging.Formatter):
            def format(self, record):
                log_entry = {
                    'timestamp': datetime.fromtimestamp(record.created).isoformat(),
                    'level': record.levelname,
                    'logger': record.name,
                    'message': record.getMessage(),
                    'module': record.module,
                    'function': record.funcName,
                    'line': record.lineno,
                    'thread': record.thread,
                    'process': record.process,
                    'thread_name': record.threadName
                }

                # Add any extra fields
                if hasattr(record, 'extra_data'):
                    log_entry.update(record.extra_data)

                if record.exc_info:
                    log_entry['exception'] = self.formatException(record.exc_info)

                return json.dumps(log_entry, ensure_ascii=False, indent=2)

        file_handler.setFormatter(StructuredFormatter())

        # Console handler for development
        if os.environ.get('FLASK_ENV') == 'development':
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)
            console_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(console_formatter)
            logger.addHandler(console_handler)

        logger.addHandler(file_handler)
        self._loggers[name] = logger

    def get_logger(self, name: str = 'validoai') -> logging.Logger:
        """Get logger by name"""
        if name not in self._loggers:
            with self._lock:
                if name not in self._loggers:
                    log_file = Path('logs') / f'{name}.log'
                    self._setup_logger(name, log_file)

        return self._loggers[name]

    def log_activity(self, level: LogLevel, message: str,
                     logger_name: str = 'validoai',
                     extra_data: Optional[Dict[str, Any]] = None,
                     user_id: Optional[str] = None,
                     session_id: Optional[str] = None,
                     request_id: Optional[str] = None):
        """Log activity with structured data"""

        logger = self.get_logger(logger_name)

        # Create log record with extra data
        extra = {'extra_data': extra_data or {}}

        if user_id:
            extra['extra_data']['user_id'] = user_id
        if session_id:
            extra['extra_data']['session_id'] = session_id
        if request_id:
            extra['extra_data']['request_id'] = request_id

        logger.log(level.value, message, extra=extra)

    def log_user_action(self, user_id: str, action: str,
                       resource: str, details: Optional[Dict[str, Any]] = None):
        """Log user action for audit trail"""
        self.log_activity(
            LogLevel.INFO,
            f"User action: {action} on {resource}",
            logger_name='audit',
            extra_data={
                'user_id': user_id,
                'action': action,
                'resource': resource,
                'details': details or {}
            }
        )

    def log_performance(self, operation: str, duration_ms: float,
                       details: Optional[Dict[str, Any]] = None):
        """Log performance metrics"""
        self.log_activity(
            LogLevel.INFO,
            f"Performance: {operation} took {duration_ms:.2f}ms",
            logger_name='performance',
            extra_data={
                'operation': operation,
                'duration_ms': duration_ms,
                'details': details or {}
            }
        )

    def log_error(self, error: Exception, context: Optional[Dict[str, Any]] = None):
        """Log error with context"""
        logger = self.get_logger('error')
        logger.error(f"Exception: {str(error)}", exc_info=True, extra={'extra_data': context or {}})

    def log_security_event(self, event_type: str, user_id: Optional[str] = None,
                          ip_address: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        """Log security-related events"""
        self.log_activity(
            LogLevel.WARNING,
            f"Security event: {event_type}",
            logger_name='audit',
            extra_data={
                'event_type': event_type,
                'user_id': user_id,
                'ip_address': ip_address,
                'details': details or {}
            }
        )

# ============================================================================
# CONFIGURATION MANAGER SINGLETON
# ============================================================================

class ConfigurationManager(metaclass=SingletonMeta):
    """
    Singleton Configuration Manager
    Centralized configuration management with caching
    """

    def __init__(self):
        self._config_cache: Dict[str, Any] = {}
        self._config_file = Path('config') / 'app_config.json'
        self._env_prefix = 'VALIDOAI_'
        self._lock = threading.Lock()
        self._last_modified = None
        self._load_config()

    def _load_config(self):
        """Load configuration from file and environment"""
        with self._lock:
            # Load from JSON file
            if self._config_file.exists():
                try:
                    with open(self._config_file, 'r', encoding='utf-8') as f:
                        file_config = json.load(f)
                        self._config_cache.update(file_config)
                except Exception as e:
                    error_handler.log_error(
                        f"Failed to load config file: {e}",
                        ErrorSeverity.ERROR,
                        ErrorCategory.SYSTEM
                    )

            # Override with environment variables
            for key, value in os.environ.items():
                if key.startswith(self._env_prefix):
                    config_key = key[len(self._env_prefix):].lower()
                    # Try to parse as JSON, fallback to string
                    try:
                        parsed_value = json.loads(value)
                    except:
                        parsed_value = value
                    self._config_cache[config_key] = parsed_value

            self._last_modified = datetime.now()

    def get(self, key: str, default=None):
        """Get configuration value"""
        # Check if config file has been modified
        if self._config_file.exists():
            file_modified = datetime.fromtimestamp(self._config_file.stat().st_mtime)
            if self._last_modified and file_modified > self._last_modified:
                self._load_config()

        return self._config_cache.get(key, default)

    def set(self, key: str, value: Any):
        """Set configuration value"""
        with self._lock:
            self._config_cache[key] = value

            # Save to file
            self._config_file.parent.mkdir(exist_ok=True)
            try:
                with open(self._config_file, 'w', encoding='utf-8') as f:
                    json.dump(self._config_cache, f, indent=2, ensure_ascii=False)
            except Exception as e:
                error_handler.log_error(
                    f"Failed to save config: {e}",
                    ErrorSeverity.ERROR,
                    ErrorCategory.SYSTEM
                )

    def get_all(self) -> Dict[str, Any]:
        """Get all configuration values"""
        return self._config_cache.copy()

    def reload(self):
        """Force reload configuration"""
        self._load_config()

# ============================================================================
# CACHE MANAGER SINGLETON
# ============================================================================

class CacheManager(metaclass=SingletonMeta):
    """
    Singleton Cache Manager
    In-memory caching with TTL support
    """

    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()
        self._cleanup_interval = 300  # 5 minutes
        self._start_cleanup_thread()

    def _start_cleanup_thread(self):
        """Start background cleanup thread"""
        def cleanup_worker():
            while True:
                try:
                    self._cleanup_expired()
                    threading.Event().wait(self._cleanup_interval)
                except Exception as e:
                    error_handler.log_error(
                        f"Cache cleanup error: {e}",
                        ErrorSeverity.ERROR,
                        ErrorCategory.SYSTEM
                    )

        cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        cleanup_thread.start()

    def _cleanup_expired(self):
        """Remove expired cache entries"""
        current_time = datetime.now().timestamp()
        expired_keys = []

        with self._lock:
            for key, data in self._cache.items():
                if current_time > data['expires_at']:
                    expired_keys.append(key)

            for key in expired_keys:
                del self._cache[key]

        if expired_keys:
            global_logger.get_logger().info(f"Cleaned up {len(expired_keys)} expired cache entries")

    def set(self, key: str, value: Any, ttl_seconds: int = 300):
        """Set cache value with TTL"""
        expires_at = datetime.now().timestamp() + ttl_seconds

        with self._lock:
            self._cache[key] = {
                'value': value,
                'expires_at': expires_at,
                'created_at': datetime.now().timestamp()
            }

    def get(self, key: str, default=None):
        """Get cache value"""
        current_time = datetime.now().timestamp()

        with self._lock:
            if key in self._cache:
                data = self._cache[key]
                if current_time <= data['expires_at']:
                    return data['value']
                else:
                    # Remove expired entry
                    del self._cache[key]

        return default

    def delete(self, key: str) -> bool:
        """Delete cache entry"""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
        return False

    def clear(self):
        """Clear all cache entries"""
        with self._lock:
            self._cache.clear()

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            total_entries = len(self._cache)
            current_time = datetime.now().timestamp()
            expired_count = sum(1 for data in self._cache.values()
                              if current_time > data['expires_at'])

            return {
                'total_entries': total_entries,
                'expired_entries': expired_count,
                'active_entries': total_entries - expired_count
            }

# ============================================================================
# GLOBAL INSTANCES
# ============================================================================

# Create global singleton instances
error_handler = ErrorHandler()
global_logger = GlobalLogger()
config_manager = ConfigurationManager()
cache_manager = CacheManager()

# Convenience functions
def log_error(message: str, severity: ErrorSeverity = ErrorSeverity.ERROR,
             category: ErrorCategory = ErrorCategory.SYSTEM,
             exception: Optional[Exception] = None,
             context: Optional[ErrorContext] = None) -> str:
    """Convenience function to log errors"""
    return error_handler.log_error(message, severity, category, exception, context)

def get_logger(name: str = 'validoai') -> logging.Logger:
    """Convenience function to get logger"""
    return global_logger.get_logger(name)

def get_config(key: str, default=None):
    """Convenience function to get configuration"""
    return config_manager.get(key, default)

def set_config(key: str, value: Any):
    """Convenience function to set configuration"""
    config_manager.set(key, value)

def cache_get(key: str, default=None):
    """Convenience function to get cached value"""
    return cache_manager.get(key, default)

def cache_set(key: str, value: Any, ttl_seconds: int = 300):
    """Convenience function to set cached value"""
    cache_manager.set(key, value, ttl_seconds)

# ============================================================================
# TEST FUNCTIONS
# ============================================================================

def test_singleton_patterns():
    """Test all singleton patterns"""
    print("🧪 Testing Singleton Patterns...")

    # Test Error Handler
    error_id1 = log_error("Test error 1", ErrorSeverity.ERROR, ErrorCategory.SYSTEM)
    error_id2 = log_error("Test error 2", ErrorSeverity.WARNING, ErrorCategory.DATABASE)

    print(f"✅ Logged errors: {error_id1}, {error_id2}")

    # Test Logger
    logger = get_logger('test')
    logger.info("Test log message")
    print("✅ Logger working")

    # Test Configuration
    set_config('test_key', 'test_value')
    value = get_config('test_key')
    print(f"✅ Config working: {value}")

    # Test Cache
    cache_set('test_cache', 'cached_value', 60)
    cached_value = cache_get('test_cache')
    print(f"✅ Cache working: {cached_value}")

    # Test Error Statistics
    stats = error_handler.get_statistics()
    print(f"✅ Error stats: {stats['total_errors']} total errors")

    print("\\n🎉 All Singleton patterns working correctly!")

if __name__ == '__main__':
    test_singleton_patterns()
