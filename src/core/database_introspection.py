#!/usr/bin/env python3
"""
Database Introspection Utility for ValidoAI
Comprehensive database metadata extraction and analysis
"""

import os
import sys
import json
import logging
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

# Database drivers
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    POSTGRESQL_AVAILABLE = True
except ImportError:
    POSTGRESQL_AVAILABLE = False

try:
    import pymysql
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False

try:
    import sqlite3
    SQLITE_AVAILABLE = True
except ImportError:
    SQLITE_AVAILABLE = False

try:
    import pyodbc
    MSSQL_AVAILABLE = True
except ImportError:
    MSSQL_AVAILABLE = False

try:
    from cassandra.cluster import Cluster
    from cassandra.auth import PlainTextAuthProvider
    CASSANDRA_AVAILABLE = True
except ImportError:
    CASSANDRA_AVAILABLE = False

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

try:
    from pymongo import MongoClient
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DatabaseObject:
    """Represents a database object (table, view, function, etc.)"""
    name: str
    schema: str = ""
    type: str = ""
    definition: str = ""
    created_at: datetime = None
    modified_at: datetime = None
    size_bytes: int = 0
    row_count: int = 0
    columns: List[Dict[str, Any]] = field(default_factory=list)
    indexes: List[Dict[str, Any]] = field(default_factory=list)
    constraints: List[Dict[str, Any]] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    permissions: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class DatabaseMetadata:
    """Complete database metadata"""
    database_name: str
    database_type: str
    version: str
    size_bytes: int = 0
    tables: List[DatabaseObject] = field(default_factory=list)
    views: List[DatabaseObject] = field(default_factory=list)
    materialized_views: List[DatabaseObject] = field(default_factory=list)
    functions: List[DatabaseObject] = field(default_factory=list)
    procedures: List[DatabaseObject] = field(default_factory=list)
    triggers: List[DatabaseObject] = field(default_factory=list)
    sequences: List[DatabaseObject] = field(default_factory=list)
    types: List[DatabaseObject] = field(default_factory=list)
    extensions: List[Dict[str, Any]] = field(default_factory=list)
    schemas: List[str] = field(default_factory=list)
    users: List[Dict[str, Any]] = field(default_factory=list)
    roles: List[Dict[str, Any]] = field(default_factory=list)
    connections: List[Dict[str, Any]] = field(default_factory=list)

