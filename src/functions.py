"""
ValidoAI - Common Utility Functions
Provides centralized utility functions for the entire application
"""

import os
import sys
import json
import uuid
import hashlib
import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import requests
from flask import request, session, g, current_app
import sqlite3
from dataclasses import dataclass, asdict

# Configure logging
logger = logging.getLogger(__name__)

# ============================================================================
# CORE UTILITY FUNCTIONS
# ============================================================================

def get_project_root() -> Path:
    """Get the project root directory"""
    return Path(__file__).parent.parent

def get_config_path() -> Path:
    """Get the configuration file path"""
    return get_project_root() / "config" / "app_config.json"

def get_data_path() -> Path:
    """Get the data directory path"""
    return get_project_root() / "data"

def get_uploads_path() -> Path:
    """Get the uploads directory path"""
    return get_project_root() / "uploads"

def get_models_path() -> Path:
    """Get the models directory path"""
    return get_project_root() / "models"

def get_logs_path() -> Path:
    """Get the logs directory path"""
    return get_project_root() / "logs"

# ============================================================================
# DATABASE UTILITIES
# ============================================================================

def get_database_connection(db_path: str = None) -> sqlite3.Connection:
    """Get a database connection with proper configuration"""
    if db_path is None:
        db_path = str(get_data_path() / "sqlite" / "sample.db")
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Enable dict-like access
    return conn

def execute_query(query: str, params: tuple = None, db_path: str = None) -> List[Dict]:
    """Execute a database query and return results as list of dictionaries"""
    try:
        with get_database_connection(db_path) as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if query.strip().upper().startswith('SELECT'):
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
            else:
                conn.commit()
                return [{"affected_rows": cursor.rowcount}]
    except Exception as e:
        logger.error(f"Database query error: {e}")
        raise

def table_exists(table_name: str, db_path: str = None) -> bool:
    """Check if a table exists in the database"""
    query = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"
    result = execute_query(query, (table_name,), db_path)
    return len(result) > 0

def get_table_schema(table_name: str, db_path: str = None) -> List[Dict]:
    """Get the schema of a table"""
    query = f"PRAGMA table_info({table_name})"
    return execute_query(query, db_path=db_path)

# ============================================================================
# ROUTING AND NAVIGATION UTILITIES
# ============================================================================

def get_current_route() -> str:
    """Get the current route/endpoint"""
    return request.endpoint or 'unknown'

def get_current_url() -> str:
    """Get the current full URL"""
    return request.url

def get_home_route() -> str:
    """Get the home page route"""
    return '/'

def get_dashboard_route() -> str:
    """Get the dashboard route"""
    return '/dashboard'

def get_chat_local_route() -> str:
    """Get the chat-local route"""
    return '/chat-local'

def get_api_base_url() -> str:
    """Get the API base URL"""
    return '/api/v1'

def is_api_request() -> bool:
    """Check if the current request is an API request"""
    return request.path.startswith('/api/')

def is_ajax_request() -> bool:
    """Check if the current request is an AJAX request"""
    return request.headers.get('X-Requested-With') == 'XMLHttpRequest'

# ============================================================================
# INTERNATIONALIZATION (I18N) UTILITIES
# ============================================================================

# Supported languages
SUPPORTED_LANGUAGES = {
    'en': 'English',
    'sr': 'Serbian',
    'hr': 'Croatian',
    'bs': 'Bosnian',
    'mk': 'Macedonian',
    'sl': 'Slovenian'
}

# Translation dictionaries
TRANSLATIONS = {
    'en': {
        'welcome': 'Welcome to ValidoAI',
        'dashboard': 'Dashboard',
        'chat_local': 'AI Chat',
        'settings': 'Settings',
        'financial_analysis': 'Financial Analysis',
        'reports': 'Reports',
        'help': 'Help',
        'logout': 'Logout'
    },
    'sr': {
        'welcome': 'Dobrodošli u ValidoAI',
        'dashboard': 'Kontrolna tabla',
        'chat_local': 'AI Chat',
        'settings': 'Podešavanja',
        'financial_analysis': 'Finansijska analiza',
        'reports': 'Izveštaji',
        'help': 'Pomoć',
        'logout': 'Odjava'
    },
    'hr': {
        'welcome': 'Dobrodošli u ValidoAI',
        'dashboard': 'Nadzorna ploča',
        'chat_local': 'AI Chat',
        'settings': 'Postavke',
        'financial_analysis': 'Financijska analiza',
        'reports': 'Izvještaji',
        'help': 'Pomoć',
        'logout': 'Odjava'
    }
}

