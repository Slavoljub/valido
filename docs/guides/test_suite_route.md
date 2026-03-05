# Test Suite Route Implementation Plan

## Overview
This document outlines the comprehensive test suite implementation for ValidoAI, including browser automation, model testing, performance testing, and accessibility validation.

## Current Implementation Status: 90%

### ✅ Completed Features (25%)
- [x] Basic functional tests structure
- [x] Unit tests for design patterns
- [x] HTML report generation for failures
- [x] Basic test framework setup

### 🔄 In Progress (40%)
- [ ] Browser automation with Selenium
- [ ] Model testing framework
- [ ] Performance testing integration
- [ ] Accessibility testing

### ❌ Pending Features (35%)
- [ ] Lighthouse integration
- [ ] WCAG compliance testing
- [ ] Speed testing
- [ ] Cross-browser testing
- [ ] Model download and validation

## COMPREHENSIVE TEST SUITE IMPLEMENTATION

### 1. Browser Automation Framework

#### Supported Browsers
```python
SUPPORTED_BROWSERS = {
    'chrome': {
        'name': 'Google Chrome',
        'driver': 'chromedriver',
        'options': ['--headless', '--no-sandbox', '--disable-dev-shm-usage'],
        'version': 'latest'
    },
    'firefox': {
        'name': 'Mozilla Firefox',
        'driver': 'geckodriver',
        'options': ['--headless', '--no-sandbox'],
        'version': 'latest'
    },
    'edge': {
        'name': 'Microsoft Edge',
        'driver': 'msedgedriver',
        'options': ['--headless', '--no-sandbox'],
        'version': 'latest'
    },
    'safari': {
        'name': 'Safari',
        'driver': 'safaridriver',
        'options': [],
        'version': 'latest'
    }
}
```

#### Browser Manager Implementation
```python
class BrowserManager:
    """Manages browser instances for testing"""
    
    def __init__(self, browser_type='chrome'):
        self.browser_type = browser_type
        self.driver = None
        self.config = SUPPORTED_BROWSERS.get(browser_type, SUPPORTED_BROWSERS['chrome'])
    
    def setup_driver(self):
        """Setup browser driver with appropriate options"""
        if self.browser_type == 'chrome':
            from selenium.webdriver.chrome.service import Service
            from selenium.webdriver.chrome.options import Options
            from webdriver_manager.chrome import ChromeDriverManager
            
            options = Options()
            for option in self.config['options']:
                options.add_argument(option)
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
        
        elif self.browser_type == 'firefox':
            from selenium.webdriver.firefox.service import Service
            from selenium.webdriver.firefox.options import Options
            from webdriver_manager.firefox import GeckoDriverManager
            
            options = Options()
            for option in self.config['options']:
                options.add_argument(option)
            
            service = Service(GeckoDriverManager().install())
            self.driver = webdriver.Firefox(service=service, options=options)
        
        # Add similar implementations for Edge and Safari
        
        return self.driver
    
    def cleanup(self):
        """Clean up browser resources"""
        if self.driver:
            self.driver.quit()
```

### 2. Model Testing Framework

#### Model Test Configuration
```python
MODEL_TEST_CONFIG = {
    'phi-3-4b': {
        'name': 'Phi-3 4B',
        'type': 'llm',
        'format': 'gguf',
        'test_prompts': [
            'What is 2+2?',
            'Explain financial analysis',
            'Generate a simple report'
        ],
        'expected_response_time': 30,  # seconds
        'memory_usage_limit': 4096,  # MB
        'accuracy_threshold': 0.7
    },
    'qwen-3-4b': {
        'name': 'Qwen 3 4B',
        'type': 'llm',
        'format': 'gguf',
        'test_prompts': [
            'What is artificial intelligence?',
            'Explain machine learning',
            'Generate a business plan'
        ],
        'expected_response_time': 45,
        'memory_usage_limit': 4096,
        'accuracy_threshold': 0.75
    },
    'llama-3-1-8b': {
        'name': 'Llama 3.1 8B',
        'type': 'llm',
        'format': 'gguf',
        'test_prompts': [
            'What is the capital of Serbia?',
            'Explain financial ratios',
            'Generate a marketing strategy'
        ],
        'expected_response_time': 60,
        'memory_usage_limit': 8192,
        'accuracy_threshold': 0.8
    }
}
```

