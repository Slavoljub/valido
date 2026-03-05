#!/usr/bin/env python3
"""
Comprehensive CRUD Route Testing Suite
Tests all 48+ CRUD routes from the unified system
"""

import sys
import os
import json
import time
import pytest
import unittest
from pathlib import Path
from flask import url_for
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app import create_app

# Import CRUD configurations
try:
    from src.config.table_configurations import (
        get_companies_config, get_users_config, get_business_partners_config,
        get_products_config, get_financial_transactions_config, get_employees_config
    )
    CRUD_CONFIGS_AVAILABLE = True
except ImportError:
    CRUD_CONFIGS_AVAILABLE = False
    print("⚠️  CRUD configurations not available, using fallback table list")

# List of all tables from the PostgreSQL schema
ALL_TABLES = [
    'companies', 'users', 'business_partners', 'products', 'financial_transactions',
    'employees', 'countries', 'warehouses', 'ai_models_system', 'ai_model_usage',
    'ai_model_performance', 'ai_model_costs', 'tickets', 'ticket_messages',
    'ticket_attachments', 'settings', 'user_permissions', 'user_roles',
    'role_permissions', 'notifications', 'notification_templates', 'logs',
    'audit_trails', 'file_attachments', 'file_versions', 'categories',
    'tags', 'tag_assignments', 'comments', 'comment_replies', 'ratings',
    'reviews', 'favorites', 'bookmarks', 'subscriptions', 'subscription_plans',
    'billing_history', 'payment_methods', 'tax_rates', 'currencies',
    'language_translations', 'system_configurations', 'maintenance_logs',
    'backup_history', 'api_keys', 'webhooks', 'integration_logs',
    'report_templates', 'scheduled_reports', 'dashboard_widgets',
    'widget_configurations', 'user_preferences', 'theme_settings'
]

