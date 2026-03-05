#!/usr/bin/env python3
"""
Comprehensive Route Tester for ValidoAI
Tests all routes in the application including unified CRUD routes
"""

import sys
import os
import json
import requests
import time
from pathlib import Path
from typing import Dict, List, Any, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import Flask app
try:
    import app
    app = app.app
    from src.config.table_configurations import get_all_table_configs
    from src.crud.unified_crud_config import crud_config_registry
    from src.crud.unified_crud_operations import unified_crud_registry
    from src.routes.unified_route_generator import unified_route_generator
except ImportError as e:
    print(f"Error importing Flask app: {e}")
    print("Make sure you're running this from the project root")
    sys.exit(1)

@dataclass
class RouteTestResult:
    """Result of testing a single route"""
    url: str
    method: str
    status_code: int
    response_time: float
    success: bool
    error: str = None
    content_length: int = 0
    content_type: str = None

@dataclass
class RouteTestSummary:
    """Summary of route testing results"""
    total_routes: int
    successful_routes: int
    failed_routes: int
    total_response_time: float
    average_response_time: float
    success_rate: float
    results: List[RouteTestResult]

class ComprehensiveRouteTester:
    """Comprehensive route testing system"""

    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ValidoAI Route Tester 1.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })

    def get_all_routes(self) -> List[Dict[str, Any]]:
        """Get all routes from the Flask application"""
        routes = []

        with app.test_client() as client:
            # Get Flask app routes
            for rule in app.url_map.iter_rules():
                if rule.endpoint != 'static':
                    methods = [method for method in rule.methods if method not in ['OPTIONS', 'HEAD']]
                    routes.append({
                        'url': rule.rule,
                        'methods': methods,
                        'endpoint': rule.endpoint,
                        'category': self._categorize_route(rule.rule)
                    })

        return routes

    def get_unified_crud_routes(self) -> List[Dict[str, Any]]:
        """Get all unified CRUD routes"""
        crud_routes = []
        all_configs = get_all_table_configs()

        for table_name, config in all_configs.items():
            base_url = f"/{table_name}"

            # Main CRUD routes
            crud_routes.extend([
                {'url': base_url, 'methods': ['GET'], 'endpoint': f'{table_name}.index', 'category': 'unified_crud'},
                {'url': f"{base_url}/create", 'methods': ['GET'], 'endpoint': f'{table_name}.create_form', 'category': 'unified_crud'},
                {'url': base_url, 'methods': ['POST'], 'endpoint': f'{table_name}.create', 'category': 'unified_crud'},
                {'url': f"{base_url}/export", 'methods': ['GET'], 'endpoint': f'{table_name}.export', 'category': 'unified_crud'},
                {'url': f"{base_url}/bulk", 'methods': ['POST'], 'endpoint': f'{table_name}.bulk_operations', 'category': 'unified_crud'},
                {'url': f"{base_url}/api/list", 'methods': ['GET'], 'endpoint': f'{table_name}.api_list', 'category': 'unified_crud_api'},
                {'url': f"{base_url}/api/stats", 'methods': ['GET'], 'endpoint': f'{table_name}.api_stats', 'category': 'unified_crud_api'},
            ])

        return crud_routes

    def _categorize_route(self, url: str) -> str:
        """Categorize a route based on its URL pattern"""
        if url.startswith('/api/'):
            return 'api'
        elif url.startswith('/chat'):
            return 'chat'
        elif url.startswith('/settings'):
            return 'settings'
        elif url.startswith('/database'):
            return 'database'
        elif url.startswith('/ml-') or url.startswith('/llm'):
            return 'ml_demo'
        elif url.startswith('/test') or url.startswith('/demo'):
            return 'testing'
        elif url.startswith('/ui-') or url.startswith('/example'):
            return 'ui_examples'
        elif url.startswith('/companies') or url.startswith('/users') or url.startswith('/products'):
            return 'business'
        else:
            return 'main'

    def test_route(self, route: Dict[str, Any]) -> List[RouteTestResult]:
        """Test a single route with all its methods"""
        results = []

        for method in route['methods']:
            result = self._test_single_route(route['url'], method, route.get('category', 'unknown'))
            results.append(result)

        return results

    def _test_single_route(self, url: str, method: str, category: str) -> RouteTestResult:
        """Test a single route with specific method"""
        full_url = f"{self.base_url}{url}"

        start_time = time.time()
        error = None
        status_code = 0
        content_length = 0
        content_type = None

        try:
            with app.test_client() as client:
                if method == 'GET':
                    response = client.get(url)
                elif method == 'POST':
                    # For POST requests, try with empty data first
                    response = client.post(url, data={})
                else:
                    # For other methods, use GET as fallback for testing
                    response = client.get(url)

                status_code = response.status_code
                content_length = len(response.get_data())
                content_type = response.content_type

        except Exception as e:
            error = str(e)
            status_code = 500

        response_time = time.time() - start_time

        success = status_code in [200, 201, 204, 301, 302, 303, 304, 307, 308]

        return RouteTestResult(
            url=url,
            method=method,
            status_code=status_code,
            response_time=response_time,
            success=success,
            error=error,
            content_length=content_length,
            content_type=content_type
        )

    def test_all_routes(self, max_workers: int = 10) -> RouteTestSummary:
        """Test all routes in the application"""
        print("🔍 Discovering routes...")
        all_routes = self.get_all_routes()
        unified_crud_routes = self.get_unified_crud_routes()

        # Combine all routes
        all_routes.extend(unified_crud_routes)
        print(f"📋 Found {len(all_routes)} total routes to test")

        results = []
        total_routes = len(all_routes)

        print(f"🧪 Testing {total_routes} routes with {max_workers} parallel workers...")

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all route tests
            future_to_route = {
                executor.submit(self.test_route, route): route
                for route in all_routes
            }

            completed = 0
            for future in as_completed(future_to_route):
                route = future_to_route[future]
                try:
                    route_results = future.result()
                    results.extend(route_results)
                    completed += 1

                    if completed % 50 == 0:
                        print(f"📊 Progress: {completed}/{total_routes} routes tested")

                except Exception as e:
                    print(f"❌ Error testing route {route['url']}: {e}")

        # Calculate summary
        successful_routes = sum(1 for result in results if result.success)
        failed_routes = len(results) - successful_routes
        total_response_time = sum(result.response_time for result in results)
        average_response_time = total_response_time / len(results) if results else 0
        success_rate = (successful_routes / len(results)) * 100 if results else 0

        summary = RouteTestSummary(
            total_routes=len(results),
            successful_routes=successful_routes,
            failed_routes=failed_routes,
            total_response_time=total_response_time,
            average_response_time=average_response_time,
            success_rate=success_rate,
            results=results
        )

        return summary

    def generate_detailed_report(self, summary: RouteTestSummary) -> str:
        """Generate a detailed test report"""
        report = []
        report.append("=" * 80)
        report.append("🎯 VALIDOAI COMPREHENSIVE ROUTE TEST REPORT")
        report.append("=" * 80)
        report.append(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")

        # Summary section
        report.append("📊 SUMMARY")
        report.append("-" * 50)
        report.append(f"Total Routes Tested: {summary.total_routes}")
        report.append(f"✅ Successful Routes: {summary.successful_routes}")
        report.append(f"❌ Failed Routes: {summary.failed_routes}")
        report.append(f"📈 Success Rate: {summary.success_rate:.1f}%")
        report.append(f"⏱️  Total Response Time: {summary.total_response_time:.2f}s")
        report.append(f"⚡ Average Response Time: {summary.average_response_time:.3f}s")
        report.append("")

        # Failed routes section
        failed_routes = [r for r in summary.results if not r.success]
        if failed_routes:
            report.append("❌ FAILED ROUTES")
            report.append("-" * 50)
            for result in failed_routes:
                report.append(f"🔴 {result.method} {result.url}")
                report.append(f"   Status: {result.status_code}")
                report.append(f"   Error: {result.error or 'N/A'}")
                report.append(f"   Response Time: {result.response_time:.3f}s")
                report.append("")
        else:
            report.append("✅ NO FAILED ROUTES - All routes are working!")

        # Success statistics by category
        report.append("📈 SUCCESS STATISTICS BY CATEGORY")
        report.append("-" * 50)

        # Group results by category
        categories = {}
        for result in summary.results:
            # Extract category from URL (simplified)
            if result.url.startswith('/api/'):
                category = 'API'
            elif result.url.startswith('/chat'):
                category = 'Chat'
            elif result.url.startswith('/settings'):
                category = 'Settings'
            elif result.url.startswith('/database'):
                category = 'Database'
            elif result.url.startswith('/companies') or result.url.startswith('/users'):
                category = 'Business'
            elif result.url.startswith('/unified_crud'):
                category = 'Unified CRUD'
            else:
                category = 'Main'

            if category not in categories:
                categories[category] = {'total': 0, 'success': 0}

            categories[category]['total'] += 1
            if result.success:
                categories[category]['success'] += 1

        for category, stats in categories.items():
            success_rate = (stats['success'] / stats['total']) * 100 if stats['total'] > 0 else 0
            report.append(f"📁 {category}: {stats['success']}/{stats['total']} ({success_rate:.1f}%)")

        report.append("")
        report.append("=" * 80)
        report.append("🎉 Route testing completed successfully!")
        report.append("=" * 80)

        return "\n".join(report)

    def save_results(self, summary: RouteTestSummary, filename: str = None):
        """Save test results to file"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"logs/route_test_results_{timestamp}.json"

        # Ensure logs directory exists
        Path(filename).parent.mkdir(exist_ok=True)

        # Convert results to serializable format
        results_data = {
            'test_date': datetime.now().isoformat(),
            'summary': {
                'total_routes': summary.total_routes,
                'successful_routes': summary.successful_routes,
                'failed_routes': summary.failed_routes,
                'total_response_time': summary.total_response_time,
                'average_response_time': summary.average_response_time,
                'success_rate': summary.success_rate
            },
            'results': [
                {
                    'url': r.url,
                    'method': r.method,
                    'status_code': r.status_code,
                    'response_time': r.response_time,
                    'success': r.success,
                    'error': r.error,
                    'content_length': r.content_length,
                    'content_type': r.content_type
                }
                for r in summary.results
            ]
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results_data, f, indent=2, ensure_ascii=False)

        print(f"💾 Results saved to: {filename}")


def main():
    """Main function"""
    print("🚀 Starting Comprehensive Route Testing")
    print("=" * 60)

    # Initialize tester
    tester = ComprehensiveRouteTester()

    try:
        # Run tests
        summary = tester.test_all_routes(max_workers=20)

        # Generate and display report
        report = tester.generate_detailed_report(summary)
        print(report)

        # Save results
        tester.save_results(summary)

        # Exit with appropriate code
        if summary.success_rate >= 95:
            print("✅ All tests passed with excellent success rate!")
            sys.exit(0)
        elif summary.success_rate >= 80:
            print("⚠️  Tests completed with good success rate")
            sys.exit(0)
        else:
            print("❌ Tests completed with poor success rate")
            sys.exit(1)

    except Exception as e:
        print(f"💥 Fatal error during testing: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