def get_current_language() -> str:
    """Get the current language from session or request"""
    return session.get('language', request.accept_languages.best_match(SUPPORTED_LANGUAGES.keys(), default='en'))

def set_language(language: str) -> None:
    """Set the current language"""
    if language in SUPPORTED_LANGUAGES:
        session['language'] = language

def translate(key: str, language: str = None) -> str:
    """Translate a key to the specified language"""
    if language is None:
        language = get_current_language()
    
    return TRANSLATIONS.get(language, TRANSLATIONS['en']).get(key, key)

def get_language_name(language_code: str) -> str:
    """Get the full name of a language from its code"""
    return SUPPORTED_LANGUAGES.get(language_code, 'Unknown')

def get_supported_languages() -> Dict[str, str]:
    """Get all supported languages"""
    return SUPPORTED_LANGUAGES.copy()

# ============================================================================
# FILE AND UPLOAD UTILITIES
# ============================================================================

def generate_unique_filename(original_filename: str, prefix: str = "") -> str:
    """Generate a unique filename with UUID"""
    name, ext = os.path.splitext(original_filename)
    unique_id = str(uuid.uuid4())[:8]
    return f"{prefix}{name}_{unique_id}{ext}"

def get_file_extension(filename: str) -> str:
    """Get the file extension from filename"""
    return os.path.splitext(filename)[1].lower()

def is_allowed_file(filename: str, allowed_extensions: List[str] = None) -> bool:
    """Check if file extension is allowed"""
    if allowed_extensions is None:
        allowed_extensions = ['.pdf', '.xlsx', '.csv', '.txt', '.doc', '.docx', '.jpg', '.png']
    
    return get_file_extension(filename) in allowed_extensions

def get_file_size_mb(file_path: str) -> float:
    """Get file size in MB"""
    return os.path.getsize(file_path) / (1024 * 1024)

def create_upload_directory(session_id: str) -> Path:
    """Create upload directory for a session"""
    upload_dir = get_uploads_path() / "chat-local" / f"{session_id}-artifact-validoai"
    upload_dir.mkdir(parents=True, exist_ok=True)
    return upload_dir

def save_uploaded_file(file, session_id: str) -> Dict[str, Any]:
    """Save an uploaded file and return file info"""
    if file and is_allowed_file(file.filename):
        upload_dir = create_upload_directory(session_id)
        filename = generate_unique_filename(file.filename, "valido-ai-")
        file_path = upload_dir / filename
        
        file.save(str(file_path))
        
        return {
            'id': str(uuid.uuid4()),
            'name': file.filename,
            'path': str(file_path),
            'size': os.path.getsize(file_path),
            'upload_date': datetime.now().isoformat()
        }
    return None

# ============================================================================
# SESSION AND CACHE UTILITIES
# ============================================================================

def generate_session_id() -> str:
    """Generate a unique session ID"""
    return f"valido-ai-{uuid.uuid4()}"

def get_session_data(session_id: str) -> Dict[str, Any]:
    """Get session data from database"""
    query = "SELECT * FROM chat_sessions WHERE session_uuid = ?"
    result = execute_query(query, (session_id,))
    return result[0] if result else None

def save_session_data(session_id: str, data: Dict[str, Any]) -> bool:
    """Save session data to database"""
    try:
        query = """
        INSERT OR REPLACE INTO chat_sessions 
        (session_uuid, user_id, model_name, session_name, updated_at)
        VALUES (?, ?, ?, ?, ?)
        """
        execute_query(query, (
            session_id,
            data.get('user_id'),
            data.get('model_name'),
            data.get('session_name', 'New Session'),
            datetime.now().isoformat()
        ))
        return True
    except Exception as e:
        logger.error(f"Error saving session data: {e}")
        return False

def get_session_messages(session_id: str, limit: int = 50) -> List[Dict]:
    """Get messages for a session"""
    query = """
    SELECT * FROM chat_messages 
    WHERE session_uuid = ? 
    ORDER BY created_at DESC 
    LIMIT ?
    """
    return execute_query(query, (session_id, limit))