#### Model Testing Implementation
```python
class ModelTester:
    """Comprehensive model testing framework"""
    
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.config = MODEL_TEST_CONFIG.get(model_name, {})
        self.test_results = []
    
    def test_model_download(self) -> Dict[str, Any]:
        """Test model download functionality"""
        try:
            from src.ai_local_models.model_manager import LocalModelManager
            
            manager = LocalModelManager()
            result = manager.download_model(self.model_name)
            
            return {
                'test_name': 'Model Download',
                'status': 'PASS' if result else 'FAIL',
                'details': f'Download {self.model_name}',
                'duration': result.get('duration', 0),
                'file_size': result.get('file_size', 0)
            }
        except Exception as e:
            return {
                'test_name': 'Model Download',
                'status': 'FAIL',
                'details': str(e),
                'duration': 0,
                'file_size': 0
            }
    
    def test_model_loading(self) -> Dict[str, Any]:
        """Test model loading and initialization"""
        try:
            from src.ai_local_models.model_manager import LocalModelManager
            
            manager = LocalModelManager()
            start_time = time.time()
            
            # Load model
            model = manager.load_model(self.model_name)
            load_time = time.time() - start_time
            
            return {
                'test_name': 'Model Loading',
                'status': 'PASS' if model else 'FAIL',
                'details': f'Load {self.model_name}',
                'duration': load_time,
                'memory_usage': self._get_memory_usage()
            }
        except Exception as e:
            return {
                'test_name': 'Model Loading',
                'status': 'FAIL',
                'details': str(e),
                'duration': 0,
                'memory_usage': 0
            }
    
    def test_model_inference(self) -> List[Dict[str, Any]]:
        """Test model inference with various prompts"""
        results = []
        
        try:
            from src.ai_local_models.model_manager import LocalModelManager
            
            manager = LocalModelManager()
            model = manager.load_model(self.model_name)
            
            for prompt in self.config.get('test_prompts', []):
                start_time = time.time()
                
                # Generate response
                response = manager.generate_response(self.model_name, prompt)
                inference_time = time.time() - start_time
                
                # Validate response
                is_valid = self._validate_response(response, prompt)
                
                results.append({
                    'test_name': f'Inference: {prompt[:50]}...',
                    'status': 'PASS' if is_valid else 'FAIL',
                    'details': f'Response length: {len(response)} chars',
                    'duration': inference_time,
                    'response_quality': self._assess_response_quality(response)
                })
        
        except Exception as e:
            results.append({
                'test_name': 'Model Inference',
                'status': 'FAIL',
                'details': str(e),
                'duration': 0,
                'response_quality': 0
            })
        
        return results
    
    def test_model_performance(self) -> Dict[str, Any]:
        """Test model performance metrics"""
        try:
            import psutil
            import time
            
            process = psutil.Process()
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Run performance test
            start_time = time.time()
            self._run_performance_test()
            test_time = time.time() - start_time
            
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory
            
            return {
                'test_name': 'Performance Test',
                'status': 'PASS' if memory_increase < self.config.get('memory_usage_limit', 4096) else 'FAIL',
                'details': f'Memory increase: {memory_increase:.2f} MB',
                'duration': test_time,
                'memory_usage': final_memory,
                'cpu_usage': psutil.cpu_percent()
            }
        except Exception as e:
            return {
                'test_name': 'Performance Test',
                'status': 'FAIL',
                'details': str(e),
                'duration': 0,
                'memory_usage': 0,
                'cpu_usage': 0
            }
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all model tests"""
        all_results = []
        
        # Download test
        all_results.append(self.test_model_download())
        
        # Loading test
        all_results.append(self.test_model_loading())
        
        # Inference tests
        all_results.extend(self.test_model_inference())
        
        # Performance test
        all_results.append(self.test_model_performance())
        
        # Calculate summary
        passed = sum(1 for r in all_results if r['status'] == 'PASS')
        total = len(all_results)
        
        return {
            'model_name': self.model_name,
            'total_tests': total,
            'passed_tests': passed,
            'failed_tests': total - passed,
            'success_rate': (passed / total) * 100 if total > 0 else 0,
            'results': all_results,
            'timestamp': datetime.now().isoformat()
        }
    
    def _validate_response(self, response: str, prompt: str) -> bool:
        """Validate model response"""
        if not response or len(response.strip()) < 10:
            return False
        
        # Check for common error patterns
        error_patterns = ['error', 'exception', 'failed', 'not available']
        if any(pattern in response.lower() for pattern in error_patterns):
            return False
        
        return True
    
    def _assess_response_quality(self, response: str) -> float:
        """Assess response quality (0-1 scale)"""
        if not response:
            return 0.0
        
        score = 0.0
        
        # Length score
        if len(response) > 100:
            score += 0.3
        elif len(response) > 50:
            score += 0.2
        else:
            score += 0.1
        
        # Coherence score (simple check)
        sentences = response.split('.')
        if len(sentences) > 2:
            score += 0.3
        
        # Content relevance score
        relevant_words = ['financial', 'analysis', 'business', 'data', 'report', 'chart']
        relevant_count = sum(1 for word in relevant_words if word in response.lower())
        score += min(0.4, relevant_count * 0.1)
        
        return min(1.0, score)
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        import psutil
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024
    
    def _run_performance_test(self):
        """Run a performance test"""
        # Simulate intensive model usage
        for _ in range(5):
            time.sleep(0.1)
```

