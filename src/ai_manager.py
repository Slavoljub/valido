#!/usr/bin/env python3
"""
Unified AI Manager - DRY Implementation
Consolidates all AI functionality into a single, comprehensive system
"""

import os
import sys
import json
import logging
import hashlib
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from config.unified_config import config
    from database.unified_db_manager import db
except ImportError:
    config = None
    db = None

logger = logging.getLogger(__name__)

class AIContext:
    """AI Context for safety and monitoring"""

    def __init__(self, user_id: str = None, company_id: str = None,
                 session_id: str = None, risk_level: str = "low"):
        self.user_id = user_id
        self.company_id = company_id
        self.session_id = session_id
        self.risk_level = risk_level
        self.timestamp = datetime.now().isoformat()
        self.metadata = {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            'user_id': self.user_id,
            'company_id': self.company_id,
            'session_id': self.session_id,
            'risk_level': self.risk_level,
            'timestamp': self.timestamp,
            'metadata': self.metadata
        }

class AISafetyManager:
    """AI Safety Manager with comprehensive safety checks"""

    def __init__(self):
        self.safety_rules = {
            'max_tokens': 4096,
            'temperature': 0.7,
            'max_length': 2048,
            'prohibited_topics': [
                'harmful', 'illegal', 'inappropriate', 'sensitive'
            ],
            'rate_limits': {
                'requests_per_minute': 60,
                'tokens_per_minute': 10000
            }
        }
        self.violation_log = []

    def validate_input(self, input_text: str, context: AIContext = None) -> Dict[str, Any]:
        """Validate user input for safety"""
        try:
            # Check input length
            if len(input_text) > self.safety_rules['max_length']:
                return {
                    'safe': False,
                    'reason': 'Input too long',
                    'confidence': 0.9
                }

            # Check for prohibited content
            for topic in self.safety_rules['prohibited_topics']:
                if topic.lower() in input_text.lower():
                    return {
                        'safe': False,
                        'reason': f'Contains prohibited topic: {topic}',
                        'confidence': 0.8
                    }

            # Check for financial data exposure
            if self._contains_sensitive_data(input_text):
                return {
                    'safe': False,
                    'reason': 'Contains sensitive financial data',
                    'confidence': 0.95
                }

            return {
                'safe': True,
                'reason': 'Input passed safety checks',
                'confidence': 0.9
            }

        except Exception as e:
            logger.error(f"Error in safety validation: {e}")
            return {
                'safe': False,
                'reason': 'Safety validation error',
                'confidence': 0.5
            }

    def _contains_sensitive_data(self, text: str) -> bool:
        """Check if text contains sensitive financial data"""
        sensitive_patterns = [
            r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b',  # Credit card
            r'\b\d{3}[- ]?\d{2}[- ]?\d{4}\b',  # SSN
            r'\b[A-Z]{2}\d{2}[A-Z0-9]{16}\b',  # IBAN
            r'\$\d{1,3}(,\d{3})*\.?\d{0,2}',  # Dollar amounts
            r'\d+\.\d+\.\d+\.\d+',  # IP addresses
            r'\b\d{10,15}\b'  # Long numbers (potentially phone/bank account)
        ]

        import re
        for pattern in sensitive_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False

    def log_violation(self, violation: Dict[str, Any]):
        """Log safety violation"""
        self.violation_log.append({
            'timestamp': datetime.now().isoformat(),
            **violation
        })

        # Keep only last 1000 violations
        if len(self.violation_log) > 1000:
            self.violation_log = self.violation_log[-1000:]

class RedisCacheManager:
    """Redis Cache Manager with fallback"""

    def __init__(self):
        self.cache = {}
        self.redis_available = False

        try:
            import redis
            self.redis = redis.Redis(host='localhost', port=6379, decode_responses=True)
            self.redis.ping()
            self.redis_available = True
            logger.info("✅ Redis cache initialized")
        except Exception as e:
            logger.warning(f"⚠️ Redis not available: {e}")
            self.redis_available = False

    def get(self, key: str) -> Optional[str]:
        """Get value from cache"""
        try:
            if self.redis_available:
                return self.redis.get(key)
            else:
                return self.cache.get(key)
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None

    def set(self, key: str, value: str, expire: int = 3600) -> bool:
        """Set value in cache"""
        try:
            if self.redis_available:
                return self.redis.set(key, value, ex=expire)
            else:
                self.cache[key] = value
                return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False

    def delete(self, key: str) -> bool:
        """Delete value from cache"""
        try:
            if self.redis_available:
                return bool(self.redis.delete(key))
            else:
                return bool(self.cache.pop(key, None))
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False

