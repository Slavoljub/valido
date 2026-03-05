"""
AI Models and OpenAI Integration
Organized AI functionality for the ValidoAI application
"""

import logging
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
from dataclasses import dataclass
import time

from openai import OpenAI
from ..core_config.config import Configuration

logger = logging.getLogger(__name__)


@dataclass
class AIModelConfig:
    """Configuration for AI models"""
    name: str
    max_tokens: int
    default_temp: float
    description: str


class AIModelManager:
    """Manages AI model configurations and availability"""
    
    AVAILABLE_MODELS = {
        # GPT-4 Models
        "gpt-4o": AIModelConfig("GPT-4o", 4096, 0.7, "Most capable model for complex tasks"),
        "gpt-4o-mini": AIModelConfig("GPT-4o Mini", 4096, 0.7, "Fast and efficient model"),
        "gpt-4-turbo": AIModelConfig("GPT-4 Turbo", 4096, 0.7, "Previous generation GPT-4"),
        "gpt-4": AIModelConfig("GPT-4", 4096, 0.7, "Base GPT-4 model"),
        
        # GPT-3.5 Models
        "gpt-3.5-turbo": AIModelConfig("GPT-3.5 Turbo", 4096, 0.7, "Fast and cost-effective"),
        "gpt-3.5-turbo-16k": AIModelConfig("GPT-3.5 Turbo 16K", 16384, 0.7, "Extended context window"),
        
        # DALL-E Models
        "dall-e-3": AIModelConfig("DALL-E 3", 4096, 0.7, "Image generation model"),
        "dall-e-2": AIModelConfig("DALL-E 2", 4096, 0.7, "Previous image generation model"),
        
        # Whisper Models
        "whisper-1": AIModelConfig("Whisper", 4096, 0.7, "Speech-to-text model"),
        
        # TTS Models
        "tts-1": AIModelConfig("TTS-1", 4096, 0.7, "Text-to-speech model"),
        "tts-1-hd": AIModelConfig("TTS-1 HD", 4096, 0.7, "High-definition text-to-speech"),
        
        # Embedding Models
        "text-embedding-3-small": AIModelConfig("Text Embedding 3 Small", 4096, 0.7, "Small embedding model"),
        "text-embedding-3-large": AIModelConfig("Text Embedding 3 Large", 4096, 0.7, "Large embedding model"),
        "text-embedding-ada-002": AIModelConfig("Text Embedding Ada 002", 4096, 0.7, "Previous embedding model"),
        
        # Moderation Models
        "text-moderation-latest": AIModelConfig("Text Moderation Latest", 4096, 0.7, "Content moderation model"),
        "text-moderation-stable": AIModelConfig("Text Moderation Stable", 4096, 0.7, "Stable moderation model")
    }
    
    DEFAULT_MODEL = "gpt-3.5-turbo"
    
    @classmethod
    def get_model_config(cls, model_name: str) -> Optional[AIModelConfig]:
        """Get configuration for a specific model"""
        return cls.AVAILABLE_MODELS.get(model_name)
    
    @classmethod
    def get_available_models(cls) -> Dict[str, AIModelConfig]:
        """Get all available models"""
        return cls.AVAILABLE_MODELS.copy()
    
    @classmethod
    def is_model_available(cls, model_name: str) -> bool:
        """Check if a model is available"""
        return model_name in cls.AVAILABLE_MODELS


class OpenAIWrapper:
    """Wrapper for OpenAI API interactions"""
    
    def __init__(self):
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """Initialize OpenAI client"""
        try:
            config = Configuration()
            if not config.openai.api_key:
                raise ValueError("OpenAI API key not configured")
            
            self.client = OpenAI(
                api_key=config.openai.api_key,
                organization=config.openai.organization,
                base_url=config.openai.api_base
            )
            logger.info("OpenAI client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            self.client = None
    
    def is_available(self) -> bool:
        """Check if OpenAI client is available"""
        return self.client is not None
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = None,
        max_tokens: int = None,
        temperature: float = None,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """
        Make a chat completion request
        
        Args:
            messages: List of message dictionaries
            model: Model to use (defaults to config)
            max_tokens: Maximum tokens (defaults to config)
            temperature: Temperature setting (defaults to config)
            **kwargs: Additional parameters
            
        Returns:
            Response dictionary or None if failed
        """
        if not self.is_available():
            logger.error("OpenAI client not available")
            return None
        
        try:
            # Use defaults from config if not provided
            config = Configuration()
            model = model or config.openai.default_model
            max_tokens = max_tokens or config.openai.max_tokens
            temperature = temperature or config.openai.temperature
            
            start_time = time.time()
            
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )
            
            end_time = time.time()
            
            return {
                'response': response.choices[0].message.content,
                'model': model,
                'tokens_used': response.usage.total_tokens if hasattr(response, 'usage') else None,
                'response_time': end_time - start_time,
                'status': 'success'
            }
            
        except Exception as e:
            logger.error(f"OpenAI API request failed: {e}")
            return {
                'response': None,
                'error': str(e),
                'status': 'error'
            }


class BaseAIService(ABC):
    """Abstract base class for AI services"""
    
    def __init__(self, openai_wrapper: OpenAIWrapper):
        self.openai = openai_wrapper
    
    @abstractmethod
    def process_request(self, user_message: str, **kwargs) -> Dict[str, Any]:
        """Process a user request"""
        pass
    
    def log_request(self, endpoint: str, user_message: str, response: Dict[str, Any]) -> None:
        """Log the request for monitoring"""
        from .database_models import OpenAILog
        from ..extensions import db
        
        try:
            log_entry = OpenAILog(
                endpoint=endpoint,
                model=response.get('model', 'unknown'),
                user_message=user_message,
                ai_response=response.get('response'),
                tokens_used=response.get('tokens_used'),
                response_time=response.get('response_time'),
                status=response.get('status', 'unknown')
            )
            
            db.session.add(log_entry)
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Failed to log request: {e}")


def init_ai_models(app):
    """Initialize AI models with the Flask app"""
    # This function can be used to initialize any AI-specific configurations
    # when the Flask app starts
    pass