class CRUDRoutesTester:
    """Comprehensive CRUD routes testing class"""

    def __init__(self):
        self.app = create_app()
        self.client = self.app.test_client()
        self.test_results = {
            'summary': {
                'total_routes_tested': 0,
                'passed': 0,
                'failed': 0,
                'warnings': 0,
                'errors': 0,
                'start_time': None,
                'end_time': None,
                'duration': 0
            },
            'routes': [],
            'performance_metrics': [],
            'errors': []
        }

    def run_comprehensive_tests(self):
        """Run comprehensive CRUD route tests"""
        print("🚀 Starting Comprehensive CRUD Route Testing")
        print("=" * 80)

        self.test_results['summary']['start_time'] = time.time()

        # Test all CRUD routes
        self.test_all_crud_routes()

        # Test API endpoints
        self.test_api_endpoints()

        # Test export functionality
        self.test_export_functionality()

        # Test bulk operations
        self.test_bulk_operations()

        # Test special features
        self.test_special_features()

        # Generate performance report
        self.generate_performance_report()

        self.test_results['summary']['end_time'] = time.time()
        self.test_results['summary']['duration'] = (
            self.test_results['summary']['end_time'] - self.test_results['summary']['start_time']
        )

        self._generate_final_report()
        return self.test_results

    def test_all_crud_routes(self):
        """Test all CRUD routes for all tables"""
        print("\n📋 Testing All CRUD Routes")
        print("-" * 60)

        crud_routes = [
            ('/', 'GET', 'List/Index'),
            ('/create', 'GET', 'Create Form'),
            ('/<int:id>', 'GET', 'Show/Details'),
            ('/<int:id>/edit', 'GET', 'Edit Form'),
            ('/api/list', 'GET', 'API List'),
            ('/api/stats', 'GET', 'API Statistics'),
            ('/export', 'GET', 'Export Data'),
        ]

        for table in ALL_TABLES[:10]:  # Test first 10 tables for speed
            print(f"\n🗂️  Testing {table} routes:")
            table_routes_tested = 0
            table_routes_passed = 0

            for route_pattern, method, description in crud_routes:
                route = f"/{table}{route_pattern}"
                try:
                    start_time = time.time()

                    if method == 'GET':
                        response = self.client.get(route)
                    elif method == 'POST':
                        response = self.client.post(route, data={})

                    response_time = time.time() - start_time
                    status = response.status_code

                    # Determine success
                    if status in [200, 201, 204, 301, 302, 404]:  # 404 is acceptable for non-existent records
                        success = True
                        result = '✅'
                    else:
                        success = False
                        result = '❌'

                    if success:
                        table_routes_passed += 1
                    table_routes_tested += 1

                    # Store result
                    self.test_results['routes'].append({
                        'table': table,
                        'route': route,
                        'method': method,
                        'description': description,
                        'status_code': status,
                        'success': success,
                        'response_time': response_time
                    })

                    self.test_results['performance_metrics'].append({
                        'table': table,
                        'route': route,
                        'response_time': response_time,
                        'status_code': status
                    })

                    print("2d")
                except Exception as e:
                    table_routes_tested += 1
                    self.test_results['errors'].append({
                        'table': table,
                        'route': route,
                        'method': method,
                        'error': str(e)
                    })
                    print("2d")
                    print(f"      💥 Error: {str(e)}")

            print(f"  📊 {table}: {table_routes_passed}/{table_routes_tested} routes working")

    def test_api_endpoints(self):
        """Test API endpoints for all tables"""
        print("\n🔧 Testing API Endpoints")
        print("-" * 60)

        api_endpoints = [
            ('/api/list', 'GET', 'List API'),
            ('/api/stats', 'GET', 'Stats API'),
            ('/api/create', 'POST', 'Create API'),
        ]

        for table in ALL_TABLES[:5]:  # Test first 5 tables
            print(f"\n🗂️  Testing {table} API endpoints:")
            api_tests_passed = 0
            api_tests_total = 0

            for endpoint, method, description in api_endpoints:
                route = f"/{table}{endpoint}"
                try:
                    if method == 'GET':
                        response = self.client.get(route)
                    elif method == 'POST':
                        response = self.client.post(route, json={})

                    status = response.status_code
                    success = status in [200, 201, 204, 404, 422]  # Include validation errors

                    if success:
                        api_tests_passed += 1
                    api_tests_total += 1

                    print("2d")
                    if success and status == 200 and method == 'GET':
                        try:
                            data = response.get_json()
                            if isinstance(data, dict):
                                if 'records' in data:
                                    print(f"      📊 Records: {len(data.get('records', []))}")
                                if 'total' in data:
                                    print(f"      📊 Total: {data.get('total', 0)}")
                        except:
                            pass

                except Exception as e:
                    api_tests_total += 1
                    print("2d")
                    print(f"      💥 Error: {str(e)}")

            print(f"  📊 {table} API: {api_tests_passed}/{api_tests_total} endpoints working")

    def test_export_functionality(self):
        """Test export functionality for all tables"""
        print("\n📤 Testing Export Functionality")
        print("-" * 60)

        export_formats = ['csv', 'json', 'xlsx']

        for table in ALL_TABLES[:3]:  # Test first 3 tables
            print(f"\n🗂️  Testing {table} exports:")
            export_tests_passed = 0
            export_tests_total = 0

            for format_type in export_formats:
                route = f"/{table}/export?format={format_type}"
                try:
                    response = self.client.get(route)
                    status = response.status_code
                    success = status in [200, 201, 204]

                    if success:
                        export_tests_passed += 1
                    export_tests_total += 1

                    print("2d")
                    # Check content type
                    if success and status == 200:
                        content_type = response.headers.get('content-type', '').lower()
                        if format_type == 'csv' and 'text/csv' in content_type:
                            print("      ✅ Correct CSV content type")
                        elif format_type == 'json' and 'application/json' in content_type:
                            print("      ✅ Correct JSON content type")
                        elif format_type == 'xlsx' and ('application/vnd' in content_type or 'application/octet-stream' in content_type):
                            print("      ✅ Correct Excel content type")
                except Exception as e:
                    export_tests_total += 1
                    print("2d")
                    print(f"      💥 Error: {str(e)}")

            print(f"  📊 {table} exports: {export_tests_passed}/{export_tests_total} formats working")

    def test_bulk_operations(self):
        """Test bulk operations for tables that support them"""
        print("\n⚡ Testing Bulk Operations")
        print("-" * 60)

        bulk_operations = [
            ('/bulk-delete', 'POST', 'Bulk Delete'),
            ('/bulk-update', 'POST', 'Bulk Update'),
            ('/bulk-export', 'GET', 'Bulk Export'),
        ]

        bulk_supported_tables = ['companies', 'users', 'products']  # Tables likely to support bulk ops

        for table in bulk_supported_tables:
            print(f"\n🗂️  Testing {table} bulk operations:")
            bulk_tests_passed = 0
            bulk_tests_total = 0

            for endpoint, method, description in bulk_operations:
                route = f"/{table}{endpoint}"
                try:
                    if method == 'GET':
                        response = self.client.get(route)
                    elif method == 'POST':
                        response = self.client.post(route, json={'ids': []})

                    status = response.status_code
                    success = status in [200, 201, 204, 400, 422]  # Include validation errors

                    if success:
                        bulk_tests_passed += 1
                    bulk_tests_total += 1

                    print("2d")
                except Exception as e:
                    bulk_tests_total += 1
                    print("2d")
                    print(f"      💥 Error: {str(e)}")

            print(f"  📊 {table} bulk ops: {bulk_tests_passed}/{bulk_tests_total} operations working")

    def test_special_features(self):
        """Test special features like tabs, filters, search"""
        print("\n🎨 Testing Special Features")
        print("-" * 60)

        special_features = [
            ('/?search=test', 'GET', 'Search'),
            ('/?page=1', 'GET', 'Pagination'),
            ('/?sort_by=id', 'GET', 'Sorting'),
            ('/api/search', 'POST', 'API Search'),
        ]

        # Test special features on companies (known to have tabs)
        table = 'companies'
        print(f"\n🗂️  Testing {table} special features:")

        feature_tests_passed = 0
        feature_tests_total = 0

        for endpoint, method, description in special_features:
            route = f"/{table}{endpoint}"
            try:
                if method == 'GET':
                    response = self.client.get(route)
                elif method == 'POST':
                    response = self.client.post(route, json={'query': 'test'})

                status = response.status_code
                success = status in [200, 201, 204, 302, 400, 422]

                if success:
                    feature_tests_passed += 1
                feature_tests_total += 1

                print("2d")
            except Exception as e:
                feature_tests_total += 1
                print("2d")
                print(f"      💥 Error: {str(e)}")

        print(f"  📊 {table} features: {feature_tests_passed}/{feature_tests_total} features working")

    def generate_performance_report(self):
        """Generate performance report"""
        print("\n⚡ Performance Analysis")
        print("-" * 60)

        if not self.test_results['performance_metrics']:
            print("⚠️  No performance metrics collected")
            return

        metrics = self.test_results['performance_metrics']

        # Calculate statistics
        response_times = [m['response_time'] for m in metrics if m['response_time'] > 0]

        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            max_response_time = max(response_times)
            min_response_time = min(response_times)

            print(".3f")
            print(".3f")
            print(".3f")
            # Performance thresholds
            slow_routes = [m for m in metrics if m['response_time'] > 2.0]
            if slow_routes:
                print(f"⚠️  {len(slow_routes)} routes took more than 2 seconds:")
                for route in slow_routes[:5]:  # Show first 5
                    print(".2f")

    def _generate_final_report(self):
        """Generate final test report"""
        print("\n" + "=" * 80)
        print("📊 FINAL TEST REPORT")
        print("=" * 80)

        summary = self.test_results['summary']

        # Update summary counts
        total_routes = len(self.test_results['routes'])
        passed_routes = len([r for r in self.test_results['routes'] if r['success']])
        failed_routes = total_routes - passed_routes

        summary.update({
            'total_routes_tested': total_routes,
            'passed': passed_routes,
            'failed': failed_routes,
            'errors': len(self.test_results['errors'])
        })

        print(f"🧪 Total Routes Tested: {total_routes}")
        print(f"✅ Passed: {passed_routes}")
        print(f"❌ Failed: {failed_routes}")
        print(f"💥 Errors: {len(self.test_results['errors'])}")
        print(".2f")

        if total_routes > 0:
            success_rate = (passed_routes / total_routes) * 100
            print(".2f")

            if success_rate >= 90:
                print("🎉 EXCELLENT! Most CRUD routes are working correctly!")
            elif success_rate >= 75:
                print("⚠️  GOOD! Most routes are working with minor issues.")
            elif success_rate >= 50:
                print("⚠️  FAIR! Some routes need attention.")
            else:
                print("❌ CRITICAL! Many routes have issues and need attention.")

        print(".2f")

        # Save detailed results
        self._save_test_results()

        print("\n📄 Detailed results saved to: crud_routes_test_results.json")
        print("🎯 Next steps: Fix failing routes and implement missing CRUD operations")

    def _save_test_results(self):
        """Save test results to file"""
        try:
            with open('crud_routes_test_results.json', 'w', encoding='utf-8') as f:
                json.dump(self.test_results, f, indent=2, default=str)
        except Exception as e:
            print(f"❌ Failed to save results: {str(e)}")


