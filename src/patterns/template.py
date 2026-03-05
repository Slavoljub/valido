"""
Template Method Pattern Implementation
Provides template method pattern for database operations
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class QueryTemplate(ABC):
    """Abstract base class for query templates"""
    
    def __init__(self, table_name: str):
        self.table_name = table_name
        self.result = None
        self.error = None
    
    def execute(self, **kwargs) -> bool:
        """Template method for executing queries"""
        try:
            # Template method steps
            self.validate_parameters(**kwargs)
            query = self.build_query(**kwargs)
            self.validate_query(query)
            self.result = self.execute_query(query, **kwargs)
            self.post_process_result(**kwargs)
            return True
            
        except Exception as e:
            self.error = str(e)
            logger.error(f"Error executing query template: {e}")
            return False
    
    @abstractmethod
    def validate_parameters(self, **kwargs) -> None:
        """Validate input parameters"""
        pass
    
    @abstractmethod
    def build_query(self, **kwargs) -> str:
        """Build the SQL query"""
        pass
    
    def validate_query(self, query: str) -> None:
        """Validate the generated query"""
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")
        
        # Basic SQL injection prevention
        dangerous_keywords = ['DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'CREATE']
        query_upper = query.upper()
        
        for keyword in dangerous_keywords:
            if keyword in query_upper and not self.is_safe_keyword(query_upper, keyword):
                raise ValueError(f"Potentially dangerous keyword '{keyword}' detected")
    
    def is_safe_keyword(self, query: str, keyword: str) -> bool:
        """Check if keyword usage is safe"""
        # This is a simplified check - in production, use proper SQL parsing
        return False
    
    def execute_query(self, query: str, **kwargs) -> Any:
        """Execute the query"""
        from src.database_adapter import get_database_adapter
        db = get_database_adapter()
        return db.execute_query(query, kwargs.get('params'))
    
    def post_process_result(self, **kwargs) -> None:
        """Post-process the query result"""
        pass
    
    def get_result(self) -> Any:
        """Get query result"""
        return self.result
    
    def get_error(self) -> str:
        """Get query error"""
        return self.error

class SelectTemplate(QueryTemplate):
    """Template for SELECT queries"""
    
    def __init__(self, table_name: str, columns: List[str] = None, conditions: Dict[str, Any] = None):
        super().__init__(table_name)
        self.columns = columns or ['*']
        self.conditions = conditions or {}
    
    def validate_parameters(self, **kwargs) -> None:
        """Validate SELECT parameters"""
        if not self.table_name:
            raise ValueError("Table name is required")
        
        if self.columns and not isinstance(self.columns, list):
            raise ValueError("Columns must be a list")
    
    def build_query(self, **kwargs) -> str:
        """Build SELECT query"""
        columns_str = ', '.join(self.columns)
        query = f"SELECT {columns_str} FROM {self.table_name}"
        
        if self.conditions:
            where_clauses = []
            for column, value in self.conditions.items():
                if isinstance(value, str):
                    where_clauses.append(f"{column} = '{value}'")
                else:
                    where_clauses.append(f"{column} = {value}")
            
            if where_clauses:
                query += " WHERE " + " AND ".join(where_clauses)
        
        # Add ORDER BY if specified
        if 'order_by' in kwargs:
            query += f" ORDER BY {kwargs['order_by']}"
        
        # Add LIMIT if specified
        if 'limit' in kwargs:
            query += f" LIMIT {kwargs['limit']}"
        
        return query

class InsertTemplate(QueryTemplate):
    """Template for INSERT queries"""
    
    def __init__(self, table_name: str, data: Dict[str, Any]):
        super().__init__(table_name)
        self.data = data
    
    def validate_parameters(self, **kwargs) -> None:
        """Validate INSERT parameters"""
        if not self.table_name:
            raise ValueError("Table name is required")
        
        if not self.data or not isinstance(self.data, dict):
            raise ValueError("Data must be a non-empty dictionary")
    
    def build_query(self, **kwargs) -> str:
        """Build INSERT query"""
        columns = list(self.data.keys())
        values = list(self.data.values())
        
        columns_str = ', '.join(columns)
        placeholders = ', '.join(['?' for _ in values])
        
        query = f"INSERT INTO {self.table_name} ({columns_str}) VALUES ({placeholders})"
        
        # Store parameters for execution
        kwargs['params'] = tuple(values)
        return query

class UpdateTemplate(QueryTemplate):
    """Template for UPDATE queries"""
    
    def __init__(self, table_name: str, data: Dict[str, Any], conditions: Dict[str, Any]):
        super().__init__(table_name)
        self.data = data
        self.conditions = conditions
    
    def validate_parameters(self, **kwargs) -> None:
        """Validate UPDATE parameters"""
        if not self.table_name:
            raise ValueError("Table name is required")
        
        if not self.data or not isinstance(self.data, dict):
            raise ValueError("Data must be a non-empty dictionary")
        
        if not self.conditions or not isinstance(self.conditions, dict):
            raise ValueError("Conditions must be a non-empty dictionary")
    
    def build_query(self, **kwargs) -> str:
        """Build UPDATE query"""
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
        
        # Store parameters for execution
        kwargs['params'] = tuple(params)
        return query

class DeleteTemplate(QueryTemplate):
    """Template for DELETE queries"""
    
    def __init__(self, table_name: str, conditions: Dict[str, Any]):
        super().__init__(table_name)
        self.conditions = conditions
    
    def validate_parameters(self, **kwargs) -> None:
        """Validate DELETE parameters"""
        if not self.table_name:
            raise ValueError("Table name is required")
        
        if not self.conditions or not isinstance(self.conditions, dict):
            raise ValueError("Conditions must be a non-empty dictionary")
    
    def build_query(self, **kwargs) -> str:
        """Build DELETE query"""
        query = f"DELETE FROM {self.table_name}"
        params = []
        
        if self.conditions:
            where_clauses = []
            for column, value in self.conditions.items():
                where_clauses.append(f"{column} = ?")
                params.append(value)
            
            query += " WHERE " + " AND ".join(where_clauses)
        
        # Store parameters for execution
        kwargs['params'] = tuple(params)
        return query

class TemplateMethod:
    """Template method manager for database operations"""
    
    def __init__(self):
        self.templates = {}
        self.query_history = []
    
    def register_template(self, name: str, template: QueryTemplate) -> None:
        """Register a query template"""
        self.templates[name] = template
        logger.info(f"Registered template: {name}")
    
    def execute_template(self, name: str, **kwargs) -> bool:
        """Execute a registered template"""
        if name not in self.templates:
            logger.error(f"Template '{name}' not found")
            return False
        
        try:
            template = self.templates[name]
            success = template.execute(**kwargs)
            
            if success:
                self.query_history.append({
                    'name': name,
                    'template': template,
                    'result': template.get_result(),
                    'timestamp': self._get_timestamp()
                })
            
            return success
            
        except Exception as e:
            logger.error(f"Error executing template '{name}': {e}")
            return False
    
    def create_select_template(self, table_name: str, columns: List[str] = None, 
                             conditions: Dict[str, Any] = None) -> SelectTemplate:
        """Create a SELECT template"""
        return SelectTemplate(table_name, columns, conditions)
    
    def create_insert_template(self, table_name: str, data: Dict[str, Any]) -> InsertTemplate:
        """Create an INSERT template"""
        return InsertTemplate(table_name, data)
    
    def create_update_template(self, table_name: str, data: Dict[str, Any], 
                             conditions: Dict[str, Any]) -> UpdateTemplate:
        """Create an UPDATE template"""
        return UpdateTemplate(table_name, data, conditions)
    
    def create_delete_template(self, table_name: str, conditions: Dict[str, Any]) -> DeleteTemplate:
        """Create a DELETE template"""
        return DeleteTemplate(table_name, conditions)
    
    def get_template(self, name: str) -> Optional[QueryTemplate]:
        """Get a registered template"""
        return self.templates.get(name)
    
    def list_templates(self) -> List[str]:
        """List all registered templates"""
        return list(self.templates.keys())
    
    def remove_template(self, name: str) -> bool:
        """Remove a registered template"""
        if name in self.templates:
            del self.templates[name]
            logger.info(f"Removed template: {name}")
            return True
        return False
    
    def get_query_history(self) -> List[Dict[str, Any]]:
        """Get query execution history"""
        return self.query_history.copy()
    
    def clear_history(self) -> None:
        """Clear query history"""
        self.query_history.clear()
        logger.info("Query history cleared")
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def get_template_stats(self) -> Dict[str, Any]:
        """Get template usage statistics"""
        stats = {
            'total_templates': len(self.templates),
            'total_executions': len(self.query_history),
            'template_usage': {},
            'successful_executions': 0,
            'failed_executions': 0
        }
        
        for execution in self.query_history:
            template_name = execution['name']
            stats['template_usage'][template_name] = stats['template_usage'].get(template_name, 0) + 1
            
            if execution['result'] is not None:
                stats['successful_executions'] += 1
            else:
                stats['failed_executions'] += 1
        
        return stats