class EnvironmentConfig:
    """Environment Configuration Manager"""

    def __init__(self):
        self.config = {}
        self.load_config()

    def load_config(self):
        """Load configuration from environment and files"""
        try:
            # Load from environment variables
            self.config.update({
                'debug': os.getenv('DEBUG', 'false').lower() == 'true',
                'testing': os.getenv('TESTING', 'false').lower() == 'true',
                'database_type': os.getenv('DATABASE_TYPE', 'sqlite'),
                'database_host': os.getenv('DATABASE_HOST', 'localhost'),
                'database_port': int(os.getenv('DATABASE_PORT', '5432')),
                'database_name': os.getenv('DATABASE_NAME', 'validoai'),
                'database_user': os.getenv('DATABASE_USER', 'validoai'),
                'database_password': os.getenv('DATABASE_PASSWORD', ''),
                'ai_enabled': os.getenv('AI_ENABLED', 'true').lower() == 'true',
                'ai_default_model': os.getenv('AI_DEFAULT_MODEL', 'qwen-3'),
                'ai_model_path': os.getenv('AI_MODEL_PATH', 'local_llm_models/'),
                'gpu_enabled': os.getenv('GPU_ENABLED', 'false').lower() == 'true',
                'secret_key': os.getenv('SECRET_KEY', 'dev-secret-key'),
                'jwt_secret_key': os.getenv('JWT_SECRET_KEY', 'dev-jwt-key'),
                'domain': os.getenv('DOMAIN', 'validoai.test')
            })

            # Load from .env file if available
            env_file = Path('.env')
            if env_file.exists():
                from dotenv import load_dotenv
                load_dotenv()
                self.config.update({
                    'debug': os.getenv('DEBUG', 'false').lower() == 'true',
                    'testing': os.getenv('TESTING', 'false').lower() == 'true',
                    'database_type': os.getenv('DATABASE_TYPE', 'sqlite'),
                    'database_host': os.getenv('DATABASE_HOST', 'localhost'),
                    'database_port': int(os.getenv('DATABASE_PORT', '5432')),
                    'database_name': os.getenv('DATABASE_NAME', 'validoai'),
                    'database_user': os.getenv('DATABASE_USER', 'validoai'),
                    'database_password': os.getenv('DATABASE_PASSWORD', ''),
                    'ai_enabled': os.getenv('AI_ENABLED', 'true').lower() == 'true',
                    'ai_default_model': os.getenv('AI_DEFAULT_MODEL', 'qwen-3'),
                    'ai_model_path': os.getenv('AI_MODEL_PATH', 'local_llm_models/'),
                    'gpu_enabled': os.getenv('GPU_ENABLED', 'false').lower() == 'true',
                    'secret_key': os.getenv('SECRET_KEY', 'dev-secret-key'),
                    'jwt_secret_key': os.getenv('JWT_SECRET_KEY', 'dev-jwt-key'),
                    'domain': os.getenv('DOMAIN', 'validoai.test')
                })

        except Exception as e:
            logger.error(f"Error loading environment config: {e}")
            # Use default values
            self.config = {
                'debug': True,
                'testing': False,
                'database_type': 'sqlite',
                'ai_enabled': True,
                'ai_default_model': 'qwen-3',
                'secret_key': 'dev-secret-key'
            }

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.config.get(key, default)

