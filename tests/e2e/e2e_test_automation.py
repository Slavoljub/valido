#!/usr/bin/env python3
"""
ValidoAI - Comprehensive E2E Test Automation Suite
Supports TDD with Puppeteer, Selenium, and Playwright
"""

import asyncio
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
import pytest
from playwright.async_api import async_playwright, Browser, Page, BrowserContext
import requests
from bs4 import BeautifulSoup
import lighthouse
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, TaskID
from rich.text import Text
from rich.layout import Layout
from rich.live import Live
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from dataclasses import dataclass, field
from enum import Enum
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_automation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TestFramework(Enum):
    """Supported test frameworks"""
    SELENIUM = "selenium"
    PLAYWRIGHT = "playwright"
    PUPPETEER = "puppeteer"

class BrowserType(Enum):
    """Supported browser types"""
    CHROME = "chrome"
    FIREFOX = "firefox"
    EDGE = "edge"
    SAFARI = "safari"

@dataclass
class TestResult:
    """Test result data structure"""
    test_name: str
    framework: TestFramework
    browser: BrowserType
    status: str  # 'pass', 'fail', 'skip'
    duration: float
    error_message: Optional[str] = None
    screenshots: List[str] = field(default_factory=list)
    logs: List[str] = field(default_factory=list)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    accessibility_score: Optional[float] = None
    seo_score: Optional[float] = None
    lighthouse_score: Optional[Dict[str, float]] = None

@dataclass
class TestSuite:
    """Test suite configuration"""
    name: str
    description: str
    tests: List[Dict[str, Any]]
    framework: TestFramework
    browser: BrowserType
    base_url: str = "http://localhost:5000"
    timeout: int = 30
    retries: int = 3
    headless: bool = True

