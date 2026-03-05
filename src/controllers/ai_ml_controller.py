"""
AI/ML Controller - AI/ML-Specific Features
========================================
This controller demonstrates how to organize imports for AI/ML features.
It shows best practices for importing AI/ML dependencies only when needed.
"""

import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from flask import jsonify, request, current_app
from flask_login import login_required, current_user

logger = logging.getLogger(__name__)

class AIMLController:
    """Controller for AI/ML-specific operations with lazy loading."""

    def __init__(self):
        """Initialize with lazy-loaded AI/ML features."""
        self._ai_models = {}
        self._initialize_models()

    def _initialize_models(self):
        """Initialize AI/ML models only when needed."""
        # This will be populated when specific models are accessed
        pass

    def _get_tensorflow_model(self, model_type: str = 'simple'):
        """Get TensorFlow model with lazy loading."""
        if f'tensorflow_{model_type}' not in self._ai_models:
            try:
                import tensorflow as tf
                
                if model_type == 'simple':
                    model = tf.keras.Sequential([
                        tf.keras.layers.Dense(128, activation='relu', input_shape=(10,)),
                        tf.keras.layers.Dropout(0.2),
                        tf.keras.layers.Dense(64, activation='relu'),
                        tf.keras.layers.Dense(1, activation='sigmoid')
                    ])
                    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
                
                elif model_type == 'cnn':
                    model = tf.keras.Sequential([
                        tf.keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=(28, 28, 1)),
                        tf.keras.layers.MaxPooling2D((2, 2)),
                        tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
                        tf.keras.layers.MaxPooling2D((2, 2)),
                        tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
                        tf.keras.layers.Flatten(),
                        tf.keras.layers.Dense(64, activation='relu'),
                        tf.keras.layers.Dense(10, activation='softmax')
                    ])
                    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
                
                else:
                    raise ValueError(f"Unsupported TensorFlow model type: {model_type}")
                
                self._ai_models[f'tensorflow_{model_type}'] = {
                    'model': model,
                    'framework': tf,
                    'version': tf.__version__,
                    'type': 'tensorflow'
                }
                logger.info(f"✅ TensorFlow {model_type} model loaded")
                
            except ImportError:
                logger.error("❌ TensorFlow not available")
                raise ImportError("TensorFlow not available. Install with: pip install tensorflow")
            except Exception as e:
                logger.error(f"❌ TensorFlow model loading failed: {e}")
                raise
        
        return self._ai_models[f'tensorflow_{model_type}']['model']

    def _get_pytorch_model(self, model_type: str = 'simple'):
        """Get PyTorch model with lazy loading."""
        if f'pytorch_{model_type}' not in self._ai_models:
            try:
                import torch
                import torch.nn as nn
                
                if model_type == 'simple':
                    class SimpleModel(nn.Module):
                        def __init__(self):
                            super(SimpleModel, self).__init__()
                            self.fc1 = nn.Linear(10, 128)
                            self.fc2 = nn.Linear(128, 64)
                            self.fc3 = nn.Linear(64, 1)
                            self.relu = nn.ReLU()
                            self.sigmoid = nn.Sigmoid()
                        
                        def forward(self, x):
                            x = self.relu(self.fc1(x))
                            x = self.relu(self.fc2(x))
                            x = self.sigmoid(self.fc3(x))
                            return x
                    
                    model = SimpleModel()
                
                elif model_type == 'cnn':
                    class CNNModel(nn.Module):
                        def __init__(self):
                            super(CNNModel, self).__init__()
                            self.conv1 = nn.Conv2d(1, 32, 3)
                            self.conv2 = nn.Conv2d(32, 64, 3)
                            self.pool = nn.MaxPool2d(2, 2)
                            self.fc1 = nn.Linear(64 * 5 * 5, 128)
                            self.fc2 = nn.Linear(128, 10)
                            self.relu = nn.ReLU()
                        
                        def forward(self, x):
                            x = self.pool(self.relu(self.conv1(x)))
                            x = self.pool(self.relu(self.conv2(x)))
                            x = x.view(-1, 64 * 5 * 5)
                            x = self.relu(self.fc1(x))
                            x = self.fc2(x)
                            return x
                    
                    model = CNNModel()
                
                else:
                    raise ValueError(f"Unsupported PyTorch model type: {model_type}")
                
                self._ai_models[f'pytorch_{model_type}'] = {
                    'model': model,
                    'framework': torch,
                    'version': torch.__version__,
                    'type': 'pytorch'
                }
                logger.info(f"✅ PyTorch {model_type} model loaded")
                
            except ImportError:
                logger.error("❌ PyTorch not available")
                raise ImportError("PyTorch not available. Install with: pip install torch")
            except Exception as e:
                logger.error(f"❌ PyTorch model loading failed: {e}")
                raise
        
        return self._ai_models[f'pytorch_{model_type}']['model']

    def _get_openai_client(self):
        """Get OpenAI client with lazy loading."""
        if 'openai' not in self._ai_models:
            try:
                import openai
                
                api_key = current_app.config.get('OPENAI_API_KEY')
                if not api_key:
                    raise ValueError("OpenAI API key not configured")
                
                openai.api_key = api_key
                
                self._ai_models['openai'] = {
                    'client': openai,
                    'version': openai.__version__,
                    'type': 'openai'
                }
                logger.info("✅ OpenAI client initialized")
                
            except ImportError:
                logger.error("❌ OpenAI not available")
                raise ImportError("OpenAI not available. Install with: pip install openai")
            except Exception as e:
                logger.error(f"❌ OpenAI client initialization failed: {e}")
                raise
        
        return self._ai_models['openai']['client']

    def _get_sentence_transformer(self, model_name: str = 'all-MiniLM-L6-v2'):
        """Get Sentence Transformer model with lazy loading."""
        if f'sentence_transformer_{model_name}' not in self._ai_models:
            try:
                from sentence_transformers import SentenceTransformer
                
                model = SentenceTransformer(model_name)
                
                self._ai_models[f'sentence_transformer_{model_name}'] = {
                    'model': model,
                    'model_name': model_name,
                    'type': 'sentence_transformer'
                }
                logger.info(f"✅ Sentence Transformer model {model_name} loaded")
                
            except ImportError:
                logger.error("❌ Sentence Transformers not available")
                raise ImportError("Sentence Transformers not available. Install with: pip install sentence-transformers")
            except Exception as e:
                logger.error(f"❌ Sentence Transformer model loading failed: {e}")
                raise
        
        return self._ai_models[f'sentence_transformer_{model_name}']['model']

    def _get_sklearn_model(self, model_type: str = 'random_forest'):
        """Get scikit-learn model with lazy loading."""
        if f'sklearn_{model_type}' not in self._ai_models:
            try:
                import sklearn
                from sklearn.ensemble import RandomForestClassifier
                from sklearn.linear_model import LogisticRegression
                from sklearn.svm import SVC
                
                if model_type == 'random_forest':
                    model = RandomForestClassifier(n_estimators=100, random_state=42)
                elif model_type == 'logistic_regression':
                    model = LogisticRegression(random_state=42)
                elif model_type == 'svm':
                    model = SVC(random_state=42)
                else:
                    raise ValueError(f"Unsupported scikit-learn model type: {model_type}")
                
                self._ai_models[f'sklearn_{model_type}'] = {
                    'model': model,
                    'framework': sklearn,
                    'version': sklearn.__version__,
                    'type': 'sklearn'
                }
                logger.info(f"✅ Scikit-learn {model_type} model loaded")
                
            except ImportError:
                logger.error("❌ Scikit-learn not available")
                raise ImportError("Scikit-learn not available. Install with: pip install scikit-learn")
            except Exception as e:
                logger.error(f"❌ Scikit-learn model loading failed: {e}")
                raise
        
        return self._ai_models[f'sklearn_{model_type}']['model']

    @staticmethod
    def test_tensorflow(model_type: str = 'simple'):
        """Test TensorFlow model and return status."""
        try:
            controller = AIMLController()
            model = controller._get_tensorflow_model(model_type)
            
            # Get model summary
            model_info = {
                'layers': len(model.layers),
                'trainable_params': model.count_params(),
                'model_type': model_type
            }
            
            return jsonify({
                'status': 'success',
                'framework': 'tensorflow',
                'model_type': model_type,
                'model_info': model_info,
                'version': controller._ai_models[f'tensorflow_{model_type}']['version'],
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            return jsonify({
                'status': 'error',
                'framework': 'tensorflow',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }), 500

    @staticmethod
    def test_pytorch(model_type: str = 'simple'):
        """Test PyTorch model and return status."""
        try:
            controller = AIMLController()
            model = controller._get_pytorch_model(model_type)
            
            # Get model info
            total_params = sum(p.numel() for p in model.parameters())
            trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
            
            model_info = {
                'total_params': total_params,
                'trainable_params': trainable_params,
                'model_type': model_type
            }
            
            return jsonify({
                'status': 'success',
                'framework': 'pytorch',
                'model_type': model_type,
                'model_info': model_info,
                'version': controller._ai_models[f'pytorch_{model_type}']['version'],
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            return jsonify({
                'status': 'error',
                'framework': 'pytorch',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }), 500

    @staticmethod
    def test_openai():
        """Test OpenAI API and return status."""
        try:
            controller = AIMLController()
            client = controller._get_openai_client()
            
            # Test with a simple completion
            response = client.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Hello! Please respond with 'API test successful'."}],
                max_tokens=10
            )
            
            return jsonify({
                'status': 'success',
                'framework': 'openai',
                'response': response.choices[0].message.content,
                'version': controller._ai_models['openai']['version'],
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            return jsonify({
                'status': 'error',
                'framework': 'openai',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }), 500

    @staticmethod
    def test_sentence_transformer(model_name: str = 'all-MiniLM-L6-v2'):
        """Test Sentence Transformer and return status."""
        try:
            controller = AIMLController()
            model = controller._get_sentence_transformer(model_name)
            
            # Test with simple sentences
            sentences = ["Hello world", "How are you?"]
            embeddings = model.encode(sentences)
            
            return jsonify({
                'status': 'success',
                'framework': 'sentence_transformer',
                'model_name': model_name,
                'embedding_shape': embeddings.shape,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            return jsonify({
                'status': 'error',
                'framework': 'sentence_transformer',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }), 500

    @staticmethod
    def test_sklearn(model_type: str = 'random_forest'):
        """Test scikit-learn model and return status."""
        try:
            controller = AIMLController()
            model = controller._get_sklearn_model(model_type)
            
            # Get model info
            model_info = {
                'model_type': model_type,
                'model_class': model.__class__.__name__
            }
            
            return jsonify({
                'status': 'success',
                'framework': 'sklearn',
                'model_type': model_type,
                'model_info': model_info,
                'version': controller._ai_models[f'sklearn_{model_type}']['version'],
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            return jsonify({
                'status': 'error',
                'framework': 'sklearn',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }), 500

    @staticmethod
    def get_ai_ml_status():
        """Get status of all available AI/ML frameworks."""
        controller = AIMLController()
        
        status = {
            'frameworks': {},
            'timestamp': datetime.now().isoformat()
        }
        
        # Test each framework
        frameworks_to_test = [
            ('tensorflow', lambda: controller._test_tensorflow_internal()),
            ('pytorch', lambda: controller._test_pytorch_internal()),
            ('openai', lambda: controller._test_openai_internal()),
            ('sentence_transformer', lambda: controller._test_sentence_transformer_internal()),
            ('sklearn', lambda: controller._test_sklearn_internal())
        ]
        
        for framework_name, test_func in frameworks_to_test:
            try:
                result = test_func()
                status['frameworks'][framework_name] = {
                    'available': True,
                    'status': 'working',
                    'details': result
                }
            except ImportError as e:
                status['frameworks'][framework_name] = {
                    'available': False,
                    'status': 'not_installed',
                    'error': str(e)
                }
            except Exception as e:
                status['frameworks'][framework_name] = {
                    'available': False,
                    'status': 'error',
                    'error': str(e)
                }
        
        return jsonify(status)

    def _test_tensorflow_internal(self):
        """Internal TensorFlow test."""
        model = self._get_tensorflow_model('simple')
        return {
            'layers': len(model.layers),
            'params': model.count_params()
        }

    def _test_pytorch_internal(self):
        """Internal PyTorch test."""
        model = self._get_pytorch_model('simple')
        total_params = sum(p.numel() for p in model.parameters())
        return {
            'total_params': total_params,
            'trainable_params': sum(p.numel() for p in model.parameters() if p.requires_grad)
        }

    def _test_openai_internal(self):
        """Internal OpenAI test."""
        client = self._get_openai_client()
        response = client.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Test"}],
            max_tokens=5
        )
        return {
            'response_length': len(response.choices[0].message.content)
        }

    def _test_sentence_transformer_internal(self):
        """Internal Sentence Transformer test."""
        model = self._get_sentence_transformer()
        embeddings = model.encode(["Test sentence"])
        return {
            'embedding_dimension': embeddings.shape[1]
        }

    def _test_sklearn_internal(self):
        """Internal scikit-learn test."""
        model = self._get_sklearn_model('random_forest')
        return {
            'model_type': model.__class__.__name__
        }

    def cleanup_models(self):
        """Clean up loaded models to free memory."""
        for model_name, model_info in self._ai_models.items():
            try:
                # Clear model references
                if 'model' in model_info:
                    del model_info['model']
                logger.info(f"✅ Cleaned up {model_name}")
            except Exception as e:
                logger.error(f"❌ Error cleaning up {model_name}: {e}")
        
        self._ai_models.clear()
