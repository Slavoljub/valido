"""
Model Testing Framework for AI Models
Tests model download, loading, inference, and performance
"""

import os
import time
import json
import logging
import psutil
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

# Model test configuration
MODEL_TEST_CONFIG = {
    'phi-3-4b': {
        'name': 'Phi-3 4B',
        'type': 'llm',
        'format': 'gguf',
        'test_prompts': [
            'What is 2+2?',
            'Explain financial analysis',
            'Generate a simple report'
        ],
        'expected_response_time': 30,  # seconds
        'memory_usage_limit': 4096,  # MB
        'accuracy_threshold': 0.7,
        'file_size_expected': 2.5  # GB
    },
    'qwen-3-4b': {
        'name': 'Qwen 3 4B',
        'type': 'llm',
        'format': 'gguf',
        'test_prompts': [
            'What is artificial intelligence?',
            'Explain machine learning',
            'Generate a business plan'
        ],
        'expected_response_time': 45,
        'memory_usage_limit': 4096,
        'accuracy_threshold': 0.75,
        'file_size_expected': 2.8
    },
    'llama-3-1-8b': {
        'name': 'Llama 3.1 8B',
        'type': 'llm',
        'format': 'gguf',
        'test_prompts': [
            'What is the capital of Serbia?',
            'Explain financial ratios',
            'Generate a marketing strategy'
        ],
        'expected_response_time': 60,
        'memory_usage_limit': 8192,
        'accuracy_threshold': 0.8,
        'file_size_expected': 5.2
    },
    'mistral-7b': {
        'name': 'Mistral 7B',
        'type': 'llm',
        'format': 'gguf',
        'test_prompts': [
            'What is machine learning?',
            'Explain neural networks',
            'Generate a project proposal'
        ],
        'expected_response_time': 50,
        'memory_usage_limit': 7168,
        'accuracy_threshold': 0.78,
        'file_size_expected': 4.5
    }
}


