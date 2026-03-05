#!/usr/bin/env python3
"""
N8N Integration for AI Chat System
Provides integration with n8n workflows and external APIs
"""

import os
import json
import requests
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import asyncio
from urllib.parse import urljoin


logger = logging.getLogger(__name__)


class N8NIntegration:
    """N8N workflow integration for chat system"""

    def __init__(self):
        """Initialize N8N integration"""
        self.base_url = os.environ.get('N8N_BASE_URL', 'http://localhost:5678').rstrip('/')
        self.api_key = os.environ.get('N8N_API_KEY', '')
        self.enabled = os.environ.get('N8N_ENABLED', 'false').lower() == 'true'
        self.timeout = int(os.environ.get('N8N_WEBHOOK_TIMEOUT', '30'))
        self.retry_attempts = int(os.environ.get('N8N_RETRY_ATTEMPTS', '3'))

        # Common n8n webhooks for different operations
        self.webhooks = {
            'chat_response': '/webhook/chat-response',
            'financial_analysis': '/webhook/financial-analysis',
            'data_processing': '/webhook/data-processing',
            'api_integration': '/webhook/api-integration',
            'database_query': '/webhook/database-query'
        }

    def is_enabled(self) -> bool:
        """Check if N8N integration is enabled"""
        return self.enabled and self.base_url and self.api_key

    def trigger_webhook(self, webhook_type: str, data: Dict[str, Any],
                       async_mode: bool = False) -> Dict[str, Any]:
        """Trigger an N8N webhook"""
        if not self.is_enabled():
            return {
                'success': False,
                'error': 'N8N integration is not enabled'
            }

        if webhook_type not in self.webhooks:
            return {
                'success': False,
                'error': f'Unknown webhook type: {webhook_type}'
            }

        webhook_url = urljoin(self.base_url, self.webhooks[webhook_type])

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }

        payload = {
            'timestamp': datetime.now().isoformat(),
            'source': 'valido_ai_chat',
            'data': data
        }

        for attempt in range(self.retry_attempts):
            try:
                response = requests.post(
                    webhook_url,
                    json=payload,
                    headers=headers,
                    timeout=self.timeout
                )

                if response.status_code == 200:
                    try:
                        result = response.json()
                        return {
                            'success': True,
                            'data': result,
                            'attempt': attempt + 1
                        }
                    except json.JSONDecodeError:
                        return {
                            'success': True,
                            'data': {'message': response.text},
                            'attempt': attempt + 1
                        }
                else:
                    logger.warning(f"N8N webhook attempt {attempt + 1} failed with status {response.status_code}")

            except requests.exceptions.RequestException as e:
                logger.warning(f"N8N webhook attempt {attempt + 1} failed: {e}")

            if attempt < self.retry_attempts - 1:
                # Wait before retry (exponential backoff)
                import time
                time.sleep(2 ** attempt)

        return {
            'success': False,
            'error': f'Failed to trigger N8N webhook after {self.retry_attempts} attempts'
        }

    def process_chat_message(self, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process chat message through N8N"""
        if not context:
            context = {}

        data = {
            'message': message,
            'context': context,
            'message_type': 'chat',
            'processing_mode': 'ai_response'
        }

        return self.trigger_webhook('chat_response', data)

    def financial_analysis_request(self, query: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send financial analysis request to N8N"""
        if not data:
            data = {}

        payload = {
            'query': query,
            'data': data,
            'analysis_type': 'financial',
            'request_timestamp': datetime.now().isoformat()
        }

        return self.trigger_webhook('financial_analysis', payload)

    def api_integration_request(self, api_name: str, endpoint: str,
                              method: str = 'GET', data: Dict[str, Any] = None,
                              headers: Dict[str, str] = None) -> Dict[str, Any]:
        """Send API integration request to N8N"""
        if not data:
            data = {}
        if not headers:
            headers = {}

        payload = {
            'api_name': api_name,
            'endpoint': endpoint,
            'method': method.upper(),
            'data': data,
            'headers': headers,
            'integration_type': 'external_api'
        }

        return self.trigger_webhook('api_integration', payload)

    def database_query_request(self, query: str, database: str = 'main',
                             parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send database query request to N8N"""
        if not parameters:
            parameters = {}

        payload = {
            'query': query,
            'database': database,
            'parameters': parameters,
            'query_type': 'select'
        }

        return self.trigger_webhook('database_query', payload)


class APIIntegrationManager:
    """Manages various API integrations for the chat system"""

    def __init__(self):
        """Initialize API integration manager"""
        self.n8n_integration = N8NIntegration()
        self.api_configs = self._load_api_configs()

    def _load_api_configs(self) -> Dict[str, Dict[str, Any]]:
        """Load API configurations from environment"""
        configs = {}

        # OpenAI Configuration
        if os.environ.get('OPENAI_API_KEY'):
            configs['openai'] = {
                'api_key': os.environ.get('OPENAI_API_KEY'),
                'base_url': 'https://api.openai.com/v1',
                'models': ['gpt-3.5-turbo', 'gpt-4', 'gpt-4-turbo-preview']
            }

        # Anthropic Configuration
        if os.environ.get('ANTHROPIC_API_KEY'):
            configs['anthropic'] = {
                'api_key': os.environ.get('ANTHROPIC_API_KEY'),
                'base_url': 'https://api.anthropic.com/v1',
                'models': ['claude-3-opus', 'claude-3-sonnet', 'claude-3-haiku']
            }

        # Google AI Configuration
        if os.environ.get('GOOGLE_AI_API_KEY'):
            configs['google'] = {
                'api_key': os.environ.get('GOOGLE_AI_API_KEY'),
                'base_url': 'https://generativelanguage.googleapis.com/v1',
                'models': ['gemini-pro', 'gemini-pro-vision']
            }

        # Hugging Face Configuration
        if os.environ.get('HUGGINGFACE_API_KEY'):
            configs['huggingface'] = {
                'api_key': os.environ.get('HUGGINGFACE_API_KEY'),
                'base_url': 'https://api-inference.huggingface.co/models',
                'models': []
            }

        return configs

    def get_available_apis(self) -> List[str]:
        """Get list of available API integrations"""
        return list(self.api_configs.keys())

    def call_openai_api(self, model: str, messages: List[Dict[str, str]],
                       max_tokens: int = 1000) -> Dict[str, Any]:
        """Call OpenAI API"""
        if 'openai' not in self.api_configs:
            return {'success': False, 'error': 'OpenAI API not configured'}

        try:
            headers = {
                'Authorization': f"Bearer {self.api_configs['openai']['api_key']}",
                'Content-Type': 'application/json'
            }

            data = {
                'model': model,
                'messages': messages,
                'max_tokens': max_tokens
            }

            response = requests.post(
                f"{self.api_configs['openai']['base_url']}/chat/completions",
                json=data,
                headers=headers,
                timeout=30
            )

            if response.status_code == 200:
                return {'success': True, 'data': response.json()}
            else:
                return {'success': False, 'error': f'OpenAI API error: {response.status_code}'}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def call_anthropic_api(self, model: str, messages: List[Dict[str, str]],
                          max_tokens: int = 1000) -> Dict[str, Any]:
        """Call Anthropic API"""
        if 'anthropic' not in self.api_configs:
            return {'success': False, 'error': 'Anthropic API not configured'}

        try:
            headers = {
                'x-api-key': self.api_configs['anthropic']['api_key'],
                'Content-Type': 'application/json',
                'anthropic-version': '2023-06-01'
            }

            # Convert messages to Anthropic format
            system_message = ""
            user_messages = []

            for msg in messages:
                if msg['role'] == 'system':
                    system_message = msg['content']
                else:
                    user_messages.append(msg)

            data = {
                'model': model,
                'max_tokens': max_tokens,
                'system': system_message,
                'messages': user_messages
            }

            response = requests.post(
                f"{self.api_configs['anthropic']['base_url']}/messages",
                json=data,
                headers=headers,
                timeout=30
            )

            if response.status_code == 200:
                return {'success': True, 'data': response.json()}
            else:
                return {'success': False, 'error': f'Anthropic API error: {response.status_code}'}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def call_google_ai_api(self, message: str, model: str = 'gemini-pro') -> Dict[str, Any]:
        """Call Google AI API"""
        if 'google' not in self.api_configs:
            return {'success': False, 'error': 'Google AI API not configured'}

        try:
            headers = {
                'Content-Type': 'application/json'
            }

            data = {
                'contents': [{
                    'parts': [{
                        'text': message
                    }]
                }],
                'generationConfig': {
                    'temperature': 0.7,
                    'maxOutputTokens': 1000
                }
            }

            url = f"{self.api_configs['google']['base_url']}/models/{model}:generateContent?key={self.api_configs['google']['api_key']}"

            response = requests.post(url, json=data, headers=headers, timeout=30)

            if response.status_code == 200:
                return {'success': True, 'data': response.json()}
            else:
                return {'success': False, 'error': f'Google AI API error: {response.status_code}'}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def call_external_api(self, api_name: str, endpoint: str, method: str = 'GET',
                         data: Dict[str, Any] = None, headers: Dict[str, str] = None) -> Dict[str, Any]:
        """Call external API through N8N or directly"""
        if self.n8n_integration.is_enabled():
            # Use N8N for API integration
            return self.n8n_integration.api_integration_request(
                api_name, endpoint, method, data, headers
            )
        else:
            # Direct API call (simplified example)
            try:
                response = requests.request(
                    method=method,
                    url=endpoint,
                    json=data if data else None,
                    headers=headers,
                    timeout=30
                )

                if response.status_code < 400:
                    return {'success': True, 'data': response.json()}
                else:
                    return {'success': False, 'error': f'API error: {response.status_code}'}

            except Exception as e:
                return {'success': False, 'error': str(e)}


class ChatAPIIntegration:
    """Integrates API calls into the chat system"""

    def __init__(self):
        """Initialize chat API integration"""
        self.n8n_integration = N8NIntegration()
        self.api_manager = APIIntegrationManager()

    def process_chat_with_apis(self, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process chat message with API integrations"""
        if not context:
            context = {}

        # Check if message requires API integration
        api_call = self._detect_api_call(message)
        if api_call:
            return self._execute_api_call(api_call, context)

        # Check if message should use N8N
        if self.n8n_integration.is_enabled():
            return self.n8n_integration.process_chat_message(message, context)

        # Default response
        return {
            'success': True,
            'response': 'Message processed successfully',
            'source': 'local_ai'
        }

    def _detect_api_call(self, message: str) -> Optional[Dict[str, Any]]:
        """Detect if message contains API call request"""
        message_lower = message.lower()

        # API call patterns
        api_patterns = {
            'openai': ['openai', 'gpt', 'chatgpt'],
            'anthropic': ['claude', 'anthropic'],
            'google': ['gemini', 'google ai', 'bard'],
            'huggingface': ['huggingface', 'hf model'],
            'weather': ['weather', 'temperature', 'forecast'],
            'news': ['news', 'headlines', 'latest news'],
            'stocks': ['stock price', 'stock market', 'ticker'],
            'currency': ['exchange rate', 'currency conversion'],
            'translation': ['translate', 'translation'],
            'search': ['search', 'google', 'web search']
        }

        for api_type, patterns in api_patterns.items():
            if any(pattern in message_lower for pattern in patterns):
                return {
                    'api_type': api_type,
                    'message': message,
                    'confidence': 0.8
                }

        return None

    def _execute_api_call(self, api_call: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute API call based on detected type"""
        api_type = api_call['api_type']
        message = api_call['message']

        try:
            if api_type == 'openai':
                return self.api_manager.call_openai_api(
                    'gpt-3.5-turbo',
                    [{'role': 'user', 'content': message}]
                )
            elif api_type == 'anthropic':
                return self.api_manager.call_anthropic_api(
                    'claude-3-haiku-20240307',
                    [{'role': 'user', 'content': message}]
                )
            elif api_type == 'google':
                return self.api_manager.call_google_ai_api(message)
            else:
                # Use N8N for other API calls
                if self.n8n_integration.is_enabled():
                    return self.n8n_integration.api_integration_request(
                        api_type, f'/api/{api_type}', 'POST', {'message': message}
                    )
                else:
                    return {
                        'success': False,
                        'error': f'API integration for {api_type} not available'
                    }

        except Exception as e:
            return {
                'success': False,
                'error': f'API call failed: {str(e)}'
            }


# Global instances
n8n_integration = N8NIntegration()
api_integration_manager = APIIntegrationManager()
chat_api_integration = ChatAPIIntegration()