class DatabaseIntrospector:
    """Universal database introspection engine"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.database_type = config.get('type', 'sqlite')
        self.connection = None
        self.metadata = None

    def connect(self) -> bool:
        """Establish database connection"""
        try:
            if self.database_type == 'postgresql':
                return self._connect_postgresql()
            elif self.database_type == 'mysql':
                return self._connect_mysql()
            elif self.database_type == 'sqlite':
                return self._connect_sqlite()
            elif self.database_type == 'mssql':
                return self._connect_mssql()
            elif self.database_type == 'mongodb':
                return self._connect_mongodb()
            elif self.database_type == 'redis':
                return self._connect_redis()
            elif self.database_type == 'cassandra':
                return self._connect_cassandra()
            else:
                logger.error(f"Unsupported database type: {self.database_type}")
                return False
        except Exception as e:
            logger.error(f"Connection failed for {self.database_type}: {e}")
            return False

    def _connect_postgresql(self) -> bool:
        """Connect to PostgreSQL database"""
        if not POSTGRESQL_AVAILABLE:
            logger.error("PostgreSQL driver not available")
            return False

        try:
            conn_string = (
                f"host={self.config.get('host', 'localhost')} "
                f"port={self.config.get('port', 5432)} "
                f"dbname={self.config.get('database', 'postgres')} "
                f"user={self.config.get('username', 'postgres')} "
                f"password={self.config.get('password', '')}"
            )

            if self.config.get('ssl_mode'):
                conn_string += f" sslmode={self.config['ssl_mode']}"

            self.connection = psycopg2.connect(conn_string)
            logger.info("✅ Connected to PostgreSQL database")
            return True

        except Exception as e:
            logger.error(f"PostgreSQL connection failed: {e}")
            return False

    def _connect_mysql(self) -> bool:
        """Connect to MySQL database"""
        if not MYSQL_AVAILABLE:
            logger.error("MySQL driver not available")
            return False

        try:
            self.connection = pymysql.connect(
                host=self.config.get('host', 'localhost'),
                port=self.config.get('port', 3306),
                user=self.config.get('username', 'root'),
                password=self.config.get('password', ''),
                database=self.config.get('database', ''),
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
            logger.info("✅ Connected to MySQL database")
            return True

        except Exception as e:
            logger.error(f"MySQL connection failed: {e}")
            return False

    def _connect_sqlite(self) -> bool:
        """Connect to SQLite database"""
        if not SQLITE_AVAILABLE:
            logger.error("SQLite driver not available")
            return False

        try:
            db_path = self.config.get('database', 'data/sqlite/app.db')
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            self.connection = sqlite3.connect(db_path)
            self.connection.row_factory = sqlite3.Row
            logger.info("✅ Connected to SQLite database")
            return True

        except Exception as e:
            logger.error(f"SQLite connection failed: {e}")
            return False

    def _connect_mssql(self) -> bool:
        """Connect to Microsoft SQL Server"""
        if not MSSQL_AVAILABLE:
            logger.error("MSSQL driver not available")
            return False

        try:
            conn_string = (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={self.config.get('host', 'localhost')};"
                f"DATABASE={self.config.get('database', 'master')};"
                f"UID={self.config.get('username', 'sa')};"
                f"PWD={self.config.get('password', '')};"
                f"TrustServerCertificate=yes;"
            )

            self.connection = pyodbc.connect(conn_string)
            logger.info("✅ Connected to MSSQL database")
            return True

        except Exception as e:
            logger.error(f"MSSQL connection failed: {e}")
            return False

    def _connect_mongodb(self) -> bool:
        """Connect to MongoDB"""
        if not MONGODB_AVAILABLE:
            logger.error("MongoDB driver not available")
            return False

        try:
            host = self.config.get('host', 'localhost')
            port = self.config.get('port', 27017)
            database = self.config.get('database', 'admin')

            if self.config.get('username') and self.config.get('password'):
                uri = f"mongodb://{self.config['username']}:{self.config['password']}@{host}:{port}/{database}"
            else:
                uri = f"mongodb://{host}:{port}/{database}"

            self.connection = MongoClient(uri)
            logger.info("✅ Connected to MongoDB")
            return True

        except Exception as e:
            logger.error(f"MongoDB connection failed: {e}")
            return False

    def _connect_redis(self) -> bool:
        """Connect to Redis"""
        if not REDIS_AVAILABLE:
            logger.error("Redis driver not available")
            return False

        try:
            self.connection = redis.Redis(
                host=self.config.get('host', 'localhost'),
                port=self.config.get('port', 6379),
                password=self.config.get('password'),
                db=self.config.get('database', 0),
                decode_responses=True
            )

            # Test connection
            self.connection.ping()
            logger.info("✅ Connected to Redis")
            return True

        except Exception as e:
            logger.error(f"Redis connection failed: {e}")
            return False

    def _connect_cassandra(self) -> bool:
        """Connect to Cassandra"""
        if not CASSANDRA_AVAILABLE:
            logger.error("Cassandra driver not available")
            return False

        try:
            auth_provider = None
            if self.config.get('username') and self.config.get('password'):
                auth_provider = PlainTextAuthProvider(
                    username=self.config['username'],
                    password=self.config['password']
                )

            cluster = Cluster(
                [self.config.get('host', 'localhost')],
                port=self.config.get('port', 9042),
                auth_provider=auth_provider
            )

            self.connection = cluster.connect()
            if self.config.get('keyspace'):
                self.connection.set_keyspace(self.config['keyspace'])

            logger.info("✅ Connected to Cassandra")
            return True

        except Exception as e:
            logger.error(f"Cassandra connection failed: {e}")
            return False

    def introspect(self) -> DatabaseMetadata:
        """Perform complete database introspection"""
        if not self.connection:
            raise ConnectionError("No active database connection")

        self.metadata = DatabaseMetadata(
            database_name=self.config.get('database', 'unknown'),
            database_type=self.database_type,
            version=self._get_version()
        )

        try:
            if self.database_type in ['postgresql', 'mysql', 'sqlite', 'mssql']:
                self._introspect_relational()
            elif self.database_type == 'mongodb':
                self._introspect_mongodb()
            elif self.database_type == 'redis':
                self._introspect_redis()
            elif self.database_type == 'cassandra':
                self._introspect_cassandra()

            logger.info(f"✅ Database introspection completed for {self.database_type}")
            return self.metadata

        except Exception as e:
            logger.error(f"Database introspection failed: {e}")
            raise

    def _get_version(self) -> str:
        """Get database version"""
        try:
            if self.database_type == 'postgresql':
                with self.connection.cursor() as cursor:
                    cursor.execute("SELECT version()")
                    return cursor.fetchone()[0]
            elif self.database_type == 'mysql':
                with self.connection.cursor() as cursor:
                    cursor.execute("SELECT VERSION()")
                    return cursor.fetchone()['VERSION()']
            elif self.database_type == 'sqlite':
                with self.connection as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT sqlite_version()")
                    return cursor.fetchone()[0]
            elif self.database_type == 'mssql':
                with self.connection.cursor() as cursor:
                    cursor.execute("SELECT @@VERSION")
                    return cursor.fetchone()[0]
            else:
                return "Unknown"
        except Exception as e:
            logger.warning(f"Could not get version: {e}")
            return "Unknown"

    def _introspect_relational(self):
        """Introspect relational databases"""
        if self.database_type == 'postgresql':
            self._introspect_postgresql()
        elif self.database_type == 'mysql':
            self._introspect_mysql()
        elif self.database_type == 'sqlite':
            self._introspect_sqlite()
        elif self.database_type == 'mssql':
            self._introspect_mssql()

    def _introspect_postgresql(self):
        """PostgreSQL-specific introspection"""
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:

            # Get schemas
            cursor.execute("""
                SELECT schema_name
                FROM information_schema.schemata
                WHERE schema_name NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
                ORDER BY schema_name
            """)
            self.metadata.schemas = [row['schema_name'] for row in cursor.fetchall()]

            # Get tables
            cursor.execute("""
                SELECT
                    schemaname as schema_name,
                    tablename as table_name,
                    tableowner as owner,
                    tablespace,
                    hasindexes,
                    hasrules,
                    hastriggers,
                    rowsecurity
                FROM pg_tables
                WHERE schemaname NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
                ORDER BY schemaname, tablename
            """)

            for row in cursor.fetchall():
                table = DatabaseObject(
                    name=row['table_name'],
                    schema=row['schema_name'],
                    type='table'
                )
                self.metadata.tables.append(table)

            # Get views
            cursor.execute("""
                SELECT
                    schemaname as schema_name,
                    viewname as view_name,
                    viewowner as owner,
                    definition
                FROM pg_views
                WHERE schemaname NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
                ORDER BY schemaname, viewname
            """)

            for row in cursor.fetchall():
                view = DatabaseObject(
                    name=row['view_name'],
                    schema=row['schema_name'],
                    type='view',
                    definition=row['definition']
                )
                self.metadata.views.append(view)

            # Get functions
            cursor.execute("""
                SELECT
                    n.nspname as schema_name,
                    p.proname as function_name,
                    pg_get_functiondef(p.oid) as definition,
                    p.proowner::regrole as owner,
                    p.prokind
                FROM pg_proc p
                JOIN pg_namespace n ON p.pronamespace = n.oid
                WHERE n.nspname NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
                ORDER BY n.nspname, p.proname
            """)

            for row in cursor.fetchall():
                func = DatabaseObject(
                    name=row['function_name'],
                    schema=row['schema_name'],
                    type='function',
                    definition=row['definition']
                )
                self.metadata.functions.append(func)

            # Get extensions
            cursor.execute("""
                SELECT
                    name,
                    default_version,
                    installed_version,
                    comment
                FROM pg_extension
                ORDER BY name
            """)

            for row in cursor.fetchall():
                self.metadata.extensions.append(dict(row))

    def _introspect_mysql(self):
        """MySQL-specific introspection"""
        with self.connection.cursor() as cursor:

            # Get databases
            cursor.execute("SHOW DATABASES")
            databases = [row['Database'] for row in cursor.fetchall()]

            # Get tables
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()

            for table_row in tables:
                table_name = list(table_row.values())[0]

                # Get table info
                cursor.execute(f"DESCRIBE `{table_name}`")
                columns = cursor.fetchall()

                table = DatabaseObject(
                    name=table_name,
                    type='table',
                    columns=[dict(col) for col in columns]
                )

                self.metadata.tables.append(table)

            # Get views
            cursor.execute("""
                SELECT TABLE_NAME, VIEW_DEFINITION
                FROM information_schema.VIEWS
                WHERE TABLE_SCHEMA = DATABASE()
            """)

            for row in cursor.fetchall():
                view = DatabaseObject(
                    name=row['TABLE_NAME'],
                    type='view',
                    definition=row['VIEW_DEFINITION']
                )
                self.metadata.views.append(view)

            # Get procedures
            cursor.execute("""
                SELECT ROUTINE_NAME, ROUTINE_DEFINITION
                FROM information_schema.ROUTINES
                WHERE ROUTINE_TYPE = 'PROCEDURE'
                AND ROUTINE_SCHEMA = DATABASE()
            """)

            for row in cursor.fetchall():
                proc = DatabaseObject(
                    name=row['ROUTINE_NAME'],
                    type='procedure',
                    definition=row['ROUTINE_DEFINITION']
                )
                self.metadata.procedures.append(proc)

            # Get functions
            cursor.execute("""
                SELECT ROUTINE_NAME, ROUTINE_DEFINITION
                FROM information_schema.ROUTINES
                WHERE ROUTINE_TYPE = 'FUNCTION'
                AND ROUTINE_SCHEMA = DATABASE()
            """)

            for row in cursor.fetchall():
                func = DatabaseObject(
                    name=row['ROUTINE_NAME'],
                    type='function',
                    definition=row['ROUTINE_DEFINITION']
                )
                self.metadata.functions.append(func)

    def _introspect_sqlite(self):
        """SQLite-specific introspection"""
        with self.connection as conn:
            cursor = conn.cursor()

            # Get tables
            cursor.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
                ORDER BY name
            """)

            for row in cursor.fetchall():
                table_name = row[0]

                # Get table info
                cursor.execute(f"PRAGMA table_info(`{table_name}`)")
                columns = cursor.fetchall()

                table = DatabaseObject(
                    name=table_name,
                    type='table',
                    columns=[dict(zip(['cid', 'name', 'type', 'notnull', 'dflt_value', 'pk'], col)) for col in columns]
                )

                self.metadata.tables.append(table)

            # Get views
            cursor.execute("""
                SELECT name, sql FROM sqlite_master
                WHERE type='view' AND name NOT LIKE 'sqlite_%'
                ORDER BY name
            """)

            for row in cursor.fetchall():
                view = DatabaseObject(
                    name=row[0],
                    type='view',
                    definition=row[1]
                )
                self.metadata.views.append(view)

            # Get indexes
            cursor.execute("""
                SELECT name, tbl_name, sql FROM sqlite_master
                WHERE type='index' AND name NOT LIKE 'sqlite_%'
                ORDER BY tbl_name, name
            """)

            for row in cursor.fetchall():
                index = DatabaseObject(
                    name=row[0],
                    type='index',
                    definition=row[2]
                )

                # Find the table and add index to it
                for table in self.metadata.tables:
                    if table.name == row[1]:
                        table.indexes.append({'name': row[0], 'definition': row[2]})
                        break

    def _introspect_mssql(self):
        """Microsoft SQL Server introspection"""
        with self.connection.cursor() as cursor:

            # Get tables
            cursor.execute("""
                SELECT
                    TABLE_SCHEMA,
                    TABLE_NAME,
                    TABLE_TYPE
                FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_TYPE = 'BASE TABLE'
                ORDER BY TABLE_SCHEMA, TABLE_NAME
            """)

            for row in cursor.fetchall():
                table = DatabaseObject(
                    name=row.TABLE_NAME,
                    schema=row.TABLE_SCHEMA,
                    type='table'
                )
                self.metadata.tables.append(table)

            # Get views
            cursor.execute("""
                SELECT
                    TABLE_SCHEMA,
                    TABLE_NAME,
                    VIEW_DEFINITION
                FROM INFORMATION_SCHEMA.VIEWS
                ORDER BY TABLE_SCHEMA, TABLE_NAME
            """)

            for row in cursor.fetchall():
                view = DatabaseObject(
                    name=row.TABLE_NAME,
                    schema=row.TABLE_SCHEMA,
                    type='view',
                    definition=row.VIEW_DEFINITION
                )
                self.metadata.views.append(view)

            # Get procedures
            cursor.execute("""
                SELECT
                    SCHEMA_NAME(schema_id) as schema_name,
                    name,
                    definition
                FROM sys.procedures p
                JOIN sys.sql_modules m ON p.object_id = m.object_id
                ORDER BY schema_name, name
            """)

            for row in cursor.fetchall():
                proc = DatabaseObject(
                    name=row.name,
                    schema=row.schema_name,
                    type='procedure',
                    definition=row.definition
                )
                self.metadata.procedures.append(proc)

            # Get functions
            cursor.execute("""
                SELECT
                    SCHEMA_NAME(schema_id) as schema_name,
                    name,
                    definition
                FROM sys.objects o
                JOIN sys.sql_modules m ON o.object_id = m.object_id
                WHERE o.type IN ('FN', 'IF', 'TF')
                ORDER BY schema_name, name
            """)

            for row in cursor.fetchall():
                func = DatabaseObject(
                    name=row.name,
                    schema=row.schema_name,
                    type='function',
                    definition=row.definition
                )
                self.metadata.functions.append(func)

    def _introspect_mongodb(self):
        """MongoDB-specific introspection"""
        # Get database names
        db_names = self.connection.list_database_names()
        self.metadata.schemas = db_names

        # Use the specified database
        db = self.connection[self.config.get('database', 'admin')]

        # Get collections (equivalent to tables)
        collection_names = db.list_collection_names()

        for collection_name in collection_names:
            collection = db[collection_name]

            # Get collection stats
            stats = db.command("collstats", collection_name)

            table = DatabaseObject(
                name=collection_name,
                type='collection',
                size_bytes=stats.get('size', 0),
                row_count=stats.get('count', 0)
            )

            # Get sample document to infer schema
            sample_doc = collection.find_one()
            if sample_doc:
                columns = []
                for key, value in sample_doc.items():
                    if key != '_id':
                        columns.append({
                            'name': key,
                            'type': type(value).__name__,
                            'sample_value': str(value)[:100]
                        })
                table.columns = columns

            self.metadata.tables.append(table)

    def _introspect_redis(self):
        """Redis-specific introspection"""
        info = self.connection.info()

        # Redis doesn't have traditional tables, but we can list keys
        keys = self.connection.keys('*')
        key_types = {}

        for key in keys[:1000]:  # Limit for performance
            key_type = self.connection.type(key)
            if key_type not in key_types:
                key_types[key_type] = []
            key_types[key_type].append(key)

        for key_type, key_list in key_types.items():
            table = DatabaseObject(
                name=f"keys_{key_type}",
                type=key_type,
                row_count=len(key_list)
            )
            self.metadata.tables.append(table)

        self.metadata.size_bytes = info.get('used_memory', 0)

    def _introspect_cassandra(self):
        """Cassandra-specific introspection"""
        # Get keyspaces
        keyspaces = self.connection.metadata.keyspaces
        self.metadata.schemas = list(keyspaces.keys())

        # Get tables for current keyspace
        if self.config.get('keyspace') in keyspaces:
            keyspace = keyspaces[self.config['keyspace']]

            for table_name, table in keyspace.tables.items():
                db_table = DatabaseObject(
                    name=table_name,
                    type='table'
                )

                # Get columns
                for column_name, column in table.columns.items():
                    db_table.columns.append({
                        'name': column_name,
                        'type': column.cql_type,
                        'kind': column.kind
                    })

                self.metadata.tables.append(db_table)

    def generate_report(self) -> str:
        """Generate comprehensive database report"""
        if not self.metadata:
            return "No metadata available. Run introspect() first."

        report = []
        report.append(f"# 🗄️ Database Introspection Report")
        report.append(f"**Database:** {self.metadata.database_name}")
        report.append(f"**Type:** {self.metadata.database_type}")
        report.append(f"**Version:** {self.metadata.version}")
        report.append(f"**Size:** {self._format_bytes(self.metadata.size_bytes)}")
        report.append("")

        # Summary
        report.append("## 📊 Summary")
        report.append(f"- **Tables:** {len(self.metadata.tables)}")
        report.append(f"- **Views:** {len(self.metadata.views)}")
        report.append(f"- **Functions:** {len(self.metadata.functions)}")
        report.append(f"- **Procedures:** {len(self.metadata.procedures)}")
        if self.database_type in ['postgresql', 'mysql', 'mssql']:
            report.append(f"- **Schemas:** {len(self.metadata.schemas)}")
        report.append("")

        # Tables
        if self.metadata.tables:
            report.append("## 📋 Tables")
            for table in self.metadata.tables:
                report.append(f"### {table.schema}.{table.name}" if table.schema else f"### {table.name}")
                if table.columns:
                    report.append("**Columns:**")
                    for col in table.columns[:5]:  # Show first 5 columns
                        if isinstance(col, dict):
                            col_name = col.get('name', col.get('column_name', 'Unknown'))
                            col_type = col.get('type', col.get('data_type', 'Unknown'))
                            report.append(f"- {col_name}: {col_type}")
                        else:
                            report.append(f"- {col}")
                    if len(table.columns) > 5:
                        report.append(f"- ... and {len(table.columns) - 5} more columns")
                report.append("")

        # Views
        if self.metadata.views:
            report.append("## 👁️ Views")
            for view in self.metadata.views:
                report.append(f"- {view.schema}.{view.name}" if view.schema else f"- {view.name}")
            report.append("")

        # Functions
        if self.metadata.functions:
            report.append("## 🔧 Functions")
            for func in self.metadata.functions:
                report.append(f"- {func.schema}.{func.name}" if func.schema else f"- {func.name}")
            report.append("")

        # Procedures
        if self.metadata.procedures:
            report.append("## ⚙️ Procedures")
            for proc in self.metadata.procedures:
                report.append(f"- {proc.schema}.{proc.name}" if proc.schema else f"- {proc.name}")
            report.append("")

        return "\n".join(report)

    def _format_bytes(self, bytes_val: int) -> str:
        """Format bytes to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_val < 1024.0:
                return ".1f"
            bytes_val /= 1024.0
        return ".1f"

    def export_metadata(self, format: str = 'json') -> str:
        """Export metadata in specified format"""
        if not self.metadata:
            return "{}"

        if format == 'json':
            return json.dumps(self._metadata_to_dict(), indent=2)
        elif format == 'markdown':
            return self.generate_report()
        else:
            return str(self.metadata)

    def _metadata_to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary"""
        return {
            'database_name': self.metadata.database_name,
            'database_type': self.metadata.database_type,
            'version': self.metadata.version,
            'size_bytes': self.metadata.size_bytes,
            'tables': [self._object_to_dict(obj) for obj in self.metadata.tables],
            'views': [self._object_to_dict(obj) for obj in self.metadata.views],
            'functions': [self._object_to_dict(obj) for obj in self.metadata.functions],
            'procedures': [self._object_to_dict(obj) for obj in self.metadata.procedures],
            'schemas': self.metadata.schemas,
            'extensions': self.metadata.extensions
        }

    def _object_to_dict(self, obj: DatabaseObject) -> Dict[str, Any]:
        """Convert DatabaseObject to dictionary"""
        return {
            'name': obj.name,
            'schema': obj.schema,
            'type': obj.type,
            'definition': obj.definition,
            'created_at': obj.created_at.isoformat() if obj.created_at else None,
            'modified_at': obj.modified_at.isoformat() if obj.modified_at else None,
            'size_bytes': obj.size_bytes,
            'row_count': obj.row_count,
            'columns': obj.columns,
            'indexes': obj.indexes,
            'constraints': obj.constraints
        }

    def disconnect(self):
        """Close database connection"""
        try:
            if self.connection:
                if self.database_type in ['postgresql', 'mysql', 'mssql']:
                    self.connection.close()
                elif self.database_type == 'mongodb':
                    self.connection.close()
                elif self.database_type == 'redis':
                    self.connection.close()
                elif self.database_type == 'cassandra':
                    self.connection.shutdown()

                logger.info(f"✅ Disconnected from {self.database_type} database")
        except Exception as e:
            logger.error(f"Error disconnecting: {e}")

