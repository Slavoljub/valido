"""
MySQL Database Adapter
Provides MySQL-specific database operations
"""

import os
import logging
import mysql.connector
from mysql.connector import Error
from typing import Optional, Dict, Any, List
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class MySQLAdapter:
    """MySQL database adapter"""
    
    def __init__(self, host: str = 'localhost', port: int = 3306, 
                 database: str = 'validoai', user: str = 'root', 
                 password: str = 'root', charset: str = 'utf8mb4'):
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.charset = charset
        self.connection = None
        self.pool = None
        
    def connect(self) -> bool:
        """Connect to MySQL database"""
        try:
            if not self.connection or not self.connection.is_connected():
                self.connection = mysql.connector.connect(
                    host=self.host,
                    port=self.port,
                    database=self.database,
                    user=self.user,
                    password=self.password,
                    charset=self.charset,
                    autocommit=True,
                    pool_name="validoai_pool",
                    pool_size=5
                )
                logger.info(f"Connected to MySQL database: {self.database} on {self.host}:{self.port}")
                return True
        except Error as e:
            logger.error(f"Error connecting to MySQL: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from MySQL database"""
        try:
            if self.connection and self.connection.is_connected():
                self.connection.close()
                self.connection = None
                logger.info("Disconnected from MySQL database")
        except Error as e:
            logger.error(f"Error disconnecting from MySQL: {e}")
    
    @contextmanager
    def get_cursor(self):
        """Get database cursor with automatic cleanup"""
        cursor = None
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
            cursor = self.connection.cursor(dictionary=True)
            yield cursor
        except Error as e:
            logger.error(f"Database error: {e}")
            if cursor:
                cursor.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """Execute a query and return results"""
        try:
            with self.get_cursor() as cursor:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                if query.strip().upper().startswith('SELECT'):
                    return cursor.fetchall()
                else:
                    self.connection.commit()
                    return [{'affected_rows': cursor.rowcount}]
        except Error as e:
            logger.error(f"Error executing query: {e}")
            return []
    
    def get_tables(self) -> List[str]:
        """Get list of tables in the database"""
        try:
            query = "SHOW TABLES"
            results = self.execute_query(query)
            return [list(row.values())[0] for row in results]
        except Error as e:
            logger.error(f"Error getting tables: {e}")
            return []
    
    def get_table_info(self, table_name: str) -> List[Dict[str, Any]]:
        """Get table structure information"""
        try:
            query = f"DESCRIBE {table_name}"
            return self.execute_query(query)
        except Error as e:
            logger.error(f"Error getting table info: {e}")
            return []
    
    def get_table_data(self, table_name: str, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get data from a table with pagination"""
        try:
            query = f"SELECT * FROM {table_name} LIMIT {limit} OFFSET {offset}"
            return self.execute_query(query)
        except Error as e:
            logger.error(f"Error getting table data: {e}")
            return []
    
    def insert_record(self, table_name: str, data: Dict[str, Any]) -> bool:
        """Insert a record into a table"""
        try:
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['%s' for _ in data])
            query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
            
            result = self.execute_query(query, tuple(data.values()))
            return len(result) > 0
        except Error as e:
            logger.error(f"Error inserting record: {e}")
            return False
    
    def update_record(self, table_name: str, record_id: int, data: Dict[str, Any], id_column: str = 'id') -> bool:
        """Update a record in a table"""
        try:
            set_clause = ', '.join([f"{k} = %s" for k in data.keys()])
            query = f"UPDATE {table_name} SET {set_clause} WHERE {id_column} = %s"
            
            values = list(data.values()) + [record_id]
            result = self.execute_query(query, tuple(values))
            return len(result) > 0
        except Error as e:
            logger.error(f"Error updating record: {e}")
            return False
    
    def delete_record(self, table_name: str, record_id: int, id_column: str = 'id') -> bool:
        """Delete a record from a table"""
        try:
            query = f"DELETE FROM {table_name} WHERE {id_column} = %s"
            result = self.execute_query(query, (record_id,))
            return len(result) > 0
        except Error as e:
            logger.error(f"Error deleting record: {e}")
            return False
    
    def get_record_count(self, table_name: str) -> int:
        """Get the number of records in a table"""
        try:
            query = f"SELECT COUNT(*) as count FROM {table_name}"
            result = self.execute_query(query)
            return result[0]['count'] if result else 0
        except Error as e:
            logger.error(f"Error getting record count: {e}")
            return 0
    
    def search_records(self, table_name: str, search_term: str, columns: List[str] = None) -> List[Dict[str, Any]]:
        """Search records in a table"""
        try:
            if not columns:
                # Get all columns for the table
                table_info = self.get_table_info(table_name)
                columns = [col['Field'] for col in table_info]
            
            search_conditions = []
            params = []
            
            for column in columns:
                search_conditions.append(f"{column} LIKE %s")
                params.append(f"%{search_term}%")
            
            where_clause = " OR ".join(search_conditions)
            query = f"SELECT * FROM {table_name} WHERE {where_clause}"
            
            return self.execute_query(query, tuple(params))
        except Error as e:
            logger.error(f"Error searching records: {e}")
            return []
    
    def create_table(self, table_name: str, columns: List[Dict[str, str]]) -> bool:
        """Create a new table"""
        try:
            column_definitions = []
            for col in columns:
                col_def = f"{col['name']} {col['type']}"
                if col.get('primary_key'):
                    col_def += " PRIMARY KEY"
                if col.get('auto_increment'):
                    col_def += " AUTO_INCREMENT"
                if col.get('not_null'):
                    col_def += " NOT NULL"
                if col.get('default'):
                    col_def += f" DEFAULT {col['default']}"
                column_definitions.append(col_def)
            
            query = f"CREATE TABLE {table_name} ({', '.join(column_definitions)})"
            result = self.execute_query(query)
            return len(result) > 0
        except Error as e:
            logger.error(f"Error creating table: {e}")
            return False
    
    def drop_table(self, table_name: str) -> bool:
        """Drop a table"""
        try:
            query = f"DROP TABLE {table_name}"
            result = self.execute_query(query)
            return len(result) > 0
        except Error as e:
            logger.error(f"Error dropping table: {e}")
            return False
    
    def backup_database(self, backup_path: str) -> bool:
        """Create a backup of the database"""
        try:
            import subprocess
            import datetime
            
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = f"{backup_path}/validoai_backup_{timestamp}.sql"
            
            # Create backup directory if it doesn't exist
            os.makedirs(backup_path, exist_ok=True)
            
            # Use mysqldump to create backup
            cmd = [
                'mysqldump',
                f'--host={self.host}',
                f'--port={self.port}',
                f'--user={self.user}',
                f'--password={self.password}',
                '--single-transaction',
                '--routines',
                '--triggers',
                self.database
            ]
            
            with open(backup_file, 'w') as f:
                subprocess.run(cmd, stdout=f, check=True)
            
            logger.info(f"Database backed up to: {backup_file}")
            return True
        except Exception as e:
            logger.error(f"Error backing up database: {e}")
            return False
    
    def get_database_info(self) -> Dict[str, Any]:
        """Get database information"""
        try:
            info = {
                'type': 'mysql',
                'host': self.host,
                'port': self.port,
                'database': self.database,
                'user': self.user,
                'tables': self.get_tables(),
                'total_tables': len(self.get_tables()),
                'connected': self.connection and self.connection.is_connected()
            }
            
            # Get database size
            try:
                size_query = """
                SELECT 
                    ROUND(SUM(data_length + index_length) / 1024 / 1024, 1) AS 'DB Size in MB'
                FROM information_schema.tables 
                WHERE table_schema = %s
                """
                size_result = self.execute_query(size_query, (self.database,))
                if size_result:
                    info['size_mb'] = size_result[0]['DB Size in MB']
            except:
                info['size_mb'] = 'Unknown'
            
            return info
        except Error as e:
            logger.error(f"Error getting database info: {e}")
            return {'type': 'mysql', 'error': str(e)}
    
    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            return self.connect()
        except Error as e:
            logger.error(f"Connection test failed: {e}")
            return False
