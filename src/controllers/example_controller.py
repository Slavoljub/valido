"""
Example Controller - Comprehensive Feature Demonstration
Demonstrates all available features, imports, and integrations
"""
import os
import sys
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
import traceback

from flask import render_template, jsonify, request, current_app, g
from werkzeug.exceptions import HTTPException

logger = logging.getLogger(__name__)

@dataclass
class FeatureDemo:
    """Feature demonstration data"""
    name: str
    category: str
    description: str
    code_snippet: str
    status: str  # 'available', 'unavailable', 'error'
    message: str
    dependencies: List[str]

@dataclass
class IntegrationDemo:
    """Integration demonstration data"""
    name: str
    type: str  # 'database', 'ai_ml', 'api', 'utility'
    description: str
    status: str
    details: Dict[str, Any]

class ExampleController:
    """Comprehensive example controller demonstrating all available features"""
    
    def __init__(self):
        self.features = {}
        self.integrations = {}
        self._initialize_features()
    
    def _initialize_features(self):
        """Initialize and check all available features"""
        logger.info("Initializing comprehensive feature demonstrations...")
        
        # Database Features
        self._check_database_features()
        
        # AI/ML Features
        self._check_ai_ml_features()
        
        # API Features
        self._check_api_features()
        
        # Utility Features
        self._check_utility_features()
        
        # Framework Features
        self._check_framework_features()
        
        logger.info(f"Feature initialization complete. {len(self.features)} features available.")
    
    def _check_database_features(self):
        """Check database-related features"""
        features = [
            {
                'name': 'PostgreSQL Connection',
                'category': 'database',
                'description': 'PostgreSQL database connection and operations',
                'code_snippet': '''
from src.database.database_manager import DatabaseManager
db = DatabaseManager()
connection = db.get_postgresql_connection()
''',
                'dependencies': ['psycopg2', 'sqlalchemy']
            },
            {
                'name': 'MongoDB Integration',
                'category': 'database',
                'description': 'MongoDB NoSQL database operations',
                'code_snippet': '''
from pymongo import MongoClient
client = MongoClient('mongodb://localhost:27017/')
db = client['valido_ai']
''',
                'dependencies': ['pymongo']
            },
            {
                'name': 'Redis Caching',
                'category': 'database',
                'description': 'Redis cache operations',
                'code_snippet': '''
import redis
r = redis.Redis(host='localhost', port=6379, db=0)
r.set('key', 'value')
''',
                'dependencies': ['redis']
            },
            {
                'name': 'SQLite Operations',
                'category': 'database',
                'description': 'SQLite database operations',
                'code_snippet': '''
import sqlite3
conn = sqlite3.connect('data/sqlite/sample.db')
cursor = conn.cursor()
''',
                'dependencies': ['sqlite3']
            }
        ]
        
        for feature in features:
            self.features[feature['name']] = self._test_feature_availability(feature)
    
    def _check_ai_ml_features(self):
        """Check AI/ML-related features"""
        features = [
            {
                'name': 'TensorFlow Models',
                'category': 'ai_ml',
                'description': 'TensorFlow model loading and inference',
                'code_snippet': '''
import tensorflow as tf
model = tf.keras.models.load_model('models/tensorflow_model.h5')
predictions = model.predict(data)
''',
                'dependencies': ['tensorflow']
            },
            {
                'name': 'PyTorch Models',
                'category': 'ai_ml',
                'description': 'PyTorch model operations',
                'code_snippet': '''
import torch
import torch.nn as nn
model = torch.load('models/pytorch_model.pth')
model.eval()
''',
                'dependencies': ['torch']
            },
            {
                'name': 'OpenAI Integration',
                'category': 'ai_ml',
                'description': 'OpenAI API integration',
                'code_snippet': '''
import openai
openai.api_key = 'your-api-key'
response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello!"}]
)
''',
                'dependencies': ['openai']
            },
            {
                'name': 'Sentence Transformers',
                'category': 'ai_ml',
                'description': 'Sentence embedding and similarity',
                'code_snippet': '''
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
embeddings = model.encode(['Hello world', 'How are you?'])
''',
                'dependencies': ['sentence-transformers']
            },
            {
                'name': 'Scikit-learn Models',
                'category': 'ai_ml',
                'description': 'Scikit-learn machine learning',
                'code_snippet': '''
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
clf = RandomForestClassifier(n_estimators=100)
clf.fit(X_train, y_train)
''',
                'dependencies': ['scikit-learn']
            }
        ]
        
        for feature in features:
            self.features[feature['name']] = self._test_feature_availability(feature)
    
    def _check_api_features(self):
        """Check API-related features"""
        features = [
            {
                'name': 'REST API Endpoints',
                'category': 'api',
                'description': 'Flask REST API endpoints',
                'code_snippet': '''
@app.route('/api/data', methods=['GET'])
def get_data():
    return jsonify({'data': 'example'})
''',
                'dependencies': ['flask']
            },
            {
                'name': 'WebSocket Support',
                'category': 'api',
                'description': 'Real-time WebSocket communication',
                'code_snippet': '''
from flask_socketio import SocketIO, emit
socketio = SocketIO(app)
@socketio.on('message')
def handle_message(data):
    emit('response', {'data': data})
''',
                'dependencies': ['flask-socketio']
            },
            {
                'name': 'GraphQL Support',
                'category': 'api',
                'description': 'GraphQL API endpoints',
                'code_snippet': '''
from flask_graphql import GraphQLView
from graphene import Schema
app.add_url_rule('/graphql', view_func=GraphQLView.as_view('graphql', schema=schema))
''',
                'dependencies': ['flask-graphql', 'graphene']
            }
        ]
        
        for feature in features:
            self.features[feature['name']] = self._test_feature_availability(feature)
    
    def _check_utility_features(self):
        """Check utility features"""
        features = [
            {
                'name': 'File Upload',
                'category': 'utility',
                'description': 'Secure file upload handling',
                'code_snippet': '''
from werkzeug.utils import secure_filename
import os
file = request.files['file']
filename = secure_filename(file.filename)
file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
''',
                'dependencies': ['werkzeug']
            },
            {
                'name': 'Email Sending',
                'category': 'utility',
                'description': 'Email functionality',
                'code_snippet': '''
from flask_mail import Mail, Message
mail = Mail(app)
msg = Message('Subject', sender='from@example.com', recipients=['to@example.com'])
mail.send(msg)
''',
                'dependencies': ['flask-mail']
            },
            {
                'name': 'Background Tasks',
                'category': 'utility',
                'description': 'Celery background task processing',
                'code_snippet': '''
from celery import Celery
celery = Celery('tasks', broker='redis://localhost:6379/0')
@celery.task
def background_task():
    return 'Task completed'
''',
                'dependencies': ['celery']
            },
            {
                'name': 'Caching',
                'category': 'utility',
                'description': 'Flask-Caching integration',
                'code_snippet': '''
from flask_caching import Cache
cache = Cache(app, config={'CACHE_TYPE': 'redis'})
@cache.memoize(timeout=300)
def expensive_function():
    return 'cached result'
''',
                'dependencies': ['flask-caching']
            }
        ]
        
        for feature in features:
            self.features[feature['name']] = self._test_feature_availability(feature)
    
    def _check_framework_features(self):
        """Check framework-specific features"""
        features = [
            {
                'name': 'User Authentication',
                'category': 'framework',
                'description': 'Flask-Login authentication',
                'code_snippet': '''
from flask_login import login_user, logout_user, login_required
@login_required
def protected_route():
    return 'Protected content'
''',
                'dependencies': ['flask-login']
            },
            {
                'name': 'Database Migrations',
                'category': 'framework',
                'description': 'Flask-Migrate database migrations',
                'code_snippet': '''
from flask_migrate import Migrate
migrate = Migrate(app, db)
# Run: flask db migrate -m "Initial migration"
''',
                'dependencies': ['flask-migrate']
            },
            {
                'name': 'CORS Support',
                'category': 'framework',
                'description': 'Cross-Origin Resource Sharing',
                'code_snippet': '''
from flask_cors import CORS
CORS(app, resources={r"/api/*": {"origins": "*"}})
''',
                'dependencies': ['flask-cors']
            },
            {
                'name': 'Session Management',
                'category': 'framework',
                'description': 'Flask session handling',
                'code_snippet': '''
from flask_session import Session
Session(app)
session['user_id'] = user.id
''',
                'dependencies': ['flask-session']
            }
        ]
        
        for feature in features:
            self.features[feature['name']] = self._test_feature_availability(feature)
    
    def _test_feature_availability(self, feature: Dict[str, Any]) -> FeatureDemo:
        """Test if a feature is available"""
        try:
            # Check dependencies
            missing_deps = []
            for dep in feature['dependencies']:
                try:
                    __import__(dep)
                except ImportError:
                    missing_deps.append(dep)
            
            if missing_deps:
                return FeatureDemo(
                    name=feature['name'],
                    category=feature['category'],
                    description=feature['description'],
                    code_snippet=feature['code_snippet'],
                    status='unavailable',
                    message=f"Missing dependencies: {', '.join(missing_deps)}",
                    dependencies=feature['dependencies']
                )
            
            # Test the feature
            test_result = self._test_specific_feature(feature['name'])
            
            return FeatureDemo(
                name=feature['name'],
                category=feature['category'],
                description=feature['description'],
                code_snippet=feature['code_snippet'],
                status='available' if test_result['success'] else 'error',
                message=test_result['message'],
                dependencies=feature['dependencies']
            )
            
        except Exception as e:
            return FeatureDemo(
                name=feature['name'],
                category=feature['category'],
                description=feature['description'],
                code_snippet=feature['code_snippet'],
                status='error',
                message=f"Error testing feature: {str(e)}",
                dependencies=feature['dependencies']
            )
    
    def _test_specific_feature(self, feature_name: str) -> Dict[str, Any]:
        """Test specific feature functionality"""
        try:
            if 'PostgreSQL' in feature_name:
                # Test PostgreSQL connection
                from src.database.database_manager import DatabaseManager
                db_manager = DatabaseManager()
                connection = db_manager.get_postgresql_connection()
                if connection:
                    return {'success': True, 'message': 'PostgreSQL connection successful'}
                else:
                    return {'success': False, 'message': 'PostgreSQL connection failed'}
            
            elif 'MongoDB' in feature_name:
                # Test MongoDB connection
                try:
                    import pymongo
                    client = pymongo.MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=1000)
                    client.server_info()
                    return {'success': True, 'message': 'MongoDB connection successful'}
                except Exception as e:
                    return {'success': False, 'message': f'MongoDB connection failed: {str(e)}'}
            
            elif 'Redis' in feature_name:
                # Test Redis connection
                try:
                    import redis
                    r = redis.Redis(host='localhost', port=6379, db=0, socket_connect_timeout=1)
                    r.ping()
                    return {'success': True, 'message': 'Redis connection successful'}
                except Exception as e:
                    return {'success': False, 'message': f'Redis connection failed: {str(e)}'}
            
            elif 'TensorFlow' in feature_name:
                # Test TensorFlow
                try:
                    import tensorflow as tf
                    version = tf.__version__
                    return {'success': True, 'message': f'TensorFlow {version} available'}
                except Exception as e:
                    return {'success': False, 'message': f'TensorFlow not available: {str(e)}'}
            
            elif 'PyTorch' in feature_name:
                # Test PyTorch
                try:
                    import torch
                    version = torch.__version__
                    return {'success': True, 'message': f'PyTorch {version} available'}
                except Exception as e:
                    return {'success': False, 'message': f'PyTorch not available: {str(e)}'}
            
            elif 'OpenAI' in feature_name:
                # Test OpenAI
                try:
                    import openai
                    return {'success': True, 'message': 'OpenAI library available'}
                except Exception as e:
                    return {'success': False, 'message': f'OpenAI not available: {str(e)}'}
            
            else:
                # Generic test - just check if dependencies are importable
                return {'success': True, 'message': 'Feature dependencies available'}
                
        except Exception as e:
            return {'success': False, 'message': f'Test failed: {str(e)}'}
    
    def show(self):
        """Show comprehensive feature demonstration"""
        try:
            # Generate demo data
            demo_data = self._generate_demo_data()
            
            # Get feature summary
            feature_summary = self.get_feature_summary()
            
            return render_template('example/index.html',
                                 features=self.features,
                                 demo_data=demo_data,
                                 feature_summary=feature_summary,
                                 integrations=self.integrations)
        except Exception as e:
            logger.error(f"Error in example controller show: {e}")
            return render_template('errors/error.html',
                                 error_code=500,
                                 error_title="Example Controller Error",
                                 error_message="Failed to load example demonstrations.",
                                 stack_trace=traceback.format_exc()), 500
    
    def _generate_demo_data(self) -> Dict[str, Any]:
        """Generate comprehensive demo data"""
        return {
            'timestamp': datetime.now().isoformat(),
            'features_count': len(self.features),
            'available_features': len([f for f in self.features.values() if f.status == 'available']),
            'unavailable_features': len([f for f in self.features.values() if f.status == 'unavailable']),
            'error_features': len([f for f in self.features.values() if f.status == 'error']),
            'categories': {
                'database': len([f for f in self.features.values() if f.category == 'database']),
                'ai_ml': len([f for f in self.features.values() if f.category == 'ai_ml']),
                'api': len([f for f in self.features.values() if f.category == 'api']),
                'utility': len([f for f in self.features.values() if f.category == 'utility']),
                'framework': len([f for f in self.features.values() if f.category == 'framework'])
            }
        }
    
    def get_feature_summary(self) -> Dict[str, Any]:
        """Get summary of all features"""
        categories = {}
        for feature in self.features.values():
            if feature.category not in categories:
                categories[feature.category] = {'total': 0, 'available': 0, 'unavailable': 0, 'error': 0}
            
            categories[feature.category]['total'] += 1
            categories[feature.category][feature.status] += 1
        
        return {
            'total_features': len(self.features),
            'categories': categories,
            'overall_status': {
                'available': len([f for f in self.features.values() if f.status == 'available']),
                'unavailable': len([f for f in self.features.values() if f.status == 'unavailable']),
                'error': len([f for f in self.features.values() if f.status == 'error'])
            }
        }
    
    @staticmethod
    def api_demo():
        """API endpoint for feature demonstrations"""
        try:
            controller = ExampleController()
            return jsonify({
                'status': 'success',
                'data': {
                    'features': {name: asdict(feature) for name, feature in controller.features.items()},
                    'summary': controller.get_feature_summary(),
                    'timestamp': datetime.now().isoformat()
                }
            })
        except Exception as e:
            logger.error(f"Error in API demo: {e}")
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500
    
    @staticmethod
    def test_feature(feature_name: str):
        """Test a specific feature via API"""
        try:
            controller = ExampleController()
            
            if feature_name not in controller.features:
                return jsonify({
                    'status': 'error',
                    'message': f'Feature "{feature_name}" not found'
                }), 404
            
            feature = controller.features[feature_name]
            test_result = controller._test_specific_feature(feature_name)
            
            return jsonify({
                'status': 'success',
                'feature': asdict(feature),
                'test_result': test_result,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Error testing feature {feature_name}: {e}")
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500
    
    @staticmethod
    def get_available_features():
        """Get list of available features"""
        try:
            controller = ExampleController()
            available_features = [
                {
                    'name': name,
                    'category': feature.category,
                    'description': feature.description,
                    'status': feature.status
                }
                for name, feature in controller.features.items()
                if feature.status == 'available'
            ]
            
            return jsonify({
                'status': 'success',
                'features': available_features,
                'count': len(available_features),
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Error getting available features: {e}")
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500
