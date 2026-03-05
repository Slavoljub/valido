#!/usr/bin/env python3
"""
Route Status Testing System
Tests all routes in the Flask application to ensure they are working properly
"""

import requests
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import time
import json
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

@dataclass
class RouteTestResult:
    """Result of testing a single route"""
    route_path: str
    route_method: str
    expected_status: int
    actual_status: int
    response_time: float
    is_success: bool
    error_message: Optional[str] = None
    response_size: int = 0
    content_type: str = ""
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

@dataclass
class RouteTestSuite:
    """Complete test suite for route testing"""
    test_id: str
    base_url: str
    total_routes: int
    passed_tests: int
    failed_tests: int
    total_response_time: float
    test_results: List[RouteTestResult]
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage"""
        if self.total_routes == 0:
            return 0.0
        return (self.passed_tests / self.total_routes) * 100

    @property
    def average_response_time(self) -> float:
        """Calculate average response time"""
        if self.passed_tests == 0:
            return 0.0
        return self.total_response_time / self.passed_tests

class RouteTester:
    """Advanced Route Testing System"""

    def __init__(self, base_url: str = "http://localhost:5000"):
        """Initialize the route tester"""
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.timeout = 30

        # Common routes to test
        self.common_routes = [
            # Main pages
            {"path": "/", "method": "GET", "expected_status": 200},
            {"path": "/chat-local", "method": "GET", "expected_status": 200},
            {"path": "/database-example", "method": "GET", "expected_status": 200},
            {"path": "/database-simple", "method": "GET", "expected_status": 200},
            {"path": "/settings/database", "method": "GET", "expected_status": 200},
            {"path": "/ui-examples", "method": "GET", "expected_status": 200},
            {"path": "/ml-algorithms-demo", "method": "GET", "expected_status": 200},

            # API endpoints
            {"path": "/api/theme/available", "method": "GET", "expected_status": 200},
            {"path": "/api/database/test-connection", "method": "POST", "expected_status": 400},  # Missing data
            {"path": "/api/database/get-tables", "method": "POST", "expected_status": 400},  # Missing data
            {"path": "/api/database/get-table-data", "method": "POST", "expected_status": 400},  # Missing data

            # Static files
            {"path": "/static/css/main.css", "method": "GET", "expected_status": 200},
            {"path": "/static/js/main.js", "method": "GET", "expected_status": 200},

            # Error pages (these should return error status)
            {"path": "/nonexistent-page", "method": "GET", "expected_status": 404},
        ]

        # Authentication routes (if applicable)
        self.auth_routes = [
            {"path": "/auth/login", "method": "GET", "expected_status": 200},
            {"path": "/auth/logout", "method": "GET", "expected_status": 302},  # Redirect
        ]

        # Admin routes (if applicable)
        self.admin_routes = [
            {"path": "/admin", "method": "GET", "expected_status": 200},
            {"path": "/admin/dashboard", "method": "GET", "expected_status": 200},
        ]

    def test_single_route(self, route: Dict[str, Any]) -> RouteTestResult:
        """Test a single route"""
        start_time = time.time()

        try:
            url = urljoin(self.base_url, route["path"])
            method = route["method"]
            expected_status = route["expected_status"]

            # Prepare request
            if method == "GET":
                response = self.session.get(url, timeout=30)
            elif method == "POST":
                # For POST requests, send empty JSON if no data provided
                data = route.get("data", {})
                response = self.session.post(url, json=data, timeout=30)
            elif method == "PUT":
                data = route.get("data", {})
                response = self.session.put(url, json=data, timeout=30)
            elif method == "DELETE":
                response = self.session.delete(url, timeout=30)
            else:
                # Default to GET
                response = self.session.get(url, timeout=30)

            response_time = time.time() - start_time

            # Check if status matches expected
            is_success = response.status_code == expected_status

            return RouteTestResult(
                route_path=route["path"],
                route_method=method,
                expected_status=expected_status,
                actual_status=response.status_code,
                response_time=response_time,
                is_success=is_success,
                response_size=len(response.content),
                content_type=response.headers.get('content-type', ''),
                error_message=None if is_success else f"Expected {expected_status}, got {response.status_code}"
            )

        except requests.exceptions.RequestException as e:
            response_time = time.time() - start_time
            return RouteTestResult(
                route_path=route["path"],
                route_method=route["method"],
                expected_status=route["expected_status"],
                actual_status=0,
                response_time=response_time,
                is_success=False,
                error_message=str(e)
            )
        except Exception as e:
            response_time = time.time() - start_time
            return RouteTestResult(
                route_path=route["path"],
                route_method=route["method"],
                expected_status=route["expected_status"],
                actual_status=0,
                response_time=response_time,
                is_success=False,
                error_message=f"Unexpected error: {str(e)}"
            )

    def test_all_routes(self, include_auth: bool = False, include_admin: bool = False) -> RouteTestSuite:
        """Test all routes in the application"""
        logger.info(f"Starting Route Test Suite for {self.base_url}")

        all_routes = self.common_routes.copy()

        if include_auth:
            all_routes.extend(self.auth_routes)

        if include_admin:
            all_routes.extend(self.admin_routes)

        # Test each route
        test_results = []
        total_response_time = 0.0
        passed_tests = 0
        failed_tests = 0

        for route in all_routes:
            logger.info(f"Testing route: {route['method']} {route['path']}")

            result = self.test_single_route(route)
            test_results.append(result)

            total_response_time += result.response_time

            if result.is_success:
                passed_tests += 1
                logger.info(f"✅ {route['method']} {route['path']} - {result.actual_status} ({result.response_time:.2f}s)")
            else:
                failed_tests += 1
                logger.error(f"❌ {route['method']} {route['path']} - Expected {result.expected_status}, got {result.actual_status} ({result.response_time:.2f}s)")
                if result.error_message:
                    logger.error(f"   Error: {result.error_message}")

        # Create test suite result
        test_suite = RouteTestSuite(
            test_id=f"route_test_{int(time.time())}",
            base_url=self.base_url,
            total_routes=len(all_routes),
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            total_response_time=total_response_time,
            test_results=test_results
        )

        logger.info(".2f"
        return test_suite

    def test_api_endpoints_with_data(self) -> List[RouteTestResult]:
        """Test API endpoints with proper data"""
        api_tests = [
            {
                "path": "/api/database/test-connection",
                "method": "POST",
                "expected_status": 200,
                "data": {"database_name": "main"}
            },
            {
                "path": "/api/database/get-tables",
                "method": "POST",
                "expected_status": 200,
                "data": {"database_name": "main"}
            },
            {
                "path": "/api/database/get-table-data",
                "method": "POST",
                "expected_status": 200,
                "data": {"database_name": "main", "table_name": "sqlite_master"}
            },
            {
                "path": "/api/theme/change",
                "method": "POST",
                "expected_status": 200,
                "data": {"theme": "dark"}
            }
        ]

        results = []
        for api_test in api_tests:
            logger.info(f"Testing API: {api_test['method']} {api_test['path']}")
            result = self.test_single_route(api_test)
            results.append(result)

            if result.is_success:
                logger.info(f"✅ API test passed: {api_test['path']}")
            else:
                logger.error(f"❌ API test failed: {api_test['path']} - {result.error_message}")

        return results

    def test_database_connectivity(self) -> Dict[str, Any]:
        """Test database connectivity through the application"""
        logger.info("Testing database connectivity...")

        # Test database connection endpoint
        test_result = self.test_single_route({
            "path": "/api/database/test-connection",
            "method": "POST",
            "expected_status": 200,
            "data": {"database_name": "main"}
        })

        if test_result.is_success:
            logger.info("✅ Database connectivity test passed")
            return {
                "success": True,
                "database_status": "connected",
                "response_time": test_result.response_time
            }
        else:
            logger.error(f"❌ Database connectivity test failed: {test_result.error_message}")
            return {
                "success": False,
                "database_status": "disconnected",
                "error": test_result.error_message,
                "response_time": test_result.response_time
            }

    def test_chat_functionality(self) -> Dict[str, Any]:
        """Test chat functionality through the application"""
        logger.info("Testing chat functionality...")

        # Test chat page load
        chat_page_test = self.test_single_route({
            "path": "/chat-local",
            "method": "GET",
            "expected_status": 200
        })

        if not chat_page_test.is_success:
            logger.error(f"❌ Chat page test failed: {chat_page_test.error_message}")
            return {
                "success": False,
                "chat_status": "page_load_failed",
                "error": chat_page_test.error_message
            }

        # Test theme API (part of chat functionality)
        theme_test = self.test_single_route({
            "path": "/api/theme/available",
            "method": "GET",
            "expected_status": 200
        })

        if theme_test.is_success:
            logger.info("✅ Chat functionality test passed")
            return {
                "success": True,
                "chat_status": "functional",
                "page_load_time": chat_page_test.response_time,
                "theme_api_time": theme_test.response_time
            }
        else:
            logger.error(f"❌ Theme API test failed: {theme_test.error_message}")
            return {
                "success": False,
                "chat_status": "theme_api_failed",
                "error": theme_test.error_message
            }

    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """Generate comprehensive application status report"""
        logger.info("Generating comprehensive application status report...")

        # Test all routes
        route_suite = self.test_all_routes(include_auth=True, include_admin=False)

        # Test API endpoints with data
        api_results = self.test_api_endpoints_with_data()

        # Test database connectivity
        db_status = self.test_database_connectivity()

        # Test chat functionality
        chat_status = self.test_chat_functionality()

        # Combine all results
        all_route_results = route_suite.test_results + api_results

        comprehensive_report = {
            "test_timestamp": datetime.now().isoformat(),
            "base_url": self.base_url,
            "overall_status": {
                "routes_success_rate": route_suite.success_rate,
                "total_routes_tested": len(all_route_results),
                "passed_routes": sum(1 for r in all_route_results if r.is_success),
                "failed_routes": sum(1 for r in all_route_results if not r.is_success),
                "average_response_time": sum(r.response_time for r in all_route_results) / len(all_route_results) if all_route_results else 0
            },
            "database_status": db_status,
            "chat_status": chat_status,
            "route_details": [asdict(result) for result in all_route_results],
            "failed_routes": [asdict(result) for result in all_route_results if not result.is_success],
            "performance_metrics": {
                "fastest_route": min((r for r in all_route_results if r.is_success), key=lambda x: x.response_time, default=None),
                "slowest_route": max((r for r in all_route_results if r.is_success), key=lambda x: x.response_time, default=None),
                "average_response_time": sum(r.response_time for r in all_route_results) / len(all_route_results) if all_route_results else 0
            }
        }

        # Convert performance metrics to dict format if they exist
        if comprehensive_report["performance_metrics"]["fastest_route"]:
            comprehensive_report["performance_metrics"]["fastest_route"] = asdict(comprehensive_report["performance_metrics"]["fastest_route"])

        if comprehensive_report["performance_metrics"]["slowest_route"]:
            comprehensive_report["performance_metrics"]["slowest_route"] = asdict(comprehensive_report["performance_metrics"]["slowest_route"])

        return comprehensive_report

    def save_report(self, report: Dict[str, Any], output_path: str = "data/test_reports"):
        """Save comprehensive report to file"""
        try:
            import json
            from pathlib import Path

            output_dir = Path(output_path)
            output_dir.mkdir(parents=True, exist_ok=True)

            # Save JSON report
            json_path = output_dir / f"route_status_report_{int(time.time())}.json"
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)

            # Save HTML report
            html_path = output_dir / f"route_status_report_{int(time.time())}.html"
            html_report = self._generate_html_report(report)
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_report)

            logger.info(f"Route status reports saved: {json_path}, {html_path}")
            return str(json_path)

        except Exception as e:
            logger.error(f"Error saving route status report: {e}")
            return None

    def _generate_html_report(self, report: Dict[str, Any]) -> str:
        """Generate HTML report for route testing"""
        html = ".2f"".2f"f"""
        <html>
        <head>
            <title>Route Status Test Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .summary {{ background: #f0f0f0; padding: 20px; margin: 20px 0; }}
                .status-section {{ background: #e8f4f8; padding: 15px; margin: 10px 0; }}
                .success {{ color: green; }}
                .failure {{ color: red; }}
                .warning {{ color: orange; }}
                .route {{ margin: 10px 0; padding: 10px; border: 1px solid #ddd; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <h1>Route Status Test Report</h1>

            <div class="summary">
                <h2>Overall Status</h2>
                <p><strong>Test Time:</strong> {report['test_timestamp']}</p>
                <p><strong>Base URL:</strong> {report['base_url']}</p>
                <p><strong>Success Rate:</strong> <span class="{'success' if report['overall_status']['routes_success_rate'] >= 80 else 'failure'}">{report['overall_status']['routes_success_rate']:.2f}%</span></p>
                <p><strong>Total Routes Tested:</strong> {report['overall_status']['total_routes_tested']}</p>
                <p><strong>Passed:</strong> <span class="success">{report['overall_status']['passed_routes']}</span></p>
                <p><strong>Failed:</strong> <span class="failure">{report['overall_status']['failed_routes']}</span></p>
                <p><strong>Average Response Time:</strong> {report['overall_status']['average_response_time']:.2f}s</p>
            </div>

            <div class="status-section">
                <h2>Database Status</h2>
                <p><strong>Status:</strong> <span class="{'success' if report['database_status']['success'] else 'failure'}">{report['database_status']['database_status']}</span></p>
                <p><strong>Response Time:</strong> {report['database_status'].get('response_time', 0):.2f}s</p>
                {'<p><strong>Error:</strong> ' + report['database_status'].get('error', '') + '</p>' if not report['database_status']['success'] else ''}
            </div>

            <div class="status-section">
                <h2>Chat Functionality Status</h2>
                <p><strong>Status:</strong> <span class="{'success' if report['chat_status']['success'] else 'failure'}">{report['chat_status']['chat_status']}</span></p>
                <p><strong>Page Load Time:</strong> {report['chat_status'].get('page_load_time', 0):.2f}s</p>
                {'<p><strong>Error:</strong> ' + report['chat_status'].get('error', '') + '</p>' if not report['chat_status']['success'] else ''}
            </div>
        """

        # Performance metrics
        if report['performance_metrics']['fastest_route']:
            fastest = report['performance_metrics']['fastest_route']
            html += ".2f"f"""
            <div class="status-section">
                <h2>Performance Metrics</h2>
                <p><strong>Fastest Route:</strong> {fastest['route_method']} {fastest['route_path']} ({fastest['response_time']:.2f}s)</p>
            """

            if report['performance_metrics']['slowest_route']:
                slowest = report['performance_metrics']['slowest_route']
                html += ".2f"f"""
                <p><strong>Slowest Route:</strong> {slowest['route_method']} {slowest['route_path']} ({slowest['response_time']:.2f}s)</p>
            """

            html += "</div>"

        # Failed routes
        if report['failed_routes']:
            html += """
            <h2>Failed Routes</h2>
            """

            for route in report['failed_routes']:
                html += ".2f"".2f"f"""
                <div class="route failure">
                    <h3>{route['route_method']} {route['route_path']}</h3>
                    <p><strong>Expected Status:</strong> {route['expected_status']}</p>
                    <p><strong>Actual Status:</strong> {route['actual_status']}</p>
                    <p><strong>Response Time:</strong> {route['response_time']:.2f}s</p>
                    <p><strong>Error:</strong> {route.get('error_message', 'Unknown error')}</p>
                </div>
            """

        html += """
        </body>
        </html>
        """

        return html

# Global instance
route_tester = RouteTester()
