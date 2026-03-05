"""
Component-Based CSS Architecture for ValidoAI
Implements modular CSS loading and component-specific styles
"""

import os
import json
from typing import Dict, List, Set
from pathlib import Path
from flask import current_app

class ComponentCSSLoader:
    """Manages component-based CSS loading and organization"""

    def __init__(self, static_folder: str = "static"):
        self.static_folder = Path(static_folder)
        self.component_registry: Dict[str, Dict] = {}
        self.loaded_components: Set[str] = set()
        self._load_component_registry()

    def _load_component_registry(self):
        """Load component registry from JSON file"""
        registry_path = self.static_folder / "css" / "component-registry.json"
        if registry_path.exists():
            with open(registry_path, 'r') as f:
                self.component_registry = json.load(f)
        else:
            # Default component registry
            self.component_registry = {
                "dashboard": {
                    "css": ["css/dashboard.css"],
                    "dependencies": ["base", "animations"],
                    "critical": True
                },
                "charts": {
                    "css": ["css/charts.css"],
                    "dependencies": ["base"],
                    "critical": False
                },
                "forms": {
                    "css": ["css/forms.css"],
                    "dependencies": ["base"],
                    "critical": True
                },
                "tables": {
                    "css": ["css/tables.css"],
                    "dependencies": ["base"],
                    "critical": False
                },
                "modals": {
                    "css": ["css/modals.css"],
                    "dependencies": ["base", "animations"],
                    "critical": False
                },
                "notifications": {
                    "css": ["css/notifications.css"],
                    "dependencies": ["base", "animations"],
                    "critical": True
                },
                "widgets": {
                    "css": ["css/widgets.css"],
                    "dependencies": ["base", "charts"],
                    "critical": False
                },
                "animations": {
                    "css": ["css/animations.css"],
                    "dependencies": [],
                    "critical": True
                },
                "base": {
                    "css": ["css/base.css"],
                    "dependencies": [],
                    "critical": True
                }
            }

    def get_component_css(self, component_name: str) -> str:
        """Get CSS content for a specific component"""
        if component_name not in self.component_registry:
            return ""

        component = self.component_registry[component_name]
        css_files = component.get("css", [])
        css_content = []

        for css_file in css_files:
            file_path = self.static_folder / css_file
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    css_content.append(f.read())

        return "\n".join(css_content)

    def get_component_dependencies(self, component_name: str) -> List[str]:
        """Get all dependencies for a component (including nested dependencies)"""
        if component_name not in self.component_registry:
            return []

        component = self.component_registry[component_name]
        dependencies = component.get("dependencies", [])
        all_deps = set(dependencies)

        # Recursively get dependencies
        for dep in dependencies:
            all_deps.update(self.get_component_dependencies(dep))

        # Remove the component itself from dependencies
        all_deps.discard(component_name)

        return list(all_deps)

    def generate_component_css_links(self, components: List[str], strategy: str = "deferred") -> List[str]:
        """Generate CSS links for components based on loading strategy"""
        links = []

        if strategy == "critical":
            # Inline critical CSS
            for component in components:
                if self.is_component_critical(component):
                    css_content = self.get_component_css(component)
                    if css_content:
                        links.append(f'<style data-component="{component}">{css_content}</style>')

        elif strategy == "deferred":
            # Use preload with deferred loading
            for component in components:
                component_deps = self.get_component_dependencies(component)
                all_components = component_deps + [component]

                for comp in all_components:
                    if comp in self.component_registry:
                        for css_file in self.component_registry[comp]["css"]:
                            if self._file_exists(css_file):
                                links.append(f'<link rel="preload" href="/static/{css_file}" as="style" onload="this.onload=null;this.rel=\'stylesheet\'" data-component="{comp}">')
                                links.append(f'<noscript><link rel="stylesheet" href="/static/{css_file}"></noscript>')

        elif strategy == "lazy":
            # Load on demand
            for component in components:
                component_deps = self.get_component_dependencies(component)
                all_components = component_deps + [component]

                for comp in all_components:
                    if comp in self.component_registry:
                        for css_file in self.component_registry[comp]["css"]:
                            if self._file_exists(css_file):
                                links.append(f'<link rel="lazy-stylesheet" href="/static/{css_file}" data-component="{comp}">')

        return links

    def is_component_critical(self, component_name: str) -> bool:
        """Check if a component is marked as critical"""
        return self.component_registry.get(component_name, {}).get("critical", False)

    def get_critical_components(self, components: List[str]) -> List[str]:
        """Get critical components from a list"""
        return [comp for comp in components if self.is_component_critical(comp)]

    def get_deferred_components(self, components: List[str]) -> List[str]:
        """Get deferred components from a list"""
        return [comp for comp in components if not self.is_component_critical(comp)]

    def _file_exists(self, file_path: str) -> bool:
        """Check if a CSS file exists"""
        return (self.static_folder / file_path).exists()

    def optimize_component_loading(self, components: List[str], strategy: str = "hybrid") -> Dict[str, List[str]]:
        """Optimize component loading based on strategy"""
        if strategy == "hybrid":
            # Critical components inlined, others deferred
            critical = self.get_critical_components(components)
            deferred = self.get_deferred_components(components)

            return {
                "critical": [f'<style data-component="{comp}">{self.get_component_css(comp)}</style>' for comp in critical if self.get_component_css(comp)],
                "deferred": self.generate_component_css_links(deferred, "deferred"),
                "lazy": []
            }
        elif strategy == "all-deferred":
            return {
                "critical": [],
                "deferred": self.generate_component_css_links(components, "deferred"),
                "lazy": []
            }
        else:
            return {
                "critical": self.generate_component_css_links(components, "critical"),
                "deferred": [],
                "lazy": []
            }

    def generate_component_js_loader(self, components: List[str]) -> str:
        """Generate JavaScript for lazy loading CSS components"""
        js_code = """
        // Component CSS Lazy Loader
        class ComponentCSSLoader {
            constructor() {
                this.loadedComponents = new Set();
                this.loadingComponents = new Set();
            }

            loadComponent(componentName) {
                if (this.loadedComponents.has(componentName) || this.loadingComponents.has(componentName)) {
                    return Promise.resolve();
                }

                this.loadingComponents.add(componentName);

                return new Promise((resolve, reject) => {
                    const link = document.createElement('link');
                    link.rel = 'stylesheet';
                    link.href = `/static/css/${componentName}.css`;
                    link.dataset.component = componentName;

                    link.onload = () => {
                        this.loadedComponents.add(componentName);
                        this.loadingComponents.delete(componentName);
                        resolve();
                    };

                    link.onerror = () => {
                        this.loadingComponents.delete(componentName);
                        reject(new Error(`Failed to load CSS for component: ${componentName}`));
                    };

                    document.head.appendChild(link);
                });
            }

            loadComponents(componentNames) {
                const promises = componentNames.map(name => this.loadComponent(name));
                return Promise.all(promises);
            }

            preloadComponent(componentName) {
                const link = document.createElement('link');
                link.rel = 'preload';
                link.href = `/static/css/${componentName}.css`;
                link.as = 'style';
                link.dataset.component = componentName;
                document.head.appendChild(link);
            }
        }

        // Global instance
        window.componentCSSLoader = new ComponentCSSLoader();
        """

        # Add component-specific loading logic
        for component in components:
            if not self.is_component_critical(component):
                js_code += f"""
                // Auto-load {component} component when needed
                document.addEventListener('component:{component}:needed', () => {{
                    window.componentCSSLoader.loadComponent('{component}');
                }});
                """

        return f'<script>{js_code}</script>'

    def create_component_css_file(self, component_name: str, css_content: str):
        """Create a CSS file for a component"""
        css_dir = self.static_folder / "css"
        css_dir.mkdir(exist_ok=True)

        file_path = css_dir / f"{component_name}.css"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(css_content)

        # Update registry
        if component_name not in self.component_registry:
            self.component_registry[component_name] = {
                "css": [f"css/{component_name}.css"],
                "dependencies": [],
                "critical": False
            }

        self._save_registry()

    def _save_registry(self):
        """Save component registry to file"""
        registry_path = self.static_folder / "css" / "component-registry.json"
        with open(registry_path, 'w', encoding='utf-8') as f:
            json.dump(self.component_registry, f, indent=2)


# Global instance
component_css_loader = ComponentCSSLoader()
