/**
 * Valido White Theme - JavaScript
 * Interactive functionality and theme-specific behaviors
 */

class ValidoWhiteTheme {
    constructor() {
        this.themeName = 'valido-white';
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.initializeComponents();
        this.setupAnimations();
        this.setupAccessibility();
    }

    setupEventListeners() {
        // Theme switching
        document.addEventListener('DOMContentLoaded', () => {
            this.setupThemeSwitcher();
            this.setupSidebarToggle();
            this.setupModalSystem();
            this.setupToastSystem();
            this.setupFormValidation();
            this.setupNavigation();
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            this.handleKeyboardShortcuts(e);
        });

        // Responsive behavior
        window.addEventListener('resize', () => {
            this.handleResize();
        });
    }

    setupThemeSwitcher() {
        const themeButtons = document.querySelectorAll('[onclick*="switchTheme"]');
        themeButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                const themeName = button.getAttribute('data-theme') || 'valido-white';
                this.switchTheme(themeName);
            });
        });
    }

    switchTheme(themeName) {
        // Update theme CSS
        const themeCss = document.getElementById('theme-css');
        if (themeCss) {
            themeCss.href = `/static/themes/${themeName}/css/theme.css`;
        }

        // Update theme JS
        this.loadThemeScript(themeName);

        // Update theme images
        this.loadThemeImages(themeName);

        // Update theme fonts
        this.loadThemeFonts(themeName);

        // Update document attributes
        document.documentElement.setAttribute('data-theme', themeName);
        
        // Save to localStorage
        localStorage.setItem('valido-theme', themeName);

        // Trigger theme change event
        this.triggerThemeChangeEvent(themeName);

        // Show success toast
        this.showToast('success', `Theme switched to ${themeName}`);
    }

    loadThemeScript(themeName) {
        const existingScript = document.getElementById('theme-script');
        if (existingScript) {
            existingScript.remove();
        }

        const script = document.createElement('script');
        script.id = 'theme-script';
        script.src = `/static/themes/${themeName}/js/theme.js`;
        script.onload = () => {
            console.log(`Theme script loaded: ${themeName}`);
        };
        document.head.appendChild(script);
    }

    loadThemeImages(themeName) {
        // Update logo and theme-specific images
        const logo = document.querySelector('.logo img');
        if (logo) {
            logo.src = `/static/themes/${themeName}/images/logo.svg`;
        }

        // Update other theme-specific images
        const themeImages = document.querySelectorAll('[data-theme-image]');
        themeImages.forEach(img => {
            const imageName = img.getAttribute('data-theme-image');
            img.src = `/static/themes/${themeName}/images/${imageName}`;
        });
    }

    loadThemeFonts(themeName) {
        // Load theme-specific fonts
        const fontLink = document.createElement('link');
        fontLink.rel = 'stylesheet';
        fontLink.href = `/static/themes/${themeName}/fonts/fonts.css`;
        document.head.appendChild(fontLink);
    }

    triggerThemeChangeEvent(themeName) {
        const event = new CustomEvent('themeChanged', {
            detail: { theme: themeName }
        });
        document.dispatchEvent(event);
    }

    setupSidebarToggle() {
        const sidebarToggle = document.querySelector('[onclick*="toggleSidebar"]');
        if (sidebarToggle) {
            sidebarToggle.addEventListener('click', (e) => {
                e.preventDefault();
                this.toggleSidebar();
            });
        }
    }

    toggleSidebar() {
        const sidebar = document.getElementById('sidebar');
        const overlay = document.getElementById('mobile-overlay');
        
        if (sidebar && overlay) {
            if (sidebar.classList.contains('-translate-x-full')) {
                sidebar.classList.remove('-translate-x-full');
                overlay.classList.remove('hidden');
                sidebar.classList.add('animate-slide-in-left');
            } else {
                sidebar.classList.add('-translate-x-full');
                overlay.classList.add('hidden');
                sidebar.classList.add('animate-slide-out-left');
            }
        }
    }

    setupModalSystem() {
        // Modal triggers
        const modalTriggers = document.querySelectorAll('[onclick*="showModal"]');
        modalTriggers.forEach(trigger => {
            trigger.addEventListener('click', (e) => {
                e.preventDefault();
                const modalType = trigger.getAttribute('data-modal') || 'default';
                this.showModal(modalType);
            });
        });

        // Modal close
        const modalClose = document.querySelectorAll('[onclick*="hideModal"]');
        modalClose.forEach(close => {
            close.addEventListener('click', (e) => {
                e.preventDefault();
                this.hideModal();
            });
        });
    }

    showModal(modalType) {
        const modalContainer = document.getElementById('modal-container');
        const modalContent = document.getElementById('modal-content');
        
        if (modalContainer && modalContent) {
            // Load modal content based on type
            this.loadModalContent(modalType, modalContent);
            
            // Show modal with animation
            modalContainer.classList.remove('hidden');
            modalContainer.classList.add('animate-fade-in');
        }
    }

    loadModalContent(modalType, modalContent) {
        const modalTemplates = {
            'quick-actions': this.getQuickActionsModal(),
            'dashboard-examples': this.getDashboardExamplesModal(),
            'settings': this.getSettingsModal(),
            'profile': this.getProfileModal()
        };

        const template = modalTemplates[modalType] || modalTemplates['quick-actions'];
        modalContent.innerHTML = template;
    }

    getQuickActionsModal() {
        return `
            <div class="p-6">
                <h3 class="text-lg font-semibold text-neutral-900 mb-4">Quick Actions</h3>
                <div class="space-y-3">
                    <button onclick="validoTheme.showToast('success', 'New transaction created')" 
                            class="w-full text-left p-3 rounded-lg border border-neutral-200 hover:bg-neutral-50 transition-colors duration-200">
                        <i class="fas fa-plus mr-2 text-primary-600"></i>
                        New Transaction
                    </button>
                    <button onclick="validoTheme.showToast('info', 'Report generated')" 
                            class="w-full text-left p-3 rounded-lg border border-neutral-200 hover:bg-neutral-50 transition-colors duration-200">
                        <i class="fas fa-file-alt mr-2 text-primary-600"></i>
                        Generate Report
                    </button>
                    <button onclick="validoTheme.showToast('warning', 'Backup started')" 
                            class="w-full text-left p-3 rounded-lg border border-neutral-200 hover:bg-neutral-50 transition-colors duration-200">
                        <i class="fas fa-download mr-2 text-primary-600"></i>
                        Backup Data
                    </button>
                </div>
                <div class="mt-6 flex justify-end">
                    <button onclick="validoTheme.hideModal()" 
                            class="px-4 py-2 text-neutral-600 hover:text-neutral-900 transition-colors duration-200">
                        Close
                    </button>
                </div>
            </div>
        `;
    }

    getDashboardExamplesModal() {
        return `
            <div class="p-6">
                <h3 class="text-lg font-semibold text-neutral-900 mb-4">Dashboard Examples</h3>
                <div class="space-y-3">
                    <a href="/dashboard/banking" 
                       class="block p-3 rounded-lg border border-neutral-200 hover:bg-neutral-50 transition-colors duration-200">
                        <i class="fas fa-university mr-2 text-primary-600"></i>
                        Banking Dashboard
                    </a>
                    <a href="/dashboard/compact" 
                       class="block p-3 rounded-lg border border-neutral-200 hover:bg-neutral-50 transition-colors duration-200">
                        <i class="fas fa-compress-alt mr-2 text-primary-600"></i>
                        Compact Dashboard
                    </a>
                    <a href="/dashboard" 
                       class="block p-3 rounded-lg border border-neutral-200 hover:bg-neutral-50 transition-colors duration-200">
                        <i class="fas fa-chart-line mr-2 text-primary-600"></i>
                        Overview Dashboard
                    </a>
                </div>
                <div class="mt-6 flex justify-end">
                    <button onclick="validoTheme.hideModal()" 
                            class="px-4 py-2 text-neutral-600 hover:text-neutral-900 transition-colors duration-200">
                        Close
                    </button>
                </div>
            </div>
        `;
    }

    hideModal() {
        const modalContainer = document.getElementById('modal-container');
        if (modalContainer) {
            modalContainer.classList.add('hidden');
        }
    }

    setupToastSystem() {
        // Toast container setup
        if (!document.getElementById('toast-container')) {
            const toastContainer = document.createElement('div');
            toastContainer.id = 'toast-container';
            toastContainer.className = 'fixed top-4 right-4 z-50 space-y-2';
            document.body.appendChild(toastContainer);
        }
    }

    showToast(type, message, duration = 5000) {
        const toastContainer = document.getElementById('toast-container');
        if (!toastContainer) return;

        const toast = document.createElement('div');
        const colors = {
            success: 'bg-success-50 text-success-700 border-success-200',
            error: 'bg-danger-50 text-danger-700 border-danger-200',
            warning: 'bg-warning-50 text-warning-700 border-warning-200',
            info: 'bg-primary-50 text-primary-700 border-primary-200'
        };
        
        toast.className = `p-4 rounded-lg border ${colors[type]} shadow-lg animate-slide-up`;
        toast.innerHTML = `
            <div class="flex items-center justify-between">
                <span>${message}</span>
                <button onclick="this.parentElement.parentElement.remove()" 
                        class="ml-4 text-current hover:opacity-75">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        toastContainer.appendChild(toast);
        
        // Auto-remove after duration
        setTimeout(() => {
            if (toast.parentElement) {
                toast.remove();
            }
        }, duration);
    }

    setupFormValidation() {
        // Real-time form validation
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            const inputs = form.querySelectorAll('input, textarea, select');
            inputs.forEach(input => {
                input.addEventListener('blur', () => {
                    this.validateField(input);
                });
                
                input.addEventListener('input', () => {
                    this.clearFieldError(input);
                });
            });

            form.addEventListener('submit', (e) => {
                if (!this.validateForm(form)) {
                    e.preventDefault();
                }
            });
        });
    }

    validateField(field) {
        const value = field.value.trim();
        const type = field.type;
        const required = field.hasAttribute('required');
        
        // Clear previous errors
        this.clearFieldError(field);
        
        // Required validation
        if (required && !value) {
            this.showFieldError(field, 'This field is required');
            return false;
        }
        
        // Type-specific validation
        if (value) {
            switch (type) {
                case 'email':
                    if (!this.isValidEmail(value)) {
                        this.showFieldError(field, 'Please enter a valid email address');
                        return false;
                    }
                    break;
                case 'url':
                    if (!this.isValidUrl(value)) {
                        this.showFieldError(field, 'Please enter a valid URL');
                        return false;
                    }
                    break;
                case 'number':
                    if (isNaN(value)) {
                        this.showFieldError(field, 'Please enter a valid number');
                        return false;
                    }
                    break;
            }
        }
        
        return true;
    }

    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    isValidUrl(url) {
        try {
            new URL(url);
            return true;
        } catch {
            return false;
        }
    }

    showFieldError(field, message) {
        field.classList.add('border-danger-500');
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'text-danger-600 text-sm mt-1';
        errorDiv.textContent = message;
        errorDiv.id = `${field.id}-error`;
        
        field.parentNode.appendChild(errorDiv);
    }

    clearFieldError(field) {
        field.classList.remove('border-danger-500');
        
        const errorDiv = document.getElementById(`${field.id}-error`);
        if (errorDiv) {
            errorDiv.remove();
        }
    }

    validateForm(form) {
        const inputs = form.querySelectorAll('input, textarea, select');
        let isValid = true;
        
        inputs.forEach(input => {
            if (!this.validateField(input)) {
                isValid = false;
            }
        });
        
        return isValid;
    }

    setupNavigation() {
        // Active navigation highlighting
        const currentPath = window.location.pathname;
        const navLinks = document.querySelectorAll('.nav-link');
        
        navLinks.forEach(link => {
            if (link.getAttribute('href') === currentPath) {
                link.classList.add('active');
            }
        });

        // Smooth scrolling for anchor links
        const anchorLinks = document.querySelectorAll('a[href^="#"]');
        anchorLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const target = document.querySelector(link.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth' });
                }
            });
        });
    }

    setupAnimations() {
        // Intersection Observer for scroll animations
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-fade-in');
                }
            });
        }, observerOptions);

        // Observe elements with animation classes
        const animatedElements = document.querySelectorAll('.animate-on-scroll');
        animatedElements.forEach(el => observer.observe(el));
    }

    setupAccessibility() {
        // Skip navigation functionality
        const skipLink = document.querySelector('a[href="#main-content"]');
        if (skipLink) {
            skipLink.addEventListener('click', (e) => {
                e.preventDefault();
                const mainContent = document.getElementById('main-content');
                if (mainContent) {
                    mainContent.focus();
                    mainContent.scrollIntoView({ behavior: 'smooth' });
                }
            });
        }

        // ARIA live regions for dynamic content
        const liveRegion = document.createElement('div');
        liveRegion.setAttribute('aria-live', 'polite');
        liveRegion.setAttribute('aria-atomic', 'true');
        liveRegion.className = 'sr-only';
        document.body.appendChild(liveRegion);
    }

    handleKeyboardShortcuts(e) {
        // Ctrl/Cmd + K for search
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.querySelector('input[placeholder*="Search"]');
            if (searchInput) {
                searchInput.focus();
            }
        }

        // Escape key to close modals
        if (e.key === 'Escape') {
            this.hideModal();
        }

        // Ctrl/Cmd + T for theme switcher
        if ((e.ctrlKey || e.metaKey) && e.key === 't') {
            e.preventDefault();
            const themeButton = document.querySelector('[onclick*="switchTheme"]');
            if (themeButton) {
                themeButton.click();
            }
        }
    }

    handleResize() {
        // Handle responsive behavior
        const sidebar = document.getElementById('sidebar');
        const overlay = document.getElementById('mobile-overlay');
        
        if (window.innerWidth >= 1024) {
            // Desktop: show sidebar
            if (sidebar) {
                sidebar.classList.remove('-translate-x-full');
            }
            if (overlay) {
                overlay.classList.add('hidden');
            }
        } else {
            // Mobile: hide sidebar
            if (sidebar) {
                sidebar.classList.add('-translate-x-full');
            }
            if (overlay) {
                overlay.classList.add('hidden');
            }
        }
    }

    initializeComponents() {
        // Initialize tooltips
        this.initializeTooltips();
        
        // Initialize dropdowns
        this.initializeDropdowns();
        
        // Initialize tabs
        this.initializeTabs();
    }

    initializeTooltips() {
        const tooltipElements = document.querySelectorAll('[data-tooltip]');
        tooltipElements.forEach(element => {
            element.addEventListener('mouseenter', (e) => {
                this.showTooltip(e.target);
            });
            
            element.addEventListener('mouseleave', (e) => {
                this.hideTooltip(e.target);
            });
        });
    }

    showTooltip(element) {
        const tooltipText = element.getAttribute('data-tooltip');
        const tooltip = document.createElement('div');
        tooltip.className = 'absolute z-50 px-2 py-1 text-xs text-white bg-neutral-900 rounded shadow-lg opacity-0 pointer-events-none transition-opacity duration-200';
        tooltip.textContent = tooltipText;
        tooltip.id = 'tooltip';
        
        document.body.appendChild(tooltip);
        
        const rect = element.getBoundingClientRect();
        tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
        tooltip.style.top = rect.top - tooltip.offsetHeight - 5 + 'px';
        
        setTimeout(() => {
            tooltip.classList.remove('opacity-0');
        }, 10);
    }

    hideTooltip(element) {
        const tooltip = document.getElementById('tooltip');
        if (tooltip) {
            tooltip.remove();
        }
    }

    initializeDropdowns() {
        const dropdowns = document.querySelectorAll('[data-dropdown]');
        dropdowns.forEach(dropdown => {
            const trigger = dropdown.querySelector('[data-dropdown-trigger]');
            const content = dropdown.querySelector('[data-dropdown-content]');
            
            if (trigger && content) {
                trigger.addEventListener('click', (e) => {
                    e.preventDefault();
                    this.toggleDropdown(dropdown);
                });
            }
        });
    }

    toggleDropdown(dropdown) {
        const content = dropdown.querySelector('[data-dropdown-content]');
        if (content) {
            content.classList.toggle('hidden');
        }
    }

    initializeTabs() {
        const tabContainers = document.querySelectorAll('[data-tabs]');
        tabContainers.forEach(container => {
            const tabs = container.querySelectorAll('[data-tab]');
            const contents = container.querySelectorAll('[data-tab-content]');
            
            tabs.forEach(tab => {
                tab.addEventListener('click', (e) => {
                    e.preventDefault();
                    const target = tab.getAttribute('data-tab');
                    this.switchTab(container, target);
                });
            });
        });
    }

    switchTab(container, targetTab) {
        const tabs = container.querySelectorAll('[data-tab]');
        const contents = container.querySelectorAll('[data-tab-content]');
        
        // Remove active classes
        tabs.forEach(tab => tab.classList.remove('active'));
        contents.forEach(content => content.classList.add('hidden'));
        
        // Add active classes
        const activeTab = container.querySelector(`[data-tab="${targetTab}"]`);
        const activeContent = container.querySelector(`[data-tab-content="${targetTab}"]`);
        
        if (activeTab) activeTab.classList.add('active');
        if (activeContent) activeContent.classList.remove('hidden');
    }
}

// Initialize theme when DOM is loaded
let validoTheme;
document.addEventListener('DOMContentLoaded', () => {
    validoTheme = new ValidoWhiteTheme();
});

// Export for global access
window.ValidoWhiteTheme = ValidoWhiteTheme;
window.validoTheme = validoTheme;