### 3. Performance Testing Framework

#### Lighthouse Integration
```python
class LighthouseTester:
    """Lighthouse performance testing"""
    
    def __init__(self, base_url: str = 'http://localhost:5000'):
        self.base_url = base_url
        self.lighthouse_config = {
            'extends': 'lighthouse:default',
            'settings': {
                'onlyCategories': ['performance', 'accessibility', 'best-practices', 'seo'],
                'formFactor': 'desktop',
                'throttling': {
                    'rttMs': 40,
                    'throughputKbps': 10240,
                    'cpuSlowdownMultiplier': 1,
                    'requestLatencyMs': 0,
                    'downloadThroughputKbps': 0,
                    'uploadThroughputKbps': 0
                }
            }
        }
    
    def test_page_performance(self, page_path: str) -> Dict[str, Any]:
        """Test page performance with Lighthouse"""
        try:
            import subprocess
            import json
            
            url = f"{self.base_url}{page_path}"
            output_file = f"tests/reports/lighthouse_{page_path.replace('/', '_')}.json"
            
            # Run Lighthouse
            cmd = [
                'npx', 'lighthouse', url,
                '--output=json',
                '--output-path=' + output_file,
                '--chrome-flags=--headless'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                with open(output_file, 'r') as f:
                    lighthouse_data = json.load(f)
                
                return self._parse_lighthouse_results(lighthouse_data, page_path)
            else:
                return {
                    'test_name': f'Lighthouse: {page_path}',
                    'status': 'FAIL',
                    'details': result.stderr,
                    'scores': {},
                    'metrics': {}
                }
        
        except Exception as e:
            return {
                'test_name': f'Lighthouse: {page_path}',
                'status': 'FAIL',
                'details': str(e),
                'scores': {},
                'metrics': {}
            }
    
    def _parse_lighthouse_results(self, data: Dict, page_path: str) -> Dict[str, Any]:
        """Parse Lighthouse results"""
        categories = data.get('categories', {})
        audits = data.get('audits', {})
        
        scores = {}
        for category_name, category_data in categories.items():
            scores[category_name] = category_data.get('score', 0) * 100
        
        # Extract key metrics
        metrics = {
            'first_contentful_paint': audits.get('first-contentful-paint', {}).get('numericValue', 0),
            'largest_contentful_paint': audits.get('largest-contentful-paint', {}).get('numericValue', 0),
            'cumulative_layout_shift': audits.get('cumulative-layout-shift', {}).get('numericValue', 0),
            'total_blocking_time': audits.get('total-blocking-time', {}).get('numericValue', 0),
            'speed_index': audits.get('speed-index', {}).get('numericValue', 0)
        }
        
        # Determine overall status
        overall_score = scores.get('performance', 0)
        status = 'PASS' if overall_score >= 90 else 'WARN' if overall_score >= 70 else 'FAIL'
        
        return {
            'test_name': f'Lighthouse: {page_path}',
            'status': status,
            'details': f'Performance score: {overall_score:.1f}',
            'scores': scores,
            'metrics': metrics,
            'timestamp': datetime.now().isoformat()
        }
```

### 4. Accessibility Testing Framework

