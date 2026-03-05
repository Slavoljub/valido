"""
Dynamic Menu Generator for ValidoAI
Reads routes from routes.py and generates sidebar menus
"""

import re
import inspect
from typing import List, Dict, Any, Optional
from pathlib import Path
import importlib.util


class MenuGenerator:
    """Generates dynamic menus from routes.py file"""
    
    def __init__(self, routes_file_path: str = "routes.py"):
        self.routes_file_path = routes_file_path
        self.routes_cache = None
        self.menu_cache = None
    
    def read_routes_file(self) -> str:
        """Read the routes.py file content"""
        try:
            with open(self.routes_file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            print(f"Warning: {self.routes_file_path} not found")
            return ""
        except Exception as e:
            print(f"Error reading routes file: {e}")
            return ""
    
    def extract_routes(self) -> List[Dict[str, Any]]:
        """Extract routes from routes.py file"""
        if self.routes_cache is not None:
            return self.routes_cache
            
        content = self.read_routes_file()
        routes = []
        
        # Pattern to match Flask routes (including blueprint routes)
        route_pattern = r'@(?:app|blueprint|[a-zA-Z_][a-zA-Z0-9_]*_bp)\.route\([\'"`]([^\'"`]+)[\'"`](?:,\s*methods=\[([^\]]+)\])?\)'
        
        # Pattern to match route function definitions
        func_pattern = r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\([^)]*\):'
        
        lines = content.split('\n')
        current_route = None
        
        for i, line in enumerate(lines):
            # Check for route decorator
            route_match = re.search(route_pattern, line.strip())
            if route_match:
                path = route_match.group(1)
                methods = route_match.group(2) if route_match.group(2) else "['GET']"
                
                # Skip API routes
                if path.startswith('/api/'):
                    continue
                
                # Skip error routes
                if path.startswith('/error'):
                    continue
                
                current_route = {
                    'path': path,
                    'methods': methods,
                    'function_name': None,
                    'title': self.generate_title_from_path(path),
                    'icon': self.get_icon_for_path(path),
                    'category': self.categorize_route(path)
                }
            
            # Check for function definition
            elif current_route and re.search(func_pattern, line.strip()):
                func_match = re.search(func_pattern, line.strip())
                current_route['function_name'] = func_match.group(1)
                routes.append(current_route)
                current_route = None
        
        # Remove duplicates and filter routes
        unique_routes = []
        seen_paths = set()
        
        for route in routes:
            # Clean path by removing GET parameters for deduplication
            clean_path = route['path'].split('?')[0]
            
            # Skip routes that don't meet pretty URL standards
            if (clean_path.startswith('/api/') or 
                clean_path.startswith('/notifications/api/') or
                clean_path.startswith('/llm/') or
                clean_path.startswith('/ticket/') or
                clean_path.startswith('/settings/') or
                clean_path.startswith('/chat/') or
                '?' in route['path'] or
                clean_path in seen_paths or
                '<' in route['path'] or  # Skip routes with path parameters
                '>' in route['path'] or  # Skip routes with path parameters
                clean_path.startswith('/error') or  # Skip error routes
                clean_path.startswith('/htmx/') or  # Skip HTMX routes
                clean_path.startswith('/static/') or  # Skip static routes
                clean_path.startswith('/uploads/') or  # Skip upload routes
                clean_path.startswith('/cache/') or  # Skip cache routes
                clean_path.startswith('/logs/') or  # Skip log routes
                clean_path.startswith('/data/') or  # Skip data routes
                clean_path.startswith('/models/') or  # Skip model routes
                clean_path.startswith('/local_llm_models/') or  # Skip model routes
                clean_path.startswith('/venv/') or  # Skip virtual environment
                clean_path.startswith('/env') or  # Skip environment files
                clean_path.startswith('/.') or  # Skip hidden files
                any(param in route['path'] for param in ['<int:', '<str:', '<uuid:', '<path:', '<float:', '<any:']) or  # Skip parameterized routes
                any(skip in route['path'] for skip in ['/test', '/debug', '/admin', '/internal', '/system', '/config', '/backup', '/temp', '/tmp']) or  # Skip internal routes
                len(clean_path.split('/')) > 3):  # Skip deeply nested routes
                continue
            
            # Only include GET routes in the menu
            if route.get('methods') and 'GET' in route['methods']:
                # Additional validation for clean URLs
                if (clean_path.startswith('/') and 
                    not clean_path.endswith('/') and 
                    clean_path != '/' and
                    all(char.isalnum() or char in '-_' for char in clean_path[1:].replace('/', ''))):
                    unique_routes.append(route)
                    seen_paths.add(clean_path)
        
        self.routes_cache = unique_routes
        return unique_routes
    
    def generate_title_from_path(self, path: str) -> str:
        """Generate a human-readable title from route path"""
        if path == '/':
            return 'Home'
        
        # Remove leading slash and split
        parts = path.strip('/').split('/')
        
        # Handle special cases
        if len(parts) == 1:
            if parts[0] == 'dashboard':
                return 'Dashboard'
            elif parts[0] == 'settings':
                return 'Settings'
            elif parts[0] == 'profile':
                return 'Profile'
            elif parts[0] == 'chat-local':
                return 'Local Chat'
            elif parts[0] == 'chat-external':
                return 'External Chat'
            elif parts[0] == 'ticketing':
                return 'Ticketing'
            elif parts[0] == 'ml-alg-demo':
                return 'ML Algorithms'
            else:
                return parts[0].replace('-', ' ').title()
        
        # Handle nested routes
        if len(parts) == 2:
            if parts[0] == 'dashboard':
                return f'Dashboard - {parts[1].replace("-", " ").title()}'
            elif parts[0] == 'settings':
                return f'Settings - {parts[1].replace("-", " ").title()}'
            elif parts[0] == 'ticketing':
                return f'Ticketing - {parts[1].replace("-", " ").title()}'
            else:
                return f'{parts[0].replace("-", " ").title()} - {parts[1].replace("-", " ").title()}'
        
        return path.replace('-', ' ').title()
    
    def get_icon_for_path(self, path: str) -> str:
        """Get appropriate icon for route path"""
        path_lower = path.lower()
        
        # Dashboard icons
        if 'dashboard' in path_lower:
            return 'fas fa-chart-line'
        elif path == '/':
            return 'fas fa-home'
        elif 'settings' in path_lower:
            return 'fas fa-cog'
        elif 'profile' in path_lower:
            return 'fas fa-user'
        elif 'chat' in path_lower:
            return 'fas fa-comments'
        elif 'ticketing' in path_lower or 'ticket' in path_lower:
            return 'fas fa-ticket-alt'
        elif 'ml-alg' in path_lower or 'algorithm' in path_lower:
            return 'fas fa-brain'
        elif 'auth' in path_lower or 'login' in path_lower:
            return 'fas fa-sign-in-alt'
        elif 'register' in path_lower:
            return 'fas fa-user-plus'
        elif 'logout' in path_lower:
            return 'fas fa-sign-out-alt'
        elif 'example' in path_lower:
            return 'fas fa-file-alt'
        elif 'test' in path_lower:
            return 'fas fa-vial'
        else:
            return 'fas fa-link'
    
    def categorize_route(self, path: str) -> str:
        """Categorize route into menu sections"""
        path_lower = path.lower()
        
        if path == '/':
            return 'main'
        elif 'dashboard' in path_lower:
            return 'dashboard'
        elif 'settings' in path_lower:
            return 'settings'
        elif 'chat' in path_lower:
            return 'ai'
        elif 'ml-alg' in path_lower or 'algorithm' in path_lower:
            return 'ai'
        elif 'ticketing' in path_lower or 'ticket' in path_lower:
            return 'support'
        elif 'auth' in path_lower or 'login' in path_lower or 'register' in path_lower:
            return 'auth'
        elif 'example' in path_lower or 'test' in path_lower:
            return 'development'
        # Database structure routes
        elif any(x in path_lower for x in ['companies', 'partners', 'users', 'fiscal-years', 'charts-of-accounts', 'general-ledger']):
            return 'finance'
        elif any(x in path_lower for x in ['invoices', 'bank', 'fixed-assets', 'budgets', 'taxes']):
            return 'accounting'
        elif any(x in path_lower for x in ['inventory', 'warehouses']):
            return 'inventory'
        elif any(x in path_lower for x in ['crm-', 'leads', 'opportunities']):
            return 'crm'
        elif any(x in path_lower for x in ['employees', 'payrolls']):
            return 'hr'
        elif any(x in path_lower for x in ['email-', 'erp-modules', 'routes-permissions', 'audit-logs', 'demo-logs', 'llm-embeddings']):
            return 'system'
        else:
            return 'other'
    
    def generate_main_menu(self) -> List[Dict[str, Any]]:
        """Generate main menu structure"""
        if self.menu_cache is not None:
            return self.menu_cache

        routes = self.extract_routes()
        menu = []

        # Group routes by category
        categories = {}
        for route in routes:
            category = route['category']
            if category not in categories:
                categories[category] = []
            categories[category].append(route)

        # Add predefined routes for certain categories
        predefined_routes = {
            'ai': [
                {'path': '/chat', 'title': 'AI Chat Assistant', 'icon': 'fas fa-comments', 'description': 'Advanced AI-powered business assistant'},
                {'path': '/ai-models', 'title': 'AI Models', 'icon': 'fas fa-robot', 'description': 'Manage AI models and configurations'},
                {'path': '/ml-demo', 'title': 'ML Demo', 'icon': 'fas fa-magic', 'description': 'Machine learning demonstrations'}
            ]
        }

        # Add predefined routes to their categories
        for category, routes_list in predefined_routes.items():
            if category not in categories:
                categories[category] = []
            # Add predefined routes that aren't already in the category
            existing_paths = {route.get('path', '') for route in categories[category]}
            for predefined_route in routes_list:
                if predefined_route['path'] not in existing_paths:
                    categories[category].append(predefined_route)
        
        # Create menu structure
        category_config = {
            'main': {'title': 'Main', 'icon': 'fas fa-home', 'order': 1},
            'dashboard': {'title': 'Dashboard', 'icon': 'fas fa-chart-line', 'order': 2},
            'ai': {'title': 'AI & ML', 'icon': 'fas fa-brain', 'order': 3, 'routes': [
                {'path': '/chat', 'title': 'AI Chat Assistant', 'icon': 'fas fa-comments', 'description': 'Advanced AI-powered business assistant'},
                {'path': '/ai-models', 'title': 'AI Models', 'icon': 'fas fa-robot', 'description': 'Manage AI models and configurations'},
                {'path': '/ml-demo', 'title': 'ML Demo', 'icon': 'fas fa-magic', 'description': 'Machine learning demonstrations'}
            ]},
            'finance': {'title': 'Finance', 'icon': 'fas fa-dollar-sign', 'order': 4},
            'accounting': {'title': 'Accounting', 'icon': 'fas fa-calculator', 'order': 5},
            'inventory': {'title': 'Inventory', 'icon': 'fas fa-boxes', 'order': 6},
            'crm': {'title': 'CRM', 'icon': 'fas fa-users', 'order': 7},
            'hr': {'title': 'HR', 'icon': 'fas fa-user-tie', 'order': 8},
            'system': {'title': 'System', 'icon': 'fas fa-server', 'order': 9},
            'settings': {'title': 'Settings', 'icon': 'fas fa-cog', 'order': 10},
            'support': {'title': 'Support', 'icon': 'fas fa-headset', 'order': 11},
            'auth': {'title': 'Authentication', 'icon': 'fas fa-user-shield', 'order': 12},
            'development': {'title': 'Development', 'icon': 'fas fa-code', 'order': 13},
            'other': {'title': 'Other', 'icon': 'fas fa-ellipsis-h', 'order': 14}
        }
        
        # Sort categories by order
        sorted_categories = sorted(categories.items(), key=lambda x: category_config.get(x[0], {}).get('order', 999))
        
        for category, category_routes in sorted_categories:
            if not category_routes:
                continue
                
            config = category_config.get(category, {})
            menu.append({
                'category': category,
                'title': config.get('title', category.title()),
                'icon': config.get('icon', 'fas fa-folder'),
                'routes': sorted(category_routes, key=lambda x: x['path'])
            })
        
        self.menu_cache = menu
        return menu
    
    def generate_sidebar_menu(self) -> List[Dict[str, Any]]:
        """Generate sidebar menu HTML structure"""
        menu = self.generate_main_menu()
        return menu


# Global instance
menu_generator = MenuGenerator()


def main_menu_sidebar() -> List[Dict[str, Any]]:
    """Get main menu for sidebar"""
    return menu_generator.generate_sidebar_menu()


def main_menu() -> List[Dict[str, Any]]:
    """Get main menu structure"""
    return menu_generator.generate_main_menu()


def get_routes() -> List[Dict[str, Any]]:
    """Get all routes"""
    return menu_generator.extract_routes()


def clear_cache():
    """Clear menu and routes cache"""
    menu_generator.routes_cache = None
    menu_generator.menu_cache = None

# Clear cache on import to ensure fresh data
if __name__ == "__main__":
    clear_cache()
