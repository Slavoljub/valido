"""
Database Controller - Database-Specific Features
==============================================
This controller demonstrates how to organize imports for specific database features.
It shows best practices for importing database-specific dependencies only when needed.
"""

import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from flask import jsonify, request, current_app
from flask_login import login_required, current_user

logger = logging.getLogger(__name__)

class DatabaseController:
    """Controller for database-specific operations with lazy loading."""

    def __init__(self):
        """Initialize with lazy-loaded database features."""
        self._databases = {}
        self._initialize_databases()

    def _initialize_databases(self):
        """Initialize database connections only when needed."""
        # This will be populated when specific databases are accessed
        pass

    def _get_postgresql_connection(self):
        """Get PostgreSQL connection with lazy loading."""
        if 'postgresql' not in self._databases:
            try:
                import psycopg2
                from psycopg2.extras import RealDictCursor
                
                # Get connection details from environment or config
                host = current_app.config.get('POSTGRESQL_HOST', 'localhost')
                port = current_app.config.get('POSTGRESQL_PORT', 5432)
                database = current_app.config.get('POSTGRESQL_DATABASE', 'ai_valido_online')
                user = current_app.config.get('POSTGRESQL_USER', 'postgres')
                password = current_app.config.get('POSTGRESQL_PASSWORD', 'postgres')
                
                conn = psycopg2.connect(
                    host=host,
                    port=port,
                    database=database,
                    user=user,
                    password=password,
                    cursor_factory=RealDictCursor
                )
                
                self._databases['postgresql'] = {
                    'connection': conn,
                    'driver': psycopg2,
                    'version': psycopg2.__version__
                }
                logger.info("✅ PostgreSQL connection established")
                
            except ImportError:
                logger.error("❌ PostgreSQL driver (psycopg2) not available")
                raise ImportError("PostgreSQL driver not available. Install with: pip install psycopg2")
            except Exception as e:
                logger.error(f"❌ PostgreSQL connection failed: {e}")
                raise
        
        return self._databases['postgresql']['connection']

    def _get_mongodb_connection(self):
        """Get MongoDB connection with lazy loading."""
        if 'mongodb' not in self._databases:
            try:
                import pymongo
                from pymongo import MongoClient
                
                # Get connection details from environment or config
                host = current_app.config.get('MONGODB_HOST', 'localhost')
                port = current_app.config.get('MONGODB_PORT', 27017)
                database = current_app.config.get('MONGODB_DATABASE', 'ai_valido_online')
                
                client = MongoClient(f"mongodb://{host}:{port}/")
                db = client[database]
                
                self._databases['mongodb'] = {
                    'client': client,
                    'database': db,
                    'driver': pymongo,
                    'version': pymongo.__version__
                }
                logger.info("✅ MongoDB connection established")
                
            except ImportError:
                logger.error("❌ MongoDB driver (pymongo) not available")
                raise ImportError("MongoDB driver not available. Install with: pip install pymongo")
            except Exception as e:
                logger.error(f"❌ MongoDB connection failed: {e}")
                raise
        
        return self._databases['mongodb']['database']

    def _get_redis_connection(self):
        """Get Redis connection with lazy loading."""
        if 'redis' not in self._databases:
            try:
                import redis
                
                # Get connection details from environment or config
                host = current_app.config.get('REDIS_HOST', 'localhost')
                port = current_app.config.get('REDIS_PORT', 6379)
                db = current_app.config.get('REDIS_DB', 0)
                
                r = redis.Redis(host=host, port=port, db=db, decode_responses=True)
                
                # Test connection
                r.ping()
                
                self._databases['redis'] = {
                    'connection': r,
                    'driver': redis,
                    'version': redis.__version__
                }
                logger.info("✅ Redis connection established")
                
            except ImportError:
                logger.error("❌ Redis driver not available")
                raise ImportError("Redis driver not available. Install with: pip install redis")
            except Exception as e:
                logger.error(f"❌ Redis connection failed: {e}")
                raise
        
        return self._databases['redis']['connection']

    def _get_vector_db_connection(self, db_type: str = 'pinecone'):
        """Get vector database connection with lazy loading."""
        if f'vector_{db_type}' not in self._databases:
            try:
                if db_type == 'pinecone':
                    import pinecone
                    
                    api_key = current_app.config.get('PINECONE_API_KEY')
                    environment = current_app.config.get('PINECONE_ENVIRONMENT', 'us-west1-gcp')
                    
                    if not api_key:
                        raise ValueError("Pinecone API key not configured")
                    
                    pinecone.init(api_key=api_key, environment=environment)
                    index_name = current_app.config.get('PINECONE_INDEX', 'valido-ai-index')
                    
                    # Try to get existing index or create new one
                    try:
                        index = pinecone.Index(index_name)
                    except:
                        # Create index if it doesn't exist
                        dimension = current_app.config.get('PINECONE_DIMENSION', 384)
                        index = pinecone.create_index(
                            name=index_name,
                            dimension=dimension,
                            metric='cosine'
                        )
                    
                    self._databases[f'vector_{db_type}'] = {
                        'index': index,
                        'driver': pinecone,
                        'type': 'pinecone'
                    }
                    logger.info("✅ Pinecone vector database connection established")
                
                elif db_type == 'chromadb':
                    import chromadb
                    
                    client = chromadb.Client()
                    collection_name = current_app.config.get('CHROMADB_COLLECTION', 'valido-ai-collection')
                    
                    # Try to get existing collection or create new one
                    try:
                        collection = client.get_collection(collection_name)
                    except:
                        collection = client.create_collection(collection_name)
                    
                    self._databases[f'vector_{db_type}'] = {
                        'collection': collection,
                        'client': client,
                        'driver': chromadb,
                        'type': 'chromadb'
                    }
                    logger.info("✅ ChromaDB vector database connection established")
                
                else:
                    raise ValueError(f"Unsupported vector database type: {db_type}")
                
            except ImportError as e:
                logger.error(f"❌ Vector database driver not available: {e}")
                raise ImportError(f"Vector database driver not available for {db_type}")
            except Exception as e:
                logger.error(f"❌ Vector database connection failed: {e}")
                raise
        
        return self._databases[f'vector_{db_type}']

    @staticmethod
    def test_postgresql():
        """Test PostgreSQL connection and return status."""
        try:
            controller = DatabaseController()
            conn = controller._get_postgresql_connection()
            
            with conn.cursor() as cursor:
                cursor.execute("SELECT version();")
                version = cursor.fetchone()
            
            return jsonify({
                'status': 'success',
                'database': 'postgresql',
                'version': version['version'] if version else 'Unknown',
                'driver_version': controller._databases['postgresql']['version'],
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            return jsonify({
                'status': 'error',
                'database': 'postgresql',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }), 500

    @staticmethod
    def test_mongodb():
        """Test MongoDB connection and return status."""
        try:
            controller = DatabaseController()
            db = controller._get_mongodb_connection()
            
            # Test with a simple operation
            result = db.command('ping')
            
            return jsonify({
                'status': 'success',
                'database': 'mongodb',
                'ping': result,
                'driver_version': controller._databases['mongodb']['version'],
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            return jsonify({
                'status': 'error',
                'database': 'mongodb',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }), 500

    @staticmethod
    def test_redis():
        """Test Redis connection and return status."""
        try:
            controller = DatabaseController()
            r = controller._get_redis_connection()
            
            # Test with ping
            ping_result = r.ping()
            
            return jsonify({
                'status': 'success',
                'database': 'redis',
                'ping': ping_result,
                'driver_version': controller._databases['redis']['version'],
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            return jsonify({
                'status': 'error',
                'database': 'redis',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }), 500

    @staticmethod
    def test_vector_db(db_type: str = 'pinecone'):
        """Test vector database connection and return status."""
        try:
            controller = DatabaseController()
            vector_db = controller._get_vector_db_connection(db_type)
            
            if db_type == 'pinecone':
                # Test with a simple query
                index = vector_db['index']
                stats = index.describe_index_stats()
                
                return jsonify({
                    'status': 'success',
                    'database': f'vector_{db_type}',
                    'index_stats': stats,
                    'type': 'pinecone',
                    'timestamp': datetime.now().isoformat()
                })
            
            elif db_type == 'chromadb':
                # Test with a simple operation
                collection = vector_db['collection']
                count = collection.count()
                
                return jsonify({
                    'status': 'success',
                    'database': f'vector_{db_type}',
                    'collection_count': count,
                    'type': 'chromadb',
                    'timestamp': datetime.now().isoformat()
                })
            
        except Exception as e:
            return jsonify({
                'status': 'error',
                'database': f'vector_{db_type}',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }), 500

    @staticmethod
    def get_database_status():
        """Get status of all available databases."""
        controller = DatabaseController()
        
        status = {
            'databases': {},
            'timestamp': datetime.now().isoformat()
        }
        
        # Test each database type
        databases_to_test = [
            ('postgresql', controller._test_postgresql_internal),
            ('mongodb', controller._test_mongodb_internal),
            ('redis', controller._test_redis_internal),
            ('vector_pinecone', lambda: controller._test_vector_db_internal('pinecone')),
            ('vector_chromadb', lambda: controller._test_vector_db_internal('chromadb'))
        ]
        
        for db_name, test_func in databases_to_test:
            try:
                result = test_func()
                status['databases'][db_name] = {
                    'available': True,
                    'status': 'connected',
                    'details': result
                }
            except ImportError as e:
                status['databases'][db_name] = {
                    'available': False,
                    'status': 'driver_not_available',
                    'error': str(e)
                }
            except Exception as e:
                status['databases'][db_name] = {
                    'available': False,
                    'status': 'connection_failed',
                    'error': str(e)
                }
        
        return jsonify(status)

    def _test_postgresql_internal(self):
        """Internal PostgreSQL test."""
        conn = self._get_postgresql_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT version();")
            return cursor.fetchone()

    def _test_mongodb_internal(self):
        """Internal MongoDB test."""
        db = self._get_mongodb_connection()
        return db.command('ping')

    def _test_redis_internal(self):
        """Internal Redis test."""
        r = self._get_redis_connection()
        return r.ping()

    def _test_vector_db_internal(self, db_type: str):
        """Internal vector database test."""
        vector_db = self._get_vector_db_connection(db_type)
        if db_type == 'pinecone':
            return vector_db['index'].describe_index_stats()
        elif db_type == 'chromadb':
            return {'count': vector_db['collection'].count()}

    def close_connections(self):
        """Close all database connections."""
        for db_name, db_info in self._databases.items():
            try:
                if 'connection' in db_info:
                    db_info['connection'].close()
                elif 'client' in db_info:
                    db_info['client'].close()
                logger.info(f"✅ Closed connection to {db_name}")
            except Exception as e:
                logger.error(f"❌ Error closing {db_name} connection: {e}")
        
        self._databases.clear()