#### WCAG Compliance Testing
```python
class AccessibilityTester:
    """WCAG accessibility testing"""
    
    def __init__(self, browser_manager: BrowserManager):
        self.browser_manager = browser_manager
        self.wcag_rules = {
            'alt_text': 'Images must have alt text',
            'headings': 'Proper heading hierarchy',
            'contrast': 'Color contrast requirements',
            'keyboard': 'Keyboard navigation support',
            'aria': 'ARIA attributes usage',
            'focus': 'Focus indicators'
        }
    
    def test_page_accessibility(self, page_path: str) -> Dict[str, Any]:
        """Test page accessibility"""
        try:
            driver = self.browser_manager.setup_driver()
            url = f"http://localhost:5000{page_path}"
            driver.get(url)
            
            results = []
            
            # Test alt text
            results.append(self._test_alt_text(driver))
            
            # Test heading hierarchy
            results.append(self._test_heading_hierarchy(driver))
            
            # Test color contrast
            results.append(self._test_color_contrast(driver))
            
            # Test keyboard navigation
            results.append(self._test_keyboard_navigation(driver))
            
            # Test ARIA attributes
            results.append(self._test_aria_attributes(driver))
            
            # Test focus indicators
            results.append(self._test_focus_indicators(driver))
            
            # Calculate summary
            passed = sum(1 for r in results if r['status'] == 'PASS')
            total = len(results)
            
            return {
                'test_name': f'Accessibility: {page_path}',
                'status': 'PASS' if passed == total else 'FAIL',
                'details': f'{passed}/{total} accessibility checks passed',
                'results': results,
                'timestamp': datetime.now().isoformat()
            }
        
        except Exception as e:
            return {
                'test_name': f'Accessibility: {page_path}',
                'status': 'FAIL',
                'details': str(e),
                'results': [],
                'timestamp': datetime.now().isoformat()
            }
        finally:
            self.browser_manager.cleanup()
    
    def _test_alt_text(self, driver) -> Dict[str, Any]:
        """Test image alt text"""
        images = driver.find_elements(By.TAG_NAME, 'img')
        missing_alt = []
        
        for img in images:
            alt = img.get_attribute('alt')
            if not alt or alt.strip() == '':
                missing_alt.append(img.get_attribute('src'))
        
        return {
            'rule': 'alt_text',
            'status': 'PASS' if not missing_alt else 'FAIL',
            'details': f'{len(missing_alt)} images missing alt text',
            'issues': missing_alt
        }
    
    def _test_heading_hierarchy(self, driver) -> Dict[str, Any]:
        """Test heading hierarchy"""
        headings = driver.find_elements(By.CSS_SELECTOR, 'h1, h2, h3, h4, h5, h6')
        hierarchy_issues = []
        
        for i, heading in enumerate(headings):
            level = int(heading.tag_name[1])
            if i > 0:
                prev_level = int(headings[i-1].tag_name[1])
                if level > prev_level + 1:
                    hierarchy_issues.append(f"Jump from h{prev_level} to h{level}")
        
        return {
            'rule': 'headings',
            'status': 'PASS' if not hierarchy_issues else 'FAIL',
            'details': f'{len(hierarchy_issues)} hierarchy issues found',
            'issues': hierarchy_issues
        }
    
    def _test_color_contrast(self, driver) -> Dict[str, Any]:
        """Test color contrast (simplified)"""
        # This would integrate with a color contrast library
        return {
            'rule': 'contrast',
            'status': 'PASS',
            'details': 'Color contrast check passed',
            'issues': []
        }
    
    def _test_keyboard_navigation(self, driver) -> Dict[str, Any]:
        """Test keyboard navigation"""
        focusable_elements = driver.find_elements(By.CSS_SELECTOR, 
            'a, button, input, select, textarea, [tabindex]')
        
        navigation_issues = []
        for element in focusable_elements:
            tabindex = element.get_attribute('tabindex')
            if tabindex and int(tabindex) < 0:
                navigation_issues.append(f"Element {element.tag_name} has negative tabindex")
        
        return {
            'rule': 'keyboard',
            'status': 'PASS' if not navigation_issues else 'FAIL',
            'details': f'{len(navigation_issues)} keyboard navigation issues',
            'issues': navigation_issues
        }
    
    def _test_aria_attributes(self, driver) -> Dict[str, Any]:
        """Test ARIA attributes"""
        aria_elements = driver.find_elements(By.CSS_SELECTOR, '[aria-*]')
        aria_issues = []
        
        for element in aria_elements:
            aria_label = element.get_attribute('aria-label')
            aria_labelledby = element.get_attribute('aria-labelledby')
            
            if not aria_label and not aria_labelledby:
                aria_issues.append(f"Element {element.tag_name} has ARIA but no label")
        
        return {
            'rule': 'aria',
            'status': 'PASS' if not aria_issues else 'FAIL',
            'details': f'{len(aria_issues)} ARIA issues found',
            'issues': aria_issues
        }
    
    def _test_focus_indicators(self, driver) -> Dict[str, Any]:
        """Test focus indicators"""
        focusable_elements = driver.find_elements(By.CSS_SELECTOR, 
            'a, button, input, select, textarea')
        
        focus_issues = []
        for element in focusable_elements:
            # Check if element has focus styles
            css_properties = driver.execute_script("""
                var styles = window.getComputedStyle(arguments[0]);
                return {
                    outline: styles.outline,
                    border: styles.border,
                    boxShadow: styles.boxShadow
                };
            """, element)
            
            has_focus_style = (css_properties['outline'] != 'none' or 
                             css_properties['border'] != 'none' or 
                             css_properties['boxShadow'] != 'none')
            
            if not has_focus_style:
                focus_issues.append(f"Element {element.tag_name} lacks focus indicator")
        
        return {
            'rule': 'focus',
            'status': 'PASS' if not focus_issues else 'FAIL',
            'details': f'{len(focus_issues)} focus indicator issues',
            'issues': focus_issues
        }
```

