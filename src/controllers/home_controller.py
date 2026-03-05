import logging
from flask import render_template

from src.models.example_page import ExamplePage  # reuse model for demo content
from src.factories.viewmodel_factory import viewmodel_factory

logger = logging.getLogger(__name__)

class HomeController:
    """Controller for the landing page (/)"""

    @staticmethod
    def index():
        try:
            # Make sure we have at least one page for demo list
            ExamplePage.seed_demo()  # type: ignore
            # Build simple list of pages for navigation using factory
            pages_vm = [viewmodel_factory.build(page) for page in ExamplePage.query.all()]  # type: ignore
        except Exception as e:
            logger.warning(f"Could not load example pages: {e}")
            pages_vm = []
        
        # Provide dashboard_data for the template
        dashboard_data = {
            'notifications': [],
            'recent_activities': [],
            'stats': {
                'total_users': 0,
                'total_projects': 0,
                'total_sales': 0,
                'total_revenue': 0
            }
        }
        
        return render_template('dashboard/index.html', 
                             pages=pages_vm, 
                             dashboard_data=dashboard_data)
