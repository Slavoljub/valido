"""
AI Providers Management
Handles multiple AI providers with fallback logic and configuration
"""

import os
import logging
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import openai
import requests

logger = logging.getLogger(__name__)

@dataclass
class AIProviderConfig:
    """Configuration for an AI provider"""
    name: str
    api_key: Optional[str] = None
    api_base: str = ""
    default_model: str = ""
    enabled: bool = True
    priority: int = 1
    timeout: int = 30
    max_retries: int = 3

class AIProvider:
    """Base class for AI providers"""
    
    def __init__(self, config: AIProviderConfig):
        self.config = config
        self.name = config.name
    
    def test_connection(self) -> Dict[str, Any]:
        """Test connection to the provider"""
        try:
            # Simple connection test
            return {
                "success": True,
                "provider": self.name,
                "message": "Connection successful"
            }
        except Exception as e:
            return {
                "success": False,
                "provider": self.name,
                "error": str(e)
            }
    
    def generate_response(self, prompt: str, model: str = None, **kwargs) -> Dict[str, Any]:
        """Generate response from the provider"""
        try:
            # Default implementation - override in subclasses
            return {
                "provider": self.name,
                "response": f"Sample response from {self.name}",
                "model": model or self.config.default_model,
                "success": True
            }
        except Exception as e:
            return {
                "provider": self.name,
                "error": str(e),
                "success": False
            }
    
    def get_models(self) -> List[str]:
        """Get available models for this provider"""
        return [self.config.default_model]

class OpenAIProvider(AIProvider):
    """OpenAI provider implementation"""
    
    def __init__(self, config: AIProviderConfig):
        super().__init__(config)
        if config.api_key:
            openai.api_key = config.api_key
            if config.api_base:
                openai.api_base = config.api_base
    
    def test_connection(self) -> Dict[str, Any]:
        """Test OpenAI connection"""
        try:
            if not self.config.api_key:
                return {
                    "success": False,
                    "provider": self.name,
                    "error": "API key not configured"
                }
            
            # Test with a simple request
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            
            return {
                "success": True,
                "provider": self.name,
                "message": "Connection successful"
            }
        except Exception as e:
            return {
                "success": False,
                "provider": self.name,
                "error": str(e)
            }
    
    def generate_response(self, prompt: str, model: str = None, **kwargs) -> Dict[str, Any]:
        """Generate response from OpenAI"""
        try:
            if not self.config.api_key:
                return {
                    "provider": self.name,
                    "error": "API key not configured",
                    "success": False
                }
            
            model = model or self.config.default_model or "gpt-3.5-turbo"
            
            response = openai.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=kwargs.get('max_tokens', 1000),
                temperature=kwargs.get('temperature', 0.7)
            )
            
            return {
                "provider": self.name,
                "response": response.choices[0].message.content,
                "model": model,
                "success": True
            }
        except Exception as e:
            return {
                "provider": self.name,
                "error": str(e),
                "success": False
            }
    
    def get_models(self) -> List[str]:
        """Get available OpenAI models"""
        return [
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-16k", 
            "gpt-4",
            "gpt-4-turbo",
            "gpt-4o",
            "gpt-4o-mini"
        ]