def save_message(session_id: str, message_type: str, content: str, metadata: Dict = None) -> bool:
    """Save a message to the database"""
    try:
        query = """
        INSERT INTO chat_messages 
        (session_uuid, message_type, content, metadata, created_at)
        VALUES (?, ?, ?, ?, ?)
        """
        execute_query(query, (
            session_id,
            message_type,
            content,
            json.dumps(metadata) if metadata else None,
            datetime.now().isoformat()
        ))
        return True
    except Exception as e:
        logger.error(f"Error saving message: {e}")
        return False

# ============================================================================
# FINANCIAL DATA UTILITIES
# ============================================================================

def get_financial_summary(company_id: str = None, period: str = "current_month") -> Dict[str, Any]:
    """Get financial summary for a company and period"""
    try:
        # Get current month/year
        now = datetime.now()
        if period == "current_month":
            start_date = now.replace(day=1).strftime('%Y-%m-%d')
            end_date = now.strftime('%Y-%m-%d')
        elif period == "current_year":
            start_date = now.replace(month=1, day=1).strftime('%Y-%m-%d')
            end_date = now.strftime('%Y-%m-%d')
        else:
            start_date = (now - timedelta(days=30)).strftime('%Y-%m-%d')
            end_date = now.strftime('%Y-%m-%d')
        
        # Get revenue
        revenue_query = """
        SELECT COALESCE(SUM(amount), 0) as total_revenue
        FROM invoices 
        WHERE invoice_type = 'sale' 
        AND invoice_date BETWEEN ? AND ?
        """
        if company_id:
            revenue_query += " AND company_id = ?"
            revenue_result = execute_query(revenue_query, (start_date, end_date, company_id))
        else:
            revenue_result = execute_query(revenue_query, (start_date, end_date))
        
        # Get expenses
        expense_query = """
        SELECT COALESCE(SUM(amount), 0) as total_expenses
        FROM invoices 
        WHERE invoice_type = 'purchase' 
        AND invoice_date BETWEEN ? AND ?
        """
        if company_id:
            expense_query += " AND company_id = ?"
            expense_result = execute_query(expense_query, (start_date, end_date, company_id))
        else:
            expense_result = execute_query(expense_query, (start_date, end_date))
        
        total_revenue = revenue_result[0]['total_revenue'] if revenue_result else 0
        total_expenses = expense_result[0]['total_expenses'] if expense_result else 0
        
        return {
            'period': period,
            'start_date': start_date,
            'end_date': end_date,
            'total_revenue': float(total_revenue),
            'total_expenses': float(total_expenses),
            'net_income': float(total_revenue - total_expenses),
            'profit_margin': float((total_revenue - total_expenses) / total_revenue * 100) if total_revenue > 0 else 0
        }
    except Exception as e:
        logger.error(f"Error getting financial summary: {e}")
        return {}

def get_top_partners(company_id: str = None, limit: int = 5) -> List[Dict]:
    """Get top partners by revenue"""
    try:
        query = """
        SELECT p.name, p.type, COALESCE(SUM(i.amount), 0) as total_amount
        FROM partners p
        LEFT JOIN invoices i ON p.id = i.partner_id
        WHERE i.invoice_type = 'sale'
        """
        if company_id:
            query += " AND i.company_id = ?"
            query += " GROUP BY p.id, p.name, p.type ORDER BY total_amount DESC LIMIT ?"
            result = execute_query(query, (company_id, limit))
        else:
            query += " GROUP BY p.id, p.name, p.type ORDER BY total_amount DESC LIMIT ?"
            result = execute_query(query, (limit,))
        
        return result
    except Exception as e:
        logger.error(f"Error getting top partners: {e}")
        return []

def get_recent_transactions(company_id: str = None, limit: int = 10) -> List[Dict]:
    """Get recent financial transactions"""
    try:
        query = """
        SELECT i.*, p.name as partner_name
        FROM invoices i
        LEFT JOIN partners p ON i.partner_id = p.id
        """
        if company_id:
            query += " WHERE i.company_id = ?"
            query += " ORDER BY i.invoice_date DESC LIMIT ?"
            result = execute_query(query, (company_id, limit))
        else:
            query += " ORDER BY i.invoice_date DESC LIMIT ?"
            result = execute_query(query, (limit,))
        
        return result
    except Exception as e:
        logger.error(f"Error getting recent transactions: {e}")
        return []

# ============================================================================
# VALIDATION UTILITIES
# ============================================================================

