"""
Template Integration for ValidoAI Application
Copies and integrates templates from templates-valido-original/ to templates/
"""

import os
import shutil
import logging
from pathlib import Path
from flask import current_app

logger = logging.getLogger(__name__)

class TemplateIntegrator:
    """Handles template integration and management"""
    
    def __init__(self, app=None):
        self.app = app
        self.source_dir = 'templates-valido-original'
        self.target_dir = 'templates'
        self.integrated_templates = []
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize the template integrator with Flask app"""
        self.app = app
        
        # Register template integration with app context
        with app.app_context():
            self.setup_template_integration()
    
    def setup_template_integration(self):
        """Setup template integration"""
        try:
            # Ensure target directory exists
            target_path = Path(self.target_dir)
            target_path.mkdir(exist_ok=True)
            
            # Copy templates from original directory
            self.copy_templates()
            
            # Update template references
            self.update_template_references()
            
            # Register template routes
            self.register_template_routes()
            
            logger.info("Template integration completed successfully")
            
        except Exception as e:
            logger.error(f"Template integration failed: {e}")
    
    def copy_templates(self):
        """Copy templates from templates-valido-original/ to templates/"""
        try:
            source_path = Path(self.source_dir)
            target_path = Path(self.target_dir)
            
            if not source_path.exists():
                logger.warning(f"Source directory {self.source_dir} does not exist")
                return
            
            # Copy all files from source to target
            for item in source_path.rglob('*'):
                if item.is_file():
                    # Calculate relative path
                    relative_path = item.relative_to(source_path)
                    target_file = target_path / relative_path
                    
                    # Create target directory if it doesn't exist
                    target_file.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Copy file
                    shutil.copy2(item, target_file)
                    self.integrated_templates.append(str(relative_path))
                    
                    logger.info(f"Copied template: {relative_path}")
            
            logger.info(f"Copied {len(self.integrated_templates)} templates")
            
        except Exception as e:
            logger.error(f"Error copying templates: {e}")
    
    def update_template_references(self):
        """Update template references in routes and views"""
        try:
            # Update route references to use integrated templates
            template_mappings = {
                'ai_sveska.html': 'ai/ai_sveska.html',
                'analiza_plata.html': 'analytics/analiza_plata.html',
                'analiza.html': 'analytics/analiza.html',
                'funkcionalnosti.html': 'features/funkcionalnosti.html',
                'index.html': 'main/index.html',
                'pdv.html': 'financial/pdv.html',
                'poreski_chat.html': 'chat/poreski_chat.html'
            }
            
            # Update the template mappings in the app context
            if hasattr(current_app, 'template_mappings'):
                current_app.template_mappings.update(template_mappings)
            else:
                current_app.template_mappings = template_mappings
            
            logger.info("Template references updated")
            
        except Exception as e:
            logger.error(f"Error updating template references: {e}")
    
    def register_template_routes(self):
        """Register routes for integrated templates"""
        try:
            from flask import Blueprint, render_template
            
            # Create blueprint for integrated templates
            integrated_bp = Blueprint('integrated', __name__, url_prefix='/integrated')
            
            # Register routes for each integrated template
            template_routes = {
                'ai_sveska': 'ai/ai_sveska.html',
                'analiza_plata': 'analytics/analiza_plata.html',
                'analiza': 'analytics/analiza.html',
                'funkcionalnosti': 'features/funkcionalnosti.html',
                'pdv': 'financial/pdv.html',
                'poreski_chat': 'chat/poreski_chat.html'
            }
            
            for route_name, template_path in template_routes.items():
                @integrated_bp.route(f'/{route_name}')
                def template_route(template=template_path):
                    return render_template(template)
            
            # Register blueprint with app
            if self.app:
                self.app.register_blueprint(integrated_bp)
            
            logger.info("Integrated template routes registered")
            
        except Exception as e:
            logger.error(f"Error registering template routes: {e}")
    
    def get_integrated_templates(self):
        """Get list of integrated templates"""
        return self.integrated_templates
    
    def validate_templates(self):
        """Validate that all templates are properly integrated"""
        try:
            missing_templates = []
            
            for template in self.integrated_templates:
                template_path = Path(self.target_dir) / template
                if not template_path.exists():
                    missing_templates.append(template)
            
            if missing_templates:
                logger.warning(f"Missing templates: {missing_templates}")
                return False
            
            logger.info("All templates validated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Template validation failed: {e}")
            return False
    
    def create_template_index(self):
        """Create an index of all integrated templates"""
        try:
            index_content = """# ValidoAI Integrated Templates

This file contains an index of all integrated templates from `templates-valido-original/`.

## Template Structure

```
templates/
├── ai/
│   └── ai_sveska.html
├── analytics/
│   ├── analiza.html
│   └── analiza_plata.html
├── chat/
│   └── poreski_chat.html
├── features/
│   └── funkcionalnosti.html
├── financial/
│   └── pdv.html
└── main/
    └── index.html
```

## Available Templates

