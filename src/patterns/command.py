"""
Command Pattern Implementation
Provides command pattern for database operations
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import logging
from enum import Enum

logger = logging.getLogger(__name__)

class CommandType(Enum):
    """Command types enumeration"""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    BULK_INSERT = "bulk_insert"
    BULK_UPDATE = "bulk_update"
    BULK_DELETE = "bulk_delete"
    CUSTOM = "custom"

class DatabaseCommand(ABC):
    """Abstract base class for database commands"""
    
    def __init__(self, command_type: CommandType, table_name: str = None):
        self.command_type = command_type
        self.table_name = table_name
        self.executed = False
        self.result = None
        self.error = None
    
    @abstractmethod
    def execute(self, **kwargs) -> bool:
        """Execute the command"""
        pass
    
    @abstractmethod
    def undo(self) -> bool:
        """Undo the command"""
        pass
    
    def get_result(self) -> Any:
        """Get command result"""
        return self.result
    
    def get_error(self) -> str:
        """Get command error"""
        return self.error

class CreateCommand(DatabaseCommand):
    """Create record command"""
    
    def __init__(self, table_name: str, data: Dict[str, Any]):
        super().__init__(CommandType.CREATE, table_name)
        self.data = data
        self.created_id = None
    
    def execute(self, **kwargs) -> bool:
        """Execute create command"""
        try:
            # Build INSERT query
            columns = list(self.data.keys())
            placeholders = ', '.join(['?' for _ in columns])
            values = list(self.data.values())
            
            query = f"INSERT INTO {self.table_name} ({', '.join(columns)}) VALUES ({placeholders})"
            
            # Execute query
            from src.database_adapter import get_database_adapter
            db = get_database_adapter()
            result = db.execute_query(query, tuple(values))
            
            self.created_id = result[0].get('id') if result else None
            self.result = result
            self.executed = True
            
            logger.info(f"Created record in {self.table_name} with ID: {self.created_id}")
            return True
            
        except Exception as e:
            self.error = str(e)
            logger.error(f"Error executing create command: {e}")
            return False
    
    def undo(self) -> bool:
        """Undo create command"""
        if not self.executed or not self.created_id:
            return False
        
        try:
            query = f"DELETE FROM {self.table_name} WHERE id = ?"
            from src.database_adapter import get_database_adapter
            db = get_database_adapter()
            result = db.execute_query(query, (self.created_id,))
            
            logger.info(f"Undid create command for record {self.created_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error undoing create command: {e}")
            return False

class ReadCommand(DatabaseCommand):
    """Read records command"""
    
    def __init__(self, table_name: str, conditions: Dict[str, Any] = None, limit: int = None):
        super().__init__(CommandType.READ, table_name)
        self.conditions = conditions or {}
        self.limit = limit
    
    def execute(self, **kwargs) -> bool:
        """Execute read command"""
        try:
            # Build SELECT query
            query = f"SELECT * FROM {self.table_name}"
            params = []
            
            if self.conditions:
                where_clauses = []
                for column, value in self.conditions.items():
                    where_clauses.append(f"{column} = ?")
                    params.append(value)
                
                if where_clauses:
                    query += " WHERE " + " AND ".join(where_clauses)
            
            if self.limit:
                query += f" LIMIT {self.limit}"
            
            # Execute query
            from src.database_adapter import get_database_adapter
            db = get_database_adapter()
            result = db.execute_query(query, tuple(params))
            
            self.result = result
            self.executed = True
            
            logger.info(f"Read {len(result)} records from {self.table_name}")
            return True
            
        except Exception as e:
            self.error = str(e)
            logger.error(f"Error executing read command: {e}")
            return False
    
    def undo(self) -> bool:
        """Read commands cannot be undone"""
        return True

class UpdateCommand(DatabaseCommand):
    """Update records command"""
    
    def __init__(self, table_name: str, data: Dict[str, Any], conditions: Dict[str, Any]):
        super().__init__(CommandType.UPDATE, table_name)
        self.data = data
        self.conditions = conditions
        self.old_data = None
    
    def execute(self, **kwargs) -> bool:
        """Execute update command"""
        try:
            # First, get old data for undo
            if self.conditions:
                where_clauses = []
                params = []
                for column, value in self.conditions.items():
                    where_clauses.append(f"{column} = ?")
                    params.append(value)
                
                select_query = f"SELECT * FROM {self.table_name} WHERE " + " AND ".join(where_clauses)
                from src.database_adapter import get_database_adapter
                db = get_database_adapter()
                self.old_data = db.execute_query(select_query, tuple(params))
            
            # Build UPDATE query
            set_clauses = []
            params = []
            
            for column, value in self.data.items():
                set_clauses.append(f"{column} = ?")
                params.append(value)
            
            query = f"UPDATE {self.table_name} SET {', '.join(set_clauses)}"
            
            if self.conditions:
                where_clauses = []
                for column, value in self.conditions.items():
                    where_clauses.append(f"{column} = ?")
                    params.append(value)
                
                query += " WHERE " + " AND ".join(where_clauses)
            
            # Execute query
            result = db.execute_query(query, tuple(params))
            
            self.result = result
            self.executed = True
            
            logger.info(f"Updated records in {self.table_name}")
            return True
            
        except Exception as e:
            self.error = str(e)
            logger.error(f"Error executing update command: {e}")
            return False
    
    def undo(self) -> bool:
        """Undo update command"""
        if not self.executed or not self.old_data:
            return False
        
        try:
            # Restore old data
            for old_record in self.old_data:
                set_clauses = []
                params = []
                
                for column, value in old_record.items():
                    if column != 'id':  # Don't update primary key
                        set_clauses.append(f"{column} = ?")
                        params.append(value)
                
                query = f"UPDATE {self.table_name} SET {', '.join(set_clauses)} WHERE id = ?"
                params.append(old_record['id'])
                
                from src.database_adapter import get_database_adapter
                db = get_database_adapter()
                db.execute_query(query, tuple(params))
            
            logger.info(f"Undid update command for {self.table_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error undoing update command: {e}")
            return False

class DeleteCommand(DatabaseCommand):
    """Delete records command"""
    
    def __init__(self, table_name: str, conditions: Dict[str, Any]):
        super().__init__(CommandType.DELETE, table_name)
        self.conditions = conditions
        self.deleted_data = None
    
    def execute(self, **kwargs) -> bool:
        """Execute delete command"""
        try:
            # First, get data to be deleted for undo
            if self.conditions:
                where_clauses = []
                params = []
                for column, value in self.conditions.items():
                    where_clauses.append(f"{column} = ?")
                    params.append(value)
                
                select_query = f"SELECT * FROM {self.table_name} WHERE " + " AND ".join(where_clauses)
                from src.database_adapter import get_database_adapter
                db = get_database_adapter()
                self.deleted_data = db.execute_query(select_query, tuple(params))
            
            # Build DELETE query
            query = f"DELETE FROM {self.table_name}"
            params = []
            
            if self.conditions:
                where_clauses = []
                for column, value in self.conditions.items():
                    where_clauses.append(f"{column} = ?")
                    params.append(value)
                
                query += " WHERE " + " AND ".join(where_clauses)
            
            # Execute query
            result = db.execute_query(query, tuple(params))
            
            self.result = result
            self.executed = True
            
            logger.info(f"Deleted records from {self.table_name}")
            return True
            
        except Exception as e:
            self.error = str(e)
            logger.error(f"Error executing delete command: {e}")
            return False
    
    def undo(self) -> bool:
        """Undo delete command"""
        if not self.executed or not self.deleted_data:
            return False
        
        try:
            # Restore deleted data
            for record in self.deleted_data:
                columns = list(record.keys())
                placeholders = ', '.join(['?' for _ in columns])
                values = list(record.values())
                
                query = f"INSERT INTO {self.table_name} ({', '.join(columns)}) VALUES ({placeholders})"
                
                from src.database_adapter import get_database_adapter
                db = get_database_adapter()
                db.execute_query(query, tuple(values))
            
            logger.info(f"Undid delete command for {self.table_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error undoing delete command: {e}")
            return False

class CommandInvoker:
    """Command invoker for executing and managing commands"""
    
    def __init__(self):
        self.command_history = []
        self.max_history = 100
    
    def execute_command(self, command: DatabaseCommand, **kwargs) -> bool:
        """Execute a command"""
        try:
            success = command.execute(**kwargs)
            
            if success:
                # Add to history for undo
                self.command_history.append(command)
                
                # Limit history size
                if len(self.command_history) > self.max_history:
                    self.command_history.pop(0)
            
            return success
            
        except Exception as e:
            logger.error(f"Error executing command: {e}")
            return False
    
    def undo_last_command(self) -> bool:
        """Undo the last executed command"""
        if not self.command_history:
            logger.warning("No commands to undo")
            return False
        
        try:
            last_command = self.command_history.pop()
            success = last_command.undo()
            
            if success:
                logger.info(f"Undid command: {last_command.command_type.value}")
            else:
                logger.error(f"Failed to undo command: {last_command.command_type.value}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error undoing command: {e}")
            return False
    
    def undo_all_commands(self) -> bool:
        """Undo all commands in history"""
        try:
            success_count = 0
            total_commands = len(self.command_history)
            
            while self.command_history:
                command = self.command_history.pop()
                if command.undo():
                    success_count += 1
            
            logger.info(f"Undid {success_count}/{total_commands} commands")
            return success_count == total_commands
            
        except Exception as e:
            logger.error(f"Error undoing all commands: {e}")
            return False
    
    def get_command_history(self) -> List[DatabaseCommand]:
        """Get command history"""
        return self.command_history.copy()
    
    def clear_history(self) -> None:
        """Clear command history"""
        self.command_history.clear()
        logger.info("Command history cleared")
    
    def get_history_stats(self) -> Dict[str, Any]:
        """Get command history statistics"""
        stats = {
            'total_commands': len(self.command_history),
            'command_types': {},
            'successful_commands': 0,
            'failed_commands': 0
        }
        
        for command in self.command_history:
            command_type = command.command_type.value
            stats['command_types'][command_type] = stats['command_types'].get(command_type, 0) + 1
            
            if command.executed and not command.error:
                stats['successful_commands'] += 1
            else:
                stats['failed_commands'] += 1
        
        return stats
