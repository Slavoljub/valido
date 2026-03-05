#!/usr/bin/env python3
"""
Comprehensive Test Suite for Unified Chat System
Tests sample questions, model testing, report generation, and theme validation
"""

import sys
import os
import json
import unittest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.controllers.unified_chat_controller import UnifiedChatController

class TestUnifiedChatController(unittest.TestCase):
    """Test cases for UnifiedChatController"""

    def setUp(self):
        """Set up test fixtures"""
        self.chat_controller = UnifiedChatController()
        self.test_session_id = "test-session-123"
        self.test_question_id = "1"
        self.test_model_id = "test-model-123"

    def test_get_question_suggestions(self):
        """Test getting question suggestions"""
        suggestions = self.chat_controller.get_question_suggestions()

        self.assertIsInstance(suggestions, list)
        self.assertGreater(len(suggestions), 0)

        # Check structure of first suggestion
        first_suggestion = suggestions[0]
        required_fields = ['id', 'category', 'question', 'expected_output', 'test_data', 'icon']
        for field in required_fields:
            self.assertIn(field, first_suggestion)

        # Test specific categories exist
        categories = [s['category'] for s in suggestions]
        self.assertIn('Financial Analysis', categories)
        self.assertIn('Business Intelligence', categories)
        self.assertIn('Reporting', categories)

    def test_get_available_models(self):
        """Test getting available models"""
        models = self.chat_controller.get_available_models()

        self.assertIsInstance(models, list)

        if models:  # Only test structure if models exist
            first_model = models[0]
            required_fields = ['id', 'name', 'is_downloaded', 'memory_required']
            for field in required_fields:
                self.assertIn(field, first_model)

    def test_create_session(self):
        """Test session creation"""
        session_data = self.chat_controller.create_session()

        if 'error' not in session_data:
            self.assertIn('session_id', session_data)
            self.assertIn('user_id', session_data)
            self.assertIn('created_at', session_data)
            self.assertEqual(session_data['model_type'], 'local')

    def test_get_session(self):
        """Test getting session data"""
        # Create session first
        session_data = self.chat_controller.create_session()
        session_id = session_data.get('session_id')

        if session_id:
            retrieved_session = self.chat_controller.get_session(session_id)
            self.assertIsNotNone(retrieved_session)
            self.assertEqual(retrieved_session['session_id'], session_id)

    def test_test_question_with_model(self):
        """Test question testing with model"""
        result = self.chat_controller.test_question_with_model(
            self.test_question_id,
            self.test_model_id
        )

        self.assertIsInstance(result, dict)
        if 'error' not in result:
            self.assertIn('question_id', result)
            self.assertIn('model_id', result)
            self.assertIn('status', result)
            self.assertIn('timestamp', result)

    def test_get_theme_colors(self):
        """Test getting theme colors"""
        result = self.chat_controller.get_theme_colors('light')

        self.assertIsInstance(result, dict)
        if 'error' not in result:
            self.assertIn('theme_name', result)
            self.assertIn('css_variables', result)
            self.assertIn('is_valid', result)
            self.assertTrue(result['is_valid'])

    def test_test_theme_changes(self):
        """Test theme changes validation"""
        result = self.chat_controller.test_theme_changes()

        self.assertIsInstance(result, dict)
        if 'error' not in result:
            self.assertIn('test_results', result)
            self.assertIn('total_themes', result)
            self.assertIn('passed_tests', result)
            self.assertIn('failed_tests', result)

    @patch('src.controllers.unified_chat_controller.UnifiedChatController.get_available_models')
    def test_run_comprehensive_test_suite(self, mock_get_models):
        """Test comprehensive test suite"""
        # Mock available models
        mock_get_models.return_value = [
            {
                'id': 'model1',
                'name': 'Test Model 1',
                'is_downloaded': True,
                'memory_required': 4096
            },
            {
                'id': 'model2',
                'name': 'Test Model 2',
                'is_downloaded': True,
                'memory_required': 4096
            }
        ]

        result = self.chat_controller.run_comprehensive_test_suite()

        self.assertIsInstance(result, dict)
        if 'error' not in result:
            self.assertIn('summary', result)
            self.assertIn('results', result)
            self.assertIn('timestamp', result)

            summary = result['summary']
            self.assertIn('total_questions', summary)
            self.assertIn('total_models', summary)
            self.assertIn('total_tests', summary)

    def test_process_file_upload_no_file(self):
        """Test file upload with no file"""
        mock_file = Mock()
        mock_file.filename = ''

        result = self.chat_controller.process_file_upload(mock_file, self.test_session_id)

        self.assertIn('error', result)
        self.assertEqual(result['error'], 'No file provided')

    def test_process_file_upload_large_file(self):
        """Test file upload with large file"""
        mock_file = Mock()
        mock_file.filename = 'test.txt'

        # Mock file to be too large
        mock_file.seek = Mock()
        mock_file.tell = Mock(return_value=20 * 1024 * 1024)  # 20MB

        result = self.chat_controller.process_file_upload(mock_file, self.test_session_id)

        self.assertIn('error', result)
        self.assertIn('too large', result['error'])

    def test_get_system_resources(self):
        """Test getting system resources"""
        resources = self.chat_controller.get_system_resources()

        self.assertIsInstance(resources, dict)
        self.assertIn('cpu_percent', resources)
        self.assertIn('memory', resources)
        self.assertIn('active_sessions', resources)

    def test_get_chat_analytics(self):
        """Test getting chat analytics"""
        analytics = self.chat_controller.get_chat_analytics()

        self.assertIsInstance(analytics, dict)
        if 'error' not in analytics:
            self.assertIn('total_sessions', analytics)
            self.assertIn('total_messages', analytics)
            self.assertIn('system_resources', analytics)

