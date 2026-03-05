"""
Repository Pattern Implementation for Data Access Layer
Provides abstraction layer for database operations
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import logging
from .observer import EventType, notify_event

logger = logging.getLogger(__name__)

class Repository(ABC):
    """Abstract base class for repository pattern"""
    
    @abstractmethod
    def find_all(self, filters: Dict[str, Any] = None, 
                 order_by: str = None, limit: int = None, 
                 offset: int = None) -> List[Dict[str, Any]]:
        """Find all records with optional filtering and pagination"""
        pass
    
    @abstractmethod
    def find_by_id(self, record_id: Any) -> Optional[Dict[str, Any]]:
        """Find record by ID"""
        pass
    
    @abstractmethod
    def create(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create new record"""
        pass
    
    @abstractmethod
    def update(self, record_id: Any, data: Dict[str, Any]) -> bool:
        """Update existing record"""
        pass
    
    @abstractmethod
    def delete(self, record_id: Any) -> bool:
        """Delete record by ID"""
        pass
    
    @abstractmethod
    def count(self, filters: Dict[str, Any] = None) -> int:
        """Count records with optional filtering"""
        pass
    
    @abstractmethod
    def exists(self, record_id: Any) -> bool:
        """Check if record exists"""
        pass

class BaseRepository(Repository):
    """Base repository implementation with common functionality"""
    
    def __init__(self, table_name: str, primary_key: str = 'id', 
                 database_adapter=None, user_id: str = None):
        self.table_name = table_name
        self.primary_key = primary_key
        self.database_adapter = database_adapter
        self.user_id = user_id
    
    def find_all(self, filters: Dict[str, Any] = None, 
                 order_by: str = None, limit: int = None, 
                 offset: int = None) -> List[Dict[str, Any]]:
        """Find all records with optional filtering and pagination"""
        try:
            # Build query
            query = f"SELECT * FROM {self.table_name}"
            params = []
            
            # Add filters
            if filters:
                where_clauses = []
                for key, value in filters.items():
                    if self.database_adapter.db_type == 'mysql':
                        where_clauses.append(f"{key} = %s")
                    else:
                        where_clauses.append(f"{key} = ?")
                    params.append(value)
                
                if where_clauses:
                    query += " WHERE " + " AND ".join(where_clauses)
            
            # Add ordering
            if order_by:
                query += f" ORDER BY {order_by}"
            
            # Add pagination
            if limit is not None:
                query += f" LIMIT {limit}"
                if offset is not None:
                    query += f" OFFSET {offset}"
            
            # Execute query
            results = self.database_adapter.execute_query(query, tuple(params) if params else None)
            
            # Notify event
            notify_event(
                EventType.SELECT,
                table_name=self.table_name,
                data={'filters': filters, 'count': len(results)},
                user_id=self.user_id
            )
            
            return results
        except Exception as e:
            logger.error(f"Error in find_all for {self.table_name}: {e}")
            notify_event(
                EventType.ERROR,
                table_name=self.table_name,
                data={'error': str(e), 'operation': 'find_all'},
                user_id=self.user_id
            )
            return []
    
    def find_by_id(self, record_id: Any) -> Optional[Dict[str, Any]]:
        """Find record by ID"""
        try:
            if self.database_adapter.db_type == 'mysql':
                query = f"SELECT * FROM {self.table_name} WHERE {self.primary_key} = %s"
            else:
                query = f"SELECT * FROM {self.table_name} WHERE {self.primary_key} = ?"
            
            results = self.database_adapter.execute_query(query, (record_id,))
            
            if results:
                # Notify event
                notify_event(
                    EventType.SELECT,
                    table_name=self.table_name,
                    record_id=record_id,
                    user_id=self.user_id
                )
                return results[0]
            
            return None
        except Exception as e:
            logger.error(f"Error in find_by_id for {self.table_name}: {e}")
            notify_event(
                EventType.ERROR,
                table_name=self.table_name,
                record_id=record_id,
                data={'error': str(e), 'operation': 'find_by_id'},
                user_id=self.user_id
            )
            return None
    
    def create(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create new record"""
        try:
            # Remove primary key if it's auto-increment
            if self.primary_key in data and data[self.primary_key] is None:
                del data[self.primary_key]
            
            # Insert record
            success = self.database_adapter.insert_record(self.table_name, data)
            
            if success:
                # Get the created record
                # Find the record by the most unique field (excluding auto-increment ID)
                unique_fields = [k for k, v in data.items() if v is not None and k != self.primary_key]
                if unique_fields:
                    # Use the first unique field to find the record
                    field_name = unique_fields[0]
                    field_value = data[field_name]
                    
                    if self.database_adapter.db_type == 'mysql':
                        query = f"SELECT * FROM {self.table_name} WHERE {field_name} = %s ORDER BY {self.primary_key} DESC LIMIT 1"
                    else:
                        query = f"SELECT * FROM {self.table_name} WHERE {field_name} = ? ORDER BY {self.primary_key} DESC LIMIT 1"
                    
                    results = self.database_adapter.execute_query(query, (field_value,))
                    
                    if results:
                        created_record = results[0]
                        
                        # Notify event
                        notify_event(
                            EventType.INSERT,
                            table_name=self.table_name,
                            record_id=created_record.get(self.primary_key),
                            data=data,
                            user_id=self.user_id
                        )
                        
                        return created_record
            
            return None
        except Exception as e:
            logger.error(f"Error in create for {self.table_name}: {e}")
            notify_event(
                EventType.ERROR,
                table_name=self.table_name,
                data={'error': str(e), 'operation': 'create', 'data': data},
                user_id=self.user_id
            )
            return None
    
    def update(self, record_id: Any, data: Dict[str, Any]) -> bool:
        """Update existing record"""
        try:
            # Remove primary key from update data
            if self.primary_key in data:
                del data[self.primary_key]
            
            # Update record
            success = self.database_adapter.update_record(
                self.table_name, record_id, data, self.primary_key
            )
            
            if success:
                # Notify event
                notify_event(
                    EventType.UPDATE,
                    table_name=self.table_name,
                    record_id=record_id,
                    data=data,
                    user_id=self.user_id
                )
            
            return success
        except Exception as e:
            logger.error(f"Error in update for {self.table_name}: {e}")
            notify_event(
                EventType.ERROR,
                table_name=self.table_name,
                record_id=record_id,
                data={'error': str(e), 'operation': 'update', 'update_data': data},
                user_id=self.user_id
            )
            return False
    
    def delete(self, record_id: Any) -> bool:
        """Delete record by ID"""
        try:
            success = self.database_adapter.delete_record(
                self.table_name, record_id, self.primary_key
            )
            
            if success:
                # Notify event
                notify_event(
                    EventType.DELETE,
                    table_name=self.table_name,
                    record_id=record_id,
                    user_id=self.user_id
                )
            
            return success
        except Exception as e:
            logger.error(f"Error in delete for {self.table_name}: {e}")
            notify_event(
                EventType.ERROR,
                table_name=self.table_name,
                record_id=record_id,
                data={'error': str(e), 'operation': 'delete'},
                user_id=self.user_id
            )
            return False
    
    def count(self, filters: Dict[str, Any] = None) -> int:
        """Count records with optional filtering"""
        try:
            query = f"SELECT COUNT(*) as count FROM {self.table_name}"
            params = []
            
            # Add filters
            if filters:
                where_clauses = []
                for key, value in filters.items():
                    if self.database_adapter.db_type == 'mysql':
                        where_clauses.append(f"{key} = %s")
                    else:
                        where_clauses.append(f"{key} = ?")
                    params.append(value)
                
                if where_clauses:
                    query += " WHERE " + " AND ".join(where_clauses)
            
            results = self.database_adapter.execute_query(query, tuple(params) if params else None)
            
            if results:
                return results[0]['count']
            
            return 0
        except Exception as e:
            logger.error(f"Error in count for {self.table_name}: {e}")
            return 0
    
    def exists(self, record_id: Any) -> bool:
        """Check if record exists"""
        try:
            if self.database_adapter.db_type == 'mysql':
                query = f"SELECT COUNT(*) as count FROM {self.table_name} WHERE {self.primary_key} = %s"
            else:
                query = f"SELECT COUNT(*) as count FROM {self.table_name} WHERE {self.primary_key} = ?"
            
            results = self.database_adapter.execute_query(query, (record_id,))
            
            if results:
                return results[0]['count'] > 0
            
            return False
        except Exception as e:
            logger.error(f"Error in exists for {self.table_name}: {e}")
            return False
    
    def search(self, search_term: str, search_fields: List[str] = None) -> List[Dict[str, Any]]:
        """Search records by term across specified fields"""
        try:
            if not search_fields:
                # Get all text fields from table info
                table_info = self.database_adapter.get_table_info(self.table_name)
                search_fields = [col['name'] for col in table_info if 'text' in col['type'].lower() or 'varchar' in col['type'].lower()]
            
            if not search_fields:
                return []
            
            # Build search query
            search_clauses = []
            params = []
            
            for field in search_fields:
                if self.database_adapter.db_type == 'mysql':
                    search_clauses.append(f"{field} LIKE %s")
                else:
                    search_clauses.append(f"{field} LIKE ?")
                params.append(f"%{search_term}%")
            
            query = f"SELECT * FROM {self.table_name} WHERE " + " OR ".join(search_clauses)
            
            results = self.database_adapter.execute_query(query, tuple(params))
            
            # Notify event
            notify_event(
                EventType.SELECT,
                table_name=self.table_name,
                data={'search_term': search_term, 'search_fields': search_fields, 'count': len(results)},
                user_id=self.user_id
            )
            
            return results
        except Exception as e:
            logger.error(f"Error in search for {self.table_name}: {e}")
            return []
    
    def bulk_create(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create multiple records"""
        created_records = []
        
        for record in records:
            created_record = self.create(record)
            if created_record:
                created_records.append(created_record)
        
        return created_records
    
    def bulk_update(self, updates: List[Dict[str, Any]]) -> int:
        """Update multiple records"""
        success_count = 0
        
        for update in updates:
            if 'id' in update:
                if self.update(update['id'], update):
                    success_count += 1
        
        return success_count
    
    def bulk_delete(self, record_ids: List[Any]) -> int:
        """Delete multiple records"""
        success_count = 0
        
        for record_id in record_ids:
            if self.delete(record_id):
                success_count += 1
        
        return success_count

# Specific Repository Implementations

class CompanyRepository(BaseRepository):
    """Repository for company operations"""
    
    def __init__(self, database_adapter=None, user_id: str = None):
        super().__init__('companies', 'company_id', database_adapter, user_id)
    
    def find_by_tax_id(self, tax_id: str) -> Optional[Dict[str, Any]]:
        """Find company by tax ID"""
        results = self.find_all({'tax_id': tax_id})
        return results[0] if results else None
    
    def find_by_registration_number(self, registration_number: str) -> Optional[Dict[str, Any]]:
        """Find company by registration number"""
        results = self.find_all({'registration_number': registration_number})
        return results[0] if results else None
    
    def find_active_companies(self) -> List[Dict[str, Any]]:
        """Find all active companies"""
        return self.find_all({'status': 'active'})

class EmployeeRepository(BaseRepository):
    """Repository for employee operations"""
    
    def __init__(self, database_adapter=None, user_id: str = None):
        super().__init__('employees', 'employee_id', database_adapter, user_id)
    
    def find_by_company(self, company_id: int) -> List[Dict[str, Any]]:
        """Find employees by company ID"""
        return self.find_all({'company_id': company_id})
    
    def find_by_department(self, department: str) -> List[Dict[str, Any]]:
        """Find employees by department"""
        return self.find_all({'department': department})
    
    def find_active_employees(self) -> List[Dict[str, Any]]:
        """Find all active employees"""
        return self.find_all({'status': 'active'})

class TransactionRepository(BaseRepository):
    """Repository for transaction operations"""
    
    def __init__(self, database_adapter=None, user_id: str = None):
        super().__init__('transactions', 'transaction_id', database_adapter, user_id)
    
    def find_by_date_range(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Find transactions within date range"""
        try:
            if self.database_adapter.db_type == 'mysql':
                query = f"SELECT * FROM {self.table_name} WHERE transaction_date BETWEEN %s AND %s"
            else:
                query = f"SELECT * FROM {self.table_name} WHERE transaction_date BETWEEN ? AND ?"
            
            results = self.database_adapter.execute_query(query, (start_date, end_date))
            
            # Notify event
            notify_event(
                EventType.SELECT,
                table_name=self.table_name,
                data={'start_date': start_date, 'end_date': end_date, 'count': len(results)},
                user_id=self.user_id
            )
            
            return results
        except Exception as e:
            logger.error(f"Error in find_by_date_range for {self.table_name}: {e}")
            return []
    
    def find_by_amount_range(self, min_amount: float, max_amount: float) -> List[Dict[str, Any]]:
        """Find transactions within amount range"""
        try:
            if self.database_adapter.db_type == 'mysql':
                query = f"SELECT * FROM {self.table_name} WHERE amount BETWEEN %s AND %s"
            else:
                query = f"SELECT * FROM {self.table_name} WHERE amount BETWEEN ? AND ?"
            
            results = self.database_adapter.execute_query(query, (min_amount, max_amount))
            
            # Notify event
            notify_event(
                EventType.SELECT,
                table_name=self.table_name,
                data={'min_amount': min_amount, 'max_amount': max_amount, 'count': len(results)},
                user_id=self.user_id
            )
            
            return results
        except Exception as e:
            logger.error(f"Error in find_by_amount_range for {self.table_name}: {e}")
            return []
    
    def get_transaction_summary(self) -> Dict[str, Any]:
        """Get transaction summary statistics"""
        try:
            if self.database_adapter.db_type == 'mysql':
                query = f"""
                    SELECT 
                        COUNT(*) as total_transactions,
                        SUM(amount) as total_amount,
                        AVG(amount) as average_amount,
                        MIN(amount) as min_amount,
                        MAX(amount) as max_amount
                    FROM {self.table_name}
                """
            else:
                query = f"""
                    SELECT 
                        COUNT(*) as total_transactions,
                        SUM(amount) as total_amount,
                        AVG(amount) as average_amount,
                        MIN(amount) as min_amount,
                        MAX(amount) as max_amount
                    FROM {self.table_name}
                """
            
            results = self.database_adapter.execute_query(query)
            
            if results:
                return results[0]
            
            return {}
        except Exception as e:
            logger.error(f"Error in get_transaction_summary for {self.table_name}: {e}")
            return {}

# Repository Factory

class RepositoryFactory:
    """Factory for creating repository instances"""
    
    _repositories = {}
    
    @classmethod
    def get_repository(cls, table_name: str, database_adapter=None, user_id: str = None) -> Repository:
        """Get or create repository for table"""
        key = f"{table_name}_{user_id}"
        
        if key not in cls._repositories:
            # Create appropriate repository based on table name
            if table_name == 'companies':
                cls._repositories[key] = CompanyRepository(database_adapter, user_id)
            elif table_name == 'employees':
                cls._repositories[key] = EmployeeRepository(database_adapter, user_id)
            elif table_name == 'transactions':
                cls._repositories[key] = TransactionRepository(database_adapter, user_id)
            else:
                # Use base repository for unknown tables
                cls._repositories[key] = BaseRepository(table_name, 'id', database_adapter, user_id)
        
        return cls._repositories[key]
    
    @classmethod
    def clear_cache(cls):
        """Clear repository cache"""
        cls._repositories.clear()
