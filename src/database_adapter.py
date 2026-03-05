"""
Database Adapter
Provides unified interface for different database types
"""

import os
import logging
import sqlite3
from typing import Optional, Dict, Any, List
from pathlib import Path

logger = logging.getLogger(__name__)

class DatabaseAdapter:
    """Unified database adapter for different database types"""
    
    def __init__(self, db_type: str = 'sqlite', **kwargs):
        self.db_type = db_type
        self.connection = None
        self.config = kwargs
        
        # Ensure data directory exists
        self.data_dir = Path('data/sqlite')
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize MySQL adapter if needed
        if db_type == 'mysql':
            try:
                from src.database.mysql_adapter import MySQLAdapter
                self.mysql_adapter = MySQLAdapter(
                    host=kwargs.get('host', 'localhost'),
                    port=kwargs.get('port', 3306),
                    database=kwargs.get('database', 'validoai'),
                    user=kwargs.get('user', 'root'),
                    password=kwargs.get('password', 'root')
                )
            except ImportError:
                logger.error("MySQL connector not installed. Install with: pip install mysql-connector-python")
                self.mysql_adapter = None
    
    def connect(self) -> bool:
        """Connect to the database"""
        try:
            if self.db_type == 'sqlite':
                db_path = self.data_dir / 'app.db'
                self.connection = sqlite3.connect(str(db_path))
                self.connection.row_factory = sqlite3.Row
                logger.info(f"Connected to SQLite database: {db_path}")
                return True
            elif self.db_type == 'mysql':
                if self.mysql_adapter:
                    return self.mysql_adapter.connect()
                else:
                    logger.error("MySQL adapter not available")
                    return False
            else:
                logger.error(f"Unsupported database type: {self.db_type}")
                return False
        except Exception as e:
            logger.error(f"Error connecting to database: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from the database"""
        if self.db_type == 'sqlite':
            if self.connection:
                self.connection.close()
                self.connection = None
                logger.info("Disconnected from SQLite database")
        elif self.db_type == 'mysql':
            if self.mysql_adapter:
                self.mysql_adapter.disconnect()
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """Execute a query and return results"""
        try:
            if self.db_type == 'sqlite':
                if not self.connection:
                    if not self.connect():
                        return []
                
                cursor = self.connection.cursor()
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                if query.strip().upper().startswith('SELECT'):
                    results = []
                    for row in cursor.fetchall():
                        results.append(dict(row))
                    return results
                else:
                    self.connection.commit()
                    return [{'affected_rows': cursor.rowcount}]
            elif self.db_type == 'mysql':
                if self.mysql_adapter:
                    return self.mysql_adapter.execute_query(query, params)
                else:
                    return []
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            return []
    
    def get_tables(self) -> List[str]:
        """Get list of tables in the database"""
        try:
            if self.db_type == 'sqlite':
                query = "SELECT name FROM sqlite_master WHERE type='table'"
                results = self.execute_query(query)
                return [row['name'] for row in results if row['name'] != 'sqlite_sequence']
            elif self.db_type == 'mysql':
                if self.mysql_adapter:
                    return self.mysql_adapter.get_tables()
                else:
                    return []
            else:
                return []
        except Exception as e:
            logger.error(f"Error getting tables: {e}")
            return []
    
    def get_table_info(self, table_name: str) -> List[Dict[str, Any]]:
        """Get table structure information"""
        try:
            if self.db_type == 'sqlite':
                query = f"PRAGMA table_info({table_name})"
                return self.execute_query(query)
            elif self.db_type == 'mysql':
                if self.mysql_adapter:
                    return self.mysql_adapter.get_table_info(table_name)
                else:
                    return []
            else:
                return []
        except Exception as e:
            logger.error(f"Error getting table info: {e}")
            return []
    
    def get_table_data(self, table_name: str, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get data from a table with pagination"""
        try:
            if self.db_type == 'sqlite':
                query = f"SELECT * FROM {table_name} LIMIT {limit} OFFSET {offset}"
                return self.execute_query(query)
            elif self.db_type == 'mysql':
                if self.mysql_adapter:
                    return self.mysql_adapter.get_table_data(table_name, limit, offset)
                else:
                    return []
            else:
                return []
        except Exception as e:
            logger.error(f"Error getting table data: {e}")
            return []
    
    def insert_record(self, table_name: str, data: Dict[str, Any]) -> bool:
        """Insert a record into a table"""
        try:
            if self.db_type == 'sqlite':
                columns = ', '.join(data.keys())
                placeholders = ', '.join(['?' for _ in data])
                query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
                
                result = self.execute_query(query, tuple(data.values()))
                return len(result) > 0
            elif self.db_type == 'mysql':
                if self.mysql_adapter:
                    return self.mysql_adapter.insert_record(table_name, data)
                else:
                    return False
            else:
                return False
        except Exception as e:
            logger.error(f"Error inserting record: {e}")
            return False
    
    def update_record(self, table_name: str, record_id: int, data: Dict[str, Any], id_column: str = 'id') -> bool:
        """Update a record in a table"""
        try:
            if self.db_type == 'sqlite':
                set_clause = ', '.join([f"{k} = ?" for k in data.keys()])
                query = f"UPDATE {table_name} SET {set_clause} WHERE {id_column} = ?"
                
                values = list(data.values()) + [record_id]
                result = self.execute_query(query, tuple(values))
                return len(result) > 0
            elif self.db_type == 'mysql':
                if self.mysql_adapter:
                    return self.mysql_adapter.update_record(table_name, record_id, data, id_column)
                else:
                    return False
            else:
                return False
        except Exception as e:
            logger.error(f"Error updating record: {e}")
            return False
    
    def delete_record(self, table_name: str, record_id: int, id_column: str = 'id') -> bool:
        """Delete a record from a table"""
        try:
            if self.db_type == 'sqlite':
                query = f"DELETE FROM {table_name} WHERE {id_column} = ?"
                result = self.execute_query(query, (record_id,))
                return len(result) > 0
            elif self.db_type == 'mysql':
                if self.mysql_adapter:
                    return self.mysql_adapter.delete_record(table_name, record_id, id_column)
                else:
                    return False
            else:
                return False
        except Exception as e:
            logger.error(f"Error deleting record: {e}")
            return False
    
    def get_record_count(self, table_name: str) -> int:
        """Get the number of records in a table"""
        try:
            if self.db_type == 'sqlite':
                query = f"SELECT COUNT(*) as count FROM {table_name}"
                result = self.execute_query(query)
                return result[0]['count'] if result else 0
            elif self.db_type == 'mysql':
                if self.mysql_adapter:
                    return self.mysql_adapter.get_record_count(table_name)
                else:
                    return 0
            else:
                return 0
        except Exception as e:
            logger.error(f"Error getting record count: {e}")
            return 0
    
    def search_records(self, table_name: str, search_term: str, columns: List[str] = None) -> List[Dict[str, Any]]:
        """Search records in a table"""
        try:
            if self.db_type == 'sqlite':
                if not columns:
                    # Get all columns for the table
                    table_info = self.get_table_info(table_name)
                    columns = [col['name'] for col in table_info]
                
                search_conditions = []
                params = []
                
                for column in columns:
                    search_conditions.append(f"{column} LIKE ?")
                    params.append(f"%{search_term}%")
                
                where_clause = " OR ".join(search_conditions)
                query = f"SELECT * FROM {table_name} WHERE {where_clause}"
                
                return self.execute_query(query, tuple(params))
            elif self.db_type == 'mysql':
                if self.mysql_adapter:
                    return self.mysql_adapter.search_records(table_name, search_term, columns)
                else:
                    return []
            else:
                return []
        except Exception as e:
            logger.error(f"Error searching records: {e}")
            return []
    
    def create_table(self, table_name: str, columns: List[Dict[str, str]]) -> bool:
        """Create a new table"""
        try:
            if self.db_type == 'sqlite':
                column_definitions = []
                for col in columns:
                    col_def = f"{col['name']} {col['type']}"
                    if col.get('primary_key'):
                        col_def += " PRIMARY KEY"
                    if col.get('not_null'):
                        col_def += " NOT NULL"
                    if col.get('default'):
                        col_def += f" DEFAULT {col['default']}"
                    column_definitions.append(col_def)
                
                query = f"CREATE TABLE {table_name} ({', '.join(column_definitions)})"
                result = self.execute_query(query)
                return len(result) > 0
            elif self.db_type == 'mysql':
                if self.mysql_adapter:
                    return self.mysql_adapter.create_table(table_name, columns)
                else:
                    return False
            else:
                return False
        except Exception as e:
            logger.error(f"Error creating table: {e}")
            return False
    
    def drop_table(self, table_name: str) -> bool:
        """Drop a table"""
        try:
            if self.db_type == 'sqlite':
                query = f"DROP TABLE {table_name}"
                result = self.execute_query(query)
                return len(result) > 0
            elif self.db_type == 'mysql':
                if self.mysql_adapter:
                    return self.mysql_adapter.drop_table(table_name)
                else:
                    return False
            else:
                return False
        except Exception as e:
            logger.error(f"Error dropping table: {e}")
            return False
    
    def backup_database(self, backup_path: str) -> bool:
        """Create a backup of the database"""
        try:
            if self.db_type == 'sqlite':
                import shutil
                db_path = self.data_dir / 'app.db'
                shutil.copy2(db_path, backup_path)
                logger.info(f"Database backed up to: {backup_path}")
                return True
            elif self.db_type == 'mysql':
                if self.mysql_adapter:
                    return self.mysql_adapter.backup_database(backup_path)
                else:
                    return False
            else:
                logger.error(f"Backup not supported for database type: {self.db_type}")
                return False
        except Exception as e:
            logger.error(f"Error backing up database: {e}")
            return False
    
    def get_database_info(self) -> Dict[str, Any]:
        """Get database information"""
        try:
            if self.db_type == 'sqlite':
                info = {
                    'type': self.db_type,
                    'tables': self.get_tables(),
                    'total_tables': len(self.get_tables())
                }
                
                db_path = self.data_dir / 'app.db'
                info['path'] = str(db_path)
                info['exists'] = db_path.exists()
                if db_path.exists():
                    info['size'] = db_path.stat().st_size
                    info['modified'] = db_path.stat().st_mtime
                
                return info
            elif self.db_type == 'mysql':
                if self.mysql_adapter:
                    return self.mysql_adapter.get_database_info()
                else:
                    return {'type': 'mysql', 'error': 'MySQL adapter not available'}
            else:
                return {'type': self.db_type, 'error': 'Unsupported database type'}
        except Exception as e:
            logger.error(f"Error getting database info: {e}")
            return {'type': self.db_type, 'error': str(e)}
    
    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            if self.db_type == 'sqlite':
                return self.connect()
            elif self.db_type == 'mysql':
                if self.mysql_adapter:
                    return self.mysql_adapter.test_connection()
                else:
                    return False
            else:
                return False
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False

# Global database adapter instance
_db_adapter = None

def get_database_connection() -> Optional[DatabaseAdapter]:
    """Get database connection"""
    global _db_adapter
    
    if _db_adapter is None:
        db_type = os.getenv('DB_TYPE', 'sqlite')
        
        if db_type == 'mysql':
            _db_adapter = DatabaseAdapter(
                db_type=db_type,
                host=os.getenv('DB_HOST', 'localhost'),
                port=int(os.getenv('DB_PORT', '3306')),
                database=os.getenv('DB_NAME', 'validoai'),
                user=os.getenv('DB_USER', 'root'),
                password=os.getenv('DB_PASSWORD', 'root')
            )
        else:
            _db_adapter = DatabaseAdapter(db_type)
    
    return _db_adapter

def get_database_adapter() -> DatabaseAdapter:
    """Get database adapter instance"""
    return get_database_connection()

def close_database_connection():
    """Close database connection"""
    global _db_adapter
    
    if _db_adapter:
        _db_adapter.disconnect()
        _db_adapter = None