# Convenience functions
def introspect_database(config: Dict[str, Any]) -> DatabaseMetadata:
    """Introspect a database with the given configuration"""
    introspector = DatabaseIntrospector(config)

    if not introspector.connect():
        raise ConnectionError("Failed to connect to database")

    try:
        return introspector.introspect()
    finally:
        introspector.disconnect()

def create_database_notebook(db_type: str, config: Dict[str, Any]) -> str:
    """Create a comprehensive database notebook for the specified type"""
    introspector = DatabaseIntrospector(config)

    if not introspector.connect():
        raise ConnectionError(f"Failed to connect to {db_type} database")

    try:
        metadata = introspector.introspect()
        report = introspector.generate_report()

        # Create notebook content
        notebook = {
            "cells": [
                {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": [
                        f"# 🗄️ {db_type.upper()} Database Introspection & CRUD Operations\n",
                        "\n",
                        f"This notebook provides comprehensive {db_type.upper()} database operations including:\n",
                        "\n",
                        "- 🔍 **Database Introspection**: Complete metadata analysis\n",
                        "- 🏗️ **Schema Operations**: Create, modify, and manage database objects\n",
                        "- 📊 **CRUD Operations**: Create, Read, Update, Delete operations\n",
                        "- 🔍 **Advanced Queries**: Complex queries and analytics\n",
                        "- 📈 **Performance Optimization**: Indexing and optimization\n",
                        "- 🔐 **Security**: Permissions and access control\n",
                        "- 📋 **Backup & Recovery**: Data management operations\n",
                        "\n",
                        "---"
                    ]
                },
                {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": [
                        "## 🔧 Environment Setup\n",
                        "\n",
                        "First, let's set up the environment and establish database connection."
                    ]
                },
                {
                    "cell_type": "code",
                    "metadata": {},
                    "source": [
                        "# Import required modules\n",
                        "import sys\n",
                        "import os\n",
                        "from pathlib import Path\n",
                        "\n",
                        "# Add src to path\n",
                        "sys.path.insert(0, str(Path('../src').resolve()))\n",
                        "\n",
                        "# Import database introspection utility\n",
                        "from src.core.database_introspection import DatabaseIntrospector, introspect_database\n",
                        "\n",
                        "print('✅ Environment setup complete')"
                    ],
                    "execution_count": None,
                    "outputs": []
                },
                {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": [
                        "## 🔍 Database Introspection\n",
                        "\n",
                        "Let's analyze the database structure and metadata."
                    ]
                },
                {
                    "cell_type": "code",
                    "metadata": {},
                    "source": [
                        "# Database configuration\n",
                        f"db_config = {json.dumps(config, indent=2)}\n",
                        "\n",
                        "# Create introspector instance\n",
                        "introspector = DatabaseIntrospector(db_config)\n",
                        "\n",
                        "# Connect to database\n",
                        "if introspector.connect():\n",
                        "    print('✅ Database connection established')\n",
                        "    \n",
                        "    # Perform introspection\n",
                        "    metadata = introspector.introspect()\n",
                        "    print(f'✅ Introspection completed for {{metadata.database_name}}')\n",
                        "    print(f'Database Type: {{metadata.database_type}}')\n",
                        "    print(f'Version: {{metadata.version}}')\n",
                        "    print(f'Tables: {{len(metadata.tables)}}')\n",
                        "    print(f'Views: {{len(metadata.views)}}')\n",
                        "    print(f'Functions: {{len(metadata.functions)}}')\n",
                        "    print(f'Procedures: {{len(metadata.procedures)}}')\n",
                        "else:\n",
                        "    print('❌ Failed to connect to database')"
                    ],
                    "execution_count": None,
                    "outputs": []
                },
                {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": [
                        "## 📋 Database Objects Overview\n",
                        "\n",
                        "Here's a comprehensive overview of all database objects:"
                    ]
                }
            ],
            "metadata": {
                "kernelspec": {
                    "display_name": "ValidoAI Python",
                    "language": "python",
                    "name": "validoai-python"
                },
                "language_info": {
                    "codemirror_mode": {
                        "name": "ipython",
                        "version": 3
                    },
                    "file_extension": ".py",
                    "mimetype": "text/x-python",
                    "name": "python",
                    "nbconvert_exporter": "python",
                    "pygments_lexer": "ipython3",
                    "version": "3.12.0"
                }
            },
            "nbformat": 4,
            "nbformat_minor": 4
        }

        # Add database objects sections
        if metadata.tables:
            notebook["cells"].append({
                "cell_type": "markdown",
                "metadata": {},
                "source": ["## 📊 Tables\n", "\n", "List of all tables in the database:"]
            })

            table_list = []
            for table in metadata.tables:
                table_list.append(f"- {table.schema}.{table.name}" if table.schema else f"- {table.name}")

            notebook["cells"].append({
                "cell_type": "markdown",
                "metadata": {},
                "source": ["\\n".join(table_list)]
            })

        if metadata.views:
            notebook["cells"].append({
                "cell_type": "markdown",
                "metadata": {},
                "source": ["## 👁️ Views\n", "\n", "List of all views in the database:"]
            })

            view_list = []
            for view in metadata.views:
                view_list.append(f"- {view.schema}.{view.name}" if view.schema else f"- {view.name}")

            notebook["cells"].append({
                "cell_type": "markdown",
                "metadata": {},
                "source": ["\\n".join(view_list)]
            })

        if metadata.functions:
            notebook["cells"].append({
                "cell_type": "markdown",
                "metadata": {},
                "source": ["## 🔧 Functions\n", "\n", "List of all functions in the database:"]
            })

            func_list = []
            for func in metadata.functions:
                func_list.append(f"- {func.schema}.{func.name}" if func.schema else f"- {func.name}")

            notebook["cells"].append({
                "cell_type": "markdown",
                "metadata": {},
                "source": ["\\n".join(func_list)]
            })

        # Add CRUD operations section
        notebook["cells"].extend([
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## 📊 CRUD Operations\n",
                    "\n",
                    "Let's demonstrate basic CRUD operations with the database."
                ]
            },
            {
                "cell_type": "code",
                "metadata": {},
                "source": [
                    "# Example CRUD operations\n",
                    "# This section would contain database-specific CRUD examples\n",
                    "\n",
                    "print('CRUD operations section - customize for your specific database')"
                ],
                "execution_count": None,
                "outputs": []
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## 📈 Advanced Analytics\n",
                    "\n",
                    "Let's perform some advanced analytics on the database."
                ]
            },
            {
                "cell_type": "code",
                "metadata": {},
                "source": [
                    "# Advanced analytics section\n",
                    "# This would contain database-specific analytics queries\n",
                    "\n",
                    "print('Advanced analytics section - customize for your specific database')"
                ],
                "execution_count": None,
                "outputs": []
            }
        ])

        return json.dumps(notebook, indent=2)

    finally:
        introspector.disconnect()

