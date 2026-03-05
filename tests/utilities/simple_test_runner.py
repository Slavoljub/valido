#!/usr/bin/env python3
"""
Simple Test Runner for ValidoAI
Basic functionality tests to verify project is working
"""

import os
import sys
import time
import json
import requests
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

class SimpleTestRunner:
    def __init__(self):
        self.base_url = "http://localhost:5000"
        self.test_results = []
        self.start_time = datetime.now()

    def setup_webdriver(self, headless=True):
        """Setup Selenium WebDriver"""
        options = Options()
        if headless:
            options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")

        return webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )

    def record_test_result(self, test_name, status, error_message=None, details=None):
        """Record test result"""
        result = {
            "test_name": test_name,
            "status": status,
            "error_message": str(error_message) if error_message else None,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{'✅' if status == 'passed' else '❌'} {test_name}: {status.upper()}")
        if error_message:
            print(f"   Error: {error_message}")

    def test_app_running(self):
        """Test if Flask app is running"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=10)
            if response.status_code == 200:
                self.record_test_result("Flask App Running", "passed", details=f"Status: {response.status_code}")
            else:
                self.record_test_result("Flask App Running", "failed", f"Status: {response.status_code}")
        except Exception as e:
            self.record_test_result("Flask App Running", "failed", str(e))

    def test_ui_examples_page(self):
        """Test UI examples page loads and has expected content"""
        try:
            driver = self.setup_webdriver()
            driver.get(f"{self.base_url}/ui-examples")
            time.sleep(2)

            # Check page title
            if "UI Examples" in driver.title:
                self.record_test_result("UI Examples Page", "passed")
            else:
                self.record_test_result("UI Examples Page", "failed", f"Title: {driver.title}")

            # Check for theme switching buttons
            theme_buttons = driver.find_elements(By.CSS_SELECTOR, "[data-theme]")
            if len(theme_buttons) > 0:
                self.record_test_result("Theme Buttons Present", "passed", details=f"Found {len(theme_buttons)} theme buttons")
            else:
                self.record_test_result("Theme Buttons Present", "failed", "No theme buttons found")

            # Check for WYSIWYG editor
            editor_elements = driver.find_elements(By.CSS_SELECTOR, "[data-froala-editor]")
            if len(editor_elements) > 0:
                self.record_test_result("WYSIWYG Editor Present", "passed", details=f"Found {len(editor_elements)} editor elements")
            else:
                self.record_test_result("WYSIWYG Editor Present", "failed", "No WYSIWYG editor found")

            # Check for gallery system
            gallery_elements = driver.find_elements(By.CSS_SELECTOR, "[data-gallery], .cursor-pointer img")
            if len(gallery_elements) > 0:
                self.record_test_result("Gallery System Present", "passed", details=f"Found {len(gallery_elements)} gallery elements")
            else:
                self.record_test_result("Gallery System Present", "failed", "No gallery elements found")

            driver.quit()

        except Exception as e:
            self.record_test_result("UI Examples Page", "failed", str(e))

    def test_theme_switching(self):
        """Test theme switching functionality"""
        try:
            driver = self.setup_webdriver()
            driver.get(f"{self.base_url}/ui-examples")
            time.sleep(2)

            # Get initial theme
            body = driver.find_element(By.TAG_NAME, "body")
            initial_theme = body.get_attribute("data-theme") or "valido-white"

            # Click a different theme
            themes_to_test = ["valido-dark", "material-light", "dracula"]
            for theme in themes_to_test:
                try:
                    theme_button = driver.find_element(By.CSS_SELECTOR, f"[data-theme='{theme}']")
                    theme_button.click()
                    time.sleep(1)

                    # Check if theme changed
                    current_theme = body.get_attribute("data-theme")
                    if theme in (current_theme or ""):
                        self.record_test_result(f"Theme Switch to {theme}", "passed")
                    else:
                        self.record_test_result(f"Theme Switch to {theme}", "failed", f"Theme not changed to {theme}")
                    break
                except Exception as e:
                    continue

            driver.quit()

        except Exception as e:
            self.record_test_result("Theme Switching", "failed", str(e))

    def test_easy_features(self):
        """Test easy-to-implement features"""
        try:
            driver = self.setup_webdriver()
            driver.get(f"{self.base_url}/ui-examples")
            time.sleep(2)

            features_to_test = [
                ("Back to Top Button", "#back-to-top"),
                ("Reading Progress", "#reading-progress"),
                ("Copy to Clipboard", "[data-copy]"),
                ("Enhanced Tooltips", "[data-tooltip]"),
                ("Loading Animations", "[data-loading]"),
                ("Dark Mode Toggle", "[data-theme-toggle]")
            ]

            for feature_name, selector in features_to_test:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if len(elements) > 0:
                        self.record_test_result(feature_name, "passed", details=f"Found {len(elements)} elements")
                    else:
                        self.record_test_result(feature_name, "failed", f"No elements found for {selector}")
                except Exception as e:
                    self.record_test_result(feature_name, "failed", str(e))

            driver.quit()

        except Exception as e:
            self.record_test_result("Easy Features", "failed", str(e))

    def test_responsive_design(self):
        """Test responsive design"""
        try:
            driver = self.setup_webdriver()

            screen_sizes = [
                (1920, 1080, "desktop"),
                (768, 1024, "tablet"),
                (375, 667, "mobile")
            ]

            for width, height, device in screen_sizes:
                driver.get(f"{self.base_url}/ui-examples")
                driver.set_window_size(width, height)
                time.sleep(1)

                # Check if page is responsive
                body = driver.find_element(By.TAG_NAME, "body")
                scroll_width = driver.execute_script("return document.body.scrollWidth")
                viewport_width = driver.execute_script("return window.innerWidth")

                if scroll_width <= viewport_width + 20:
                    self.record_test_result(f"Responsive {device}", "passed", details=f"{width}x{height}")
                else:
                    self.record_test_result(f"Responsive {device}", "failed", details=f"Horizontal scroll detected: {scroll_width}px > {viewport_width}px")

            driver.quit()

        except Exception as e:
            self.record_test_result("Responsive Design", "failed", str(e))

    def test_performance_metrics(self):
        """Test basic performance metrics"""
        try:
            driver = self.setup_webdriver()
            driver.get(f"{self.base_url}/ui-examples")

            # Get performance metrics
            navigation = driver.execute_script("return performance.getEntriesByType('navigation')[0]")

            if navigation:
                load_time = navigation['loadEventEnd'] - navigation['fetchStart']
                dom_time = navigation['domContentLoadedEventEnd'] - navigation['fetchStart']

                # Record metrics
                self.record_test_result("Performance Load Time", "passed" if load_time < 3000 else "failed",
                                      details=f"Load time: {load_time:.2f}ms")
                self.record_test_result("Performance DOM Ready", "passed" if dom_time < 2000 else "failed",
                                      details=f"DOM ready: {dom_time:.2f}ms")
            else:
                self.record_test_result("Performance Metrics", "failed", "Could not get performance data")

            driver.quit()

        except Exception as e:
            self.record_test_result("Performance Metrics", "failed", str(e))

    def generate_report(self):
        """Generate test report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["status"] == "passed"])
        failed_tests = total_tests - passed_tests

        # Generate HTML report
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>ValidoAI Test Report - {timestamp}</title>
            <style>
                * {{ box-sizing: border-box; }}
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
                .container {{ max-width: 1200px; margin: 0 auto; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px; }}
                .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }}
                .stat-card {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); text-align: center; }}
                .stat-number {{ font-size: 2.5em; font-weight: bold; margin: 0; }}
                .stat-label {{ color: #666; margin: 5px 0 0 0; }}
                .passed {{ color: #28a745; }}
                .failed {{ color: #dc3545; }}
                .test-results {{ background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); overflow: hidden; }}
                .test-result {{ padding: 15px 20px; border-bottom: 1px solid #eee; display: flex; align-items: center; justify-content: space-between; }}
                .test-result:last-child {{ border-bottom: none; }}
                .test-name {{ font-weight: 600; }}
                .test-status {{ padding: 4px 12px; border-radius: 4px; font-size: 0.85em; font-weight: 600; }}
                .status-passed {{ background: #d4edda; color: #155724; }}
                .status-failed {{ background: #f8d7da; color: #721c24; }}
                .error-details {{ background: #f8f9fa; padding: 10px; border-radius: 4px; margin: 10px 0; font-family: monospace; font-size: 0.85em; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🧪 ValidoAI Test Report</h1>
                    <p>Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
                    <p>Simple Test Suite Results</p>
                </div>

                <div class="stats">
                    <div class="stat-card">
                        <div class="stat-number">{total_tests}</div>
                        <div class="stat-label">Total Tests</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number passed">{passed_tests}</div>
                        <div class="stat-label">Passed</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number failed">{failed_tests}</div>
                        <div class="stat-label">Failed</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{(passed_tests/total_tests*100):.1f}%</div>
                        <div class="stat-label">Success Rate</div>
                    </div>
                </div>

                <div class="test-results">
                    <h2 style="padding: 20px; margin: 0; background: #f8f9fa; border-bottom: 2px solid #e9ecef;">Test Results</h2>
        """

        for result in self.test_results:
            status_class = "status-passed" if result["status"] == "passed" else "status-failed"
            html_content += f"""
                    <div class="test-result">
                        <div>
                            <div class="test-name">{result['test_name']}</div>
                            <div class="test-status {status_class}">{result['status'].upper()}</div>
                            {f'<div class="error-details">{result["error_message"]}</div>' if result["error_message"] else ''}
                        </div>
                    </div>
            """

        html_content += """
                </div>
            </div>
        </body>
        </html>
        """

        # Save report
        os.makedirs("tests/reports", exist_ok=True)
        report_path = f"tests/reports/simple_test_report_{timestamp}.html"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"\n📊 Test report generated: {report_path}")
        print(f"✅ Success Rate: {(passed_tests/total_tests)*100:.1f}%")

        return (passed_tests/total_tests*100)

    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting Simple Test Suite")
        print("=" * 50)

        # Run tests
        self.test_app_running()
        self.test_ui_examples_page()
        self.test_theme_switching()
        self.test_easy_features()
        self.test_responsive_design()
        self.test_performance_metrics()

        # Generate report and get success rate
        success_rate = self.generate_report()

        return success_rate

def main():
    """Main function"""
    runner = SimpleTestRunner()
    success_rate = runner.run_all_tests()

    # Exit with appropriate code
    if success_rate >= 80:
        print(f"\n🎉 All tests completed with {success_rate:.1f}% success rate!")
        sys.exit(0)
    else:
        print(f"\n⚠️  Tests completed with {success_rate:.1f}% success rate - needs improvement")
        sys.exit(1)

if __name__ == "__main__":
    main()
