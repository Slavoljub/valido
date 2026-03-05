#!/usr/bin/env python3
"""
ValidoAI - Critical CSS Generator with Tailwind CSS
===============================================
Automatic critical CSS extraction and inlining system

This module provides comprehensive critical CSS generation with:
- Tailwind CSS optimization
- Critical CSS extraction
- Automatic inlining
- Performance monitoring
- Cache management
"""

import os
import re
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import threading
from concurrent.futures import ThreadPoolExecutor
import logging

# ============================================================================
# CONFIGURATION
# ============================================================================

@dataclass
class CriticalCSSConfig:
    """Configuration for critical CSS generation"""
    tailwind_config_path: str = "tailwind.config.js"
    content_paths: List[str] = None
    output_dir: str = "static/css/critical"
    cache_dir: str = "cache/critical_css"
    max_workers: int = 4
    timeout: int = 30
    enable_compression: bool = True
    enable_cache: bool = True
    cache_ttl: int = 3600  # 1 hour

    def __post_init__(self):
        if self.content_paths is None:
            self.content_paths = [
                "templates/**/*.html",
                "static/js/**/*.js",
                "src/**/*.py"
            ]

# ============================================================================
# CRITICAL CSS EXTRACTOR
# ============================================================================

class CriticalCSSExtractor:
    """Extracts critical CSS from templates and routes"""

    def __init__(self, config: CriticalCSSConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()

        # Create necessary directories
        Path(config.output_dir).mkdir(parents=True, exist_ok=True)
        Path(config.cache_dir).mkdir(parents=True, exist_ok=True)

        # Load Tailwind CSS utilities
        self.tailwind_utils = self._load_tailwind_utils()

    def _load_tailwind_utils(self) -> Dict[str, str]:
        """Load Tailwind CSS utility classes"""
        # Common Tailwind utilities used in web applications
        return {
            # Layout
            'container': '.container { width: 100%; max-width: 100%; margin: 0 auto; padding: 0 1rem; }',
            'flex': '.flex { display: flex; }',
            'grid': '.grid { display: grid; }',
            'hidden': '.hidden { display: none; }',
            'block': '.block { display: block; }',

            # Spacing
            'm-0': '.m-0 { margin: 0; }',
            'p-0': '.p-0 { padding: 0; }',
            'mx-auto': '.mx-auto { margin-left: auto; margin-right: auto; }',

            # Colors
            'bg-white': '.bg-white { background-color: #ffffff; }',
            'bg-gray-100': '.bg-gray-100 { background-color: #f3f4f6; }',
            'text-gray-900': '.text-gray-900 { color: #111827; }',
            'text-blue-600': '.text-blue-600 { color: #2563eb; }',

            # Typography
            'text-sm': '.text-sm { font-size: 0.875rem; line-height: 1.25rem; }',
            'text-base': '.text-base { font-size: 1rem; line-height: 1.5rem; }',
            'text-lg': '.text-lg { font-size: 1.125rem; line-height: 1.75rem; }',
            'font-bold': '.font-bold { font-weight: 700; }',
            'font-semibold': '.font-semibold { font-weight: 600; }',

            # Responsive utilities
            'sm:block': '@media (min-width: 640px) { .sm\\:block { display: block; } }',
            'md:flex': '@media (min-width: 768px) { .md\\:flex { display: flex; } }',
            'lg:grid': '@media (min-width: 1024px) { .lg\\:grid { display: grid; } }',
        }

    def extract_from_template(self, template_path: str) -> Set[str]:
        """Extract Tailwind classes from HTML template"""
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Regex patterns for Tailwind classes
            patterns = [
                r'class=["\'][^"\']*?([\\w\\-:]+)[^"\']*?["\']',  # class="..."
                r'className=["\'][^"\']*?([\\w\\-:]+)[^"\']*?["\']',  # className="..."
                r'@apply\\s+([^;]+)',  # @apply directive
            ]

            classes = set()
            for pattern in patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    # Split multiple classes and clean them
                    for cls in match.split():
                        cls = cls.strip()
                        if cls and not cls.startswith('{{') and not cls.startswith('{%'):
                            classes.add(cls)

            return classes

        except Exception as e:
            self.logger.error(f"Error extracting from {template_path}: {e}")
            return set()

    def extract_from_route(self, route_name: str) -> Set[str]:
        """Extract classes from route-specific context"""
        # This would analyze the specific route's template usage
        # For now, return common classes based on route type
        route_classes = {
            'dashboard': {'bg-white', 'text-gray-900', 'p-4', 'm-2', 'flex', 'grid'},
            'auth': {'bg-white', 'text-gray-900', 'p-6', 'm-auto', 'flex', 'block'},
            'settings': {'bg-white', 'text-gray-900', 'p-4', 'm-2', 'flex', 'grid'},
            'default': {'container', 'mx-auto', 'p-4', 'text-base', 'bg-white'}
        }

        return route_classes.get(route_name.split('.')[0], route_classes['default'])

    def generate_critical_css(self, route_name: str, template_classes: Set[str] = None) -> str:
        """Generate critical CSS for a specific route"""

        if template_classes is None:
            template_classes = set()

        # Combine template classes with route-specific classes
        route_classes = self.extract_from_route(route_name)
        all_classes = template_classes.union(route_classes)

        # Generate CSS from Tailwind utilities
        critical_css = []
        responsive_rules = []

        for class_name in all_classes:
            if class_name in self.tailwind_utils:
                css_rule = self.tailwind_utils[class_name]

                if css_rule.startswith('@media'):
                    responsive_rules.append(css_rule)
                else:
                    critical_css.append(css_rule)

        # Combine regular and responsive rules
        final_css = '\\n'.join(critical_css + responsive_rules)

        # Add basic reset styles
        reset_css = '''
        * { box-sizing: border-box; }
        body { margin: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
        [hidden] { display: none !important; }
        '''

        return reset_css + final_css

    def extract_all_routes(self) -> List[str]:
        """Extract all routes from the application"""
        # This would analyze the Flask routes
        # For now, return common routes
        return [
            'index', 'dashboard', 'auth.login', 'auth.register',
            'settings', 'content.management', 'ai.sentiment-analysis',
            'scraping', 'recycle-bin', 'ui-examples'
        ]

    def generate_all_critical_css(self) -> Dict[str, str]:
        """Generate critical CSS for all routes"""
        routes = self.extract_all_routes()
        critical_css_files = {}

        with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            futures = {}

            for route in routes:
                future = executor.submit(self.generate_critical_css, route)
                futures[future] = route

            for future in futures:
                route = futures[future]
                try:
                    css_content = future.result(timeout=self.config.timeout)
                    critical_css_files[route] = css_content
                except Exception as e:
                    self.logger.error(f"Error generating CSS for {route}: {e}")
                    critical_css_files[route] = ""

        return critical_css_files

    def save_critical_css(self, route_name: str, css_content: str):
        """Save critical CSS to file"""
        filename = f"{route_name.replace('.', '_')}.css"
        filepath = Path(self.config.output_dir) / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(css_content)

        self.logger.info(f"Saved critical CSS for {route_name} to {filepath}")

    def minify_css(self, css_content: str) -> str:
        """Minify CSS content"""
        if not self.config.enable_compression:
            return css_content

        # Simple CSS minification
        # Remove comments
        css_content = re.sub(r'/\*[^*]*\*\+\([^/*][^*]*\*\+\)*/', '', css_content)

        # Remove whitespace
        css_content = re.sub(r'\\s+', ' ', css_content)
        css_content = re.sub(r';\\s*}', '}', css_content)
        css_content = re.sub(r',\\s*', ',', css_content)
        css_content = re.sub(r'{\\s*', '{', css_content)
        css_content = re.sub(r'\\s*}', '}', css_content)

        return css_content.strip()

# ============================================================================
# CRITICAL CSS MANAGER
# ============================================================================

class CriticalCSSManager:
    """Manages critical CSS generation and caching"""

    def __init__(self, config: CriticalCSSConfig = None):
        self.config = config or CriticalCSSConfig()
        self.extractor = CriticalCSSExtractor(self.config)
        self.logger = logging.getLogger(__name__)

    def generate_for_route(self, route_name: str, force: bool = False) -> str:
        """Generate critical CSS for a specific route"""
        cache_key = f"critical_css_{route_name}"
        cache_file = Path(self.config.cache_dir) / f"{cache_key}.json"

        # Check cache first
        if not force and self.config.enable_cache and cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    cached_data = json.load(f)

                # Check if cache is still valid
                cache_time = datetime.fromisoformat(cached_data['timestamp'])
                if datetime.now() - cache_time < timedelta(seconds=self.config.cache_ttl):
                    return cached_data['css']
            except Exception:
                pass  # Cache invalid, regenerate

        # Generate new critical CSS
        css_content = self.extractor.generate_critical_css(route_name)

        # Minify if enabled
        if self.config.enable_compression:
            css_content = self.extractor.minify_css(css_content)

        # Save to cache
        if self.config.enable_cache:
            cache_data = {
                'route': route_name,
                'css': css_content,
                'timestamp': datetime.now().isoformat(),
                'hash': hashlib.md5(css_content.encode()).hexdigest()
            }

            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)

        # Save to output file
        self.extractor.save_critical_css(route_name, css_content)

        return css_content

    def generate_all(self, force: bool = False):
        """Generate critical CSS for all routes"""
        routes = self.extractor.extract_all_routes()

        self.logger.info(f"Generating critical CSS for {len(routes)} routes...")

        for route in routes:
            try:
                css_content = self.generate_for_route(route, force)
                self.logger.info(f"✅ Generated critical CSS for {route} ({len(css_content)} chars)")
            except Exception as e:
                self.logger.error(f"❌ Failed to generate CSS for {route}: {e}")

        self.logger.info("🎉 Critical CSS generation completed!")

    def get_inline_css(self, route_name: str) -> str:
        """Get critical CSS ready for inlining"""
        css_content = self.generate_for_route(route_name)

        # Wrap in style tags
        return f"<style>\\n{css_content}\\n</style>"

    def get_css_link(self, route_name: str) -> str:
        """Get link tag for critical CSS file"""
        filename = f"{route_name.replace('.', '_')}.css"
        return f'<link rel=\"preload\" href=\"/static/css/critical/{filename}\" as=\"style\" onload=\"this.onload=null;this.rel=\\'stylesheet\\'\">'

