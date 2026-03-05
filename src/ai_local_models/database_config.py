#!/usr/bin/env python3
"""
Database Configuration and Testing Interface
Provides web interface for configuring and testing database connections
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path

from flask import Blueprint, request, jsonify, render_template, current_app
from .database_manager import GlobalDatabaseManager, db_manager
from .redis_cache_manager import RedisCacheManager, redis_cache
from .ai_safety_manager import AISafetyManager, ai_safety_manager

logger = logging.getLogger(__name__)

@dataclass
class DatabaseTestResult:
    """Result of database connection test"""
    database_name: str
    status: str  # 'success', 'failed', 'warning'
    message: str
    response_time: float = 0.0
    error_details: Optional[str] = None
    connection_info: Optional[Dict[str, Any]] = None

class DatabaseConfigInterface:
    """Web interface for database configuration and testing"""

    def __init__(self):
        self.db_manager = db_manager
        self.config_file = Path(".env")
        self.backup_file = Path(".env.backup")

    def test_database_connections(self) -> Dict[str, Any]:
        """Test all database connections and return results"""
        results = {}
        health_check = self.db_manager.health_check()

        for db_name, health_info in health_check.items():
            if health_info['status'] == 'healthy':
                results[db_name] = DatabaseTestResult(
                    database_name=db_name,
                    status='success',
                    message='Connection successful',
                    response_time=health_info.get('response_time', 0),
                    connection_info=self._get_connection_info(db_name)
                )
            else:
                results[db_name] = DatabaseTestResult(
                    database_name=db_name,
                    status='failed',
                    message=f"Connection failed: {health_info.get('error', 'Unknown error')}",
                    error_details=health_info.get('error')
                )

        return {
            'timestamp': datetime.now().isoformat(),
            'results': {k: asdict(v) for k, v in results.items()},
            'summary': {
                'total': len(results),
                'successful': len([r for r in results.values() if r.status == 'success']),
                'failed': len([r for r in results.values() if r.status == 'failed'])
            }
        }

    def _get_connection_info(self, db_name: str) -> Dict[str, Any]:
        """Get connection information for a database"""
        try:
            connection = self.db_manager.get_connection(db_name)
            config = connection.config

            return {
                'type': config.type,
                'host': config.host,
                'port': config.port,
                'database': config.database,
                'connection_string': config.get_connection_string()
            }
        except Exception as e:
            return {'error': str(e)}

    def get_database_config(self) -> Dict[str, Any]:
        """Get current database configuration from environment"""
        config = {}

        # Database type
        config['database_type'] = os.getenv('DATABASE_TYPE', 'sqlite')

        # Main database
        config['main_database'] = {
            'type': os.getenv('DB_TYPE', 'sqlite'),
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', '5432')),
            'database': os.getenv('DB_NAME', 'data/sqlite/app.db'),
            'username': os.getenv('DB_USER', ''),
            'password': os.getenv('DB_PASSWORD', ''),
            'ssl': os.getenv('DB_SSL', 'false').lower() == 'true',
            'timeout': int(os.getenv('DB_TIMEOUT', '30'))
        }

        # Embeddings database
        config['embeddings_database'] = {
            'type': os.getenv('EMBEDDINGS_DB_TYPE', 'postgresql'),
            'host': os.getenv('EMBEDDINGS_DB_HOST', 'localhost'),
            'port': int(os.getenv('EMBEDDINGS_DB_PORT', '5432')),
            'database': os.getenv('EMBEDDINGS_DB_NAME', 'ai_embeddings'),
            'username': os.getenv('EMBEDDINGS_DB_USER', ''),
            'password': os.getenv('EMBEDDINGS_DB_PASSWORD', ''),
            'ssl': os.getenv('EMBEDDINGS_DB_SSL', 'true').lower() == 'true',
            'timeout': int(os.getenv('EMBEDDINGS_DB_TIMEOUT', '60'))
        }

        # Analytics database
        config['analytics_database'] = {
            'type': os.getenv('ANALYTICS_DB_TYPE', 'sqlite'),
            'database': os.getenv('ANALYTICS_DB_NAME', 'data/sqlite/analytics.db'),
            'timeout': int(os.getenv('ANALYTICS_DB_TIMEOUT', '30'))
        }

        return config

    def update_database_config(self, new_config: Dict[str, Any]) -> Tuple[bool, str]:
        """Update database configuration and save to .env file"""
        try:
            # Create backup of current .env file
            if self.config_file.exists():
                import shutil
                shutil.copy2(self.config_file, self.backup_file)
                logger.info("✅ Created backup of .env file")

            # Read current .env content
            env_content = {}
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            env_content[key] = value

            # Update with new configuration
            if 'database_type' in new_config:
                env_content['DATABASE_TYPE'] = new_config['database_type']

            # Update main database config
            if 'main_database' in new_config:
                main_db = new_config['main_database']
                env_content.update({
                    'DB_TYPE': main_db.get('type', 'sqlite'),
                    'DB_HOST': main_db.get('host', 'localhost'),
                    'DB_PORT': str(main_db.get('port', 5432)),
                    'DB_NAME': main_db.get('database', 'data/sqlite/app.db'),
                    'DB_USER': main_db.get('username', ''),
                    'DB_PASSWORD': main_db.get('password', ''),
                    'DB_SSL': str(main_db.get('ssl', False)).lower(),
                    'DB_TIMEOUT': str(main_db.get('timeout', 30))
                })

            # Update embeddings database config
            if 'embeddings_database' in new_config:
                emb_db = new_config['embeddings_database']
                env_content.update({
                    'EMBEDDINGS_DB_TYPE': emb_db.get('type', 'postgresql'),
                    'EMBEDDINGS_DB_HOST': emb_db.get('host', 'localhost'),
                    'EMBEDDINGS_DB_PORT': str(emb_db.get('port', 5432)),
                    'EMBEDDINGS_DB_NAME': emb_db.get('database', 'ai_embeddings'),
                    'EMBEDDINGS_DB_USER': emb_db.get('username', ''),
                    'EMBEDDINGS_DB_PASSWORD': emb_db.get('password', ''),
                    'EMBEDDINGS_DB_SSL': str(emb_db.get('ssl', True)).lower(),
                    'EMBEDDINGS_DB_TIMEOUT': str(emb_db.get('timeout', 60))
                })

            # Update analytics database config
            if 'analytics_database' in new_config:
                ana_db = new_config['analytics_database']
                env_content.update({
                    'ANALYTICS_DB_TYPE': ana_db.get('type', 'sqlite'),
                    'ANALYTICS_DB_NAME': ana_db.get('database', 'data/sqlite/analytics.db'),
                    'ANALYTICS_DB_TIMEOUT': str(ana_db.get('timeout', 30))
                })

            # Write updated configuration to .env file
            with open(self.config_file, 'w', encoding='utf-8') as f:
                f.write("# AI Local Models - Database Configuration\n")
                f.write(f"# Updated at: {datetime.now().isoformat()}\n\n")

                for key, value in env_content.items():
                    f.write(f"{key}={value}\n")

            logger.info("✅ Database configuration updated successfully")
            return True, "Configuration updated successfully. Restart the application to apply changes."

        except Exception as e:
            error_msg = f"Error updating configuration: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

    def test_specific_database(self, db_name: str) -> DatabaseTestResult:
        """Test a specific database connection"""
        try:
            connection = self.db_manager.get_connection(db_name)

            # Try to execute a simple query
            if connection.config.type == 'sqlite':
                result = connection.query("SELECT 1 as test")
                success = result is not None
            else:
                result = connection.query("SELECT 1 as test")
                success = result is not None

            if success:
                return DatabaseTestResult(
                    database_name=db_name,
                    status='success',
                    message='Connection successful',
                    connection_info=self._get_connection_info(db_name)
                )
            else:
                return DatabaseTestResult(
                    database_name=db_name,
                    status='failed',
                    message='Query failed'
                )

        except Exception as e:
            return DatabaseTestResult(
                database_name=db_name,
                status='failed',
                message=f'Connection failed: {str(e)}',
                error_details=str(e)
            )

    def get_database_stats(self) -> Dict[str, Any]:
        """Get comprehensive database statistics"""
        try:
            stats = self.db_manager.get_database_stats()
            return {
                'timestamp': datetime.now().isoformat(),
                'databases': stats,
                'system_info': {
                    'total_databases': len(stats),
                    'active_connections': len([s for s in stats.values() if s['status'] == 'connected']),
                    'total_tables': sum(s.get('tables', 0) for s in stats.values())
                }
            }
        except Exception as e:
            return {
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }

    def reset_to_defaults(self) -> Tuple[bool, str]:
        """Reset database configuration to defaults"""
        try:
            default_config = {
                'database_type': 'sqlite',
                'main_database': {
                    'type': 'sqlite',
                    'database': 'data/sqlite/app.db',
                    'timeout': 30
                },
                'embeddings_database': {
                    'type': 'postgresql',
                    'host': 'localhost',
                    'port': 5432,
                    'database': 'ai_embeddings',
                    'username': 'ai_user',
                    'password': 'secure_password_123',
                    'ssl': True,
                    'timeout': 60
                },
                'analytics_database': {
                    'type': 'sqlite',
                    'database': 'data/sqlite/analytics.db',
                    'timeout': 30
                }
            }

            return self.update_database_config(default_config)

        except Exception as e:
            return False, f"Error resetting to defaults: {str(e)}"

# Global instance
db_config_interface = DatabaseConfigInterface()

# Flask Blueprint for database configuration routes
database_config_bp = Blueprint('database_config', __name__, url_prefix='/api/database')

@database_config_bp.route('/test', methods=['GET'])
def test_all_databases():
    """Test all database connections"""
    try:
        results = db_config_interface.test_database_connections()
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@database_config_bp.route('/test/<db_name>', methods=['GET'])
def test_database(db_name):
    """Test specific database connection"""
    try:
        result = db_config_interface.test_specific_database(db_name)
        return jsonify(asdict(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@database_config_bp.route('/config', methods=['GET'])
def get_config():
    """Get current database configuration"""
    try:
        config = db_config_interface.get_database_config()
        return jsonify(config)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@database_config_bp.route('/config', methods=['POST'])
def update_config():
    """Update database configuration"""
    try:
        new_config = request.get_json()
        if not new_config:
            return jsonify({'error': 'No configuration data provided'}), 400

        success, message = db_config_interface.update_database_config(new_config)
        if success:
            return jsonify({'message': message})
        else:
            return jsonify({'error': message}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@database_config_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get database statistics"""
    try:
        stats = db_config_interface.get_database_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@database_config_bp.route('/reset', methods=['POST'])
