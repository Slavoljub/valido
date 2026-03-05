"""
Data Integrator
Handles multiple data source integration for AI processing
"""

import logging
import pandas as pd
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
import sqlite3
import sqlalchemy
from sqlalchemy import create_engine
import pymysql
import psycopg2
import pymongo
from pymongo import MongoClient
import pyarrow as pa
import pyarrow.parquet as pq
from PIL import Image
import fitz  # PyMuPDF for PDF processing
import tabula
import io
from datetime import datetime

logger = logging.getLogger(__name__)

try:
    import magic
    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False
    logger.warning("python-magic not available, file type detection will be limited")

class DataSourceError(Exception):
    """Custom exception for data source errors"""
    pass

class DatabaseConnector:
    """Base class for database connections"""

    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.engine = None

    def connect(self):
        """Connect to database"""
        raise NotImplementedError

    def disconnect(self):
        """Disconnect from database"""
        if self.engine:
            self.engine.dispose()

    def execute_query(self, query: str) -> pd.DataFrame:
        """Execute query and return DataFrame"""
        raise NotImplementedError

class MySQLConnector(DatabaseConnector):
    """MySQL database connector"""

    def connect(self):
        try:
            self.engine = create_engine(self.connection_string)
            logger.info("Connected to MySQL database")
        except Exception as e:
            raise DataSourceError(f"MySQL connection failed: {e}")

    def execute_query(self, query: str) -> pd.DataFrame:
        if not self.engine:
            self.connect()
        return pd.read_sql(query, self.engine)

class PostgreSQLConnector(DatabaseConnector):
    """PostgreSQL database connector"""

    def connect(self):
        try:
            self.engine = create_engine(self.connection_string)
            logger.info("Connected to PostgreSQL database")
        except Exception as e:
            raise DataSourceError(f"PostgreSQL connection failed: {e}")

    def execute_query(self, query: str) -> pd.DataFrame:
        if not self.engine:
            self.connect()
        return pd.read_sql(query, self.engine)

class MongoDBConnector:
    """MongoDB connector"""

    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.client = None
        self.db = None

    def connect(self, database_name: str):
        try:
            self.client = MongoClient(self.connection_string)
            self.db = self.client[database_name]
            logger.info(f"Connected to MongoDB database: {database_name}")
        except Exception as e:
            raise DataSourceError(f"MongoDB connection failed: {e}")

    def disconnect(self):
        if self.client:
            self.client.close()

    def execute_query(self, collection: str, query: Dict = None) -> pd.DataFrame:
        if not self.db:
            raise DataSourceError("Not connected to database")

        if query is None:
            query = {}

        cursor = self.db[collection].find(query)
        data = list(cursor)
        return pd.DataFrame(data)

class SQLiteConnector(DatabaseConnector):
    """SQLite database connector"""

    def connect(self):
        try:
            self.engine = create_engine(self.connection_string)
            logger.info("Connected to SQLite database")
        except Exception as e:
            raise DataSourceError(f"SQLite connection failed: {e}")

    def execute_query(self, query: str) -> pd.DataFrame:
        if not self.engine:
            self.connect()
        return pd.read_sql(query, self.engine)

