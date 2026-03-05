#!/usr/bin/env python3
"""
ValidoAI Simple Test Suite
==========================

Quick validation test for the ValidoAI application to check basic functionality.

Usage:
    python tests/simple_test.py
    python tests/simple_test.py --url http://localhost:5000

Author: ValidoAI Development Team
Version: 1.0.0
"""

import os
import sys
import time
import requests
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_route(url, route, expected_status=200, description=""):
    """Test a single route"""
    try:
        start_time = time.time()
        response = requests.get(url, timeout=10)
        load_time = time.time() - start_time

        if response.status_code == expected_status:
            print(".2f")
            return True, load_time
        else:
            print(".2f")
            return False, load_time

    except requests.exceptions.RequestException as e:
        print(f"❌ {route} - ERROR: {str(e)}")
        return False, 0

def main():
    """Main test function"""
    import argparse

    parser = argparse.ArgumentParser(description='ValidoAI Simple Test')
    parser.add_argument('--url', default='http://localhost:5000', help='Base URL of the application')

    args = parser.parse_args()

    base_url = args.url.rstrip('/')

    print("🚀 ValidoAI Simple Test Suite")
    print(f"Target: {base_url}")
    print("=" * 50)

    # Test routes
    routes = [
        ('/', 200, 'Dashboard'),
        ('/ui-examples', 200, 'UI Examples'),
        ('/docs', 200, 'API Documentation'),
        ('/database-example', 200, 'Database Management'),
        ('/api-docs', 200, 'API Docs JSON'),
    ]

    passed = 0
    failed = 0
    total_load_time = 0

    for route, expected_status, description in routes:
        url = f"{base_url}{route}"
        success, load_time = test_route(url, route, expected_status, description)
        total_load_time += load_time

        if success:
            passed += 1
        else:
            failed += 1

    # Summary
    print("\n📊 Test Summary")
    print("=" * 30)
    print(f"Total Tests: {len(routes)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(".2f")
    print(".2f")

    if passed == len(routes):
        print("\n🎉 ALL TESTS PASSED! The application is working correctly.")
        sys.exit(0)
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please check the application.")
        sys.exit(1)

if __name__ == "__main__":
    main()
