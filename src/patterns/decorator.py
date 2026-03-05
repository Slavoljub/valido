#!/usr/bin/env python3
"""
Decorator Pattern Implementation
Wraps functionality (e.g., logging, caching, preprocessing) around core LLM inference
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Callable, Optional, List
import logging
import time
import functools
import hashlib
import json

logger = logging.getLogger(__name__)

class LLMInference(ABC):
    """Abstract base class for LLM inference"""
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text from prompt"""
        pass

class BaseLLMInference(LLMInference):
    """Base LLM inference implementation"""
    
    def __init__(self, model_name: str = "default"):
        self.model_name = model_name
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Base text generation"""
        return f"[{self.model_name}] Response to: {prompt[:50]}..."

class InferenceDecorator(LLMInference):
    """Base decorator class for LLM inference"""
    
    def __init__(self, inference: LLMInference):
        self._inference = inference
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Delegate to wrapped inference"""
        return self._inference.generate(prompt, **kwargs)

class LoggingDecorator(InferenceDecorator):
    """Decorator that adds logging functionality"""
    
    def __init__(self, inference: LLMInference, log_level: str = "INFO"):
        super().__init__(inference)
        self.log_level = log_level
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate with logging"""
        start_time = time.time()
        
        logger.info(f"Starting inference with prompt: {prompt[:100]}...")
        logger.info(f"Inference parameters: {kwargs}")
        
        try:
            result = self._inference.generate(prompt, **kwargs)
            
            end_time = time.time()
            duration = end_time - start_time
            
            logger.info(f"Inference completed in {duration:.2f}s")
            logger.info(f"Generated response: {result[:100]}...")
            
            return result
            
        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            
            logger.error(f"Inference failed after {duration:.2f}s: {e}")
            raise

class CachingDecorator(InferenceDecorator):
    """Decorator that adds caching functionality"""
    
    def __init__(self, inference: LLMInference, cache_ttl: int = 3600):
        super().__init__(inference)
        self.cache_ttl = cache_ttl
        self._cache: Dict[str, Dict[str, Any]] = {}
    
    def _generate_cache_key(self, prompt: str, **kwargs) -> str:
        """Generate cache key from prompt and parameters"""
        cache_data = {
            "prompt": prompt,
            "kwargs": sorted(kwargs.items())
        }
        cache_string = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_string.encode()).hexdigest()
    
    def _is_cache_valid(self, cache_entry: Dict[str, Any]) -> bool:
        """Check if cache entry is still valid"""
        if "timestamp" not in cache_entry:
            return False
        
        current_time = time.time()
        return (current_time - cache_entry["timestamp"]) < self.cache_ttl
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate with caching"""
        cache_key = self._generate_cache_key(prompt, **kwargs)
        
        # Check cache
        if cache_key in self._cache:
            cache_entry = self._cache[cache_key]
            if self._is_cache_valid(cache_entry):
                logger.info(f"Cache hit for prompt: {prompt[:50]}...")
                return cache_entry["result"]
            else:
                # Remove expired cache entry
                del self._cache[cache_key]
        
        # Generate new result
        logger.info(f"Cache miss for prompt: {prompt[:50]}...")
        result = self._inference.generate(prompt, **kwargs)
        
        # Store in cache
        self._cache[cache_key] = {
            "result": result,
            "timestamp": time.time()
        }
        
        return result
    
    def clear_cache(self):
        """Clear all cached results"""
        self._cache.clear()
        logger.info("Cache cleared")