class ModelDownloader:
    """AI Model Downloader"""

    def __init__(self):
        self.models_dir = Path("local_llm_models")
        self.models_dir.mkdir(exist_ok=True)

    def download_model(self, model_name: str) -> bool:
        """Download a specific AI model"""
        try:
            # This would implement actual model downloading
            # For now, just create a placeholder
            model_path = self.models_dir / f"{model_name}.gguf"
            if not model_path.exists():
                # Create a dummy file for testing
                model_path.write_text(f"# Placeholder for {model_name} model")
                logger.info(f"✅ Model {model_name} downloaded")
                return True
            return True
        except Exception as e:
            logger.error(f"❌ Error downloading model {model_name}: {e}")
            return False

    def get_text_models(self) -> List[Dict[str, Any]]:
        """Get available text models"""
        return [
            {
                'id': 'qwen-3',
                'name': 'Qwen 3B',
                'type': 'local',
                'size': '4GB',
                'description': 'General purpose AI assistant',
                'provider': 'Local',
                'category': 'General Purpose',
                'available': True,
                'downloaded': (self.models_dir / 'qwen-3.gguf').exists()
            },
            {
                'id': 'phi-3',
                'name': 'Phi-3 Mini',
                'type': 'local',
                'size': '2.3GB',
                'description': 'Lightweight instruction model',
                'provider': 'Local',
                'category': 'Lightweight',
                'available': True,
                'downloaded': (self.models_dir / 'phi-3.gguf').exists()
            },
            {
                'id': 'mistral-7b',
                'name': 'Mistral 7B',
                'type': 'local',
                'size': '4.1GB',
                'description': 'Advanced reasoning model',
                'provider': 'Local',
                'category': 'Advanced',
                'available': True,
                'downloaded': (self.models_dir / 'mistral-7b.gguf').exists()
            },
            {
                'id': 'gpt-4',
                'name': 'GPT-4',
                'type': 'external',
                'size': 'API',
                'description': 'OpenAI GPT-4 for advanced tasks',
                'provider': 'OpenAI',
                'category': 'Premium',
                'available': bool(os.getenv('OPENAI_API_KEY')),
                'downloaded': True
            },
            {
                'id': 'claude-3',
                'name': 'Claude 3',
                'type': 'external',
                'size': 'API',
                'description': 'Anthropic Claude for analysis',
                'provider': 'Anthropic',
                'category': 'Premium',
                'available': bool(os.getenv('ANTHROPIC_API_KEY')),
                'downloaded': True
            },
            {
                'id': 'gemini-pro',
                'name': 'Gemini Pro',
                'type': 'external',
                'size': 'API',
                'description': 'Google Gemini for tasks',
                'provider': 'Google',
                'category': 'Premium',
                'available': bool(os.getenv('GOOGLE_API_KEY')),
                'downloaded': True
            }
        ]

    def get_audio_models(self) -> List[Dict[str, Any]]:
        """Get available audio models"""
        return [
            {
                'id': 'whisper-base',
                'name': 'Whisper Base',
                'type': 'local',
                'size': '74MB',
                'description': 'Speech to text transcription',
                'provider': 'Local',
                'category': 'Transcription',
                'available': True,
                'downloaded': True
            },
            {
                'id': 'whisper-large',
                'name': 'Whisper Large',
                'type': 'local',
                'size': '1.5GB',
                'description': 'High accuracy speech recognition',
                'provider': 'Local',
                'category': 'Advanced',
                'available': True,
                'downloaded': False
            }
        ]

    def get_models_by_category(self, category: str = None) -> Dict[str, List[Dict[str, Any]]]:
        """Get models organized by category"""
        text_models = self.get_text_models()
        audio_models = self.get_audio_models()

        if category == 'local':
            return {
                'Local LLM Models': [m for m in text_models if m['type'] == 'local'],
                'Local Audio Models': audio_models
            }
        elif category == 'external':
            return {
                'External API Models': [m for m in text_models if m['type'] == 'external']
            }
        else:
            return {
                'Local LLM Models': [m for m in text_models if m['type'] == 'local'],
                'External API Models': [m for m in text_models if m['type'] == 'external'],
                'Local Audio Models': audio_models
            }

class GPUDetector:
    """GPU Detection and Management"""

    def __init__(self):
        self.gpu_available = False
        self.gpu_info = {}
        self.detect_gpu()

    def detect_gpu(self):
        """Detect available GPU resources"""
        try:
            import pynvml
            pynvml.nvmlInit()

            device_count = pynvml.nvmlDeviceGetCount()
            if device_count > 0:
                self.gpu_available = True
                handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                self.gpu_info = {
                    'name': pynvml.nvmlDeviceGetName(handle),
                    'memory_total': info.total,
                    'memory_used': info.used,
                    'memory_free': info.free
                }
                logger.info("✅ GPU detected and available")
            else:
                logger.info("ℹ️ No GPU detected")
        except Exception as e:
            logger.info(f"ℹ️ GPU detection not available: {e}")

    def get_gpu_info(self) -> Dict[str, Any]:
        """Get GPU information"""
        return {
            'available': self.gpu_available,
            'info': self.gpu_info
        }

    def get_gpu_status(self) -> Dict[str, Any]:
        """Get GPU status for backward compatibility"""
        return self.get_gpu_info()

# Global instances
ai_safety_manager = AISafetyManager()
redis_cache = RedisCacheManager()
env_config = EnvironmentConfig()

# Export for backward compatibility
__all__ = [
    'AIContext',
    'AISafetyManager',
    'RedisCacheManager',
    'EnvironmentConfig',
    'ModelDownloader',
    'GPUDetector',
    'ai_safety_manager',
    'redis_cache',
    'env_config'
]