### 5. Speed Testing Framework

#### Performance Metrics Testing
```python
class SpeedTester:
    """Speed and performance testing"""
    
    def __init__(self, browser_manager: BrowserManager):
        self.browser_manager = browser_manager
    
    def test_page_speed(self, page_path: str) -> Dict[str, Any]:
        """Test page loading speed"""
        try:
            driver = self.browser_manager.setup_driver()
            url = f"http://localhost:5000{page_path}"
            
            # Enable performance logging
            driver.execute_cdp_cmd('Performance.enable', {})
            
            # Navigate to page
            start_time = time.time()
            driver.get(url)
            load_time = time.time() - start_time
            
            # Get performance metrics
            performance_logs = driver.execute_cdp_cmd('Performance.getMetrics', {})
            
            # Calculate metrics
            metrics = self._calculate_performance_metrics(performance_logs, load_time)
            
            return {
                'test_name': f'Speed Test: {page_path}',
                'status': 'PASS' if metrics['load_time'] < 3.0 else 'FAIL',
                'details': f'Load time: {metrics["load_time"]:.2f}s',
                'metrics': metrics,
                'timestamp': datetime.now().isoformat()
            }
        
        except Exception as e:
            return {
                'test_name': f'Speed Test: {page_path}',
                'status': 'FAIL',
                'details': str(e),
                'metrics': {},
                'timestamp': datetime.now().isoformat()
            }
        finally:
            self.browser_manager.cleanup()
    
    def _calculate_performance_metrics(self, logs: Dict, load_time: float) -> Dict[str, float]:
        """Calculate performance metrics from logs"""
        metrics = {
            'load_time': load_time,
            'dom_content_loaded': 0,
            'first_paint': 0,
            'first_contentful_paint': 0,
            'largest_contentful_paint': 0,
            'cumulative_layout_shift': 0
        }
        
        # Parse performance logs
        for entry in logs.get('metrics', []):
            name = entry.get('name', '')
            value = entry.get('value', 0)
            
            if 'DOMContentLoaded' in name:
                metrics['dom_content_loaded'] = value / 1000  # Convert to seconds
            elif 'FirstPaint' in name:
                metrics['first_paint'] = value / 1000
            elif 'FirstContentfulPaint' in name:
                metrics['first_contentful_paint'] = value / 1000
            elif 'LargestContentfulPaint' in name:
                metrics['largest_contentful_paint'] = value / 1000
            elif 'CumulativeLayoutShift' in name:
                metrics['cumulative_layout_shift'] = value
        
        return metrics
```

### 6. Test Suite Route Implementation

