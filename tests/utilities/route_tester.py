#!/usr/bin/env python3
"""
ValidoAI Route Tester
====================

This module provides comprehensive route testing for the ValidoAI application,
checking all endpoints for availability, response codes, and basic functionality.

Usage:
    python tests/route_tester.py
    python tests/route_tester.py --url http://localhost:5000

Author: ValidoAI Development Team
Version: 1.0.0
"""

import os
import sys
import time
import requests
import json
from datetime import datetime
from typing import Dict, List, Any
from urllib.parse import urljoin

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class RouteTester:
    """Comprehensive route testing for ValidoAI application"""

    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url.rstrip('/')
        self.test_results = {
            'summary': {
                'total_routes': 0,
                'passed': 0,
                'failed': 0,
                'warnings': 0,
                'start_time': None,
                'end_time': None,
                'duration': 0
            },
            'routes': [],
            'performance_metrics': []
        }

        # Define all routes to test with expected status codes
        self.routes_config = [
            {'path': '/', 'method': 'GET', 'expected_status': 200, 'description': 'Dashboard/Homepage'},
            {'path': '/ui-examples', 'method': 'GET', 'expected_status': 200, 'description': 'UI Examples Page'},
            {'path': '/docs', 'method': 'GET', 'expected_status': 200, 'description': 'API Documentation'},
            {'path': '/database-example', 'method': 'GET', 'expected_status': 200, 'description': 'Database Management'},
            {'path': '/test-suite', 'method': 'GET', 'expected_status': 200, 'description': 'Test Suite'},
            {'path': '/ml-algorithms-demo', 'method': 'GET', 'expected_status': 200, 'description': 'ML Algorithms Demo'},
            {'path': '/api-docs', 'method': 'GET', 'expected_status': 200, 'description': 'API Documentation JSON'},
            {'path': '/theme-switcher', 'method': 'GET', 'expected_status': 200, 'description': 'Theme Switcher Modal'},
            {'path': '/nonexistent', 'method': 'GET', 'expected_status': 404, 'description': '404 Error Page'},
            {'path': '/api/nonexistent', 'method': 'GET', 'expected_status': 404, 'description': 'API 404 Error'},
        ]

        # API endpoints to test
        self.api_routes_config = [
            {'path': '/api/questions', 'method': 'GET', 'expected_status': 200, 'description': 'Get Questions'},
            {'path': '/api/questions', 'method': 'POST', 'expected_status': 201, 'description': 'Create Question'},
            {'path': '/api/questions/categories', 'method': 'GET', 'expected_status': 200, 'description': 'Get Categories'},
            {'path': '/api/questions/stats', 'method': 'GET', 'expected_status': 200, 'description': 'Get Statistics'},
            {'path': '/api/database/connections', 'method': 'GET', 'expected_status': 200, 'description': 'Database Connections'},
            {'path': '/api/theme/info', 'method': 'GET', 'expected_status': 200, 'description': 'Theme Information'},
            {'path': '/api/test/run', 'method': 'POST', 'expected_status': 200, 'description': 'Run Tests'},
            {'path': '/api/test/status/test_001', 'method': 'GET', 'expected_status': 200, 'description': 'Test Status'},
        ]

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all route tests"""
        print(f"\n🚀 Starting ValidoAI Route Tests")
        print(f"Target: {self.base_url}")
        print("=" * 60)

        self.test_results['summary']['start_time'] = datetime.now()

        # Test main routes
        self._test_main_routes()

        # Test API routes
        self._test_api_routes()

        # Test error handling
        self._test_error_handling()

        self.test_results['summary']['end_time'] = datetime.now()
        self.test_results['summary']['duration'] = (
            self.test_results['summary']['end_time'] - self.test_results['summary']['start_time']
        ).total_seconds()

        self._calculate_summary()
        self._generate_report()

        return self.test_results

    def _test_main_routes(self):
        """Test main application routes"""
        print("\n📍 Testing Main Routes")
        print("-" * 40)

        for route_config in self.routes_config:
            if route_config['path'].startswith('/api'):
                continue  # Skip API routes for now

            self._test_single_route(route_config)

    def _test_api_routes(self):
        """Test API endpoints"""
        print("\n🔧 Testing API Routes")
        print("-" * 40)

        for route_config in self.api_routes_config:
            self._test_single_route(route_config)

    def _test_error_handling(self):
        """Test error handling routes"""
        print("\n🚨 Testing Error Handling")
        print("-" * 40)

        error_routes = [
            {'path': '/nonexistent', 'method': 'GET', 'expected_status': 404, 'description': '404 Error Page'},
            {'path': '/api/nonexistent', 'method': 'GET', 'expected_status': 404, 'description': 'API 404 Error'},
            {'path': '/admin', 'method': 'GET', 'expected_status': 404, 'description': 'Unauthorized Access'},
        ]

        for route_config in error_routes:
            self._test_single_route(route_config)

    def _test_single_route(self, route_config: Dict[str, Any]):
        """Test a single route"""
        try:
            url = urljoin(self.base_url, route_config['path'])
            method = route_config['method']
            expected_status = route_config['expected_status']
            description = route_config['description']

            start_time = time.time()

            # Prepare request data
            if method == 'GET':
                response = requests.get(url, timeout=10)
            elif method == 'POST':
                if 'api/test/run' in url:
                    data = {'test_type': 'ui'}
                else:
                    data = {'test': 'data'}
                response = requests.post(url, json=data, timeout=10)
            else:
                response = requests.get(url, timeout=10)

            load_time = time.time() - start_time

            # Determine test result
            actual_status = response.status_code
            if actual_status == expected_status:
                status = 'PASSED'
                color = 'green'
                symbol = '✅'
            elif actual_status == 200 and expected_status == 404:
                status = 'WARNING'
                color = 'yellow'
                symbol = '⚠️ '
            else:
                status = 'FAILED'
                color = 'red'
                symbol = '❌'

            # Create test result
            result = {
                'path': route_config['path'],
                'method': method,
                'expected_status': expected_status,
                'actual_status': actual_status,
                'status': status,
                'description': description,
                'load_time': load_time,
                'response_size': len(response.content),
                'content_type': response.headers.get('content-type', 'unknown'),
                'timestamp': datetime.now().isoformat()
            }

            self.test_results['routes'].append(result)
            self.test_results['performance_metrics'].append({
                'path': route_config['path'],
                'load_time': load_time,
                'status_code': actual_status
            })

            # Print result
            print(".2f"
            # Additional checks for successful responses
            if actual_status == 200 and method == 'GET':
                self._check_route_content(url, response.text, route_config['path'])

        except requests.exceptions.Timeout:
            result = {
                'path': route_config['path'],
                'method': route_config['method'],
                'expected_status': route_config['expected_status'],
                'actual_status': None,
                'status': 'FAILED',
                'description': route_config['description'],
                'load_time': None,
                'error': 'Timeout',
                'timestamp': datetime.now().isoformat()
            }
            self.test_results['routes'].append(result)
            print(f"❌ {route_config['method']} {route_config['path']} - TIMEOUT")

        except requests.exceptions.ConnectionError:
            result = {
                'path': route_config['path'],
                'method': route_config['method'],
                'expected_status': route_config['expected_status'],
                'actual_status': None,
                'status': 'FAILED',
                'description': route_config['description'],
                'load_time': None,
                'error': 'Connection Error',
                'timestamp': datetime.now().isoformat()
            }
            self.test_results['routes'].append(result)
            print(f"❌ {route_config['method']} {route_config['path']} - CONNECTION ERROR")

        except Exception as e:
            result = {
                'path': route_config['path'],
                'method': route_config['method'],
                'expected_status': route_config['expected_status'],
                'actual_status': None,
                'status': 'FAILED',
                'description': route_config['description'],
                'load_time': None,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            self.test_results['routes'].append(result)
            print(f"❌ {route_config['method']} {route_config['path']} - ERROR: {str(e)}")

    def _check_route_content(self, url: str, content: str, path: str):
        """Check route content for expected elements"""
        checks = {
            '/': ['dashboard', 'theme', 'sidebar'],
            '/ui-examples': ['ui-examples', 'component', 'theme'],
            '/docs': ['swagger-ui', 'api', 'documentation'],
            '/database-example': ['database', 'table', 'connection'],
            '/test-suite': ['test', 'suite', 'automation'],
        }

        if path in checks:
            missing_elements = []
            for element in checks[path]:
                if element.lower() not in content.lower():
                    missing_elements.append(element)

            if missing_elements:
                print(f"   ⚠️  Missing expected elements: {', '.join(missing_elements)}")

    def _calculate_summary(self):
        """Calculate test summary"""
        total_routes = len(self.test_results['routes'])
        passed = len([r for r in self.test_results['routes'] if r['status'] == 'PASSED'])
        failed = len([r for r in self.test_results['routes'] if r['status'] == 'FAILED'])
        warnings = len([r for r in self.test_results['routes'] if r['status'] == 'WARNING'])

        self.test_results['summary']['total_routes'] = total_routes
        self.test_results['summary']['passed'] = passed
        self.test_results['summary']['failed'] = failed
        self.test_results['summary']['warnings'] = warnings

        if total_routes > 0:
            success_rate = (passed / total_routes) * 100
            self.test_results['summary']['success_rate'] = round(success_rate, 2)
        else:
            self.test_results['summary']['success_rate'] = 0

    def _generate_report(self):
        """Generate test report"""
        print("
📊 Route Test Results Summary"        print("=" * 60)

        summary = self.test_results['summary']
        print(f"Total Routes Tested: {summary['total_routes']}")
        print(f"Passed: {summary['passed']}")
        print(f"Failed: {summary['failed']}")
        print(f"Warnings: {summary['warnings']}")
        print(".2f")
        print(".2f")

        # Performance summary
        if self.test_results['performance_metrics']:
            load_times = [m['load_time'] for m in self.test_results['performance_metrics'] if m['load_time']]
            if load_times:
                avg_load_time = sum(load_times) / len(load_times)
                max_load_time = max(load_times)
                min_load_time = min(load_times)

                print("
⚡ Performance Metrics:"                print(".2f")
                print(".2f")
                print(".2f")

        # Save detailed results
        self._save_results_to_file()

        # Success indicator
        success_rate = summary['success_rate']
        if success_rate >= 90:
            print("
🎉 EXCELLENT! All routes are working correctly!"        elif success_rate >= 75:
            print("
⚠️  GOOD! Most routes are working with minor issues."        else:
            print("
❌ CRITICAL! Many routes have issues and need attention."
    def _save_results_to_file(self):
        """Save test results to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"route_test_results_{timestamp}.json"

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.test_results, f, indent=2, default=str)
            print(f"\n📄 Detailed results saved to: {filename}")
        except Exception as e:
            print(f"❌ Failed to save results: {str(e)}")

def main():
    """Main function to run route tests"""
    import argparse

    parser = argparse.ArgumentParser(description='ValidoAI Route Tester')
    parser.add_argument('--url', default='http://localhost:5000', help='Base URL of the application')

    args = parser.parse_args()

    # Create route tester instance
    route_tester = RouteTester(base_url=args.url)

    # Run tests
    try:
        results = route_tester.run_all_tests()

        # Exit with appropriate code
        success_rate = results['summary']['success_rate']
        if success_rate >= 90:
            sys.exit(0)  # Success
        elif success_rate >= 75:
            sys.exit(1)  # Warning
        else:
            sys.exit(2)  # Critical failure

    except KeyboardInterrupt:
        print("\n⚠️  Route testing interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Route testing failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
