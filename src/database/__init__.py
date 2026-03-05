"""
ValidoAI - Unified Database System
==================================
Centralized database management following Cursor Rules
Supports multiple database types with unified interface
"""

import os
import sqlite3
import logging
from typing import Optional, Dict, Any, List, Union
from pathlib import Path
from datetime import datetime, timedelta
import random
from contextlib import contextmanager
from dataclasses import dataclass
from urllib.parse import urlparse

# Import master configuration system
# Import configuration with fallback
try:
    from src.config import config_manager
    MASTER_CONFIG_AVAILABLE = True
    print("✅ Master configuration available")
except ImportError:
    MASTER_CONFIG_AVAILABLE = False
    print("⚠️ Master configuration not available, using fallback")

# Database driver imports with fallbacks
try:
    import psycopg2
    POSTGRESQL_AVAILABLE = True
except ImportError:
    POSTGRESQL_AVAILABLE = False

try:
    import pymysql
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False

try:
    import pymongo
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

try:
    from elasticsearch import Elasticsearch
    ELASTICSEARCH_AVAILABLE = True
except ImportError:
    ELASTICSEARCH_AVAILABLE = False

try:
    from cassandra.cluster import Cluster
    CASSANDRA_AVAILABLE = True
    print("✅ Cassandra available")
except (ImportError, Exception) as e:
    CASSANDRA_AVAILABLE = False
    print(f"⚠️ Cassandra not available: {e} - install build dependencies for cassandra-driver")

try:
    from neo4j import GraphDatabase
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False

try:
    import couchdb
    COUCHDB_AVAILABLE = True
except ImportError:
    COUCHDB_AVAILABLE = False

try:
    from couchbase.cluster import Cluster as CouchbaseCluster
    from couchbase.auth import PasswordAuthenticator
    COUCHBASE_AVAILABLE = True
except ImportError:
    COUCHBASE_AVAILABLE = False

try:
    from influxdb_client import InfluxDBClient
    INFLUXDB_AVAILABLE = True
except ImportError:
    INFLUXDB_AVAILABLE = False

try:
    import clickhouse_driver
    CLICKHOUSE_AVAILABLE = True
except ImportError:
    CLICKHOUSE_AVAILABLE = False

try:
    import boto3
    DYNAMODB_AVAILABLE = True
except ImportError:
    DYNAMODB_AVAILABLE = False

try:
    from azure.cosmos import CosmosClient
    COSMOSDB_AVAILABLE = True
except ImportError:
    COSMOSDB_AVAILABLE = False

try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    FIRESTORE_AVAILABLE = True
except ImportError:
    FIRESTORE_AVAILABLE = False

try:
    from arango import ArangoClient
    ARANGODB_AVAILABLE = True
except ImportError:
    ARANGODB_AVAILABLE = False

try:
    import pyorient
    ORIENTDB_AVAILABLE = True
except ImportError:
    ORIENTDB_AVAILABLE = False

try:
    import pyodbc
    MSSQL_AVAILABLE = True
except ImportError:
    MSSQL_AVAILABLE = False

# Vector Database Support (with graceful fallbacks)
try:
    import pinecone
    PINECONE_AVAILABLE = True
    print("✅ Pinecone available")
except ImportError:
    try:
        import pinecone_client
        PINECONE_AVAILABLE = True
        print("✅ Pinecone client available")
    except ImportError:
        PINECONE_AVAILABLE = False
        print("⚠️ Pinecone not available - install with: pip install pinecone")

try:
    from weaviate import Client as WeaviateClient
    WEAVIATE_AVAILABLE = True
    print("✅ Weaviate available")
except ImportError:
    WEAVIATE_AVAILABLE = False
    print("⚠️ Weaviate not available - install with: pip install weaviate-client")

try:
    from qdrant_client import QdrantClient
    QDRANT_AVAILABLE = True
    print("✅ Qdrant available")
except ImportError:
    QDRANT_AVAILABLE = False
    print("⚠️ Qdrant not available - install with: pip install qdrant-client")

try:
    import chromadb
    CHROMADB_AVAILABLE = True
    print("✅ ChromaDB available")
except ImportError:
    CHROMADB_AVAILABLE = False
    print("⚠️ ChromaDB not available - install with: pip install chromadb")

try:
    from milvus import default_server
    MILVUS_AVAILABLE = True
    print("✅ Milvus available")
except ImportError:
    MILVUS_AVAILABLE = False
    print("⚠️ Milvus not available - install with: pip install pymilvus")

try:
    import faiss
    FAISS_AVAILABLE = True
    print("✅ FAISS available")
except ImportError:
    FAISS_AVAILABLE = False
    print("⚠️ FAISS not available - install with: pip install faiss-cpu")

try:
    import sentence_transformers
    SENTENCE_TRANSFORMERS_AVAILABLE = True
    print("✅ Sentence Transformers available")
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    print("⚠️ Sentence Transformers not available - install with: pip install sentence-transformers")

try:
    import openai
    OPENAI_EMBEDDINGS_AVAILABLE = True
    print("✅ OpenAI available")
except ImportError:
    OPENAI_EMBEDDINGS_AVAILABLE = False
    print("⚠️ OpenAI not available - install with: pip install openai")

logger = logging.getLogger(__name__)

# Import global logger if available
try:
    from src.core.global_logger import global_logger, ErrorContext, ErrorSeverity, ErrorCategory
    GLOBAL_LOGGER_AVAILABLE = True
except ImportError:
    GLOBAL_LOGGER_AVAILABLE = False

def log_database_error(operation: str, error: Exception, context_data: dict = None):
    """Log database errors using global logger"""
    if GLOBAL_LOGGER_AVAILABLE:
        context = ErrorContext(**context_data) if context_data else ErrorContext()
        context.component = "database"
        context.function = operation
        global_logger.log_error(
            f"Database error during {operation}: {str(error)}",
            ErrorSeverity.ERROR,
            ErrorCategory.DATABASE,
            error,
            context,
            tags=['database', operation]
        )
    else:
        logger.error(f"Database error during {operation}: {error}")

# ============================================================================
# DATABASE CONFIGURATION CLASSES (Following Factory Pattern)
# ============================================================================

@dataclass
class DatabaseConnection:
    """Database connection wrapper following adapter pattern"""
    connection: Any
    connection_type: str
    database_type: str

    def close(self):
        """Close the database connection"""
        if self.connection:
            try:
                if hasattr(self.connection, 'close'):
                    self.connection.close()
                logger.info("✅ Database connection closed")
            except Exception as e:
                logger.error(f"❌ Error closing database connection: {e}")

    def get_cursor(self):
        """Get database cursor"""
        try:
            if self.database_type == 'sqlite':
                return self.connection.cursor()
            elif self.database_type in ['postgresql', 'mysql']:
                return self.connection.cursor()
            else:
                raise NotImplementedError(f"Cursor not implemented for {self.database_type}")
        except Exception as e:
            logger.error(f"❌ Error getting database cursor: {e}")
            raise

    def commit(self):
        """Commit transaction"""
        try:
            if hasattr(self.connection, 'commit'):
                self.connection.commit()
        except Exception as e:
            logger.error(f"❌ Error committing transaction: {e}")
            raise

    def rollback(self):
        """Rollback transaction"""
        try:
            if hasattr(self.connection, 'rollback'):
                self.connection.rollback()
        except Exception as e:
            logger.error(f"❌ Error rolling back transaction: {e}")
            raise

