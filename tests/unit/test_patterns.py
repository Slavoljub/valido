#!/usr/bin/env python3
"""
Unit Tests for Design Patterns
Tests all implemented design patterns
"""

import unittest
import sys
import os
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.patterns.singleton import DatabaseConnection, LLMModelManager, ConfigManager
from src.patterns.factory import LLMModelFactory, InferenceStrategyFactory
from src.patterns.strategy import CPUStrategy, GPUStrategy, QuantizedStrategy, StrategyContext
from src.patterns.pipeline import Pipeline, PipelineBuilder, TokenizationStep, PreprocessingStep
from src.patterns.decorator import BaseLLMInference, LoggingDecorator, CachingDecorator

class TestSingletonPattern(unittest.TestCase):
    """Test Singleton pattern implementation"""
    
    def setUp(self):
        """Set up test data"""
        self.report_data = {
            "timestamp": datetime.now().isoformat(),
            "test_type": "unit_patterns",
            "results": []
        }
    
    def tearDown(self):
        """Clean up after tests"""
        failed_tests = [result for result in self.report_data["results"] if not result["passed"]]
        if failed_tests:
            self._generate_html_report()
    
    def _record_test_result(self, test_name: str, passed: bool, error: str = None):
        """Record test result"""
        self.report_data["results"].append({
            "test_name": test_name,
            "passed": passed,
            "error": error,
            "timestamp": datetime.now().isoformat()
        })
    
    def _generate_html_report(self):
        """Generate HTML report for failed tests"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = f"tests/reports/{timestamp}-unit_patterns.html"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Unit Pattern Tests Report - {timestamp}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f0f0f0; padding: 10px; border-radius: 5px; }}
                .test-result {{ margin: 10px 0; padding: 10px; border-radius: 5px; }}
                .passed {{ background-color: #d4edda; border: 1px solid #c3e6cb; }}
                .failed {{ background-color: #f8d7da; border: 1px solid #f5c6cb; }}
                .error {{ color: #721c24; font-family: monospace; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Unit Pattern Tests Report</h1>
                <p>Generated: {self.report_data["timestamp"]}</p>
                <p>Test Type: {self.report_data["test_type"]}</p>
            </div>
        """
        
        for result in self.report_data["results"]:
            status_class = "passed" if result["passed"] else "failed"
            status_text = "PASSED" if result["passed"] else "FAILED"
            
            html_content += f"""
            <div class="test-result {status_class}">
                <h3>{result["test_name"]} - {status_text}</h3>
                <p>Timestamp: {result["timestamp"]}</p>
                {f'<div class="error">Error: {result["error"]}</div>' if result["error"] else ''}
            </div>
            """
        
        html_content += """
        </body>
        </html>
        """
        
        with open(report_path, 'w') as f:
            f.write(html_content)
    
    def test_database_connection_singleton(self):
        """Test DatabaseConnection singleton"""
        try:
            # Create two instances
            db1 = DatabaseConnection()
            db2 = DatabaseConnection()
            
            # They should be the same instance
            self.assertIs(db1, db2)
            
            # Test connection functionality
            conn1 = db1.get_connection("test.db")
            conn2 = db2.get_connection("test.db")
            
            # Should return the same connection
            self.assertIs(conn1, conn2)
            
            self._record_test_result("test_database_connection_singleton", True)
            
        except Exception as e:
            self._record_test_result("test_database_connection_singleton", False, str(e))
            raise
    
    def test_llm_model_manager_singleton(self):
        """Test LLMModelManager singleton"""
        try:
            # Create two instances
            manager1 = LLMModelManager()
            manager2 = LLMModelManager()
            
            # They should be the same instance
            self.assertIs(manager1, manager2)
            
            # Test model loading
            config = {"size": "7B", "type": "llama"}
            model1 = manager1.load_model("test-model", config)
            model2 = manager2.get_model("test-model")
            
            # Should return the same model
            self.assertEqual(model1, model2)
            
            self._record_test_result("test_llm_model_manager_singleton", True)
            
        except Exception as e:
            self._record_test_result("test_llm_model_manager_singleton", False, str(e))
            raise
    
    def test_config_manager_singleton(self):
        """Test ConfigManager singleton"""
        try:
            # Create two instances
            config1 = ConfigManager()
            config2 = ConfigManager()
            
            # They should be the same instance
            self.assertIs(config1, config2)
            
            # Test config functionality
            config1.set_config("test_key", "test_value")
            value = config2.get_config("test_key")
            
            # Should return the same value
            self.assertEqual(value, "test_value")
            
            self._record_test_result("test_config_manager_singleton", True)
            
        except Exception as e:
            self._record_test_result("test_config_manager_singleton", False, str(e))
            raise

