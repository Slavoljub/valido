"""
ValidoAI - Unified Controller System
==================================
Global controllers for all database operations following Cursor Rules
Supports all database types with unified CRUD operations
"""

import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

# Import unified systems
from src.database import database_manager, DatabaseConnection
from src.config import config_manager, db_config as database_config
from src.models.unified_models import (
    db, Company, User, Invoice, InvoiceItem,
    EmailTemplate, EmailCampaign, EmailRecipient,
    AIModel, AIInsight
)

logger = logging.getLogger(__name__)

# ============================================================================
# ENUMS AND DATA CLASSES
# ============================================================================

class OperationType(Enum):
    """Supported CRUD operations"""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    LIST = "list"
    SEARCH = "search"
    COUNT = "count"

class DatabaseType(Enum):
    """Supported database types"""
    SQL = "sql"
    NOSQL = "nosql"
    TIMESERIES = "timeseries"
    GRAPH = "graph"

@dataclass
class QueryResult:
    """Standardized query result"""
    data: List[Dict[str, Any]]
    count: int
    success: bool
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class CrudResult:
    """CRUD operation result"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    affected_rows: int = 0
    operation: str = ""

# ============================================================================
# UNIFIED CONTROLLER SYSTEM
# ============================================================================

class UnifiedController:
    """Unified controller for all database operations"""

    def __init__(self, model_class=None, table_name: str = None):
        self.model_class = model_class
        self.table_name = table_name or (model_class.__tablename__ if model_class else None)
        self.database_type = database_config.type
        self._query_builders = {
            'sqlite': self._build_sqlite_query,
            'postgresql': self._build_postgresql_query,
            'mysql': self._build_mysql_query,
            'mongodb': self._build_mongodb_query,
            'redis': self._build_redis_query,
            'cassandra': self._build_cassandra_query,
            'elasticsearch': self._build_elasticsearch_query
        }

    def list(self, filters: Dict[str, Any] = None,
             limit: int = 100, offset: int = 0,
             order_by: str = None, order_dir: str = "ASC") -> QueryResult:
        """List records with pagination and filtering"""

        try:
            if self.model_class and self.database_type in ['sqlite', 'postgresql', 'mysql']:
                return self._list_sql_model(filters, limit, offset, order_by, order_dir)
            else:
                return self._list_raw_database(filters, limit, offset, order_by, order_dir)

        except Exception as e:
            logger.error(f"❌ List operation failed: {e}")
            return QueryResult(data=[], count=0, success=False, error=str(e))

    def _list_sql_model(self, filters, limit, offset, order_by, order_dir) -> QueryResult:
        """List records using SQLAlchemy models"""
        query = self.model_class.query

        # Apply filters
        if filters:
            for key, value in filters.items():
                if hasattr(self.model_class, key):
                    query = query.filter(getattr(self.model_class, key) == value)

        # Apply ordering
        if order_by and hasattr(self.model_class, order_by):
            column = getattr(self.model_class, order_by)
            query = query.order_by(column.desc() if order_dir.upper() == "DESC" else column)

        # Get total count
        total_count = query.count()

        # Apply pagination
        records = query.limit(limit).offset(offset).all()

        # Convert to dict format
        data = []
        for record in records:
            if hasattr(record, '__dict__'):
                data.append({k: v for k, v in record.__dict__.items() if not k.startswith('_')})
            else:
                data.append(record)

        return QueryResult(
            data=data,
            count=total_count,
            success=True,
            metadata={'limit': limit, 'offset': offset}
        )

    def _list_raw_database(self, filters, limit, offset, order_by, order_dir) -> QueryResult:
        """List records using raw database queries"""
        query_builder = self._query_builders.get(self.database_type, self._build_sqlite_query)

        query, params = query_builder(
            operation=OperationType.LIST,
            filters=filters,
            limit=limit,
            offset=offset,
            order_by=order_by,
            order_dir=order_dir
        )

        try:
            result = database_manager.execute_query(query, params)
            total_count = len(result) if isinstance(result, list) else 0

            return QueryResult(
                data=result,
                count=total_count,
                success=True,
                metadata={'limit': limit, 'offset': offset}
            )

        except Exception as e:
            return QueryResult(data=[], count=0, success=False, error=str(e))

    def get(self, record_id: Union[str, int]) -> QueryResult:
        """Get single record by ID"""

        try:
            if self.model_class and self.database_type in ['sqlite', 'postgresql', 'mysql']:
                record = self.model_class.query.get(record_id)
                if record:
                    data = {k: v for k, v in record.__dict__.items() if not k.startswith('_')}
                    return QueryResult(data=[data], count=1, success=True)
                else:
                    return QueryResult(data=[], count=0, success=True)  # Not found, but no error

            # Raw database query
            query_builder = self._query_builders.get(self.database_type, self._build_sqlite_query)
            query, params = query_builder(OperationType.READ, record_id=record_id)

            result = database_manager.execute_query(query, params)

            return QueryResult(
                data=result,
                count=len(result),
                success=True
            )

        except Exception as e:
            logger.error(f"❌ Get operation failed: {e}")
            return QueryResult(data=[], count=0, success=False, error=str(e))

    def create(self, data: Dict[str, Any]) -> CrudResult:
        """Create new record"""

        try:
            if self.model_class and self.database_type in ['sqlite', 'postgresql', 'mysql']:
                # Use SQLAlchemy model
                record = self.model_class(**data)
                db.session.add(record)
                db.session.commit()

                created_data = {k: v for k, v in record.__dict__.items() if not k.startswith('_')}
                return CrudResult(
                    success=True,
                    data=created_data,
                    affected_rows=1,
                    operation="create"
                )

            # Raw database query
            query_builder = self._query_builders.get(self.database_type, self._build_sqlite_query)
            query, params = query_builder(OperationType.CREATE, data=data)

            result = database_manager.execute_query(query, params)
            return CrudResult(
                success=True,
                data=data,
                affected_rows=1,
                operation="create"
            )

        except Exception as e:
            logger.error(f"❌ Create operation failed: {e}")
            return CrudResult(success=False, error=str(e), operation="create")

    def update(self, record_id: Union[str, int], data: Dict[str, Any]) -> CrudResult:
        """Update existing record"""

        try:
            if self.model_class and self.database_type in ['sqlite', 'postgresql', 'mysql']:
                # Use SQLAlchemy model
                record = self.model_class.query.get(record_id)
                if not record:
                    return CrudResult(success=False, error="Record not found", operation="update")

                for key, value in data.items():
                    if hasattr(record, key):
                        setattr(record, key, value)

                record.updated_at = datetime.utcnow()
                db.session.commit()

                updated_data = {k: v for k, v in record.__dict__.items() if not k.startswith('_')}
                return CrudResult(
                    success=True,
                    data=updated_data,
                    affected_rows=1,
                    operation="update"
                )

            # Raw database query
            query_builder = self._query_builders.get(self.database_type, self._build_sqlite_query)
            query, params = query_builder(OperationType.UPDATE, record_id=record_id, data=data)

            result = database_manager.execute_query(query, params)
            return CrudResult(
                success=True,
                data=data,
                affected_rows=1,
                operation="update"
            )

        except Exception as e:
            logger.error(f"❌ Update operation failed: {e}")
            return CrudResult(success=False, error=str(e), operation="update")

    def delete(self, record_id: Union[str, int]) -> CrudResult:
        """Delete record"""

        try:
            if self.model_class and self.database_type in ['sqlite', 'postgresql', 'mysql']:
                # Use SQLAlchemy model
                record = self.model_class.query.get(record_id)
                if not record:
                    return CrudResult(success=False, error="Record not found", operation="delete")

                db.session.delete(record)
                db.session.commit()

                return CrudResult(
                    success=True,
                    affected_rows=1,
                    operation="delete"
                )

            # Raw database query
            query_builder = self._query_builders.get(self.database_type, self._build_sqlite_query)
            query, params = query_builder(OperationType.DELETE, record_id=record_id)

            result = database_manager.execute_query(query, params)
            return CrudResult(
                success=True,
                affected_rows=1,
                operation="delete"
            )

        except Exception as e:
            logger.error(f"❌ Delete operation failed: {e}")
            return CrudResult(success=False, error=str(e), operation="delete")

    def search(self, search_term: str, search_fields: List[str] = None,
               limit: int = 100, offset: int = 0) -> QueryResult:
        """Search records"""

        try:
            if self.model_class and self.database_type in ['sqlite', 'postgresql', 'mysql']:
                return self._search_sql_model(search_term, search_fields, limit, offset)
            else:
                return self._search_raw_database(search_term, search_fields, limit, offset)

        except Exception as e:
            logger.error(f"❌ Search operation failed: {e}")
            return QueryResult(data=[], count=0, success=False, error=str(e))

    def _search_sql_model(self, search_term, search_fields, limit, offset) -> QueryResult:
        """Search using SQLAlchemy models"""
        from sqlalchemy import or_, func

        query = self.model_class.query
        search_filters = []

        if search_fields:
            for field_name in search_fields:
                if hasattr(self.model_class, field_name):
                    field = getattr(self.model_class, field_name)
                    search_filters.append(func.lower(field).contains(search_term.lower()))
        else:
            # Search in all string/text columns
            for column in self.model_class.__table__.columns:
                if str(column.type).lower() in ['varchar', 'text', 'string']:
                    search_filters.append(func.lower(column).contains(search_term.lower()))

        if search_filters:
            query = query.filter(or_(*search_filters))

        total_count = query.count()
        records = query.limit(limit).offset(offset).all()

        data = []
        for record in records:
            data.append({k: v for k, v in record.__dict__.items() if not k.startswith('_')})

        return QueryResult(
            data=data,
            count=total_count,
            success=True,
            metadata={'search_term': search_term, 'limit': limit, 'offset': offset}
        )

    def _search_raw_database(self, search_term, search_fields, limit, offset) -> QueryResult:
        """Search using raw database queries"""
        query_builder = self._query_builders.get(self.database_type, self._build_sqlite_query)
        query, params = query_builder(
            OperationType.SEARCH,
            search_term=search_term,
            search_fields=search_fields,
            limit=limit,
            offset=offset
        )

        result = database_manager.execute_query(query, params)
        return QueryResult(
            data=result,
            count=len(result),
            success=True,
            metadata={'search_term': search_term, 'limit': limit, 'offset': offset}
        )

    def count(self, filters: Dict[str, Any] = None) -> QueryResult:
        """Count records"""

        try:
            if self.model_class and self.database_type in ['sqlite', 'postgresql', 'mysql']:
                query = self.model_class.query

                if filters:
                    for key, value in filters.items():
                        if hasattr(self.model_class, key):
                            query = query.filter(getattr(self.model_class, key) == value)

                total_count = query.count()
                return QueryResult(data=[], count=total_count, success=True)

            # Raw database query
            query_builder = self._query_builders.get(self.database_type, self._build_sqlite_query)
            query, params = query_builder(OperationType.COUNT, filters=filters)

            result = database_manager.execute_query(query, params)
            count = result[0].get('count', 0) if result else 0

            return QueryResult(data=[], count=count, success=True)

        except Exception as e:
            logger.error(f"❌ Count operation failed: {e}")
            return QueryResult(data=[], count=0, success=False, error=str(e))

    def get_datatable_data(self, start: int = 0, length: int = 10,
                          search_value: str = "", order_column: int = 0,
                          order_dir: str = "asc") -> Dict[str, Any]:
        """Get data formatted for DataTable AJAX requests"""
        try:
            # Map column index to field name (adjust based on your table structure)
            column_mapping = {
                0: 'company_name',      # Company column
                1: 'legal_name',        # Legal Name column
                2: 'tax_id',           # Tax ID column
                3: 'industry',         # Industry column
                4: 'company_type',     # Type column
                5: 'status',           # Status column
                6: 'created_at'        # Created column
            }

            # Get order by field
            order_by = column_mapping.get(order_column, 'created_at')

            # Build filters for search
            filters = {}
            if search_value:
                # Search across multiple fields
                search_filters = {
                    'company_name': search_value,
                    'legal_name': search_value,
                    'tax_id': search_value,
                    'industry': search_value,
                    'email': search_value
                }
                filters = search_filters

            # Get filtered data
            result = self.list(
                filters=filters,
                limit=length,
                offset=start,
                order_by=order_by,
                order_dir=order_dir.upper()
            )

            # Get total count without filters
            total_result = self.count()

            # Get filtered count with filters
            filtered_result = self.count(filters)

            return {
                'data': result.data,
                'total': total_result.count,
                'filtered': filtered_result.count,
                'success': True
            }

        except Exception as e:
            logger.error(f"❌ DataTable data retrieval failed: {e}")
            return {
                'data': [],
                'total': 0,
                'filtered': 0,
                'success': False,
                'error': str(e)
            }

    def get_related_data(self, record_id: Union[str, int]) -> Dict[str, Any]:
        """Get related data for a record (invoices, users, etc.)"""
        try:
            related_data = {
                'invoices': [],
                'users': [],
                'total_invoices': 0,
                'total_users': 0
            }

            if self.model_class and self.database_type in ['sqlite', 'postgresql', 'mysql']:
                # Get the record
                record = self.model_class.query.get(record_id)
                if record:
                    # Get related invoices
                    if hasattr(record, 'invoices'):
                        related_data['invoices'] = [
                            {k: v for k, v in invoice.__dict__.items() if not k.startswith('_')}
                            for invoice in record.invoices
                        ]
                        related_data['total_invoices'] = len(related_data['invoices'])

                    # Get related users
                    if hasattr(record, 'users'):
                        related_data['users'] = [
                            {k: v for k, v in user.__dict__.items() if not k.startswith('_')}
                            for user in record.users
                        ]
                        related_data['total_users'] = len(related_data['users'])

            return related_data

        except Exception as e:
            logger.error(f"❌ Related data retrieval failed: {e}")
            return {
                'invoices': [],
                'users': [],
                'total_invoices': 0,
                'total_users': 0,
                'error': str(e)
            }

    # ============================================================================
    # DATABASE-SPECIFIC QUERY BUILDERS
    # ============================================================================

    def _build_sqlite_query(self, operation: OperationType, **kwargs) -> tuple:
        """Build SQLite queries"""
        table = self.table_name or "unknown_table"

        if operation == OperationType.LIST:
            filters = kwargs.get('filters', {})
            limit = kwargs.get('limit', 100)
            offset = kwargs.get('offset', 0)
            order_by = kwargs.get('order_by')
            order_dir = kwargs.get('order_dir', 'ASC')

            query = f"SELECT * FROM {table}"
            params = []

            # Add WHERE clause
            if filters:
                where_parts = []
                for key, value in filters.items():
                    where_parts.append(f"{key} = ?")
                    params.append(value)
                query += " WHERE " + " AND ".join(where_parts)

            # Add ORDER BY
            if order_by:
                query += f" ORDER BY {order_by} {order_dir}"

            # Add LIMIT/OFFSET
            query += f" LIMIT {limit} OFFSET {offset}"

            return query, params

        elif operation == OperationType.READ:
            record_id = kwargs.get('record_id')
            return f"SELECT * FROM {table} WHERE id = ?", [record_id]

        elif operation == OperationType.CREATE:
            data = kwargs.get('data', {})
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['?' for _ in data.keys()])
            values = list(data.values())
            return f"INSERT INTO {table} ({columns}) VALUES ({placeholders})", values

        elif operation == OperationType.UPDATE:
            record_id = kwargs.get('record_id')
            data = kwargs.get('data', {})
            set_parts = []
            params = []
            for key, value in data.items():
                set_parts.append(f"{key} = ?")
                params.append(value)
            params.append(record_id)
            return f"UPDATE {table} SET {', '.join(set_parts)} WHERE id = ?", params

        elif operation == OperationType.DELETE:
            record_id = kwargs.get('record_id')
            return f"DELETE FROM {table} WHERE id = ?", [record_id]

        elif operation == OperationType.SEARCH:
            search_term = kwargs.get('search_term', '')
            search_fields = kwargs.get('search_fields', ['name', 'description'])
            limit = kwargs.get('limit', 100)
            offset = kwargs.get('offset', 0)

            search_conditions = []
            params = []
            for field in search_fields:
                search_conditions.append(f"{field} LIKE ?")
                params.append(f"%{search_term}%")

            query = f"SELECT * FROM {table} WHERE {' OR '.join(search_conditions)} LIMIT {limit} OFFSET {offset}"
            return query, params

        elif operation == OperationType.COUNT:
            filters = kwargs.get('filters', {})
            query = f"SELECT COUNT(*) as count FROM {table}"
            params = []

            if filters:
                where_parts = []
                for key, value in filters.items():
                    where_parts.append(f"{key} = ?")
                    params.append(value)
                query += " WHERE " + " AND ".join(where_parts)

            return query, params

        return "", []

    def _build_postgresql_query(self, operation: OperationType, **kwargs) -> tuple:
        """Build PostgreSQL queries (similar to SQLite but with RETURNING)"""
        table = self.table_name or "unknown_table"

        if operation == OperationType.CREATE:
            data = kwargs.get('data', {})
            columns = ', '.join(data.keys())
            placeholders = ', '.join([f"${i+1}" for i in range(len(data.keys()))])
            values = list(data.values())
            query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders}) RETURNING *"
            return query, values

        elif operation == OperationType.UPDATE:
            record_id = kwargs.get('record_id')
            data = kwargs.get('data', {})
            set_parts = []
            params = []
            for i, (key, value) in enumerate(data.items()):
                set_parts.append(f"{key} = ${i+1}")
                params.append(value)
            params.append(record_id)
            query = f"UPDATE {table} SET {', '.join(set_parts)} WHERE id = ${len(params)} RETURNING *"
            return query, params

        # Fall back to SQLite-style queries for other operations
        return self._build_sqlite_query(operation, **kwargs)

    def _build_mysql_query(self, operation: OperationType, **kwargs) -> tuple:
        """Build MySQL queries"""
        # MySQL uses %s placeholders instead of ?
        query, params = self._build_sqlite_query(operation, **kwargs)
        return query.replace('?', '%s'), params

    def _build_mongodb_query(self, operation: OperationType, **kwargs) -> tuple:
        """Build MongoDB queries (returns query dict, not SQL)"""
        collection = self.table_name or "unknown_collection"

        if operation == OperationType.LIST:
            filters = kwargs.get('filters', {})
            limit = kwargs.get('limit', 100)
            offset = kwargs.get('offset', 0)

            query = {
                'collection': collection,
                'operation': 'find',
                'filter': filters,
                'limit': limit,
                'skip': offset
            }
            return query, {}

        elif operation == OperationType.READ:
            record_id = kwargs.get('record_id')
            query = {
                'collection': collection,
                'operation': 'find_one',
                'filter': {'_id': record_id}
            }
            return query, {}

        elif operation == OperationType.CREATE:
            data = kwargs.get('data', {})
            query = {
                'collection': collection,
                'operation': 'insert_one',
                'document': data
            }
            return query, {}

        elif operation == OperationType.UPDATE:
            record_id = kwargs.get('record_id')
            data = kwargs.get('data', {})
            query = {
                'collection': collection,
                'operation': 'update_one',
                'filter': {'_id': record_id},
                'update': {'$set': data}
            }
            return query, {}

        elif operation == OperationType.DELETE:
            record_id = kwargs.get('record_id')
            query = {
                'collection': collection,
                'operation': 'delete_one',
                'filter': {'_id': record_id}
            }
            return query, {}

        return {}, {}

    def _build_redis_query(self, operation: OperationType, **kwargs) -> tuple:
        """Build Redis queries"""
        key = self.table_name or "unknown_key"

        if operation == OperationType.LIST:
            limit = kwargs.get('limit', 100)
            query = {
                'operation': 'lrange',
                'key': key,
                'start': 0,
                'stop': limit - 1
            }
            return query, {}

        elif operation == OperationType.READ:
            record_id = kwargs.get('record_id')
            query = {
                'operation': 'get',
                'key': f"{key}:{record_id}"
            }
            return query, {}

        elif operation == OperationType.CREATE:
            data = kwargs.get('data', {})
            query = {
                'operation': 'set',
                'key': f"{key}:{data.get('id', 'new')}",
                'value': data
            }
            return query, {}

        return {}, {}

    def _build_cassandra_query(self, operation: OperationType, **kwargs) -> tuple:
        """Build Cassandra queries"""
        table = self.table_name or "unknown_table"

        if operation == OperationType.LIST:
            filters = kwargs.get('filters', {})
            limit = kwargs.get('limit', 100)

            where_parts = []
            params = []
            for key, value in filters.items():
                where_parts.append(f"{key} = ?")
                params.append(value)

            where_clause = " WHERE " + " AND ".join(where_parts) if where_parts else ""
            query = f"SELECT * FROM {table}{where_clause} LIMIT {limit}"
            return query, params

        # Fall back to basic queries for other operations
        return self._build_sqlite_query(operation, **kwargs)

    def _build_elasticsearch_query(self, operation: OperationType, **kwargs) -> tuple:
        """Build Elasticsearch queries"""
        index = self.table_name or "unknown_index"

        if operation == OperationType.LIST:
            filters = kwargs.get('filters', {})
            limit = kwargs.get('limit', 100)
            offset = kwargs.get('offset', 0)

            query = {
                'index': index,
                'operation': 'search',
                'body': {
                    'query': {'match_all': {}} if not filters else {'term': filters},
                    'size': limit,
                    'from': offset
                }
            }
            return query, {}

        elif operation == OperationType.SEARCH:
            search_term = kwargs.get('search_term', '')
            limit = kwargs.get('limit', 100)

            query = {
                'index': index,
                'operation': 'search',
                'body': {
                    'query': {
                        'multi_match': {
                            'query': search_term,
                            'fields': ['*']
                        }
                    },
                    'size': limit
                }
            }
            return query, {}

        return {}, {}

# ============================================================================
# GLOBAL CONTROLLER MANAGER
# ============================================================================

class GlobalControllerManager:
    """Global controller manager for all database operations"""

    def __init__(self):
        self.controllers = {}
        self._init_default_controllers()

    def _init_default_controllers(self):
        """Initialize default controllers for common models"""
        try:
            # SQLAlchemy model controllers
            self.controllers['companies'] = UnifiedController(Company, 'companies')
            self.controllers['users'] = UnifiedController(User, 'users')
            self.controllers['invoices'] = UnifiedController(Invoice, 'invoices')
            self.controllers['invoice_items'] = UnifiedController(InvoiceItem, 'invoice_items')
            self.controllers['email_templates'] = UnifiedController(EmailTemplate, 'email_templates')
            self.controllers['email_campaigns'] = UnifiedController(EmailCampaign, 'email_campaigns')
            self.controllers['email_recipients'] = UnifiedController(EmailRecipient, 'email_recipients')
            self.controllers['ai_models'] = UnifiedController(AIModel, 'ai_models')
            self.controllers['ai_insights'] = UnifiedController(AIInsight, 'ai_insights')

            logger.info("✅ Default controllers initialized")

        except Exception as e:
            logger.error(f"❌ Error initializing default controllers: {e}")

    def get_controller(self, table_name: str, model_class=None) -> UnifiedController:
        """Get or create controller for table/model"""
        if table_name not in self.controllers:
            self.controllers[table_name] = UnifiedController(model_class, table_name)

        return self.controllers[table_name]

    def execute_crud_operation(self, table_name: str, operation: str,
                              model_class=None, **kwargs) -> Union[QueryResult, CrudResult]:
        """Execute CRUD operation on any table"""
        try:
            controller = self.get_controller(table_name, model_class)

            if operation == 'list':
                return controller.list(**kwargs)
            elif operation == 'get':
                return controller.get(**kwargs)
            elif operation == 'create':
                return controller.create(**kwargs)
            elif operation == 'update':
                return controller.update(**kwargs)
            elif operation == 'delete':
                return controller.delete(**kwargs)
            elif operation == 'search':
                return controller.search(**kwargs)
            elif operation == 'count':
                return controller.count(**kwargs)
            else:
                raise ValueError(f"Unknown operation: {operation}")

        except Exception as e:
            logger.error(f"❌ CRUD operation failed: {e}")
            if operation in ['list', 'get', 'search', 'count']:
                return QueryResult(data=[], count=0, success=False, error=str(e))
            else:
                return CrudResult(success=False, error=str(e), operation=operation)

    # Convenience methods for common operations
    def list_records(self, table_name: str, filters=None, limit=100, offset=0,
                    order_by=None, order_dir="ASC", model_class=None) -> QueryResult:
        """List records from any table"""
        return self.execute_crud_operation(
            table_name, 'list', model_class,
            filters=filters, limit=limit, offset=offset,
            order_by=order_by, order_dir=order_dir
        )

    def get_record(self, table_name: str, record_id: Union[str, int], model_class=None) -> QueryResult:
        """Get single record from any table"""
        return self.execute_crud_operation(table_name, 'get', model_class, record_id=record_id)

    def create_record(self, table_name: str, data: Dict[str, Any], model_class=None) -> CrudResult:
        """Create record in any table"""
        return self.execute_crud_operation(table_name, 'create', model_class, data=data)

    def update_record(self, table_name: str, record_id: Union[str, int],
                     data: Dict[str, Any], model_class=None) -> CrudResult:
        """Update record in any table"""
        return self.execute_crud_operation(
            table_name, 'update', model_class,
            record_id=record_id, data=data
        )

    def delete_record(self, table_name: str, record_id: Union[str, int], model_class=None) -> CrudResult:
        """Delete record from any table"""
        return self.execute_crud_operation(table_name, 'delete', model_class, record_id=record_id)

    def search_records(self, table_name: str, search_term: str, search_fields=None,
                      limit=100, offset=0, model_class=None) -> QueryResult:
        """Search records in any table"""
        return self.execute_crud_operation(
            table_name, 'search', model_class,
            search_term=search_term, search_fields=search_fields,
            limit=limit, offset=offset
        )

    def count_records(self, table_name: str, filters=None, model_class=None) -> QueryResult:
        """Count records in any table"""
        return self.execute_crud_operation(table_name, 'count', model_class, filters=filters)

    def get_table_stats(self, table_name: str, model_class=None) -> Dict[str, Any]:
        """Get statistics for any table"""
        try:
            count_result = self.count_records(table_name, model_class)

            stats = {
                'table_name': table_name,
                'total_records': count_result.count,
                'database_type': database_config.type,
                'success': count_result.success
            }

            if not count_result.success:
                stats['error'] = count_result.error

            return stats

        except Exception as e:
            return {
                'table_name': table_name,
                'total_records': 0,
                'database_type': database_config.type,
                'success': False,
                'error': str(e)
            }

    def get_all_table_stats(self) -> Dict[str, Any]:
        """Get statistics for all tables"""
        stats = {
            'database_type': database_config.type,
            'tables': {},
            'timestamp': datetime.now().isoformat()
        }

        for table_name in self.controllers.keys():
            stats['tables'][table_name] = self.get_table_stats(table_name)

        return stats

# ============================================================================
# GLOBAL INSTANCE
# ============================================================================

# Create global controller manager instance
controller_manager = GlobalControllerManager()

# Export commonly used functions for easy access
list_records = controller_manager.list_records
get_record = controller_manager.get_record
create_record = controller_manager.create_record
update_record = controller_manager.update_record
delete_record = controller_manager.delete_record
search_records = controller_manager.search_records
count_records = controller_manager.count_records

logger.info("✅ Unified controller system initialized successfully")
logger.info(f"📊 Controllers available: {len(controller_manager.controllers)}")
if database_config and hasattr(database_config, 'type'):
    logger.info(f"💾 Database type: {database_config.type}")
else:
    logger.info("💾 Database type: Not configured (using fallback)")

# ============================================================================
# USAGE EXAMPLES
# ============================================================================

"""
# Basic Usage Examples:

# List companies with pagination
companies = list_records('companies', limit=50, offset=0)
print(f"Found {companies.count} companies")

# Get single user
user = get_record('users', user_id=123)
if user.success and user.data:
    print(f"User: {user.data[0]['email']}")

# Create new invoice
new_invoice = create_record('invoices', {
    'company_id': 'company-uuid',
    'customer_name': 'ABC Corp',
    'total_amount': 1500.00,
    'status': 'draft'
})
if new_invoice.success:
    print(f"Created invoice with ID: {new_invoice.data['id']}")

# Update user
update_result = update_record('users', user_id=123, data={'status': 'active'})

# Search companies
search_results = search_records('companies', 'tech', ['company_name', 'industry'])

# Count records
total_users = count_records('users')
print(f"Total users: {total_users.count}")

# Get table statistics
stats = controller_manager.get_table_stats('companies')
print(f"Companies table: {stats['total_records']} records")
"""