@dataclass
class VectorDatabaseConnection:
    """Vector database connection wrapper following adapter pattern"""
    connection: Any
    connection_type: str
    database_type: str
    embedding_model: Optional[Any] = None
    embedding_dimension: int = 384  # Default for most sentence transformers

    def close(self):
        """Close the vector database connection"""
        if self.connection:
            try:
                if hasattr(self.connection, 'close'):
                    self.connection.close()
                logger.info("✅ Vector database connection closed")
            except Exception as e:
                logger.error(f"❌ Error closing vector database connection: {e}")

    def embed_text(self, text: str) -> List[float]:
        """Generate embeddings for text"""
        try:
            if self.embedding_model:
                return self.embedding_model.encode([text])[0].tolist()
            elif OPENAI_EMBEDDINGS_AVAILABLE:
                # Fallback to OpenAI embeddings
                import openai
                client = openai.OpenAI()
                response = client.embeddings.create(
                    input=text,
                    model="text-embedding-3-small"
                )
                return response.data[0].embedding
            else:
                raise NotImplementedError("No embedding model available")
        except Exception as e:
            logger.error(f"❌ Error generating embeddings: {e}")
            raise

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        try:
            if self.embedding_model:
                return self.embedding_model.encode(texts).tolist()
            elif OPENAI_EMBEDDINGS_AVAILABLE:
                # Fallback to OpenAI embeddings
                import openai
                client = openai.OpenAI()
                response = client.embeddings.create(
                    input=texts,
                    model="text-embedding-3-small"
                )
                return [data.embedding for data in response.data]
            else:
                raise NotImplementedError("No embedding model available")
        except Exception as e:
            logger.error(f"❌ Error generating batch embeddings: {e}")
            raise

    def similarity_search(self, query: str, limit: int = 10, **kwargs) -> List[Dict[str, Any]]:
        """Perform similarity search"""
        try:
            query_embedding = self.embed_text(query)
            return self._perform_similarity_search(query_embedding, limit, **kwargs)
        except Exception as e:
            logger.error(f"❌ Error performing similarity search: {e}")
            raise

    def _perform_similarity_search(self, query_embedding: List[float], limit: int, **kwargs) -> List[Dict[str, Any]]:
        """Perform similarity search (to be implemented by subclasses)"""
        raise NotImplementedError("Similarity search not implemented for this vector database")

    def insert_vectors(self, vectors: List[List[float]], metadata: List[Dict[str, Any]], **kwargs):
        """Insert vectors with metadata"""
        raise NotImplementedError("Vector insertion not implemented for this vector database")

    def delete_vectors(self, vector_ids: List[str], **kwargs):
        """Delete vectors by ID"""
        raise NotImplementedError("Vector deletion not implemented for this vector database")

    def update_vectors(self, vector_ids: List[str], vectors: List[List[float]], metadata: List[Dict[str, Any]], **kwargs):
        """Update vectors and metadata"""
        raise NotImplementedError("Vector update not implemented for this vector database")

# ============================================================================
# VECTOR DATABASE IMPLEMENTATIONS
# ============================================================================

class PineconeVectorConnection(VectorDatabaseConnection):
    """Pinecone-specific vector database implementation"""

    def _perform_similarity_search(self, query_embedding: List[float], limit: int, **kwargs) -> List[Dict[str, Any]]:
        """Perform similarity search in Pinecone"""
        try:
            index = self.connection['index']
            results = index.query(
                vector=query_embedding,
                top_k=limit,
                include_metadata=True,
                **kwargs
            )

            search_results = []
            for match in results['matches']:
                search_results.append({
                    'id': match['id'],
                    'score': match['score'],
                    'metadata': match.get('metadata', {}),
                    'vector': match.get('vector', [])
                })

            return search_results

        except Exception as e:
            logger.error(f"❌ Pinecone similarity search error: {e}")
            return []

    def insert_vectors(self, vectors: List[List[float]], metadata: List[Dict[str, Any]], **kwargs):
        """Insert vectors into Pinecone"""
        try:
            index = self.connection['index']

            # Prepare data for Pinecone
            upsert_data = []
            for i, (vector, meta) in enumerate(zip(vectors, metadata)):
                vector_id = meta.get('id', f"vec_{i}")
                upsert_data.append((vector_id, vector, meta))

            index.upsert(vectors=upsert_data)
            logger.info(f"✅ Inserted {len(vectors)} vectors into Pinecone")

        except Exception as e:
            logger.error(f"❌ Pinecone vector insertion error: {e}")
            raise

    def delete_vectors(self, vector_ids: List[str], **kwargs):
        """Delete vectors from Pinecone"""
        try:
            index = self.connection['index']
            index.delete(ids=vector_ids)
            logger.info(f"✅ Deleted {len(vector_ids)} vectors from Pinecone")

        except Exception as e:
            logger.error(f"❌ Pinecone vector deletion error: {e}")
            raise

class ChromaVectorConnection(VectorDatabaseConnection):
    """ChromaDB-specific vector database implementation"""

    def _perform_similarity_search(self, query_embedding: List[float], limit: int, **kwargs) -> List[Dict[str, Any]]:
        """Perform similarity search in ChromaDB"""
        try:
            collection = self.connection['collection']
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=limit,
                **kwargs
            )

            search_results = []
            for i, (doc_id, distance, metadata) in enumerate(zip(
                results['ids'][0],
                results['distances'][0],
                results['metadatas'][0]
            )):
                search_results.append({
                    'id': doc_id,
                    'score': 1.0 / (1.0 + distance),  # Convert distance to similarity score
                    'metadata': metadata,
                    'distance': distance
                })

            return search_results

        except Exception as e:
            logger.error(f"❌ ChromaDB similarity search error: {e}")
            return []

    def insert_vectors(self, vectors: List[List[float]], metadata: List[Dict[str, Any]], **kwargs):
        """Insert vectors into ChromaDB"""
        try:
            collection = self.connection['collection']

            ids = [meta.get('id', f"vec_{i}") for i, meta in enumerate(metadata)]
            documents = [meta.get('text', '') for meta in metadata]

            collection.add(
                embeddings=vectors,
                metadatas=metadata,
                documents=documents,
                ids=ids
            )

            logger.info(f"✅ Inserted {len(vectors)} vectors into ChromaDB")

        except Exception as e:
            logger.error(f"❌ ChromaDB vector insertion error: {e}")
            raise

    def delete_vectors(self, vector_ids: List[str], **kwargs):
        """Delete vectors from ChromaDB"""
        try:
            collection = self.connection['collection']
            collection.delete(ids=vector_ids)
            logger.info(f"✅ Deleted {len(vector_ids)} vectors from ChromaDB")

        except Exception as e:
            logger.error(f"❌ ChromaDB vector deletion error: {e}")
            raise

class WeaviateVectorConnection(VectorDatabaseConnection):
    """Weaviate-specific vector database implementation"""

    def _perform_similarity_search(self, query_embedding: List[float], limit: int, **kwargs) -> List[Dict[str, Any]]:
        """Perform similarity search in Weaviate"""
        try:
            client = self.connection

            # Define the class name for search
            class_name = kwargs.get('class_name', 'Document')

            results = client.query.get(
                class_name,
                ["content", "title", "url", "timestamp"]
            ).with_near_vector({
                "vector": query_embedding
            }).with_limit(limit).with_additional(["distance", "id"]).do()

            search_results = []
            if 'data' in results and 'Get' in results['data']:
                for item in results['data']['Get'][class_name]:
                    search_results.append({
                        'id': item.get('_additional', {}).get('id', ''),
                        'score': item.get('_additional', {}).get('distance', 0),
                        'metadata': {
                            'content': item.get('content', ''),
                            'title': item.get('title', ''),
                            'url': item.get('url', ''),
                            'timestamp': item.get('timestamp', '')
                        }
                    })

            return search_results

        except Exception as e:
            logger.error(f"❌ Weaviate similarity search error: {e}")
            return []

    def insert_vectors(self, vectors: List[List[float]], metadata: List[Dict[str, Any]], **kwargs):
        """Insert vectors into Weaviate"""
        try:
            client = self.connection
            class_name = kwargs.get('class_name', 'Document')

            # Prepare data objects
            with client.batch as batch:
                for i, (vector, meta) in enumerate(zip(vectors, metadata)):
                    properties = {
                        'content': meta.get('text', ''),
                        'title': meta.get('title', ''),
                        'url': meta.get('url', ''),
                        'timestamp': meta.get('timestamp', '')
                    }

                    batch.add_data_object(
                        data_object=properties,
                        class_name=class_name,
                        vector=vector
                    )

            logger.info(f"✅ Inserted {len(vectors)} vectors into Weaviate")

        except Exception as e:
            logger.error(f"❌ Weaviate vector insertion error: {e}")
            raise

