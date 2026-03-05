/**
 * AI Valido Design System JavaScript
 * Handles performance optimizations, lazy loading, and component interactions
 */

// Performance optimization: Use requestIdleCallback for non-critical tasks
const requestIdleCallback = window.requestIdleCallback || ((callback) => setTimeout(callback, 1));

// Design System Class
class ValidoDesignSystem {
    constructor() {
        this.observer = null;
        this.components = new Map();
        this.init();
    }

    init() {
        // Initialize when DOM is ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setup());
        } else {
            this.setup();
        }
    }

    setup() {
        this.setupLazyLoading();
        this.setupMegaMenu();
        this.setupAccordion();
        this.setupCharts();
        this.setupPerformanceMonitoring();
        this.setupAccessibility();
    }

    // Lazy Loading with IntersectionObserver
    setupLazyLoading() {
        if (!('IntersectionObserver' in window)) {
            // Fallback for older browsers
            this.loadAllComponents();
            return;
        }

        this.observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    this.loadComponent(entry.target);
                    this.observer.unobserve(entry.target);
                }
            });
        }, {
            rootMargin: '100px',
            threshold: 0.1
        });

        // Observe all lazy-load components
        document.querySelectorAll('.lazy-load').forEach(el => {
            this.observer.observe(el);
        });
    }

    loadComponent(element) {
        const componentType = element.dataset.component;
        
        switch (componentType) {
            case 'table':
                this.loadTable(element);
                break;
            case 'chart':
                this.loadChart(element);
                break;
            case 'image':
                this.loadImage(element);
                break;
            default:
                element.classList.remove('hidden');
        }
    }

    loadTable(element) {
        const table = element.querySelector('table');
        if (table) {
            table.classList.remove('hidden');
            this.addTableSorting(table);
        }
    }

    loadChart(element) {
        const chartId = element.dataset.chartId;
        const chartData = element.dataset.chartData;
        
        if (chartId && chartData && window.ApexCharts) {
            try {
                const config = JSON.parse(chartData);
                new ApexCharts(document.getElementById(chartId), config).render();
            } catch (error) {
                console.error('Error loading chart:', error);
            }
        }
    }

    loadImage(element) {
        const img = element.querySelector('img');
        if (img && img.dataset.src) {
            img.src = img.dataset.src;
            img.classList.remove('lazy');
        }
    }

    // Mega Menu functionality
    setupMegaMenu() {
        document.querySelectorAll('.flowbite-mega-menu-toggle').forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                const menu = button.closest('.flowbite-mega-menu');
                const content = menu.querySelector('.mega-menu-content');
                
                // Close other open menus
                document.querySelectorAll('.mega-menu-content').forEach(other => {
                    if (other !== content) {
                        other.classList.add('hidden');
                        other.previousElementSibling.setAttribute('aria-expanded', 'false');
                    }
                });

                // Toggle current menu
                content.classList.toggle('hidden');
                const isExpanded = !content.classList.contains('hidden');
                button.setAttribute('aria-expanded', isExpanded.toString());

                // Focus management
                if (isExpanded) {
                    const firstLink = content.querySelector('a');
                    if (firstLink) firstLink.focus();
                }
            });
        });

        // Close menu when clicking outside
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.flowbite-mega-menu')) {
                document.querySelectorAll('.mega-menu-content').forEach(content => {
                    content.classList.add('hidden');
                    const button = content.previousElementSibling;
                    if (button) button.setAttribute('aria-expanded', 'false');
                });
            }
        });
    }

    // Accordion functionality
    setupAccordion() {
        document.querySelectorAll('.accordion-header').forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                const content = button.nextElementSibling;
                const isExpanded = button.getAttribute('aria-expanded') === 'true';
                
                // Close other accordion items
                const accordion = button.closest('.preline-accordion');
                if (accordion) {
                    accordion.querySelectorAll('.accordion-content').forEach(other => {
                        if (other !== content) {
                            other.classList.add('hidden');
                            other.previousElementSibling.setAttribute('aria-expanded', 'false');
                        }
                    });
                }

                // Toggle current item
                content.classList.toggle('hidden');
                button.setAttribute('aria-expanded', (!isExpanded).toString());
            });
        });
    }

    // Chart initialization
    setupCharts() {
        if (typeof ApexCharts !== 'undefined') {
            document.querySelectorAll('[data-chart]').forEach(element => {
                const chartType = element.dataset.chart;
                const chartData = element.dataset.chartData;
                
                if (chartData) {
                    try {
                        const config = JSON.parse(chartData);
                        new ApexCharts(element, config).render();
                    } catch (error) {
                        console.error('Error initializing chart:', error);
                    }
                }
            });
        }
    }

    // Performance monitoring
    setupPerformanceMonitoring() {
        // Monitor Core Web Vitals
        if ('PerformanceObserver' in window) {
            // Largest Contentful Paint
            const lcpObserver = new PerformanceObserver((list) => {
                const entries = list.getEntries();
                const lastEntry = entries[entries.length - 1];
                console.log('LCP:', lastEntry.startTime);
            });
            lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] });

            // First Input Delay
            const fidObserver = new PerformanceObserver((list) => {
                const entries = list.getEntries();
                entries.forEach(entry => {
                    console.log('FID:', entry.processingStart - entry.startTime);
                });
            });
            fidObserver.observe({ entryTypes: ['first-input'] });

            // Cumulative Layout Shift
            const clsObserver = new PerformanceObserver((list) => {
                let clsValue = 0;
                const entries = list.getEntries();
                entries.forEach(entry => {
                    if (!entry.hadRecentInput) {
                        clsValue += entry.value;
                    }
                });
                console.log('CLS:', clsValue);
            });
            clsObserver.observe({ entryTypes: ['layout-shift'] });
        }
    }

    // Accessibility enhancements
    setupAccessibility() {
        // Skip link functionality
        const skipLink = document.querySelector('.skip-link');
        if (skipLink) {
            skipLink.addEventListener('click', (e) => {
                e.preventDefault();
                const target = document.querySelector(skipLink.getAttribute('href'));
                if (target) {
                    target.focus();
                    target.scrollIntoView();
                }
            });
        }

        // Keyboard navigation for custom components
        document.addEventListener('keydown', (e) => {
            // Escape key closes modals and menus
            if (e.key === 'Escape') {
                document.querySelectorAll('.mega-menu-content, .modal').forEach(el => {
                    el.classList.add('hidden');
                });
            }
        });

        // Focus management for modals
        document.querySelectorAll('[data-modal]').forEach(button => {
            button.addEventListener('click', () => {
                const modalId = button.dataset.modal;
                const modal = document.getElementById(modalId);
                if (modal) {
                    const focusableElements = modal.querySelectorAll(
                        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
                    );
                    if (focusableElements.length > 0) {
                        focusableElements[0].focus();
                    }
                }
            });
        });
    }

    // Utility methods
    addTableSorting(table) {
        const headers = table.querySelectorAll('th[data-sortable]');
        headers.forEach(header => {
            header.addEventListener('click', () => {
                const column = header.cellIndex;
                const tbody = table.querySelector('tbody');
                const rows = Array.from(tbody.querySelectorAll('tr'));
                
                rows.sort((a, b) => {
                    const aValue = a.cells[column].textContent;
                    const bValue = b.cells[column].textContent;
                    return aValue.localeCompare(bValue);
                });
                
                rows.forEach(row => tbody.appendChild(row));
            });
        });
    }

    loadAllComponents() {
        document.querySelectorAll('.lazy-load').forEach(el => {
            this.loadComponent(el);
        });
    }

    // Public API
    static getInstance() {
        if (!window.validoDesignSystem) {
            window.validoDesignSystem = new ValidoDesignSystem();
        }
        return window.validoDesignSystem;
    }
}

// Initialize design system
document.addEventListener('DOMContentLoaded', () => {
    ValidoDesignSystem.getInstance();
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ValidoDesignSystem;
}