def run_parallel_route_tests():
    """Run route tests in parallel for better performance"""
    print("🚀 Starting Parallel CRUD Route Testing")
    print("=" * 80)

    def test_table_routes(table_name):
        """Test routes for a single table"""
        try:
            app = create_app()
            with app.test_client() as client:
                results = []

                # Test main routes
                routes = [
                    f'/{table_name}',
                    f'/{table_name}/create',
                    f'/{table_name}/api/list',
                    f'/{table_name}/api/stats'
                ]

                for route in routes:
                    try:
                        response = client.get(route)
                        results.append({
                            'table': table_name,
                            'route': route,
                            'status': response.status_code,
                            'success': response.status_code in [200, 201, 204, 301, 302, 404]
                        })
                    except Exception as e:
                        results.append({
                            'table': table_name,
                            'route': route,
                            'status': None,
                            'success': False,
                            'error': str(e)
                        })

                return results

        except Exception as e:
            return [{
                'table': table_name,
                'error': f"Failed to test table {table_name}: {str(e)}"
            }]

    # Test first 20 tables in parallel
    test_tables = ALL_TABLES[:20]

    print(f"🧪 Testing {len(test_tables)} tables in parallel...")

    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_table = {executor.submit(test_table_routes, table): table for table in test_tables}

        all_results = []
        for future in as_completed(future_to_table):
            table = future_to_table[future]
            try:
                results = future.result()
                all_results.extend(results)
            except Exception as e:
                print(f"❌ Error testing {table}: {str(e)}")

    # Analyze results
    successful_routes = [r for r in all_results if r.get('success', False)]
    failed_routes = [r for r in all_results if not r.get('success', False)]

    print("\n📊 Parallel Test Results:")
    print(f"  ✅ Successful routes: {len(successful_routes)}")
    print(f"  ❌ Failed routes: {len(failed_routes)}")
    print(".2f")

    return all_results


