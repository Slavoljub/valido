/**
 * Interactive Charts Component for ValidoAI
 * Chart.js integration with data labels and interactive features
 */

class ValidoAICharts {
    constructor() {
        this.charts = new Map();
        this.Chart = null;
        this.defaultOptions = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        usePointStyle: true,
                        padding: 20,
                        font: {
                            size: 12
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    borderColor: 'rgba(255, 255, 255, 0.2)',
                    borderWidth: 1,
                    cornerRadius: 8,
                    displayColors: true,
                    padding: 12,
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            if (context.parsed.y !== null) {
                                label += new Intl.NumberFormat().format(context.parsed.y);
                            }
                            return label;
                        }
                    }
                },
                datalabels: {
                    display: true,
                    color: '#666',
                    font: {
                        size: 11,
                        weight: 'bold'
                    },
                    formatter: function(value, context) {
                        return value > 0 ? value.toLocaleString() : '';
                    },
                    anchor: 'end',
                    align: 'top',
                    offset: 4
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)',
                        borderColor: 'rgba(0, 0, 0, 0.2)'
                    },
                    ticks: {
                        callback: function(value) {
                            return value.toLocaleString();
                        }
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            },
            interaction: {
                intersect: false,
                mode: 'index'
            },
            animation: {
                duration: 750,
                easing: 'easeInOutQuart'
            }
        };
    }

    async init() {
        if (!window.Chart) {
            await this.loadChartJS();
        }

        // Load Chart.js DataLabels plugin
        await this.loadDataLabelsPlugin();
    }

    async loadChartJS() {
        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = 'https://cdn.jsdelivr.net/npm/chart.js';
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        });
    }

    async loadDataLabelsPlugin() {
        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = 'https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels';
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        });
    }

    createChart(canvasId, type, data, options = {}) {
        const chartId = this.generateId();
        const ctx = document.getElementById(canvasId);

        if (!ctx) {
            console.error(`Canvas element with id '${canvasId}' not found`);
            return null;
        }

        const config = this.mergeOptions(type, data, options);
        const chart = new Chart(ctx, config);

        this.charts.set(chartId, {
            chart: chart,
            canvasId: canvasId,
            config: config,
            type: type
        });

        this.addInteractiveFeatures(chartId);
        this.applyThemeIntegration(chartId);

        return chartId;
    }

    mergeOptions(type, data, customOptions) {
        const baseOptions = { ...this.defaultOptions };
        const typeSpecificOptions = this.getTypeSpecificOptions(type);

        return {
            type: type,
            data: data,
            options: {
                ...baseOptions,
                ...typeSpecificOptions,
                ...customOptions
            }
        };
    }

    getTypeSpecificOptions(type) {
        const options = {};

        switch (type) {
            case 'bar':
                options.plugins = {
                    ...options.plugins,
                    datalabels: {
                        ...options.plugins?.datalabels,
                        anchor: 'end',
                        align: 'top'
                    }
                };
                break;

            case 'line':
                options.elements = {
                    point: {
                        radius: 4,
                        hoverRadius: 6,
                        borderWidth: 2,
                        hoverBorderWidth: 3
                    },
                    line: {
                        tension: 0.4
                    }
                };
                options.plugins.datalabels.display = false; // Usually too cluttered for line charts
                break;

            case 'pie':
            case 'doughnut':
                options.plugins.legend.position = 'right';
                options.plugins.datalabels = {
                    ...options.plugins.datalabels,
                    formatter: (value, ctx) => {
                        const total = ctx.dataset.data.reduce((a, b) => a + b, 0);
                        const percentage = ((value / total) * 100).toFixed(1);
                        return percentage + '%';
                    },
                    anchor: 'center',
                    align: 'center',
                    color: '#fff',
                    font: {
                        size: 12,
                        weight: 'bold'
                    }
                };
                break;

            case 'radar':
                options.scale = {
                    ticks: {
                        beginAtZero: true,
                        max: 100
                    }
                };
                break;
        }

        return options;
    }

    addInteractiveFeatures(chartId) {
        const chartData = this.charts.get(chartId);
        if (!chartData) return;

        const chart = chartData.chart;

        // Add click handler
        chart.options.onClick = (event, elements) => {
            if (elements.length > 0) {
                const element = elements[0];
                const datasetIndex = element.datasetIndex;
                const index = element.index;
                const dataset = chart.data.datasets[datasetIndex];
                const value = dataset.data[index];
                const label = chart.data.labels[index];

                this.handleChartClick(chartId, {
                    datasetIndex,
                    index,
                    value,
                    label,
                    datasetLabel: dataset.label
                });
            }
        };

        // Add hover effects
        chart.options.onHover = (event, elements) => {
            event.native.target.style.cursor = elements.length > 0 ? 'pointer' : 'default';
        };

        // Add export functionality
        this.addExportFeature(chartId);

        // Add data manipulation features
        this.addDataManipulation(chartId);
    }

    handleChartClick(chartId, data) {
        const chartData = this.charts.get(chartId);
        if (!chartData) return;

        // Show detailed information modal
        if (window.showGlobalModal) {
            showGlobalModal({
                title: `Chart Data Details`,
                content: `
                    <div class="space-y-4">
                        <div class="grid grid-cols-2 gap-4">
                            <div>
                                <h4 class="font-semibold text-neutral-900 dark:text-white">Label</h4>
                                <p class="text-neutral-600 dark:text-neutral-400">${data.label || 'N/A'}</p>
                            </div>
                            <div>
                                <h4 class="font-semibold text-neutral-900 dark:text-white">Value</h4>
                                <p class="text-neutral-600 dark:text-neutral-400">${data.value?.toLocaleString() || 'N/A'}</p>
                            </div>
                            <div>
                                <h4 class="font-semibold text-neutral-900 dark:text-white">Dataset</h4>
                                <p class="text-neutral-600 dark:text-neutral-400">${data.datasetLabel || 'N/A'}</p>
                            </div>
                            <div>
                                <h4 class="font-semibold text-neutral-900 dark:text-white">Index</h4>
                                <p class="text-neutral-600 dark:text-neutral-400">${data.index + 1}</p>
                            </div>
                        </div>

                        <div class="border-t border-neutral-200 dark:border-neutral-700 pt-4">
                            <h4 class="font-semibold text-neutral-900 dark:text-white mb-2">Quick Actions</h4>
                            <div class="flex flex-wrap gap-2">
                                <button class="btn btn-sm btn-outline-primary" onclick="ValidoAICharts.editDataPoint('${chartId}', ${data.datasetIndex}, ${data.index})">
                                    Edit Value
                                </button>
                                <button class="btn btn-sm btn-outline-info" onclick="ValidoAICharts.highlightData('${chartId}', ${data.datasetIndex}, ${data.index})">
                                    Highlight
                                </button>
                                <button class="btn btn-sm btn-outline-success" onclick="ValidoAICharts.duplicateData('${chartId}', ${data.datasetIndex}, ${data.index})">
                                    Duplicate
                                </button>
                            </div>
                        </div>
                    </div>
                `,
                size: 'max-w-md'
            });
        }
    }

    editDataPoint(chartId, datasetIndex, index) {
        const chartData = this.charts.get(chartId);
        if (!chartData) return;

        const currentValue = chartData.chart.data.datasets[datasetIndex].data[index];

        if (window.showGlobalModal) {
            showGlobalModal({
                title: 'Edit Data Point',
                content: `
                    <div class="mb-4">
                        <label class="block text-sm font-medium mb-2">New Value</label>
                        <input type="number" class="form-control" id="editValue" value="${currentValue}" step="any">
                    </div>
                `,
                actions: true,
                actionText: 'Update',
                onAction: () => {
                    const newValue = parseFloat(document.getElementById('editValue').value);
                    if (!isNaN(newValue)) {
                        chartData.chart.data.datasets[datasetIndex].data[index] = newValue;
                        chartData.chart.update();
                        if (window.showToast) {
                            showToast('success', 'Data point updated successfully');
                        }
                    }
                }
            });
        }
    }

    highlightData(chartId, datasetIndex, index) {
        const chartData = this.charts.get(chartId);
        if (!chartData) return;

        // Reset all highlights
        chartData.chart.data.datasets.forEach((dataset, dsIndex) => {
            dataset.backgroundColor = dataset.originalBackgroundColor || dataset.backgroundColor;
            dataset.borderColor = dataset.originalBorderColor || dataset.borderColor;
            dataset.borderWidth = dataset.originalBorderWidth || dataset.borderWidth;
        });

        // Highlight selected point
        const dataset = chartData.chart.data.datasets[datasetIndex];
        dataset.originalBackgroundColor = dataset.backgroundColor;
        dataset.originalBorderColor = dataset.borderColor;
        dataset.originalBorderWidth = dataset.borderWidth;

        if (Array.isArray(dataset.backgroundColor)) {
            dataset.backgroundColor = dataset.backgroundColor.map((color, i) =>
                i === index ? this.adjustColor(color, 0.7) : color
            );
        } else {
            dataset.backgroundColor = this.adjustColor(dataset.backgroundColor, 0.7);
        }

        dataset.borderColor = '#ff6b6b';
        dataset.borderWidth = 3;

        chartData.chart.update();

        if (window.showToast) {
            showToast('info', 'Data point highlighted');
        }
    }

    duplicateData(chartId, datasetIndex, index) {
        const chartData = this.charts.get(chartId);
        if (!chartData) return;

        const value = chartData.chart.data.datasets[datasetIndex].data[index];
        const label = chartData.chart.data.labels[index];

        // Add new data point
        chartData.chart.data.labels.push(`${label} (Copy)`);
        chartData.chart.data.datasets[datasetIndex].data.push(value);

        chartData.chart.update();

        if (window.showToast) {
            showToast('success', 'Data point duplicated');
        }
    }

    addExportFeature(chartId) {
        const chartData = this.charts.get(chartId);
        if (!chartData) return;

        // Add export button to chart container
        const container = document.getElementById(chartData.canvasId).parentNode;
        const exportContainer = document.createElement('div');
        exportContainer.className = 'chart-export-features mb-3';
        exportContainer.innerHTML = `
            <div class="flex flex-wrap gap-2 justify-center">
                <button class="btn btn-sm btn-outline-primary export-png" title="Export as PNG">
                    <i class="fas fa-image"></i> PNG
                </button>
                <button class="btn btn-sm btn-outline-success export-jpg" title="Export as JPG">
                    <i class="fas fa-camera"></i> JPG
                </button>
                <button class="btn btn-sm btn-outline-info export-json" title="Export as JSON">
                    <i class="fas fa-code"></i> JSON
                </button>
                <button class="btn btn-sm btn-outline-warning export-csv" title="Export as CSV">
                    <i class="fas fa-table"></i> CSV
                </button>
            </div>
        `;

        container.insertBefore(exportContainer, container.firstChild);

        // Bind export events
        exportContainer.querySelector('.export-png').onclick = () => this.exportAsImage(chartId, 'png');
        exportContainer.querySelector('.export-jpg').onclick = () => this.exportAsImage(chartId, 'jpg');
        exportContainer.querySelector('.export-json').onclick = () => this.exportAsJSON(chartId);
        exportContainer.querySelector('.export-csv').onclick = () => this.exportAsCSV(chartId);
    }

    addDataManipulation(chartId) {
        const chartData = this.charts.get(chartId);
        if (!chartData) return;

        const container = document.getElementById(chartData.canvasId).parentNode;
        const manipulationContainer = document.createElement('div');
        manipulationContainer.className = 'chart-manipulation-features mb-3';
        manipulationContainer.innerHTML = `
            <div class="row g-2">
                <div class="col-auto">
                    <button class="btn btn-sm btn-outline-secondary add-data" title="Add Data Point">
                        <i class="fas fa-plus"></i> Add Data
                    </button>
                </div>
                <div class="col-auto">
                    <button class="btn btn-sm btn-outline-warning randomize-data" title="Randomize Data">
                        <i class="fas fa-random"></i> Randomize
                    </button>
                </div>
                <div class="col-auto">
                    <button class="btn btn-sm btn-outline-info toggle-datalabels" title="Toggle Data Labels">
                        <i class="fas fa-tag"></i> Labels
                    </button>
                </div>
                <div class="col-auto">
                    <button class="btn btn-sm btn-outline-success animate-chart" title="Animate Chart">
                        <i class="fas fa-play"></i> Animate
                    </button>
                </div>
            </div>
        `;

        container.appendChild(manipulationContainer);

        // Bind manipulation events
        manipulationContainer.querySelector('.add-data').onclick = () => this.addDataPoint(chartId);
        manipulationContainer.querySelector('.randomize-data').onclick = () => this.randomizeData(chartId);
        manipulationContainer.querySelector('.toggle-datalabels').onclick = () => this.toggleDataLabels(chartId);
        manipulationContainer.querySelector('.animate-chart').onclick = () => this.animateChart(chartId);
    }

    addDataPoint(chartId) {
        const chartData = this.charts.get(chartId);
        if (!chartData) return;

        if (window.showGlobalModal) {
            showGlobalModal({
                title: 'Add Data Point',
                content: `
                    <div class="row g-3">
                        <div class="col-12">
                            <label class="form-label">Label</label>
                            <input type="text" class="form-control" id="newLabel" placeholder="Enter label">
                        </div>
                        <div class="col-12">
                            <label class="form-label">Value</label>
                            <input type="number" class="form-control" id="newValue" placeholder="Enter value">
                        </div>
                        <div class="col-12">
                            <label class="form-label">Dataset</label>
                            <select class="form-select" id="datasetSelect">
                                ${chartData.chart.data.datasets.map((ds, i) => `<option value="${i}">${ds.label || 'Dataset ' + (i + 1)}</option>`).join('')}
                            </select>
                        </div>
                    </div>
                `,
                actions: true,
                actionText: 'Add',
                onAction: () => {
                    const label = document.getElementById('newLabel').value;
                    const value = parseFloat(document.getElementById('newValue').value);
                    const datasetIndex = parseInt(document.getElementById('datasetSelect').value);

                    if (label && !isNaN(value)) {
                        chartData.chart.data.labels.push(label);
                        chartData.chart.data.datasets[datasetIndex].data.push(value);
                        chartData.chart.update();

                        if (window.showToast) {
                            showToast('success', 'Data point added successfully');
                        }
                    }
                }
            });
        }
    }

    randomizeData(chartId) {
        const chartData = this.charts.get(chartId);
        if (!chartData) return;

        chartData.chart.data.datasets.forEach(dataset => {
            dataset.data = dataset.data.map(() => Math.floor(Math.random() * 1000));
        });

        chartData.chart.update();

        if (window.showToast) {
            showToast('info', 'Data randomized');
        }
    }

    toggleDataLabels(chartId) {
        const chartData = this.charts.get(chartId);
        if (!chartData) return;

        const currentDisplay = chartData.chart.options.plugins.datalabels.display;
        chartData.chart.options.plugins.datalabels.display = !currentDisplay;
        chartData.chart.update();

        if (window.showToast) {
            showToast('info', `Data labels ${!currentDisplay ? 'enabled' : 'disabled'}`);
        }
    }

    animateChart(chartId) {
        const chartData = this.charts.get(chartId);
        if (!chartData) return;

        // Create a bounce animation
        const originalData = JSON.parse(JSON.stringify(chartData.chart.data.datasets));

        chartData.chart.data.datasets.forEach((dataset, dsIndex) => {
            dataset.data = dataset.data.map((value, index) => {
                return { original: value, current: 0 };
            });
        });

        chartData.chart.update();

        let progress = 0;
        const duration = 1000;
        const startTime = Date.now();

        const animate = () => {
            const elapsed = Date.now() - startTime;
            progress = Math.min(elapsed / duration, 1);

            const easeOutBounce = (t) => {
                const n1 = 7.5625;
                const d1 = 2.75;

                if (t < 1 / d1) {
                    return n1 * t * t;
                } else if (t < 2 / d1) {
                    return n1 * (t -= 1.5 / d1) * t + 0.75;
                } else if (t < 2.5 / d1) {
                    return n1 * (t -= 2.25 / d1) * t + 0.9375;
                } else {
                    return n1 * (t -= 2.625 / d1) * t + 0.984375;
                }
            };

            const easedProgress = easeOutBounce(progress);

            chartData.chart.data.datasets.forEach((dataset, dsIndex) => {
                dataset.data = dataset.data.map((item, index) => {
                    const target = originalData[dsIndex].data[index];
                    return item.original * easedProgress;
                });
            });

            chartData.chart.update();

            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };

        requestAnimationFrame(animate);

        if (window.showToast) {
            showToast('success', 'Chart animated!');
        }
    }

    exportAsImage(chartId, format = 'png') {
        const chartData = this.charts.get(chartId);
        if (!chartData) return;

        const link = document.createElement('a');
        link.download = `chart.${format}`;
        link.href = chartData.chart.toBase64Image(`image/${format}`, 1);
        link.click();

        if (window.showToast) {
            showToast('success', `Chart exported as ${format.toUpperCase()}`);
        }
    }

    exportAsJSON(chartId) {
        const chartData = this.charts.get(chartId);
        if (!chartData) return;

        const data = {
            type: chartData.type,
            labels: chartData.chart.data.labels,
            datasets: chartData.chart.data.datasets.map(ds => ({
                label: ds.label,
                data: ds.data,
                backgroundColor: ds.backgroundColor,
                borderColor: ds.borderColor,
                borderWidth: ds.borderWidth
            }))
        };

        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.download = 'chart-data.json';
        link.href = url;
        link.click();
        URL.revokeObjectURL(url);

        if (window.showToast) {
            showToast('success', 'Chart data exported as JSON');
        }
    }

    exportAsCSV(chartId) {
        const chartData = this.charts.get(chartId);
        if (!chartData) return;

        let csv = 'Label,' + chartData.chart.data.datasets.map(ds => ds.label || 'Dataset').join(',') + '\n';

        chartData.chart.data.labels.forEach((label, index) => {
            let row = label;
            chartData.chart.data.datasets.forEach(dataset => {
                row += ',' + (dataset.data[index] || '');
            });
            csv += row + '\n';
        });

        const blob = new Blob([csv], { type: 'text/csv' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.download = 'chart-data.csv';
        link.href = url;
        link.click();
        URL.revokeObjectURL(url);

        if (window.showToast) {
            showToast('success', 'Chart data exported as CSV');
        }
    }

    applyThemeIntegration(chartId) {
        const chartData = this.charts.get(chartId);
        if (!chartData) return;

        // Listen for theme changes
        document.addEventListener('themeChanged', (event) => {
            this.updateChartTheme(chartId, event.detail.theme);
        });

        // Initial theme application
        const currentTheme = localStorage.getItem('valido-theme') || 'valido-white';
        this.updateChartTheme(chartId, currentTheme);
    }

    updateChartTheme(chartId, theme) {
        const chartData = this.charts.get(chartId);
        if (!chartData) return;

        const chart = chartData.chart;
        const isDark = ['valido-dark', 'material-dark', 'dracula', 'monokai'].includes(theme);

        // Update chart colors
        const textColor = isDark ? '#f9fafb' : '#374151';
        const gridColor = isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)';
        const borderColor = isDark ? 'rgba(255, 255, 255, 0.2)' : 'rgba(0, 0, 0, 0.2)';

        if (chart.options.scales) {
            if (chart.options.scales.y) {
                chart.options.scales.y.grid.color = gridColor;
                chart.options.scales.y.grid.borderColor = borderColor;
                chart.options.scales.y.ticks.color = textColor;
            }
            if (chart.options.scales.x) {
                chart.options.scales.x.grid.color = gridColor;
                chart.options.scales.x.ticks.color = textColor;
            }
        }

        // Update legend and tooltip
        if (chart.options.plugins) {
            if (chart.options.plugins.legend) {
                chart.options.plugins.legend.labels.color = textColor;
            }
            if (chart.options.plugins.tooltip) {
                chart.options.plugins.tooltip.backgroundColor = isDark ? 'rgba(31, 41, 55, 0.9)' : 'rgba(0, 0, 0, 0.8)';
                chart.options.plugins.tooltip.titleColor = textColor;
                chart.options.plugins.tooltip.bodyColor = textColor;
            }
            if (chart.options.plugins.datalabels) {
                chart.options.plugins.datalabels.color = textColor;
            }
        }

        // Update button styles
        const container = document.getElementById(chartData.canvasId).parentNode;
        container.classList.toggle('chart-theme-dark', isDark);

        chart.update();
    }

    adjustColor(color, factor) {
        // Simple color adjustment for highlighting
        if (typeof color === 'string' && color.startsWith('#')) {
            const r = parseInt(color.slice(1, 3), 16);
            const g = parseInt(color.slice(3, 5), 16);
            const b = parseInt(color.slice(5, 7), 16);

            const newR = Math.min(255, Math.floor(r * factor));
            const newG = Math.min(255, Math.floor(g * factor));
            const newB = Math.min(255, Math.floor(b * factor));

            return `#${newR.toString(16).padStart(2, '0')}${newG.toString(16).padStart(2, '0')}${newB.toString(16).padStart(2, '0')}`;
        }
        return color;
    }

    generateId() {
        return 'chart_' + Math.random().toString(36).substr(2, 9);
    }

    destroy(chartId) {
        const chartData = this.charts.get(chartId);
        if (chartData) {
            chartData.chart.destroy();
            this.charts.delete(chartId);
        }
    }

    update(chartId) {
        const chartData = this.charts.get(chartId);
        if (chartData) {
            chartData.chart.update();
        }
    }

    getChart(chartId) {
        const chartData = this.charts.get(chartId);
        return chartData ? chartData.chart : null;
    }

    // Utility methods for creating common chart types
    createBarChart(canvasId, data, options = {}) {
        return this.createChart(canvasId, 'bar', data, options);
    }

    createLineChart(canvasId, data, options = {}) {
        return this.createChart(canvasId, 'line', data, options);
    }

    createPieChart(canvasId, data, options = {}) {
        return this.createChart(canvasId, 'pie', data, options);
    }

    createDoughnutChart(canvasId, data, options = {}) {
        return this.createChart(canvasId, 'doughnut', data, options);
    }

    createRadarChart(canvasId, data, options = {}) {
        return this.createChart(canvasId, 'radar', data, options);
    }

    createAreaChart(canvasId, data, options = {}) {
        const areaOptions = {
            ...options,
            fill: true,
            interaction: {
                intersect: false,
                mode: 'index'
            }
        };
        return this.createChart(canvasId, 'line', data, areaOptions);
    }
}

// Global instance
window.ValidoAICharts = new ValidoAICharts();
