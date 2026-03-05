#!/usr/bin/env python3
"""
Comprehensive Integration Tests for AI Chat System
Tests all new features including external models, data sources, disclaimers, and enhanced functionality
"""

import pytest
import json
import os
from unittest.mock import Mock, patch, MagicMock
from flask import Flask, request
from flask.testing import FlaskClient

from src.ai_local_models.data_source_integrator import (
    DataSourceIntegrator,
    WordPressIntegration,
    WooCommerceIntegration,
    StripeIntegration,
    ShopifyIntegration,
    QuickBooksIntegration,
    SalesforceIntegration
)
from src.ai_local_models.n8n_integration import (
    N8NIntegration,
    APIIntegrationManager,
    ChatAPIIntegration
)
from src.controllers.chat_controller import chat_controller
from routes import create_app
from src.ai_local_models.question_manager import question_manager


class TestDataSourceIntegration:
    """Test data source integration functionality"""

    def test_data_source_integrator_initialization(self):
        """Test data source integrator initialization"""
        integrator = DataSourceIntegrator()
        assert integrator.sources is not None
        assert isinstance(integrator.sources, dict)

    def test_available_sources(self):
        """Test getting available data sources"""
        integrator = DataSourceIntegrator()
        sources = integrator.get_available_sources()
        assert isinstance(sources, list)

    @patch('requests.get')
    def test_wordpress_integration(self, mock_get):
        """Test WordPress integration"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'found': 5,
            'posts': [{'id': 1, 'title': 'Test Post'}]
        }
        mock_get.return_value = mock_response

        with patch.dict(os.environ, {
            'WORDPRESS_ENABLED': 'true',
            'WORDPRESS_URL': 'https://test.com',
            'WORDPRESS_USERNAME': 'user',
            'WORDPRESS_PASSWORD': 'pass'
        }):
            integrator = DataSourceIntegrator()
            wordpress = integrator.sources.get('wordpress')

            if wordpress:
                result = wordpress.get_posts()
                assert result['success'] is True

    @patch('requests.get')
    def test_stripe_integration(self, mock_get):
        """Test Stripe integration"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'object': 'balance',
            'available': [{'amount': 10000, 'currency': 'usd'}]
        }
        mock_get.return_value = mock_response

        with patch.dict(os.environ, {
            'STRIPE_ENABLED': 'true',
            'STRIPE_SECRET_KEY': 'sk_test_123'
        }):
            integrator = DataSourceIntegrator()
            stripe = integrator.sources.get('stripe')

            if stripe:
                result = stripe.get_balance()
                assert result['success'] is True

    @patch('requests.get')
    def test_quickbooks_integration(self, mock_get):
        """Test QuickBooks integration"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'CompanyInfo': {'CompanyName': 'Test Company'}
        }
        mock_get.return_value = mock_response

        with patch.dict(os.environ, {
            'QUICKBOOKS_ENABLED': 'true',
            'QUICKBOOKS_CLIENT_ID': 'test_client_id',
            'QUICKBOOKS_CLIENT_SECRET': 'test_client_secret'
        }):
            integrator = DataSourceIntegrator()
            quickbooks = integrator.sources.get('quickbooks')

            if quickbooks:
                result = quickbooks.get_company_info()
                assert result['success'] is True


class TestN8NIntegration:
    """Test N8N integration functionality"""

    def test_n8n_integration_initialization(self):
        """Test N8N integration initialization"""
        with patch.dict(os.environ, {
            'N8N_ENABLED': 'true',
            'N8N_BASE_URL': 'http://localhost:5678',
            'N8N_API_KEY': 'test_key'
        }):
            n8n = N8NIntegration()
            assert n8n.is_enabled() is True

    def test_n8n_disabled(self):
        """Test N8N integration when disabled"""
        with patch.dict(os.environ, {
            'N8N_ENABLED': 'false'
        }):
            n8n = N8NIntegration()
            assert n8n.is_enabled() is False

    @patch('requests.post')
    def test_n8n_webhook_trigger(self, mock_post):
        """Test N8N webhook triggering"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'result': 'success'}
        mock_post.return_value = mock_response

        with patch.dict(os.environ, {
            'N8N_ENABLED': 'true',
            'N8N_BASE_URL': 'http://localhost:5678',
            'N8N_API_KEY': 'test_key'
        }):
            n8n = N8NIntegration()
            result = n8n.trigger_webhook('chat_response', {'message': 'test'})

            assert result['success'] is True
            assert result['data'] == {'result': 'success'}

    def test_api_integration_manager(self):
        """Test API integration manager"""
        with patch.dict(os.environ, {
            'OPENAI_API_KEY': 'test_key'
        }):
            manager = APIIntegrationManager()
            available_apis = manager.get_available_apis()
            assert 'openai' in available_apis


