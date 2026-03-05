#!/usr/bin/env python3
"""
Comprehensive Dashboard Test Suite for ValidoAI
Tests all dashboard features, layouts, themes, and functionality
"""

import os
import sys
import time
import json
import pytest
import requests
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.firefox.options import Options as FirefoxOptions
    from selenium.webdriver.edge.options import Options as EdgeOptions
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("Selenium not available - skipping browser tests")

try:
    import playwright
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("Playwright not available - skipping Playwright tests")

@dataclass
class TestResult:
    """Test result data structure"""
    test_name: str
    status: str  # 'PASS', 'FAIL', 'SKIP', 'ERROR'
    duration: float
    error_message: str = None
    screenshot_path: str = None
    browser: str = None
    timestamp: datetime = None

class DashboardTestSuite:
    """Comprehensive dashboard testing suite"""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.results: List[TestResult] = []
        self.screenshots_dir = project_root / "tests" / "screenshots"
        self.screenshots_dir.mkdir(exist_ok=True)
        
        # Test data
        self.test_data = {
            "dashboard_urls": [
                "/dashboard",
                "/dashboard/banking", 
                "/dashboard/compact"
            ],
            "themes": [
                "valido-white",
                "valido-dark", 
                "material-light",
                "material-dark",
                "dracula",
                "nord",
                "solarized-light",
                "monokai"
            ],
            "browsers": ["chrome", "firefox", "edge"] if SELENIUM_AVAILABLE else []
        }
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all test categories"""
        print("🚀 Starting Comprehensive Dashboard Test Suite")
        print("=" * 60)
        
        start_time = time.time()
        
        # Test categories
        test_categories = [
            ("Unit Tests", self.run_unit_tests),
            ("Integration Tests", self.run_integration_tests),
            ("UI Tests", self.run_ui_tests),
            ("Theme Tests", self.run_theme_tests),
            ("Responsive Tests", self.run_responsive_tests),
            ("Accessibility Tests", self.run_accessibility_tests),
            ("Performance Tests", self.run_performance_tests),
            ("Cross-browser Tests", self.run_cross_browser_tests),
            ("End-to-End Tests", self.run_e2e_tests)
        ]
        
        results = {}
        for category_name, test_func in test_categories:
            print(f"\n📋 Running {category_name}...")
            try:
                category_results = test_func()
                results[category_name] = category_results
                print(f"✅ {category_name} completed")
            except Exception as e:
                print(f"❌ {category_name} failed: {e}")
                results[category_name] = {"error": str(e)}
        
        total_duration = time.time() - start_time
        
        # Generate report
        report = self.generate_test_report(results, total_duration)
        
        print("\n" + "=" * 60)
        print("🎯 Test Suite Complete!")
        print(f"⏱️  Total Duration: {total_duration:.2f}s")
        print(f"📊 Results: {report['summary']}")
        
        return report
    
    def run_unit_tests(self) -> Dict[str, Any]:
        """Run unit tests for dashboard components"""
        results = {
            "tests_run": 0,
            "passed": 0,
            "failed": 0,
            "errors": []
        }
        
        # Test theme switching functionality
        try:
            # Test theme CSS loading
            for theme in self.test_data["themes"]:
                css_url = f"{self.base_url}/static/css/themes/{theme}.css"
                response = requests.get(css_url, timeout=10)
                if response.status_code == 200:
                    results["passed"] += 1
                else:
                    results["failed"] += 1
                    results["errors"].append(f"Theme {theme} CSS not found")
                results["tests_run"] += 1
        except Exception as e:
            results["errors"].append(f"Theme tests failed: {e}")
        
        # Test logo loading
        try:
            logo_url = f"{self.base_url}/static/img/valido.svg"
            response = requests.get(logo_url, timeout=10)
            if response.status_code == 200:
                results["passed"] += 1
            else:
                results["failed"] += 1
                results["errors"].append("Logo not found")
            results["tests_run"] += 1
        except Exception as e:
            results["errors"].append(f"Logo test failed: {e}")
        
        return results
    
    def run_integration_tests(self) -> Dict[str, Any]:
        """Run integration tests for dashboard functionality"""
        results = {
            "tests_run": 0,
            "passed": 0,
            "failed": 0,
            "errors": []
        }
        
        # Test dashboard endpoints
        for url in self.test_data["dashboard_urls"]:
            try:
                response = requests.get(f"{self.base_url}{url}", timeout=10)
                if response.status_code == 200:
                    results["passed"] += 1
                    # Check for required elements in response
                    if "ValidoAI" in response.text and "dashboard" in response.text.lower():
                        results["passed"] += 1
                    else:
                        results["failed"] += 1
                        results["errors"].append(f"Missing required content in {url}")
                else:
                    results["failed"] += 1
                    results["errors"].append(f"Endpoint {url} returned {response.status_code}")
                results["tests_run"] += 2
            except Exception as e:
                results["failed"] += 1
                results["errors"].append(f"Integration test failed for {url}: {e}")
                results["tests_run"] += 1
        
        return results
    
    def run_ui_tests(self) -> Dict[str, Any]:
        """Run UI tests using Selenium"""
        if not SELENIUM_AVAILABLE:
            return {"error": "Selenium not available"}
        
        results = {
            "tests_run": 0,
            "passed": 0,
            "failed": 0,
            "errors": [],
            "screenshots": []
        }
        
        # Test with Chrome
        try:
            chrome_options = ChromeOptions()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            
            driver = webdriver.Chrome(options=chrome_options)
            driver.set_window_size(1920, 1080)
            
            # Test dashboard pages
            for url in self.test_data["dashboard_urls"]:
                try:
                    driver.get(f"{self.base_url}{url}")
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.TAG_NAME, "body"))
                    )
                    
                    # Test sidebar toggle
                    try:
                        sidebar_toggle = driver.find_element(By.CSS_SELECTOR, "[onclick*='toggleSidebar']")
                        sidebar_toggle.click()
                        time.sleep(1)
                        results["passed"] += 1
                    except:
                        results["failed"] += 1
                        results["errors"].append(f"Sidebar toggle failed on {url}")
                    
                    # Test theme switcher
                    try:
                        theme_button = driver.find_element(By.CSS_SELECTOR, "[onclick*='switchTheme']")
                        theme_button.click()
                        time.sleep(1)
                        results["passed"] += 1
                    except:
                        results["failed"] += 1
                        results["errors"].append(f"Theme switcher failed on {url}")
                    
                    # Take screenshot
                    screenshot_path = self.screenshots_dir / f"ui_test_{url.replace('/', '_')}_{int(time.time())}.png"
                    driver.save_screenshot(str(screenshot_path))
                    results["screenshots"].append(str(screenshot_path))
                    
                    results["tests_run"] += 2
                    
                except Exception as e:
                    results["failed"] += 1
                    results["errors"].append(f"UI test failed for {url}: {e}")
                    results["tests_run"] += 1
            
            driver.quit()
            
        except Exception as e:
            results["errors"].append(f"Chrome UI tests failed: {e}")
        
        return results
    
    def run_theme_tests(self) -> Dict[str, Any]:
        """Test theme switching and appearance"""
        results = {
            "tests_run": 0,
            "passed": 0,
            "failed": 0,
            "errors": [],
            "theme_results": {}
        }
        
        if not SELENIUM_AVAILABLE:
            return {"error": "Selenium not available"}
        
        try:
            chrome_options = ChromeOptions()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            
            driver = webdriver.Chrome(options=chrome_options)
            driver.set_window_size(1920, 1080)
            
            for theme in self.test_data["themes"]:
                try:
                    # Test theme CSS loading
                    css_url = f"{self.base_url}/static/css/themes/{theme}.css"
                    response = requests.get(css_url, timeout=10)
                    
                    if response.status_code == 200:
                        results["theme_results"][theme] = "PASS"
                        results["passed"] += 1
                    else:
                        results["theme_results"][theme] = "FAIL"
                        results["failed"] += 1
                        results["errors"].append(f"Theme {theme} CSS not found")
                    
                    results["tests_run"] += 1
                    
                except Exception as e:
                    results["theme_results"][theme] = "ERROR"
                    results["failed"] += 1
                    results["errors"].append(f"Theme {theme} test failed: {e}")
                    results["tests_run"] += 1
            
            driver.quit()
            
        except Exception as e:
            results["errors"].append(f"Theme tests failed: {e}")
        
        return results
    
    def run_responsive_tests(self) -> Dict[str, Any]:
        """Test responsive design across different screen sizes"""
        if not SELENIUM_AVAILABLE:
            return {"error": "Selenium not available"}
        
        results = {
            "tests_run": 0,
            "passed": 0,
            "failed": 0,
            "errors": [],
            "responsive_results": {}
        }
        
        screen_sizes = [
            (1920, 1080, "desktop"),
            (1024, 768, "tablet"),
            (768, 1024, "tablet-portrait"),
            (375, 667, "mobile"),
            (320, 568, "mobile-small")
        ]
        
        try:
            chrome_options = ChromeOptions()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            
            driver = webdriver.Chrome(options=chrome_options)
            
            for width, height, device in screen_sizes:
                try:
                    driver.set_window_size(width, height)
                    
                    for url in self.test_data["dashboard_urls"]:
                        driver.get(f"{self.base_url}{url}")
                        time.sleep(2)
                        
                        # Check if page loads properly
                        body = driver.find_element(By.TAG_NAME, "body")
                        if body.is_displayed():
                            results["responsive_results"][f"{device}_{url}"] = "PASS"
                            results["passed"] += 1
                        else:
                            results["responsive_results"][f"{device}_{url}"] = "FAIL"
                            results["failed"] += 1
                        
                        # Take screenshot
                        screenshot_path = self.screenshots_dir / f"responsive_{device}_{url.replace('/', '_')}_{int(time.time())}.png"
                        driver.save_screenshot(str(screenshot_path))
                        
                        results["tests_run"] += 1
                        
                except Exception as e:
                    results["responsive_results"][device] = "ERROR"
                    results["failed"] += 1
                    results["errors"].append(f"Responsive test failed for {device}: {e}")
                    results["tests_run"] += 1
            
            driver.quit()
            
        except Exception as e:
            results["errors"].append(f"Responsive tests failed: {e}")
        
        return results
    
    def run_accessibility_tests(self) -> Dict[str, Any]:
        """Test accessibility features"""
        results = {
            "tests_run": 0,
            "passed": 0,
            "failed": 0,
            "errors": [],
            "accessibility_issues": []
        }
        
        if not SELENIUM_AVAILABLE:
            return {"error": "Selenium not available"}
        
        try:
            chrome_options = ChromeOptions()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            
            driver = webdriver.Chrome(options=chrome_options)
            
            for url in self.test_data["dashboard_urls"]:
                try:
                    driver.get(f"{self.base_url}{url}")
                    
                    # Test skip navigation link
                    try:
                        skip_link = driver.find_element(By.CSS_SELECTOR, "a[href='#main-content']")
                        if skip_link.is_displayed():
                            results["passed"] += 1
                        else:
                            results["failed"] += 1
                            results["accessibility_issues"].append("Skip navigation link not visible")
                    except:
                        results["failed"] += 1
                        results["accessibility_issues"].append("Skip navigation link not found")
                    
                    # Test alt text for images
                    images = driver.find_elements(By.TAG_NAME, "img")
                    for img in images:
                        alt_text = img.get_attribute("alt")
                        if not alt_text:
                            results["accessibility_issues"].append(f"Image missing alt text: {img.get_attribute('src')}")
                    
                    # Test form labels
                    inputs = driver.find_elements(By.TAG_NAME, "input")
                    for input_elem in inputs:
                        input_id = input_elem.get_attribute("id")
                        if input_id:
                            label = driver.find_element(By.CSS_SELECTOR, f"label[for='{input_id}']")
                            if not label:
                                results["accessibility_issues"].append(f"Input missing label: {input_id}")
                    
                    results["tests_run"] += 1
                    
                except Exception as e:
                    results["failed"] += 1
                    results["errors"].append(f"Accessibility test failed for {url}: {e}")
                    results["tests_run"] += 1
            
            driver.quit()
            
        except Exception as e:
            results["errors"].append(f"Accessibility tests failed: {e}")
        
        return results
    
    def run_performance_tests(self) -> Dict[str, Any]:
        """Test dashboard performance"""
        results = {
            "tests_run": 0,
            "passed": 0,
            "failed": 0,
            "errors": [],
            "performance_metrics": {}
        }
        
        for url in self.test_data["dashboard_urls"]:
            try:
                start_time = time.time()
                response = requests.get(f"{self.base_url}{url}", timeout=30)
                load_time = time.time() - start_time
                
                results["performance_metrics"][url] = {
                    "load_time": load_time,
                    "status_code": response.status_code,
                    "content_length": len(response.content)
                }
                
                # Performance thresholds
                if load_time < 3.0:  # 3 seconds
                    results["passed"] += 1
                else:
                    results["failed"] += 1
                    results["errors"].append(f"Slow load time for {url}: {load_time:.2f}s")
                
                if response.status_code == 200:
                    results["passed"] += 1
                else:
                    results["failed"] += 1
                    results["errors"].append(f"HTTP error for {url}: {response.status_code}")
                
                results["tests_run"] += 2
                
            except Exception as e:
                results["failed"] += 1
                results["errors"].append(f"Performance test failed for {url}: {e}")
                results["tests_run"] += 1
        
        return results
    
    def run_cross_browser_tests(self) -> Dict[str, Any]:
        """Test across different browsers"""
        if not SELENIUM_AVAILABLE:
            return {"error": "Selenium not available"}
        
        results = {
            "tests_run": 0,
            "passed": 0,
            "failed": 0,
            "errors": [],
            "browser_results": {}
        }
        
        browsers = {
            "chrome": ChromeOptions,
            "firefox": FirefoxOptions,
            "edge": EdgeOptions
        }
        
        for browser_name, options_class in browsers.items():
            try:
                options = options_class()
                options.add_argument("--headless")
                options.add_argument("--no-sandbox")
                
                if browser_name == "chrome":
                    driver = webdriver.Chrome(options=options)
                elif browser_name == "firefox":
                    driver = webdriver.Firefox(options=options)
                elif browser_name == "edge":
                    driver = webdriver.Edge(options=options)
                
                driver.set_window_size(1920, 1080)
                
                browser_results = {}
                
                for url in self.test_data["dashboard_urls"]:
                    try:
                        driver.get(f"{self.base_url}{url}")
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.TAG_NAME, "body"))
                        )
                        
                        # Basic functionality test
                        title = driver.title
                        if "ValidoAI" in title:
                            browser_results[url] = "PASS"
                            results["passed"] += 1
                        else:
                            browser_results[url] = "FAIL"
                            results["failed"] += 1
                        
                        results["tests_run"] += 1
                        
                    except Exception as e:
                        browser_results[url] = "ERROR"
                        results["failed"] += 1
                        results["errors"].append(f"{browser_name} test failed for {url}: {e}")
                        results["tests_run"] += 1
                
                results["browser_results"][browser_name] = browser_results
                driver.quit()
                
            except Exception as e:
                results["errors"].append(f"{browser_name} tests failed: {e}")
        
        return results
    
    def run_e2e_tests(self) -> Dict[str, Any]:
        """Run end-to-end tests"""
        if not PLAYWRIGHT_AVAILABLE:
            return {"error": "Playwright not available"}
        
        results = {
            "tests_run": 0,
            "passed": 0,
            "failed": 0,
            "errors": [],
            "e2e_scenarios": {}
        }
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                # Test complete user journey
                scenarios = [
                    {
                        "name": "dashboard_navigation",
                        "steps": [
                            ("navigate", "/dashboard"),
                            ("click", "[onclick*='toggleSidebar']"),
                            ("wait", 1000),
                            ("click", "a[href='/dashboard/banking']"),
                            ("wait", 2000),
                            ("verify", "text=Banking Dashboard")
                        ]
                    },
                    {
                        "name": "theme_switching",
                        "steps": [
                            ("navigate", "/dashboard"),
                            ("click", "[onclick*='switchTheme']"),
                            ("wait", 1000),
                            ("verify", "css=[data-theme]")
                        ]
                    }
                ]
                
                for scenario in scenarios:
                    try:
                        scenario_results = []
                        
                        for step_type, step_data in scenario["steps"]:
                            if step_type == "navigate":
                                page.goto(f"{self.base_url}{step_data}")
                            elif step_type == "click":
                                page.click(step_data)
                            elif step_type == "wait":
                                page.wait_for_timeout(step_data)
                            elif step_type == "verify":
                                if step_data.startswith("text="):
                                    text = step_data[5:]
                                    if page.locator(f"text={text}").count() > 0:
                                        scenario_results.append("PASS")
                                    else:
                                        scenario_results.append("FAIL")
                                elif step_data.startswith("css="):
                                    selector = step_data[4:]
                                    if page.locator(selector).count() > 0:
                                        scenario_results.append("PASS")
                                    else:
                                        scenario_results.append("FAIL")
                        
                        if all(result == "PASS" for result in scenario_results):
                            results["e2e_scenarios"][scenario["name"]] = "PASS"
                            results["passed"] += 1
                        else:
                            results["e2e_scenarios"][scenario["name"]] = "FAIL"
                            results["failed"] += 1
                        
                        results["tests_run"] += 1
                        
                    except Exception as e:
                        results["e2e_scenarios"][scenario["name"]] = "ERROR"
                        results["failed"] += 1
                        results["errors"].append(f"E2E scenario {scenario['name']} failed: {e}")
                        results["tests_run"] += 1
                
                browser.close()
                
        except Exception as e:
            results["errors"].append(f"E2E tests failed: {e}")
        
        return results
    
    def generate_test_report(self, results: Dict[str, Any], total_duration: float) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        total_tests = 0
        total_passed = 0
        total_failed = 0
        total_errors = 0
        
        for category, category_results in results.items():
            if isinstance(category_results, dict) and "tests_run" in category_results:
                total_tests += category_results.get("tests_run", 0)
                total_passed += category_results.get("passed", 0)
                total_failed += category_results.get("failed", 0)
                total_errors += len(category_results.get("errors", []))
        
        summary = {
            "total_tests": total_tests,
            "passed": total_passed,
            "failed": total_failed,
            "errors": total_errors,
            "success_rate": (total_passed / total_tests * 100) if total_tests > 0 else 0,
            "duration": total_duration
        }
        
        # Save detailed report
        report_path = project_root / "tests" / "reports" / f"dashboard_test_report_{int(time.time())}.json"
        report_path.parent.mkdir(exist_ok=True)
        
        full_report = {
            "timestamp": datetime.now().isoformat(),
            "summary": summary,
            "detailed_results": results,
            "test_configuration": {
                "base_url": self.base_url,
                "themes_tested": self.test_data["themes"],
                "browsers_tested": self.test_data["browsers"],
                "urls_tested": self.test_data["dashboard_urls"]
            }
        }
        
        with open(report_path, 'w') as f:
            json.dump(full_report, f, indent=2)
        
        return full_report

def main():
    """Main test runner"""
    # Check if server is running
    try:
        response = requests.get("http://localhost:5000", timeout=5)
        if response.status_code != 200:
            print("❌ Server not responding properly")
            return
    except:
        print("❌ Server not running on localhost:5000")
        print("Please start the Flask application first:")
        print("python app.py")
        return
    
    # Run test suite
    test_suite = DashboardTestSuite()
    report = test_suite.run_all_tests()
    
    # Print summary
    summary = report["summary"]
    print(f"\n📊 Test Summary:")
    print(f"   Total Tests: {summary['total_tests']}")
    print(f"   Passed: {summary['passed']}")
    print(f"   Failed: {summary['failed']}")
    print(f"   Errors: {summary['errors']}")
    print(f"   Success Rate: {summary['success_rate']:.1f}%")
    print(f"   Duration: {summary['duration']:.2f}s")
    
    # Exit with appropriate code
    if summary['failed'] > 0 or summary['errors'] > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
