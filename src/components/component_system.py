"""
Component System Architecture for ValidoAI
Comprehensive component library with theme support
"""

from typing import Dict, List, Any, Optional, Callable
from flask import current_app, render_template_string, session, g
import os
import json
import logging

logger = logging.getLogger(__name__)

class ComponentRegistry:
    """Registry for all UI components"""

    def __init__(self):
        self.components: Dict[str, Dict[str, Any]] = {}
        self.categories: Dict[str, List[str]] = {}
        self.themes: Dict[str, Dict[str, Any]] = {}

    def register_component(self, name: str, component_type: str,
                         template_path: str, config: Dict[str, Any] = None):
        """Register a component"""
        self.components[name] = {
            'type': component_type,
            'template_path': template_path,
            'config': config or {},
            'dependencies': config.get('dependencies', []) if config else [],
            'version': config.get('version', '1.0.0') if config else '1.0.0',
            'author': config.get('author', 'ValidoAI') if config else 'ValidoAI',
            'description': config.get('description', '') if config else ''
        }

        if component_type not in self.categories:
            self.categories[component_type] = []
        if name not in self.categories[component_type]:
            self.categories[component_type].append(name)

    def get_component(self, name: str) -> Optional[Dict[str, Any]]:
        """Get component by name"""
        return self.components.get(name)

    def get_components_by_type(self, component_type: str) -> List[Dict[str, Any]]:
        """Get all components of a specific type"""
        component_names = self.categories.get(component_type, [])
        return [self.components[name] for name in component_names if name in self.components]

    def render_component(self, name: str, **context) -> str:
        """Render a component with context"""
        component = self.get_component(name)
        if not component:
            return f"<!-- Component '{name}' not found -->"

        try:
            # Add theme context
            context['theme'] = self.get_current_theme()
            context['component'] = component

            # Check if template file exists
            template_path = component['template_path']
            if os.path.exists(template_path):
                with open(template_path, 'r', encoding='utf-8') as f:
                    template_content = f.read()
                return render_template_string(template_content, **context)
            else:
                return f"<!-- Template not found: {template_path} -->"

        except Exception as e:
            logger.error(f"Error rendering component {name}: {e}")
            return f"<!-- Error rendering component {name}: {e} -->"

    def get_current_theme(self) -> Dict[str, Any]:
        """Get current theme settings"""
        theme_name = session.get('theme', 'light')
        return self.themes.get(theme_name, self.themes.get('light', {}))

    def set_theme(self, theme_name: str, theme_config: Dict[str, Any]):
        """Set theme configuration"""
        self.themes[theme_name] = theme_config