def reset_config():
    """Reset database configuration to defaults"""
    try:
        success, message = db_config_interface.reset_to_defaults()
        if success:
            return jsonify({'message': message})
        else:
            return jsonify({'error': message}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@database_config_bp.route('/save-env', methods=['POST'])
def save_env_file():
    """Save content to .env file"""
    try:
        data = request.get_json()
        if not data or 'content' not in data:
            return jsonify({'error': 'No content provided'}), 400

        success, message = save_env_file_content(data['content'])
        if success:
            return jsonify({'message': message})
        else:
            return jsonify({'error': message}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@database_config_bp.route('/env-content', methods=['GET'])
def get_env_content():
    """Get current .env file content"""
    try:
        env_file = Path('.env')
        if env_file.exists():
            with open(env_file, 'r', encoding='utf-8') as f:
                content = f.read()
            return jsonify({'content': content})
        else:
            return jsonify({'content': '# .env file not found'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Settings page template integration
def get_database_settings_context():
    """Get context data for database settings page"""
    try:
        config = db_config_interface.get_database_config()
        test_results = db_config_interface.test_database_connections()
        stats = db_config_interface.get_database_stats()

        return {
            'database_config': config,
            'database_tests': test_results,
            'database_stats': stats,
            'current_env_content': _get_env_file_content()
        }
    except Exception as e:
        logger.error(f"Error getting database settings context: {e}")
        return {
            'database_config': {},
            'database_tests': {'error': str(e)},
            'database_stats': {'error': str(e)},
            'current_env_content': ''
        }

def _get_env_file_content():
    """Get current .env file content"""
    try:
        env_file = Path('.env')
        if env_file.exists():
            with open(env_file, 'r', encoding='utf-8') as f:
                return f.read()
        return "# .env file not found"
    except Exception as e:
        return f"# Error reading .env file: {e}"

def save_env_file_content(content: str) -> Tuple[bool, str]:
    """Save content to .env file"""
    try:
        env_file = Path('.env')

        # Create backup
        if env_file.exists():
            backup_file = env_file.with_suffix('.backup')
            import shutil
            shutil.copy2(env_file, backup_file)

        # Write new content
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(content)

        logger.info("✅ .env file updated successfully")
        return True, ".env file updated successfully. Restart the application to apply changes."

    except Exception as e:
        error_msg = f"Error saving .env file: {str(e)}"
        logger.error(error_msg)
        return False, error_msg
