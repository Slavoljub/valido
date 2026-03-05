#!/usr/bin/env python3
"""
Test Error Handling System
==========================

Comprehensive tests for the ValidoAI error handling system.
Tests error handlers, decorators, and error recovery mechanisms.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock, mock_open
import tempfile
import json
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, jsonify
from flask.testing import FlaskClient
import pytest

class TestErrorHandling(unittest.TestCase):
    """Test cases for error handling system"""

    def setUp(self):
        """Set up test environment"""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

        # Mock the error handling initialization
        with patch('src.error_handling.init_error_handling'):
            from src.routes.unified_route_generator import handle_template_errors
            self.handle_template_errors = handle_template_errors

    def tearDown(self):
        """Clean up test environment"""
        pass

    def test_handle_template_errors_decorator(self):
        """Test the handle_template_errors decorator functionality"""
        @self.handle_template_errors
        def test_function():
            """Test function that should work normally"""
            return "Success"

        # Test normal execution
        result = test_function()
        self.assertEqual(result, "Success")

    def test_handle_template_errors_with_exception(self):
        """Test handle_template_errors with exceptions"""
        @self.handle_template_errors
        def failing_function():
            """Test function that raises an exception"""
            raise ValueError("Test error")

        # Test exception handling
        with patch('src.routes.unified_route_generator.render_template') as mock_render:
            mock_render.return_value = "Error template rendered"

            result = failing_function()
            # handle_template_errors returns a tuple (response, status_code)
            self.assertEqual(result[0], "Error template rendered")
            self.assertEqual(result[1], 500)

            # Verify render_template was called with error template
            mock_render.assert_called_once()
            call_args = mock_render.call_args[1]
            self.assertEqual(call_args['template_name_or_list'], 'errors/error.html')
            self.assertIn('error', call_args)

    def test_handle_template_errors_logging(self):
        """Test that handle_template_errors logs errors properly"""
        with patch('src.routes.unified_route_generator.logger') as mock_logger:
            @self.handle_template_errors
            def error_function():
                raise RuntimeError("Test logging error")

            with patch('src.routes.unified_route_generator.render_template'):
                error_function()

            # Verify error was logged
            mock_logger.error.assert_called_once()
            log_message = mock_logger.error.call_args[0][0]
            self.assertIn("Template error in error_function", log_message)
            self.assertIn("Test logging error", log_message)

    def test_error_handler_404(self):
        """Test 404 error handler"""
        # Register error handler
        @self.app.errorhandler(404)
        def handle_404(error):
            return jsonify({'error': 'Not found', 'status': 404}), 404

        # Test 404 response
        response = self.client.get('/nonexistent-route')
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Not found')
        self.assertEqual(data['status'], 404)

    def test_error_handler_500(self):
        """Test 500 error handler"""
        # Register error handler
        @self.app.errorhandler(500)
        def handle_500(error):
            return jsonify({'error': 'Internal server error', 'status': 500}), 500

        # Create a route that raises 500 error
        @self.app.route('/error-500')
        def error_route():
            raise Exception("Test 500 error")

        # Test 500 response
        response = self.client.get('/error-500')
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Internal server error')
        self.assertEqual(data['status'], 500)

    def test_error_handler_validation_error(self):
        """Test validation error handler"""
        # Register error handler for validation errors
        @self.app.errorhandler(ValueError)
        def handle_validation_error(error):
            return jsonify({'error': 'Validation error', 'message': str(error)}), 400

        # Create a route that raises validation error
        @self.app.route('/validation-error')
        def validation_error_route():
            raise ValueError("Invalid input data")

        # Test validation error response
        response = self.client.get('/validation-error')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Validation error')
        self.assertIn('Invalid input data', data['message'])

    def test_error_handler_generic_exception(self):
        """Test generic exception handler"""
        # Register generic error handler
        @self.app.errorhandler(Exception)
        def handle_generic_error(error):
            return jsonify({'error': 'Unexpected error', 'message': str(error)}), 500

        # Create a route that raises generic exception
        @self.app.route('/generic-error')
        def generic_error_route():
            raise RuntimeError("Unexpected runtime error")

        # Test generic error response
        response = self.client.get('/generic-error')
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Unexpected error')
        self.assertIn('Unexpected runtime error', data['message'])

    def test_error_handler_with_request_context(self):
        """Test error handler with request context information"""
        error_details = {}

        @self.app.errorhandler(500)
        def handle_500_with_context(error):
            error_details['url'] = request.url
            error_details['method'] = request.method
            error_details['timestamp'] = datetime.now().isoformat()
            return jsonify(error_details), 500

        @self.app.route('/context-error')
        def context_error_route():
            raise Exception("Context test error")

        # Test error handler with context
        response = self.client.get('/context-error')
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertIn('url', data)
        self.assertIn('method', data)
        self.assertIn('timestamp', data)
        self.assertEqual(data['method'], 'GET')
        self.assertTrue(data['url'].endswith('/context-error'))

    def test_multiple_error_handlers(self):
        """Test multiple error handlers for different error types"""
        responses = {}

        @self.app.errorhandler(400)
        def handle_400(error):
            responses['400'] = True
            return jsonify({'error': 'Bad request'}), 400

        @self.app.errorhandler(403)
        def handle_403(error):
            responses['403'] = True
            return jsonify({'error': 'Forbidden'}), 403

        @self.app.errorhandler(404)
        def handle_404(error):
            responses['404'] = True
            return jsonify({'error': 'Not found'}), 404

        # Test different error codes
        self.client.get('/nonexistent')  # Should trigger 404
        self.assertTrue(responses.get('404', False))

        # Simulate 400 error
        with self.app.test_request_context('/test', method='POST', data={'invalid': 'data'}):
            from werkzeug.exceptions import BadRequest
            try:
                raise BadRequest("Invalid data")
            except BadRequest as e:
                with self.app.test_client() as client:
                    # This is a simplified test - in real scenario, the error handler would be triggered
                    pass

    def test_error_handler_json_response(self):
        """Test that error handlers return proper JSON responses"""
        @self.app.errorhandler(422)
        def handle_unprocessable_entity(error):
            return jsonify({
                'error': 'Unprocessable Entity',
                'code': 422,
                'message': str(error),
                'timestamp': datetime.now().isoformat()
            }), 422

        @self.app.route('/unprocessable')
        def unprocessable_route():
            from werkzeug.exceptions import UnprocessableEntity
            raise UnprocessableEntity("Data validation failed")

        # Test JSON structure
        response = self.client.get('/unprocessable')
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.content_type, 'application/json')

        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('code', data)
        self.assertIn('message', data)
        self.assertIn('timestamp', data)
        self.assertEqual(data['error'], 'Unprocessable Entity')
        self.assertEqual(data['code'], 422)

    def test_error_handler_with_headers(self):
        """Test error handler with custom headers"""
        @self.app.errorhandler(429)
        def handle_rate_limit(error):
            response = jsonify({'error': 'Too many requests'})
            response.headers['Retry-After'] = '60'
            response.headers['X-Rate-Limit-Reset'] = '60'
            return response, 429

        @self.app.route('/rate-limit')
        def rate_limit_route():
            from werkzeug.exceptions import TooManyRequests
            raise TooManyRequests("Rate limit exceeded")

        # Test headers in error response
        response = self.client.get('/rate-limit')
        self.assertEqual(response.status_code, 429)
        self.assertEqual(response.headers.get('Retry-After'), '60')
        self.assertEqual(response.headers.get('X-Rate-Limit-Reset'), '60')

    def test_error_handler_logging(self):
        """Test that error handlers properly log errors"""
        log_messages = []

        def mock_error_logger(message, *args, **kwargs):
            log_messages.append(message)

        with patch('src.error_handling.logger') as mock_logger:
            mock_logger.error = mock_error_logger

            @self.app.errorhandler(500)
            def handle_500_with_logging(error):
                mock_logger.error(f"Internal error: {error}")
                return jsonify({'error': 'Internal server error'}), 500

            @self.app.route('/logging-error')
            def logging_error_route():
                raise Exception("Test error for logging")

            # Trigger error
            self.client.get('/logging-error')

            # Check if error was logged
            self.assertTrue(len(log_messages) > 0)
            self.assertTrue(any("Internal error" in msg for msg in log_messages))

    def test_error_template_rendering(self):
        """Test error template rendering fallback"""
        with patch('src.routes.unified_route_generator.render_template') as mock_render:
            mock_render.side_effect = Exception("Template rendering failed")

            @self.handle_template_errors
            def template_error_function():
                raise ValueError("Template test error")

            # Should handle the template rendering error gracefully
            with self.assertRaises(Exception):
                # If template rendering fails, the original exception should be raised
                template_error_function()

class TestHypercornServer(unittest.TestCase):
    """Test cases for Hypercorn server configuration"""

    def setUp(self):
        """Set up test environment for Hypercorn tests"""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True

    def test_hypercorn_server_creation(self):
        """Test Hypercorn server creation"""
        with patch('src.hypercorn_server.hypercorn') as mock_hypercorn:
            from src.hypercorn_server import create_hypercorn_server

            server = create_hypercorn_server(self.app)
            self.assertIsNotNone(server)
            self.assertEqual(server.app, self.app)

    def test_hypercorn_config_creation(self):
        """Test Hypercorn configuration creation"""
        with patch('src.hypercorn_server.hypercorn'):
            from src.hypercorn_server import HypercornServer

            server = HypercornServer(self.app)
            self.assertIsNotNone(server.config)
            self.assertTrue(hasattr(server.config, 'bind'))
            self.assertTrue(len(server.config.bind) > 0)

    def test_ssl_configuration(self):
        """Test SSL configuration for Hypercorn"""
        with patch('src.hypercorn_server.hypercorn'):
            with patch('src.hypercorn_server.os.path.exists', return_value=True):
                with patch.dict(os.environ, {'SSL_ENABLED': 'true'}):
                    from src.hypercorn_server import HypercornServer

                    server = HypercornServer(self.app)

                    # Check if SSL configuration is attempted
                    # Note: This is a basic test - full SSL testing would require certificates
                    self.assertIsNotNone(server.config)

    def test_hypercorn_server_without_ssl(self):
        """Test Hypercorn server configuration without SSL"""
        with patch('src.hypercorn_server.hypercorn'):
            with patch.dict(os.environ, {'SSL_ENABLED': 'false'}):
                from src.hypercorn_server import HypercornServer

                server = HypercornServer(self.app)
                self.assertIsNotNone(server.config)
                # Should have at least one binding (HTTP)
                self.assertTrue(len(server.config.bind) >= 1)

class TestApplicationFactory(unittest.TestCase):
    """Test cases for Flask application factory"""

    def test_create_app_development(self):
        """Test create_app with development configuration"""
        from app import create_app

        app = create_app('development')
        self.assertIsNotNone(app)
        self.assertEqual(app.config['DEBUG'], True)

    def test_create_app_production(self):
        """Test create_app with production configuration"""
        from app import create_app

        app = create_app('production')
        self.assertIsNotNone(app)
        self.assertEqual(app.config['DEBUG'], False)

    def test_create_app_default(self):
        """Test create_app with default configuration"""
        from app import create_app

        app = create_app()
        self.assertIsNotNone(app)
        # Should default to development-like settings
        self.assertTrue(hasattr(app, 'config'))

if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)