class ComponentBuilder:
    """Helper class to build common components"""

    def __init__(self, registry: ComponentRegistry):
        self.registry = registry

    def build_button_component(self, name: str, config: Dict[str, Any]):
        """Build button component"""
        template = f'''
        <button
            class="btn {config.get('variant', 'primary')} {config.get('size', 'md')}"
            type="{{{{ component.config.get('type', 'button') }}}}|safe"
            id="{{{{ component.config.get('id', '') }}}}|safe"
            name="{{{{ component.config.get('name', '') }}}}|safe"
            value="{{{{ component.config.get('value', '') }}}}|safe"
            disabled="{{{{ 'disabled' if component.config.get('disabled') else '' }}}}|safe"
            onclick="{{{{ component.config.get('onclick', '') }}}}|safe"
            :class="{{{{ component.config.get('class', '') }}}}|safe"
        >
            {{{{ component.config.get('icon', '') }}}}|safe
            {{{{ component.config.get('text', 'Button') }}}}|safe
        </button>
        '''
        self.registry.register_component(name, 'button', f'templates/components/{name}.html', config)

    def build_modal_component(self, name: str, config: Dict[str, Any]):
        """Build modal component"""
        template = f'''
        <div
            x-show="{config.get('show_var', 'showModal')}"
            x-cloak
            class="modal-overlay"
            @click="{config.get('close_on_overlay', True) and f'{config.get("show_var", "showModal")} = false' or ''}"
        >
            <div class="modal-content {{ config.get('size', 'md') }}" @click.stop>
                <div class="modal-header">
                    <h3 class="modal-title">{{{{ component.config.get('title', 'Modal Title') }}}}|safe</h3>
                    <button
                        type="button"
                        class="modal-close"
                        @click="{config.get('show_var', 'showModal')} = false"
                    >
                        ×
                    </button>
                </div>
                <div class="modal-body">
                    {{{{ component.config.get('content', '') }}}}|safe
                </div>
                <div class="modal-footer">
                    {{{{ component.config.get('footer', '') }}}}|safe
                </div>
            </div>
        </div>
        '''
        self.registry.register_component(name, 'modal', f'templates/components/{name}.html', config)

    def build_table_component(self, name: str, config: Dict[str, Any]):
        """Build table component"""
        template = f'''
        <div class="table-container">
            <table class="data-table {{ config.get('striped', True) and 'striped' or '' }}">
                <thead>
                    <tr>
                        {{{{ component.config.get('headers', '') }}}}|safe
                    </tr>
                </thead>
                <tbody>
                    {{{{ component.config.get('rows', '') }}}}|safe
                </tbody>
            </table>
        </div>
        '''
        self.registry.register_component(name, 'table', f'templates/components/{name}.html', config)

    def build_form_component(self, name: str, config: Dict[str, Any]):
        """Build form component"""
        template = f'''
        <form
            method="{{{{ component.config.get('method', 'POST') }}}}|safe"
            action="{{{{ component.config.get('action', '') }}}}|safe"
            enctype="{{{{ component.config.get('enctype', 'application/x-www-form-urlencoded') }}}}|safe"
            class="form {{ config.get('layout', 'vertical') }}"
            @submit="{{{{ component.config.get('onsubmit', '') }}}}|safe"
        >
            {{{{ component.config.get('fields', '') }}}}|safe
            <div class="form-actions">
                {{{{ component.config.get('actions', '') }}}}|safe
            </div>
        </form>
        '''
        self.registry.register_component(name, 'form', f'templates/components/{name}.html', config)

    def build_card_component(self, name: str, config: Dict[str, Any]):
        """Build card component"""
        template = f'''
        <div class="card {{ config.get('variant', 'default') }}">
            {{{{ component.config.get('header', '') }}}}|safe
            <div class="card-body">
                {{{{ component.config.get('content', '') }}}}|safe
            </div>
            {{{{ component.config.get('footer', '') }}}}|safe
        </div>
        '''
        self.registry.register_component(name, 'card', f'templates/components/{name}.html', config)

    def build_alert_component(self, name: str, config: Dict[str, Any]):
        """Build alert component"""
        template = f'''
        <div class="alert {{ config.get('type', 'info') }} {{ config.get('dismissible', True) and 'dismissible' or '' }}">
            {{{{ component.config.get('icon', '') }}}}|safe
            <div class="alert-content">
                <div class="alert-title">{{{{ component.config.get('title', '') }}}}|safe</div>
                <div class="alert-message">{{{{ component.config.get('message', '') }}}}|safe</div>
            </div>
            {{{{ component.config.get('dismissible', True) and '<button type="button" class="alert-close" onclick="this.parentElement.style.display=\'none\'">×</button>' or '' }}}}|safe
        </div>
        '''
        self.registry.register_component(name, 'alert', f'templates/components/{name}.html', config)

