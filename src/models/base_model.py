"""
Base Model Class
Provides a foundation for all models in the application
"""

from datetime import datetime
from typing import Dict, Any, List, Optional, Type, TypeVar, Generic, ClassVar
import json
import uuid
from abc import ABC, abstractmethod

from src.core_config.event_manager import EventEmitter
from src.database.factory import DatabaseFactory, DatabaseConnection

T = TypeVar('T', bound='BaseModel')

class BaseModel(EventEmitter, ABC):
    """
    Abstract Base Model Class
    
    This class provides a foundation for all models in the application.
    It implements common functionality for CRUD operations, validation,
    serialization, and event emission.
    """
    
    # Class variables to be overridden by subclasses
    table_name: ClassVar[str] = ""
    db_type: ClassVar[str] = "mysql"
    primary_key: ClassVar[str] = "id"
    fields: ClassVar[List[str]] = []
    required_fields: ClassVar[List[str]] = []
    default_values: ClassVar[Dict[str, Any]] = {}
    
    def __init__(self, **kwargs):
        """
        Initialize a new model instance
        
        Args:
            **kwargs: Initial values for model fields
        """
        super().__init__()
        
        # Set default values
        for field, value in self.default_values.items():
            setattr(self, field, value)
        
        # Set provided values
        for field, value in kwargs.items():
            if field in self.fields or not self.fields:
                setattr(self, field, value)
    
    @classmethod
    def get_db_connection(cls) -> DatabaseConnection:
        """
        Get a database connection for this model
        
        Returns:
            DatabaseConnection: The database connection
        """
        return DatabaseFactory.get_connection(cls.db_type)
    
    @classmethod
    def find_by_id(cls: Type[T], record_id: Any) -> Optional[T]:
        """
        Find a record by ID
        
        Args:
            record_id: The record ID
            
        Returns:
            Optional[T]: The model instance or None if not found
        """
        db = cls.get_db_connection()
        try:
            if cls.db_type in ['mysql', 'postgres', 'sqlite']:
                query = f"SELECT * FROM {cls.table_name} WHERE {cls.primary_key} = %s"
                rows = db.fetch_all(query, [record_id])
            elif cls.db_type == 'mongodb':
                rows = db.fetch_all(cls.table_name, {cls.primary_key: record_id})
            else:
                # Redis or other NoSQL
                rows = []
                data = db.fetch_one(f"{cls.table_name}:{record_id}")
                if data:
                    rows = [data]
            
            if rows and len(rows) > 0:
                return cls(**rows[0])
            return None
        finally:
            db.disconnect()
    
    @classmethod
    def find_all(cls: Type[T], conditions: Dict[str, Any] = None) -> List[T]:
        """
        Find all records matching conditions
        
        Args:
            conditions: Dictionary of conditions (field=value)
            
        Returns:
            List[T]: List of model instances
        """
        db = cls.get_db_connection()
        try:
            if conditions is None:
                conditions = {}
            
            if cls.db_type in ['mysql', 'postgres', 'sqlite']:
                if conditions:
                    where_clause = ' AND '.join([f"{k} = %s" for k in conditions.keys()])
                    query = f"SELECT * FROM {cls.table_name} WHERE {where_clause}"
                    rows = db.fetch_all(query, list(conditions.values()))
                else:
                    query = f"SELECT * FROM {cls.table_name}"
                    rows = db.fetch_all(query)
            elif cls.db_type == 'mongodb':
                rows = db.fetch_all(cls.table_name, conditions)
            else:
                # Redis or other NoSQL - limited support for conditions
                rows = []
            
            return [cls(**row) for row in rows]
        finally:
            db.disconnect()
    
    @classmethod
    def find_one(cls: Type[T], conditions: Dict[str, Any]) -> Optional[T]:
        """
        Find one record matching conditions
        
        Args:
            conditions: Dictionary of conditions (field=value)
            
        Returns:
            Optional[T]: The model instance or None if not found
        """
        db = cls.get_db_connection()
        try:
            if cls.db_type in ['mysql', 'postgres', 'sqlite']:
                where_clause = ' AND '.join([f"{k} = %s" for k in conditions.keys()])
                query = f"SELECT * FROM {cls.table_name} WHERE {where_clause} LIMIT 1"
                row = db.fetch_one(query, list(conditions.values()))
            elif cls.db_type == 'mongodb':
                row = db.fetch_one(cls.table_name, conditions)
            else:
                # Redis or other NoSQL - limited support for conditions
                row = None
            
            if row:
                return cls(**row)
            return None
        finally:
            db.disconnect()
    
    @classmethod
    def count(cls, conditions: Dict[str, Any] = None) -> int:
        """
        Count records matching conditions
        
        Args:
            conditions: Dictionary of conditions (field=value)
            
        Returns:
            int: Number of records
        """
        db = cls.get_db_connection()
        try:
            if conditions is None:
                conditions = {}
            
            if cls.db_type in ['mysql', 'postgres', 'sqlite']:
                if conditions:
                    where_clause = ' AND '.join([f"{k} = %s" for k in conditions.keys()])
                    query = f"SELECT COUNT(*) as count FROM {cls.table_name} WHERE {where_clause}"
                    row = db.fetch_one(query, list(conditions.values()))
                else:
                    query = f"SELECT COUNT(*) as count FROM {cls.table_name}"
                    row = db.fetch_one(query)
                
                return row.get('count', 0) if row else 0
            elif cls.db_type == 'mongodb':
                return len(db.fetch_all(cls.table_name, conditions))
            else:
                # Redis or other NoSQL - limited support for counting
                return 0
        finally:
            db.disconnect()
    
    def save(self) -> bool:
        """
        Save the model to the database
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.validate():
            return False
        
        db = cls.get_db_connection()
        try:
            data = self.to_dict()
            
            # Remove primary key if it's None (for auto-increment)
            if self.primary_key in data and data[self.primary_key] is None:
                del data[self.primary_key]
            
            # Set created_at and updated_at if they exist in fields
            now = datetime.now().isoformat()
            if 'created_at' in self.fields and not hasattr(self, 'created_at'):
                data['created_at'] = now
            if 'updated_at' in self.fields:
                data['updated_at'] = now
            
            # Insert or update
            if not hasattr(self, self.primary_key) or getattr(self, self.primary_key) is None:
                # Insert
                record_id = db.insert(self.table_name, data)
                if record_id:
                    setattr(self, self.primary_key, record_id)
                    self.emit('after_create', self)
                    return True
            else:
                # Update
                record_id = getattr(self, self.primary_key)
                condition = {self.primary_key: record_id}
                success = db.update(self.table_name, data, condition)
                if success:
                    self.emit('after_update', self)
                    return True
            
            return False
        finally:
            db.disconnect()
    
    def delete(self) -> bool:
        """
        Delete the model from the database
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not hasattr(self, self.primary_key) or getattr(self, self.primary_key) is None:
            return False
        
        db = cls.get_db_connection()
        try:
            record_id = getattr(self, self.primary_key)
            condition = {self.primary_key: record_id}
            success = db.delete(self.table_name, condition)
            
            if success:
                self.emit('after_delete', self)
                return True
            
            return False
        finally:
            db.disconnect()
    
    def validate(self) -> bool:
        """
        Validate the model data
        
        Returns:
            bool: True if valid, False otherwise
        """
        # Check required fields
        for field in self.required_fields:
            if not hasattr(self, field) or getattr(self, field) is None:
                return False
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the model to a dictionary
        
        Returns:
            Dict[str, Any]: Dictionary representation of the model
        """
        data = {}
        
        if self.fields:
            # Only include defined fields
            for field in self.fields:
                if hasattr(self, field):
                    value = getattr(self, field)
                    # Convert datetime to ISO format
                    if isinstance(value, datetime):
                        value = value.isoformat()
                    data[field] = value
        else:
            # Include all attributes that don't start with underscore
            for attr in dir(self):
                if not attr.startswith('_') and not callable(getattr(self, attr)):
                    value = getattr(self, attr)
                    # Convert datetime to ISO format
                    if isinstance(value, datetime):
                        value = value.isoformat()
                    data[attr] = value
        
        return data
    
    def to_json(self) -> str:
        """
        Convert the model to JSON
        
        Returns:
            str: JSON representation of the model
        """
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        """
        Create a model instance from a dictionary
        
        Args:
            data: Dictionary of field values
            
        Returns:
            T: Model instance
        """
        return cls(**data)
    
    @classmethod
    def from_json(cls: Type[T], json_str: str) -> T:
        """
        Create a model instance from JSON
        
        Args:
            json_str: JSON string
            
        Returns:
            T: Model instance
        """
        data = json.loads(json_str)
        return cls.from_dict(data)