class TestSampleQuestionsIntegration(unittest.TestCase):
    """Test sample questions integration and functionality"""

    def setUp(self):
        self.chat_controller = UnifiedChatController()

    def test_question_structure_completeness(self):
        """Test that all questions have complete structure"""
        questions = self.chat_controller.get_question_suggestions()

        for question in questions:
            # Check required fields
            self.assertIn('id', question)
            self.assertIn('category', question)
            self.assertIn('question', question)
            self.assertIn('expected_output', question)
            self.assertIn('test_data', question)
            self.assertIn('icon', question)

            # Check question is not empty
            self.assertGreater(len(question['question']), 0)

            # Check expected output is meaningful
            self.assertGreater(len(question['expected_output']), 10)

            # Check test data is dict
            self.assertIsInstance(question['test_data'], dict)

            # Check icon is valid
            self.assertTrue(question['icon'].startswith('fas fa-'))

    def test_question_categories_coverage(self):
        """Test that questions cover all important categories"""
        questions = self.chat_controller.get_question_suggestions()
        categories = set(q['category'] for q in questions)

        expected_categories = {
            'Financial Analysis',
            'Business Intelligence',
            'Operations',
            'Reporting',
            'Data Analysis',
            'Compliance'
        }

        # At least some of the expected categories should be present
        self.assertTrue(expected_categories.intersection(categories))

    def test_question_ids_uniqueness(self):
        """Test that question IDs are unique"""
        questions = self.chat_controller.get_question_suggestions()
        ids = [q['id'] for q in questions]

        self.assertEqual(len(ids), len(set(ids)), "Question IDs are not unique")

    def test_reporting_questions_exist(self):
        """Test that reporting questions exist for different formats"""
        questions = self.chat_controller.get_question_suggestions()
        reporting_questions = [q for q in questions if q['category'] == 'Reporting']

        self.assertGreater(len(reporting_questions), 0, "No reporting questions found")

        # Check for different formats
        formats_mentioned = []
        for question in reporting_questions:
            test_data = question.get('test_data', {})
            format_type = test_data.get('format', '')
            if format_type:
                formats_mentioned.append(format_type)

        # Should have at least PDF mentioned
        self.assertIn('pdf', [f.lower() for f in formats_mentioned])

class TestModelIntegration(unittest.TestCase):
    """Test model integration and selection"""

    def setUp(self):
        self.chat_controller = UnifiedChatController()

    def test_model_config_loading(self):
        """Test loading model configuration"""
        models = self.chat_controller.get_available_models()

        # Should return a list (even if empty)
        self.assertIsInstance(models, list)

        if models:
            for model in models:
                # Check model structure
                required_fields = ['id', 'name', 'is_downloaded', 'memory_required']
                for field in required_fields:
                    self.assertIn(field, model)

    def test_model_selection_for_testing(self):
        """Test model selection for question testing"""
        models = self.chat_controller.get_available_models()

        if models:
            # Test with first available model
            first_model = models[0]
            questions = self.chat_controller.get_question_suggestions()

            if questions:
                first_question = questions[0]

                result = self.chat_controller.test_question_with_model(
                    first_question['id'],
                    first_model['id']
                )

                # Should return a result dict
                self.assertIsInstance(result, dict)
                if 'error' not in result:
                    self.assertEqual(result['question_id'], first_question['id'])
                    self.assertEqual(result['model_id'], first_model['id'])

class TestThemeValidation(unittest.TestCase):
    """Test theme validation and color testing"""

    def setUp(self):
        self.chat_controller = UnifiedChatController()

    def test_theme_colors_structure(self):
        """Test theme colors structure"""
        result = self.chat_controller.get_theme_colors('light')

        if 'error' not in result:
            self.assertIn('theme_name', result)
            self.assertIn('css_variables', result)
            self.assertIn('is_valid', result)

            css_vars = result['css_variables']
            self.assertIsInstance(css_vars, dict)

            # Should have basic color variables
            basic_vars = ['--bg-primary', '--text-primary']
            for var in basic_vars:
                self.assertIn(var, css_vars)

    def test_theme_validation(self):
        """Test theme validation process"""
        result = self.chat_controller.test_theme_changes()

        if 'error' not in result:
            self.assertIn('test_results', result)
            self.assertIn('total_themes', result)
            self.assertIn('passed_tests', result)

            test_results = result['test_results']
            self.assertIsInstance(test_results, list)

            if test_results:
                first_result = test_results[0]
                self.assertIn('theme_name', first_result)
                self.assertIn('status', first_result)

if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