class QdrantVectorConnection(VectorDatabaseConnection):
    """Qdrant-specific vector database implementation"""

    def _perform_similarity_search(self, query_embedding: List[float], limit: int, **kwargs) -> List[Dict[str, Any]]:
        """Perform similarity search in Qdrant"""
        try:
            client = self.connection
            collection_name = kwargs.get('collection_name', 'validoai')

            results = client.search(
                collection_name=collection_name,
                query_vector=query_embedding,
                limit=limit,
                **kwargs
            )

            search_results = []
            for result in results:
                search_results.append({
                    'id': result.id,
                    'score': result.score,
                    'metadata': result.payload,
                    'vector': result.vector
                })

            return search_results

        except Exception as e:
            logger.error(f"❌ Qdrant similarity search error: {e}")
            return []

    def insert_vectors(self, vectors: List[List[float]], metadata: List[Dict[str, Any]], **kwargs):
        """Insert vectors into Qdrant"""
        try:
            client = self.connection
            collection_name = kwargs.get('collection_name', 'validoai')

            points = []
            for i, (vector, meta) in enumerate(zip(vectors, metadata)):
                point_id = meta.get('id', i)
                points.append({
                    'id': point_id,
                    'vector': vector,
                    'payload': meta
                })

            client.upsert(
                collection_name=collection_name,
                points=points
            )

            logger.info(f"✅ Inserted {len(vectors)} vectors into Qdrant")

        except Exception as e:
            logger.error(f"❌ Qdrant vector insertion error: {e}")
            raise

    def delete_vectors(self, vector_ids: List[str], **kwargs):
        """Delete vectors from Qdrant"""
        try:
            client = self.connection
            collection_name = kwargs.get('collection_name', 'validoai')

            client.delete(
                collection_name=collection_name,
                points_selector={'points': vector_ids}
            )

            logger.info(f"✅ Deleted {len(vector_ids)} vectors from Qdrant")

        except Exception as e:
            logger.error(f"❌ Qdrant vector deletion error: {e}")
            raise

class FAISSVectorConnection(VectorDatabaseConnection):
    """FAISS-specific vector database implementation"""

    def _perform_similarity_search(self, query_embedding: List[float], limit: int, **kwargs) -> List[Dict[str, Any]]:
        """Perform similarity search in FAISS"""
        try:
            index = self.connection['index']
            index_path = self.connection['index_path']

            # Convert to numpy array
            import numpy as np
            query_vector = np.array([query_embedding], dtype=np.float32)

            # Search
            distances, indices = index.search(query_vector, limit)

            search_results = []
            for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
                if idx != -1:  # Valid result
                    search_results.append({
                        'id': str(idx),
                        'score': 1.0 / (1.0 + distance),  # Convert distance to similarity
                        'metadata': {'index': idx},
                        'distance': distance
                    })

            return search_results

        except Exception as e:
            logger.error(f"❌ FAISS similarity search error: {e}")
            return []

    def insert_vectors(self, vectors: List[List[float]], metadata: List[Dict[str, Any]], **kwargs):
        """Insert vectors into FAISS"""
        try:
            index = self.connection['index']
            index_path = self.connection['index_path']

            # Convert to numpy array
            import numpy as np
            vector_array = np.array(vectors, dtype=np.float32)

            # Add to index
            index.add(vector_array)

            # Save index
            faiss.write_index(index, index_path)

            logger.info(f"✅ Inserted {len(vectors)} vectors into FAISS")

        except Exception as e:
            logger.error(f"❌ FAISS vector insertion error: {e}")
            raise

# ============================================================================
# VECTOR DATABASE FACTORY
# ============================================================================

class VectorDatabaseFactory:
    """Factory for creating vector database connections"""

    @staticmethod
    def create_connection(database_type: str) -> VectorDatabaseConnection:
        """Create vector database connection based on type"""
        connection_manager = DatabaseConnectionManager()

        # Map database types to specific implementations
        vector_db_mappings = {
            'pinecone': lambda: PineconeVectorConnection(
                connection=connection_manager._create_pinecone_connection().connection,
                connection_type='cloud',
                database_type='pinecone'
            ),
            'chromadb': lambda: ChromaVectorConnection(
                connection=connection_manager._create_chromadb_connection().connection,
                connection_type='file',
                database_type='chromadb'
            ),
            'weaviate': lambda: WeaviateVectorConnection(
                connection=connection_manager._create_weaviate_connection().connection,
                connection_type='network',
                database_type='weaviate'
            ),
            'qdrant': lambda: QdrantVectorConnection(
                connection=connection_manager._create_qdrant_connection().connection,
                connection_type='network',
                database_type='qdrant'
            ),
            'faiss': lambda: FAISSVectorConnection(
                connection=connection_manager._create_faiss_connection().connection,
                connection_type='file',
                database_type='faiss'
            )
        }

        if database_type in vector_db_mappings:
            return vector_db_mappings[database_type]()
        else:
            raise NotImplementedError(f"Vector database type {database_type} not supported")

# ============================================================================
# DATABASE CONNECTION MANAGER (Following Singleton Pattern)
# ============================================================================

