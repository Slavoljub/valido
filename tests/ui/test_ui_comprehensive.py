#!/usr/bin/env python3
"""
Comprehensive UI Testing Suite
Using pytest, Selenium, and Playwright for thorough testing
"""

import pytest
import time
import json
import os
from datetime import datetime
from typing import Dict, List
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from playwright.sync_api import sync_playwright
import requests
from bs4 import BeautifulSoup
import allure
from _pytest.nodes import Item
import pytest_html
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Configuration
BASE_URL = "http://localhost:5000"
SCREENSHOT_DIR = "tests/reports/screenshots"
REPORT_DIR = "tests/reports/comprehensive"

@pytest.fixture(scope="session")
def browser_config():
    """Browser configuration for tests"""
    return {
        "headless": True,
        "window_size": (1920, 1080),
        "implicit_wait": 10,
        "page_load_timeout": 30
    }

@pytest.fixture
def selenium_driver(browser_config):
    """Selenium WebDriver fixture"""
    options = Options()
    if browser_config["headless"]:
        options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(f"--window-size={browser_config['window_size'][0]},{browser_config['window_size'][1]}")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    driver.implicitly_wait(browser_config["implicit_wait"])
    driver.set_page_load_timeout(browser_config["page_load_timeout"])

    yield driver
    driver.quit()