def validate_email(email: str) -> bool:
    """Validate email format"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone: str) -> bool:
    """Validate phone number format"""
    import re
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone)
    return len(digits) >= 8 and len(digits) <= 15

def validate_tax_number(tax_number: str) -> bool:
    """Validate Serbian tax number format"""
    import re
    # Serbian tax number format: 8 digits
    pattern = r'^\d{8}$'
    return re.match(pattern, tax_number) is not None

def validate_amount(amount: Union[str, float]) -> bool:
    """Validate amount format"""
    try:
        float(amount)
        return True
    except (ValueError, TypeError):
        return False

# ============================================================================
# FORMATTING UTILITIES
# ============================================================================

def format_currency(amount: float, currency: str = "RSD") -> str:
    """Format amount as currency"""
    if currency == "RSD":
        return f"{amount:,.2f} RSD"
    elif currency == "EUR":
        return f"€{amount:,.2f}"
    elif currency == "USD":
        return f"${amount:,.2f}"
    else:
        return f"{amount:,.2f} {currency}"

def format_date(date: Union[str, datetime], format_str: str = "%d.%m.%Y") -> str:
    """Format date string"""
    if isinstance(date, str):
        try:
            date = datetime.fromisoformat(date.replace('Z', '+00:00'))
        except ValueError:
            return date
    
    return date.strftime(format_str)

def format_datetime(dt: Union[str, datetime], format_str: str = "%d.%m.%Y %H:%M") -> str:
    """Format datetime string"""
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
        except ValueError:
            return dt
    
    return dt.strftime(format_str)

def format_file_size(bytes_size: int) -> str:
    """Format file size in human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} TB"

# ============================================================================
# SECURITY UTILITIES
# ============================================================================

def hash_password(password: str) -> str:
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash"""
    return hash_password(password) == hashed

def generate_api_key() -> str:
    """Generate a secure API key"""
    return hashlib.sha256(uuid.uuid4().bytes).hexdigest()

def sanitize_input(input_str: str) -> str:
    """Sanitize user input to prevent XSS"""
    import html
    return html.escape(input_str.strip())

# ============================================================================
# ERROR HANDLING UTILITIES
# ============================================================================

def log_error(error: Exception, context: str = "") -> str:
    """Log an error and return error ID"""
    error_id = str(uuid.uuid4())
    logger.error(f"Error ID: {error_id}, Context: {context}, Error: {str(error)}")
    return error_id

def create_error_response(error: Exception, status_code: int = 500) -> Dict[str, Any]:
    """Create a standardized error response"""
    error_id = log_error(error)
    return {
        'success': False,
        'error': {
            'id': error_id,
            'message': str(error),
            'type': type(error).__name__,
            'timestamp': datetime.now().isoformat()
        }
    }, status_code

def create_success_response(data: Any, message: str = "Success") -> Dict[str, Any]:
    """Create a standardized success response"""
    return {
        'success': True,
        'message': message,
        'data': data,
        'timestamp': datetime.now().isoformat()
    }

# ============================================================================
# CONFIGURATION UTILITIES
# ============================================================================

@dataclass
class AppConfig:
    """Application configuration dataclass"""
    debug: bool = False
    host: str = "localhost"
    port: int = 5000
    secret_key: str = "your-secret-key-here"
    database_path: str = "data/sqlite/sample.db"
    upload_folder: str = "uploads"
    max_file_size: int = 16 * 1024 * 1024  # 16MB
    supported_languages: List[str] = None
    
    def __post_init__(self):
        if self.supported_languages is None:
            self.supported_languages = list(SUPPORTED_LANGUAGES.keys())

def load_config() -> AppConfig:
    """Load application configuration"""
    config_path = get_config_path()
    
    if config_path.exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
                return AppConfig(**config_data)
        except Exception as e:
            logger.error(f"Error loading config: {e}")
    
    # Return default configuration
    return AppConfig()

def save_config(config: AppConfig) -> bool:
    """Save application configuration"""
    try:
        config_path = get_config_path()
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(asdict(config), f, indent=2, ensure_ascii=False)
        
        return True
    except Exception as e:
        logger.error(f"Error saving config: {e}")
        return False

# ============================================================================
# INITIALIZATION
# ============================================================================

def initialize_application() -> None:
    """Initialize the application and create necessary directories"""
    # Create necessary directories
    directories = [
        get_data_path(),
        get_uploads_path(),
        get_models_path(),
        get_logs_path(),
        get_data_path() / "sqlite",
        get_uploads_path() / "chat-local"
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
    
    logger.info("Application directories initialized successfully")

# Initialize when module is imported
initialize_application()