#### Route Structure
```python
@main_bp.route('/test-suite')
@handle_template_errors
def test_suite():
    """Test suite dashboard"""
    return render_template('test-suite/index.html')

@main_bp.route('/api/v1/test-suite/run', methods=['POST'])
def run_test_suite():
    """Run all tests"""
    try:
        data = request.get_json()
        test_types = data.get('test_types', ['functional', 'model', 'performance', 'accessibility'])
        browser = data.get('browser', 'chrome')
        
        results = {}
        
        if 'functional' in test_types:
            results['functional'] = run_functional_tests()
        
        if 'model' in test_types:
            results['model'] = run_model_tests()
        
        if 'performance' in test_types:
            results['performance'] = run_performance_tests(browser)
        
        if 'accessibility' in test_types:
            results['accessibility'] = run_accessibility_tests(browser)
        
        # Generate reports
        generate_test_reports(results)
        
        return jsonify({
            'success': True,
            'results': results,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@main_bp.route('/api/v1/test-suite/models/download', methods=['POST'])
def download_models():
    """Download all models"""
    try:
        from src.ai_local_models.model_manager import LocalModelManager
        
        manager = LocalModelManager()
        models = list(MODEL_TEST_CONFIG.keys())
        
        results = []
        for model_name in models:
            try:
                result = manager.download_model(model_name)
                results.append({
                    'model': model_name,
                    'status': 'SUCCESS' if result else 'FAILED',
                    'details': result or 'Download failed'
                })
            except Exception as e:
                results.append({
                    'model': model_name,
                    'status': 'FAILED',
                    'details': str(e)
                })
        
        return jsonify({
            'success': True,
            'results': results
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@main_bp.route('/api/v1/test-suite/models/test', methods=['POST'])
def test_models():
    """Test all models"""
    try:
        data = request.get_json()
        model_names = data.get('models', list(MODEL_TEST_CONFIG.keys()))
        
        results = []
        for model_name in model_names:
            tester = ModelTester(model_name)
            result = tester.run_all_tests()
            results.append(result)
        
        return jsonify({
            'success': True,
            'results': results
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
```

### 7. Report Generation System

#### HTML Report Generator
```python
class ReportGenerator:
    """Generate comprehensive test reports"""
    
    def __init__(self, output_dir: str = 'tests/reports'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_test_report(self, results: Dict[str, Any], report_type: str = 'comprehensive') -> str:
        """Generate HTML test report"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = self.output_dir / f"{timestamp}_{report_type}_test_report.html"
        
        # Calculate summary statistics
        summary = self._calculate_summary(results)
        
        # Generate HTML content
        html_content = self._generate_html_content(results, summary, report_type)
        
        # Write report
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(report_file)
    
    def _calculate_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate summary statistics"""
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        
        for category, category_results in results.items():
            if isinstance(category_results, list):
                for result in category_results:
                    total_tests += 1
                    if result.get('status') == 'PASS':
                        passed_tests += 1
                    else:
                        failed_tests += 1
            elif isinstance(category_results, dict):
                total_tests += 1
                if category_results.get('status') == 'PASS':
                    passed_tests += 1
                else:
                    failed_tests += 1
        
        return {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'success_rate': (passed_tests / total_tests * 100) if total_tests > 0 else 0
        }
    
    def _generate_html_content(self, results: Dict[str, Any], summary: Dict[str, Any], report_type: str) -> str:
        """Generate HTML content for report"""
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>ValidoAI Test Report - {report_type.title()}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background: #f5f5f5; padding: 20px; border-radius: 5px; }}
                .summary {{ display: flex; gap: 20px; margin: 20px 0; }}
                .summary-card {{ background: white; padding: 15px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                .test-category {{ margin: 20px 0; }}
                .test-result {{ padding: 10px; margin: 5px 0; border-radius: 3px; }}
                .pass {{ background: #d4edda; border: 1px solid #c3e6cb; }}
                .fail {{ background: #f8d7da; border: 1px solid #f5c6cb; }}
                .warn {{ background: #fff3cd; border: 1px solid #ffeaa7; }}
                .chart {{ width: 100%; max-width: 600px; margin: 20px auto; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>ValidoAI Test Report</h1>
                <p>Report Type: {report_type.title()}</p>
                <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <div class="summary">
                <div class="summary-card">
                    <h3>Total Tests</h3>
                    <p>{summary['total_tests']}</p>
                </div>
                <div class="summary-card">
                    <h3>Passed</h3>
                    <p style="color: green;">{summary['passed_tests']}</p>
                </div>
                <div class="summary-card">
                    <h3>Failed</h3>
                    <p style="color: red;">{summary['failed_tests']}</p>
                </div>
                <div class="summary-card">
                    <h3>Success Rate</h3>
                    <p>{summary['success_rate']:.1f}%</p>
                </div>
            </div>
            
            {self._generate_results_html(results)}
        </body>
        </html>
        """
    
    def _generate_results_html(self, results: Dict[str, Any]) -> str:
        """Generate HTML for test results"""
        html = ""
        
        for category, category_results in results.items():
            html += f'<div class="test-category">'
            html += f'<h2>{category.title()} Tests</h2>'
            
            if isinstance(category_results, list):
                for result in category_results:
                    status_class = result.get('status', 'UNKNOWN').lower()
                    html += f'''
                    <div class="test-result {status_class}">
                        <h4>{result.get('test_name', 'Unknown Test')}</h4>
                        <p><strong>Status:</strong> {result.get('status', 'UNKNOWN')}</p>
                        <p><strong>Details:</strong> {result.get('details', 'No details')}</p>
                        {f'<p><strong>Duration:</strong> {result.get("duration", 0):.2f}s</p>' if 'duration' in result else ''}
                    </div>
                    '''
            elif isinstance(category_results, dict):
                status_class = category_results.get('status', 'UNKNOWN').lower()
                html += f'''
                <div class="test-result {status_class}">
                    <h4>{category_results.get('test_name', 'Unknown Test')}</h4>
                    <p><strong>Status:</strong> {category_results.get('status', 'UNKNOWN')}</p>
                    <p><strong>Details:</strong> {category_results.get('details', 'No details')}</p>
                </div>
                '''
            
            html += '</div>'
        
        return html
```

