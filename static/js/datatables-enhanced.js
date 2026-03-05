/**
 * Enhanced DataTables Integration for ValidoAI
 * Feature-rich DataTables with all possible options
 */

class ValidoAIDataTables {
    constructor() {
        this.tables = new Map();
        this.defaultOptions = {
            responsive: true,
            pageLength: 25,
            lengthMenu: [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
            language: {
                search: "🔍 Search:",
                lengthMenu: "Show _MENU_ entries",
                info: "Showing _START_ to _END_ of _TOTAL_ entries",
                infoEmpty: "No entries to show",
                infoFiltered: "(filtered from _MAX_ total entries)",
                paginate: {
                    first: "First",
                    last: "Last",
                    next: "Next",
                    previous: "Previous"
                }
            },
            dom: '<"top"fB>rt<"bottom"lip><"clear">',
            buttons: [
                'copy', 'csv', 'excel', 'pdf', 'print',
                {
                    extend: 'colvis',
                    text: 'Columns',
                    className: 'btn btn-outline-secondary'
                }
            ]
        };
    }

    init(selector, options = {}) {
        const tableId = this.generateId();
        const config = this.mergeOptions(options);

        // Initialize DataTable
        const table = $(selector).DataTable(config);

        // Store reference
        this.tables.set(tableId, {
            table: table,
            selector: selector,
            config: config
        });

        // Add theme integration
        this.applyThemeIntegration(tableId);

        // Add custom features
        this.addCustomFeatures(tableId);

        return tableId;
    }

    mergeOptions(customOptions) {
        return {
            ...this.defaultOptions,
            ...customOptions,
            initComplete: (settings, json) => {
                // Custom initialization
                this.onTableInit(settings, json);

                // Call custom initComplete if provided
                if (customOptions.initComplete) {
                    customOptions.initComplete(settings, json);
                }
            }
        };
    }

    onTableInit(settings, json) {
        // Add custom styling and features after initialization
        const table = settings.oInstance;
        const tableWrapper = $(table.table().container());

        // Add theme-aware styling
        this.updateTableStyling(tableWrapper);

        // Add export functionality
        this.addExportFeatures(tableWrapper, table);

        // Add advanced filtering
        this.addAdvancedFilters(tableWrapper, table);

        // Add bulk operations
        this.addBulkOperations(tableWrapper, table);
    }

    updateTableStyling(wrapper) {
        // Apply theme-aware styling
        wrapper.addClass('valido-datatable');

        // Add responsive classes
        wrapper.find('.dataTables_wrapper').addClass('table-responsive');

        // Style buttons
        wrapper.find('.dt-buttons button').each(function() {
            $(this).removeClass('dt-button').addClass('btn btn-sm');
        });
    }

    addExportFeatures(wrapper, table) {
        const exportContainer = $('<div class="export-features mb-3"></div>');

        // Custom export options
        const exportOptions = [
            { text: 'Export Visible', action: () => this.exportVisible(table) },
            { text: 'Export All', action: () => this.exportAll(table) },
            { text: 'Export Selected', action: () => this.exportSelected(table) }
        ];

        exportOptions.forEach(option => {
            const button = $(`<button class="btn btn-outline-primary btn-sm me-2">${option.text}</button>`);
            button.on('click', option.action);
            exportContainer.append(button);
        });

        wrapper.find('.dataTables_filter').after(exportContainer);
    }

    addAdvancedFilters(wrapper, table) {
        const filterContainer = $('<div class="advanced-filters mb-3"></div>');

        // Date range filter
        const dateFilter = `
            <div class="row g-3">
                <div class="col-md-3">
                    <label class="form-label">From Date</label>
                    <input type="date" class="form-control form-control-sm date-from">
                </div>
                <div class="col-md-3">
                    <label class="form-label">To Date</label>
                    <input type="date" class="form-control form-control-sm date-to">
                </div>
                <div class="col-md-3">
                    <label class="form-label">Status</label>
                    <select class="form-select form-select-sm status-filter">
                        <option value="">All Status</option>
                        <option value="active">Active</option>
                        <option value="inactive">Inactive</option>
                        <option value="pending">Pending</option>
                    </select>
                </div>
                <div class="col-md-3">
                    <label class="form-label">&nbsp;</label>
                    <div>
                        <button class="btn btn-outline-secondary btn-sm me-2 clear-filters">Clear Filters</button>
                        <button class="btn btn-primary btn-sm apply-filters">Apply Filters</button>
                    </div>
                </div>
            </div>
        `;

        filterContainer.html(dateFilter);
        wrapper.find('.dataTables_length').after(filterContainer);

        // Bind filter events
        this.bindFilterEvents(wrapper, table);
    }

    bindFilterEvents(wrapper, table) {
        wrapper.find('.apply-filters').on('click', () => {
            const dateFrom = wrapper.find('.date-from').val();
            const dateTo = wrapper.find('.date-to').val();
            const status = wrapper.find('.status-filter').val();

            this.applyFilters(table, { dateFrom, dateTo, status });
        });

        wrapper.find('.clear-filters').on('click', () => {
            wrapper.find('.date-from').val('');
            wrapper.find('.date-to').val('');
            wrapper.find('.status-filter').val('');
            table.search('').columns().search('').draw();
        });
    }

    applyFilters(table, filters) {
        // Apply date range filter
        if (filters.dateFrom || filters.dateTo) {
            $.fn.dataTable.ext.search.push((settings, data, dataIndex) => {
                const dateStr = data[4]; // Assuming date is in column 4
                const rowDate = new Date(dateStr);

                if (filters.dateFrom && rowDate < new Date(filters.dateFrom)) return false;
                if (filters.dateTo && rowDate > new Date(filters.dateTo)) return false;

                return true;
            });
        }

        // Apply status filter
        if (filters.status) {
            table.column(3).search(filters.status); // Assuming status is in column 3
        }

        table.draw();
    }

    addBulkOperations(wrapper, table) {
        const bulkContainer = $('<div class="bulk-operations mb-3"></div>');

        const bulkOptions = `
            <div class="d-flex align-items-center gap-2">
                <div class="form-check">
                    <input class="form-check-input select-all" type="checkbox">
                    <label class="form-check-label">Select All</label>
                </div>
                <span class="text-muted">|</span>
                <button class="btn btn-outline-danger btn-sm bulk-delete" disabled>Bulk Delete</button>
                <button class="btn btn-outline-primary btn-sm bulk-export" disabled>Bulk Export</button>
                <button class="btn btn-outline-success btn-sm bulk-status" disabled>Change Status</button>
            </div>
        `;

        bulkContainer.html(bulkOptions);
        wrapper.find('.advanced-filters').after(bulkContainer);

        this.bindBulkEvents(wrapper, table);
    }

    bindBulkEvents(wrapper, table) {
        // Select all checkbox
        wrapper.find('.select-all').on('change', function() {
            const isChecked = $(this).is(':checked');
            wrapper.find('tbody input[type="checkbox"]').prop('checked', isChecked);
            wrapper.find('.bulk-delete, .bulk-export, .bulk-status').prop('disabled', !isChecked);
        });

        // Individual checkboxes
        wrapper.on('change', 'tbody input[type="checkbox"]', function() {
            const checkedBoxes = wrapper.find('tbody input[type="checkbox"]:checked');
            const selectAll = wrapper.find('.select-all');

            if (checkedBoxes.length === 0) {
                selectAll.prop('indeterminate', false).prop('checked', false);
            } else if (checkedBoxes.length === wrapper.find('tbody input[type="checkbox"]').length) {
                selectAll.prop('indeterminate', false).prop('checked', true);
            } else {
                selectAll.prop('indeterminate', true);
            }

            wrapper.find('.bulk-delete, .bulk-export, .bulk-status').prop('disabled', checkedBoxes.length === 0);
        });
    }

    addCustomFeatures(tableId) {
        const tableData = this.tables.get(tableId);
        if (!tableData) return;

        const table = tableData.table;
        const wrapper = $(table.table().container());

        // Add row highlighting
        this.addRowHighlighting(wrapper, table);

        // Add column sorting indicators
        this.addColumnSorting(wrapper, table);

        // Add inline editing
        this.addInlineEditing(wrapper, table);

        // Add expandable rows
        this.addExpandableRows(wrapper, table);
    }

    addRowHighlighting(wrapper, table) {
        wrapper.on('mouseenter', 'tbody tr', function() {
            $(this).addClass('table-row-hover');
        }).on('mouseleave', 'tbody tr', function() {
            $(this).removeClass('table-row-hover');
        });

        // Click to select row
        wrapper.on('click', 'tbody tr', function(e) {
            if (!$(e.target).is('input[type="checkbox"]')) {
                $(this).toggleClass('table-row-selected');
            }
        });
    }

    addColumnSorting(wrapper, table) {
        // Add custom sorting indicators
        table.on('draw.dt', function() {
            wrapper.find('th').each(function() {
                const th = $(this);
                const sortIcon = th.find('.sort-icon');

                if (sortIcon.length === 0) {
                    th.append('<i class="fas fa-sort sort-icon ms-2"></i>');
                }
            });
        });
    }

    addInlineEditing(wrapper, table) {
        let editRow = null;

        wrapper.on('dblclick', 'tbody td', function() {
            if (editRow) return; // Prevent multiple edits

            const cell = $(this);
            const row = cell.closest('tr');
            const colIndex = cell.index();
            const originalValue = cell.text().trim();

            // Create input field
            const input = $('<input type="text" class="form-control form-control-sm">');
            input.val(originalValue);
            cell.html(input);
            input.focus().select();

            editRow = { cell, row, colIndex, originalValue };

            // Handle save/cancel
            input.on('blur keydown', function(e) {
                if (e.type === 'blur' || (e.type === 'keydown' && e.key === 'Enter')) {
                    const newValue = $(this).val();
                    cell.text(newValue);

                    // Update DataTable data
                    const rowIndex = table.row(row).index();
                    table.cell(rowIndex, colIndex).data(newValue);

                    editRow = null;
                } else if (e.type === 'keydown' && e.key === 'Escape') {
                    cell.text(originalValue);
                    editRow = null;
                }
            });
        });
    }

    addExpandableRows(wrapper, table) {
        // Add expand button to first column
        table.on('draw.dt', function() {
            wrapper.find('tbody tr').each(function() {
                const row = $(this);
                const firstCell = row.find('td:first');

                if (firstCell.find('.expand-btn').length === 0) {
                    firstCell.prepend('<button class="btn btn-sm btn-outline-secondary expand-btn me-2"><i class="fas fa-plus"></i></button>');
                }
            });
        });

        wrapper.on('click', '.expand-btn', function() {
            const btn = $(this);
            const row = btn.closest('tr');
            const icon = btn.find('i');

            if (icon.hasClass('fa-plus')) {
                // Expand row
                icon.removeClass('fa-plus').addClass('fa-minus');
                const detailsRow = $('<tr class="expandable-row"><td colspan="100%"><div class="expandable-content p-3 bg-light">Additional details will be shown here...</div></td></tr>');
                row.after(detailsRow);
            } else {
                // Collapse row
                icon.removeClass('fa-minus').addClass('fa-plus');
                row.next('.expandable-row').remove();
            }
        });
    }

    applyThemeIntegration(tableId) {
        const tableData = this.tables.get(tableId);
        if (!tableData) return;

        const table = tableData.table;
        const wrapper = $(table.table().container());

        // Listen for theme changes
        document.addEventListener('themeChanged', (event) => {
            this.updateTableTheme(wrapper, event.detail.theme);
        });

        // Initial theme application
        const currentTheme = localStorage.getItem('valido-theme') || 'valido-white';
        this.updateTableTheme(wrapper, currentTheme);
    }

    updateTableTheme(wrapper, theme) {
        // Remove existing theme classes
        wrapper.removeClass((index, className) => {
            return className.startsWith('datatable-theme-');
        });

        // Add new theme class
        wrapper.addClass(`datatable-theme-${theme}`);

        // Update button styles based on theme
        const isDark = ['valido-dark', 'material-dark', 'dracula', 'monokai'].includes(theme);
        wrapper.find('.btn-outline-primary').toggleClass('btn-outline-light', isDark);
        wrapper.find('.btn-outline-secondary').toggleClass('btn-outline-light', isDark);
        wrapper.find('.btn-outline-danger').toggleClass('btn-outline-light', isDark);
    }

    // Export methods
    exportVisible(table) {
        table.button('.buttons-copy').trigger();
    }

    exportAll(table) {
        // Temporarily show all rows
        const currentLength = table.page.len();
        table.page.len(-1).draw();

        setTimeout(() => {
            table.button('.buttons-excel').trigger();
            table.page.len(currentLength).draw();
        }, 100);
    }

    exportSelected(table) {
        const selectedRows = table.rows('.table-row-selected').data();
        if (selectedRows.length === 0) {
            alert('No rows selected for export');
            return;
        }

        // Create CSV from selected data
        const headers = table.columns().header().toArray().map(h => $(h).text());
        let csv = headers.join(',') + '\n';

        selectedRows.each(function(row) {
            csv += row.join(',') + '\n';
        });

        // Download CSV
        const blob = new Blob([csv], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'selected-data.csv';
        a.click();
        window.URL.revokeObjectURL(url);
    }

    generateId() {
        return 'datatable_' + Math.random().toString(36).substr(2, 9);
    }

    destroy(tableId) {
        const tableData = this.tables.get(tableId);
        if (tableData) {
            tableData.table.destroy();
            this.tables.delete(tableId);
        }
    }

    refresh(tableId) {
        const tableData = this.tables.get(tableId);
        if (tableData) {
            tableData.table.ajax.reload();
        }
    }

    getTable(tableId) {
        const tableData = this.tables.get(tableId);
        return tableData ? tableData.table : null;
    }
}

// Global instance
window.ValidoAIDataTables = new ValidoAIDataTables();