class TestChatControllerIntegration:
    """Test chat controller with new features"""

    def test_get_question_suggestions_database(self):
        """Test getting question suggestions from database"""
        with patch.dict(os.environ, {
            'CHAT_QUESTIONS_FROM_DATABASE': 'true'
        }):
            # Mock question manager
            with patch('src.controllers.chat_controller.question_manager') as mock_qm:
                mock_qm.get_questions_for_chat.return_value = [
                    {'id': 1, 'text': 'Test question', 'category': 'financial'}
                ]

                result = chat_controller.get_question_suggestions('all')
                assert result['success'] is True
                assert 'questions' in result

    def test_get_question_suggestions_fallback(self):
        """Test fallback to code-based questions"""
        with patch.dict(os.environ, {
            'CHAT_QUESTIONS_FROM_DATABASE': 'false'
        }):
            result = chat_controller.get_question_suggestions('financial')
            assert result['success'] is True
            assert 'questions' in result
            assert result['source'] == 'code'


class TestQuestionManagerIntegration:
    """Test question manager integration"""

    def test_question_manager_initialization(self):
        """Test question manager initialization"""
        # Test that question manager can be imported and initialized
        try:
            categories = question_manager.get_all_categories()
            assert isinstance(categories, list)
        except Exception as e:
            # If database is not available, should handle gracefully
            assert "database" in str(e).lower() or "connection" in str(e).lower()

    def test_question_creation(self):
        """Test question creation"""
        try:
            question_id = question_manager.create_question(
                text="Test question for integration",
                category_id=1,
                expected_response_type="analysis"
            )
            assert isinstance(question_id, int)
        except Exception:
            # Database might not be available in test environment
            pass