class DatabaseConnectionManager:
    """Database connection manager following singleton pattern"""

    _instance = None
    _connections = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnectionManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self._current_connection = None

    @contextmanager
    def get_connection(self, database_type: str = None) -> DatabaseConnection:
        """Get database connection as context manager"""
        db_type = database_type or config_manager.get_config('database', {}).get('type')
        connection_key = f"{config_manager.get_config('database', {}).get('type')}_{config_manager.get_config('database', {}).get('database')}"

        try:
            # Check if we have an existing connection
            if connection_key in self._connections:
                connection = self._connections[connection_key]
                # Validate connection is still alive
                if self._validate_connection(connection):
                    yield connection
                    return

            # Create new connection
            connection = self._create_connection(db_type)
            self._connections[connection_key] = connection
            self._current_connection = connection

            yield connection

        except Exception as e:
            logger.error(f"❌ Database connection error: {e}")
            raise
        finally:
            # Connection is managed by context manager
            pass

    def _create_connection(self, database_type: str) -> Union[DatabaseConnection, VectorDatabaseConnection]:
        """Create database connection following factory pattern"""
        try:
            connection_methods = {
                # SQL Databases
                'sqlite': self._create_sqlite_connection,
                'postgresql': self._create_postgresql_connection,
                'mysql': self._create_mysql_connection,
                'mssql': self._create_mssql_connection,

                # NoSQL Databases
                'mongodb': self._create_mongodb_connection,
                'redis': self._create_redis_connection,
                'cassandra': self._create_cassandra_connection,
                'couchdb': self._create_couchdb_connection,
                'couchbase': self._create_couchbase_connection,
                'dynamodb': self._create_dynamodb_connection,
                'cosmosdb': self._create_cosmosdb_connection,
                'firestore': self._create_firestore_connection,

                # Graph Databases
                'neo4j': self._create_neo4j_connection,
                'arangodb': self._create_arangodb_connection,
                'orientdb': self._create_orientdb_connection,

                # Time Series Databases
                'influxdb': self._create_influxdb_connection,
                'clickhouse': self._create_clickhouse_connection,

                # Search Engines
                'elasticsearch': self._create_elasticsearch_connection,

                # Vector Databases
                'pinecone': self._create_pinecone_connection,
                'weaviate': self._create_weaviate_connection,
                'qdrant': self._create_qdrant_connection,
                'chromadb': self._create_chromadb_connection,
                'milvus': self._create_milvus_connection,
                'faiss': self._create_faiss_connection
            }

            if database_type in connection_methods:
                return connection_methods[database_type]()
            else:
                raise NotImplementedError(f"Database type {database_type} not supported")
        except Exception as e:
            logger.error(f"❌ Error creating {database_type} connection: {e}")
            raise

    def _create_sqlite_connection(self) -> DatabaseConnection:
        """Create SQLite connection"""
        try:
            db_path = config_manager.get_config('database', {}).get('database')
            if not db_path:
                db_path = "data/sqlite/validoai.db"

            # Ensure directory exists
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)

            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row  # Enable column access by name

            logger.info(f"✅ SQLite connection established: {db_path}")
            return DatabaseConnection(
                connection=conn,
                connection_type='file',
                database_type='sqlite'
            )

        except Exception as e:
            logger.error(f"❌ SQLite connection error: {e}")
            raise

    def _create_postgresql_connection(self) -> DatabaseConnection:
        """Create PostgreSQL connection"""
        try:
            # Import here to handle optional dependency
            import psycopg2

            conn = psycopg2.connect(
                host=config_manager.get_config('database', {}).get('host'),
                port=config_manager.get_config('database', {}).get('port'),
                database=config_manager.get_config('database', {}).get('database'),
                user=config_manager.get_config('database', {}).get('username'),
                password=config_manager.get_config('database', {}).get('password')
            )

            logger.info(f"✅ PostgreSQL connection established: {config_manager.get_config('database', {}).get('host')}:{config_manager.get_config('database', {}).get('port')}")
            return DatabaseConnection(
                connection=conn,
                connection_type='network',
                database_type='postgresql'
            )

        except ImportError:
            logger.error("❌ psycopg2 not installed. Install with: pip install psycopg2-binary")
            raise
        except Exception as e:
            logger.error(f"❌ PostgreSQL connection error: {e}")
            raise

    def _create_mysql_connection(self) -> DatabaseConnection:
        """Create MySQL connection"""
        try:
            # Import here to handle optional dependency
            import pymysql

            conn = pymysql.connect(
                host=config_manager.get_config('database', {}).get('host'),
                port=config_manager.get_config('database', {}).get('port'),
                database=config_manager.get_config('database', {}).get('database'),
                user=config_manager.get_config('database', {}).get('username'),
                password=config_manager.get_config('database', {}).get('password')
            )

            logger.info(f"✅ MySQL connection established: {config_manager.get_config('database', {}).get('host')}:{config_manager.get_config('database', {}).get('port')}")
            return DatabaseConnection(
                connection=conn,
                connection_type='network',
                database_type='mysql'
            )

        except ImportError:
            logger.error("❌ pymysql not installed. Install with: pip install pymysql")
            raise
        except Exception as e:
            logger.error(f"❌ MySQL connection error: {e}")
            raise

    def _create_mongodb_connection(self) -> DatabaseConnection:
        """Create MongoDB connection"""
        try:
            if not MONGODB_AVAILABLE:
                raise ImportError("pymongo not available")

            mongodb_config = config_manager.get_config('external_services', {}).get('mongodb', {})
            connection_string = mongodb_config.get('connection_string') or \
                              os.environ.get('MONGODB_URL', 'mongodb://localhost:27017/validoai')

            client = pymongo.MongoClient(connection_string)

            logger.info("✅ MongoDB connection established")
            return DatabaseConnection(
                connection=client,
                connection_type='network',
                database_type='mongodb'
            )

        except ImportError:
            logger.error("❌ pymongo not installed. Install with: pip install pymongo")
            raise
        except Exception as e:
            logger.error(f"❌ MongoDB connection error: {e}")
            raise

    def _create_redis_connection(self) -> DatabaseConnection:
        """Create Redis connection"""
        try:
            if not REDIS_AVAILABLE:
                raise ImportError("redis not available")

            redis_config = config_manager.get_config('external_services', {}).get('redis', {})
            host = redis_config.get('host', os.environ.get('REDIS_HOST', 'localhost'))
            port = redis_config.get('port', int(os.environ.get('REDIS_PORT', '6379')))
            db = redis_config.get('db', int(os.environ.get('REDIS_DB', '0')))
            password = redis_config.get('password', os.environ.get('REDIS_PASSWORD', ''))

            conn = redis.Redis(host=host, port=port, db=db, password=password)

            logger.info(f"✅ Redis connection established: {host}:{port}")
            return DatabaseConnection(
                connection=conn,
                connection_type='network',
                database_type='redis'
            )

        except ImportError:
            logger.error("❌ redis not installed. Install with: pip install redis")
            raise
        except Exception as e:
            logger.error(f"❌ Redis connection error: {e}")
            raise

    def _create_elasticsearch_connection(self) -> DatabaseConnection:
        """Create Elasticsearch connection"""
        try:
            if not ELASTICSEARCH_AVAILABLE:
                raise ImportError("elasticsearch not available")

            es_config = config_manager.get_config('external_services', {}).get('elasticsearch', {})
            hosts = es_config.get('hosts', [os.environ.get('ELASTICSEARCH_HOST', 'localhost:9200')])
            username = es_config.get('username', os.environ.get('ELASTICSEARCH_USER', ''))
            password = es_config.get('password', os.environ.get('ELASTICSEARCH_PASSWORD', ''))

            conn = Elasticsearch(
                hosts=hosts,
                http_auth=(username, password) if username and password else None
            )

            logger.info(f"✅ Elasticsearch connection established: {hosts}")
            return DatabaseConnection(
                connection=conn,
                connection_type='network',
                database_type='elasticsearch'
            )

        except ImportError:
            logger.error("❌ elasticsearch not installed. Install with: pip install elasticsearch")
            raise
        except Exception as e:
            logger.error(f"❌ Elasticsearch connection error: {e}")
            raise

    def _create_cassandra_connection(self) -> DatabaseConnection:
        """Create Cassandra connection"""
        try:
            if not CASSANDRA_AVAILABLE:
                raise ImportError("cassandra-driver not available")

            hosts = os.environ.get('CASSANDRA_HOSTS', 'localhost').split(',')
            keyspace = os.environ.get('CASSANDRA_KEYSPACE', 'validoai')

            cluster = Cluster(hosts)
            session = cluster.connect(keyspace)

            logger.info(f"✅ Cassandra connection established: {hosts}")
            return DatabaseConnection(
                connection={'cluster': cluster, 'session': session},
                connection_type='network',
                database_type='cassandra'
            )

        except ImportError:
            logger.error("❌ cassandra-driver not installed. Install with: pip install cassandra-driver")
            raise
        except Exception as e:
            logger.error(f"❌ Cassandra connection error: {e}")
            raise

    def _create_neo4j_connection(self) -> DatabaseConnection:
        """Create Neo4j connection"""
        try:
            if not NEO4J_AVAILABLE:
                raise ImportError("neo4j not available")

            uri = os.environ.get('NEO4J_URL', 'bolt://localhost:7687')
            username = os.environ.get('NEO4J_USER', 'neo4j')
            password = os.environ.get('NEO4J_PASSWORD', 'password')

            driver = GraphDatabase.driver(uri, auth=(username, password))

            logger.info(f"✅ Neo4j connection established: {uri}")
            return DatabaseConnection(
                connection=driver,
                connection_type='network',
                database_type='neo4j'
            )

        except ImportError:
            logger.error("❌ neo4j not installed. Install with: pip install neo4j")
            raise
        except Exception as e:
            logger.error(f"❌ Neo4j connection error: {e}")
            raise

    def _create_couchdb_connection(self) -> DatabaseConnection:
        """Create CouchDB connection"""
        try:
            if not COUCHDB_AVAILABLE:
                raise ImportError("couchdb not available")

            server_url = os.environ.get('COUCHDB_URL', 'http://localhost:5984')
            username = os.environ.get('COUCHDB_USER', 'admin')
            password = os.environ.get('COUCHDB_PASSWORD', 'password')

            server = couchdb.Server(server_url)
            server.resource.credentials = (username, password)

            logger.info(f"✅ CouchDB connection established: {server_url}")
            return DatabaseConnection(
                connection=server,
                connection_type='network',
                database_type='couchdb'
            )

        except ImportError:
            logger.error("❌ couchdb not installed. Install with: pip install couchdb")
            raise
        except Exception as e:
            logger.error(f"❌ CouchDB connection error: {e}")
            raise

    def _create_couchbase_connection(self) -> DatabaseConnection:
        """Create Couchbase connection"""
        try:
            if not COUCHBASE_AVAILABLE:
                raise ImportError("couchbase not available")

            connection_string = os.environ.get('COUCHBASE_URL', 'couchbase://localhost')
            username = os.environ.get('COUCHBASE_USERNAME', 'Administrator')
            password = os.environ.get('COUCHBASE_PASSWORD', 'password')

            auth = PasswordAuthenticator(username, password)
            cluster = CouchbaseCluster(connection_string, auth)

            logger.info(f"✅ Couchbase connection established: {connection_string}")
            return DatabaseConnection(
                connection=cluster,
                connection_type='network',
                database_type='couchbase'
            )

        except ImportError:
            logger.error("❌ couchbase not installed. Install with: pip install couchbase")
            raise
        except Exception as e:
            logger.error(f"❌ Couchbase connection error: {e}")
            raise

    def _create_influxdb_connection(self) -> DatabaseConnection:
        """Create InfluxDB connection"""
        try:
            if not INFLUXDB_AVAILABLE:
                raise ImportError("influxdb-client not available")

            url = os.environ.get('INFLUXDB_URL', 'http://localhost:8086')
            token = os.environ.get('INFLUXDB_TOKEN', '')
            org = os.environ.get('INFLUXDB_ORG', 'validoai')

            client = InfluxDBClient(url=url, token=token, org=org)

            logger.info(f"✅ InfluxDB connection established: {url}")
            return DatabaseConnection(
                connection=client,
                connection_type='network',
                database_type='influxdb'
            )

        except ImportError:
            logger.error("❌ influxdb-client not installed. Install with: pip install influxdb-client")
            raise
        except Exception as e:
            logger.error(f"❌ InfluxDB connection error: {e}")
            raise

    def _create_clickhouse_connection(self) -> DatabaseConnection:
        """Create ClickHouse connection"""
        try:
            if not CLICKHOUSE_AVAILABLE:
                raise ImportError("clickhouse-driver not available")

            host = os.environ.get('CLICKHOUSE_HOST', 'localhost')
            port = int(os.environ.get('CLICKHOUSE_PORT', '9000'))
            database = os.environ.get('CLICKHOUSE_DATABASE', 'validoai')
            user = os.environ.get('CLICKHOUSE_USER', 'default')
            password = os.environ.get('CLICKHOUSE_PASSWORD', '')

            conn = clickhouse_driver.connect(
                host=host,
                port=port,
                database=database,
                user=user,
                password=password
            )

            logger.info(f"✅ ClickHouse connection established: {host}:{port}")
            return DatabaseConnection(
                connection=conn,
                connection_type='network',
                database_type='clickhouse'
            )

        except ImportError:
            logger.error("❌ clickhouse-driver not installed. Install with: pip install clickhouse-driver")
            raise
        except Exception as e:
            logger.error(f"❌ ClickHouse connection error: {e}")
            raise

    def _create_dynamodb_connection(self) -> DatabaseConnection:
        """Create DynamoDB connection"""
        try:
            if not DYNAMODB_AVAILABLE:
                raise ImportError("boto3 not available")

            region = os.environ.get('DYNAMODB_REGION', 'us-east-1')
            endpoint_url = os.environ.get('DYNAMODB_ENDPOINT', None)

            client = boto3.resource(
                'dynamodb',
                region_name=region,
                endpoint_url=endpoint_url,
                aws_access_key_id=os.environ.get('DYNAMODB_ACCESS_KEY_ID', 'local'),
                aws_secret_access_key=os.environ.get('DYNAMODB_SECRET_ACCESS_KEY', 'local')
            )

            logger.info(f"✅ DynamoDB connection established: {region}")
            return DatabaseConnection(
                connection=client,
                connection_type='network',
                database_type='dynamodb'
            )

        except ImportError:
            logger.error("❌ boto3 not installed. Install with: pip install boto3")
            raise
        except Exception as e:
            logger.error(f"❌ DynamoDB connection error: {e}")
            raise

    def _create_cosmosdb_connection(self) -> DatabaseConnection:
        """Create CosmosDB connection"""
        try:
            if not COSMOSDB_AVAILABLE:
                raise ImportError("azure-cosmos not available")

            endpoint = os.environ.get('COSMOSDB_ENDPOINT', '')
            key = os.environ.get('COSMOSDB_KEY', '')

            client = CosmosClient(endpoint, key)

            logger.info(f"✅ CosmosDB connection established: {endpoint}")
            return DatabaseConnection(
                connection=client,
                connection_type='network',
                database_type='cosmosdb'
            )

        except ImportError:
            logger.error("❌ azure-cosmos not installed. Install with: pip install azure-cosmos")
            raise
        except Exception as e:
            logger.error(f"❌ CosmosDB connection error: {e}")
            raise

    def _create_firestore_connection(self) -> DatabaseConnection:
        """Create Firestore connection"""
        try:
            if not FIRESTORE_AVAILABLE:
                raise ImportError("firebase-admin not available")

            cred_path = os.environ.get('FIRESTORE_CREDENTIALS_PATH', '')
            if cred_path and os.path.exists(cred_path):
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
            else:
                firebase_admin.initialize_app()

            client = firestore.client()

            logger.info("✅ Firestore connection established")
            return DatabaseConnection(
                connection=client,
                connection_type='network',
                database_type='firestore'
            )

        except ImportError:
            logger.error("❌ firebase-admin not installed. Install with: pip install firebase-admin")
            raise
        except Exception as e:
            logger.error(f"❌ Firestore connection error: {e}")
            raise

    def _create_arangodb_connection(self) -> DatabaseConnection:
        """Create ArangoDB connection"""
        try:
            if not ARANGODB_AVAILABLE:
                raise ImportError("python-arango not available")

            hosts = os.environ.get('ARANGODB_HOST', 'http://localhost:8529')
            username = os.environ.get('ARANGODB_USER', 'root')
            password = os.environ.get('ARANGODB_PASSWORD', 'password')

            client = ArangoClient(hosts=hosts)
            db = client.db('validoai', username=username, password=password)

            logger.info(f"✅ ArangoDB connection established: {hosts}")
            return DatabaseConnection(
                connection={'client': client, 'db': db},
                connection_type='network',
                database_type='arangodb'
            )

        except ImportError:
            logger.error("❌ python-arango not installed. Install with: pip install python-arango")
            raise
        except Exception as e:
            logger.error(f"❌ ArangoDB connection error: {e}")
            raise

    def _create_orientdb_connection(self) -> DatabaseConnection:
        """Create OrientDB connection"""
        try:
            if not ORIENTDB_AVAILABLE:
                raise ImportError("pyorient not available")

            host = os.environ.get('ORIENTDB_HOST', 'localhost')
            port = int(os.environ.get('ORIENTDB_PORT', '2480'))
            database = os.environ.get('ORIENTDB_DATABASE', 'validoai')
            user = os.environ.get('ORIENTDB_USER', 'admin')
            password = os.environ.get('ORIENTDB_PASSWORD', 'admin')

            client = pyorient.OrientDB(host, port)
            client.connect(user, password)
            db = client.db_open(database, user, password)

            logger.info(f"✅ OrientDB connection established: {host}:{port}")
            return DatabaseConnection(
                connection={'client': client, 'db': db},
                connection_type='network',
                database_type='orientdb'
            )

        except ImportError:
            logger.error("❌ pyorient not installed. Install with: pip install pyorient")
            raise
        except Exception as e:
            logger.error(f"❌ OrientDB connection error: {e}")
            raise

    def _create_mssql_connection(self) -> DatabaseConnection:
        """Create MSSQL connection"""
        try:
            if not MSSQL_AVAILABLE:
                raise ImportError("pyodbc not available")

            connection_string = os.environ.get('MSSQL_URL', '')

            if not connection_string:
                server = os.environ.get('MSSQL_HOST', 'localhost')
                database = os.environ.get('MSSQL_NAME', 'validoai')
                username = os.environ.get('MSSQL_USER', 'sa')
                password = os.environ.get('MSSQL_PASSWORD', '')
                driver = os.environ.get('MSSQL_DRIVER', 'ODBC Driver 17 for SQL Server')

                connection_string = f'DRIVER={{{driver}}};SERVER={server};DATABASE={database};UID={username};PWD={password}'

            conn = pyodbc.connect(connection_string)

            logger.info(f"✅ MSSQL connection established: {server}")
            return DatabaseConnection(
                connection=conn,
                connection_type='network',
                database_type='mssql'
            )

        except ImportError:
            logger.error("❌ pyodbc not installed. Install with: pip install pyodbc")
            raise
        except Exception as e:
            logger.error(f"❌ MSSQL connection error: {e}")
            raise

    def _create_pinecone_connection(self) -> VectorDatabaseConnection:
        """Create Pinecone connection"""
        try:
            if not PINECONE_AVAILABLE:
                raise ImportError("pinecone-client not available")

            api_key = os.environ.get('PINECONE_API_KEY', '')
            environment = os.environ.get('PINECONE_ENVIRONMENT', '')
            index_name = os.environ.get('PINECONE_INDEX_NAME', 'validoai')

            # Handle different Pinecone package versions
            if hasattr(pinecone, 'init'):
                pinecone.init(api_key=api_key, environment=environment)
                index = pinecone.Index(index_name)
            else:
                # New Pinecone client
                pc = pinecone.Pinecone(api_key=api_key)
                index = pc.Index(index_name)

            # Initialize embedding model
            embedding_model = None
            if SENTENCE_TRANSFORMERS_AVAILABLE:
                from sentence_transformers import SentenceTransformer
                embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

            connection = VectorDatabaseConnection(
                connection={'client': pinecone, 'index': index},
                connection_type='cloud',
                database_type='pinecone',
                embedding_model=embedding_model,
                embedding_dimension=384
            )

            logger.info(f"✅ Pinecone connection established: {index_name}")
            return connection

        except ImportError:
            logger.error("❌ pinecone-client not installed. Install with: pip install pinecone-client")
            raise
        except Exception as e:
            logger.error(f"❌ Pinecone connection error: {e}")
            raise

    def _create_weaviate_connection(self) -> VectorDatabaseConnection:
        """Create Weaviate connection"""
        try:
            if not WEAVIATE_AVAILABLE:
                raise ImportError("weaviate-client not available")

            url = os.environ.get('WEAVIATE_URL', 'http://localhost:8080')
            api_key = os.environ.get('WEAVIATE_API_KEY', '')

            auth_config = None
            if api_key:
                from weaviate.auth import AuthApiKey
                auth_config = AuthApiKey(api_key=api_key)

            client = WeaviateClient(url, auth_client_secret=auth_config)

            # Initialize embedding model
            embedding_model = None
            if SENTENCE_TRANSFORMERS_AVAILABLE:
                from sentence_transformers import SentenceTransformer
                embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

            connection = VectorDatabaseConnection(
                connection=client,
                connection_type='network',
                database_type='weaviate',
                embedding_model=embedding_model,
                embedding_dimension=384
            )

            logger.info(f"✅ Weaviate connection established: {url}")
            return connection

        except ImportError:
            logger.error("❌ weaviate-client not installed. Install with: pip install weaviate-client")
            raise
        except Exception as e:
            logger.error(f"❌ Weaviate connection error: {e}")
            raise

    def _create_qdrant_connection(self) -> VectorDatabaseConnection:
        """Create Qdrant connection"""
        try:
            if not QDRANT_AVAILABLE:
                raise ImportError("qdrant-client not available")

            url = os.environ.get('QDRANT_URL', 'http://localhost:6333')
            api_key = os.environ.get('QDRANT_API_KEY', '')

            client = QdrantClient(url=url, api_key=api_key if api_key else None)

            # Initialize embedding model
            embedding_model = None
            if SENTENCE_TRANSFORMERS_AVAILABLE:
                from sentence_transformers import SentenceTransformer
                embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

            connection = VectorDatabaseConnection(
                connection=client,
                connection_type='network',
                database_type='qdrant',
                embedding_model=embedding_model,
                embedding_dimension=384
            )

            logger.info(f"✅ Qdrant connection established: {url}")
            return connection

        except ImportError:
            logger.error("❌ qdrant-client not installed. Install with: pip install qdrant-client")
            raise
        except Exception as e:
            logger.error(f"❌ Qdrant connection error: {e}")
            raise

    def _create_chromadb_connection(self) -> VectorDatabaseConnection:
        """Create ChromaDB connection"""
        try:
            if not CHROMADB_AVAILABLE:
                raise ImportError("chromadb not available")

            persist_directory = os.environ.get('CHROMA_PERSIST_DIRECTORY', 'data/chroma_db')

            client = chromadb.PersistentClient(path=persist_directory)
            collection_name = os.environ.get('CHROMA_COLLECTION_NAME', 'validoai')
            collection = client.get_or_create_collection(name=collection_name)

            # Initialize embedding model
            embedding_model = None
            if SENTENCE_TRANSFORMERS_AVAILABLE:
                from sentence_transformers import SentenceTransformer
                embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

            connection = VectorDatabaseConnection(
                connection={'client': client, 'collection': collection},
                connection_type='file',
                database_type='chromadb',
                embedding_model=embedding_model,
                embedding_dimension=384
            )

            logger.info(f"✅ ChromaDB connection established: {persist_directory}")
            return connection

        except ImportError:
            logger.error("❌ chromadb not installed. Install with: pip install chromadb")
            raise
        except Exception as e:
            logger.error(f"❌ ChromaDB connection error: {e}")
            raise

    def _create_milvus_connection(self) -> VectorDatabaseConnection:
        """Create Milvus connection"""
        try:
            if not MILVUS_AVAILABLE:
                raise ImportError("pymilvus not available")

            host = os.environ.get('MILVUS_HOST', 'localhost')
            port = os.environ.get('MILVUS_PORT', '19530')

            from pymilvus import connections
            connections.connect("default", host=host, port=port)

            # Initialize embedding model
            embedding_model = None
            if SENTENCE_TRANSFORMERS_AVAILABLE:
                from sentence_transformers import SentenceTransformer
                embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

            connection = VectorDatabaseConnection(
                connection=connections,
                connection_type='network',
                database_type='milvus',
                embedding_model=embedding_model,
                embedding_dimension=768  # Milvus often uses larger embeddings
            )

            logger.info(f"✅ Milvus connection established: {host}:{port}")
            return connection

        except ImportError:
            logger.error("❌ pymilvus not installed. Install with: pip install pymilvus")
            raise
        except Exception as e:
            logger.error(f"❌ Milvus connection error: {e}")
            raise

    def _create_faiss_connection(self) -> VectorDatabaseConnection:
        """Create FAISS connection"""
        try:
            if not FAISS_AVAILABLE:
                raise ImportError("faiss not available")

            index_path = os.environ.get('FAISS_INDEX_PATH', 'data/faiss_index.idx')

            # Create or load FAISS index
            dimension = int(os.environ.get('FAISS_DIMENSION', '384'))

            if os.path.exists(index_path):
                index = faiss.read_index(index_path)
            else:
                # Create a new index
                index = faiss.IndexFlatL2(dimension)

            # Initialize embedding model
            embedding_model = None
            if SENTENCE_TRANSFORMERS_AVAILABLE:
                from sentence_transformers import SentenceTransformer
                embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

            connection = VectorDatabaseConnection(
                connection={'index': index, 'index_path': index_path},
                connection_type='file',
                database_type='faiss',
                embedding_model=embedding_model,
                embedding_dimension=dimension
            )

            logger.info(f"✅ FAISS connection established: {index_path}")
            return connection

        except ImportError:
            logger.error("❌ faiss not installed. Install with: pip install faiss-cpu")
            raise
        except Exception as e:
            logger.error(f"❌ FAISS connection error: {e}")
            raise

    def _validate_connection(self, connection: DatabaseConnection) -> bool:
        """Validate database connection is still alive"""
        try:
            if connection.database_type == 'sqlite':
                # SQLite connections don't need validation
                return True
            elif connection.database_type == 'postgresql':
                cursor = connection.connection.cursor()
                cursor.execute('SELECT 1')
                cursor.close()
                return True
            elif connection.database_type == 'mysql':
                cursor = connection.connection.cursor()
                cursor.execute('SELECT 1')
                cursor.close()
                return True
            return False
        except Exception as e:
            logger.warning(f"⚠️ Connection validation failed: {e}")
            return False

    def close_all_connections(self):
        """Close all database connections"""
        try:
            for connection in self._connections.values():
                connection.close()
            self._connections.clear()
            self._current_connection = None
            logger.info("✅ All database connections closed")
        except Exception as e:
            logger.error(f"❌ Error closing database connections: {e}")

    def get_current_connection(self) -> Optional[DatabaseConnection]:
        """Get current active connection"""
        return self._current_connection

