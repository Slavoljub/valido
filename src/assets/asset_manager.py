"""
Asset Management System for ValidoAI
Comprehensive asset handling for CSS, JS, fonts, and images
"""

from typing import Dict, List, Any, Optional, Set
import os
import json
import hashlib
import logging
from pathlib import Path
from flask import current_app, url_for
import mimetypes

logger = logging.getLogger(__name__)

class AssetManager:
    """Centralized asset management system"""

    def __init__(self):
        self.assets: Dict[str, Dict[str, Any]] = {}
        self.bundles: Dict[str, List[str]] = {}
        self.dependencies: Dict[str, Set[str]] = {}
        self.cache_manifest: Dict[str, str] = {}
        self.themes: Dict[str, Dict[str, Any]] = {}

    def register_asset(self, name: str, asset_type: str, path: str,
                      config: Dict[str, Any] = None):
        """Register an asset"""
        asset_hash = self._calculate_file_hash(path) if os.path.exists(path) else None

        self.assets[name] = {
            'type': asset_type,
            'path': path,
            'config': config or {},
            'hash': asset_hash,
            'version': config.get('version', '1.0.0') if config else '1.0.0',
            'dependencies': config.get('dependencies', []) if config else [],
            'minified': config.get('minified', False) if config else False,
            'async': config.get('async', False) if config else False,
            'defer': config.get('defer', False) if config else False,
            'integrity': config.get('integrity', '') if config else '',
            'crossorigin': config.get('crossorigin', '') if config else ''
        }

        # Track dependencies
        if not self.dependencies.get(asset_type):
            self.dependencies[asset_type] = set()
        self.dependencies[asset_type].update(self.assets[name]['dependencies'])

    def register_bundle(self, name: str, assets: List[str], bundle_type: str = 'js'):
        """Register an asset bundle"""
        self.bundles[name] = assets

        # Validate that all assets in bundle exist
        for asset in assets:
            if asset not in self.assets:
                logger.warning(f"Asset '{asset}' in bundle '{name}' not found")

    def get_asset_url(self, name: str) -> Optional[str]:
        """Get URL for an asset with cache busting"""
        asset = self.assets.get(name)
        if not asset:
            return None

        base_url = asset['path']
        if asset['hash']:
            # Add cache busting parameter
            separator = '&' if '?' in base_url else '?'
            base_url += f"{separator}v={asset['hash'][:8]}"

        return url_for('static', filename=base_url)

    def get_bundle_assets(self, name: str) -> List[str]:
        """Get all assets in a bundle"""
        return self.bundles.get(name, [])

    def render_css_links(self, names: List[str] = None, exclude: List[str] = None) -> str:
        """Render CSS link tags"""
        css_assets = []
        
        for name in (names or self.assets.keys()):
            # Check if it's a bundle
            if name in self.bundles:
                # Add all assets from the bundle
                bundle_assets = self.bundles[name]
                for asset_name in bundle_assets:
                    if asset_name in self.assets and self.assets[asset_name]['type'] == 'css':
                        css_assets.append(asset_name)
            # Check if it's a direct asset
            elif name in self.assets and self.assets[name]['type'] == 'css':
                css_assets.append(name)

        if exclude:
            css_assets = [name for name in css_assets if name not in exclude]

        links = []
        for name in css_assets:
            asset = self.assets[name]
            attrs = []

            if asset['config'].get('media'):
                attrs.append(f'media="{asset["config"]["media"]}"')
            if asset['config'].get('integrity'):
                attrs.append(f'integrity="{asset["config"]["integrity"]}"')
            if asset['config'].get('crossorigin'):
                attrs.append(f'crossorigin="{asset["config"]["crossorigin"]}"')

            attr_string = ' '.join(attrs)
            links.append(f'<link rel="stylesheet" href="{self.get_asset_url(name)}" {attr_string}>')

        return '\n'.join(links)

    def render_js_scripts(self, names: List[str] = None, exclude: List[str] = None) -> str:
        """Render JavaScript script tags"""
        js_assets = [name for name in (names or self.assets.keys())
                    if self.assets[name]['type'] == 'js']

        if exclude:
            js_assets = [name for name in js_assets if name not in exclude]

        scripts = []
        for name in js_assets:
            asset = self.assets[name]
            attrs = []

            if asset['config'].get('async'):
                attrs.append('async')
            if asset['config'].get('defer'):
                attrs.append('defer')
            if asset['config'].get('type'):
                attrs.append(f'type="{asset["config"]["type"]}"')
            if asset['config'].get('integrity'):
                attrs.append(f'integrity="{asset["config"]["integrity"]}"')
            if asset['config'].get('crossorigin'):
                attrs.append(f'crossorigin="{asset["config"]["crossorigin"]}"')

            attr_string = ' '.join(attrs)
            scripts.append(f'<script src="{self.get_asset_url(name)}" {attr_string}></script>')

        return '\n'.join(scripts)

    def render_font_links(self, names: List[str] = None) -> str:
        """Render font link tags (Google Fonts, etc.)"""
        font_assets = [name for name in (names or self.assets.keys())
                      if self.assets[name]['type'] == 'font']

        links = []
        for name in font_assets:
            asset = self.assets[name]
            font_url = asset['config'].get('font_url', '')
            if font_url:
                links.append(f'<link href="{font_url}" rel="stylesheet">')

        return '\n'.join(links)

    def render_favicon_links(self) -> str:
        """Render favicon link tags"""
        favicon_assets = [name for name in self.assets.keys()
                         if self.assets[name]['type'] == 'favicon']

        links = []
        for name in favicon_assets:
            asset = self.assets[name]
            rel = asset['config'].get('rel', 'icon')
            size = asset['config'].get('size', '')
            links.append(f'<link rel="{rel}" href="{self.get_asset_url(name)}" sizes="{size}">')

        return '\n'.join(links)

    def get_theme_assets(self, theme_name: str) -> Dict[str, List[str]]:
        """Get assets for a specific theme"""
        theme = self.themes.get(theme_name, {})
        return {
            'css': theme.get('css', []),
            'js': theme.get('js', []),
            'fonts': theme.get('fonts', [])
        }

    def set_theme(self, theme_name: str, assets: Dict[str, List[str]]):
        """Set assets for a theme"""
        self.themes[theme_name] = assets

    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate file hash for cache busting"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception as e:
            logger.warning(f"Could not calculate hash for {file_path}: {e}")
            return ''

    def get_asset_manifest(self) -> Dict[str, Any]:
        """Get asset manifest for debugging/build process"""
        return {
            'assets': self.assets,
            'bundles': self.bundles,
            'dependencies': {k: list(v) for k, v in self.dependencies.items()},
            'themes': self.themes,
            'cache_manifest': self.cache_manifest
        }