class ValidationDecorator(InferenceDecorator):
    """Decorator that adds input validation"""
    
    def __init__(self, inference: LLMInference, max_length: int = 1000):
        super().__init__(inference)
        self.max_length = max_length
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate with validation"""
        # Validate input
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty")
        
        if len(prompt) > self.max_length:
            raise ValueError(f"Prompt too long. Maximum length: {self.max_length}")
        
        # Validate parameters
        max_tokens = kwargs.get("max_tokens", 100)
        if max_tokens <= 0:
            raise ValueError("max_tokens must be positive")
        
        if max_tokens > 1000:
            logger.warning(f"Large max_tokens value: {max_tokens}")
        
        logger.info(f"Input validation passed for prompt: {prompt[:50]}...")
        return self._inference.generate(prompt, **kwargs)

class RateLimitingDecorator(InferenceDecorator):
    """Decorator that adds rate limiting"""
    
    def __init__(self, inference: LLMInference, requests_per_minute: int = 60):
        super().__init__(inference)
        self.requests_per_minute = requests_per_minute
        self.request_times: List[float] = []
    
    def _clean_old_requests(self):
        """Remove requests older than 1 minute"""
        current_time = time.time()
        self.request_times = [
            req_time for req_time in self.request_times
            if current_time - req_time < 60
        ]
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate with rate limiting"""
        self._clean_old_requests()
        
        if len(self.request_times) >= self.requests_per_minute:
            wait_time = 60 - (time.time() - self.request_times[0])
            if wait_time > 0:
                logger.warning(f"Rate limit exceeded. Waiting {wait_time:.2f}s")
                time.sleep(wait_time)
        
        # Add current request
        self.request_times.append(time.time())
        
        logger.info(f"Rate limiting passed. Current requests: {len(self.request_times)}")
        return self._inference.generate(prompt, **kwargs)

class MetricsDecorator(InferenceDecorator):
    """Decorator that adds metrics collection"""
    
    def __init__(self, inference: LLMInference):
        super().__init__(inference)
        self.metrics = {
            "total_requests": 0,
            "total_tokens": 0,
            "total_time": 0.0,
            "average_time": 0.0,
            "errors": 0
        }
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate with metrics collection"""
        start_time = time.time()
        
        try:
            result = self._inference.generate(prompt, **kwargs)
            
            # Update metrics
            end_time = time.time()
            duration = end_time - start_time
            
            self.metrics["total_requests"] += 1
            self.metrics["total_tokens"] += len(result.split())
            self.metrics["total_time"] += duration
            self.metrics["average_time"] = self.metrics["total_time"] / self.metrics["total_requests"]
            
            logger.info(f"Metrics updated: {self.metrics}")
            return result
            
        except Exception as e:
            self.metrics["errors"] += 1
            logger.error(f"Error in inference: {e}")
            raise
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        return self.metrics.copy()

class RetryDecorator(InferenceDecorator):
    """Decorator that adds retry functionality"""
    
    def __init__(self, inference: LLMInference, max_retries: int = 3, delay: float = 1.0):
        super().__init__(inference)
        self.max_retries = max_retries
        self.delay = delay
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate with retry logic"""
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                logger.info(f"Inference attempt {attempt + 1}/{self.max_retries + 1}")
                return self._inference.generate(prompt, **kwargs)
                
            except Exception as e:
                last_exception = e
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                
                if attempt < self.max_retries:
                    logger.info(f"Retrying in {self.delay}s...")
                    time.sleep(self.delay)
                    self.delay *= 2  # Exponential backoff
        
        logger.error(f"All {self.max_retries + 1} attempts failed")
        raise last_exception

# Utility function to create decorated inference
def create_decorated_inference(
    base_inference: LLMInference,
    enable_logging: bool = True,
    enable_caching: bool = True,
    enable_validation: bool = True,
    enable_rate_limiting: bool = False,
    enable_metrics: bool = True,
    enable_retry: bool = False,
    **kwargs
) -> LLMInference:
    """Create inference with specified decorators"""
    
    inference = base_inference
    
    # Apply decorators in order
    if enable_retry:
        inference = RetryDecorator(inference, **kwargs.get("retry_config", {}))
    
    if enable_validation:
        inference = ValidationDecorator(inference, **kwargs.get("validation_config", {}))
    
    if enable_rate_limiting:
        inference = RateLimitingDecorator(inference, **kwargs.get("rate_limit_config", {}))
    
    if enable_caching:
        inference = CachingDecorator(inference, **kwargs.get("cache_config", {}))
    
    if enable_metrics:
        inference = MetricsDecorator(inference)
    
    if enable_logging:
        inference = LoggingDecorator(inference, **kwargs.get("logging_config", {}))
    
    return inference