class TestFactoryPattern(unittest.TestCase):
    """Test Factory pattern implementation"""
    
    def setUp(self):
        """Set up test data"""
        self.report_data = {
            "timestamp": datetime.now().isoformat(),
            "test_type": "unit_patterns",
            "results": []
        }
    
    def tearDown(self):
        """Clean up after tests"""
        failed_tests = [result for result in self.report_data["results"] if not result["passed"]]
        if failed_tests:
            self._generate_html_report()
    
    def _record_test_result(self, test_name: str, passed: bool, error: str = None):
        """Record test result"""
        self.report_data["results"].append({
            "test_name": test_name,
            "passed": passed,
            "error": error,
            "timestamp": datetime.now().isoformat()
        })
    
    def _generate_html_report(self):
        """Generate HTML report for failed tests"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = f"tests/reports/{timestamp}-unit_patterns.html"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Unit Pattern Tests Report - {timestamp}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f0f0f0; padding: 10px; border-radius: 5px; }}
                .test-result {{ margin: 10px 0; padding: 10px; border-radius: 5px; }}
                .passed {{ background-color: #d4edda; border: 1px solid #c3e6cb; }}
                .failed {{ background-color: #f8d7da; border: 1px solid #f5c6cb; }}
                .error {{ color: #721c24; font-family: monospace; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Unit Pattern Tests Report</h1>
                <p>Generated: {self.report_data["timestamp"]}</p>
                <p>Test Type: {self.report_data["test_type"]}</p>
            </div>
        """
        
        for result in self.report_data["results"]:
            status_class = "passed" if result["passed"] else "failed"
            status_text = "PASSED" if result["passed"] else "FAILED"
            
            html_content += f"""
            <div class="test-result {status_class}">
                <h3>{result["test_name"]} - {status_text}</h3>
                <p>Timestamp: {result["timestamp"]}</p>
                {f'<div class="error">Error: {result["error"]}</div>' if result["error"] else ''}
            </div>
            """
        
        html_content += """
        </body>
        </html>
        """
        
        with open(report_path, 'w') as f:
            f.write(html_content)
    
    def test_llm_model_factory(self):
        """Test LLMModelFactory"""
        try:
            # Test creating different model types
            config = {"size": "7B"}
            
            phi3_model = LLMModelFactory.create_model("phi3", config)
            self.assertIsNotNone(phi3_model)
            self.assertEqual(phi3_model.model_name, "Phi-3")
            
            qwen3_model = LLMModelFactory.create_model("qwen3", config)
            self.assertIsNotNone(qwen3_model)
            self.assertEqual(qwen3_model.model_name, "Qwen 3")
            
            llama3_model = LLMModelFactory.create_model("llama3", config)
            self.assertIsNotNone(llama3_model)
            self.assertEqual(llama3_model.model_name, "Llama 3")
            
            # Test invalid model type
            with self.assertRaises(ValueError):
                LLMModelFactory.create_model("invalid", config)
            
            self._record_test_result("test_llm_model_factory", True)
            
        except Exception as e:
            self._record_test_result("test_llm_model_factory", False, str(e))
            raise
    
    def test_inference_strategy_factory(self):
        """Test InferenceStrategyFactory"""
        try:
            # Test creating different strategies
            cpu_strategy = InferenceStrategyFactory.create_strategy("cpu")
            self.assertIsInstance(cpu_strategy, CPUStrategy)
            
            gpu_strategy = InferenceStrategyFactory.create_strategy("gpu")
            self.assertIsInstance(gpu_strategy, GPUStrategy)
            
            quantized_strategy = InferenceStrategyFactory.create_strategy("quantized")
            self.assertIsInstance(quantized_strategy, QuantizedStrategy)
            
            # Test invalid strategy type
            with self.assertRaises(ValueError):
                InferenceStrategyFactory.create_strategy("invalid")
            
            self._record_test_result("test_inference_strategy_factory", True)
            
        except Exception as e:
            self._record_test_result("test_inference_strategy_factory", False, str(e))
            raise