class AssetBuilder:
    """Helper class to build common assets"""

    def __init__(self, manager: AssetManager):
        self.manager = manager

    def build_tailwind_css(self):
        """Build Tailwind CSS asset"""
        self.manager.register_asset(
            'tailwind_css',
            'css',
            'static/css/tailwind.css',
            {
                'version': '3.3.0',
                'minified': True,
                'description': 'Tailwind CSS framework'
            }
        )

    def build_alpine_js(self):
        """Build Alpine.js asset"""
        self.manager.register_asset(
            'alpine_js',
            'js',
            'static/js/alpine.min.js',
            {
                'version': '3.13.0',
                'defer': True,
                'description': 'Alpine.js framework'
            }
        )

    def build_htmx_js(self):
        """Build HTMX asset"""
        self.manager.register_asset(
            'htmx_js',
            'js',
            'static/js/htmx.js',
            {
                'version': '1.9.6',
                'defer': True,
                'description': 'HTMX library'
            }
        )

    def build_main_css(self):
        """Build main application CSS"""
        self.manager.register_asset(
            'main_css',
            'css',
            'static/css/main.css',
            {
                'version': '1.0.0',
                'minified': True,
                'description': 'Main application styles'
            }
        )

    def build_main_js(self):
        """Build main application JavaScript"""
        self.manager.register_asset(
            'main_js',
            'js',
            'static/js/main.js',
            {
                'version': '1.0.0',
                'defer': True,
                'description': 'Main application JavaScript'
            }
        )

    def build_theme_assets(self):
        """Build theme-specific assets"""
        # Light theme CSS
        self.manager.register_asset(
            'light_theme_css',
            'css',
            'static/css/themes/light.css',
            {
                'version': '1.0.0',
                'media': 'screen',
                'description': 'Light theme styles'
            }
        )

        # Dark theme CSS
        self.manager.register_asset(
            'dark_theme_css',
            'css',
            'static/css/themes/dark.css',
            {
                'version': '1.0.0',
                'media': 'screen',
                'description': 'Dark theme styles'
            }
        )

    def build_valido_themes(self):
        """Build Valido theme assets - professional themes with Tailwind classes"""
        # Valido White Theme
        self.manager.register_asset(
            'valido_white_css',
            'css',
            'static/themes/valido-white.css',
            {
                'version': '1.0.0',
                'media': 'screen',
                'description': 'Valido White Theme - Professional Light Theme'
            }
        )

        # Valido Dark Theme
        self.manager.register_asset(
            'valido_dark_css',
            'css',
            'static/themes/valido-dark.css',
            {
                'version': '1.0.0',
                'media': 'screen',
                'description': 'Valido Dark Theme - Professional Dark Theme'
            }
        )

        # Valido High Contrast Theme
        self.manager.register_asset(
            'valido_high_contrast_css',
            'css',
            'static/themes/valido-high-contrast.css',
            {
                'version': '1.0.0',
                'media': 'screen',
                'description': 'Valido High Contrast Theme - Enhanced Accessibility'
            }
        )

        # Valido Minimal Theme
        self.manager.register_asset(
            'valido_minimal_css',
            'css',
            'static/themes/valido-minimal.css',
            {
                'version': '1.0.0',
                'media': 'screen',
                'description': 'Valido Minimal Theme - Clean and Minimalist'
            }
        )

    def build_font_assets(self):
        """Build font assets"""
        # Inter font from Google Fonts
        self.manager.register_asset(
            'inter_font',
            'font',
            '',
            {
                'font_url': 'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap',
                'description': 'Inter font family'
            }
        )

        # Local font files
        self.manager.register_asset(
            'custom_font_woff2',
            'font',
            'static/fonts/custom-font.woff2',
            {
                'description': 'Custom font WOFF2'
            }
        )

    def build_icon_assets(self):
        """Build icon and favicon assets"""
        # Favicon
        self.manager.register_asset(
            'favicon_ico',
            'favicon',
            'static/favicons/favicon.ico',
            {
                'rel': 'icon',
                'description': 'Site favicon'
            }
        )

        # Apple touch icon
        self.manager.register_asset(
            'apple_touch_icon',
            'favicon',
            'static/icons/apple-touch-icon.png',
            {
                'rel': 'apple-touch-icon',
                'size': '180x180',
                'description': 'Apple touch icon'
            }
        )

    def build_component_assets(self):
        """Build component-specific assets"""
        self.manager.register_asset(
            'modal_css',
            'css',
            'static/css/components/modal.css',
            {
                'version': '1.0.0',
                'description': 'Modal component styles'
            }
        )

        self.manager.register_asset(
            'table_css',
            'css',
            'static/css/components/table.css',
            {
                'version': '1.0.0',
                'description': 'Table component styles'
            }
        )

        self.manager.register_asset(
            'form_css',
            'css',
            'static/css/components/form.css',
            {
                'version': '1.0.0',
                'description': 'Form component styles'
            }
        )

        self.manager.register_asset(
            'toast_css',
            'css',
            'static/css/components/toast.css',
            {
                'version': '1.0.0',
                'description': 'Toast notification styles'
            }
        )

        self.manager.register_asset(
            'captcha_css',
            'css',
            'static/css/components/captcha.css',
            {
                'version': '1.0.0',
                'description': 'CAPTCHA component styles'
            }
        )