class AdvancedModalBuilder:
    """Builder for advanced modal with search, filter, pagination"""

    def __init__(self, registry: ComponentRegistry):
        self.registry = registry

    def build_advanced_crud_modal(self, name: str, config: Dict[str, Any]):
        """Build advanced CRUD modal with search, filter, pagination"""
        template = f'''
        <div
            x-show="{config.get('show_var', 'showAdvancedModal')}"
            x-cloak
            class="modal-overlay advanced-modal-overlay"
        >
            <div class="modal-content advanced-modal {{ config.get('size', 'xl') }}">
                <div class="modal-header">
                    <h3 class="modal-title">
                        {{{{ component.config.get('title', 'Advanced CRUD') }}}}|safe
                    </h3>
                    <div class="modal-controls">
                        <button
                            type="button"
                            class="btn btn-secondary btn-sm"
                            @click="{config.get('show_var', 'showAdvancedModal')} = false"
                        >
                            Close
                        </button>
                    </div>
                </div>

                <div class="modal-body">
                    <!-- Search and Filter Controls -->
                    <div class="modal-controls-section">
                        <div class="search-group">
                            <input
                                type="text"
                                class="form-control"
                                placeholder="Search..."
                                x-model="{config.get('search_var', 'searchQuery')}"
                                @input.debounce.300ms="{config.get('search_handler', 'searchData')}"
                            >
                        </div>

                        <div class="filter-group">
                            <select
                                class="form-control"
                                x-model="{config.get('filter_var', 'selectedFilter')}"
                                @change="{config.get('filter_handler', 'applyFilter')}"
                            >
                                <option value="">All Filters</option>
                                <template x-for="filter in {config.get('filter_options', 'filterOptions')}" :key="filter.value">
                                    <option :value="filter.value" x-text="filter.label"></option>
                                </template>
                            </select>
                        </div>

                        <div class="column-selector">
                            <button
                                type="button"
                                class="btn btn-outline btn-sm"
                                @click="{config.get('columns_var', 'showColumnSelector')} = true"
                            >
                                Columns
                            </button>
                        </div>
                    </div>

                    <!-- Column Selector Modal -->
                    <div
                        x-show="{config.get('columns_var', 'showColumnSelector')}"
                        x-cloak
                        class="column-selector-overlay"
                        @click="{config.get('columns_var', 'showColumnSelector')} = false"
                    >
                        <div class="column-selector-content" @click.stop>
                            <h4>Show Columns</h4>
                            <div class="column-checkboxes">
                                <template x-for="column in {config.get('columns_list', 'availableColumns')}" :key="column.key">
                                    <label class="checkbox-item">
                                        <input
                                            type="checkbox"
                                            :value="column.key"
                                            x-model="{config.get('visible_columns', 'visibleColumns')}"
                                        >
                                        <span x-text="column.label"></span>
                                    </label>
                                </template>
                            </div>
                            <div class="column-actions">
                                <button
                                    type="button"
                                    class="btn btn-primary btn-sm"
                                    @click="{config.get('columns_var', 'showColumnSelector')} = false"
                                >
                                    Apply
                                </button>
                            </div>
                        </div>
                    </div>

                    <!-- Data Table -->
                    <div class="data-table-container">
                        <table class="data-table advanced-table">
                            <thead>
                                <tr>
                                    <th class="checkbox-column">
                                        <input
                                            type="checkbox"
                                            x-model="{config.get('select_all_var', 'selectAll')}"
                                            @change="{config.get('select_all_handler', 'toggleSelectAll')}"
                                        >
                                    </th>
                                    <template x-for="column in {config.get('visible_columns', 'visibleColumns')}" :key="column">
                                        <th
                                            class="sortable-column"
                                            @click="{config.get('sort_handler', 'sortBy')}($event, column)"
                                        >
                                            <span x-text="getColumnLabel(column)"></span>
                                            <span class="sort-indicator" :class="getSortClass(column)"></span>
                                        </th>
                                    </template>
                                    <th class="actions-column">Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                <template x-for="(item, index) in {config.get('data_var', 'tableData')}" :key="getItemKey(item)">
                                    <tr>
                                        <td>
                                            <input
                                                type="checkbox"
                                                :value="getItemKey(item)"
                                                x-model="{config.get('selected_items', 'selectedItems')}"
                                            >
                                        </td>
                                        <template x-for="column in {config.get('visible_columns', 'visibleColumns')}" :key="column">
                                            <td>
                                                <span x-text="getCellValue(item, column)"></span>
                                            </td>
                                        </template>
                                        <td class="actions-cell">
                                            <button
                                                type="button"
                                                class="btn btn-sm btn-primary"
                                                @click="{config.get('edit_handler', 'editItem')}(item)"
                                            >
                                                Edit
                                            </button>
                                            <button
                                                type="button"
                                                class="btn btn-sm btn-danger"
                                                @click="{config.get('delete_handler', 'deleteItem')}(item)"
                                            >
                                                Delete
                                            </button>
                                        </td>
                                    </tr>
                                </template>
                            </tbody>
                        </table>
                    </div>

                    <!-- Pagination -->
                    <div class="pagination-container">
                        <div class="pagination-info">
                            <span x-text="getPaginationInfo()"></span>
                        </div>
                        <div class="pagination-controls">
                            <button
                                type="button"
                                class="btn btn-outline btn-sm"
                                :disabled="!{config.get('has_prev_var', 'hasPrevPage')}"
                                @click="{config.get('prev_handler', 'goToPrevPage')}"
                            >
                                Previous
                            </button>
                            <span class="page-indicator">
                                <span x-text="{config.get('current_page', 'currentPage')}"></span> of <span x-text="{config.get('total_pages', 'totalPages')}"></span>
                            </span>
                            <button
                                type="button"
                                class="btn btn-outline btn-sm"
                                :disabled="!{config.get('has_next_var', 'hasNextPage')}"
                                @click="{config.get('next_handler', 'goToNextPage')}"
                            >
                                Next
                            </button>
                        </div>
                    </div>

                    <!-- Bulk Actions -->
                    <div class="bulk-actions" x-show="{config.get('selected_items', 'selectedItems')}.length > 0">
                        <div class="bulk-actions-info">
                            <span x-text="{config.get('selected_items', 'selectedItems')}.length + ' items selected'"></span>
                        </div>
                        <div class="bulk-actions-controls">
                            <button
                                type="button"
                                class="btn btn-success btn-sm"
                                @click="{config.get('bulk_edit_handler', 'bulkEdit')}"
                            >
                                Bulk Edit
                            </button>
                            <button
                                type="button"
                                class="btn btn-warning btn-sm"
                                @click="{config.get('bulk_export_handler', 'bulkExport')}"
                            >
                                Export Selected
                            </button>
                            <button
                                type="button"
                                class="btn btn-danger btn-sm"
                                @click="{config.get('bulk_delete_handler', 'bulkDelete')}"
                            >
                                Delete Selected
                            </button>
                        </div>
                    </div>
                </div>

                <div class="modal-footer">
                    <div class="footer-actions">
                        <button
                            type="button"
                            class="btn btn-secondary"
                            @click="{config.get('show_var', 'showAdvancedModal')} = false"
                        >
                            Close
                        </button>
                        <button
                            type="button"
                            class="btn btn-primary"
                            @click="{config.get('save_handler', 'saveChanges')}"
                        >
                            Save Changes
                        </button>
                    </div>
                </div>
            </div>
        </div>
        '''
        self.registry.register_component(name, 'advanced_modal', f'templates/components/{name}.html', config)