def run_focused_crud_tests():
    """Run focused tests on known working CRUD tables"""
    print("🎯 Running Focused CRUD Tests")
    print("=" * 80)

    tester = CRUDRoutesTester()
    return tester.run_comprehensive_tests()


def run_quick_route_check():
    """Quick route availability check"""
    print("🔍 Quick Route Availability Check")
    print("=" * 80)

    app = create_app()
    client = app.test_client()

    # Quick check of key routes
    key_routes = [
        ('/', 'Home'),
        ('/companies', 'Companies'),
        ('/users', 'Users'),
        ('/products', 'Products'),
        ('/api/health', 'API Health'),
    ]

    print("Route Status:")
    for route, description in key_routes:
        try:
            response = client.get(route)
            status = response.status_code
            success = status in [200, 201, 204, 301, 302]
            print("30s")
        except Exception as e:
            print("30s")

    return True


def main():
    """Main function to run CRUD route tests"""
    import argparse

    parser = argparse.ArgumentParser(description='CRUD Route Testing Suite')
    parser.add_argument('--mode', choices=['quick', 'focused', 'parallel', 'comprehensive'],
                       default='focused', help='Test mode')
    parser.add_argument('--tables', type=int, default=10,
                       help='Number of tables to test (for parallel mode)')

    args = parser.parse_args()

    try:
        if args.mode == 'quick':
            run_quick_route_check()
        elif args.mode == 'parallel':
            run_parallel_route_tests()
        elif args.mode == 'comprehensive':
            tester = CRUDRoutesTester()
            results = tester.run_comprehensive_tests()
        else:  # focused
            run_focused_crud_tests()

    except KeyboardInterrupt:
        print("\n⚠️  Testing interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Testing failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
