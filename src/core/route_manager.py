"""
Route Manager
============

Manages application routes and navigation menu structure.
"""

class RouteManager:
    """Manages application routes and menu generation"""

    def __init__(self):
        """Initialize route manager with menu structure"""
        self.menu_routes = [
            {
                'path': '/',
                'menu_title': 'Dashboard',
                'icon': 'fas fa-tachometer-alt',
                'category': 'main',
                'order': 1
            },
            {
                'path': '/dashboard',
                'menu_title': 'Dashboard',
                'icon': 'fas fa-tachometer-alt',
                'category': 'main',
                'order': 1
            },
            {
                'path': '/dashboard/business-intelligence',
                'menu_title': 'Business Intelligence',
                'icon': 'fas fa-chart-bar',
                'category': 'analytics',
                'order': 2,
                'endpoint': 'main.business_intelligence_dashboard'
            },
            {
                'path': '/dashboard/predictive-analytics',
                'menu_title': 'Predictive Analytics',
                'icon': 'fas fa-brain',
                'category': 'analytics',
                'order': 3,
                'endpoint': 'main.predictive_analytics_dashboard'
            },
            # Sentiment Analysis route not yet implemented
            # {
            #     'path': '/ai/sentiment-analysis',
            #     'menu_title': 'Sentiment Analysis',
            #     'icon': 'fas fa-heart',
            #     'category': 'ai',
            #     'order': 4
            # },
            {
                'path': '/content/management',
                'menu_title': 'Content Management',
                'icon': 'fas fa-folder',
                'category': 'content',
                'order': 5
            },
            {
                'path': '/chat',
                'menu_title': 'AI Chat',
                'icon': 'fas fa-comments',
                'category': 'ai',
                'order': 6
            },
            {
                'path': '/settings',
                'menu_title': 'Settings',
                'icon': 'fas fa-cog',
                'category': 'system',
                'order': 10
            }
        ]

    def get_menu_routes(self):
        """Get all menu routes sorted by order"""
        return sorted(self.menu_routes, key=lambda x: x['order'])

    def get_routes_by_category(self, category):
        """Get routes filtered by category"""
        return [route for route in self.menu_routes if route['category'] == category]

    def add_route(self, path, menu_title, icon='fas fa-link', category='other', order=99):
        """Add a new route to the menu"""
        self.menu_routes.append({
            'path': path,
            'menu_title': menu_title,
            'icon': icon,
            'category': category,
            'order': order
        })

    def remove_route(self, path):
        """Remove a route from the menu"""
        self.menu_routes = [route for route in self.menu_routes if route['path'] != path]

    def get_route_by_path(self, path):
        """Get a specific route by path"""
        for route in self.menu_routes:
            if route['path'] == path:
                return route
        return None

    def get_categories(self):
        """Get all unique categories"""
        return list(set(route['category'] for route in self.menu_routes))