class ThemeManager:
    """Theme management system"""

    def __init__(self, asset_manager: AssetManager):
        self.asset_manager = asset_manager
        self.current_theme = 'light'
        self.available_themes = {}

    def register_theme(self, name: str, config: Dict[str, Any]):
        """Register a theme"""
        self.available_themes[name] = config

        # Register theme assets with asset manager
        theme_assets = {
            'css': config.get('css', []),
            'js': config.get('js', []),
            'fonts': config.get('fonts', [])
        }
        self.asset_manager.set_theme(name, theme_assets)

    def set_theme(self, theme_name: str):
        """Set current theme"""
        if theme_name in self.available_themes:
            self.current_theme = theme_name
            return True
        return False

    def get_theme_config(self, theme_name: str = None) -> Dict[str, Any]:
        """Get theme configuration"""
        theme = theme_name or self.current_theme
        return self.available_themes.get(theme, {})

    def get_theme_css_variables(self, theme_name: str = None) -> str:
        """Get CSS custom properties for theme"""
        theme_config = self.get_theme_config(theme_name)
        colors = theme_config.get('colors', {})

        css_vars = []
        for var_name, value in colors.items():
            css_vars.append(f'--color-{var_name}: {value};')

        return '\n'.join(css_vars)

    def render_theme_css(self, theme_name: str = None) -> str:
        """Render theme CSS"""
        theme = theme_name or self.current_theme
        theme_assets = self.asset_manager.get_theme_assets(theme)

        css_links = []
        for css_asset in theme_assets.get('css', []):
            url = self.asset_manager.get_asset_url(css_asset)
            if url:
                css_links.append(f'<link rel="stylesheet" href="{url}">')

        return '\n'.join(css_links)

# Global instances
asset_manager = AssetManager()
asset_builder = AssetBuilder(asset_manager)
theme_manager = ThemeManager(asset_manager)