@pytest.fixture
def playwright_page():
    """Playwright page fixture"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()
        yield page
        browser.close()

@allure.feature("Theme System")
@allure.story("Theme Switching")
class TestThemeSystem:
    """Test theme switching functionality"""

    @allure.step("Test individual theme switching")
    @pytest.mark.parametrize("theme", [
        "valido-white", "valido-dark", "material-light", "material-dark",
        "dracula", "monokai", "nord", "solarized-light"
    ])
    def test_individual_theme_switch(self, selenium_driver, theme):
        """Test switching to individual themes"""
        with allure.step(f"Switch to {theme} theme"):
            selenium_driver.get(f"{BASE_URL}/ui-examples")

            # Click theme button
            theme_button = WebDriverWait(selenium_driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, f"[data-theme='{theme}']"))
            )
            theme_button.click()

            # Wait for theme to apply
            time.sleep(1)

            # Verify theme was applied
            body = selenium_driver.find_element(By.TAG_NAME, "body")
            current_theme = body.get_attribute("data-theme")

            # Take screenshot
            screenshot_path = f"{SCREENSHOT_DIR}/theme_{theme}_{datetime.now().strftime('%H%M%S')}.png"
            selenium_driver.save_screenshot(screenshot_path)
            allure.attach.file(screenshot_path, f"Theme {theme} screenshot", allure.attachment_type.PNG)

            assert theme in (current_theme or ""), f"Theme {theme} was not applied correctly"

    @allure.step("Test theme persistence")
    def test_theme_persistence(self, selenium_driver):
        """Test that theme choice persists across page reloads"""
        selenium_driver.get(f"{BASE_URL}/ui-examples")

        # Set theme to dark
        dark_button = WebDriverWait(selenium_driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-theme='valido-dark']"))
        )
        dark_button.click()
        time.sleep(1)

        # Reload page
        selenium_driver.refresh()
        time.sleep(2)

        # Check if theme persisted
        body = selenium_driver.find_element(By.TAG_NAME, "body")
        current_theme = body.get_attribute("data-theme")

        assert "valido-dark" in (current_theme or ""), "Theme did not persist after page reload"

    @allure.step("Test theme with Playwright")
    def test_theme_playwright(self, playwright_page):
        """Test theme switching using Playwright"""
        playwright_page.goto(f"{BASE_URL}/ui-examples")

        # Switch theme
        playwright_page.click("[data-theme='valido-dark']")
        playwright_page.wait_for_timeout(1000)

        # Verify theme applied
        theme_attribute = playwright_page.get_attribute("body", "data-theme")
        assert "valido-dark" in (theme_attribute or ""), "Theme not applied in Playwright test"

        # Screenshot
        screenshot_path = f"{SCREENSHOT_DIR}/playwright_theme_test.png"
        playwright_page.screenshot(path=screenshot_path)
        allure.attach.file(screenshot_path, "Playwright theme test", allure.attachment_type.PNG)

@allure.feature("Responsive Design")
@allure.story("Cross-Device Compatibility")
class TestResponsiveDesign:
    """Test responsive design across different devices"""

    @allure.step("Test different screen sizes")
    @pytest.mark.parametrize("width,height,device", [
        (1920, 1080, "desktop"),
        (1366, 768, "laptop"),
        (768, 1024, "tablet_portrait"),
        (1024, 768, "tablet_landscape"),
        (375, 667, "mobile_portrait"),
        (667, 375, "mobile_landscape"),
        (320, 568, "small_mobile"),
        (414, 896, "large_mobile")
    ])
    def test_screen_sizes(self, selenium_driver, width, height, device):
        """Test UI across different screen sizes"""
        selenium_driver.get(f"{BASE_URL}/ui-examples")
        selenium_driver.set_window_size(width, height)
        time.sleep(1)

        # Check that page loads and is responsive
        body = selenium_driver.find_element(By.TAG_NAME, "body")
        assert body.is_displayed(), f"Body not displayed on {device}"

        # Check for horizontal scroll (should not exist on responsive design)
        scroll_width = selenium_driver.execute_script("return document.body.scrollWidth")
        viewport_width = selenium_driver.execute_script("return window.innerWidth")

        # Allow some tolerance for scroll bars
        assert scroll_width <= viewport_width + 20, f"Horizontal scroll detected on {device}"

        # Screenshot
        screenshot_path = f"{SCREENSHOT_DIR}/responsive_{device}_{datetime.now().strftime('%H%M%S')}.png"
        selenium_driver.save_screenshot(screenshot_path)
        allure.attach.file(screenshot_path, f"Responsive {device} screenshot", allure.attachment_type.PNG)

@allure.feature("Gallery System")
@allure.story("Interactive Media Gallery")
class TestGallerySystem:
    """Test gallery system functionality"""

    @allure.step("Test image gallery")
    def test_image_gallery(self, selenium_driver):
        """Test clicking on images opens gallery"""
        selenium_driver.get(f"{BASE_URL}/ui-examples")

        # Find clickable images
        images = selenium_driver.find_elements(By.CSS_SELECTOR, ".cursor-pointer img")
        assert len(images) > 0, "No clickable images found"

        # Click first image
        images[0].click()
        time.sleep(1)

        # Check if gallery modal opened
        modal = selenium_driver.find_element(By.ID, "gallery-modal")
        assert modal.is_displayed(), "Gallery modal did not open"

        # Test navigation
        next_button = selenium_driver.find_element(By.CSS_SELECTOR, "[onclick*='nextItem']")
        next_button.click()
        time.sleep(0.5)

        prev_button = selenium_driver.find_element(By.CSS_SELECTOR, "[onclick*='previousItem']")
        prev_button.click()
        time.sleep(0.5)

        # Close gallery
        close_button = selenium_driver.find_element(By.CSS_SELECTOR, "[onclick*='closeGallery']")
        close_button.click()
        time.sleep(0.5)

        # Verify modal is closed
        assert not modal.is_displayed(), "Gallery modal did not close"

        screenshot_path = f"{SCREENSHOT_DIR}/gallery_test_{datetime.now().strftime('%H%M%S')}.png"
        selenium_driver.save_screenshot(screenshot_path)
        allure.attach.file(screenshot_path, "Gallery test screenshot", allure.attachment_type.PNG)

@allure.feature("Text Editor")
@allure.story("Inline Text Editing")
class TestTextEditor:
    """Test text editor functionality"""

    @allure.step("Test inline text editing")
    def test_inline_editing(self, selenium_driver):
        """Test double-click to edit text"""
        selenium_driver.get(f"{BASE_URL}/ui-examples")

        # Find editable element
        editable_elements = selenium_driver.find_elements(By.CSS_SELECTOR, "[data-editable]")
        assert len(editable_elements) > 0, "No editable elements found"

        # Double-click to edit
        element = editable_elements[0]
        ActionChains(selenium_driver).double_click(element).perform()
        time.sleep(1)

        # Type text
        element.send_keys(" Test content added by automation")
        time.sleep(0.5)

        # Click outside to save
        body = selenium_driver.find_element(By.TAG_NAME, "body")
        body.click()
        time.sleep(0.5)

        # Verify text was added
        updated_text = element.text
        assert "Test content added by automation" in updated_text, "Text edit was not saved"

        screenshot_path = f"{SCREENSHOT_DIR}/text_editor_test_{datetime.now().strftime('%H%M%S')}.png"
        selenium_driver.save_screenshot(screenshot_path)
        allure.attach.file(screenshot_path, "Text editor test screenshot", allure.attachment_type.PNG)

@allure.feature("Performance Testing")
@allure.story("Load Times and Performance")
class TestPerformance:
    """Test performance metrics"""

    @allure.step("Test page load performance")
    def test_page_load_performance(self, selenium_driver):
        """Test page load times"""
        start_time = time.time()
        selenium_driver.get(f"{BASE_URL}/ui-examples")
        end_time = time.time()

        load_time = (end_time - start_time) * 1000  # Convert to milliseconds

        # Get additional performance metrics
        navigation = selenium_driver.execute_script("""
            return performance.getEntriesByType('navigation')[0];
        """)

        if navigation:
            dom_load_time = navigation['domContentLoadedEventEnd'] - navigation['fetchStart']
            full_load_time = navigation['loadEventEnd'] - navigation['fetchStart']

            allure.attach(f"""
            Page Load Performance:
            - Initial Load: {load_time:.2f}ms
            - DOM Load: {dom_load_time:.2f}ms
            - Full Load: {full_load_time:.2f}ms
            """, "Performance Metrics", allure.attachment_type.TEXT)

            # Assert reasonable load times
            assert full_load_time < 5000, f"Page load too slow: {full_load_time}ms"
            assert dom_load_time < 3000, f"DOM load too slow: {dom_load_time}ms"

    @allure.step("Test theme switching performance")
    def test_theme_switch_performance(self, selenium_driver):
        """Test theme switching speed"""
        selenium_driver.get(f"{BASE_URL}/ui-examples")

        # Test multiple theme switches
        themes = ["valido-dark", "material-light", "dracula", "valido-white"]
        switch_times = []

        for theme in themes:
            start_time = time.time()

            theme_button = selenium_driver.find_element(By.CSS_SELECTOR, f"[data-theme='{theme}']")
            theme_button.click()

            # Wait for theme to apply
            WebDriverWait(selenium_driver, 5).until(
                lambda driver: theme in (driver.find_element(By.TAG_NAME, "body").get_attribute("data-theme") or "")
            )

            end_time = time.time()
            switch_time = (end_time - start_time) * 1000
            switch_times.append(switch_time)

        avg_switch_time = sum(switch_times) / len(switch_times)

        allure.attach(f"""
        Theme Switching Performance:
        - Average switch time: {avg_switch_time:.2f}ms
        - Individual times: {[f'{t:.2f}ms' for t in switch_times]}
        """, "Theme Switch Metrics", allure.attachment_type.TEXT)

        assert avg_switch_time < 200, f"Theme switching too slow: {avg_switch_time}ms"

@allure.feature("Accessibility Testing")
@allure.story("WCAG Compliance")
class TestAccessibility:
    """Test accessibility features"""

    @allure.step("Test basic accessibility features")
    def test_basic_accessibility(self, selenium_driver):
        """Test basic accessibility compliance"""
        selenium_driver.get(f"{BASE_URL}/ui-examples")

        # Check for images without alt text
        images = selenium_driver.find_elements(By.TAG_NAME, "img")
        images_without_alt = [img for img in images if not img.get_attribute("alt")]

        # Check for proper heading hierarchy
        headings = selenium_driver.find_elements(By.CSS_SELECTOR, "h1, h2, h3, h4, h5, h6")
        heading_levels = [int(h.tag_name[1]) for h in headings]

        # Check for ARIA labels
        aria_elements = selenium_driver.find_elements(By.CSS_SELECTOR, "[aria-label], [aria-labelledby]")

        # Check for keyboard focus indicators
        focusable_elements = selenium_driver.find_elements(By.CSS_SELECTOR, "a, button, input, select, textarea, [tabindex]")

        accessibility_score = 0
        total_checks = 4

        if len(images_without_alt) == 0:
            accessibility_score += 1

        if len(headings) > 0 and self._is_heading_hierarchy_valid(heading_levels):
            accessibility_score += 1

        if len(aria_elements) > 0:
            accessibility_score += 1

        if len(focusable_elements) > 0:
            accessibility_score += 1

        score_percentage = (accessibility_score / total_checks) * 100

        allure.attach(f"""
        Accessibility Check Results:
        - Score: {score_percentage:.1f}%
        - Images without alt text: {len(images_without_alt)}
        - Headings found: {len(headings)}
        - ARIA elements: {len(aria_elements)}
        - Focusable elements: {len(focusable_elements)}
        - Heading hierarchy valid: {self._is_heading_hierarchy_valid(heading_levels)}
        """, "Accessibility Report", allure.attachment_type.TEXT)

        assert score_percentage >= 60, f"Accessibility score too low: {score_percentage}%"

    def _is_heading_hierarchy_valid(self, levels):
        """Check if heading hierarchy is valid"""
        if not levels:
            return False

        # Should start with h1
        if levels[0] != 1:
            return False

        # Check for gaps (skipping levels)
        for i in range(1, len(levels)):
            if levels[i] > levels[i-1] + 1:
                return False

        return True

@allure.feature("Error Handling")
@allure.story("Error Scenarios")
class TestErrorHandling:
    """Test error handling and edge cases"""

    @allure.step("Test 404 error handling")
    def test_404_error(self, selenium_driver):
        """Test 404 error page"""
        selenium_driver.get(f"{BASE_URL}/nonexistent-page")

        # Check if error page is displayed
        try:
            error_heading = selenium_driver.find_element(By.CSS_SELECTOR, "h1, .error-title")
            assert error_heading.is_displayed(), "Error page not displayed"
        except NoSuchElementException:
            # Some applications might redirect or show generic error
            body_text = selenium_driver.find_element(By.TAG_NAME, "body").text
            assert "404" in body_text or "not found" in body_text.lower(), "404 error not handled properly"

    @allure.step("Test JavaScript error handling")
    def test_javascript_errors(self, selenium_driver):
        """Test JavaScript error handling"""
        selenium_driver.get(f"{BASE_URL}/ui-examples")

        # Check browser console for JavaScript errors
        logs = selenium_driver.get_log("browser")
        severe_errors = [log for log in logs if log["level"] in ["SEVERE", "ERROR"]]

        # Filter out common non-critical errors
        critical_errors = [
            error for error in severe_errors
            if not any(skip in error["message"] for skip in [
                "favicon", "404", "network", "mixed content", "certificate"
            ])
        ]

        if critical_errors:
            allure.attach(
                json.dumps(critical_errors, indent=2),
                "JavaScript Errors",
                allure.attachment_type.JSON
            )

        # Allow some tolerance for non-critical errors
        assert len(critical_errors) <= 2, f"Too many JavaScript errors: {len(critical_errors)}"

# Configuration for pytest
def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "accessibility: mark test as accessibility test"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as performance test"
    )
    config.addinivalue_line(
        "markers", "visual: mark test as visual regression test"
    )

def pytest_html_report_title(report):
    """Set HTML report title"""
    report.title = "ValidoAI UI/UX Test Report"

if __name__ == "__main__":
    pytest.main([
        __file__,
        "--verbose",
        "--tb=short",
        "--html=tests/reports/comprehensive/ui_test_report.html",
        "--self-contained-html",
        "--capture=no",
        "--allure-dir=tests/reports/allure"
    ])
