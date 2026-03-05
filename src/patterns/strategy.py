#!/usr/bin/env python3
"""
Strategy Pattern Implementation
Defines a family of algorithms (e.g., inference strategies) and makes them interchangeable
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class InferenceStrategy(ABC):
    """Abstract base class for inference strategies"""
    
    @abstractmethod
    def execute(self, model: Any, prompt: str, **kwargs) -> str:
        """Execute inference with specific strategy"""
        pass
    
    @abstractmethod
    def get_info(self) -> Dict[str, Any]:
        """Get strategy information"""
        pass

class CPUStrategy(InferenceStrategy):
    """CPU inference strategy - optimized for CPU-only environments"""
    
    def execute(self, model: Any, prompt: str, **kwargs) -> str:
        """Execute inference on CPU"""
        logger.info("Executing inference on CPU")
        
        # CPU-specific optimizations
        max_length = kwargs.get("max_length", 100)
        temperature = kwargs.get("temperature", 0.7)
        
        # Simulate CPU inference
        response = f"[CPU] Response to: {prompt[:50]}... (max_length: {max_length}, temp: {temperature})"
        logger.info(f"CPU inference completed: {len(response)} characters")
        
        return response
    
    def get_info(self) -> Dict[str, Any]:
        return {
            "name": "CPU Strategy",
            "type": "cpu",
            "description": "CPU-optimized inference strategy",
            "memory_usage": "low",
            "speed": "medium"
        }

class GPUStrategy(InferenceStrategy):
    """GPU inference strategy - optimized for GPU acceleration"""
    
    def execute(self, model: Any, prompt: str, **kwargs) -> str:
        """Execute inference on GPU"""
        logger.info("Executing inference on GPU")
        
        # GPU-specific optimizations
        max_length = kwargs.get("max_length", 100)
        temperature = kwargs.get("temperature", 0.7)
        batch_size = kwargs.get("batch_size", 1)
        
        # Simulate GPU inference
        response = f"[GPU] Response to: {prompt[:50]}... (max_length: {max_length}, temp: {temperature}, batch: {batch_size})"
        logger.info(f"GPU inference completed: {len(response)} characters")
        
        return response
    
    def get_info(self) -> Dict[str, Any]:
        return {
            "name": "GPU Strategy",
            "type": "gpu",
            "description": "GPU-accelerated inference strategy",
            "memory_usage": "high",
            "speed": "fast"
        }

class QuantizedStrategy(InferenceStrategy):
    """Quantized inference strategy - optimized for memory efficiency"""
    
    def execute(self, model: Any, prompt: str, **kwargs) -> str:
        """Execute inference with quantization"""
        logger.info("Executing inference with quantization")
        
        # Quantization-specific optimizations
        max_length = kwargs.get("max_length", 100)
        bits = kwargs.get("bits", 8)
        
        # Simulate quantized inference
        response = f"[Quantized {bits}bit] Response to: {prompt[:50]}... (max_length: {max_length})"
        logger.info(f"Quantized inference completed: {len(response)} characters")
        
        return response
    
    def get_info(self) -> Dict[str, Any]:
        return {
            "name": "Quantized Strategy",
            "type": "quantized",
            "description": "Memory-efficient quantized inference",
            "memory_usage": "very_low",
            "speed": "slow"
        }

class MixedPrecisionStrategy(InferenceStrategy):
    """Mixed precision strategy - balanced performance and memory"""
    
    def execute(self, model: Any, prompt: str, **kwargs) -> str:
        """Execute inference with mixed precision"""
        logger.info("Executing inference with mixed precision")
        
        # Mixed precision optimizations
        max_length = kwargs.get("max_length", 100)
        precision = kwargs.get("precision", "fp16")
        
        # Simulate mixed precision inference
        response = f"[Mixed {precision}] Response to: {prompt[:50]}... (max_length: {max_length})"
        logger.info(f"Mixed precision inference completed: {len(response)} characters")
        
        return response
    
    def get_info(self) -> Dict[str, Any]:
        return {
            "name": "Mixed Precision Strategy",
            "type": "mixed_precision",
            "description": "Balanced performance and memory usage",
            "memory_usage": "medium",
            "speed": "fast"
        }

class StrategyContext:
    """Context class that uses different strategies"""
    
    def __init__(self, strategy: InferenceStrategy = None):
        self._strategy = strategy or CPUStrategy()
    
    def set_strategy(self, strategy: InferenceStrategy):
        """Set the strategy to use"""
        self._strategy = strategy
        logger.info(f"Strategy changed to: {strategy.__class__.__name__}")
    
    def execute_inference(self, model: Any, prompt: str, **kwargs) -> str:
        """Execute inference using current strategy"""
        return self._strategy.execute(model, prompt, **kwargs)
    
    def get_strategy_info(self) -> Dict[str, Any]:
        """Get current strategy information"""
        return self._strategy.get_info()

class StrategySelector:
    """Helper class for selecting appropriate strategy based on hardware"""
    
    @staticmethod
    def select_strategy(hardware_info: Dict[str, Any]) -> InferenceStrategy:
        """Select best strategy based on hardware capabilities"""
        
        has_gpu = hardware_info.get("gpu_available", False)
        gpu_memory = hardware_info.get("gpu_memory_gb", 0)
        cpu_cores = hardware_info.get("cpu_cores", 1)
        system_memory = hardware_info.get("system_memory_gb", 4)
        
        if has_gpu and gpu_memory >= 8:
            logger.info("Selecting GPU strategy (high memory GPU available)")
            return GPUStrategy()
        elif has_gpu and gpu_memory >= 4:
            logger.info("Selecting Mixed Precision strategy (moderate GPU memory)")
            return MixedPrecisionStrategy()
        elif system_memory < 8:
            logger.info("Selecting Quantized strategy (low system memory)")
            return QuantizedStrategy()
        else:
            logger.info("Selecting CPU strategy (default)")
            return CPUStrategy()
    
    @staticmethod
    def get_available_strategies() -> Dict[str, InferenceStrategy]:
        """Get all available strategies"""
        return {
            "cpu": CPUStrategy(),
            "gpu": GPUStrategy(),
            "quantized": QuantizedStrategy(),
            "mixed_precision": MixedPrecisionStrategy()
        }