"""
            
            for template in sorted(self.integrated_templates):
                index_content += f"- `{template}`\n"
            
            # Write index file
            index_path = Path(self.target_dir) / 'TEMPLATE_INDEX.md'
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write(index_content)
            
            logger.info("Template index created")
            
        except Exception as e:
            logger.error(f"Error creating template index: {e}")

def integrate_templates(app):
    """Main function to integrate templates"""
    integrator = TemplateIntegrator(app)
    return integrator

# Template route handlers
def create_template_routes(app):
    """Create routes for integrated templates"""
    
    @app.route('/ai-sveska')
    def ai_sveska():
        """AI Notebook page"""
        return render_template('ai/ai_sveska.html')
    
    @app.route('/analiza-plata')
    def analiza_plata():
        """Salary Analysis page"""
        return render_template('analytics/analiza_plata.html')
    
    @app.route('/analiza')
    def analiza():
        """Financial Analysis page"""
        return render_template('analytics/analiza.html')
    
    @app.route('/funkcionalnosti')
    def funkcionalnosti():
        """Features page"""
        return render_template('features/funkcionalnosti.html')
    
    @app.route('/pdv')
    def pdv():
        """VAT Calculator page"""
        return render_template('financial/pdv.html')
    
    @app.route('/poreski-chat')
    def poreski_chat():
        """Tax Chat page"""
        return render_template('chat/poreski_chat.html')
    
    @app.route('/integrated-templates')
    def integrated_templates_index():
        """Index of integrated templates"""
        integrator = TemplateIntegrator()
        templates = integrator.get_integrated_templates()
        return {
            'status': 'success',
            'data': {
                'templates': templates,
                'count': len(templates),
                'source_directory': integrator.source_dir,
                'target_directory': integrator.target_dir
            }
        }

# Template enhancement functions
def enhance_template_with_navigation(template_content):
    """Enhance template with navigation menu"""
    try:
        # Add navigation include
        if '{% include' not in template_content:
            nav_include = '{% include "components/full_navigation_menu.html" %}'
            # Insert after <body> tag
            if '<body' in template_content:
                body_pos = template_content.find('<body')
                body_end = template_content.find('>', body_pos) + 1
                template_content = template_content[:body_end] + '\n    ' + nav_include + '\n' + template_content[body_end:]
        
        return template_content
        
    except Exception as e:
        logger.error(f"Error enhancing template: {e}")
        return template_content

def enhance_template_with_colors(template_content):
    """Enhance template with HSL color system"""
    try:
        # Add CSS variables for HSL colors
        css_variables = """
<style>
:root {
    /* HSL Color System */
    --color-navy-h: 223;
    --color-navy-s: 53%;
    --color-navy-l: 22%;
    --color-navy: hsl(var(--color-navy-h), var(--color-navy-s), var(--color-navy-l));
    --color-navy-alpha: hsla(var(--color-navy-h), var(--color-navy-s), var(--color-navy-l), 0.1);
    
    --color-trust-h: 225;
    --color-trust-s: 58%;
    --color-trust-l: 51%;
    --color-trust: hsl(var(--color-trust-h), var(--color-trust-s), var(--color-trust-l));
    --color-trust-alpha: hsla(var(--color-trust-h), var(--color-trust-s), var(--color-trust-l), 0.1);
    
    --color-professional-h: 225;
    --color-professional-s: 75%;
    --color-professional-l: 63%;
    --color-professional: hsl(var(--color-professional-h), var(--color-professional-s), var(--color-professional-l));
    
    --color-vibrant-h: 180;
    --color-vibrant-s: 85%;
    --color-vibrant-l: 55%;
    --color-vibrant: hsl(var(--color-vibrant-h), var(--color-vibrant-s), var(--color-vibrant-l));
    --color-vibrant-alpha: hsla(var(--color-vibrant-h), var(--color-vibrant-s), var(--color-vibrant-l), 0.1);
}
</style>
"""
        
        # Insert CSS variables in head section
        if '<head' in template_content:
            head_pos = template_content.find('<head')
            head_end = template_content.find('>', head_pos) + 1
            template_content = template_content[:head_end] + '\n' + css_variables + template_content[head_end:]
        
        return template_content
        
    except Exception as e:
        logger.error(f"Error enhancing template with colors: {e}")
        return template_content

def enhance_all_templates():
    """Enhance all integrated templates"""
    try:
        integrator = TemplateIntegrator()
        target_path = Path(integrator.target_dir)
        
        for template_file in target_path.rglob('*.html'):
            with open(template_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Enhance template
            content = enhance_template_with_navigation(content)
            content = enhance_template_with_colors(content)
            
            # Write enhanced template
            with open(template_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Enhanced template: {template_file}")
        
        logger.info("All templates enhanced successfully")
        
    except Exception as e:
        logger.error(f"Error enhancing templates: {e}")

# Utility functions
def get_template_info(template_name):
    """Get information about a specific template"""
    try:
        template_path = Path('templates') / template_name
        
        if not template_path.exists():
            return {'error': 'Template not found'}
        
        # Get template statistics
        stat = template_path.stat()
        
        return {
            'name': template_name,
            'path': str(template_path),
            'size': stat.st_size,
            'modified': stat.st_mtime,
            'exists': True
        }
        
    except Exception as e:
        logger.error(f"Error getting template info: {e}")
        return {'error': str(e)}

def list_all_templates():
    """List all available templates"""
    try:
        templates = []
        template_path = Path('templates')
        
        if template_path.exists():
            for template_file in template_path.rglob('*.html'):
                relative_path = template_file.relative_to(template_path)
                templates.append(str(relative_path))
        
        return sorted(templates)
        
    except Exception as e:
        logger.error(f"Error listing templates: {e}")
        return []
