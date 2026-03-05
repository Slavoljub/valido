"""
Logging Configuration for ValidoAI
Best practices logging setup with focus on errors, warnings, and performance
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime
from pathlib import Path
from functools import wraps
import time

# Base logs directory
LOGS_DIR = Path('logs')

# Ensure logs directory exists
LOGS_DIR.mkdir(exist_ok=True)

# Create subdirectories for different log types
(LOGS_DIR / 'errors').mkdir(exist_ok=True)
(LOGS_DIR / 'warnings').mkdir(exist_ok=True)
(LOGS_DIR / 'performance').mkdir(exist_ok=True)
(LOGS_DIR / 'security').mkdir(exist_ok=True)
(LOGS_DIR / 'debug').mkdir(exist_ok=True)

class StructuredFormatter(logging.Formatter):
    """Structured logging formatter for better log parsing"""
    
    def format(self, record):
        # Add structured fields
        record.timestamp = datetime.utcnow().isoformat()
        record.process_id = os.getpid()
        record.thread_id = record.thread if hasattr(record, 'thread') else 'N/A'
        
        # Format the message
        formatted = super().format(record)
        
        # Add context if available
        if hasattr(record, 'context'):
            formatted += f" | Context: {record.context}"
        
        return formatted

def setup_logger(name, log_file, level=logging.INFO, max_bytes=10*1024*1024, backup_count=3):
    """Setup a logger with file rotation and structured formatting"""
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
    
    # Create structured formatter
    formatter = StructuredFormatter(
        '%(timestamp)s | %(name)s | %(levelname)s | PID:%(process_id)s | %(filename)s:%(lineno)d | %(message)s'
    )
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    
    # Console handler (only for errors and warnings in production)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.WARNING)  # Only show warnings and errors in console
    console_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def setup_application_logging():
    """Setup all application loggers following best practices"""
    
    # Error logger - Critical errors that need immediate attention
    error_logger = setup_logger(
        'validoai.errors',
        LOGS_DIR / 'errors' / 'errors.log',
        level=logging.ERROR
    )
    
    # Warning logger - Issues that need attention but aren't critical
    warning_logger = setup_logger(
        'validoai.warnings',
        LOGS_DIR / 'warnings' / 'warnings.log',
        level=logging.WARNING
    )
    
    # Performance logger - Slow operations and performance metrics
    performance_logger = setup_logger(
        'validoai.performance',
        LOGS_DIR / 'performance' / 'performance.log',
        level=logging.INFO
    )
    
    # Security logger - Security events and suspicious activities
    security_logger = setup_logger(
        'validoai.security',
        LOGS_DIR / 'security' / 'security.log',
        level=logging.WARNING
    )
    
    # Debug logger - Detailed debugging information (only in development)
    debug_logger = setup_logger(
        'validoai.debug',
        LOGS_DIR / 'debug' / 'debug.log',
        level=logging.DEBUG if os.getenv('FLASK_ENV') == 'development' else logging.INFO
    )
    
    return {
        'errors': error_logger,
        'warnings': warning_logger,
        'performance': performance_logger,
        'security': security_logger,
        'debug': debug_logger
    }

def log_error(error_type, message, exception=None, context=None):
    """Log errors with structured information"""
    logger = logging.getLogger('validoai.errors')
    
    # Create structured error message
    error_data = {
        'type': error_type,
        'message': message,
        'timestamp': datetime.utcnow().isoformat(),
        'context': context or {}
    }
    
    if exception:
        error_data['exception'] = str(exception)
        error_data['traceback'] = getattr(exception, '__traceback__', None)
    
    logger.error(f"ERROR: {error_type} | {message}", extra={'context': error_data})

def log_warning(warning_type, message, context=None):
    """Log warnings with structured information"""
    logger = logging.getLogger('validoai.warnings')
    
    warning_data = {
        'type': warning_type,
        'message': message,
        'timestamp': datetime.utcnow().isoformat(),
        'context': context or {}
    }
    
    logger.warning(f"WARNING: {warning_type} | {message}", extra={'context': warning_data})

def log_performance(operation, duration, threshold=1.0, details=None):
    """Log performance metrics - only log slow operations by default"""
    logger = logging.getLogger('validoai.performance')
    
    if duration > threshold:
        performance_data = {
            'operation': operation,
            'duration': duration,
            'threshold': threshold,
            'details': details,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        logger.warning(f"SLOW_OPERATION: {operation} took {duration:.3f}s", extra={'context': performance_data})
    else:
        # Log all operations at debug level
        logger.debug(f"PERFORMANCE: {operation} took {duration:.3f}s")

def log_security_event(event_type, details, severity='WARNING', context=None):
    """Log security-related events"""
    logger = logging.getLogger('validoai.security')
    
    security_data = {
        'event_type': event_type,
        'details': details,
        'severity': severity,
        'timestamp': datetime.utcnow().isoformat(),
        'context': context or {}
    }
    
    if severity == 'ERROR':
        logger.error(f"SECURITY_ERROR: {event_type} | {details}", extra={'context': security_data})
    elif severity == 'WARNING':
        logger.warning(f"SECURITY_WARNING: {event_type} | {details}", extra={'context': security_data})
    else:
        logger.info(f"SECURITY_INFO: {event_type} | {details}", extra={'context': security_data})

def log_database_operation(operation, table=None, duration=None, error=None, context=None):
    """Log database operations - focus on errors and slow operations"""
    logger = logging.getLogger('validoai.debug')
    
    if error:
        # Log database errors
        error_logger = logging.getLogger('validoai.errors')
        error_data = {
            'operation': operation,
            'table': table,
            'error': str(error),
            'timestamp': datetime.utcnow().isoformat(),
            'context': context or {}
        }
        error_logger.error(f"DB_ERROR: {operation} on {table} | {error}", extra={'context': error_data})
    elif duration and duration > 0.5:  # Log slow database operations
        performance_logger = logging.getLogger('validoai.performance')
        perf_data = {
            'operation': operation,
            'table': table,
            'duration': duration,
            'timestamp': datetime.utcnow().isoformat(),
            'context': context or {}
        }
        performance_logger.warning(f"SLOW_DB: {operation} on {table} took {duration:.3f}s", extra={'context': perf_data})
    else:
        # Log normal operations at debug level
        logger.debug(f"DB_OP: {operation} on {table}")

def log_ai_operation(operation, provider=None, model=None, duration=None, error=None, context=None):
    """Log AI operations - focus on errors and performance"""
    logger = logging.getLogger('validoai.debug')
    
    if error:
        # Log AI errors
        error_logger = logging.getLogger('validoai.errors')
        error_data = {
            'operation': operation,
            'provider': provider,
            'model': model,
            'error': str(error),
            'timestamp': datetime.utcnow().isoformat(),
            'context': context or {}
        }
        error_logger.error(f"AI_ERROR: {operation} ({provider}/{model}) | {error}", extra={'context': error_data})
    elif duration and duration > 2.0:  # Log slow AI operations
        performance_logger = logging.getLogger('validoai.performance')
        perf_data = {
            'operation': operation,
            'provider': provider,
            'model': model,
            'duration': duration,
            'timestamp': datetime.utcnow().isoformat(),
            'context': context or {}
        }
        performance_logger.warning(f"SLOW_AI: {operation} ({provider}/{model}) took {duration:.3f}s", extra={'context': perf_data})
    else:
        # Log normal operations at debug level
        logger.debug(f"AI_OP: {operation} ({provider}/{model})")

def performance_monitor(operation_name):
    """Decorator to monitor function performance"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                log_performance(operation_name, duration)
                return result
            except Exception as e:
                duration = time.time() - start_time
                log_error('PERFORMANCE_MONITOR', f"{operation_name} failed", e)
                raise
        return wrapper
    return decorator

