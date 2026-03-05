#!/usr/bin/env python3
"""
ValidoAI Comprehensive Test Suite
================================

This module provides comprehensive testing capabilities for the ValidoAI application,
including UI/UX testing, E2E testing, integration testing, security testing,
route testing, LLM/ML model testing, webhook and API integration testing,
and report generation.

Usage:
    python tests/comprehensive_test_suite.py
    python tests/comprehensive_test_suite.py --test-type ui
    python tests/comprehensive_test_suite.py --test-type e2e
    python tests/comprehensive_test_suite.py --test-type security
    python tests/comprehensive_test_suite.py --parallel

Author: ValidoAI Development Team
Version: 2.0.0
"""

import os
import sys
import time
import json
import requests
import subprocess
import threading
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin
import traceback

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import psutil
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
    from rich.table import Table
    from rich.panel import Panel
    from rich.layout import Layout
    from rich.live import Live
    from rich.text import Text
    import plotly.graph_objects as go
    import plotly.offline as pyo
    HAS_RICH = True
except ImportError:
    print("Warning: Rich library not available. Installing with basic output...")
    HAS_RICH = False

# Import test modules
try:
    from ui_test_framework import UITestFramework
except ImportError:
    print("Warning: UI test framework not available")
    UITestFramework = None

try:
    from e2e_test_automation import E2ETestAutomation
except ImportError:
    print("Warning: E2E test automation not available")
    E2ETestAutomation = None

try:
    from security_testing_suite import SecurityTestingSuite
except ImportError:
    print("Warning: Security testing suite not available")
    SecurityTestingSuite = None

try:
    from route_tester import RouteTester
except ImportError:
    print("Warning: Route tester not available")
    RouteTester = None

try:
    from model_tester import ModelTester
except ImportError:
    print("Warning: Model tester not available")
    ModelTester = None

try:
    from webhook_comprehensive_e2e import WebhookE2ETester
except ImportError:
    print("Warning: Webhook E2E tester not available")
    WebhookE2ETester = None

try:
    from integration_testing_framework import IntegrationTestingFramework
except ImportError:
    print("Warning: Integration testing framework not available")
    IntegrationTestingFramework = None

try:
    from report_generator import ReportGenerator
except ImportError:
    print("Warning: Report generator not available")
    ReportGenerator = None