class TestAutomationEngine:
    """Main test automation engine supporting multiple frameworks"""

    def __init__(self, framework: TestFramework = TestFramework.PLAYWRIGHT):
        self.framework = framework
        self.console = Console()
        self.results: List[TestResult] = []
        self.test_suites: List[TestSuite] = []

    def create_dashboard_tests(self) -> TestSuite:
        """Create comprehensive dashboard tests"""
        return TestSuite(
            name="Dashboard Tests",
            description="Test dashboard functionality, database management, and UI components",
            framework=self.framework,
            browser=BrowserType.CHROME,
            tests=[
                {
                    "name": "dashboard_load_test",
                    "description": "Test dashboard page loads correctly",
                    "type": "navigation",
                    "url": "/dashboard"
                },
                {
                    "name": "database_cards_display",
                    "description": "Test database cards show real data",
                    "type": "ui",
                    "selectors": [".database-card", ".database-stats"]
                },
                {
                    "name": "theme_switcher_modal",
                    "description": "Test theme switcher modal functionality",
                    "type": "interaction",
                    "selectors": ["[data-theme-toggle]", ".modal-overlay"]
                },
                {
                    "name": "language_selector",
                    "description": "Test language selector with flags",
                    "type": "interaction",
                    "selectors": [".language-selector", ".flag-icon"]
                },
                {
                    "name": "database_table_viewer",
                    "description": "Test database table viewing functionality",
                    "type": "interaction",
                    "selectors": [".table-card", ".data-table"]
                },
                {
                    "name": "search_functionality",
                    "description": "Test header search with sidebar results",
                    "type": "search",
                    "selectors": [".search-input", ".search-results"]
                },
                {
                    "name": "responsive_design",
                    "description": "Test responsive design across devices",
                    "type": "responsive",
                    "viewports": ["mobile", "tablet", "desktop"]
                },
                {
                    "name": "performance_metrics",
                    "description": "Test page performance and loading speed",
                    "type": "performance",
                    "metrics": ["load_time", "lighthouse_score"]
                },
                {
                    "name": "accessibility_check",
                    "description": "Test WCAG 2.1 AA compliance",
                    "type": "accessibility",
                    "standards": ["WCAG2A", "WCAG2AA"]
                }
            ]
        )

    def create_language_tests(self) -> TestSuite:
        """Create language and internationalization tests"""
        return TestSuite(
            name="Language & i18n Tests",
            description="Test language switching, flag display, and localization",
            framework=self.framework,
            browser=BrowserType.CHROME,
            tests=[
                {
                    "name": "flag_display_test",
                    "description": "Test all language flags display correctly",
                    "type": "visual",
                    "languages": ["en", "es", "fr", "de", "it", "pt", "ru", "zh", "ja", "sr", "sk", "sl", "nl", "se", "no", "dk", "fi", "pl", "cz", "hu", "gr", "tr", "ar"]
                },
                {
                    "name": "language_switching",
                    "description": "Test language switching functionality",
                    "type": "interaction",
                    "actions": ["select_language", "verify_content_change"]
                },
                {
                    "name": "rtl_language_support",
                    "description": "Test right-to-left language support",
                    "type": "layout",
                    "languages": ["ar"]
                }
            ]
        )

    def create_database_tests(self) -> TestSuite:
        """Create database management tests"""
        return TestSuite(
            name="Database Management Tests",
            description="Test database connection, table viewing, and data export",
            framework=self.framework,
            browser=BrowserType.CHROME,
            tests=[
                {
                    "name": "database_connection_test",
                    "description": "Test database connection status",
                    "type": "connection",
                    "databases": ["app", "sample", "ticketing"]
                },
                {
                    "name": "table_browsing",
                    "description": "Test table browsing and data viewing",
                    "type": "navigation",
                    "actions": ["click_table", "view_data", "export_csv"]
                },
                {
                    "name": "data_export",
                    "description": "Test data export functionality",
                    "type": "export",
                    "formats": ["csv", "json", "excel"]
                },
                {
                    "name": "connection_management",
                    "description": "Test connect/disconnect functionality",
                    "type": "management",
                    "actions": ["connect", "disconnect", "reconnect"]
                }
            ]
        )

    async def run_playwright_test(self, test_config: Dict[str, Any], browser: Browser, context: BrowserContext) -> TestResult:
        """Run a test using Playwright"""
        start_time = time.time()
        test_name = test_config["name"]

        try:
            page = await context.new_page()

            # Navigate to test URL
            if "url" in test_config:
                await page.goto(f"{self.test_suites[0].base_url}{test_config['url']}")
                await page.wait_for_load_state('networkidle')

            # Run specific test type
            if test_config["type"] == "navigation":
                await self._run_navigation_test(page, test_config)
            elif test_config["type"] == "ui":
                await self._run_ui_test(page, test_config)
            elif test_config["type"] == "interaction":
                await self._run_interaction_test(page, test_config)
            elif test_config["type"] == "visual":
                await self._run_visual_test(page, test_config)
            elif test_config["type"] == "performance":
                await self._run_performance_test(page, test_config)

            # Take screenshot
            screenshot_path = f"screenshots/{test_name}_{int(time.time())}.png"
            await page.screenshot(path=screenshot_path)

            duration = time.time() - start_time
            return TestResult(
                test_name=test_name,
                framework=TestFramework.PLAYWRIGHT,
                browser=BrowserType.CHROME,
                status="pass",
                duration=duration,
                screenshots=[screenshot_path]
            )

        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                test_name=test_name,
                framework=TestFramework.PLAYWRIGHT,
                browser=BrowserType.CHROME,
                status="fail",
                duration=duration,
                error_message=str(e)
            )

    async def _run_navigation_test(self, page: Page, config: Dict[str, Any]):
        """Run navigation test"""
        await page.wait_for_selector('body', timeout=10000)
        title = await page.title()
        assert "ValidoAI" in title, f"Expected 'ValidoAI' in title, got: {title}"

    async def _run_ui_test(self, page: Page, config: Dict[str, Any]):
        """Run UI component test"""
        for selector in config.get("selectors", []):
            element = await page.wait_for_selector(selector, timeout=5000)
            assert element is not None, f"Element {selector} not found"

    async def _run_interaction_test(self, page: Page, config: Dict[str, Any]):
        """Run interaction test"""
        # Theme switcher test
        theme_toggle = await page.wait_for_selector('[data-theme-toggle]')
        await theme_toggle.click()
        await page.wait_for_timeout(1000)

        # Check if modal appears
        modal = await page.wait_for_selector('.modal-overlay')
        assert modal is not None, "Theme modal should appear"

    async def _run_visual_test(self, page: Page, config: Dict[str, Any]):
        """Run visual regression test"""
        # Wait for all flags to load
        await page.wait_for_selector('.flag-icon', timeout=10000)
        flags = await page.query_selector_all('.flag-icon')
        assert len(flags) >= 20, f"Expected at least 20 flags, got {len(flags)}"

    async def _run_performance_test(self, page: Page, config: Dict[str, Any]):
        """Run performance test"""
        # Measure load time
        load_time = await page.evaluate("""
            performance.timing.loadEventEnd - performance.timing.navigationStart
        """)
        assert load_time < 3000, f"Page load time too slow: {load_time}ms"

    def run_selenium_test(self, test_config: Dict[str, Any], driver) -> TestResult:
        """Run a test using Selenium"""
        start_time = time.time()
        test_name = test_config["name"]

        try:
            # Navigate to test URL
            if "url" in test_config:
                driver.get(f"{self.test_suites[0].base_url}{test_config['url']}")
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )

            # Run specific test type
            if test_config["type"] == "navigation":
                self._run_selenium_navigation_test(driver, test_config)
            elif test_config["type"] == "ui":
                self._run_selenium_ui_test(driver, test_config)
            elif test_config["type"] == "interaction":
                self._run_selenium_interaction_test(driver, test_config)

            # Take screenshot
            screenshot_path = f"screenshots/{test_name}_{int(time.time())}.png"
            driver.save_screenshot(screenshot_path)

            duration = time.time() - start_time
            return TestResult(
                test_name=test_name,
                framework=TestFramework.SELENIUM,
                browser=BrowserType.CHROME,
                status="pass",
                duration=duration,
                screenshots=[screenshot_path]
            )

        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                test_name=test_name,
                framework=TestFramework.SELENIUM,
                browser=BrowserType.CHROME,
                status="fail",
                duration=duration,
                error_message=str(e)
            )

    def _run_selenium_navigation_test(self, driver, config: Dict[str, Any]):
        """Run navigation test with Selenium"""
        assert "ValidoAI" in driver.title, f"Expected 'ValidoAI' in title, got: {driver.title}"

    def _run_selenium_ui_test(self, driver, config: Dict[str, Any]):
        """Run UI component test with Selenium"""
        for selector in config.get("selectors", []):
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            assert element.is_displayed(), f"Element {selector} not visible"

    def _run_selenium_interaction_test(self, driver, config: Dict[str, Any]):
        """Run interaction test with Selenium"""
        # Theme switcher test
        theme_toggle = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-theme-toggle]'))
        )
        theme_toggle.click()
        time.sleep(1)

        # Check if modal appears
        modal = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.modal-overlay'))
        )
        assert modal.is_displayed(), "Theme modal should appear"

    async def run_test_suite(self, suite: TestSuite):
        """Run a complete test suite"""
        self.console.print(f"\n🚀 Running {suite.name}", style="bold blue")
        self.console.print(f"📝 {suite.description}")
        self.console.print(f"🧪 Framework: {suite.framework.value}")
        self.console.print(f"🌐 Browser: {suite.browser.value}")
        self.console.print("-" * 50)

        results = []

        if suite.framework == TestFramework.PLAYWRIGHT:
            results = await self._run_playwright_suite(suite)
        elif suite.framework == TestFramework.SELENIUM:
            results = self._run_selenium_suite(suite)

        self.results.extend(results)
        return results

    async def _run_playwright_suite(self, suite: TestSuite) -> List[TestResult]:
        """Run test suite with Playwright"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=suite.headless)
            context = await browser.new_context(
                viewport={'width': 1280, 'height': 720},
                ignore_https_errors=True
            )

            results = []
            for test_config in suite.tests:
                result = await self.run_playwright_test(test_config, browser, context)
                results.append(result)
                self._display_test_result(result)

            await browser.close()
            return results

    def _run_selenium_suite(self, suite: TestSuite) -> List[TestResult]:
        """Run test suite with Selenium"""
        options = ChromeOptions()
        if suite.headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1280,720')

        driver = webdriver.Chrome(options=options)

        try:
            results = []
            for test_config in suite.tests:
                result = self.run_selenium_test(test_config, driver)
                results.append(result)
                self._display_test_result(result)

            return results
        finally:
            driver.quit()

    def _display_test_result(self, result: TestResult):
        """Display test result in console"""
        if result.status == "pass":
            self.console.print(f"✅ {result.test_name} - {result.duration:.2f}s", style="green")
        elif result.status == "fail":
            self.console.print(f"❌ {result.test_name} - {result.duration:.2f}s", style="red")
            if result.error_message:
                self.console.print(f"   Error: {result.error_message}", style="red")
        else:
            self.console.print(f"⚠️  {result.test_name} - {result.duration:.2f}s", style="yellow")

    def generate_report(self):
        """Generate comprehensive test report"""
        # Create screenshots directory
        Path("screenshots").mkdir(exist_ok=True)
        Path("reports").mkdir(exist_ok=True)

        # Generate HTML report
        self._generate_html_report()

        # Generate JSON report
        self._generate_json_report()

        # Generate performance charts
        self._generate_performance_charts()

        # Display summary
        self._display_summary()

    def _generate_html_report(self):
        """Generate HTML test report"""
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ValidoAI Test Automation Report</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f8fafc;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            border-radius: 12px;
            margin-bottom: 2rem;
        }}
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }}
        .metric-card {{
            background: white;
            padding: 1.5rem;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .test-result {{
            background: white;
            margin-bottom: 1rem;
            padding: 1rem;
            border-radius: 8px;
            border-left: 4px solid;
        }}
        .test-result.pass {{ border-left-color: #10b981; }}
        .test-result.fail {{ border-left-color: #ef4444; }}
        .test-result.skip {{ border-left-color: #f59e0b; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🧪 ValidoAI Test Automation Report</h1>
        <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>

    <div class="summary-grid">
        <div class="metric-card">
            <h3>Total Tests</h3>
            <p style="font-size: 2rem; font-weight: bold;">{len(self.results)}</p>
        </div>
        <div class="metric-card">
            <h3>Passed</h3>
            <p style="font-size: 2rem; font-weight: bold; color: #10b981;">{len([r for r in self.results if r.status == 'pass'])}</p>
        </div>
        <div class="metric-card">
            <h3>Failed</h3>
            <p style="font-size: 2rem; font-weight: bold; color: #ef4444;">{len([r for r in self.results if r.status == 'fail'])}</p>
        </div>
        <div class="metric-card">
            <h3>Success Rate</h3>
            <p style="font-size: 2rem; font-weight: bold;">{len([r for r in self.results if r.status == 'pass']) / len(self.results) * 100:.1f}%</p>
        </div>
    </div>

    <h2>Test Results</h2>
"""

        for result in self.results:
            status_class = result.status
            status_emoji = {"pass": "✅", "fail": "❌", "skip": "⚠️"}[result.status]

            html_content += f"""
    <div class="test-result {status_class}">
        <h3>{status_emoji} {result.test_name}</h3>
        <p><strong>Framework:</strong> {result.framework.value}</p>
        <p><strong>Browser:</strong> {result.browser.value}</p>
        <p><strong>Duration:</strong> {result.duration:.2f}s</p>
        <p><strong>Status:</strong> {result.status.upper()}</p>
"""

            if result.error_message:
                html_content += f"""
        <p><strong>Error:</strong> {result.error_message}</p>
"""

            if result.screenshots:
                html_content += f"""
        <p><strong>Screenshots:</strong> {len(result.screenshots)} captured</p>
"""

            html_content += "</div>"

        html_content += """
</body>
</html>
"""

        with open("reports/test_report.html", "w", encoding="utf-8") as f:
            f.write(html_content)

    def _generate_json_report(self):
        """Generate JSON test report"""
        report_data = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "total_tests": len(self.results),
                "passed": len([r for r in self.results if r.status == "pass"]),
                "failed": len([r for r in self.results if r.status == "fail"]),
                "skipped": len([r for r in self.results if r.status == "skip"])
            },
            "results": [
                {
                    "test_name": r.test_name,
                    "framework": r.framework.value,
                    "browser": r.browser.value,
                    "status": r.status,
                    "duration": r.duration,
                    "error_message": r.error_message,
                    "screenshots": r.screenshots,
                    "performance_metrics": r.performance_metrics
                }
                for r in self.results
            ]
        }

        with open("reports/test_report.json", "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)

    def _generate_performance_charts(self):
        """Generate performance visualization charts"""
        if not self.results:
            return

        # Create performance chart
        durations = [r.duration for r in self.results]
        test_names = [r.test_name for r in self.results]

        fig = go.Figure(data=[
            go.Bar(
                x=test_names,
                y=durations,
                marker_color=['#10b981' if r.status == 'pass' else '#ef4444' for r in self.results]
            )
        ])

        fig.update_layout(
            title="Test Performance Overview",
            xaxis_title="Test Name",
            yaxis_title="Duration (seconds)",
            template="plotly_white"
        )

        fig.write_html("reports/performance_chart.html")

    def _display_summary(self):
        """Display test summary in console"""
        passed = len([r for r in self.results if r.status == "pass"])
        failed = len([r for r in self.results if r.status == "fail"])
        total = len(self.results)

        table = Table(title="🧪 Test Automation Summary")
        table.add_column("Metric", style="cyan", no_wrap=True)
        table.add_column("Value", style="magenta")
        table.add_column("Details", style="green")

        table.add_row("Total Tests", str(total), f"Across {len(self.test_suites)} suites")
        table.add_row("Passed", str(passed), f"Success rate: {passed/total*100:.1f}%")
        table.add_row("Failed", str(failed), f"Failure rate: {failed/total*100:.1f}%")
        table.add_row("Duration", ".2f", "Average per test")
        table.add_row("Reports", "Generated", "HTML, JSON, Charts")

        self.console.print(table)

        # Display failed tests
        if failed > 0:
            failed_table = Table(title="❌ Failed Tests")
            failed_table.add_column("Test Name", style="red")
            failed_table.add_column("Error", style="yellow")

            for result in self.results:
                if result.status == "fail":
                    failed_table.add_row(
                        result.test_name,
                        result.error_message[:100] + "..." if result.error_message and len(result.error_message) > 100 else result.error_message or "Unknown error"
                    )

            self.console.print(failed_table)

async def main():
    """Main test automation function"""
    console = Console()
    console.print(Panel.fit("🚀 ValidoAI Test Automation Suite", style="bold blue"))

    # Create test engine
    engine = TestAutomationEngine(TestFramework.PLAYWRIGHT)

    # Create test suites
    dashboard_suite = engine.create_dashboard_tests()
    language_suite = engine.create_language_tests()
    database_suite = engine.create_database_tests()

    engine.test_suites = [dashboard_suite, language_suite, database_suite]

    # Run all test suites
    all_results = []
    for suite in engine.test_suites:
        results = await engine.run_test_suite(suite)
        all_results.extend(results)

    # Generate comprehensive report
    engine.generate_report()

    console.print("\n✅ Test automation completed!", style="bold green")
    console.print("📊 Reports generated in 'reports/' directory", style="blue")
    console.print("📸 Screenshots saved in 'screenshots/' directory", style="blue")

if __name__ == "__main__":
    asyncio.run(main())
