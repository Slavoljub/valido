# src/extensions/theme.py
from flask import session, request, g
from functools import wraps
import json

class ThemeManager:
    THEMES = {
        'light': {
            'name': 'Light Mode',
            'class': 'light',
            'icon': 'sun',
            'description': 'Standard light theme',
            'css_vars': {
                '--bg-primary': '#ffffff',
                '--bg-secondary': '#f9fafb',
                '--text-primary': '#111827',
                '--text-secondary': '#6b7280',
                '--border-color': '#d1d5db',
                '--accent-color': '#3b82f6'
            }
        },
        'dark': {
            'name': 'Dark Mode', 
            'class': 'dark',
            'icon': 'moon',
            'description': 'Dark theme for low-light environments',
            'css_vars': {
                '--bg-primary': '#111827',
                '--bg-secondary': '#1f2937',
                '--text-primary': '#f9fafb',
                '--text-secondary': '#d1d5db',
                '--border-color': '#374151',
                '--accent-color': '#60a5fa'
            }
        },
        'dracula': {
            'name': 'Dracula',
            'class': 'dracula',
            'icon': 'ghost',
            'description': 'Dracula theme with purple accents',
            'css_vars': {
                '--bg-primary': '#282a36',
                '--bg-secondary': '#44475a',
                '--text-primary': '#f8f8f2',
                '--text-secondary': '#6272a4',
                '--border-color': '#6272a4',
                '--accent-color': '#bd93f9',
                '--accent-secondary': '#ff79c6',
                '--success-color': '#50fa7b',
                '--warning-color': '#ffb86c',
                '--error-color': '#ff5555'
            }
        },
        'high-contrast': {
            'name': 'High Contrast',
            'class': 'high-contrast',
            'icon': 'eye',
            'description': 'High contrast theme for accessibility',
            'css_vars': {
                '--bg-primary': '#000000',
                '--bg-secondary': '#1a1a1a',
                '--text-primary': '#ffffff',
                '--text-secondary': '#cccccc',
                '--border-color': '#ffffff',
                '--accent-color': '#ffff00',
                '--success-color': '#00ff00',
                '--warning-color': '#ffff00',
                '--error-color': '#ff0000'
            }
        },
        'system': {
            'name': 'System',
            'class': 'system',
            'icon': 'monitor',
            'description': 'Follows system preference',
            'css_vars': {}
        },
        'auto': {
            'name': 'Auto',
            'class': 'auto',
            'icon': 'refresh',
            'description': 'Automatically switches based on time',
            'css_vars': {}
        }
    }
    
    @staticmethod
    def get_current_theme():
        """Get current theme from session or default"""
        return session.get('theme', 'light')
    
    @staticmethod
    def set_theme(theme):
        """Set theme in session"""
        if theme in ThemeManager.THEMES:
            session['theme'] = theme
            return True
        return False
    
    @staticmethod
    def get_theme_class():
        """Get CSS class for current theme"""
        theme = ThemeManager.get_current_theme()
        return ThemeManager.THEMES[theme]['class']
    
    @staticmethod
    def get_available_themes():
        """Get list of available themes"""
        return ThemeManager.THEMES
    
    @staticmethod
    def get_theme_css_vars():
        """Get CSS variables for current theme"""
        theme = ThemeManager.get_current_theme()
        theme_config = ThemeManager.THEMES[theme]
        
        if theme == 'system':
            # Use system preference
            prefers_dark = request.headers.get('Sec-CH-Prefers-Color-Scheme') == 'dark'
            base_theme = 'dark' if prefers_dark else 'light'
            return ThemeManager.THEMES[base_theme]['css_vars']
        elif theme == 'auto':
            # Check time of day
            from datetime import datetime
            hour = datetime.now().hour
            base_theme = 'dark' if (hour < 6 or hour > 18) else 'light'
            return ThemeManager.THEMES[base_theme]['css_vars']
        else:
            return theme_config['css_vars']
    
    @staticmethod
    def is_dark_mode():
        """Check if current theme is dark mode"""
        theme = ThemeManager.get_current_theme()
        if theme == 'system':
            # Check system preference
            return request.headers.get('Sec-CH-Prefers-Color-Scheme') == 'dark'
        elif theme == 'auto':
            # Check time of day
            from datetime import datetime
            hour = datetime.now().hour
            return hour < 6 or hour > 18
        else:
            return theme in ['dark', 'dracula', 'high-contrast']
    
    @staticmethod
    def get_theme_preview_colors(theme_name):
        """Get preview colors for theme selection"""
        if theme_name in ThemeManager.THEMES:
            return ThemeManager.THEMES[theme_name]['css_vars']
        return {}

    @staticmethod
    def render_theme_css():
        """Render theme CSS variables as style tag"""
        css_vars = ThemeManager.get_theme_css_vars()
        if not css_vars:
            return ""

        css_lines = []
        for var_name, var_value in css_vars.items():
            css_lines.append(f"    {var_name}: {var_value};")

        css_content = "\n".join(css_lines)
        return f"<style>\n:root {{\n{css_content}\n}}</style>"

    @staticmethod
    def get_theme_css_variables():
        """Get CSS variables as string for inline styles"""
        css_vars = ThemeManager.get_theme_css_vars()
        if not css_vars:
            return ""

        css_lines = []
        for var_name, var_value in css_vars.items():
            css_lines.append(f"{var_name}: {var_value};")

        return "\n".join(css_lines)

# Theme context processor
def theme_context_processor():
    """Add theme information to template context"""
    return {
        'current_theme': ThemeManager.get_current_theme(),
        'theme_class': ThemeManager.get_theme_class(),
        'is_dark_mode': ThemeManager.is_dark_mode(),
        'available_themes': ThemeManager.get_available_themes(),
        'theme_css_vars': ThemeManager.get_theme_css_vars()
    }