class TestStrategyPattern(unittest.TestCase):
    """Test Strategy pattern implementation"""
    
    def setUp(self):
        """Set up test data"""
        self.report_data = {
            "timestamp": datetime.now().isoformat(),
            "test_type": "unit_patterns",
            "results": []
        }
    
    def tearDown(self):
        """Clean up after tests"""
        failed_tests = [result for result in self.report_data["results"] if not result["passed"]]
        if failed_tests:
            self._generate_html_report()
    
    def _record_test_result(self, test_name: str, passed: bool, error: str = None):
        """Record test result"""
        self.report_data["results"].append({
            "test_name": test_name,
            "passed": passed,
            "error": error,
            "timestamp": datetime.now().isoformat()
        })
    
    def _generate_html_report(self):
        """Generate HTML report for failed tests"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = f"tests/reports/{timestamp}-unit_patterns.html"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Unit Pattern Tests Report - {timestamp}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f0f0f0; padding: 10px; border-radius: 5px; }}
                .test-result {{ margin: 10px 0; padding: 10px; border-radius: 5px; }}
                .passed {{ background-color: #d4edda; border: 1px solid #c3e6cb; }}
                .failed {{ background-color: #f8d7da; border: 1px solid #f5c6cb; }}
                .error {{ color: #721c24; font-family: monospace; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Unit Pattern Tests Report</h1>
                <p>Generated: {self.report_data["timestamp"]}</p>
                <p>Test Type: {self.report_data["test_type"]}</p>
            </div>
        """
        
        for result in self.report_data["results"]:
            status_class = "passed" if result["passed"] else "failed"
            status_text = "PASSED" if result["passed"] else "FAILED"
            
            html_content += f"""
            <div class="test-result {status_class}">
                <h3>{result["test_name"]} - {status_text}</h3>
                <p>Timestamp: {result["timestamp"]}</p>
                {f'<div class="error">Error: {result["error"]}</div>' if result["error"] else ''}
            </div>
            """
        
        html_content += """
        </body>
        </html>
        """
        
        with open(report_path, 'w') as f:
            f.write(html_content)
    
    def test_strategy_context(self):
        """Test StrategyContext"""
        try:
            # Create context with default strategy
            context = StrategyContext()
            self.assertIsInstance(context._strategy, CPUStrategy)
            
            # Test CPU strategy
            result = context.execute_inference("test_model", "Hello world")
            self.assertIn("CPU", result)
            
            # Switch to GPU strategy
            context.set_strategy(GPUStrategy())
            result = context.execute_inference("test_model", "Hello world")
            self.assertIn("GPU", result)
            
            # Switch to quantized strategy
            context.set_strategy(QuantizedStrategy())
            result = context.execute_inference("test_model", "Hello world")
            self.assertIn("Quantized", result)
            
            self._record_test_result("test_strategy_context", True)
            
        except Exception as e:
            self._record_test_result("test_strategy_context", False, str(e))
            raise

class TestPipelinePattern(unittest.TestCase):
    """Test Pipeline pattern implementation"""
    
    def setUp(self):
        """Set up test data"""
        self.report_data = {
            "timestamp": datetime.now().isoformat(),
            "test_type": "unit_patterns",
            "results": []
        }
    
    def tearDown(self):
        """Clean up after tests"""
        failed_tests = [result for result in self.report_data["results"] if not result["passed"]]
        if failed_tests:
            self._generate_html_report()
    
    def _record_test_result(self, test_name: str, passed: bool, error: str = None):
        """Record test result"""
        self.report_data["results"].append({
            "test_name": test_name,
            "passed": passed,
            "error": error,
            "timestamp": datetime.now().isoformat()
        })
    
    def _generate_html_report(self):
        """Generate HTML report for failed tests"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = f"tests/reports/{timestamp}-unit_patterns.html"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Unit Pattern Tests Report - {timestamp}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f0f0f0; padding: 10px; border-radius: 5px; }}
                .test-result {{ margin: 10px 0; padding: 10px; border-radius: 5px; }}
                .passed {{ background-color: #d4edda; border: 1px solid #c3e6cb; }}
                .failed {{ background-color: #f8d7da; border: 1px solid #f5c6cb; }}
                .error {{ color: #721c24; font-family: monospace; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Unit Pattern Tests Report</h1>
                <p>Generated: {self.report_data["timestamp"]}</p>
                <p>Test Type: {self.report_data["test_type"]}</p>
            </div>
        """
        
        for result in self.report_data["results"]:
            status_class = "passed" if result["passed"] else "failed"
            status_text = "PASSED" if result["passed"] else "FAILED"
            
            html_content += f"""
            <div class="test-result {status_class}">
                <h3>{result["test_name"]} - {status_text}</h3>
                <p>Timestamp: {result["timestamp"]}</p>
                {f'<div class="error">Error: {result["error"]}</div>' if result["error"] else ''}
            </div>
            """
        
        html_content += """
        </body>
        </html>
        """
        
        with open(report_path, 'w') as f:
            f.write(html_content)
    
    def test_pipeline_builder(self):
        """Test PipelineBuilder"""
        try:
            # Create pipeline using builder
            builder = PipelineBuilder("test_pipeline")
            pipeline = (builder
                       .add_validation()
                       .add_tokenization()
                       .add_preprocessing()
                       .build())
            
            self.assertEqual(pipeline.name, "test_pipeline")
            self.assertEqual(len(pipeline.steps), 3)
            
            # Test pipeline execution
            result = pipeline.execute("Hello, World!")
            self.assertIsNotNone(result)
            
            # Check metrics
            metrics = pipeline.get_metrics()
            self.assertIn("total_time", metrics)
            self.assertTrue(metrics["success"])
            
            self._record_test_result("test_pipeline_builder", True)
            
        except Exception as e:
            self._record_test_result("test_pipeline_builder", False, str(e))
            raise