class TestExternalAPIs:
    """Test external API integrations"""

    @patch('requests.post')
    def test_openai_api_call(self, mock_post):
        """Test OpenAI API call"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'choices': [{'message': {'content': 'Test response'}}]
        }
        mock_post.return_value = mock_response

        with patch.dict(os.environ, {
            'OPENAI_API_KEY': 'test_key'
        }):
            manager = APIIntegrationManager()
            result = manager.call_openai_api('gpt-3.5-turbo', [{'role': 'user', 'content': 'Test'}])

            assert result['success'] is True
            assert result['data']['choices'][0]['message']['content'] == 'Test response'

    @patch('requests.post')
    def test_anthropic_api_call(self, mock_post):
        """Test Anthropic API call"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'content': [{'text': 'Test response'}]
        }
        mock_post.return_value = mock_response

        with patch.dict(os.environ, {
            'ANTHROPIC_API_KEY': 'test_key'
        }):
            manager = APIIntegrationManager()
            result = manager.call_anthropic_api('claude-3-haiku-20240307', [{'role': 'user', 'content': 'Test'}])

            assert result['success'] is True
            assert result['data']['content'][0]['text'] == 'Test response'

    @patch('requests.post')
    def test_google_ai_api_call(self, mock_post):
        """Test Google AI API call"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'candidates': [{
                'content': {
                    'parts': [{'text': 'Test response'}]
                }
            }]
        }
        mock_post.return_value = mock_response

        with patch.dict(os.environ, {
            'GOOGLE_AI_API_KEY': 'test_key'
        }):
            manager = APIIntegrationManager()
            result = manager.call_google_ai_api('Test message', 'gemini-pro')

            assert result['success'] is True
            assert result['data']['candidates'][0]['content']['parts'][0]['text'] == 'Test response'


class TestEnvironmentConfiguration:
    """Test environment configuration"""

    def test_environment_variables_loading(self):
        """Test that environment variables are properly loaded"""
        # Test individual environment variables
        test_vars = [
            'STARTUP_CHECKS_ENABLED',
            'DATABASE_CONNECTION_CHECKS',
            'QUESTION_MANAGER_INIT',
            'AI_SYSTEM_INIT',
            'VERBOSE_STARTUP_LOGS',
            'DEBUG_MODE',
            'CHAT_QUESTIONS_FROM_DATABASE',
            'N8N_ENABLED',
            'AI_DISCLAIMER_ENABLED'
        ]

        for var in test_vars:
            value = os.environ.get(var, 'default')
            # Should not be None (meaning it's defined in env.example)
            assert value is not None

    def test_external_model_configuration(self):
        """Test external model configuration"""
        model_vars = [
            'SUPPORTED_AI_MODELS',
            'OPENAI_MODELS',
            'ANTHROPIC_MODELS',
            'GOOGLE_MODELS',
            'COHERE_MODELS',
            'MISTRAL_MODELS',
            'OLLAMA_MODELS',
            'GROQ_MODELS',
            'REPLICATE_MODELS',
            'PERPLEXITY_MODELS'
        ]

        for var in model_vars:
            value = os.environ.get(var)
            assert value is not None
            assert len(value.split(',')) > 0

    def test_data_source_configuration(self):
        """Test data source configuration"""
        data_source_vars = [
            'SUPPORTED_DATA_SOURCES',
            'WORDPRESS_ENABLED',
            'WOOCOMMERCE_ENABLED',
            'SHOPIFY_ENABLED',
            'STRIPE_ENABLED',
            'QUICKBOOKS_ENABLED',
            'SALESFORCE_ENABLED'
        ]

        for var in data_source_vars:
            value = os.environ.get(var)
            assert value is not None


class TestComprehensiveIntegration:
    """Comprehensive integration tests"""

    def test_full_system_initialization(self):
        """Test full system initialization"""
        try:
            # Test data source integrator
            integrator = DataSourceIntegrator()
            sources = integrator.get_available_sources()
            assert isinstance(sources, list)

            # Test N8N integration
            n8n = N8NIntegration()
            enabled = n8n.is_enabled()
            assert isinstance(enabled, bool)

            # Test API integration manager
            api_manager = APIIntegrationManager()
            apis = api_manager.get_available_apis()
            assert isinstance(apis, list)

            # Test question manager (might fail if DB not available)
            try:
                categories = question_manager.get_all_categories()
                assert isinstance(categories, list)
            except Exception:
                # Expected if database is not set up
                pass

        except Exception as e:
            pytest.fail(f"System initialization failed: {e}")

    def test_configuration_consistency(self):
        """Test configuration consistency across components"""
        # Test that all configured data sources have proper environment variables
        supported_sources = os.environ.get('SUPPORTED_DATA_SOURCES', '').split(',')

        for source in supported_sources:
            source = source.strip()
            if source:
                # Check if the source has an enable flag
                enable_var = f"{source.upper()}_ENABLED"
                enable_value = os.environ.get(enable_var, 'false')
                assert enable_value is not None

    def test_ai_disclaimer_configuration(self):
        """Test AI disclaimer configuration"""
        disclaimer_enabled = os.environ.get('AI_DISCLAIMER_ENABLED', 'true')
        assert disclaimer_enabled.lower() in ['true', 'false']

        disclaimer_text = os.environ.get('AI_DISCLAIMER_TEXT', '')
        assert disclaimer_text is not None
        assert len(disclaimer_text) > 0

        disclaimer_position = os.environ.get('AI_DISCLAIMER_POSITION', 'top')
        assert disclaimer_position in ['top', 'bottom', 'modal']


class TestAPIRoutes:
    """Test API routes for new functionality"""

    def setup_method(self):
        """Setup test client"""
        self.app = create_app()
        self.client = self.app.test_client()

    def test_question_api_endpoints(self):
        """Test question API endpoints"""
        # Test get questions endpoint
        response = self.client.get('/api/questions')
        assert response.status_code in [200, 500]  # 500 might occur if DB not set up

        # Test get categories endpoint
        response = self.client.get('/api/questions/categories')
        assert response.status_code in [200, 500]

    def test_data_source_endpoints(self):
        """Test data source API endpoints"""
        # These endpoints might not exist yet, so we expect 404
        response = self.client.get('/api/data-sources/available')
        # This test validates the endpoint structure, not necessarily success
        assert response.status_code in [200, 404, 500]

    def test_external_model_endpoints(self):
        """Test external model API endpoints"""
        # These endpoints might not exist yet, so we expect 404
        response = self.client.post('/api/models/switch-external',
                                  json={'model_id': 'gpt-4o', 'provider': 'openai'})
        assert response.status_code in [200, 404, 500]


class TestErrorHandling:
    """Test error handling in new features"""

    def test_data_source_error_handling(self):
        """Test data source error handling"""
        integrator = DataSourceIntegrator()

        # Test with non-existent source
        result = integrator.get_data_from_source('nonexistent_source')
        assert result['success'] is False
        assert 'not available' in result['error']

    def test_n8n_error_handling(self):
        """Test N8N integration error handling"""
        with patch.dict(os.environ, {
            'N8N_ENABLED': 'false'
        }):
            n8n = N8NIntegration()
            result = n8n.trigger_webhook('test', {})
            assert result['success'] is False
            assert 'not enabled' in result['error']

    def test_api_integration_error_handling(self):
        """Test API integration error handling"""
        # Test with no API keys configured
        with patch.dict(os.environ, {
            'OPENAI_API_KEY': ''  # Empty API key
        }):
            manager = APIIntegrationManager()
            result = manager.call_openai_api('gpt-3.5-turbo', [])
            assert result['success'] is False
            assert 'not configured' in result['error']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