# Global instances
component_registry = ComponentRegistry()
component_builder = ComponentBuilder(component_registry)
advanced_modal_builder = AdvancedModalBuilder(component_registry)

# Initialize default components
def initialize_default_components():
    """Initialize default component library"""

    # Theme configurations
    component_registry.set_theme('light', {
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
    })

    component_registry.set_theme('dark', {
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
    })

    # Build standard components
    component_builder.build_button_component('btn_primary', {
        'variant': 'primary',
        'size': 'md',
        'type': 'button'
    })

    component_builder.build_button_component('btn_secondary', {
        'variant': 'secondary',
        'size': 'md',
        'type': 'button'
    })

    component_builder.build_button_component('btn_success', {
        'variant': 'success',
        'size': 'md',
        'type': 'button'
    })

    component_builder.build_button_component('btn_danger', {
        'variant': 'danger',
        'size': 'md',
        'type': 'button'
    })

    component_builder.build_modal_component('basic_modal', {
        'size': 'md',
        'show_var': 'showModal',
        'close_on_overlay': True
    })

    component_builder.build_table_component('data_table', {
        'striped': True
    })

    component_builder.build_card_component('info_card', {
        'variant': 'default'
    })

    component_builder.build_alert_component('info_alert', {
        'type': 'info',
        'dismissible': True
    })

    component_builder.build_alert_component('success_alert', {
        'type': 'success',
        'dismissible': True
    })

    component_builder.build_alert_component('warning_alert', {
        'type': 'warning',
        'dismissible': True
    })

    component_builder.build_alert_component('error_alert', {
        'type': 'danger',
        'dismissible': True
    })

    # Build advanced modal
    advanced_modal_builder.build_advanced_crud_modal('advanced_crud_modal', {
        'size': 'xl',
        'show_var': 'showAdvancedModal',
        'search_var': 'searchQuery',
        'filter_var': 'selectedFilter',
        'columns_var': 'showColumnSelector',
        'visible_columns': 'visibleColumns',
        'data_var': 'tableData',
        'selected_items': 'selectedItems',
        'select_all_var': 'selectAll',
        'current_page': 'currentPage',
        'total_pages': 'totalPages',
        'has_prev_var': 'hasPrevPage',
        'has_next_var': 'hasNextPage',
        'search_handler': 'searchData',
        'filter_handler': 'applyFilter',
        'sort_handler': 'sortBy',
        'select_all_handler': 'toggleSelectAll',
        'edit_handler': 'editItem',
        'delete_handler': 'deleteItem',
        'bulk_edit_handler': 'bulkEdit',
        'bulk_export_handler': 'bulkExport',
        'bulk_delete_handler': 'bulkDelete',
        'save_handler': 'saveChanges',
        'prev_handler': 'goToPrevPage',
        'next_handler': 'goToNextPage'
    })

    logger.info("Default components initialized successfully")

# Auto-initialize
initialize_default_components()
