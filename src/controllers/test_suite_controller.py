"""
Test Suite Controller - Comprehensive Testing System
Handles all testing operations, reports, and monitoring
"""
import os
import sys
import json
import time
import subprocess
import threading
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging

from flask import render_template, jsonify, request, current_app
from werkzeug.exceptions import HTTPException

logger = logging.getLogger(__name__)

class TestCategory(Enum):
    """Test categories for organization"""
    UNIT = "unit"
    INTEGRATION = "integration"
    E2E = "e2e"
    PERFORMANCE = "performance"
    SECURITY = "security"
    FUNCTIONAL = "functional"
    ROUTES = "routes"
    DATABASE = "database"
    AI_ML = "ai_ml"
    IMPORTS = "imports"

@dataclass
class TestResult:
    """Individual test result"""
    name: str
    category: str
    status: str  # 'passed', 'failed', 'skipped', 'error'
    duration: float
    message: str
    details: Dict[str, Any]
    timestamp: datetime

@dataclass
class TestSuiteResult:
    """Complete test suite result"""
    total_tests: int
    passed: int
    failed: int
    skipped: int
    errors: int
    duration: float
    categories: Dict[str, Dict[str, int]]
    results: List[TestResult]
    summary: str
    timestamp: datetime

class TestSuiteController:
    """Advanced test suite controller with comprehensive testing capabilities"""
    
    def __init__(self):
        self.test_categories = {
            TestCategory.UNIT: {
                'description': 'Unit tests for individual components',
                'path': 'tests/unit',
                'priority': 1
            },
            TestCategory.INTEGRATION: {
                'description': 'Integration tests for system interactions',
                'path': 'tests/integration',
                'priority': 2
            },
            TestCategory.E2E: {
                'description': 'End-to-end user workflow tests',
                'path': 'tests/e2e',
                'priority': 3
            },
            TestCategory.PERFORMANCE: {
                'description': 'Performance and load testing',
                'path': 'tests/performance',
                'priority': 4
            },
            TestCategory.SECURITY: {
                'description': 'Security and vulnerability testing',
                'path': 'tests/security',
                'priority': 5
            },
            TestCategory.FUNCTIONAL: {
                'description': 'Functional feature testing',
                'path': 'tests/functional',
                'priority': 6
            },
            TestCategory.ROUTES: {
                'description': 'Route and API endpoint testing',
                'path': 'tests/routes',
                'priority': 7
            },
            TestCategory.DATABASE: {
                'description': 'Database operation testing',
                'path': 'tests/database',
                'priority': 8
            },
            TestCategory.AI_ML: {
                'description': 'AI/ML model and integration testing',
                'path': 'tests/ai',
                'priority': 9
            },
            TestCategory.IMPORTS: {
                'description': 'Import and dependency testing',
                'path': 'tests',
                'priority': 10
            }
        }
        
        self._running_tests = False
        self._current_results = []
        self._test_lock = threading.Lock()
    
    def index(self):
        """Render the main test suite interface"""
        try:
            # Get available test categories and their status
            categories_status = self._get_categories_status()
            
            # Get recent test results if available
            recent_results = self._get_recent_results()
            
            return render_template('test_suite/index.html',
                                 categories=categories_status,
                                 recent_results=recent_results,
                                 test_categories=self.test_categories)
        except Exception as e:
            logger.error(f"Error rendering test suite: {e}")
            return render_template('errors/error.html',
                                 error_code=500,
                                 error_title="Test Suite Error",
                                 error_message="Failed to load test suite interface.",
                                 stack_trace=str(e)), 500
    
    def run_tests(self):
        """Run tests based on request parameters"""
        try:
            data = request.get_json() or {}
            categories = data.get('categories', [])
            run_all = data.get('run_all', False)
            
            if not categories and not run_all:
                return jsonify({'error': 'No test categories specified'}), 400
            
            # Start test execution in background thread
            if not self._running_tests:
                if run_all:
                    all_categories = [cat.value if hasattr(cat, 'value') else str(cat) for cat in self.test_categories.keys()]
                else:
                    all_categories = categories
                    
                thread = threading.Thread(target=self._execute_tests, args=(all_categories,))
                thread.daemon = True
                thread.start()
                
                return jsonify({
                    'status': 'started',
                    'message': f'Started running tests for categories: {categories if not run_all else "all"}',
                    'timestamp': datetime.now().isoformat()
                })
            else:
                return jsonify({
                    'status': 'running',
                    'message': 'Tests are already running'
                }), 409
                
        except Exception as e:
            logger.error(f"Error starting tests: {e}")
            return jsonify({'error': str(e)}), 500
    
    def get_status(self):
        """Get current test suite status"""
        try:
            categories_status = self._get_categories_status()
            
            return jsonify({
                'status': 'running' if self._running_tests else 'idle',
                'categories': categories_status,
                'recent_results': self._get_recent_results(),
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Error getting test suite status: {e}")
            return jsonify({'error': str(e)}), 500
    
    def _get_categories_status(self) -> Dict[str, Any]:
        """Get status of all test categories"""
        status = {}
        
        for category, config in self.test_categories.items():
            category_name = category.value if hasattr(category, 'value') else str(category)
            test_path = config['path']
            
            # Check if test directory exists
            exists = os.path.exists(test_path)
            
            # Count test files
            test_files = 0
            if exists:
                test_files = len([f for f in os.listdir(test_path) 
                                if f.endswith('.py') and f.startswith('test_')])
            
            status[category_name] = {
                'description': config['description'],
                'path': test_path,
                'priority': config['priority'],
                'exists': exists,
                'test_files': test_files,
                'available': exists and test_files > 0
            }
        
        return status
    
    def _get_recent_results(self) -> List[Dict[str, Any]]:
        """Get recent test results from cache or file"""
        try:
            results_file = 'tests/reports/latest_results.json'
            if os.path.exists(results_file):
                with open(results_file, 'r') as f:
                    data = json.load(f)
                    return data.get('results', [])[-10:]  # Last 10 results
        except Exception as e:
            logger.warning(f"Could not load recent results: {e}")
        
        return []
    
    def _execute_tests(self, categories: List[str]):
        """Execute tests for specified categories"""
        with self._test_lock:
            self._running_tests = True
            self._current_results = []
        
        try:
            # Try to use the comprehensive test runner
            try:
                from tests.run_comprehensive_tests import ComprehensiveTestRunner
                
                runner = ComprehensiveTestRunner()
                
                # Set progress callback if needed
                def progress_callback(progress, message):
                    logger.info(f"Test progress: {progress:.1f}% - {message}")
                
                runner.set_progress_callback(progress_callback)
                
                # Run tests
                suite_result = runner.run_tests(categories=categories)
                
                # Convert results to our format
                total_results = []
                for result in suite_result.results:
                    test_result = TestResult(
                        name=result.name,
                        category=result.category,
                        status=result.status.value,
                        duration=result.duration,
                        message=result.message,
                        details=result.details,
                        timestamp=result.timestamp
                    )
                    total_results.append(test_result)
                
                # Save results
                self._save_results(suite_result)
                
            except ImportError:
                # Fallback to simple test execution
                logger.info("Comprehensive test runner not available, using fallback")
                self._run_simple_tests(categories)
                
        except Exception as e:
            logger.error(f"Error during test execution: {e}")
        finally:
            with self._test_lock:
                self._running_tests = False
    
    def _run_simple_tests(self, categories: List[str]):
        """Fallback simple test execution"""
        try:
            import subprocess
            import sys
            
            # Run pytest for each category
            for category in categories:
                test_path = f"tests/{category}"
                if os.path.exists(test_path):
                    logger.info(f"Running tests for category: {category}")
                    
                    # Run pytest
                    result = subprocess.run([
                        sys.executable, "-m", "pytest", test_path, 
                        "-v", "--tb=short", "--json-report"
                    ], capture_output=True, text=True, timeout=300)
                    
                    # Create test result
                    test_result = TestResult(
                        name=f"{category}_tests",
                        category=category,
                        status='passed' if result.returncode == 0 else 'failed',
                        duration=0.0,  # We don't have timing info from subprocess
                        message=f"Tests {'passed' if result.returncode == 0 else 'failed'}",
                        details={
                            'return_code': result.returncode,
                            'stdout': result.stdout,
                            'stderr': result.stderr
                        },
                        timestamp=datetime.now()
                    )
                    
                    self._current_results.append(test_result)
                    
        except Exception as e:
            logger.error(f"Error in simple test execution: {e}")
        
        # Save results
        if self._current_results:
            self._save_simple_results(self._current_results)
    
    def _run_category_tests(self, category: str) -> List[TestResult]:
        """Run tests for a specific category"""
        results = []
        try:
            category_enum = TestCategory(category)
            category_config = self.test_categories.get(category_enum)
        except ValueError:
            # If category is not a valid enum value, try to find it by value
            category_config = None
            for cat_enum, config in self.test_categories.items():
                if cat_enum.value == category:
                    category_config = config
                    break
        
        if not category_config or not os.path.exists(category_config['path']):
            results.append(TestResult(
                name=f"{category}_tests",
                category=category,
                status='skipped',
                duration=0.0,
                message=f"Test directory not found: {category_config['path'] if category_config else 'Unknown'}",
                details={},
                timestamp=datetime.now()
            ))
            return results
        
        # Run pytest for the category
        try:
            cmd = [
                sys.executable, '-m', 'pytest',
                category_config['path'],
                '--json-report',
                '--json-report-file=none',
                '--tb=short',
                '-v'
            ]
            
            start_time = time.time()
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=os.getcwd()
            )
            
            stdout, stderr = process.communicate()
            duration = time.time() - start_time
            
            # Parse results
            if process.returncode == 0:
                status = 'passed'
                message = f"All tests passed for {category}"
            else:
                status = 'failed'
                message = f"Some tests failed for {category}"
            
            results.append(TestResult(
                name=f"{category}_test_suite",
                category=category,
                status=status,
                duration=duration,
                message=message,
                details={
                    'stdout': stdout,
                    'stderr': stderr,
                    'return_code': process.returncode
                },
                timestamp=datetime.now()
            ))
            
        except Exception as e:
            results.append(TestResult(
                name=f"{category}_test_suite",
                category=category,
                status='error',
                duration=0.0,
                message=f"Error running tests: {str(e)}",
                details={'error': str(e)},
                timestamp=datetime.now()
            ))
        
        return results
    
    def _compile_results(self, results: List[TestResult], total_duration: float) -> TestSuiteResult:
        """Compile test results into a comprehensive report"""
        total_tests = len(results)
        passed = len([r for r in results if r.status == 'passed'])
        failed = len([r for r in results if r.status == 'failed'])
        skipped = len([r for r in results if r.status == 'skipped'])
        errors = len([r for r in results if r.status == 'error'])
        
        # Group by category
        categories = {}
        for result in results:
            if result.category not in categories:
                categories[result.category] = {'passed': 0, 'failed': 0, 'skipped': 0, 'errors': 0}
            categories[result.category][result.status] += 1
        
        # Generate summary
        if total_tests == 0:
            summary = "No tests were executed"
        elif failed == 0 and errors == 0:
            summary = f"✅ All {total_tests} tests passed successfully"
        else:
            summary = f"⚠️ {passed} passed, {failed} failed, {errors} errors out of {total_tests} tests"
        
        return TestSuiteResult(
            total_tests=total_tests,
            passed=passed,
            failed=failed,
            skipped=skipped,
            errors=errors,
            duration=total_duration,
            categories=categories,
            results=results,
            summary=summary,
            timestamp=datetime.now()
        )
    
    def _save_results(self, suite_result: TestSuiteResult):
        """Save test results to file"""
        try:
            os.makedirs('tests/reports', exist_ok=True)
            
            # Save detailed results
            results_file = 'tests/reports/latest_results.json'
            with open(results_file, 'w') as f:
                json.dump(asdict(suite_result), f, indent=2, default=str)
            
            # Save summary
            summary_file = 'tests/reports/summary.json'
            summary_data = {
                'total_tests': suite_result.total_tests,
                'passed': suite_result.passed,
                'failed': suite_result.failed,
                'skipped': suite_result.skipped,
                'errors': suite_result.errors,
                'duration': suite_result.duration,
                'summary': suite_result.summary,
                'timestamp': suite_result.timestamp.isoformat()
            }
            
            with open(summary_file, 'w') as f:
                json.dump(summary_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving test results: {e}")
    
    def _save_simple_results(self, results: List[TestResult]):
        """Save simple test results to file"""
        try:
            # Ensure reports directory exists
            os.makedirs('tests/reports', exist_ok=True)
            
            # Create simple suite result
            passed = len([r for r in results if r.status == 'passed'])
            failed = len([r for r in results if r.status == 'failed'])
            skipped = len([r for r in results if r.status == 'skipped'])
            errors = len([r for r in results if r.status == 'error'])
            
            simple_result = {
                'total_tests': len(results),
                'passed': passed,
                'failed': failed,
                'skipped': skipped,
                'errors': errors,
                'duration': 0.0,
                'results': [asdict(r) for r in results],
                'timestamp': datetime.now().isoformat()
            }
            
            # Save latest results
            latest_file = 'tests/reports/latest_results.json'
            with open(latest_file, 'w') as f:
                json.dump(simple_result, f, indent=2, default=str)
                
        except Exception as e:
            logger.error(f"Error saving simple test results: {e}")
    
    @staticmethod
    def get_test_categories() -> Dict[str, Any]:
        """Get available test categories (static method for API access)"""
        controller = TestSuiteController()
        return controller._get_categories_status()
    
    @staticmethod
    def run_quick_tests() -> Dict[str, Any]:
        """Run a quick test suite (static method for API access)"""
        controller = TestSuiteController()
        categories = ['imports', 'unit', 'routes']  # Quick essential tests
        
        results = []
        for category in categories:
            category_results = controller._run_category_tests(category)
            results.extend(category_results)
        
        suite_result = controller._compile_results(results, 0.0)
        controller._save_results(suite_result)
        
        return asdict(suite_result)
