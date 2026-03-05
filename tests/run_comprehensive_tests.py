#!/usr/bin/env python3
"""
Comprehensive Test Runner for ValidoAI
=====================================
Advanced test runner with categories, reporting, and real-time execution
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

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logger = logging.getLogger(__name__)

class TestStatus(Enum):
    """Test execution status"""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"

@dataclass
class TestResult:
    """Individual test result"""
    name: str
    category: str
    status: TestStatus
    duration: float
    message: str
    details: Dict[str, Any]
    timestamp: datetime
    output: str = ""
    error: str = ""

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
    report_file: str = ""

class ComprehensiveTestRunner:
    """Advanced test runner with comprehensive features"""
    
    def __init__(self):
        self.test_categories = {
            'unit': {
                'description': 'Unit tests for individual components',
                'path': 'tests/unit',
                'priority': 1,
                'timeout': 30
            },
            'integration': {
                'description': 'Integration tests for system interactions',
                'path': 'tests/integration',
                'priority': 2,
                'timeout': 60
            },
            'e2e': {
                'description': 'End-to-end user workflow tests',
                'path': 'tests/e2e',
                'priority': 3,
                'timeout': 120
            },
            'performance': {
                'description': 'Performance and load testing',
                'path': 'tests/performance',
                'priority': 4,
                'timeout': 180
            },
            'security': {
                'description': 'Security and vulnerability testing',
                'path': 'tests/security',
                'priority': 5,
                'timeout': 90
            },
            'functional': {
                'description': 'Functional feature testing',
                'path': 'tests/functional',
                'priority': 6,
                'timeout': 60
            },
            'routes': {
                'description': 'Route and API endpoint testing',
                'path': 'tests/routes',
                'priority': 7,
                'timeout': 45
            },
            'database': {
                'description': 'Database operation testing',
                'path': 'tests/database',
                'priority': 8,
                'timeout': 60
            },
            'ai_ml': {
                'description': 'AI/ML model and integration testing',
                'path': 'tests/ai',
                'priority': 9,
                'timeout': 120
            },
            'imports': {
                'description': 'Import and dependency testing',
                'path': 'tests',
                'priority': 10,
                'timeout': 30
            }
        }
        
        self._running_tests = False
        self._current_results = []
        self._test_lock = threading.Lock()
        self._progress_callback = None
    
    def set_progress_callback(self, callback):
        """Set callback for progress updates"""
        self._progress_callback = callback
    
    def run_tests(self, categories: List[str] = None, run_all: bool = False) -> TestSuiteResult:
        """Run tests for specified categories or all tests"""
        if categories is None and not run_all:
            categories = ['imports', 'unit', 'routes']  # Default quick tests
        
        if run_all:
            categories = list(self.test_categories.keys())
        
        start_time = time.time()
        all_results = []
        
        # Sort categories by priority
        sorted_categories = sorted(
            categories, 
            key=lambda cat: self.test_categories.get(cat, {}).get('priority', 999)
        )
        
        total_categories = len(sorted_categories)
        
        for i, category in enumerate(sorted_categories):
            if self._progress_callback:
                progress = (i / total_categories) * 100
                self._progress_callback(progress, f"Running {category} tests...")
            
            category_results = self._run_category_tests(category)
            all_results.extend(category_results)
        
        # Compile final results
        suite_result = self._compile_results(all_results, time.time() - start_time)
        
        # Save results
        self._save_results(suite_result)
        
        if self._progress_callback:
            self._progress_callback(100, "Tests completed")
        
        return suite_result
    
    def _run_category_tests(self, category: str) -> List[TestResult]:
        """Run tests for a specific category"""
        results = []
        category_config = self.test_categories.get(category)
        
        if not category_config or not os.path.exists(category_config['path']):
            results.append(TestResult(
                name=f"{category}_tests",
                category=category,
                status=TestStatus.SKIPPED,
                duration=0.0,
                message=f"Test directory not found: {category_config['path'] if category_config else 'Unknown'}",
                details={},
                timestamp=datetime.now()
            ))
            return results
        
        # Find test files
        test_files = self._find_test_files(category_config['path'])
        
        if not test_files:
            results.append(TestResult(
                name=f"{category}_tests",
                category=category,
                status=TestStatus.SKIPPED,
                duration=0.0,
                message=f"No test files found in {category_config['path']}",
                details={'test_files': 0},
                timestamp=datetime.now()
            ))
            return results
        
        # Run pytest for each test file
        for test_file in test_files:
            result = self._run_single_test_file(category, test_file, category_config['timeout'])
            results.append(result)
        
        return results
    
    def _find_test_files(self, test_path: str) -> List[str]:
        """Find test files in the given path"""
        test_files = []
        
        if os.path.isfile(test_path) and test_path.endswith('.py'):
            test_files.append(test_path)
        elif os.path.isdir(test_path):
            for root, dirs, files in os.walk(test_path):
                for file in files:
                    if file.startswith('test_') and file.endswith('.py'):
                        test_files.append(os.path.join(root, file))
        
        return test_files
    
    def _run_single_test_file(self, category: str, test_file: str, timeout: int) -> TestResult:
        """Run a single test file"""
        start_time = time.time()
        
        try:
            # Run pytest for the specific file
            cmd = [
                sys.executable, '-m', 'pytest',
                test_file,
                '--json-report',
                '--json-report-file=none',
                '--tb=short',
                '-v',
                '--timeout', str(timeout)
            ]
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=os.getcwd()
            )
            
            stdout, stderr = process.communicate(timeout=timeout)
            duration = time.time() - start_time
            
            # Parse results
            if process.returncode == 0:
                status = TestStatus.PASSED
                message = f"All tests passed in {os.path.basename(test_file)}"
            elif process.returncode == 5:  # pytest exit code for no tests found
                status = TestStatus.SKIPPED
                message = f"No tests found in {os.path.basename(test_file)}"
            else:
                status = TestStatus.FAILED
                message = f"Some tests failed in {os.path.basename(test_file)}"
            
            return TestResult(
                name=os.path.basename(test_file),
                category=category,
                status=status,
                duration=duration,
                message=message,
                details={
                    'file': test_file,
                    'return_code': process.returncode,
                    'stdout_lines': len(stdout.splitlines()),
                    'stderr_lines': len(stderr.splitlines())
                },
                timestamp=datetime.now(),
                output=stdout,
                error=stderr
            )
            
        except subprocess.TimeoutExpired:
            process.kill()
            return TestResult(
                name=os.path.basename(test_file),
                category=category,
                status=TestStatus.ERROR,
                duration=timeout,
                message=f"Test timed out after {timeout} seconds",
                details={'file': test_file, 'timeout': timeout},
                timestamp=datetime.now(),
                error="Test execution timed out"
            )
        except Exception as e:
            return TestResult(
                name=os.path.basename(test_file),
                category=category,
                status=TestStatus.ERROR,
                duration=time.time() - start_time,
                message=f"Error running tests: {str(e)}",
                details={'file': test_file, 'error': str(e)},
                timestamp=datetime.now(),
                error=str(e)
            )
    
    def _compile_results(self, results: List[TestResult], total_duration: float) -> TestSuiteResult:
        """Compile test results into a comprehensive report"""
        total_tests = len(results)
        passed = len([r for r in results if r.status == TestStatus.PASSED])
        failed = len([r for r in results if r.status == TestStatus.FAILED])
        skipped = len([r for r in results if r.status == TestStatus.SKIPPED])
        errors = len([r for r in results if r.status == TestStatus.ERROR])
        
        # Group by category
        categories = {}
        for result in results:
            if result.category not in categories:
                categories[result.category] = {
                    'total': 0, 'passed': 0, 'failed': 0, 
                    'skipped': 0, 'errors': 0
                }
            
            categories[result.category]['total'] += 1
            categories[result.category][result.status.value] += 1
        
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
            timestamp = suite_result.timestamp.strftime('%Y%m%d_%H%M%S')
            results_file = f'tests/reports/test_results_{timestamp}.json'
            
            with open(results_file, 'w') as f:
                json.dump(asdict(suite_result), f, indent=2, default=str)
            
            # Update latest results
            latest_file = 'tests/reports/latest_results.json'
            with open(latest_file, 'w') as f:
                json.dump(asdict(suite_result), f, indent=2, default=str)
            
            suite_result.report_file = results_file
            logger.info(f"Test results saved to {results_file}")
            
        except Exception as e:
            logger.error(f"Error saving test results: {e}")
    
    def get_test_categories(self) -> Dict[str, Any]:
        """Get available test categories with status"""
        categories = {}
        
        for category_name, config in self.test_categories.items():
            test_path = config['path']
            exists = os.path.exists(test_path)
            
            test_files = 0
            if exists:
                test_files = len(self._find_test_files(test_path))
            
            categories[category_name] = {
                'description': config['description'],
                'path': test_path,
                'priority': config['priority'],
                'timeout': config['timeout'],
                'exists': exists,
                'test_files': test_files,
                'available': exists and test_files > 0
            }
        
        return categories

def main():
    """Main function for command line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Comprehensive Test Runner')
    parser.add_argument('--categories', nargs='+', help='Test categories to run')
    parser.add_argument('--all', action='store_true', help='Run all tests')
    parser.add_argument('--quick', action='store_true', help='Run quick tests only')
    parser.add_argument('--output', help='Output file for results')
    
    args = parser.parse_args()
    
    runner = ComprehensiveTestRunner()
    
    if args.all:
        results = runner.run_tests(run_all=True)
    elif args.quick:
        results = runner.run_tests(categories=['imports', 'unit', 'routes'])
    elif args.categories:
        results = runner.run_tests(categories=args.categories)
    else:
        results = runner.run_tests(categories=['imports', 'unit', 'routes'])
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"TEST RESULTS SUMMARY")
    print(f"{'='*60}")
    print(f"Total Tests: {results.total_tests}")
    print(f"Passed: {results.passed}")
    print(f"Failed: {results.failed}")
    print(f"Skipped: {results.skipped}")
    print(f"Errors: {results.errors}")
    print(f"Duration: {results.duration:.2f}s")
    print(f"Summary: {results.summary}")
    print(f"{'='*60}")
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(asdict(results), f, indent=2, default=str)
        print(f"Results saved to {args.output}")

if __name__ == "__main__":
    main()