if __name__ == '__main__':
    # CLI interface for database introspection
    import argparse

    parser = argparse.ArgumentParser(description='Database Introspection Tool')
    parser.add_argument('action', choices=['introspect', 'notebook', 'list'],
                       help='Action to perform')
    parser.add_argument('--type', '-t', required=True,
                       choices=['postgresql', 'mysql', 'sqlite', 'mssql', 'mongodb', 'redis', 'cassandra'],
                       help='Database type')
    parser.add_argument('--host', default='localhost', help='Database host')
    parser.add_argument('--port', type=int, help='Database port')
    parser.add_argument('--database', '-d', required=True, help='Database name')
    parser.add_argument('--username', '-u', help='Database username')
    parser.add_argument('--password', '-p', help='Database password')
    parser.add_argument('--output', '-o', help='Output file path')

    args = parser.parse_args()

    # Set default ports
    default_ports = {
        'postgresql': 5432,
        'mysql': 3306,
        'mssql': 1433,
        'mongodb': 27017,
        'redis': 6379,
        'cassandra': 9042
    }

    config = {
        'type': args.type,
        'host': args.host,
        'port': args.port or default_ports.get(args.type, 5432),
        'database': args.database,
        'username': args.username,
        'password': args.password
    }

    if args.action == 'introspect':
        try:
            metadata = introspect_database(config)
            report = DatabaseIntrospector(config).generate_report()
            print(report)

            if args.output:
                with open(args.output, 'w') as f:
                    f.write(report)
                print(f"\\n✅ Report saved to {args.output}")

        except Exception as e:
            print(f"❌ Introspection failed: {e}")
            sys.exit(1)

    elif args.action == 'notebook':
        try:
            notebook_content = create_database_notebook(args.type, config)
            output_file = args.output or f"{args.type}_database_operations.ipynb"

            with open(output_file, 'w') as f:
                f.write(notebook_content)

            print(f"✅ Notebook created: {output_file}")

        except Exception as e:
            print(f"❌ Notebook creation failed: {e}")
            sys.exit(1)

    elif args.action == 'list':
        # List available database drivers
        drivers = {
            'postgresql': POSTGRESQL_AVAILABLE,
            'mysql': MYSQL_AVAILABLE,
            'sqlite': SQLITE_AVAILABLE,
            'mssql': MSSQL_AVAILABLE,
            'mongodb': MONGODB_AVAILABLE,
            'redis': REDIS_AVAILABLE,
            'cassandra': CASSANDRA_AVAILABLE
        }

        print("📦 Available Database Drivers:")
        for db_type, available in drivers.items():
            status = "✅ Available" if available else "❌ Not Available"
            print("15")
        print("\\n💡 Install missing drivers with:")
        print("pip install psycopg2-binary pymysql pyodbc pymongo redis cassandra-driver")
