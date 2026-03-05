"""
Browser Manager for Selenium Testing
Supports Chrome, Firefox, Edge, and Safari browsers
"""

import os
import time
import logging
from typing import Optional, Dict, Any
from pathlib import Path

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service as ChromeService
    from selenium.webdriver.firefox.service import Service as FirefoxService
    from selenium.webdriver.edge.service import Service as EdgeService
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.firefox.options import Options as FirefoxOptions
    from selenium.webdriver.edge.options import Options as EdgeOptions
    from webdriver_manager.chrome import ChromeDriverManager
    from webdriver_manager.firefox import GeckoDriverManager
    from webdriver_manager.microsoft import EdgeChromiumDriverManager
except ImportError:
    print("Selenium not installed. Install with: pip install selenium webdriver-manager")

logger = logging.getLogger(__name__)

# Supported browsers configuration
SUPPORTED_BROWSERS = {
    'chrome': {
        'name': 'Google Chrome',
        'driver': 'chromedriver',
        'options': [
            '--headless',
            '--no-sandbox',
            '--disable-dev-shm-usage',
            '--disable-gpu',
            '--window-size=1920,1080',
            '--disable-extensions',
            '--disable-plugins',
            '--disable-images'
        ],
        'version': 'latest'
    },
    'firefox': {
        'name': 'Mozilla Firefox',
        'driver': 'geckodriver',
        'options': [
            '--headless',
            '--no-sandbox',
            '--width=1920',
            '--height=1080'
        ],
        'version': 'latest'
    },
    'edge': {
        'name': 'Microsoft Edge',
        'driver': 'msedgedriver',
        'options': [
            '--headless',
            '--no-sandbox',
            '--disable-dev-shm-usage',
            '--disable-gpu',
            '--window-size=1920,1080'
        ],
        'version': 'latest'
    }
}