# ============================================================================
# SAMPLE DATA MANAGER (Following Template Pattern)
# ============================================================================

class SampleDataManager:
    """Sample data manager following template pattern"""

    def __init__(self, db_path: str = "data/sqlite/sample.db"):
        self.db_path = db_path
        self._ensure_db_exists()

    def _ensure_db_exists(self):
        """Ensure the sample database exists"""
        db_file = Path(self.db_path)
        db_file.parent.mkdir(parents=True, exist_ok=True)

        if not db_file.exists():
            self._create_sample_db()

    def _create_sample_db(self):
        """Create sample database with demo data"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row

            # Create financial data table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS financial_data (
                    id INTEGER PRIMARY KEY,
                    date TEXT,
                    revenue REAL,
                    expenses REAL,
                    profit REAL,
                    category TEXT
                )
            """)

            # Create transactions table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY,
                    date TEXT,
                    amount REAL,
                    description TEXT,
                    category TEXT,
                    type TEXT
                )
            """)

            # Create customers table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS customers (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    email TEXT,
                    company TEXT,
                    revenue REAL,
                    status TEXT
                )
            """)

            # Generate sample data
            self._generate_sample_data(conn)

            conn.commit()
            conn.close()

            logger.info(f"✅ Sample database created: {self.db_path}")

        except Exception as e:
            logger.error(f"❌ Error creating sample database: {e}")
            raise

    def _generate_sample_data(self, conn):
        """Generate sample data following template pattern"""
        # Generate financial data for the last 12 months
        base_date = datetime.now() - timedelta(days=365)
        categories = ['Sales', 'Services', 'Consulting', 'Products']

        for i in range(365):
            date = (base_date + timedelta(days=i)).strftime('%Y-%m-%d')
            revenue = round(random.uniform(1000, 10000), 2)
            expenses = round(revenue * random.uniform(0.3, 0.7), 2)
            profit = revenue - expenses
            category = random.choice(categories)

            conn.execute(
                "INSERT INTO financial_data (date, revenue, expenses, profit, category) VALUES (?, ?, ?, ?, ?)",
                (date, revenue, expenses, profit, category)
            )

        # Generate transactions
        transaction_types = ['income', 'expense']
        descriptions = [
            'Client payment', 'Office supplies', 'Software license',
            'Consulting services', 'Equipment purchase', 'Marketing expenses'
        ]

        for i in range(100):
            date = (base_date + timedelta(days=random.randint(0, 365))).strftime('%Y-%m-%d')
            amount = round(random.uniform(100, 5000), 2)
            description = random.choice(descriptions)
            category = random.choice(categories)
            transaction_type = random.choice(transaction_types)

            conn.execute(
                "INSERT INTO transactions (date, amount, description, category, type) VALUES (?, ?, ?, ?, ?)",
                (date, amount, description, category, transaction_type)
            )

        # Generate customers
        companies = [
            'TechCorp', 'DataSys', 'InfoTech', 'GlobalSoft', 'NetWorks',
            'CloudTech', 'DataFlow', 'InfoSys', 'TechHub', 'DataCore'
        ]
        statuses = ['active', 'inactive', 'pending']

        for i in range(50):
            name = f"Customer {i+1}"
            email = f"customer{i+1}@example.com"
            company = random.choice(companies)
            revenue = round(random.uniform(5000, 50000), 2)
            status = random.choice(statuses)

            conn.execute(
                "INSERT INTO customers (name, email, company, revenue, status) VALUES (?, ?, ?, ?, ?)",
                (name, email, company, revenue, status)
            )

    def get_financial_data(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get financial data"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row

            cursor = conn.cursor()
            cursor.execute("SELECT * FROM financial_data ORDER BY date DESC LIMIT ?", (limit,))

            rows = cursor.fetchall()
            result = [dict(row) for row in rows]

            conn.close()
            return result

        except Exception as e:
            logger.error(f"❌ Error getting financial data: {e}")
            return []

    def get_transactions(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get transaction data"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row

            cursor = conn.cursor()
            cursor.execute("SELECT * FROM transactions ORDER BY date DESC LIMIT ?", (limit,))

            rows = cursor.fetchall()
            result = [dict(row) for row in rows]

            conn.close()
            return result

        except Exception as e:
            logger.error(f"❌ Error getting transactions: {e}")
            return []

    def get_customers(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get customer data"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row

            cursor = conn.cursor()
            cursor.execute("SELECT * FROM customers ORDER BY revenue DESC LIMIT ?", (limit,))

            rows = cursor.fetchall()
            result = [dict(row) for row in rows]

            conn.close()
            return result

        except Exception as e:
            logger.error(f"❌ Error getting customers: {e}")
            return []

    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get dashboard statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row

            cursor = conn.cursor()

            # Get total revenue
            cursor.execute("SELECT SUM(revenue) as total_revenue FROM financial_data")
            total_revenue = cursor.fetchone()['total_revenue'] or 0

            # Get total expenses
            cursor.execute("SELECT SUM(expenses) as total_expenses FROM financial_data")
            total_expenses = cursor.fetchone()['total_expenses'] or 0

            # Get total profit
            cursor.execute("SELECT SUM(profit) as total_profit FROM financial_data")
            total_profit = cursor.fetchone()['total_profit'] or 0

            # Get customer count
            cursor.execute("SELECT COUNT(*) as customer_count FROM customers")
            customer_count = cursor.fetchone()['customer_count']

            # Get transaction count
            cursor.execute("SELECT COUNT(*) as transaction_count FROM transactions")
            transaction_count = cursor.fetchone()['transaction_count']

            conn.close()

            return {
                'total_revenue': round(total_revenue, 2),
                'total_expenses': round(total_expenses, 2),
                'total_profit': round(total_profit, 2),
                'customer_count': customer_count,
                'transaction_count': transaction_count,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"❌ Error getting dashboard stats: {e}")
            return {
                'total_revenue': 0,
                'total_expenses': 0,
                'total_profit': 0,
                'customer_count': 0,
                'transaction_count': 0,
                'error': str(e)
            }

# ============================================================================
# UNIFIED DATABASE MANAGER (Following Facade Pattern)
# ============================================================================

class UnifiedDatabaseManager:
    """Unified database manager following facade pattern"""

    def __init__(self):
        self.connection_manager = DatabaseConnectionManager()
        self.sample_data_manager = SampleDataManager()
        self.vector_connections = {}  # Cache for vector database connections

    def execute_query(self, query: str, params: tuple = None, database_type: str = None) -> List[Dict[str, Any]]:
        """Execute SQL query following template pattern"""
        with self.connection_manager.get_connection(database_type) as conn:
            try:
                cursor = conn.get_cursor()

                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)

                if query.strip().upper().startswith('SELECT'):
                    rows = cursor.fetchall()
                    # Convert rows to dict format
                    if hasattr(rows, 'description'):
                        columns = [col[0] for col in cursor.description]
                        result = [dict(zip(columns, row)) for row in rows]
                    else:
                        result = [dict(row) for row in rows]
                else:
                    conn.commit()
                    result = []

                cursor.close()
                return result

            except Exception as e:
                logger.error(f"❌ Query execution error: {e}")
                conn.rollback()
                raise

    def get_sample_data(self, data_type: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get sample data following facade pattern"""
        try:
            if data_type == 'financial':
                return self.sample_data_manager.get_financial_data(limit)
            elif data_type == 'transactions':
                return self.sample_data_manager.get_transactions(limit)
            elif data_type == 'customers':
                return self.sample_data_manager.get_customers(limit)
            else:
                raise ValueError(f"Unknown data type: {data_type}")
        except Exception as e:
            logger.error(f"❌ Error getting sample data: {e}")
            return []

    def get_dashboard_statistics(self) -> Dict[str, Any]:
        """Get dashboard statistics"""
        return self.sample_data_manager.get_dashboard_stats()

    def initialize_database(self):
        """Initialize database with proper schema"""
        try:
            # Create main database tables through SQLAlchemy
            from app import db
            with db.app.app_context():
                db.create_all()
                logger.info("✅ Main database tables created")

            # Ensure sample data exists
            self.sample_data_manager._ensure_db_exists()
            logger.info("✅ Sample database initialized")

            return True

        except Exception as e:
            logger.error(f"❌ Database initialization error: {e}")
            return False

    def backup_database(self, backup_path: str = None):
        """Backup database"""
        try:
            if not backup_path:
                backup_path = f"backups/database_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            Path(backup_path).mkdir(parents=True, exist_ok=True)

            # Backup main database
            main_db_path = config_manager.get_config('database', {}).get('database')
            if os.path.exists(main_db_path):
                import shutil
                shutil.copy2(main_db_path, f"{backup_path}/main.db")

            # Backup sample database
            if os.path.exists(self.sample_data_manager.db_path):
                shutil.copy2(self.sample_data_manager.db_path, f"{backup_path}/sample.db")

            logger.info(f"✅ Database backup created: {backup_path}")
            return backup_path

        except Exception as e:
            logger.error(f"❌ Database backup error: {e}")
            return None

    def get_database_info(self) -> Dict[str, Any]:
        """Get database information"""
        return {
            'main_database': {
                'type': config_manager.get_config('database', {}).get('type'),
                'path': config_manager.get_config('database', {}).get('database'),
                'connection_string': config_manager.get_config('database', {}).get_connection_string()
            },
            'sample_database': {
                'path': self.sample_data_manager.db_path,
                'exists': os.path.exists(self.sample_data_manager.db_path)
            },
            'connection_manager': {
                'active_connections': len(self.connection_manager._connections),
                'current_connection': self.connection_manager._current_connection.connection_type if self.connection_manager._current_connection else None
            },
            'supported_databases': self.get_supported_databases(),
            'available_databases': self.get_available_databases()
        }

    def get_supported_databases(self) -> List[str]:
        """Get list of all supported database types"""
        return [
            'sqlite', 'postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch',
            'cassandra', 'neo4j', 'couchdb', 'couchbase', 'influxdb', 'clickhouse',
            'dynamodb', 'cosmosdb', 'firestore', 'arangodb', 'orientdb', 'mssql'
        ]

    def get_available_databases(self) -> Dict[str, bool]:
        """Get availability status of all database types"""
        return {
            # SQL Databases
            'sqlite': True, # SQLite is always available
            'postgresql': POSTGRESQL_AVAILABLE,
            'mysql': MYSQL_AVAILABLE,
            'mssql': MSSQL_AVAILABLE,

            # NoSQL Databases
            'mongodb': MONGODB_AVAILABLE,
            'redis': REDIS_AVAILABLE,
            'cassandra': CASSANDRA_AVAILABLE,
            'couchdb': COUCHDB_AVAILABLE,
            'couchbase': COUCHBASE_AVAILABLE,
            'dynamodb': DYNAMODB_AVAILABLE,
            'cosmosdb': COSMOSDB_AVAILABLE,
            'firestore': FIRESTORE_AVAILABLE,

            # Graph Databases
            'neo4j': NEO4J_AVAILABLE,
            'arangodb': ARANGODB_AVAILABLE,
            'orientdb': ORIENTDB_AVAILABLE,

            # Time Series Databases
            'influxdb': INFLUXDB_AVAILABLE,
            'clickhouse': CLICKHOUSE_AVAILABLE,

            # Search Engines
            'elasticsearch': ELASTICSEARCH_AVAILABLE,

            # Vector Databases
            'pinecone': PINECONE_AVAILABLE,
            'weaviate': WEAVIATE_AVAILABLE,
            'qdrant': QDRANT_AVAILABLE,
            'chromadb': CHROMADB_AVAILABLE,
            'milvus': MILVUS_AVAILABLE,
            'faiss': FAISS_AVAILABLE
        }

    def get_database_requirements(self) -> Dict[str, List[str]]:
        """Get installation requirements for each database type"""
        return {
            'postgresql': ['psycopg2-binary'],
            'mysql': ['pymysql'],
            'mongodb': ['pymongo'],
            'redis': ['redis'],
            'elasticsearch': ['elasticsearch'],
            'cassandra': ['cassandra-driver'],
            'neo4j': ['neo4j'],
            'couchdb': ['couchdb'],
            'couchbase': ['couchbase'],
            'influxdb': ['influxdb-client'],
            'clickhouse': ['clickhouse-driver'],
            'dynamodb': ['boto3'],
            'cosmosdb': ['azure-cosmos'],
            'firestore': ['firebase-admin'],
            'arangodb': ['python-arango'],
            'orientdb': ['pyorient'],
            'mssql': ['pyodbc']
        }

    def test_database_connection(self, database_type: str = None) -> Dict[str, Any]:
        """Test database connection"""
        db_type = database_type or config_manager.get_config('database', {}).get('type')

        try:
            with self.connection_manager.get_connection(db_type) as conn:
                result = {
                    'database_type': db_type,
                    'connection_type': conn.connection_type,
                    'status': 'success',
                    'timestamp': datetime.now().isoformat()
                }

                # Test basic operation based on database type
                if db_type == 'redis':
                    conn.connection.set('test_key', 'test_value')
                    test_value = conn.connection.get('test_key')
                    result['test_result'] = test_value == b'test_value'
                elif db_type == 'mongodb':
                    test_collection = conn.connection.validoai.test_collection
                    test_collection.insert_one({'test': 'data'})
                    count = test_collection.count_documents({'test': 'data'})
                    result['test_result'] = count > 0
                else:
                    # For SQL databases, try a simple query
                    cursor = conn.get_cursor()
                    if db_type == 'sqlite':
                        cursor.execute("SELECT 1")
                        result['test_result'] = True
                    else:
                        cursor.execute("SELECT 1 as test")
                        row = cursor.fetchone()
                        result['test_result'] = row is not None
                    cursor.close()

                return result

        except Exception as e:
            return {
                'database_type': db_type,
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def get_database_stats(self) -> Dict[str, Any]:
        """Get comprehensive database statistics"""
        stats = {
            'timestamp': datetime.now().isoformat(),
            'supported_databases': len(self.get_supported_databases()),
            'available_databases': sum(self.get_available_databases().values()),
            'active_connections': len(self.connection_manager._connections),
            'current_database': config_manager.get_config('database', {}).get('type'),
            'sample_data_available': os.path.exists(self.sample_data_manager.db_path)
        }

        # Test current database connection
        if config_manager.get_config('database', {}).get('type'):
            connection_test = self.test_database_connection(config_manager.get_config('database', {}).get('type'))
            stats['current_connection_status'] = connection_test.get('status', 'unknown')
            stats['current_connection_test'] = connection_test.get('test_result', False)

        return stats

# ============================================================================
# GLOBAL INSTANCES
# ============================================================================

# Create global instances
database_manager = UnifiedDatabaseManager()
connection_manager = DatabaseConnectionManager()
sample_data_manager = SampleDataManager()

# Export commonly used functions for backward compatibility
def get_db_connection():
    """Get database connection (backward compatibility)"""
    return connection_manager.get_connection()

def execute_query(query: str, params: tuple = None):
    """Execute query (backward compatibility)"""
    return database_manager.execute_query(query, params)

def get_sample_data(data_type: str, limit: int = 100):
    """Get sample data (backward compatibility)"""
    return database_manager.get_sample_data(data_type, limit)

# Create database configuration object
class DatabaseConfig:
    """Database configuration object"""
    def __init__(self):
        self.type = os.getenv('DATABASE_TYPE', 'sqlite')
        self.database = os.getenv('SQLITE_PATH', 'data/sqlite/app.db') if self.type == 'sqlite' else os.getenv('POSTGRES_NAME', 'ai_valido_online')
        self.host = os.getenv('POSTGRES_HOST', 'localhost')
        self.port = int(os.getenv('POSTGRES_PORT', '5432'))
        self.username = os.getenv('POSTGRES_USER', 'postgres')
        self.password = os.getenv('POSTGRES_PASSWORD', 'postgres')

# Create global database config instance
database_config = DatabaseConfig()

logger.info("✅ Unified database system initialized successfully")
logger.info(f"📊 Database type: {database_config.type}")
logger.info(f"📁 Sample database: {sample_data_manager.db_path}")
