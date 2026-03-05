"""
Critical CSS Loading System for ValidoAI
Implements critical CSS inlining and deferred loading for optimal performance
"""

import os
import hashlib
from typing import Dict, List, Set
from pathlib import Path
from flask import current_app

class CriticalCSSLoader:
    """Manages critical CSS loading and optimization"""

    def __init__(self, static_folder: str = "static"):
        self.static_folder = Path(static_folder)
        self.critical_css_cache: Dict[str, str] = {}
        self.loaded_components: Set[str] = set()

    def get_critical_css(self, route_name: str = 'dashboard') -> str:
        """
        Get critical CSS for a specific route
        """
        cache_key = f"critical_{route_name}"

        if cache_key in self.critical_css_cache:
            return self.critical_css_cache[cache_key]

        # Define critical CSS for different routes
        critical_styles = {
            'dashboard': self._get_dashboard_critical_css(),
            'login': self._get_auth_critical_css(),
            'admin': self._get_admin_critical_css(),
            'default': self._get_base_critical_css()
        }

        critical_css = critical_styles.get(route_name, critical_styles['default'])
        self.critical_css_cache[cache_key] = critical_css

        return critical_css

    def _get_dashboard_critical_css(self) -> str:
        """Critical CSS for dashboard pages"""
        return """
        /* Critical Dashboard Styles */
        body { margin: 0; padding: 0; font-family: 'Inter', system-ui, sans-serif; }
        .glass-card { background: rgba(255,255,255,0.1); backdrop-filter: blur(20px); border: 1px solid rgba(255,255,255,0.2); }
        .metric-card { background: rgba(255,255,255,0.9); border-radius: 1rem; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }
        .metric-number { font-size: 2rem; font-weight: 700; }
        .btn-modern { padding: 0.5rem 1.5rem; border-radius: 0.75rem; font-weight: 600; }
        .loading-shimmer { background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%); background-size: 200% 100%; animation: shimmer 1.5s infinite; }
        @keyframes shimmer { 0% { background-position: -200% 0; } 100% { background-position: 200% 0; } }
        .grid-modern { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.5rem; }
        .chart-modern { background: rgba(255,255,255,0.9); border-radius: 1rem; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }
        .widget-container { background: rgba(255,255,255,0.9); border-radius: 1rem; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }
        .status-indicator { display: inline-flex; align-items: center; padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 600; }
        .status-active { background: #dcfce7; color: #166534; }
        .status-warning { background: #fef3c7; color: #92400e; }
        .status-error { background: #fee2e2; color: #991b1b; }

        /* Dark mode critical styles */
        @media (prefers-color-scheme: dark) {
            .metric-card { background: rgba(31,41,55,0.9); color: white; }
            .chart-modern { background: rgba(31,41,55,0.9); }
            .widget-container { background: rgba(31,41,55,0.9); }
        }

        /* Mobile critical styles */
        @media (max-width: 768px) {
            .grid-modern { grid-template-columns: 1fr; }
            .metric-card { padding: 1rem; }
        }
        """

    def _get_auth_critical_css(self) -> str:
        """Critical CSS for authentication pages"""
        return """
        /* Critical Auth Styles */
        body { margin: 0; padding: 0; font-family: 'Inter', system-ui, sans-serif; min-height: 100vh; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .auth-card { background: rgba(255,255,255,0.95); backdrop-filter: blur(20px); border-radius: 1rem; box-shadow: 0 20px 40px rgba(0,0,0,0.1); }
        .form-input { width: 100%; padding: 0.75rem; border: 1px solid #e5e7eb; border-radius: 0.5rem; }
        .form-input:focus { outline: none; ring: 2px; ring-color: #3b82f6; border-color: #3b82f6; }
        .btn-primary { background: #3b82f6; color: white; padding: 0.75rem 1.5rem; border-radius: 0.5rem; font-weight: 600; }
        .btn-primary:hover { background: #2563eb; }
        """

    def _get_admin_critical_css(self) -> str:
        """Critical CSS for admin pages"""
        return """
        /* Critical Admin Styles */
        body { margin: 0; padding: 0; font-family: 'Inter', system-ui, sans-serif; background: #f8fafc; }
        .admin-sidebar { background: #1f2937; color: white; }
        .admin-header { background: white; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        .data-table { width: 100%; border-collapse: collapse; }
        .data-table th { background: #f8fafc; padding: 0.75rem; text-align: left; font-weight: 600; }
        .data-table td { padding: 0.75rem; border-bottom: 1px solid #e5e7eb; }
        .badge { display: inline-flex; align-items: center; padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 600; }
        """

    def _get_base_critical_css(self) -> str:
        """Base critical CSS for all pages"""
        return """
        /* Base Critical Styles */
        * { box-sizing: border-box; }
        body { margin: 0; padding: 0; font-family: 'Inter', system-ui, sans-serif; line-height: 1.6; color: #374151; }
        .container { max-width: 1200px; margin: 0 auto; padding: 0 1rem; }
        .btn { display: inline-flex; align-items: center; padding: 0.5rem 1rem; border-radius: 0.375rem; font-weight: 500; text-decoration: none; border: 1px solid transparent; cursor: pointer; }
        .btn-primary { background: #3b82f6; color: white; }
        .btn-secondary { background: #f8fafc; color: #374151; border-color: #e5e7eb; }
        .card { background: white; border-radius: 0.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        .loading { display: flex; align-items: center; justify-content: center; padding: 2rem; }
        .hidden { display: none; }
        """

    def generate_critical_css_link(self, route_name: str = 'dashboard') -> str:
        """Generate HTML link tag for critical CSS"""
        critical_css = self.get_critical_css(route_name)
        css_hash = hashlib.md5(critical_css.encode()).hexdigest()[:8]

        return f'<style id="critical-css-{css_hash}">{critical_css}</style>'

    def get_deferred_css_links(self, components: List[str]) -> List[str]:
        """Get deferred CSS links for components"""
        deferred_links = []

        # Base styles
        deferred_links.append('<link rel="preload" href="/static/css/main.css" as="style" onload="this.onload=null;this.rel=\'stylesheet\'">')
        deferred_links.append('<noscript><link rel="stylesheet" href="/static/css/main.css"></noscript>')

        # Component-specific styles
        component_styles = {
            'dashboard': ['/static/css/dashboard.css', '/static/css/charts.css'],
            'forms': ['/static/css/forms.css'],
            'tables': ['/static/css/tables.css'],
            'modals': ['/static/css/modals.css']
        }

        for component in components:
            if component in component_styles:
                for style_path in component_styles[component]:
                    if os.path.exists(self.static_folder / style_path.replace('/static/', '')):
                        deferred_links.append(f'<link rel="preload" href="{style_path}" as="style" onload="this.onload=null;this.rel=\'stylesheet\'">')
                        deferred_links.append(f'<noscript><link rel="stylesheet" href="{style_path}"></noscript>')

        return deferred_links

    def optimize_css_delivery(self, route_name: str = 'dashboard', components: List[str] = None) -> Dict[str, any]:
        """Optimize CSS delivery for a route"""
        if components is None:
            components = []

        return {
            'critical_css': self.generate_critical_css_link(route_name),
            'deferred_links': self.get_deferred_css_links(components),
            'preload_hints': self._generate_preload_hints(components)
        }

    def _generate_preload_hints(self, components: List[str]) -> List[str]:
        """Generate resource preload hints"""
        hints = []

        # Font preloading
        hints.extend([
            '<link rel="preload" href="/static/fonts/inter.woff2" as="font" type="font/woff2" crossorigin>',
            '<link rel="preload" href="/static/fonts/icons.woff2" as="font" type="font/woff2" crossorigin>'
        ])

        # Component-specific preloads
        if 'charts' in components:
            hints.append('<link rel="preload" href="https://cdn.jsdelivr.net/npm/chart.js" as="script">')

        return hints


# Global instance
critical_css_loader = CriticalCSSLoader()
