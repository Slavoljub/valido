#!/usr/bin/env python3
"""
Factory Pattern Implementation
Creates objects (e.g., different LLM models) without specifying the exact class
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class LLMModel(ABC):
    """Abstract base class for LLM models"""
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text from prompt"""
        pass
    
    @abstractmethod
    def get_info(self) -> Dict[str, Any]:
        """Get model information"""
        pass

class Phi3Model(LLMModel):
    """Microsoft Phi-3 model implementation"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.model_name = "Phi-3"
        self.model_size = config.get("size", "3.8B")
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text using Phi-3"""
        max_length = kwargs.get("max_length", 100)
        return f"[Phi-3 {self.model_size}] Response to: {prompt[:50]}... (max_length: {max_length})"
    
    def get_info(self) -> Dict[str, Any]:
        return {
            "name": self.model_name,
            "size": self.model_size,
            "type": "phi3",
            "config": self.config
        }

class Qwen3Model(LLMModel):
    """Qwen 3 model implementation"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.model_name = "Qwen 3"
        self.model_size = config.get("size", "7B")
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text using Qwen 3"""
        max_length = kwargs.get("max_length", 100)
        return f"[Qwen 3 {self.model_size}] Response to: {prompt[:50]}... (max_length: {max_length})"
    
    def get_info(self) -> Dict[str, Any]:
        return {
            "name": self.model_name,
            "size": self.model_size,
            "type": "qwen3",
            "config": self.config
        }

class Llama3Model(LLMModel):
    """Llama 3 model implementation"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.model_name = "Llama 3"
        self.model_size = config.get("size", "7B")
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text using Llama 3"""
        max_length = kwargs.get("max_length", 100)
        return f"[Llama 3 {self.model_size}] Response to: {prompt[:50]}... (max_length: {max_length})"
    
    def get_info(self) -> Dict[str, Any]:
        return {
            "name": self.model_name,
            "size": self.model_size,
            "type": "llama3",
            "config": self.config
        }

class LLMModelFactory:
    """Factory for creating LLM models"""
    
    _models = {
        "phi3": Phi3Model,
        "qwen3": Qwen3Model,
        "llama3": Llama3Model
    }
    
    @classmethod
    def create_model(cls, model_type: str, config: Dict[str, Any]) -> LLMModel:
        """Create LLM model based on type"""
        if model_type not in cls._models:
            raise ValueError(f"Unknown model type: {model_type}")
        
        try:
            model_class = cls._models[model_type]
            model = model_class(config)
            logger.info(f"Created {model_type} model with config: {config}")
            return model
        except Exception as e:
            logger.error(f"Failed to create {model_type} model: {e}")
            raise
    
    @classmethod
    def get_available_models(cls) -> Dict[str, Dict[str, Any]]:
        """Get list of available models"""
        return {
            model_type: {
                "name": model_class.__name__,
                "description": model_class.__doc__ or f"{model_type} model"
            }
            for model_type, model_class in cls._models.items()
        }
    
    @classmethod
    def register_model(cls, model_type: str, model_class: type):
        """Register a new model type"""
        if not issubclass(model_class, LLMModel):
            raise ValueError(f"Model class must inherit from LLMModel")
        
        cls._models[model_type] = model_class
        logger.info(f"Registered new model type: {model_type}")

class InferenceStrategy(ABC):
    """Abstract base class for inference strategies"""
    
    @abstractmethod
    def execute(self, model: LLMModel, prompt: str, **kwargs) -> str:
        """Execute inference with specific strategy"""
        pass

class CPUStrategy(InferenceStrategy):
    """CPU inference strategy"""
    
    def execute(self, model: LLMModel, prompt: str, **kwargs) -> str:
        """Execute inference on CPU"""
        logger.info("Executing inference on CPU")
        return model.generate(prompt, **kwargs)

class GPUStrategy(InferenceStrategy):
    """GPU inference strategy"""
    
    def execute(self, model: LLMModel, prompt: str, **kwargs) -> str:
        """Execute inference on GPU"""
        logger.info("Executing inference on GPU")
        return model.generate(prompt, **kwargs)

class QuantizedStrategy(InferenceStrategy):
    """Quantized inference strategy"""
    
    def execute(self, model: LLMModel, prompt: str, **kwargs) -> str:
        """Execute inference with quantization"""
        logger.info("Executing inference with quantization")
        return model.generate(prompt, **kwargs)

class InferenceStrategyFactory:
    """Factory for creating inference strategies"""
    
    _strategies = {
        "cpu": CPUStrategy,
        "gpu": GPUStrategy,
        "quantized": QuantizedStrategy
    }
    
    @classmethod
    def create_strategy(cls, strategy_type: str) -> InferenceStrategy:
        """Create inference strategy based on type"""
        if strategy_type not in cls._strategies:
            raise ValueError(f"Unknown strategy type: {strategy_type}")
        
        strategy_class = cls._strategies[strategy_type]
        return strategy_class()
    
    @classmethod
    def get_available_strategies(cls) -> Dict[str, str]:
        """Get list of available strategies"""
        return {
            strategy_type: strategy_class.__name__
            for strategy_type, strategy_class in cls._strategies.items()
        }