class DataIntegrator:
    """Main data integration class"""

    def __init__(self):
        self.supported_formats = {
            'parquet': self._load_parquet,
            'json': self._load_json,
            'excel': self._load_excel,
            'csv': self._load_csv,
            'pdf': self._load_pdf,
            'image': self._load_image,
            'sqlite': self._load_sqlite,
            'mysql': self._load_mysql,
            'postgresql': self._load_postgresql,
            'mongodb': self._load_mongodb
        }

        # Use the unified database connector manager
        from .database_manager import db_manager
        self.db_manager = db_manager

        self.mime_types = {
            'application/vnd.ms-excel': 'excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'excel',
            'text/csv': 'csv',
            'application/json': 'json',
            'application/parquet': 'parquet',
            'application/pdf': 'pdf',
            'image/jpeg': 'image',
            'image/png': 'image',
            'image/gif': 'image',
            'image/webp': 'image'
        }

    def load_data_source(self, source_path: Union[str, Path], format_type: str = None,
                        **kwargs) -> pd.DataFrame:
        """
        Load data from various sources

        Args:
            source_path: Path to data source or database connection string
            format_type: Type of data source ('parquet', 'json', 'excel', 'csv',
                        'pdf', 'image', 'sqlite', 'mysql', 'postgresql', 'mongodb')
            **kwargs: Additional parameters for specific data sources

        Returns:
            DataFrame containing the loaded data
        """
        try:
            # Auto-detect format if not specified
            if not format_type:
                format_type = self._detect_format(source_path)

            if format_type not in self.supported_formats:
                raise DataSourceError(f"Unsupported format: {format_type}")

            loader = self.supported_formats[format_type]
            return loader(source_path, **kwargs)

        except Exception as e:
            logger.error(f"Error loading data source {source_path}: {e}")
            raise DataSourceError(f"Failed to load data source: {e}")

    def _detect_format(self, source_path: Union[str, Path]) -> str:
        """Auto-detect file format"""
        source_path = Path(source_path)

        # Check file extension first
        extension = source_path.suffix.lower()
        if extension == '.parquet':
            return 'parquet'
        elif extension in ['.xlsx', '.xls']:
            return 'excel'
        elif extension == '.csv':
            return 'csv'
        elif extension == '.json':
            return 'json'
        elif extension == '.pdf':
            return 'pdf'
        elif extension in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
            return 'image'
        elif extension == '.db' or extension == '.sqlite':
            return 'sqlite'

        # Use magic to detect MIME type
        if MAGIC_AVAILABLE:
            try:
                mime = magic.from_file(str(source_path), mime=True)
                return self.mime_types.get(mime, 'unknown')
            except Exception:
                pass

        # Fallback to extension-based detection
        return 'unknown'

    def _load_parquet(self, file_path: Union[str, Path], **kwargs) -> pd.DataFrame:
        """Load Parquet file"""
        try:
            return pd.read_parquet(file_path, **kwargs)
        except Exception as e:
            raise DataSourceError(f"Failed to load Parquet file: {e}")

    def _load_json(self, file_path: Union[str, Path], **kwargs) -> pd.DataFrame:
        """Load JSON file"""
        try:
            return pd.read_json(file_path, **kwargs)
        except Exception as e:
            raise DataSourceError(f"Failed to load JSON file: {e}")

    def _load_excel(self, file_path: Union[str, Path], **kwargs) -> pd.DataFrame:
        """Load Excel file"""
        try:
            return pd.read_excel(file_path, **kwargs)
        except Exception as e:
            raise DataSourceError(f"Failed to load Excel file: {e}")

    def _load_csv(self, file_path: Union[str, Path], **kwargs) -> pd.DataFrame:
        """Load CSV file"""
        try:
            return pd.read_csv(file_path, **kwargs)
        except Exception as e:
            raise DataSourceError(f"Failed to load CSV file: {e}")

    def _load_pdf(self, file_path: Union[str, Path], **kwargs) -> pd.DataFrame:
        """Load PDF file and extract tables"""
        try:
            # Extract tables using tabula
            tables = tabula.read_pdf(file_path, pages='all', multiple_tables=True, **kwargs)

            if not tables:
                # If no tables found, extract text content
                doc = fitz.open(file_path)
                text_content = []
                for page in doc:
                    text_content.append({
                        'page': page.number + 1,
                        'content': page.get_text()
                    })
                doc.close()
                return pd.DataFrame(text_content)
            else:
                # Combine all tables
                if len(tables) == 1:
                    return tables[0]
                else:
                    return pd.concat(tables, ignore_index=True)

        except Exception as e:
            raise DataSourceError(f"Failed to load PDF file: {e}")

    def _load_image(self, file_path: Union[str, Path], **kwargs) -> pd.DataFrame:
        """Load and analyze image file"""
        try:
            img = Image.open(file_path)
            # Extract basic image metadata
            metadata = {
                'filename': Path(file_path).name,
                'size': img.size,
                'format': img.format,
                'mode': img.mode,
                'width': img.width,
                'height': img.height
            }
            return pd.DataFrame([metadata])
        except Exception as e:
            raise DataSourceError(f"Failed to load image file: {e}")

    def _load_sqlite(self, db_path: Union[str, Path], query: str = None, **kwargs) -> pd.DataFrame:
        """Load data from SQLite database"""
        try:
            from .database_manager import DatabaseConfig as ConnectionConfig
            config = ConnectionConfig(
                db_type='sqlite',
                database=str(db_path).replace('sqlite:///', '').replace('.db', ''),
                connection_string=f"sqlite:///{db_path}"
            )

            if not query:
                # Get all tables and their data
                tables = self.db_manager.get_table_names(config)
                all_data = []
                for table_name in tables:
                    table_query = f"SELECT * FROM {table_name}"
                    table_data = self.db_manager.execute_query(config, table_query)
                    table_data['table_name'] = table_name
                    all_data.append(table_data)
                return pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()
            else:
                return self.db_manager.execute_query(config, query)
        except Exception as e:
            raise DataSourceError(f"Failed to load SQLite data: {e}")

    def _load_mysql(self, connection_string: str, query: str, **kwargs) -> pd.DataFrame:
        """Load data from MySQL database"""
        try:
            from .database_manager import DatabaseConfig as ConnectionConfig
            from urllib.parse import urlparse

            parsed = urlparse(connection_string)
            config = ConnectionConfig(
                db_type='mysql',
                host=parsed.hostname or 'localhost',
                port=parsed.port or 3306,
                database=parsed.path.lstrip('/') or 'validoai',
                user=parsed.username or 'root',
                password=parsed.password or 'root',
                connection_string=connection_string
            )

            return self.db_manager.execute_query(config, query)
        except Exception as e:
            raise DataSourceError(f"Failed to load MySQL data: {e}")

    def _load_postgresql(self, connection_string: str, query: str, **kwargs) -> pd.DataFrame:
        """Load data from PostgreSQL database"""
        try:
            from .database_manager import DatabaseConfig as ConnectionConfig
            from urllib.parse import urlparse

            parsed = urlparse(connection_string)
            config = ConnectionConfig(
                db_type='postgresql',
                host=parsed.hostname or 'localhost',
                port=parsed.port or 5432,
                database=parsed.path.lstrip('/') or 'validoai',
                user=parsed.username or 'root',
                password=parsed.password or 'root',
                connection_string=connection_string
            )

            return self.db_manager.execute_query(config, query)
        except Exception as e:
            raise DataSourceError(f"Failed to load PostgreSQL data: {e}")

    def _load_mongodb(self, connection_string: str, database: str, collection: str,
                     query: Dict = None, **kwargs) -> pd.DataFrame:
        """Load data from MongoDB"""
        try:
            from .database_manager import DatabaseConfig as ConnectionConfig

            config = ConnectionConfig(
                db_type='mongodb',
                database=database,
                connection_string=connection_string
            )

            # Create query string for MongoDB
            if query:
                import json
                query_str = json.dumps({
                    'collection': collection,
                    'filter': query
                })
            else:
                query_str = collection

            return self.db_manager.execute_query(config, query_str)
        except Exception as e:
            raise DataSourceError(f"Failed to load MongoDB data: {e}")

    def create_embeddings(self, data: pd.DataFrame, text_columns: List[str] = None) -> pd.DataFrame:
        """
        Create embeddings for text data in DataFrame

        Args:
            data: DataFrame to process
            text_columns: List of column names to create embeddings for

        Returns:
            DataFrame with embeddings added
        """
        try:
            from sentence_transformers import SentenceTransformer

            # Initialize embedding model
            model = SentenceTransformer('all-MiniLM-L6-v2')

            if not text_columns:
                # Auto-detect text columns
                text_columns = data.select_dtypes(include=['object']).columns.tolist()

            for column in text_columns:
                if column in data.columns:
                    # Convert to string and create embeddings
                    text_data = data[column].astype(str).tolist()
                    embeddings = model.encode(text_data)

                    # Add embedding column
                    data[f'{column}_embedding'] = list(embeddings)

            logger.info(f"Created embeddings for {len(text_columns)} text columns")
            return data

        except Exception as e:
            logger.error(f"Error creating embeddings: {e}")
            return data

    def merge_data_sources(self, data_sources: List[pd.DataFrame],
                          merge_column: str = None) -> pd.DataFrame:
        """
        Merge multiple data sources

        Args:
            data_sources: List of DataFrames to merge
            merge_column: Column name to merge on (if None, concatenate)

        Returns:
            Merged DataFrame
        """
        try:
            if not data_sources:
                return pd.DataFrame()

            if len(data_sources) == 1:
                return data_sources[0]

            if merge_column:
                merged = data_sources[0]
                for df in data_sources[1:]:
                    merged = pd.merge(merged, df, on=merge_column, how='outer')
                return merged
            else:
                return pd.concat(data_sources, ignore_index=True)

        except Exception as e:
            logger.error(f"Error merging data sources: {e}")
            raise DataSourceError(f"Failed to merge data sources: {e}")

    def validate_data(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate data quality and provide statistics

        Args:
            data: DataFrame to validate

        Returns:
            Dictionary with validation results
        """
        try:
            validation_results = {
                'shape': data.shape,
                'columns': list(data.columns),
                'dtypes': data.dtypes.to_dict(),
                'null_counts': data.isnull().sum().to_dict(),
                'duplicate_count': data.duplicated().sum(),
                'memory_usage_mb': data.memory_usage(deep=True).sum() / (1024 * 1024)
            }

            # Add basic statistics for numeric columns
            numeric_columns = data.select_dtypes(include=['number']).columns
            if len(numeric_columns) > 0:
                validation_results['numeric_stats'] = data[numeric_columns].describe().to_dict()

            return validation_results

        except Exception as e:
            logger.error(f"Error validating data: {e}")
            return {'error': str(e)}

# Global instance
data_integrator = DataIntegrator()