# ============================================================================
# TAILWIND OPTIMIZER
# ============================================================================

class TailwindOptimizer:
    """Optimizes Tailwind CSS usage and purging"""

    def __init__(self, config: CriticalCSSConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)

    def analyze_usage(self) -> Dict[str, Any]:
        """Analyze Tailwind class usage across the project"""
        usage_stats = {
            'total_files': 0,
            'files_with_tailwind': 0,
            'total_classes': 0,
            'unique_classes': set(),
            'class_frequency': {},
            'unused_classes': set()
        }

        # Analyze templates
        template_dir = Path('templates')
        if template_dir.exists():
            for html_file in template_dir.rglob('*.html'):
                usage_stats['total_files'] += 1

                try:
                    with open(html_file, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Extract Tailwind classes
                    classes = re.findall(r'class=[\"\'][^\"\']*[\"\']', content)
                    if classes:
                        usage_stats['files_with_tailwind'] += 1

                        for class_attr in classes:
                            class_list = re.findall(r'([\\w\\-]+)', class_attr)
                            for cls in class_list:
                                if cls not in ['class', 'className']:
                                    usage_stats['unique_classes'].add(cls)
                                    usage_stats['total_classes'] += 1
                                    usage_stats['class_frequency'][cls] = usage_stats['class_frequency'].get(cls, 0) + 1

                except Exception as e:
                    self.logger.error(f"Error analyzing {html_file}: {e}")

        return usage_stats

    def generate_purge_config(self) -> str:
        """Generate Tailwind purge configuration"""
        usage_stats = self.analyze_usage()

        # Generate safelist based on usage
        safelist = list(usage_stats['unique_classes'])

        purge_config = f"""
        // Tailwind CSS Purge Configuration
        module.exports = {{
          content: {json.dumps(self.config.content_paths, indent=2)},
          safelist: {json.dumps(safelist, indent=2)},
          theme: {{
            extend: {{
              colors: {{
                'validoai': {{
                  'primary': '#2563eb',
                  'secondary': '#64748b',
                  'success': '#059669',
                  'warning': '#d97706',
                  'error': '#dc2626'
                }}
              }}
            }}
          }},
          plugins: []
        }}
        """

        return purge_config

    def optimize_config(self) -> str:
        """Generate optimized Tailwind configuration"""
        config = f"""
        /** @type {{import('tailwindcss').Config}} */
        module.exports = {{
          content: {json.dumps(self.config.content_paths, indent=2)},
          theme: {{
            extend: {{
              colors: {{
                validoai: {{
                  primary: '#2563eb',
                  secondary: '#64748b',
                  success: '#059669',
                  warning: '#d97706',
                  error: '#dc2626'
                }}
              }},
              fontFamily: {{
                sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif']
              }},
              spacing: {{
                '18': '4.5rem',
                '88': '22rem'
              }},
              animation: {{
                'fade-in': 'fadeIn 0.5s ease-in-out',
                'slide-up': 'slideUp 0.3s ease-out'
              }},
              keyframes: {{
                fadeIn: {{
                  '0%': {{ opacity: '0' }},
                  '100%': {{ opacity: '1' }}
                }},
                slideUp: {{
                  '0%': {{ transform: 'translateY(10px)', opacity: '0' }},
                  '100%': {{ transform: 'translateY(0)', opacity: '1' }}
                }}
              }}
            }}
          }},
          plugins: [
            // Custom plugins can be added here
          ]
        }}
        """

        return config

# ============================================================================
# CRITICAL CSS INTEGRATION
# ============================================================================

class CriticalCSSIntegration:
    """Integrates critical CSS with Flask templates"""

    def __init__(self, manager: CriticalCSSManager):
        self.manager = manager

    def inject_critical_css(self, template_content: str, route_name: str) -> str:
        """Inject critical CSS into HTML template"""
        critical_css = self.manager.get_inline_css(route_name)

        # Insert after opening <head> tag
        head_pattern = r'(<head[^>]*>)'
        replacement = f'\\1\\n{critical_css}\\n'

        return re.sub(head_pattern, replacement, template_content, flags=re.IGNORECASE)

    def add_preload_links(self, template_content: str, route_name: str) -> str:
        """Add preload links for non-critical CSS"""
        preload_link = self.manager.get_css_link(route_name)

        # Insert before closing </head> tag
        head_close_pattern = r'(</head>)'
        replacement = f'\\n{preload_link}\\n\\1'

        return re.sub(head_close_pattern, replacement, template_content, flags=re.IGNORECASE)

    def process_template(self, template_path: str, route_name: str) -> str:
        """Process template with critical CSS optimization"""
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Inject critical CSS
            content = self.inject_critical_css(content, route_name)

            # Add preload links
            content = self.add_preload_links(content, route_name)

            return content

        except Exception as e:
            self.manager.logger.error(f"Error processing template {template_path}: {e}")
            return ""

# ============================================================================
# PERFORMANCE MONITORING
# ============================================================================

class CriticalCSSPerformanceMonitor:
    """Monitors critical CSS performance impact"""

    def __init__(self):
        self.metrics = {
            'generation_times': [],
            'css_sizes': [],
            'cache_hit_rate': 0,
            'total_requests': 0,
            'cache_hits': 0
        }
        self.logger = logging.getLogger(__name__)

    def record_generation_time(self, route_name: str, duration_ms: float):
        """Record CSS generation time"""
        self.metrics['generation_times'].append({
            'route': route_name,
            'duration_ms': duration_ms,
            'timestamp': datetime.now().isoformat()
        })

        if duration_ms > 1000:  # Log slow generations
            self.logger.warning(f"Slow CSS generation for {route_name}: {duration_ms:.2f}ms")

    def record_css_size(self, route_name: str, size_bytes: int):
        """Record generated CSS size"""
        self.metrics['css_sizes'].append({
            'route': route_name,
            'size_bytes': size_bytes,
            'size_kb': size_bytes / 1024,
            'timestamp': datetime.now().isoformat()
        })

        if size_bytes > 50 * 1024:  # Log large CSS files
            self.logger.warning(f"Large critical CSS for {route_name}: {size_bytes / 1024:.2f}KB")

    def record_cache_access(self, hit: bool):
        """Record cache access"""
        self.metrics['total_requests'] += 1
        if hit:
            self.metrics['cache_hits'] += 1

        self.metrics['cache_hit_rate'] = self.metrics['cache_hits'] / self.metrics['total_requests']

    def get_performance_report(self) -> Dict[str, Any]:
        """Generate performance report"""
        if not self.metrics['generation_times']:
            return {'message': 'No performance data available'}

        avg_generation_time = sum(item['duration_ms'] for item in self.metrics['generation_times']) / len(self.metrics['generation_times'])
        avg_css_size = sum(item['size_kb'] for item in self.metrics['css_sizes']) / len(self.metrics['css_sizes']) if self.metrics['css_sizes'] else 0

        return {
            'summary': {
                'total_routes_processed': len(set(item['route'] for item in self.metrics['generation_times'])),
                'average_generation_time_ms': round(avg_generation_time, 2),
                'average_css_size_kb': round(avg_css_size, 2),
                'cache_hit_rate_percent': round(self.metrics['cache_hit_rate'] * 100, 2)
            },
            'performance_trends': {
                'generation_times': self.metrics['generation_times'][-10:],  # Last 10
                'css_sizes': self.metrics['css_sizes'][-10:]  # Last 10
            },
            'recommendations': self._generate_recommendations(avg_generation_time, avg_css_size)
        }

    def _generate_recommendations(self, avg_time: float, avg_size: float) -> List[str]:
        """Generate performance recommendations"""
        recommendations = []

        if avg_time > 500:
            recommendations.append("Consider increasing cache TTL or using background generation")

        if avg_size > 30:
            recommendations.append("Critical CSS size is large - consider optimizing class selection")

        if self.metrics['cache_hit_rate'] < 0.8:
            recommendations.append("Low cache hit rate - consider adjusting cache strategy")

        return recommendations if recommendations else ["Performance is optimal"]

# ============================================================================
# MAIN SYSTEM
# ============================================================================

# Global instances
performance_monitor = CriticalCSSPerformanceMonitor()

def generate_critical_css_for_all_routes():
    """Generate critical CSS for all routes with monitoring"""
    print("🚀 Starting Critical CSS Generation...")

    config = CriticalCSSConfig()
    manager = CriticalCSSManager(config)
    optimizer = TailwindOptimizer(config)

    start_time = datetime.now()

    try:
        # Generate critical CSS for all routes
        manager.generate_all(force=True)

        # Generate optimized Tailwind config
        optimized_config = optimizer.optimize_config()
        with open('tailwind.config.js', 'w') as f:
            f.write(optimized_config)

        # Generate purge config
        purge_config = optimizer.generate_purge_config()
        with open('tailwind.config.purge.js', 'w') as f:
            f.write(purge_config)

        duration = (datetime.now() - start_time).total_seconds() * 1000

        print("✅ Critical CSS generation completed!"        print(f"⏱️ Total time: {duration:.2f}ms")
        print(f"📊 Config files updated: tailwind.config.js, tailwind.config.purge.js")

        return True

    except Exception as e:
        print(f"❌ Critical CSS generation failed: {e}")
        return False

def get_critical_css_for_route(route_name: str) -> str:
    """Get critical CSS for a specific route"""
    config = CriticalCSSConfig()
    manager = CriticalCSSManager(config)

    return manager.get_inline_css(route_name)

if __name__ == '__main__':
    # Run critical CSS generation
    success = generate_critical_css_for_all_routes()

    if success:
        # Show performance report
        config = CriticalCSSConfig()
        monitor = CriticalCSSPerformanceMonitor()

        print("\\n📊 Performance Report:")
        report = monitor.get_performance_report()
        if 'summary' in report:
            summary = report['summary']
            print(f"  Routes processed: {summary['total_routes_processed']}")
            print(f"  Avg generation time: {summary['average_generation_time_ms']}ms")
            print(f"  Avg CSS size: {summary['average_css_size_kb']}KB")
            print(f"  Cache hit rate: {summary['cache_hit_rate_percent']}%")

        print("\\n🎉 Critical CSS system is ready!")
    else:
        print("\\n❌ Critical CSS generation failed!")