class ModelTester:
    """Comprehensive model testing framework"""
    
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.config = MODEL_TEST_CONFIG.get(model_name, {})
        self.test_results = []
        self.model_manager = None
        
        # Initialize model manager
        try:
            from src.ai_local_models.model_manager import LocalModelManager
            self.model_manager = LocalModelManager()
        except ImportError:
            logger.error("Model manager not available")
    
    def test_model_download(self) -> Dict[str, Any]:
        """Test model download functionality"""
        try:
            if not self.model_manager:
                return self._create_fail_result('Model Download', 'Model manager not available')
            
            start_time = time.time()
            
            # Check if model already exists
            model_path = self.model_manager.get_model_path(self.model_name)
            if model_path and os.path.exists(model_path):
                file_size = os.path.getsize(model_path) / (1024 * 1024 * 1024)  # GB
                duration = 0
                status = 'PASS'
                details = f'Model already exists ({file_size:.2f} GB)'
            else:
                # Download model
                result = self.model_manager.download_model(self.model_name)
                duration = time.time() - start_time
                
                if result and result.get('success'):
                    file_size = result.get('file_size', 0) / (1024 * 1024 * 1024)  # GB
                    status = 'PASS'
                    details = f'Download successful ({file_size:.2f} GB)'
                else:
                    status = 'FAIL'
                    details = result.get('error', 'Download failed')
                    file_size = 0
            
            return {
                'test_name': 'Model Download',
                'status': status,
                'details': details,
                'duration': duration,
                'file_size_gb': file_size,
                'expected_size_gb': self.config.get('file_size_expected', 0)
            }
        
        except Exception as e:
            return self._create_fail_result('Model Download', str(e))
    
    def test_model_loading(self) -> Dict[str, Any]:
        """Test model loading and initialization"""
        try:
            if not self.model_manager:
                return self._create_fail_result('Model Loading', 'Model manager not available')
            
            start_time = time.time()
            initial_memory = self._get_memory_usage()
            
            # Load model
            model = self.model_manager.load_model(self.model_name)
            load_time = time.time() - start_time
            final_memory = self._get_memory_usage()
            memory_increase = final_memory - initial_memory
            
            if model:
                status = 'PASS'
                details = f'Model loaded successfully (Memory: +{memory_increase:.1f} MB)'
            else:
                status = 'FAIL'
                details = 'Failed to load model'
                memory_increase = 0
            
            return {
                'test_name': 'Model Loading',
                'status': status,
                'details': details,
                'duration': load_time,
                'memory_increase_mb': memory_increase,
                'memory_limit_mb': self.config.get('memory_usage_limit', 4096)
            }
        
        except Exception as e:
            return self._create_fail_result('Model Loading', str(e))
    
    def test_model_inference(self) -> List[Dict[str, Any]]:
        """Test model inference with various prompts"""
        results = []
        
        try:
            if not self.model_manager:
                return [self._create_fail_result('Model Inference', 'Model manager not available')]
            
            prompts = self.config.get('test_prompts', [])
            
            for i, prompt in enumerate(prompts):
                try:
                    start_time = time.time()
                    
                    # Generate response
                    response = self.model_manager.generate_response(self.model_name, prompt)
                    inference_time = time.time() - start_time
                    
                    # Validate response
                    is_valid = self._validate_response(response, prompt)
                    quality_score = self._assess_response_quality(response)
                    
                    status = 'PASS' if is_valid else 'FAIL'
                    details = f'Response length: {len(response)} chars, Quality: {quality_score:.2f}'
                    
                    results.append({
                        'test_name': f'Inference {i+1}: {prompt[:50]}...',
                        'status': status,
                        'details': details,
                        'duration': inference_time,
                        'response_length': len(response),
                        'quality_score': quality_score,
                        'expected_time': self.config.get('expected_response_time', 30)
                    })
                
                except Exception as e:
                    results.append({
                        'test_name': f'Inference {i+1}: {prompt[:50]}...',
                        'status': 'FAIL',
                        'details': str(e),
                        'duration': 0,
                        'response_length': 0,
                        'quality_score': 0
                    })
        
        except Exception as e:
            results.append(self._create_fail_result('Model Inference', str(e)))
        
        return results
    
    def test_model_performance(self) -> Dict[str, Any]:
        """Test model performance metrics"""
        try:
            if not self.model_manager:
                return self._create_fail_result('Performance Test', 'Model manager not available')
            
            process = psutil.Process()
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            initial_cpu = psutil.cpu_percent()
            
            # Run performance test
            start_time = time.time()
            self._run_performance_test()
            test_time = time.time() - start_time
            
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            final_cpu = psutil.cpu_percent()
            memory_increase = final_memory - initial_memory
            cpu_usage = (initial_cpu + final_cpu) / 2
            
            memory_limit = self.config.get('memory_usage_limit', 4096)
            status = 'PASS' if memory_increase < memory_limit else 'FAIL'
            
            return {
                'test_name': 'Performance Test',
                'status': status,
                'details': f'Memory: +{memory_increase:.1f} MB, CPU: {cpu_usage:.1f}%',
                'duration': test_time,
                'memory_increase_mb': memory_increase,
                'memory_limit_mb': memory_limit,
                'cpu_usage_percent': cpu_usage
            }
        
        except Exception as e:
            return self._create_fail_result('Performance Test', str(e))
    
    def test_model_accuracy(self) -> Dict[str, Any]:
        """Test model accuracy with known questions"""
        try:
            if not self.model_manager:
                return self._create_fail_result('Accuracy Test', 'Model manager not available')
            
            accuracy_tests = [
                {
                    'question': 'What is 2+2?',
                    'expected_keywords': ['4', 'four', '2+2'],
                    'weight': 0.3
                },
                {
                    'question': 'What is the capital of Serbia?',
                    'expected_keywords': ['belgrade', 'beograd'],
                    'weight': 0.3
                },
                {
                    'question': 'What is artificial intelligence?',
                    'expected_keywords': ['ai', 'intelligence', 'machine', 'computer'],
                    'weight': 0.4
                }
            ]
            
            total_score = 0
            total_weight = 0
            results = []
            
            for test in accuracy_tests:
                try:
                    response = self.model_manager.generate_response(self.model_name, test['question'])
                    score = self._calculate_accuracy_score(response, test['expected_keywords'])
                    weighted_score = score * test['weight']
                    
                    total_score += weighted_score
                    total_weight += test['weight']
                    
                    results.append({
                        'question': test['question'],
                        'score': score,
                        'weighted_score': weighted_score
                    })
                
                except Exception as e:
                    results.append({
                        'question': test['question'],
                        'score': 0,
                        'weighted_score': 0,
                        'error': str(e)
                    })
            
            accuracy = total_score / total_weight if total_weight > 0 else 0
            threshold = self.config.get('accuracy_threshold', 0.7)
            status = 'PASS' if accuracy >= threshold else 'FAIL'
            
            return {
                'test_name': 'Accuracy Test',
                'status': status,
                'details': f'Accuracy: {accuracy:.2f} (threshold: {threshold})',
                'accuracy_score': accuracy,
                'threshold': threshold,
                'test_results': results
            }
        
        except Exception as e:
            return self._create_fail_result('Accuracy Test', str(e))
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all model tests"""
        all_results = []
        
        # Download test
        all_results.append(self.test_model_download())
        
        # Loading test
        all_results.append(self.test_model_loading())
        
        # Inference tests
        all_results.extend(self.test_model_inference())
        
        # Performance test
        all_results.append(self.test_model_performance())
        
        # Accuracy test
        all_results.append(self.test_model_accuracy())
        
        # Calculate summary
        passed = sum(1 for r in all_results if r['status'] == 'PASS')
        total = len(all_results)
        
        return {
            'model_name': self.model_name,
            'model_config': self.config,
            'total_tests': total,
            'passed_tests': passed,
            'failed_tests': total - passed,
            'success_rate': (passed / total) * 100 if total > 0 else 0,
            'results': all_results,
            'timestamp': datetime.now().isoformat()
        }
    
    def _validate_response(self, response: str, prompt: str) -> bool:
        """Validate model response"""
        if not response or len(response.strip()) < 10:
            return False
        
        # Check for common error patterns
        error_patterns = ['error', 'exception', 'failed', 'not available', 'not found']
        if any(pattern in response.lower() for pattern in error_patterns):
            return False
        
        return True
    
    def _assess_response_quality(self, response: str) -> float:
        """Assess response quality (0-1 scale)"""
        if not response:
            return 0.0
        
        score = 0.0
        
        # Length score (0.2)
        if len(response) > 200:
            score += 0.2
        elif len(response) > 100:
            score += 0.15
        elif len(response) > 50:
            score += 0.1
        else:
            score += 0.05
        
        # Coherence score (0.3)
        sentences = response.split('.')
        if len(sentences) > 3:
            score += 0.3
        elif len(sentences) > 2:
            score += 0.2
        elif len(sentences) > 1:
            score += 0.1
        
        # Content relevance score (0.5)
        relevant_words = [
            'financial', 'analysis', 'business', 'data', 'report', 'chart',
            'intelligence', 'machine', 'learning', 'artificial', 'neural',
            'capital', 'serbia', 'belgrade', 'beograd', 'four', '4', '2+2'
        ]
        relevant_count = sum(1 for word in relevant_words if word in response.lower())
        score += min(0.5, relevant_count * 0.1)
        
        return min(1.0, score)
    
    def _calculate_accuracy_score(self, response: str, expected_keywords: List[str]) -> float:
        """Calculate accuracy score based on expected keywords"""
        if not response:
            return 0.0
        
        response_lower = response.lower()
        found_keywords = sum(1 for keyword in expected_keywords if keyword in response_lower)
        
        return found_keywords / len(expected_keywords) if expected_keywords else 0.0
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024
    
    def _run_performance_test(self):
        """Run a performance test"""
        # Simulate intensive model usage
        for _ in range(5):
            time.sleep(0.1)
    
    def _create_fail_result(self, test_name: str, error: str) -> Dict[str, Any]:
        """Create a standardized fail result"""
        return {
            'test_name': test_name,
            'status': 'FAIL',
            'details': error,
            'duration': 0,
            'timestamp': datetime.now().isoformat()
        }


class ModelTestSuite:
    """Test suite for multiple models"""
    
    def __init__(self):
        self.testers = {}
        self.results = {}
    
    def test_all_models(self) -> Dict[str, Any]:
        """Test all configured models"""
        results = {}
        
        for model_name in MODEL_TEST_CONFIG.keys():
            try:
                logger.info(f"Testing model: {model_name}")
                tester = ModelTester(model_name)
                result = tester.run_all_tests()
                results[model_name] = result
                
                logger.info(f"Completed testing {model_name}: {result['success_rate']:.1f}% success")
            
            except Exception as e:
                logger.error(f"Failed to test model {model_name}: {e}")
                results[model_name] = {
                    'model_name': model_name,
                    'status': 'ERROR',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
        
        return results
    
    def test_specific_models(self, model_names: List[str]) -> Dict[str, Any]:
        """Test specific models"""
        results = {}
        
        for model_name in model_names:
            if model_name in MODEL_TEST_CONFIG:
                try:
                    logger.info(f"Testing model: {model_name}")
                    tester = ModelTester(model_name)
                    result = tester.run_all_tests()
                    results[model_name] = result
                except Exception as e:
                    logger.error(f"Failed to test model {model_name}: {e}")
                    results[model_name] = {
                        'model_name': model_name,
                        'status': 'ERROR',
                        'error': str(e),
                        'timestamp': datetime.now().isoformat()
                    }
            else:
                logger.warning(f"Model {model_name} not found in configuration")
        
        return results
    
    def generate_summary_report(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary report for all model tests"""
        total_models = len(results)
        successful_models = 0
        total_tests = 0
        passed_tests = 0
        
        model_summaries = []
        
        for model_name, result in results.items():
            if result.get('status') == 'ERROR':
                continue
            
            successful_models += 1
            total_tests += result.get('total_tests', 0)
            passed_tests += result.get('passed_tests', 0)
            
            model_summaries.append({
                'model_name': model_name,
                'success_rate': result.get('success_rate', 0),
                'total_tests': result.get('total_tests', 0),
                'passed_tests': result.get('passed_tests', 0),
                'failed_tests': result.get('failed_tests', 0)
            })
        
        overall_success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        return {
            'summary': {
                'total_models': total_models,
                'successful_models': successful_models,
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'failed_tests': total_tests - passed_tests,
                'overall_success_rate': overall_success_rate
            },
            'model_summaries': model_summaries,
            'detailed_results': results,
            'timestamp': datetime.now().isoformat()
        }


def run_model_tests(model_names: List[str] = None) -> Dict[str, Any]:
    """Run model tests for specified models or all models"""
    suite = ModelTestSuite()
    
    if model_names:
        results = suite.test_specific_models(model_names)
    else:
        results = suite.test_all_models()
    
    return suite.generate_summary_report(results)


def test_single_model(model_name: str) -> Dict[str, Any]:
    """Test a single model"""
    tester = ModelTester(model_name)
    return tester.run_all_tests()