class AnthropicProvider(AIProvider):
    """Anthropic (Claude) provider implementation"""
    
    def __init__(self, config: AIProviderConfig):
        super().__init__(config)
        self.api_key = config.api_key
        self.api_base = config.api_base or "https://api.anthropic.com"
    
    def test_connection(self) -> Dict[str, Any]:
        """Test Anthropic connection"""
        try:
            if not self.config.api_key:
                return {
                    "success": False,
                    "provider": self.name,
                    "error": "API key not configured"
                }
            
            # Test with a simple request
            headers = {
                "x-api-key": self.config.api_key,
                "content-type": "application/json",
                "anthropic-version": "2023-06-01"
            }
            
            data = {
                "model": "claude-3-haiku-20240307",
                "max_tokens": 5,
                "messages": [{"role": "user", "content": "Hello"}]
            }
            
            response = requests.post(
                f"{self.api_base}/v1/messages",
                headers=headers,
                json=data,
                timeout=self.config.timeout
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "provider": self.name,
                    "message": "Connection successful"
                }
            else:
                return {
                    "success": False,
                    "provider": self.name,
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
        except Exception as e:
            return {
                "success": False,
                "provider": self.name,
                "error": str(e)
            }
    
    def generate_response(self, prompt: str, model: str = None, **kwargs) -> Dict[str, Any]:
        """Generate response from Anthropic"""
        try:
            if not self.config.api_key:
                return {
                    "provider": self.name,
                    "error": "API key not configured",
                    "success": False
                }
            
            model = model or self.config.default_model or "claude-3-haiku-20240307"
            
            headers = {
                "x-api-key": self.config.api_key,
                "content-type": "application/json",
                "anthropic-version": "2023-06-01"
            }
            
            data = {
                "model": model,
                "max_tokens": kwargs.get('max_tokens', 1000),
                "messages": [{"role": "user", "content": prompt}]
            }
            
            response = requests.post(
                f"{self.api_base}/v1/messages",
                headers=headers,
                json=data,
                timeout=self.config.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "provider": self.name,
                    "response": result["content"][0]["text"],
                    "model": model,
                    "success": True
                }
            else:
                return {
                    "provider": self.name,
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "success": False
                }
        except Exception as e:
            return {
                "provider": self.name,
                "error": str(e),
                "success": False
            }
    
    def get_models(self) -> List[str]:
        """Get available Anthropic models"""
        return [
            "claude-3-haiku-20240307",
            "claude-3-sonnet-20240229",
            "claude-3-opus-20240229"
        ]

class AIProviderManager:
    """Manager for multiple AI providers with fallback logic"""
    
    def __init__(self):
        self.providers: Dict[str, AIProvider] = {}
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize available providers"""
        try:
            # Initialize OpenAI
            openai_config = AIProviderConfig(
                name="openai",
                api_key=os.getenv('OPENAI_API_KEY'),
                default_model="gpt-3.5-turbo",
                enabled=bool(os.getenv('OPENAI_API_KEY')),
                priority=1
            )
            self.providers["openai"] = OpenAIProvider(openai_config)
            
            # Initialize Anthropic
            anthropic_config = AIProviderConfig(
                name="anthropic",
                api_key=os.getenv('ANTHROPIC_API_KEY'),
                default_model="claude-3-haiku-20240307",
                enabled=bool(os.getenv('ANTHROPIC_API_KEY')),
                priority=2
            )
            self.providers["anthropic"] = AnthropicProvider(anthropic_config)
            
            logger.info(f"Initialized {len(self.providers)} AI providers")
            
        except Exception as e:
            logger.error(f"Error initializing AI providers: {e}")
    
    def get_available_providers(self) -> Dict[str, Any]:
        """Get list of available providers with their status"""
        providers_info = {}
        
        for name, provider in self.providers.items():
            test_result = provider.test_connection()
            providers_info[name] = {
                "name": name,
                "enabled": provider.config.enabled,
                "connected": test_result.get("success", False),
                "models": provider.get_models(),
                "default_model": provider.config.default_model,
                "priority": provider.config.priority,
                "test_result": test_result
            }
        
        return providers_info
    
    def generate_response(self, prompt: str, preferred_provider: str = None, model: str = None, **kwargs) -> Dict[str, Any]:
        """Generate response using the best available provider"""
        try:
            # Sort providers by priority
            sorted_providers = sorted(
                self.providers.items(),
                key=lambda x: x[1].config.priority
            )
            
            # If preferred provider is specified and available, try it first
            if preferred_provider and preferred_provider in self.providers:
                provider = self.providers[preferred_provider]
                if provider.config.enabled:
                    result = provider.generate_response(prompt, model, **kwargs)
                    if result.get("success"):
                        return result
            
            # Try providers in priority order
            for name, provider in sorted_providers:
                if not provider.config.enabled:
                    continue
                
                result = provider.generate_response(prompt, model, **kwargs)
                if result.get("success"):
                    return result
            
            # If all providers failed, return error
            return {
                "error": "All AI providers are unavailable",
                "success": False
            }
            
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return {
                "error": str(e),
                "success": False
            }
    
    def test_all_providers(self) -> Dict[str, Any]:
        """Test all configured providers"""
        results = {}
        for name, provider in self.providers.items():
            results[name] = provider.test_connection()
        return results
    
    def get_provider_status(self) -> Dict[str, Any]:
        """Get comprehensive status of all providers"""
        status = {
            "total_providers": len(self.providers),
            "enabled_providers": len([p for p in self.providers.values() if p.config.enabled]),
            "connected_providers": 0,
            "providers": {}
        }
        
        for name, provider in self.providers.items():
            test_result = provider.test_connection()
            if test_result.get("success"):
                status["connected_providers"] += 1
            
            status["providers"][name] = {
                "enabled": provider.config.enabled,
                "connected": test_result.get("success", False),
                "models": provider.get_models(),
                "default_model": provider.config.default_model,
                "priority": provider.config.priority,
                "test_result": test_result
            }
        
        return status
    
    def add_provider(self, name: str, api_key: str, config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Add or update a provider configuration"""
        try:
            if name == "openai":
                provider_config = AIProviderConfig(
                    name=name,
                    api_key=api_key,
                    default_model=config.get('default_model', 'gpt-3.5-turbo'),
                    enabled=True,
                    priority=config.get('priority', 1)
                )
                self.providers[name] = OpenAIProvider(provider_config)
            elif name == "anthropic":
                provider_config = AIProviderConfig(
                    name=name,
                    api_key=api_key,
                    default_model=config.get('default_model', 'claude-3-haiku-20240307'),
                    enabled=True,
                    priority=config.get('priority', 2)
                )
                self.providers[name] = AnthropicProvider(provider_config)
            else:
                return {
                    "success": False,
                    "error": f"Unsupported provider: {name}"
                }
            
            return {
                "success": True,
                "message": f"Provider {name} added successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_provider_models(self, provider_name: str) -> List[str]:
        """Get available models for specific provider"""
        if provider_name in self.providers:
            return self.providers[provider_name].get_models()
        return []
    
    def test_provider(self, provider_name: str) -> Dict[str, Any]:
        """Test specific provider"""
        if provider_name in self.providers:
            return self.providers[provider_name].test_connection()
        return {
            "success": False,
            "error": f"Provider {provider_name} not found"
        }

# Global instance
ai_manager = AIProviderManager()