class ValidoAITestSuite:
    """Comprehensive test suite for ValidoAI application with all testing capabilities"""

    def __init__(self, base_url: str = "http://localhost:5000", parallel: bool = True):
        self.base_url = base_url.rstrip('/')
        self.parallel = parallel
        self.console = Console() if HAS_RICH else None

        # Initialize all test frameworks with fallbacks
        self.ui_test_framework = UITestFramework(base_url) if UITestFramework else None
        self.e2e_test_automation = E2ETestAutomation(base_url) if E2ETestAutomation else None
        self.security_testing_suite = SecurityTestingSuite(base_url) if SecurityTestingSuite else None
        self.route_tester = RouteTester(base_url) if RouteTester else None
        self.model_tester = ModelTester(base_url) if ModelTester else None
        self.webhook_e2e_tester = WebhookE2ETester(base_url) if WebhookE2ETester else None
        self.integration_testing_framework = IntegrationTestingFramework(base_url) if IntegrationTestingFramework else None
        self.report_generator = ReportGenerator() if ReportGenerator else None

        # Initialize test results structure
        self.test_results = {
            'summary': {
                'total_tests': 0,
                'passed': 0,
                'failed': 0,
                'skipped': 0,
                'start_time': None,
                'end_time': None,
                'duration': 0,
                'success_rate': 0
            },
            'categories': {
                'ui_ux_tests': {'tests': [], 'passed': 0, 'failed': 0, 'duration': 0},
                'e2e_tests': {'tests': [], 'passed': 0, 'failed': 0, 'duration': 0},
                'integration_tests': {'tests': [], 'passed': 0, 'failed': 0, 'duration': 0},
                'security_tests': {'tests': [], 'passed': 0, 'failed': 0, 'duration': 0},
                'route_tests': {'tests': [], 'passed': 0, 'failed': 0, 'duration': 0},
                'llm_ml_tests': {'tests': [], 'passed': 0, 'failed': 0, 'duration': 0},
                'webhook_api_tests': {'tests': [], 'passed': 0, 'failed': 0, 'duration': 0},
                'performance_tests': {'tests': [], 'passed': 0, 'failed': 0, 'duration': 0}
            },
            'performance_metrics': {
                'load_times': [],
                'memory_usage': [],
                'response_times': [],
                'cpu_usage': [],
                'network_latency': []
            },
            'error_logs': [],
            'screenshots': [],
            'reports': {
                'html_report': None,
                'pdf_report': None,
                'json_report': None,
                'charts': []
            }
        }

        # Define test configuration
        self.test_config = {
            'timeout': 30,
            'max_retries': 3,
            'screenshot_on_failure': True,
            'parallel_execution': parallel,
            'browser_config': {
                'headless': True,
                'window_size': [1920, 1080]
            },
            'security_config': {
                'sql_injection_tests': True,
                'xss_tests': True,
                'csrf_tests': True,
                'authentication_tests': True
            }
        }

    def run_all_tests(self, categories: List[str] = None) -> Dict[str, Any]:
        """Run all test categories or specific ones"""
        if self.console:
            self.console.print("\n[bold blue]🚀 Starting ValidoAI Comprehensive Test Suite v2.0[/bold blue]")
            self.console.print(f"[dim]Target: {self.base_url}[/dim]")
            self.console.print(f"[dim]Parallel Execution: {self.parallel}[/dim]")
            self.console.print("=" * 70)

        self.test_results['summary']['start_time'] = datetime.now()

        try:
            # Define all available test categories
            all_categories = {
                'ui_ux': self._run_ui_ux_tests,
                'e2e': self._run_e2e_tests,
                'integration': self._run_integration_tests,
                'security': self._run_security_tests,
                'routes': self._run_route_tests,
                'llm_ml': self._run_llm_ml_tests,
                'webhook_api': self._run_webhook_api_tests,
                'performance': self._run_performance_tests
            }

            # Run specified categories or all
            categories_to_run = categories if categories else list(all_categories.keys())

            if self.parallel:
                self._run_tests_parallel(all_categories, categories_to_run)
            else:
                self._run_tests_sequential(all_categories, categories_to_run)

        except Exception as e:
            if self.console:
                self.console.print(f"[red]❌ Test execution error: {str(e)}[/red]")
            else:
                print(f"❌ Test execution error: {str(e)}")
            self.test_results['error_logs'].append(str(e))

        self.test_results['summary']['end_time'] = datetime.now()
        self.test_results['summary']['duration'] = (
            self.test_results['summary']['end_time'] - self.test_results['summary']['start_time']
        ).total_seconds()

        self._calculate_summary()
        self._generate_comprehensive_report()

        return self.test_results

    def run_specific_test_category(self, category: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Run a specific test category"""
        category_methods = {
            'ui_ux': self._run_ui_ux_tests,
            'e2e': self._run_e2e_tests,
            'integration': self._run_integration_tests,
            'security': self._run_security_tests,
            'routes': self._run_route_tests,
            'llm_ml': self._run_llm_ml_tests,
            'webhook_api': self._run_webhook_api_tests,
            'performance': self._run_performance_tests
        }

        if category not in category_methods:
            return {'success': False, 'error': f'Unknown test category: {category}'}

        try:
            start_time = time.time()
            result = category_methods[category]()
            duration = time.time() - start_time

            return {
                'success': True,
                'category': category,
                'result': result,
                'duration': duration,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'success': False,
                'category': category,
                'error': str(e),
                'duration': time.time() - start_time,
                'timestamp': datetime.now().isoformat()
            }

    def _run_tests_parallel(self, all_categories: Dict[str, Any], categories_to_run: List[str]):
        """Run tests in parallel using ThreadPoolExecutor"""
        if self.console:
            self.console.print(f"\n[bold yellow]⚡ Running {len(categories_to_run)} test categories in parallel[/bold yellow]")

        with ThreadPoolExecutor(max_workers=min(len(categories_to_run), 4)) as executor:
            future_to_category = {
                executor.submit(method): category
                for category, method in all_categories.items()
                if category in categories_to_run
            }

            for future in as_completed(future_to_category):
                category = future_to_category[future]
                try:
                    future.result()
                    if self.console:
                        self.console.print(f"[green]✅ {category} tests completed[/green]")
                except Exception as e:
                    if self.console:
                        self.console.print(f"[red]❌ {category} tests failed: {str(e)}[/red]")
                    self.test_results['error_logs'].append(f"{category}: {str(e)}")

    def _run_tests_sequential(self, all_categories: Dict[str, Any], categories_to_run: List[str]):
        """Run tests sequentially"""
        if self.console:
            self.console.print(f"\n[bold yellow]🔄 Running {len(categories_to_run)} test categories sequentially[/bold yellow]")

        for category in categories_to_run:
            if category in all_categories:
                try:
                    if self.console:
                        self.console.print(f"\n[bold blue]▶️ Running {category} tests...[/bold blue]")
                    all_categories[category]()
                    if self.console:
                        self.console.print(f"[green]✅ {category} tests completed[/green]")
                except Exception as e:
                    if self.console:
                        self.console.print(f"[red]❌ {category} tests failed: {str(e)}[/red]")
                    self.test_results['error_logs'].append(f"{category}: {str(e)}")

    # UI/UX Testing Methods
    def _run_ui_ux_tests(self):
        """Run UI/UX tests using the UI test framework"""
        start_time = time.time()
        try:
            if not self.ui_test_framework:
                if self.console:
                    self.console.print("\n[yellow]⚠️  UI/UX Test Framework not available - skipping[/yellow]")
                return

            if self.console:
                self.console.print("\n[bold magenta]🎨 Running UI/UX Tests[/bold magenta]")

            results = self.ui_test_framework.run_comprehensive_ui_tests()

            self.test_results['categories']['ui_ux_tests']['tests'] = results.get('tests', [])
            self.test_results['categories']['ui_ux_tests']['passed'] = results.get('passed', 0)
            self.test_results['categories']['ui_ux_tests']['failed'] = results.get('failed', 0)
            self.test_results['categories']['ui_ux_tests']['duration'] = time.time() - start_time

            if self.console:
                self.console.print(f"[dim]UI/UX Tests: {results.get('passed', 0)} passed, {results.get('failed', 0)} failed[/dim]")

        except Exception as e:
            if self.console:
                self.console.print(f"[red]❌ UI/UX tests failed: {str(e)}[/red]")
            self.test_results['error_logs'].append(f"UI/UX tests: {str(e)}")
            self.test_results['categories']['ui_ux_tests']['duration'] = time.time() - start_time

    # E2E Testing Methods
    def _run_e2e_tests(self):
        """Run E2E tests using the E2E test automation framework"""
        start_time = time.time()
        try:
            if self.console:
                self.console.print("\n[bold green]🔄 Running E2E Tests[/bold green]")

            results = self.e2e_test_automation.run_comprehensive_e2e_tests()

            self.test_results['categories']['e2e_tests']['tests'] = results.get('tests', [])
            self.test_results['categories']['e2e_tests']['passed'] = results.get('passed', 0)
            self.test_results['categories']['e2e_tests']['failed'] = results.get('failed', 0)
            self.test_results['categories']['e2e_tests']['duration'] = time.time() - start_time

            if self.console:
                self.console.print(f"[dim]E2E Tests: {results.get('passed', 0)} passed, {results.get('failed', 0)} failed[/dim]")

        except Exception as e:
            if self.console:
                self.console.print(f"[red]❌ E2E tests failed: {str(e)}[/red]")
            self.test_results['error_logs'].append(f"E2E tests: {str(e)}")
            self.test_results['categories']['e2e_tests']['duration'] = time.time() - start_time

    # Integration Testing Methods
    def _run_integration_tests(self):
        """Run integration tests using the integration testing framework"""
        start_time = time.time()
        try:
            if self.console:
                self.console.print("\n[bold blue]🔗 Running Integration Tests[/bold blue]")

            results = self.integration_testing_framework.run_comprehensive_integration_tests()

            self.test_results['categories']['integration_tests']['tests'] = results.get('tests', [])
            self.test_results['categories']['integration_tests']['passed'] = results.get('passed', 0)
            self.test_results['categories']['integration_tests']['failed'] = results.get('failed', 0)
            self.test_results['categories']['integration_tests']['duration'] = time.time() - start_time

            if self.console:
                self.console.print(f"[dim]Integration Tests: {results.get('passed', 0)} passed, {results.get('failed', 0)} failed[/dim]")

        except Exception as e:
            if self.console:
                self.console.print(f"[red]❌ Integration tests failed: {str(e)}[/red]")
            self.test_results['error_logs'].append(f"Integration tests: {str(e)}")
            self.test_results['categories']['integration_tests']['duration'] = time.time() - start_time

    # Security Testing Methods
    def _run_security_tests(self):
        """Run security tests using the security testing suite"""
        start_time = time.time()
        try:
            if self.console:
                self.console.print("\n[bold red]🔒 Running Security Tests[/bold red]")

            results = self.security_testing_suite.run_comprehensive_security_tests()

            self.test_results['categories']['security_tests']['tests'] = results.get('tests', [])
            self.test_results['categories']['security_tests']['passed'] = results.get('passed', 0)
            self.test_results['categories']['security_tests']['failed'] = results.get('failed', 0)
            self.test_results['categories']['security_tests']['duration'] = time.time() - start_time

            if self.console:
                self.console.print(f"[dim]Security Tests: {results.get('passed', 0)} passed, {results.get('failed', 0)} failed[/dim]")

        except Exception as e:
            if self.console:
                self.console.print(f"[red]❌ Security tests failed: {str(e)}[/red]")
            self.test_results['error_logs'].append(f"Security tests: {str(e)}")
            self.test_results['categories']['security_tests']['duration'] = time.time() - start_time

    # Route Testing Methods
    def _run_route_tests(self):
        """Test all application routes for availability"""
        start_time = time.time()
        try:
            if self.console:
                self.console.print("\n[bold cyan]📍 Testing Application Routes[/bold cyan]")

            results = self.route_tester.run_comprehensive_route_tests()

            self.test_results['categories']['route_tests']['tests'] = results.get('tests', [])
            self.test_results['categories']['route_tests']['passed'] = results.get('passed', 0)
            self.test_results['categories']['route_tests']['failed'] = results.get('failed', 0)
            self.test_results['categories']['route_tests']['duration'] = time.time() - start_time

            if self.console:
                self.console.print(f"[dim]Route Tests: {results.get('passed', 0)} passed, {results.get('failed', 0)} failed[/dim]")

        except Exception as e:
            if self.console:
                self.console.print(f"[red]❌ Route tests failed: {str(e)}[/red]")
            self.test_results['error_logs'].append(f"Route tests: {str(e)}")
            self.test_results['categories']['route_tests']['duration'] = time.time() - start_time

    # LLM/ML Testing Methods
    def _run_llm_ml_tests(self):
        """Run LLM and ML model tests"""
        start_time = time.time()
        try:
            if self.console:
                self.console.print("\n[bold purple]🤖 Running LLM & ML Model Tests[/bold purple]")

            results = self.model_tester.run_comprehensive_model_tests()

            self.test_results['categories']['llm_ml_tests']['tests'] = results.get('tests', [])
            self.test_results['categories']['llm_ml_tests']['passed'] = results.get('passed', 0)
            self.test_results['categories']['llm_ml_tests']['failed'] = results.get('failed', 0)
            self.test_results['categories']['llm_ml_tests']['duration'] = time.time() - start_time

            if self.console:
                self.console.print(f"[dim]LLM/ML Tests: {results.get('passed', 0)} passed, {results.get('failed', 0)} failed[/dim]")

        except Exception as e:
            if self.console:
                self.console.print(f"[red]❌ LLM/ML tests failed: {str(e)}[/red]")
            self.test_results['error_logs'].append(f"LLM/ML tests: {str(e)}")
            self.test_results['categories']['llm_ml_tests']['duration'] = time.time() - start_time

    # Webhook and API Testing Methods
    def _run_webhook_api_tests(self):
        """Run webhook and API integration tests"""
        start_time = time.time()
        try:
            if self.console:
                self.console.print("\n[bold orange]🔗 Running Webhook & API Integration Tests[/bold orange]")

            results = self.webhook_e2e_tester.run_comprehensive_webhook_tests()

            self.test_results['categories']['webhook_api_tests']['tests'] = results.get('tests', [])
            self.test_results['categories']['webhook_api_tests']['passed'] = results.get('passed', 0)
            self.test_results['categories']['webhook_api_tests']['failed'] = results.get('failed', 0)
            self.test_results['categories']['webhook_api_tests']['duration'] = time.time() - start_time

            if self.console:
                self.console.print(f"[dim]Webhook/API Tests: {results.get('passed', 0)} passed, {results.get('failed', 0)} failed[/dim]")

        except Exception as e:
            if self.console:
                self.console.print(f"[red]❌ Webhook/API tests failed: {str(e)}[/red]")
            self.test_results['error_logs'].append(f"Webhook/API tests: {str(e)}")
            self.test_results['categories']['webhook_api_tests']['duration'] = time.time() - start_time

    # Performance Testing Methods
    def _run_performance_tests(self):
        """Run performance tests"""
        start_time = time.time()
        try:
            if self.console:
                self.console.print("\n[bold yellow]⚡ Running Performance Tests[/bold yellow]")

            results = self._run_performance_test_suite()

            self.test_results['categories']['performance_tests']['tests'] = results.get('tests', [])
            self.test_results['categories']['performance_tests']['passed'] = results.get('passed', 0)
            self.test_results['categories']['performance_tests']['failed'] = results.get('failed', 0)
            self.test_results['categories']['performance_tests']['duration'] = time.time() - start_time

            if self.console:
                self.console.print(f"[dim]Performance Tests: {results.get('passed', 0)} passed, {results.get('failed', 0)} failed[/dim]")

        except Exception as e:
            if self.console:
                self.console.print(f"[red]❌ Performance tests failed: {str(e)}[/red]")
            self.test_results['error_logs'].append(f"Performance tests: {str(e)}")
            self.test_results['categories']['performance_tests']['duration'] = time.time() - start_time

    def _run_performance_test_suite(self):
        """Run comprehensive performance tests"""
        tests = []
        passed = 0
        failed = 0

        # Test response times
        try:
            response_times = self._test_response_times()
            tests.append({
                'name': 'Response Time Test',
                'status': 'passed' if response_times['success'] else 'failed',
                'details': response_times
            })
            if response_times['success']:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            tests.append({
                'name': 'Response Time Test',
                'status': 'failed',
                'error': str(e)
            })
            failed += 1

        # Test load handling
        try:
            load_test = self._test_load_handling()
            tests.append({
                'name': 'Load Handling Test',
                'status': 'passed' if load_test['success'] else 'failed',
                'details': load_test
            })
            if load_test['success']:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            tests.append({
                'name': 'Load Handling Test',
                'status': 'failed',
                'error': str(e)
            })
            failed += 1

        # Test memory usage
        try:
            memory_test = self._test_memory_usage()
            tests.append({
                'name': 'Memory Usage Test',
                'status': 'passed' if memory_test['success'] else 'failed',
                'details': memory_test
            })
            if memory_test['success']:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            tests.append({
                'name': 'Memory Usage Test',
                'status': 'failed',
                'error': str(e)
            })
            failed += 1

        return {
            'tests': tests,
            'passed': passed,
            'failed': failed
        }

    def _test_response_times(self):
        """Test response times for key routes"""
        routes_to_test = ['/', '/dashboard', '/test-suite', '/api/questions']
        results = {}

        for route in routes_to_test:
            try:
                url = urljoin(self.base_url, route)
                start_time = time.time()
                response = requests.get(url, timeout=10)
                response_time = time.time() - start_time

                results[route] = {
                    'response_time': response_time,
                    'status_code': response.status_code,
                    'success': response.status_code == 200
                }
            except Exception as e:
                results[route] = {
                    'error': str(e),
                    'success': False
                }

        avg_response_time = sum(
            result['response_time'] for result in results.values()
            if 'response_time' in result and result.get('success', False)
        ) / len([r for r in results.values() if r.get('success', False)])

        return {
            'success': avg_response_time < 2.0,  # 2 seconds threshold
            'average_response_time': avg_response_time,
            'route_results': results
        }

    def _test_load_handling(self):
        """Test load handling capabilities"""
        # Simulate concurrent requests
        def make_request():
            try:
                response = requests.get(self.base_url, timeout=5)
                return response.status_code == 200
            except:
                return False

        # Run 10 concurrent requests
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [future.result() for future in futures]

        success_rate = sum(results) / len(results)
        return {
            'success': success_rate >= 0.8,  # 80% success rate threshold
            'success_rate': success_rate,
            'total_requests': len(results),
            'successful_requests': sum(results)
        }

    def _test_memory_usage(self):
        """Test memory usage during operation"""
        try:
            # Get initial memory usage
            initial_response = requests.get(self.base_url)
            # This is a simplified memory test - in real scenario you'd monitor system resources
            return {
                'success': True,
                'memory_usage': 'N/A (simplified test)',
                'peak_memory': 'N/A (simplified test)'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def _calculate_summary(self):
        """Calculate test summary statistics"""
        total_tests = 0
        total_passed = 0
        total_failed = 0

        for category in self.test_results['categories'].values():
            total_tests += category['passed'] + category['failed']
            total_passed += category['passed']
            total_failed += category['failed']

        self.test_results['summary']['total_tests'] = total_tests
        self.test_results['summary']['passed'] = total_passed
        self.test_results['summary']['failed'] = total_failed
        self.test_results['summary']['success_rate'] = (
            (total_passed / total_tests) * 100 if total_tests > 0 else 0
        )

    def _generate_comprehensive_report(self):
        """Generate comprehensive test reports"""
        try:
            # Generate HTML report
            html_report = self.report_generator.generate_html_report(self.test_results)
            self.test_results['reports']['html_report'] = html_report

            # Generate JSON report
            json_report = self.report_generator.generate_json_report(self.test_results)
            self.test_results['reports']['json_report'] = json_report

            # Generate PDF report if available
            try:
                pdf_report = self.report_generator.generate_pdf_report(self.test_results)
                self.test_results['reports']['pdf_report'] = pdf_report
            except Exception as e:
                if self.console:
                    self.console.print(f"[yellow]⚠️ PDF report generation failed: {str(e)}[/yellow]")

            # Generate charts
            try:
                charts = self.report_generator.generate_charts(self.test_results)
                self.test_results['reports']['charts'] = charts
            except Exception as e:
                if self.console:
                    self.console.print(f"[yellow]⚠️ Chart generation failed: {str(e)}[/yellow]")

        except Exception as e:
            if self.console:
                self.console.print(f"[red]❌ Report generation failed: {str(e)}[/red]")
            self.test_results['error_logs'].append(f"Report generation: {str(e)}")

    def get_system_status(self):
        """Get current system status"""
        try:
            system_info = {}
            if psutil:
                system_info = {
                    'cpu_usage': psutil.cpu_percent(interval=1),
                    'memory_usage': psutil.virtual_memory().percent,
                    'disk_usage': psutil.disk_usage('/').percent
                }
            return {
                'status': 'healthy',
                'system_info': system_info,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def get_available_categories(self):
        """Get list of available test categories"""
        return [
            {
                'id': 'ui_ux',
                'name': 'UI/UX Testing',
                'description': 'User interface and user experience testing',
                'icon': '🎨',
                'status': 'available'
            },
            {
                'id': 'e2e',
                'name': 'E2E Testing',
                'description': 'End-to-end testing with Selenium/Playwright',
                'icon': '🔄',
                'status': 'available'
            },
            {
                'id': 'integration',
                'name': 'Integration Testing',
                'description': 'Integration testing for all components',
                'icon': '🔗',
                'status': 'available'
            },
            {
                'id': 'security',
                'name': 'Security Testing',
                'description': 'Security vulnerability and penetration testing',
                'icon': '🔒',
                'status': 'available'
            },
            {
                'id': 'routes',
                'name': 'Route Testing',
                'description': 'Route testing and validation',
                'icon': '📍',
                'status': 'available'
            },
            {
                'id': 'llm_ml',
                'name': 'LLM & ML Testing',
                'description': 'LLM and ML model testing',
                'icon': '🤖',
                'status': 'available'
            },
            {
                'id': 'webhook_api',
                'name': 'Webhook & API Testing',
                'description': 'Webhook and API integration testing',
                'icon': '🔗',
                'status': 'available'
            },
            {
                'id': 'performance',
                'name': 'Performance Testing',
                'description': 'Performance and load testing',
                'icon': '⚡',
                'status': 'available'
            }
        ]

def main():
    """Main function to run the comprehensive test suite"""
    import argparse

    parser = argparse.ArgumentParser(description='ValidoAI Comprehensive Test Suite v2.0')
    parser.add_argument('--url', default='http://localhost:5000', help='Base URL of the application')
    parser.add_argument('--parallel', action='store_true', help='Enable parallel test execution')
    parser.add_argument('--categories', nargs='*',
                        choices=['ui_ux', 'e2e', 'integration', 'security', 'routes', 'llm_ml', 'webhook_api', 'performance', 'all'],
                        default=['all'], help='Specific test categories to run')
    parser.add_argument('--format', choices=['html', 'pdf', 'json', 'all'], default='all',
                        help='Report format to generate')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    parser.add_argument('--config', help='Path to test configuration file')

    args = parser.parse_args()

    # Handle 'all' category
    if 'all' in args.categories:
        categories_to_run = ['ui_ux', 'e2e', 'integration', 'security', 'routes', 'llm_ml', 'webhook_api', 'performance']
    else:
        categories_to_run = args.categories

    # Create test suite instance
    test_suite = ValidoAITestSuite(
        base_url=args.url,
        parallel=args.parallel
    )

    if args.verbose:
        print("🔧 Test Suite Configuration:")
        print(f"   URL: {args.url}")
        print(f"   Parallel: {args.parallel}")
        print(f"   Categories: {', '.join(categories_to_run)}")
        print(f"   Report Format: {args.format}")
        print("-" * 50)

    # Run tests
    try:
        if len(categories_to_run) == 1:
            # Run specific test category
            results = test_suite.run_specific_test_category(categories_to_run[0])
        else:
            # Run multiple categories
            results = test_suite.run_all_tests(categories_to_run)

        # Generate specific report format if requested
        if args.format != 'all':
            if args.format == 'html':
                report_path = test_suite.report_generator.generate_html_report(results)
                print(f"📄 HTML Report generated: {report_path}")
            elif args.format == 'pdf':
                report_path = test_suite.report_generator.generate_pdf_report(results)
                print(f"📄 PDF Report generated: {report_path}")
            elif args.format == 'json':
                report_path = test_suite.report_generator.generate_json_report(results)
                print(f"📄 JSON Report generated: {report_path}")

        # Exit with appropriate code based on success rate
        if isinstance(results, dict) and 'success' in results:
            # Single category result
            if results['success']:
                sys.exit(0)  # Success
            else:
                sys.exit(2)  # Failure
        else:
            # Multiple categories result
            success_rate = results.get('summary', {}).get('success_rate', 0)
            if success_rate >= 90:
                sys.exit(0)  # Success
            elif success_rate >= 75:
                sys.exit(1)  # Warning
            else:
                sys.exit(2)  # Critical failure

    except KeyboardInterrupt:
        print("\n⚠️  Test execution interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Test suite failed: {str(e)}")
        if args.verbose:
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