# Initialize default assets
def initialize_default_assets():
    """Initialize default asset library"""

    # Build core framework assets
    asset_builder.build_tailwind_css()
    asset_builder.build_alpine_js()
    asset_builder.build_htmx_js()

    # Build application assets
    asset_builder.build_main_css()
    asset_builder.build_main_js()

    # Build Valido theme assets
    asset_builder.build_valido_themes()

    # Build font assets
    asset_builder.build_font_assets()

    # Build icon assets
    asset_builder.build_icon_assets()

    # Build component assets
    asset_builder.build_component_assets()

    # Create asset bundles
    asset_manager.register_bundle('core_css', ['tailwind_css', 'main_css'])
    asset_manager.register_bundle('core_js', ['alpine_js', 'htmx_js', 'main_js'])
    asset_manager.register_bundle('component_css', ['modal_css', 'table_css', 'form_css', 'toast_css', 'captcha_css'])
    asset_manager.register_bundle('fonts', ['inter_font'])

    # Initialize themes
    theme_manager.register_theme('light', {
        'name': 'Light',
        'colors': {
            'primary': '#3b82f6',
            'secondary': '#64748b',
            'success': '#10b981',
            'warning': '#f59e0b',
            'danger': '#ef4444',
            'background': '#ffffff',
            'surface': '#f8fafc',
            'text': '#1e293b',
            'text_secondary': '#64748b',
            'border': '#e2e8f0'
        },
        'css': ['light_theme_css'],
        'js': [],
        'fonts': ['inter_font']
    })

    theme_manager.register_theme('dark', {
        'name': 'Dark',
        'colors': {
            'primary': '#3b82f6',
            'secondary': '#94a3b8',
            'success': '#059669',
            'warning': '#d97706',
            'danger': '#dc2626',
            'background': '#0f172a',
            'surface': '#1e293b',
            'text': '#f8fafc',
            'text_secondary': '#94a3b8',
            'border': '#334155'
        },
        'css': ['dark_theme_css'],
        'js': [],
        'fonts': ['inter_font']
    })

    # Valido Professional Themes
    theme_manager.register_theme('valido-white', {
        'name': 'Valido White',
        'colors': {
            'primary': '#2563eb',
            'secondary': '#64748b',
            'success': '#059669',
            'warning': '#d97706',
            'danger': '#dc2626',
            'info': '#0891b2',
            'background': '#ffffff',
            'surface': '#f8fafc',
            'text': '#1e293b',
            'text_secondary': '#64748b',
            'text_muted': '#94a3b8',
            'border': '#e2e8f0'
        },
        'css': ['valido_white_css'],
        'js': [],
        'fonts': ['inter_font']
    })

    theme_manager.register_theme('valido-dark', {
        'name': 'Valido Dark',
        'colors': {
            'primary': '#3b82f6',
            'secondary': '#94a3b8',
            'success': '#10b981',
            'warning': '#f59e0b',
            'danger': '#ef4444',
            'info': '#06b6d4',
            'background': '#0f172a',
            'surface': '#1e293b',
            'text': '#f8fafc',
            'text_secondary': '#cbd5e1',
            'text_muted': '#94a3b8',
            'border': '#475569'
        },
        'css': ['valido_dark_css'],
        'js': [],
        'fonts': ['inter_font']
    })

    theme_manager.register_theme('valido-high-contrast', {
        'name': 'Valido High Contrast',
        'colors': {
            'primary': '#0000ff',
            'secondary': '#000000',
            'success': '#008000',
            'warning': '#ffa500',
            'danger': '#ff0000',
            'info': '#0000ff',
            'background': '#ffffff',
            'surface': '#f8f8f8',
            'text': '#000000',
            'text_secondary': '#000000',
            'text_muted': '#404040',
            'border': '#000000'
        },
        'css': ['valido_high_contrast_css'],
        'js': [],
        'fonts': ['inter_font']
    })

    theme_manager.register_theme('valido-minimal', {
        'name': 'Valido Minimal',
        'colors': {
            'primary': '#1f2937',
            'secondary': '#6b7280',
            'success': '#10b981',
            'warning': '#f59e0b',
            'danger': '#ef4444',
            'info': '#3b82f6',
            'background': '#ffffff',
            'surface': '#f9fafb',
            'text': '#111827',
            'text_secondary': '#374151',
            'text_muted': '#6b7280',
            'border': '#e5e7eb'
        },
        'css': ['valido_minimal_css'],
        'js': [],
        'fonts': ['inter_font']
    })

    logger.info("Default assets initialized successfully")

# Auto-initialize
initialize_default_assets()
