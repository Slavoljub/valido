#!/usr/bin/env python3
"""
Test Runner Script for ValidoAI
Runs comprehensive test suites using multiple testing frameworks
"""

import os
import sys
import subprocess
import argparse
from datetime import datetime
import json

def setup_directories():
    """Create necessary test directories"""
    directories = [
        "tests/reports",
        "tests/reports/html",
        "tests/reports/coverage",
        "tests/reports/allure",
        "tests/reports/screenshots",
        "tests/reports/comprehensive",
        "tests/reports/api",
        "tests/reports/performance"
    ]

    for directory in directories:
        os.makedirs(directory, exist_ok=True)

def install_dependencies():
    """Install test dependencies"""
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "tests/requirements.txt"
        ], check=True)
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False
    return True

def run_unittest():
    """Run unittest tests"""
    print("\n🔍 Running Unittest Tests...")
    try:
        result = subprocess.run([
            sys.executable, "-m", "unittest",
            "discover", "tests",
            "-v",
            "-p", "test_*.py"
        ], capture_output=True, text=True)

        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)

        return result.returncode == 0
    except Exception as e:
        print(f"❌ Unittest failed: {e}")
        return False

def run_pytest():
    """Run pytest tests"""
    print("\n🔍 Running Pytest Tests...")
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest",
            "tests/test_ui_comprehensive.py",
            "--verbose",
            "--tb=short",
            "--html=tests/reports/html/index.html",
            "--self-contained-html",
            "--allure-dir=tests/reports/allure"
        ], capture_output=False)

        return result.returncode == 0
    except Exception as e:
        print(f"❌ Pytest failed: {e}")
        return False

def run_selenium_tests():
    """Run Selenium-based tests"""
    print("\n🔍 Running Selenium Tests...")
    try:
        result = subprocess.run([
            sys.executable, "tests/ui_test_framework.py"
        ], capture_output=False)

        return result.returncode == 0
    except Exception as e:
        print(f"❌ Selenium tests failed: {e}")
        return False

def run_api_tests():
    """Run API tests"""
    print("\n🔍 Running API Tests...")
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest",
            "tests/test_routes.py",
            "-v"
        ], capture_output=False)

        return result.returncode == 0
    except Exception as e:
        print(f"❌ API tests failed: {e}")
        return False

def generate_report():
    """Generate comprehensive test report"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    report_data = {
        "timestamp": timestamp,
        "test_run": {
            "date": datetime.now().isoformat(),
            "environment": "development",
            "python_version": sys.version,
            "os": os.name
        },
        "test_results": {
            "unittest": "pending",
            "pytest": "pending",
            "selenium": "pending",
            "api": "pending"
        },
        "summary": {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "success_rate": 0.0
        }
    }

    # Save report
    report_path = f"tests/reports/comprehensive/test_run_{timestamp}.json"
    with open(report_path, 'w') as f:
        json.dump(report_data, f, indent=2)

    print(f"\n📊 Test report saved to: {report_path}")
    print(f"📱 HTML report: tests/reports/html/index.html")
    print(f"🖼️  Screenshots: tests/reports/screenshots/")

def main():
    """Main test runner function"""
    parser = argparse.ArgumentParser(description="ValidoAI Test Runner")
    parser.add_argument("--install-deps", action="store_true", help="Install test dependencies")
    parser.add_argument("--unittest", action="store_true", help="Run only unittest tests")
    parser.add_argument("--pytest", action="store_true", help="Run only pytest tests")
    parser.add_argument("--selenium", action="store_true", help="Run only Selenium tests")
    parser.add_argument("--api", action="store_true", help="Run only API tests")
    parser.add_argument("--all", action="store_true", help="Run all tests")

    args = parser.parse_args()

    # Setup
    setup_directories()

    # Install dependencies if requested
    if args.install_deps:
        if not install_dependencies():
            return 1

    # Run specific test suites or all tests
    results = {}

    if args.unittest or args.all:
        results["unittest"] = run_unittest()

    if args.pytest or args.all:
        results["pytest"] = run_pytest()

    if args.selenium or args.all:
        results["selenium"] = run_selenium_tests()

    if args.api or args.all:
        results["api"] = run_api_tests()

    # If no specific tests were requested, run all
    if not any([args.unittest, args.pytest, args.selenium, args.api]):
        results["unittest"] = run_unittest()
        results["pytest"] = run_pytest()
        results["selenium"] = run_selenium_tests()
        results["api"] = run_api_tests()

    # Generate report
    generate_report()

    # Summary
    passed = sum(1 for result in results.values() if result)
    total = len(results)

    print(f"\n🎯 Test Summary:")
    print(f"Total test suites: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success rate: {(passed/total)*100:.1f}%")

    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")

    return 0 if passed == total else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
