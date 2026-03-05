"""
Generate All CRUD Routes and Templates for ValidoAI
Automatically creates CRUD operations for all 48 database tables
"""

from typing import Dict, List, Any, Optional
import os
import json
from src.routes.crud_route_generator import crud_route_generator
from src.crud.crud_registry import crud_registry
import logging

logger = logging.getLogger(__name__)

class CRUDTemplateGenerator:
    """Generates templates for CRUD operations"""

    def __init__(self):
        self.template_dir = 'templates'
        self.generated_templates: Dict[str, List[str]] = {}

    def generate_table_template(self, table_name: str) -> Dict[str, Any]:
        """Generate templates for a specific table"""
        templates = {}
        template_base = f'{self.template_dir}/{table_name}'

        # Create directory if it doesn't exist
        os.makedirs(template_base, exist_ok=True)

        # Generate list template
        list_template = self._generate_list_template(table_name)
        list_path = f'{template_base}/index.html'
        self._write_template(list_path, list_template)
        templates['list'] = list_path

        # Generate create template
        create_template = self._generate_create_template(table_name)
        create_path = f'{template_base}/create.html'
        self._write_template(create_path, create_template)
        templates['create'] = create_path

        # Generate edit template
        edit_template = self._generate_edit_template(table_name)
        edit_path = f'{template_base}/edit.html'
        self._write_template(edit_path, edit_template)
        templates['edit'] = edit_path

        # Generate view template
        view_template = self._generate_view_template(table_name)
        view_path = f'{template_base}/view.html'
        self._write_template(view_path, view_template)
        templates['view'] = view_path

        # Generate delete template
        delete_template = self._generate_delete_template(table_name)
        delete_path = f'{template_base}/delete.html'
        self._write_template(delete_path, delete_template)
        templates['delete'] = delete_path

        logger.info(f"Generated templates for table: {table_name}")
        return {
            'table_name': table_name,
            'templates': templates,
            'template_count': len(templates)
        }

    def _generate_list_template(self, table_name: str) -> str:
        """Generate list template"""
        return f'''{{% extends "base.html" %}}

{{% block title %}}{{{{ table_name.replace("_", " ").title() }} List - ValidoAI{{% endblock %}}

{{% block content %}}
<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <!-- Page Header -->
    <div class="mb-8">
        <div class="flex justify-between items-center">
            <div>
                <h1 class="text-3xl font-bold text-gray-900">
                    {{{{ table_name.replace("_", " ").title() }}}
                </h1>
                <p class="mt-2 text-gray-600">
                    Manage your {{{{ table_name.replace("_", " ") }}}} records
                </p>
            </div>
            <div class="flex space-x-3">
                <button
                    type="button"
                    class="btn btn-secondary"
                    onclick="openAdvancedModal()"
                >
                    Advanced View
                </button>
                <a href="{{{{ url_for('{table_name}.create') }}}}" class="btn btn-primary">
                    Add New {{{{ table_name.replace("_", " ").title() }}}}
                </a>
            </div>
        </div>
    </div>

    <!-- Search and Filters -->
    <div class="bg-white shadow rounded-lg mb-6">
        <div class="px-6 py-4 border-b border-gray-200">
            <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div>
                    <input
                        type="text"
                        id="searchInput"
                        placeholder="Search {{{{ table_name.replace("_", " ") }}}}..."
                        class="form-control"
                        onkeyup="filterTable()"
                    >
                </div>
                <div>
                    <select id="statusFilter" class="form-control" onchange="filterTable()">
                        <option value="">All Status</option>
                        <option value="active">Active</option>
                        <option value="inactive">Inactive</option>
                    </select>
                </div>
                <div>
                    <select id="sortBy" class="form-control" onchange="sortTable()">
                        <option value="">Sort By</option>
                        <option value="name">Name</option>
                        <option value="created_at">Date Created</option>
                        <option value="updated_at">Last Updated</option>
                    </select>
                </div>
                <div>
                    <button type="button" class="btn btn-outline" onclick="exportData()">
                        Export
                    </button>
                </div>
            </div>
        </div>
    </div>

    <!-- Data Table -->
    <div class="bg-white shadow rounded-lg">
        <div class="px-6 py-4 border-b border-gray-200">
            <div class="flex justify-between items-center">
                <h3 class="text-lg font-medium text-gray-900">Records</h3>
                <div class="flex items-center space-x-2">
                    <span class="text-sm text-gray-500" id="recordCount">0 records</span>
                </div>
            </div>
        </div>

        <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200" id="dataTable">
                <thead class="bg-gray-50">
                    <tr>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            <input type="checkbox" id="selectAll" onchange="toggleSelectAll()">
                        </th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Name
                        </th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Status
                        </th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Created
                        </th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Actions
                        </th>
                    </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200" id="tableBody">
                    <!-- Data will be loaded here -->
                </tbody>
            </table>
        </div>

        <!-- Pagination -->
        <div class="px-6 py-4 border-t border-gray-200">
            <div class="flex justify-between items-center">
                <div class="text-sm text-gray-700" id="paginationInfo">
                    Showing 0 to 0 of 0 entries
                </div>
                <div class="flex space-x-2" id="paginationControls">
                    <!-- Pagination buttons will be generated here -->
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Advanced Modal -->
{{{{ component_registry.render_component('advanced_crud_modal', {
    'title': '{table_name.replace("_", " ").title()} Management',
    'table_name': '{table_name}',
    'visible_columns': ['name', 'status', 'created_at'],
    'available_columns': [
        {{'key': 'name', 'label': 'Name', 'description': 'Record name or title'}},
        {{'key': 'status', 'label': 'Status', 'description': 'Current status'}},
        {{'key': 'created_at', 'label': 'Created', 'description': 'Creation date'}},
        {{'key': 'updated_at', 'label': 'Updated', 'description': 'Last update date'}}
    ],
    'filter_options': [
        {{'value': 'active', 'label': 'Active Only'}},
        {{'value': 'inactive', 'label': 'Inactive Only'}}
    ]
}) | safe}}}}

<script>
let currentPage = 1;
let pageSize = 25;
let totalRecords = 0;
let allData = [];

function loadData() {{
    fetch(`/api/{table_name}?page=${{currentPage}}&per_page=${{pageSize}}`)
        .then(response => response.json())
        .then(data => {{
            if (data.success) {{
                allData = data.data;
                totalRecords = data.pagination.total;
                renderTable();
                renderPagination();
            }}
        }})
        .catch(error => {{
            console.error('Error loading data:', error);
            showToast('Error', 'Failed to load data', 'error');
        }});
}}

function renderTable() {{
    const tbody = document.getElementById('tableBody');
    tbody.innerHTML = '';

    allData.forEach(record => {{
        const row = document.createElement('tr');
        row.className = 'hover:bg-gray-50';

        row.innerHTML = `
            <td class="px-6 py-4 whitespace-nowrap">
                <input type="checkbox" class="row-checkbox" value="${{record.id}}" onchange="updateSelection()">
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">${{record.name || record.title || 'N/A'}}</div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
                <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${{record.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}}">
                    ${{record.is_active ? 'Active' : 'Inactive'}}
                </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                ${{record.created_at ? new Date(record.created_at).toLocaleDateString() : 'N/A'}}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                <a href="/{table_name}/view/${{record.id}}" class="text-indigo-600 hover:text-indigo-900">View</a>
                <a href="/{table_name}/edit/${{record.id}}" class="text-blue-600 hover:text-blue-900">Edit</a>
                <button onclick="deleteRecord('${{record.id}}')" class="text-red-600 hover:text-red-900">Delete</button>
            </td>
        `;

        tbody.appendChild(row);
    }});

    document.getElementById('recordCount').textContent = `${{allData.length}} records`;
}}

function renderPagination() {{
    const totalPages = Math.ceil(totalRecords / pageSize);
    const paginationControls = document.getElementById('paginationControls');
    const paginationInfo = document.getElementById('paginationInfo');

    paginationInfo.textContent = `Showing ${{((currentPage - 1) * pageSize) + 1}} to ${{Math.min(currentPage * pageSize, totalRecords)}} of ${{totalRecords}} entries`;

    paginationControls.innerHTML = '';

    // Previous button
    const prevBtn = document.createElement('button');
    prevBtn.className = `px-3 py-1 text-sm border rounded ${{currentPage === 1 ? 'bg-gray-100 text-gray-400 cursor-not-allowed' : 'bg-white text-gray-700 hover:bg-gray-50'}}`;
    prevBtn.textContent = 'Previous';
    prevBtn.onclick = () => {{
        if (currentPage > 1) {{
            currentPage--;
            loadData();
        }}
    }};
    paginationControls.appendChild(prevBtn);

    // Page numbers
    for (let i = Math.max(1, currentPage - 2); i <= Math.min(totalPages, currentPage + 2); i++) {{
        const pageBtn = document.createElement('button');
        pageBtn.className = `px-3 py-1 text-sm border rounded ${{i === currentPage ? 'bg-blue-600 text-white' : 'bg-white text-gray-700 hover:bg-gray-50'}}`;
        pageBtn.textContent = i;
        pageBtn.onclick = () => {{
            currentPage = i;
            loadData();
        }};
        paginationControls.appendChild(pageBtn);
    }}

    // Next button
    const nextBtn = document.createElement('button');
    nextBtn.className = `px-3 py-1 text-sm border rounded ${{currentPage === totalPages ? 'bg-gray-100 text-gray-400 cursor-not-allowed' : 'bg-white text-gray-700 hover:bg-gray-50'}}`;
    nextBtn.textContent = 'Next';
    nextBtn.onclick = () => {{
        if (currentPage < totalPages) {{
            currentPage++;
            loadData();
        }}
    }};
    paginationControls.appendChild(nextBtn);
}}

function filterTable() {{
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const statusFilter = document.getElementById('statusFilter').value;

    const filteredData = allData.filter(record => {{
        const matchesSearch = !searchTerm ||
            (record.name || record.title || '').toLowerCase().includes(searchTerm);
        const matchesStatus = !statusFilter ||
            (statusFilter === 'active' && record.is_active) ||
            (statusFilter === 'inactive' && !record.is_active);

        return matchesSearch && matchesStatus;
    }});

    // Update table with filtered data
    const tbody = document.getElementById('tableBody');
    tbody.innerHTML = '';

    filteredData.forEach(record => {{
        const row = document.createElement('tr');
        row.className = 'hover:bg-gray-50';

        row.innerHTML = `
            <td class="px-6 py-4 whitespace-nowrap">
                <input type="checkbox" class="row-checkbox" value="${{record.id}}" onchange="updateSelection()">
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">${{record.name || record.title || 'N/A'}}</div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
                <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${{record.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}}">
                    ${{record.is_active ? 'Active' : 'Inactive'}}
                </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                ${{record.created_at ? new Date(record.created_at).toLocaleDateString() : 'N/A'}}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                <a href="/{table_name}/view/${{record.id}}" class="text-indigo-600 hover:text-indigo-900">View</a>
                <a href="/{table_name}/edit/${{record.id}}" class="text-blue-600 hover:text-blue-900">Edit</a>
                <button onclick="deleteRecord('${{record.id}}')" class="text-red-600 hover:text-red-900">Delete</button>
            </td>
        `;

        tbody.appendChild(row);
    }});

    document.getElementById('recordCount').textContent = `${{filteredData.length}} records`;
}}

function sortTable() {{
    const sortBy = document.getElementById('sortBy').value;
    if (!sortBy) return;

    allData.sort((a, b) => {{
        let aVal = a[sortBy] || '';
        let bVal = b[sortBy] || '';

        if (sortBy.includes('date') || sortBy.includes('at')) {{
            aVal = new Date(aVal);
            bVal = new Date(bVal);
        }}

        if (aVal < bVal) return -1;
        if (aVal > bVal) return 1;
        return 0;
    }});

    renderTable();
}}

function toggleSelectAll() {{
    const selectAll = document.getElementById('selectAll').checked;
    const checkboxes = document.querySelectorAll('.row-checkbox');

    checkboxes.forEach(checkbox => {{
        checkbox.checked = selectAll;
    }});

    updateSelection();
}}

function updateSelection() {{
    const selected = document.querySelectorAll('.row-checkbox:checked');
    console.log(`${{selected.length}} items selected`);
}}

function deleteRecord(recordId) {{
    if (confirm('Are you sure you want to delete this record?')) {{
        fetch(`/api/{table_name}/${{recordId}}`, {{
            method: 'DELETE',
            headers: {{
                'Content-Type': 'application/json',
            }},
            body: JSON.stringify({{
                deleted_by: 'user',
                deleted_reason: 'Deleted via web interface'
            }})
        }})
        .then(response => response.json())
        .then(data => {{
            if (data.success) {{
                showToast('Success', 'Record deleted successfully', 'success');
                loadData();
            }} else {{
                showToast('Error', data.error || 'Failed to delete record', 'error');
            }}
        }})
        .catch(error => {{
            console.error('Error deleting record:', error);
            showToast('Error', 'Failed to delete record', 'error');
        }});
    }}
}}

function exportData() {{
    const format = 'csv';
    window.open(`/api/{table_name}/export?format=${{format}}`);
}}

function openAdvancedModal() {{
    // This will be handled by Alpine.js
    showAdvancedModal = true;
}}

function showToast(title, message, type = 'info') {{
    // Simple toast implementation
    console.log(`[${{type.toUpperCase()}}] ${{title}}: ${{message}}`);
}}

// Initialize
document.addEventListener('DOMContentLoaded', function() {{
    loadData();
}});
</script>

{{% endblock %}}
'''

    def _generate_create_template(self, table_name: str) -> str:
        """Generate create template"""
        return f'''{{% extends "base.html" %}}

{{% block title %}}Add New {{{{ table_name.replace("_", " ").title() }}}} - ValidoAI{{% endblock %}}

{{% block content %}}
<div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <!-- Page Header -->
    <div class="mb-8">
        <div class="flex items-center justify-between">
            <div>
                <h1 class="text-3xl font-bold text-gray-900">
                    Add New {{{{ table_name.replace("_", " ").title() }}}}
                </h1>
                <p class="mt-2 text-gray-600">
                    Create a new {{{{ table_name.replace("_", " ") }}}} record
                </p>
            </div>
            <a href="{{{{ url_for('{table_name}.get_list') }}}}" class="btn btn-secondary">
                Back to List
            </a>
        </div>
    </div>

    <!-- Form -->
    <div class="bg-white shadow rounded-lg">
        <div class="px-6 py-4 border-b border-gray-200">
            <h3 class="text-lg font-medium text-gray-900">Record Details</h3>
        </div>

        <form id="createForm" class="p-6 space-y-6">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                    <label for="name" class="block text-sm font-medium text-gray-700">
                        Name *
                    </label>
                    <input
                        type="text"
                        id="name"
                        name="name"
                        required
                        class="mt-1 form-control"
                        placeholder="Enter name"
                    >
                </div>

                <div>
                    <label for="email" class="block text-sm font-medium text-gray-700">
                        Email
                    </label>
                    <input
                        type="email"
                        id="email"
                        name="email"
                        class="mt-1 form-control"
                        placeholder="Enter email address"
                    >
                </div>

                <div>
                    <label for="phone" class="block text-sm font-medium text-gray-700">
                        Phone
                    </label>
                    <input
                        type="tel"
                        id="phone"
                        name="phone"
                        class="mt-1 form-control"
                        placeholder="Enter phone number"
                    >
                </div>

                <div>
                    <label for="status" class="block text-sm font-medium text-gray-700">
                        Status
                    </label>
                    <select id="status" name="is_active" class="mt-1 form-control">
                        <option value="true">Active</option>
                        <option value="false">Inactive</option>
                    </select>
                </div>
            </div>

            <div>
                <label for="description" class="block text-sm font-medium text-gray-700">
                    Description
                </label>
                <textarea
                    id="description"
                    name="description"
                    rows="4"
                    class="mt-1 form-control"
                    placeholder="Enter description"
                ></textarea>
            </div>

            <!-- Form Actions -->
            <div class="flex justify-end space-x-3 pt-6 border-t border-gray-200">
                <a href="{{{{ url_for('{table_name}.get_list') }}}}" class="btn btn-secondary">
                    Cancel
                </a>
                <button type="submit" class="btn btn-primary">
                    Create {{{{ table_name.replace("_", " ").title() }}}}
                </button>
            </div>
        </form>
    </div>
</div>

<script>
document.getElementById('createForm').addEventListener('submit', function(e) {{
    e.preventDefault();

    const formData = new FormData(this);
    const data = Object.fromEntries(formData.entries());

    // Convert string booleans
    if (data.is_active) {{
        data.is_active = data.is_active === 'true';
    }}

    fetch('/api/{table_name}', {{
        method: 'POST',
        headers: {{
            'Content-Type': 'application/json',
        }},
        body: JSON.stringify(data)
    }})
    .then(response => response.json())
    .then(result => {{
        if (result.success) {{
            showToast('Success', '{{{{ table_name.replace("_", " ").title() }}}} created successfully', 'success');
            setTimeout(() => {{
                window.location.href = '{{{{ url_for("{table_name}.get_list") }}}}';
            }}, 1500);
        }} else {{
            showToast('Error', result.error || 'Failed to create record', 'error');
        }}
    }})
    .catch(error => {{
        console.error('Error creating record:', error);
        showToast('Error', 'Failed to create record', 'error');
    }});
}});

function showToast(title, message, type = 'info') {{
    // Simple toast implementation
    console.log(`[${{type.toUpperCase()}}] ${{title}}: ${{message}}`);
}}
</script>

{{% endblock %}}
'''

    def _generate_edit_template(self, table_name: str) -> str:
        """Generate edit template"""
        return f'''{{% extends "base.html" %}}

{{% block title %}}Edit {{{{ table_name.replace("_", " ").title() }}}} - ValidoAI{{% endblock %}}

{{% block content %}}
<div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <!-- Page Header -->
    <div class="mb-8">
        <div class="flex items-center justify-between">
            <div>
                <h1 class="text-3xl font-bold text-gray-900">
                    Edit {{{{ table_name.replace("_", " ").title() }}}}
                </h1>
                <p class="mt-2 text-gray-600">
                    Update {{{{ table_name.replace("_", " ") }}}} record details
                </p>
            </div>
            <div class="flex space-x-3">
                <a href="{{{{ url_for('{table_name}.get_detail', record_id=record.id) }}}}" class="btn btn-secondary">
                    View
                </a>
                <a href="{{{{ url_for('{table_name}.get_list') }}}}" class="btn btn-secondary">
                    Back to List
                </a>
            </div>
        </div>
    </div>

    <!-- Form -->
    <div class="bg-white shadow rounded-lg">
        <div class="px-6 py-4 border-b border-gray-200">
            <h3 class="text-lg font-medium text-gray-900">Record Details</h3>
        </div>

        <form id="editForm" class="p-6 space-y-6">
            <input type="hidden" name="id" value="{{{{ record.id }}}}">

            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                    <label for="name" class="block text-sm font-medium text-gray-700">
                        Name *
                    </label>
                    <input
                        type="text"
                        id="name"
                        name="name"
                        required
                        class="mt-1 form-control"
                        value="{{{{ record.name or record.title or '' }}}}"
                    >
                </div>

                <div>
                    <label for="email" class="block text-sm font-medium text-gray-700">
                        Email
                    </label>
                    <input
                        type="email"
                        id="email"
                        name="email"
                        class="mt-1 form-control"
                        value="{{{{ record.email or '' }}}}"
                    >
                </div>

                <div>
                    <label for="phone" class="block text-sm font-medium text-gray-700">
                        Phone
                    </label>
                    <input
                        type="tel"
                        id="phone"
                        name="phone"
                        class="mt-1 form-control"
                        value="{{{{ record.phone or '' }}}}"
                    >
                </div>

                <div>
                    <label for="status" class="block text-sm font-medium text-gray-700">
                        Status
                    </label>
                    <select id="status" name="is_active" class="mt-1 form-control">
                        <option value="true" {{{{ 'selected' if record.is_active else '' }}}}>Active</option>
                        <option value="false" {{{{ 'selected' if not record.is_active else '' }}}}>Inactive</option>
                    </select>
                </div>
            </div>

            <div>
                <label for="description" class="block text-sm font-medium text-gray-700">
                    Description
                </label>
                <textarea
                    id="description"
                    name="description"
                    rows="4"
                    class="mt-1 form-control"
                >{{{{ record.description or '' }}}}</textarea>
            </div>

            <!-- Form Actions -->
            <div class="flex justify-end space-x-3 pt-6 border-t border-gray-200">
                <a href="{{{{ url_for('{table_name}.get_list') }}}}" class="btn btn-secondary">
                    Cancel
                </a>
                <button type="submit" class="btn btn-primary">
                    Update {{{{ table_name.replace("_", " ").title() }}}}
                </button>
            </div>
        </form>
    </div>
</div>

<script>
document.getElementById('editForm').addEventListener('submit', function(e) {{
    e.preventDefault();

    const formData = new FormData(this);
    const data = Object.fromEntries(formData.entries());

    // Convert string booleans
    if (data.is_active) {{
        data.is_active = data.is_active === 'true';
    }}

    fetch(`/api/{table_name}/${{data.id}}`, {{
        method: 'PUT',
        headers: {{
            'Content-Type': 'application/json',
        }},
        body: JSON.stringify(data)
    }})
    .then(response => response.json())
    .then(result => {{
        if (result.success) {{
            showToast('Success', '{{{{ table_name.replace("_", " ").title() }}}} updated successfully', 'success');
            setTimeout(() => {{
                window.location.href = '{{{{ url_for("{table_name}.get_list") }}}}';
            }}, 1500);
        }} else {{
            showToast('Error', result.error || 'Failed to update record', 'error');
        }}
    }})
    .catch(error => {{
        console.error('Error updating record:', error);
        showToast('Error', 'Failed to update record', 'error');
    }});
}});

function showToast(title, message, type = 'info') {{
    // Simple toast implementation
    console.log(`[${{type.toUpperCase()}}] ${{title}}: ${{message}}`);
}}
</script>

{{% endblock %}}
'''

    def _generate_view_template(self, table_name: str) -> str:
        """Generate view template"""
        return f'''{{% extends "base.html" %}}

{{% block title %}}View {{{{ table_name.replace("_", " ").title() }}}} - ValidoAI{{% endblock %}}

{{% block content %}}
<div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <!-- Page Header -->
    <div class="mb-8">
        <div class="flex items-center justify-between">
            <div>
                <h1 class="text-3xl font-bold text-gray-900">
                    View {{{{ table_name.replace("_", " ").title() }}}}
                </h1>
                <p class="mt-2 text-gray-600">
                    Record details and information
                </p>
            </div>
            <div class="flex space-x-3">
                <a href="{{{{ url_for('{table_name}.edit', record_id=record.id) }}}}" class="btn btn-primary">
                    Edit
                </a>
                <button onclick="deleteRecord()" class="btn btn-danger">
                    Delete
                </button>
                <a href="{{{{ url_for('{table_name}.get_list') }}}}" class="btn btn-secondary">
                    Back to List
                </a>
            </div>
        </div>
    </div>

    <!-- Record Details -->
    <div class="bg-white shadow rounded-lg">
        <div class="px-6 py-4 border-b border-gray-200">
            <h3 class="text-lg font-medium text-gray-900">Record Information</h3>
        </div>

        <div class="p-6">
            <dl class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                    <dt class="text-sm font-medium text-gray-500">ID</dt>
                    <dd class="mt-1 text-sm text-gray-900">{{{{ record.id }}}}</dd>
                </div>

                <div>
                    <dt class="text-sm font-medium text-gray-500">Name</dt>
                    <dd class="mt-1 text-sm text-gray-900">{{{{ record.name or record.title or 'N/A' }}}}</dd>
                </div>

                <div>
                    <dt class="text-sm font-medium text-gray-500">Email</dt>
                    <dd class="mt-1 text-sm text-gray-900">{{{{ record.email or 'N/A' }}}}</dd>
                </div>

                <div>
                    <dt class="text-sm font-medium text-gray-500">Phone</dt>
                    <dd class="mt-1 text-sm text-gray-900">{{{{ record.phone or 'N/A' }}}}</dd>
                </div>

                <div>
                    <dt class="text-sm font-medium text-gray-500">Status</dt>
                    <dd class="mt-1">
                        <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full {{{{ 'bg-green-100 text-green-800' if record.is_active else 'bg-red-100 text-red-800' }}}}">
                            {{{{ 'Active' if record.is_active else 'Inactive' }}}}
                        </span>
                    </dd>
                </div>

                <div>
                    <dt class="text-sm font-medium text-gray-500">Created</dt>
                    <dd class="mt-1 text-sm text-gray-900">{{{{ record.created_at.strftime('%B %d, %Y %I:%M %p') if record.created_at else 'N/A' }}}}</dd>
                </div>

                <div>
                    <dt class="text-sm font-medium text-gray-500">Last Updated</dt>
                    <dd class="mt-1 text-sm text-gray-900">{{{{ record.updated_at.strftime('%B %d, %Y %I:%M %p') if record.updated_at else 'N/A' }}}}</dd>
                </div>

                <div class="md:col-span-2">
                    <dt class="text-sm font-medium text-gray-500">Description</dt>
                    <dd class="mt-1 text-sm text-gray-900">{{{{ record.description or 'No description provided' }}}}</dd>
                </div>
            </dl>
        </div>
    </div>

    <!-- Audit Trail -->
    <div class="bg-white shadow rounded-lg mt-6">
        <div class="px-6 py-4 border-b border-gray-200">
            <h3 class="text-lg font-medium text-gray-900">Audit Information</h3>
        </div>

        <div class="p-6">
            <dl class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                    <dt class="text-sm font-medium text-gray-500">Created By</dt>
                    <dd class="mt-1 text-sm text-gray-900">{{{{ record.created_by or 'System' }}}}</dd>
                </div>

                <div>
                    <dt class="text-sm font-medium text-gray-500">Updated By</dt>
                    <dd class="mt-1 text-sm text-gray-900">{{{{ record.updated_by or 'Not updated' }}}}</dd>
                </div>
            </dl>
        </div>
    </div>
</div>

<script>
function deleteRecord() {{
    if (confirm('Are you sure you want to delete this record? This action cannot be undone.')) {{
        fetch(`/api/{table_name}/{{{{ record.id }}}}`, {{
            method: 'DELETE',
            headers: {{
                'Content-Type': 'application/json',
            }},
            body: JSON.stringify({{
                deleted_by: 'user',
                deleted_reason: 'Deleted via web interface'
            }})
        }})
        .then(response => response.json())
        .then(data => {{
            if (data.success) {{
                showToast('Success', 'Record deleted successfully', 'success');
                setTimeout(() => {{
                    window.location.href = '{{{{ url_for("{table_name}.get_list") }}}}';
                }}, 1500);
            }} else {{
                showToast('Error', data.error || 'Failed to delete record', 'error');
            }}
        }})
        .catch(error => {{
            console.error('Error deleting record:', error);
            showToast('Error', 'Failed to delete record', 'error');
        }});
    }}
}}

function showToast(title, message, type = 'info') {{
    // Simple toast implementation
    console.log(`[${{type.toUpperCase()}}] ${{title}}: ${{message}}`);
}}
</script>

{{% endblock %}}
'''

    def _generate_delete_template(self, table_name: str) -> str:
        """Generate delete template"""
        return f'''{{% extends "base.html" %}}

{{% block title %}}Delete {{{{ table_name.replace("_", " ").title() }}}} - ValidoAI{{% endblock %}}

{{% block content %}}
<div class="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <!-- Page Header -->
    <div class="mb-8">
        <div class="flex items-center justify-between">
            <div>
                <h1 class="text-3xl font-bold text-gray-900">
                    Delete {{{{ table_name.replace("_", " ").title() }}}}
                </h1>
                <p class="mt-2 text-gray-600">
                    Are you sure you want to delete this record?
                </p>
            </div>
            <div class="flex space-x-3">
                <a href="{{{{ url_for('{table_name}.get_detail', record_id=record.id) }}}}" class="btn btn-secondary">
                    Cancel
                </a>
            </div>
        </div>
    </div>

    <!-- Warning Card -->
    <div class="bg-red-50 border border-red-200 rounded-lg p-6 mb-6">
        <div class="flex">
            <div class="flex-shrink-0">
                <svg class="h-5 w-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"></path>
                </svg>
            </div>
            <div class="ml-3">
                <h3 class="text-sm font-medium text-red-800">
                    This action cannot be undone
                </h3>
                <div class="mt-2 text-sm text-red-700">
                    <p>Once you delete this record, it will be moved to the recycle bin. You can restore it later if needed.</p>
                </div>
            </div>
        </div>
    </div>

    <!-- Record Details -->
    <div class="bg-white shadow rounded-lg mb-6">
        <div class="px-6 py-4 border-b border-gray-200">
            <h3 class="text-lg font-medium text-gray-900">Record Details</h3>
        </div>

        <div class="p-6">
            <dl class="space-y-4">
                <div>
                    <dt class="text-sm font-medium text-gray-500">Name</dt>
                    <dd class="mt-1 text-sm text-gray-900">{{{{ record.name or record.title or 'N/A' }}}}</dd>
                </div>

                <div>
                    <dt class="text-sm font-medium text-gray-500">Email</dt>
                    <dd class="mt-1 text-sm text-gray-900">{{{{ record.email or 'N/A' }}}}</dd>
                </div>

                <div>
                    <dt class="text-sm font-medium text-gray-500">Status</dt>
                    <dd class="mt-1">
                        <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full {{{{ 'bg-green-100 text-green-800' if record.is_active else 'bg-red-100 text-red-800' }}}}">
                            {{{{ 'Active' if record.is_active else 'Inactive' }}}}
                        </span>
                    </dd>
                </div>
            </dl>
        </div>
    </div>

    <!-- Delete Form -->
    <div class="bg-white shadow rounded-lg">
        <div class="px-6 py-4 border-b border-gray-200">
            <h3 class="text-lg font-medium text-gray-900">Confirm Deletion</h3>
        </div>

        <form id="deleteForm" class="p-6">
            <input type="hidden" name="id" value="{{{{ record.id }}}}">

            <div class="mb-6">
                <label for="delete_reason" class="block text-sm font-medium text-gray-700 mb-2">
                    Reason for deletion (optional)
                </label>
                <textarea
                    id="delete_reason"
                    name="deleted_reason"
                    rows="3"
                    class="form-control"
                    placeholder="Enter reason for deletion..."
                ></textarea>
            </div>

            <!-- CAPTCHA for verification -->
            <div class="mb-6">
                <label class="block text-sm font-medium text-gray-700 mb-2">
                    Verification
                </label>
                {{{{ component_registry.render_component('captcha', {{
                    'id': 'delete_captcha',
                    'required': True
                }}) | safe }}}}
            </div>

            <!-- Form Actions -->
            <div class="flex justify-end space-x-3">
                <a href="{{{{ url_for('{table_name}.get_detail', record_id=record.id) }}}}" class="btn btn-secondary">
                    Cancel
                </a>
                <button type="submit" class="btn btn-danger">
                    Delete Record
                </button>
            </div>
        </form>
    </div>
</div>

<script>
document.getElementById('deleteForm').addEventListener('submit', function(e) {{
    e.preventDefault();

    const formData = new FormData(this);
    const data = Object.fromEntries(formData.entries());

    // Verify CAPTCHA
    if (!verifyCaptcha('delete_captcha')) {{
        showToast('Error', 'Please complete the CAPTCHA verification', 'error');
        return;
    }}

    fetch(`/api/{table_name}/${{data.id}}`, {{
        method: 'DELETE',
        headers: {{
            'Content-Type': 'application/json',
        }},
        body: JSON.stringify({{
            deleted_by: 'user',
            deleted_reason: data.deleted_reason || 'Deleted via web interface',
            captcha_verified: true
        }})
    }})
    .then(response => response.json())
    .then(result => {{
        if (result.success) {{
            showToast('Success', 'Record deleted successfully', 'success');
            setTimeout(() => {{
                window.location.href = '{{{{ url_for("{table_name}.get_list") }}}}';
            }}, 1500);
        }} else {{
            showToast('Error', result.error || 'Failed to delete record', 'error');
        }}
    }})
    .catch(error => {{
        console.error('Error deleting record:', error);
        showToast('Error', 'Failed to delete record', 'error');
    }});
}});

function verifyCaptcha(captchaId) {{
    // Simple CAPTCHA verification (implement your logic here)
    return true;
}}

function showToast(title, message, type = 'info') {{
    // Simple toast implementation
    console.log(`[${{type.toUpperCase()}}] ${{title}}: ${{message}}`);
}}
</script>

{{% endblock %}}
'''

    def _write_template(self, file_path: str, content: str):
        """Write template to file"""
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"Template written: {file_path}")
        except Exception as e:
            logger.error(f"Error writing template {file_path}: {e}")

    def generate_all_templates(self) -> Dict[str, Any]:
        """Generate templates for all tables"""
        results = {}
        all_tables = crud_registry.get_all_tables()

        for table_name in all_tables:
            results[table_name] = self.generate_table_template(table_name)

        return {
            'total_tables': len(all_tables),
            'generated_templates': results,
            'total_templates': sum(len(t.get('templates', {})) for t in results.values())
        }

# Global instance
template_generator = CRUDTemplateGenerator()

# Utility functions
def generate_templates_for_table(table_name: str) -> Dict[str, Any]:
    """Utility function to generate templates for a single table"""
    return template_generator.generate_table_template(table_name)

def generate_all_templates() -> Dict[str, Any]:
    """Utility function to generate templates for all tables"""
    return template_generator.generate_all_templates()