class TestDecoratorPattern(unittest.TestCase):
    """Test Decorator pattern implementation"""
    
    def setUp(self):
        """Set up test data"""
        self.report_data = {
            "timestamp": datetime.now().isoformat(),
            "test_type": "unit_patterns",
            "results": []
        }
    
    def tearDown(self):
        """Clean up after tests"""
        failed_tests = [result for result in self.report_data["results"] if not result["passed"]]
        if failed_tests:
            self._generate_html_report()
    
    def _record_test_result(self, test_name: str, passed: bool, error: str = None):
        """Record test result"""
        self.report_data["results"].append({
            "test_name": test_name,
            "passed": passed,
            "error": error,
            "timestamp": datetime.now().isoformat()
        })
    
    def _generate_html_report(self):
        """Generate HTML report for failed tests"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = f"tests/reports/{timestamp}-unit_patterns.html"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Unit Pattern Tests Report - {timestamp}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f0f0f0; padding: 10px; border-radius: 5px; }}
                .test-result {{ margin: 10px 0; padding: 10px; border-radius: 5px; }}
                .passed {{ background-color: #d4edda; border: 1px solid #c3e6cb; }}
                .failed {{ background-color: #f8d7da; border: 1px solid #f5c6cb; }}
                .error {{ color: #721c24; font-family: monospace; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Unit Pattern Tests Report</h1>
                <p>Generated: {self.report_data["timestamp"]}</p>
                <p>Test Type: {self.report_data["test_type"]}</p>
            </div>
        """
        
        for result in self.report_data["results"]:
            status_class = "passed" if result["passed"] else "failed"
            status_text = "PASSED" if result["passed"] else "FAILED"
            
            html_content += f"""
            <div class="test-result {status_class}">
                <h3>{result["test_name"]} - {status_text}</h3>
                <p>Timestamp: {result["timestamp"]}</p>
                {f'<div class="error">Error: {result["error"]}</div>' if result["error"] else ''}
            </div>
            """
        
        html_content += """
        </body>
        </html>
        """
        
        with open(report_path, 'w') as f:
            f.write(html_content)
    
    def test_logging_decorator(self):
        """Test LoggingDecorator"""
        try:
            # Create base inference
            base_inference = BaseLLMInference("test_model")
            
            # Add logging decorator
            logging_inference = LoggingDecorator(base_inference)
            
            # Test generation
            result = logging_inference.generate("Hello world")
            self.assertIsNotNone(result)
            self.assertIn("test_model", result)
            
            self._record_test_result("test_logging_decorator", True)
            
        except Exception as e:
            self._record_test_result("test_logging_decorator", False, str(e))
            raise
    
    def test_caching_decorator(self):
        """Test CachingDecorator"""
        try:
            # Create base inference
            base_inference = BaseLLMInference("test_model")
            
            # Add caching decorator
            caching_inference = CachingDecorator(base_inference)
            
            # Test first generation (cache miss)
            result1 = caching_inference.generate("Hello world")
            self.assertIsNotNone(result1)
            
            # Test second generation (cache hit)
            result2 = caching_inference.generate("Hello world")
            self.assertEqual(result1, result2)
            
            # Test with different parameters (cache miss)
            result3 = caching_inference.generate("Hello world", max_tokens=200)
            self.assertNotEqual(result1, result3)
            
            self._record_test_result("test_caching_decorator", True)
            
        except Exception as e:
            self._record_test_result("test_caching_decorator", False, str(e))
            raise

if __name__ == '__main__':
    unittest.main()