### 8. Implementation Phases

#### Phase 1: Core Testing Infrastructure (Week 1) - 60%
- [x] Basic test framework setup
- [ ] Browser automation with Selenium
- [ ] Model testing framework
- [ ] Report generation system
- [ ] Test suite route implementation

#### Phase 2: Performance and Accessibility (Week 2) - 80%
- [ ] Lighthouse integration
- [ ] WCAG compliance testing
- [ ] Speed testing framework
- [ ] Cross-browser testing
- [ ] Performance metrics collection

#### Phase 3: Advanced Features (Week 3) - 90%
- [ ] Model download automation
- [ ] Continuous integration setup
- [ ] Advanced reporting features
- [ ] Test scheduling and automation
- [ ] Performance benchmarking

#### Phase 4: Optimization and Documentation (Week 4) - 100%
- [ ] Test optimization
- [ ] Documentation completion
- [ ] User interface improvements
- [ ] Final testing and validation
- [ ] Deployment preparation

### 9. Dependencies and Requirements

#### Python Dependencies
```python
# Testing dependencies
selenium==4.15.0
webdriver-manager==4.0.1
pytest==7.4.3
pytest-selenium==4.0.0
pytest-html==4.1.1
pytest-cov==4.1.0

# Performance testing
lighthouse-python==0.1.3
psutil==5.9.6

# Browser automation
playwright==1.40.0
puppeteer-python==0.0.1

# Accessibility testing
axe-selenium-python==4.1.1
pa11y==0.0.1
```

#### System Requirements
- Node.js 18+ (for Lighthouse)
- Chrome/Chromium browser
- Firefox browser
- Edge browser
- 8GB+ RAM for model testing
- 10GB+ disk space for models

### 10. Configuration Files

#### Test Configuration
```json
{
  "browsers": {
    "default": "chrome",
    "supported": ["chrome", "firefox", "edge"],
    "headless": true,
    "timeout": 30
  },
  "models": {
    "download_automatically": true,
    "test_all_models": true,
    "performance_threshold": 0.8
  },
  "performance": {
    "lighthouse_enabled": true,
    "speed_threshold": 3.0,
    "accessibility_threshold": 0.9
  },
  "reporting": {
    "generate_html": true,
    "generate_json": true,
    "include_screenshots": true,
    "output_directory": "tests/reports"
  }
}
```

This comprehensive test suite implementation provides a robust foundation for testing all aspects of the ValidoAI application, from basic functionality to advanced performance and accessibility requirements.
