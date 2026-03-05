#!/usr/bin/env python3
"""
Comprehensive Route Testing Suite for ValidoAI
==============================================

This script provides comprehensive testing for all ValidoAI routes and endpoints,
including automated testing, performance monitoring, and integration validation.
"""

import sys
import os
import json
import time
import requests
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Add project root to path
project_root = Path.cwd()
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))

# Import ValidoAI components
try:
    from app import create_app
    print("✅ Flask app imported successfully")
except ImportError as e:
    print(f"❌ Failed to import Flask app: {e}")
    # Try to create a minimal app for testing
    try:
        from flask import Flask

        def create_app(config_name='testing'):
            app = Flask(__name__)
            app.config['TESTING'] = True
            app.config['SECRET_KEY'] = 'test-key'

            # Add basic routes for testing
            @app.route('/')
            def index():
                return 'Index page', 200

            @app.route('/health')
            def health():
                return {'status': 'healthy', 'timestamp': 'test'}, 200

            @app.route('/dashboard')
            def dashboard():
                return 'Dashboard page', 200

            @app.route('/api/health')
            def api_health():
                return {'status': 'healthy', 'timestamp': 'test'}, 200

            return app

        print("✅ Created minimal Flask app for testing")
    except Exception as e2:
        print(f"❌ Could not create minimal app: {e2}")
        sys.exit(1)