class BrowserManager:
    """Manages browser instances for testing"""
    
    def __init__(self, browser_type: str = 'chrome', headless: bool = True):
        self.browser_type = browser_type.lower()
        self.headless = headless
        self.driver = None
        self.config = SUPPORTED_BROWSERS.get(self.browser_type, SUPPORTED_BROWSERS['chrome'])
        
        if self.browser_type not in SUPPORTED_BROWSERS:
            logger.warning(f"Unsupported browser: {browser_type}. Using Chrome instead.")
            self.browser_type = 'chrome'
            self.config = SUPPORTED_BROWSERS['chrome']
    
    def setup_driver(self) -> Optional[webdriver.Remote]:
        """Setup browser driver with appropriate options"""
        try:
            if self.browser_type == 'chrome':
                return self._setup_chrome_driver()
            elif self.browser_type == 'firefox':
                return self._setup_firefox_driver()
            elif self.browser_type == 'edge':
                return self._setup_edge_driver()
            else:
                logger.error(f"Unsupported browser type: {self.browser_type}")
                return None
        
        except Exception as e:
            logger.error(f"Failed to setup {self.browser_type} driver: {e}")
            return None
    
    def _setup_chrome_driver(self) -> webdriver.Chrome:
        """Setup Chrome driver"""
        options = ChromeOptions()
        
        # Add browser options
        for option in self.config['options']:
            if not self.headless and '--headless' in option:
                continue
            options.add_argument(option)
        
        # Additional Chrome preferences
        prefs = {
            'profile.default_content_setting_values': {
                'images': 2,  # Disable images
                'plugins': 2,  # Disable plugins
                'popups': 2,   # Disable popups
                'geolocation': 2,  # Disable geolocation
                'notifications': 2,  # Disable notifications
                'media_stream': 2,  # Disable media stream
            }
        }
        options.add_experimental_option('prefs', prefs)
        
        # Setup service
        service = ChromeService(ChromeDriverManager().install())
        
        # Create driver
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.set_page_load_timeout(30)
        self.driver.implicitly_wait(10)
        
        return self.driver
    
    def _setup_firefox_driver(self) -> webdriver.Firefox:
        """Setup Firefox driver"""
        options = FirefoxOptions()
        
        # Add browser options
        for option in self.config['options']:
            if not self.headless and '--headless' in option:
                continue
            options.add_argument(option)
        
        # Firefox preferences
        options.set_preference('dom.webnotifications.enabled', False)
        options.set_preference('media.navigator.enabled', False)
        options.set_preference('media.navigator.permission.disabled', True)
        
        # Setup service
        service = FirefoxService(GeckoDriverManager().install())
        
        # Create driver
        self.driver = webdriver.Firefox(service=service, options=options)
        self.driver.set_page_load_timeout(30)
        self.driver.implicitly_wait(10)
        
        return self.driver
    
    def _setup_edge_driver(self) -> webdriver.Edge:
        """Setup Edge driver"""
        options = EdgeOptions()
        
        # Add browser options
        for option in self.config['options']:
            if not self.headless and '--headless' in option:
                continue
            options.add_argument(option)
        
        # Setup service
        service = EdgeService(EdgeChromiumDriverManager().install())
        
        # Create driver
        self.driver = webdriver.Edge(service=service, options=options)
        self.driver.set_page_load_timeout(30)
        self.driver.implicitly_wait(10)
        
        return self.driver
    
    def get_driver(self) -> Optional[webdriver.Remote]:
        """Get the current driver instance"""
        if not self.driver:
            self.driver = self.setup_driver()
        return self.driver
    
    def navigate_to(self, url: str) -> bool:
        """Navigate to a URL"""
        try:
            driver = self.get_driver()
            if driver:
                driver.get(url)
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to navigate to {url}: {e}")
            return False
    
    def take_screenshot(self, filename: str = None) -> Optional[str]:
        """Take a screenshot"""
        try:
            driver = self.get_driver()
            if not driver:
                return None
            
            if not filename:
                timestamp = int(time.time())
                filename = f"screenshot_{timestamp}.png"
            
            # Ensure screenshots directory exists
            screenshots_dir = Path("tests/reports/screenshots")
            screenshots_dir.mkdir(parents=True, exist_ok=True)
            
            filepath = screenshots_dir / filename
            driver.save_screenshot(str(filepath))
            
            return str(filepath)
        
        except Exception as e:
            logger.error(f"Failed to take screenshot: {e}")
            return None
    
    def get_page_source(self) -> Optional[str]:
        """Get page source"""
        try:
            driver = self.get_driver()
            return driver.page_source if driver else None
        except Exception as e:
            logger.error(f"Failed to get page source: {e}")
            return None
    
    def get_page_title(self) -> Optional[str]:
        """Get page title"""
        try:
            driver = self.get_driver()
            return driver.title if driver else None
        except Exception as e:
            logger.error(f"Failed to get page title: {e}")
            return None
    
    def wait_for_element(self, by, value, timeout: int = 10):
        """Wait for element to be present"""
        try:
            driver = self.get_driver()
            if driver:
                from selenium.webdriver.support.ui import WebDriverWait
                from selenium.webdriver.support import expected_conditions as EC
                
                wait = WebDriverWait(driver, timeout)
                return wait.until(EC.presence_of_element_located((by, value)))
            return None
        except Exception as e:
            logger.error(f"Failed to wait for element {value}: {e}")
            return None
    
    def execute_script(self, script: str, *args):
        """Execute JavaScript"""
        try:
            driver = self.get_driver()
            return driver.execute_script(script, *args) if driver else None
        except Exception as e:
            logger.error(f"Failed to execute script: {e}")
            return None
    
    def get_browser_info(self) -> Dict[str, Any]:
        """Get browser information"""
        try:
            driver = self.get_driver()
            if not driver:
                return {}
            
            return {
                'browser_name': driver.name,
                'browser_version': driver.capabilities.get('browserVersion', 'Unknown'),
                'driver_version': driver.capabilities.get('chrome', {}).get('chromedriverVersion', 'Unknown'),
                'platform': driver.capabilities.get('platformName', 'Unknown'),
                'window_size': driver.get_window_size(),
                'current_url': driver.current_url
            }
        except Exception as e:
            logger.error(f"Failed to get browser info: {e}")
            return {}
    
    def cleanup(self):
        """Clean up browser resources"""
        try:
            if self.driver:
                self.driver.quit()
                self.driver = None
                logger.info(f"Cleaned up {self.browser_type} driver")
        except Exception as e:
            logger.error(f"Failed to cleanup driver: {e}")
    
    def __enter__(self):
        """Context manager entry"""
        self.setup_driver()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.cleanup()


class BrowserPool:
    """Manages multiple browser instances"""
    
    def __init__(self, max_browsers: int = 3):
        self.max_browsers = max_browsers
        self.browsers = {}
        self.available_browsers = []
    
    def get_browser(self, browser_type: str = 'chrome') -> Optional[BrowserManager]:
        """Get an available browser instance"""
        if browser_type in self.available_browsers:
            self.available_browsers.remove(browser_type)
            return self.browsers[browser_type]
        
        if len(self.browsers) < self.max_browsers:
            browser = BrowserManager(browser_type)
            self.browsers[browser_type] = browser
            return browser
        
        return None
    
    def release_browser(self, browser_type: str):
        """Release a browser back to the pool"""
        if browser_type in self.browsers and browser_type not in self.available_browsers:
            self.available_browsers.append(browser_type)
    
    def cleanup_all(self):
        """Clean up all browser instances"""
        for browser in self.browsers.values():
            browser.cleanup()
        self.browsers.clear()
        self.available_browsers.clear()


# Global browser pool instance
browser_pool = BrowserPool()


def get_browser(browser_type: str = 'chrome') -> BrowserManager:
    """Get a browser instance from the pool"""
    return browser_pool.get_browser(browser_type)


def release_browser(browser_type: str):
    """Release a browser back to the pool"""
    browser_pool.release_browser(browser_type)


def cleanup_browsers():
    """Clean up all browser instances"""
    browser_pool.cleanup_all()