def log_request_error(request, error, context=None):
    """Log request errors only - not all requests"""
    logger = logging.getLogger('validoai.errors')
    
    error_data = {
        'method': request.method,
        'path': request.path,
        'client_ip': request.headers.get('X-Forwarded-For', request.remote_addr),
        'user_agent': request.headers.get('User-Agent', 'Unknown'),
        'error': str(error),
        'timestamp': datetime.utcnow().isoformat(),
        'context': context or {}
    }
    
    logger.error(f"REQUEST_ERROR: {request.method} {request.path} | {error}", extra={'context': error_data})

def cleanup_old_logs(days_to_keep=7):
    """Clean up old log files - keep only recent logs"""
    import time
    from pathlib import Path
    
    cutoff_time = time.time() - (days_to_keep * 24 * 60 * 60)
    deleted_count = 0
    
    for log_file in LOGS_DIR.rglob('*.log.*'):
        if log_file.stat().st_mtime < cutoff_time:
            try:
                log_file.unlink()
                deleted_count += 1
            except Exception as e:
                print(f"Error deleting {log_file}: {e}")
    
    if deleted_count > 0:
        print(f"Cleaned up {deleted_count} old log files")

def get_log_stats():
    """Get statistics about log files"""
    stats = {}
    
    for log_type in ['errors', 'warnings', 'performance', 'security', 'debug']:
        log_dir = LOGS_DIR / log_type
        if log_dir.exists():
            total_size = sum(f.stat().st_size for f in log_dir.glob('*.log*') if f.is_file())
            file_count = len(list(log_dir.glob('*.log*')))
            stats[log_type] = {
                'size_mb': round(total_size / (1024 * 1024), 2),
                'file_count': file_count
            }
    
    return stats

def configure_logging_for_environment():
    """Configure logging based on environment"""
    env = os.getenv('FLASK_ENV', 'production')
    
    if env == 'development':
        # In development, show more detailed logs
        logging.getLogger('validoai.debug').setLevel(logging.DEBUG)
        logging.getLogger('validoai.performance').setLevel(logging.INFO)
    else:
        # In production, focus on errors and warnings
        logging.getLogger('validoai.debug').setLevel(logging.WARNING)
        logging.getLogger('validoai.performance').setLevel(logging.WARNING)

# Initialize loggers when module is imported
loggers = setup_application_logging()

# Configure based on environment
configure_logging_for_environment()

# Export main loggers for easy access
error_logger = loggers['errors']
warning_logger = loggers['warnings']
performance_logger = loggers['performance']
security_logger = loggers['security']
debug_logger = loggers['debug']
