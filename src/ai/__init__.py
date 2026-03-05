"""
ValidoAI AI Package
==================

AI and Machine Learning functionality for ValidoAI.

This package includes:
- Local AI model management
- External AI model integration
- Chat and conversation systems
- Multimodal processing
- AI safety and security
- Model training and inference
- GPU acceleration support
"""

from .chat import *
from .sentiment import *

# Import from unified models
try:
    from src.models.unified_models import LocalModelManager
except ImportError:
    LocalModelManager = None

__all__ = [
    'LocalModelManager',
    'ChatEngine',
    'SentimentAnalyzer',
    'sentiment_analyzer'
]