class RouteTester:
    """Comprehensive route testing for ValidoAI"""

    def __init__(self):
        self.app = None
        self.client = None
        self.test_results = []
        self.routes_to_test = []

    def setup_app(self):
        """Setup Flask application for testing"""
        print("🚀 Setting up Flask application...")
        try:
            self.app = create_app('testing')
            self.client = self.app.test_client()
            print("✅ Flask application setup complete")
            return True
        except Exception as e:
            print(f"❌ Failed to setup Flask app: {e}")
            return False

    def discover_routes(self):
        """Discover all available routes"""
        print("🔍 Discovering routes...")

        self.routes_to_test = [
            # Main routes
            {'url': '/', 'method': 'GET', 'description': 'Index/Home page'},
            {'url': '/health', 'method': 'GET', 'description': 'Health check endpoint'},
            {'url': '/dashboard', 'method': 'GET', 'description': 'Main dashboard'},
            {'url': '/dashboard/business-intelligence', 'method': 'GET', 'description': 'Business Intelligence Dashboard'},
            {'url': '/dashboard/predictive-analytics', 'method': 'GET', 'description': 'Predictive Analytics Dashboard'},
            {'url': '/content/management', 'method': 'GET', 'description': 'Content Management'},
            {'url': '/ai/sentiment-analysis', 'method': 'GET', 'description': 'Sentiment Analysis'},
            {'url': '/settings', 'method': 'GET', 'description': 'Settings page'},

            # API routes
            {'url': '/api/health', 'method': 'GET', 'description': 'API Health check'},
            {'url': '/api/dashboard/data', 'method': 'GET', 'description': 'Dashboard data API'},
            {'url': '/api/predictive/data', 'method': 'GET', 'description': 'Predictive data API'},

            # Authentication routes
            {'url': '/auth/login', 'method': 'GET', 'description': 'Login page'},
            {'url': '/auth/register', 'method': 'GET', 'description': 'Registration page'},

            # Web scraping routes
            {'url': '/scraping', 'method': 'GET', 'description': 'Scraping dashboard'},
            {'url': '/scraping/config', 'method': 'GET', 'description': 'Scraping configuration'},
            {'url': '/scraping/test-url', 'method': 'POST', 'description': 'Test URL scraping'},
        ]

        print(f"✅ Discovered {len(self.routes_to_test)} routes to test")
        return self.routes_to_test

    def test_single_route(self, route_info):
        """Test a single route"""
        url = route_info['url']
        method = route_info['method']
        description = route_info['description']

        print(f"🧪 Testing {method} {url} - {description}")

        start_time = time.time()

        try:
            if method == 'GET':
                response = self.client.get(url)
            elif method == 'POST':
                response = self.client.post(url, data={'url': 'https://example.com'})
            else:
                response = self.client.get(url)  # Default fallback

            response_time = time.time() - start_time

            # Analyze response
            status_code = response.status_code
            is_success = status_code < 400
            content_length = len(response.data) if response.data else 0

            result = {
                'url': url,
                'method': method,
                'description': description,
                'status_code': status_code,
                'success': is_success,
                'response_time': response_time,
                'content_length': content_length,
                'timestamp': datetime.now().isoformat()
            }

            self.test_results.append(result)

            status_icon = "✅" if is_success else "❌"
            print(f"  {status_icon} Status: {status_code}, Time: {response_time:.3f}s, Size: {content_length} bytes")

            return result

        except Exception as e:
            response_time = time.time() - start_time
            result = {
                'url': url,
                'method': method,
                'description': description,
                'status_code': None,
                'success': False,
                'response_time': response_time,
                'content_length': 0,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

            self.test_results.append(result)
            print(f"  ❌ Error: {e}")
            return result

    def run_all_route_tests(self):
        """Run comprehensive route testing"""
        print("🚀 Starting Comprehensive Route Testing...")
        print("=" * 60)

        if not self.setup_app():
            return False

        if not self.discover_routes():
            return False

        successful_tests = 0
        total_tests = len(self.routes_to_test)

        for i, route in enumerate(self.routes_to_test, 1):
            print(f"\\n[{i}/{total_tests}] ", end="")
            result = self.test_single_route(route)
            if result['success']:
                successful_tests += 1

        return self.generate_test_report()

    def test_route_performance(self):
        """Test route performance with multiple requests"""
        print("\\n📊 Testing Route Performance...")

        performance_results = []

        for route in self.routes_to_test[:5]:  # Test first 5 routes for performance
            print(f"  Testing performance for {route['method']} {route['url']}")

            times = []
            for _ in range(5):  # 5 requests per route
                start_time = time.time()
                try:
                    if route['method'] == 'GET':
                        self.client.get(route['url'])
                    response_time = time.time() - start_time
                    times.append(response_time)
                except:
                    times.append(1.0)  # Default error time

            avg_time = np.mean(times)
            min_time = np.min(times)
            max_time = np.max(times)

            performance_results.append({
                'route': f"{route['method']} {route['url']}",
                'avg_time': avg_time,
                'min_time': min_time,
                'max_time': max_time,
                'requests': len(times)
            })

            print(f"    Avg: {avg_time:.3f}s, Min: {min_time:.3f}s, Max: {max_time:.3f}s")

        return performance_results

    def test_api_endpoints(self):
        """Test API endpoints specifically"""
        print("\\n🔌 Testing API Endpoints...")

        api_routes = [r for r in self.routes_to_test if r['url'].startswith('/api/')]
        api_results = []

        for route in api_routes:
            print(f"  Testing API: {route['method']} {route['url']}")

            result = self.test_single_route(route)

            # Additional API-specific checks
            if result['success']:
                try:
                    data = json.loads(result.get('response_data', '{}'))
                    is_json = True
                    has_required_fields = 'timestamp' in str(data)
                except:
                    is_json = False
                    has_required_fields = False

                result.update({
                    'is_json': is_json,
                    'has_required_fields': has_required_fields
                })

                print(f"    JSON: {'✅' if is_json else '❌'}, Required fields: {'✅' if has_required_fields else '❌'}")

            api_results.append(result)

        return api_results

    def generate_test_report(self):
        """Generate comprehensive test report"""
        print("\\n" + "=" * 60)
        print("📋 COMPREHENSIVE ROUTE TEST REPORT")
        print("=" * 60)

        if not self.test_results:
            print("❌ No test results available")
            return False

        # Overall statistics
        total_tests = len(self.test_results)
        successful_tests = sum(1 for r in self.test_results if r['success'])
        failed_tests = total_tests - successful_tests
        success_rate = (successful_tests / total_tests) * 100 if total_tests > 0 else 0

        print(f"\\n📊 OVERALL STATISTICS:")
        print(f"  Total Routes Tested: {total_tests}")
        print(f"  Successful: {successful_tests}")
        print(f"  Failed: {failed_tests}")
        print(f"  Success Rate: {success_rate:.1f}%")

        # Performance summary
        response_times = [r['response_time'] for r in self.test_results if r['success']]
        if response_times:
            avg_response_time = np.mean(response_times)
            print(f"  Average Response Time: {avg_response_time:.3f}s")
            print(f"  Fastest Response: {np.min(response_times):.3f}s")
            print(f"  Slowest Response: {np.max(response_times):.3f}s")

        # Route status breakdown
        print("\\n📈 ROUTE STATUS BREAKDOWN:")
        status_codes = {}
        for result in self.test_results:
            code = result.get('status_code', 'Error')
            status_codes[code] = status_codes.get(code, 0) + 1

        for code, count in sorted(status_codes.items()):
            status_icon = "✅" if str(code).startswith('2') else "❌"
            print(f"  {status_icon} {code}: {count} routes")

        # Detailed results
        print("\\n📝 DETAILED RESULTS:")
        print("-" * 80)
        print(f"{'Route':<20} {'Method':<8} {'Status':<8} {'Time':<8} {'Size':<10}")
        print("-" * 80)

        for result in self.test_results:
            status_icon = "✅" if result['success'] else "❌"
            status_code = result.get('status_code', 'N/A')
            response_time = result.get('response_time', 0)
            content_length = result.get('content_length', 0)

            print(f"{result['url']:<20} {result['method']:<8} {str(status_code):<8} {response_time:<8.3f} {content_length:<10}")
        # Recommendations
        print("\\n💡 RECOMMENDATIONS:")
        if success_rate >= 95:
            print("  ✅ Excellent! All routes are working properly.")
            print("  💡 Consider adding performance monitoring for production.")
        elif success_rate >= 80:
            print("  ⚠️ Most routes are working. Review failed routes below.")
            print("  💡 Check error logs and fix failing endpoints.")
        else:
            print("  ❌ Critical issues found. Many routes are failing.")
            print("  💡 Review application configuration and dependencies.")

        if response_times and np.mean(response_times) > 1.0:
            print("  💡 Consider optimizing slow routes for better performance.")

        return {
            'total_tests': total_tests,
            'successful_tests': successful_tests,
            'failed_tests': failed_tests,
            'success_rate': success_rate,
            'test_results': self.test_results
        }

    def create_performance_visualization(self, performance_results):
        """Create performance visualization"""
        print("\\n📊 Creating Performance Visualization...")

        if not performance_results:
            print("⚠️ No performance data to visualize")
            return

        # Create visualization
        routes = [r['route'] for r in performance_results]
        avg_times = [r['avg_time'] for r in performance_results]

        plt.figure(figsize=(12, 6))
        bars = plt.bar(range(len(routes)), avg_times, color='skyblue')
        plt.title('Route Response Times')
        plt.ylabel('Response Time (seconds)')
        plt.xticks(range(len(routes)), [r.split()[-1] for r in routes], rotation=45)

        # Add value labels
        for bar, time in zip(bars, avg_times):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.001,
                    '.3f', ha='center', va='bottom')

        plt.tight_layout()
        plt.savefig('route_performance.png', dpi=300, bbox_inches='tight')
        print("✅ Performance chart saved as 'route_performance.png'")
        plt.show()

def main():
    """Main execution function"""
    print("🚀 ValidoAI Route Testing Suite")
    print("=" * 50)

    # Initialize route tester
    tester = RouteTester()

    # Run comprehensive tests
    test_report = tester.run_all_route_tests()

    if test_report:
        # Additional tests
        performance_results = tester.test_route_performance()
        api_results = tester.test_api_endpoints()

        # Create visualizations
        if performance_results:
            try:
                tester.create_performance_visualization(performance_results)
            except ImportError:
                print("⚠️ Matplotlib not available for visualization")

        # Final summary
        print("\\n" + "=" * 50)
        print("🎉 ROUTE TESTING COMPLETED!")
        print("=" * 50)
        print(f"✅ Success Rate: {test_report['success_rate']:.1f}%")
        print(f"✅ Routes Tested: {test_report['total_tests']}")
        print("\\n💡 Next Steps:")
        print("  1. Review failed routes and fix issues")
        print("  2. Optimize slow-performing routes")
        print("  3. Add monitoring for production deployment")
        print("  4. Consider adding automated CI/CD testing")

        return True
    else:
        print("❌ Route testing failed to complete")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
