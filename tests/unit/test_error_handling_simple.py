"""
Simplified Unit Tests for Error Handling Utilities
================================================
Test the DRY error handling functions with minimal dependencies
"""

import pytest
import logging
from unittest.mock import Mock, patch
from flask import Flask, jsonify
from src.core.error_handling import (
    handle_controller_import_error,
    handle_generic_import_error,
    create_error_response
)


class TestHandleControllerImportErrorSimple:
    """Test the handle_controller_import_error function with simplified approach"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.error = ImportError("No module named 'test_controller'")
        
    def test_handle_controller_import_error_api_route(self):
        """Test handling ImportError for API routes (JSON response)"""
        with self.app.app_context():
            result = handle_controller_import_error(
                controller_name="TestController",
                error=self.error,
                error_title="Test Controller Unavailable",
                error_message_prefix="Test controller not available",
                is_api_route=True
            )
            
            # Should return a tuple (response, status_code)
            assert isinstance(result, tuple)
            assert len(result) == 2
            assert result[1] == 500
            
            # The response should be a Response object with JSON
            assert hasattr(result[0], 'json')
            json_data = result[0].get_json()
            assert json_data['error'] == "Test controller not available"
    
    def test_handle_controller_import_error_default_values(self):
        """Test handling ImportError with default values for API route"""
        with self.app.app_context():
            result = handle_controller_import_error(
                controller_name="TestController",
                error=self.error,
                is_api_route=True
            )
            
            # Should use default title and message
            assert isinstance(result, tuple)
            assert result[1] == 500
            json_data = result[0].get_json()
            assert json_data['error'] == "The testcontroller is not available."
    
    def test_handle_controller_import_error_custom_logger(self):
        """Test handling ImportError with custom logger"""
        custom_logger = Mock(spec=logging.Logger)
        
        with self.app.app_context():
            handle_controller_import_error(
                controller_name="TestController",
                error=self.error,
                is_api_route=True,
                custom_logger=custom_logger
            )
            
            # Should call the custom logger
            custom_logger.error.assert_called_once()
            assert "TestController not available" in custom_logger.error.call_args[0][0]


class TestHandleGenericImportError:
    """Test the handle_generic_import_error function"""
    
    def test_handle_generic_import_error_with_fallback(self):
        """Test handling generic ImportError with fallback response"""
        error = ImportError("No module named 'test_module'")
        fallback_response = {"status": "fallback"}
        
        result = handle_generic_import_error(
            module_name="test_module",
            error=error,
            fallback_response=fallback_response
        )
        
        assert result == fallback_response
    
    def test_handle_generic_import_error_without_fallback(self):
        """Test handling generic ImportError without fallback"""
        error = ImportError("No module named 'test_module'")
        
        result = handle_generic_import_error(
            module_name="test_module",
            error=error
        )
        
        assert result is None
    
    def test_handle_generic_import_error_custom_logger(self):
        """Test handling generic ImportError with custom logger"""
        error = ImportError("No module named 'test_module'")
        custom_logger = Mock(spec=logging.Logger)
        
        handle_generic_import_error(
            module_name="test_module",
            error=error,
            custom_logger=custom_logger
        )
        
        # Should call the custom logger
        custom_logger.warning.assert_called_once()
        assert "test_module not available" in custom_logger.warning.call_args[0][0]


class TestCreateErrorResponse:
    """Test the create_error_response function"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
    
    def test_create_error_response_api_route(self):
        """Test creating error response for API routes"""
        with self.app.app_context():
            result = create_error_response(
                error_code=400,
                error_title="Bad Request",
                error_message="Invalid request data",
                stack_trace="Traceback...",
                is_api_route=True
            )
            
            # Should return a tuple (response, status_code)
            assert isinstance(result, tuple)
            assert len(result) == 2
            assert result[1] == 400
            
            # The response should be a Response object with JSON
            assert hasattr(result[0], 'json')
            json_data = result[0].get_json()
            assert json_data['error'] == "Bad Request"
            assert json_data['message'] == "Invalid request data"
            assert json_data['stack_trace'] == "Traceback..."
    
    def test_create_error_response_api_route_no_stack_trace(self):
        """Test creating error response for API routes without stack trace"""
        with self.app.app_context():
            result = create_error_response(
                error_code=500,
                error_title="Internal Server Error",
                error_message="An unexpected error occurred",
                is_api_route=True
            )
            
            # Should return a tuple (response, status_code)
            assert isinstance(result, tuple)
            assert len(result) == 2
            assert result[1] == 500
            
            # The response should be a Response object with JSON
            assert hasattr(result[0], 'json')
            json_data = result[0].get_json()
            assert json_data['error'] == "Internal Server Error"
            assert json_data['message'] == "An unexpected error occurred"
            assert 'stack_trace' not in json_data


class TestErrorHandlingIntegration:
    """Integration tests for error handling with Flask app"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        
        @self.app.route('/test-api-error')
        def test_api_error():
            try:
                import non_existent_module
            except ImportError as e:
                return handle_controller_import_error(
                    controller_name="NonExistentController",
                    error=e,
                    is_api_route=True
                )
    
    def test_error_handling_in_flask_api_route(self):
        """Test error handling within a Flask API route"""
        with self.app.test_client() as client:
            response = client.get('/test-api-error')
            
            assert response.status_code == 500
            json_data = response.get_json()
            assert json_data['error'] == "The nonexistentcontroller is not available."


class TestDRYPrinciple:
    """Test that the DRY principle is properly implemented"""
    
    def test_consistent_error_handling(self):
        """Test that error handling is consistent across different scenarios"""
        app = Flask(__name__)
        app.config['TESTING'] = True
        error = ImportError("Test error")
        
        with app.app_context():
            # Test different controller names
            result1 = handle_controller_import_error(
                controller_name="Controller1",
                error=error,
                is_api_route=True
            )
            
            result2 = handle_controller_import_error(
                controller_name="Controller2",
                error=error,
                is_api_route=True
            )
            
            # Both should have the same structure
            assert isinstance(result1, tuple)
            assert isinstance(result2, tuple)
            assert result1[1] == result2[1] == 500
            
            json1 = result1[0].get_json()
            json2 = result2[0].get_json()
            
            # Both should have 'error' key
            assert 'error' in json1
            assert 'error' in json2
            
            # But different error messages
            assert json1['error'] != json2['error']


if __name__ == '__main__':
    pytest.main([__file__])
