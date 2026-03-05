/**
 * Valido Dark Theme - JavaScript
 * Interactive functionality and theme-specific behaviors
 */

class ValidoDarkTheme {
    constructor() {
        this.themeName = 'valido-dark';
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.initializeComponents();
        this.setupAnimations();
        this.setupAccessibility();
        this.setupDarkModeFeatures();
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
            this.setupDarkModeToggle();
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            this.handleKeyboardShortcuts(e);
        });

        // Responsive behavior
        window.addEventListener('resize', () => {
            this.handleResize();
        });

        // System theme preference changes
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
            this.handleSystemThemeChange(e);
        });
    }

    setupDarkModeFeatures() {
        // Add dark mode specific features
        this.setupDarkModeOptimizations();
        this.setupDarkModeAnimations();
        this.setupDarkModeAccessibility();
    }

    setupDarkModeOptimizations() {
        // Optimize for dark mode performance
        document.documentElement.style.colorScheme = 'dark';
        
        // Reduce motion for dark mode if preferred
        if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
            document.documentElement.classList.add('reduce-motion');
        }
    }

    setupDarkModeAnimations() {
        // Dark mode specific animations
        const darkModeAnimations = {
            'fade-in-dark': 'fadeInDark 0.3s ease-out',
            'slide-up-dark': 'slideUpDark 0.3s ease-out',
            'glow-effect': 'glowEffect 2s ease-in-out infinite alternate'
        };

        // Add custom keyframes for dark mode
        const style = document.createElement('style');
        style.textContent = `
            @keyframes fadeInDark {
                from { opacity: 0; background-color: rgba(15, 23, 42, 0.8); }
                to { opacity: 1; background-color: rgba(15, 23, 42, 1); }
            }
            
            @keyframes slideUpDark {
                from { transform: translateY(20px); opacity: 0; }
                to { transform: translateY(0); opacity: 1; }
            }
            
            @keyframes glowEffect {
                from { box-shadow: 0 0 5px rgba(59, 130, 246, 0.3); }
                to { box-shadow: 0 0 20px rgba(59, 130, 246, 0.6); }
            }
        `;
        document.head.appendChild(style);
    }

    setupDarkModeAccessibility() {
        // Enhanced accessibility for dark mode
        this.setupHighContrastMode();
        this.setupFocusIndicators();
        this.setupScreenReaderSupport();
    }

    setupHighContrastMode() {
        // Check for high contrast preference
        if (window.matchMedia('(prefers-contrast: high)').matches) {
            document.documentElement.classList.add('high-contrast');
        }
    }

    setupFocusIndicators() {
        // Enhanced focus indicators for dark mode
        const focusableElements = document.querySelectorAll('a, button, input, textarea, select, [tabindex]');
        
        focusableElements.forEach(element => {
            element.addEventListener('focus', () => {
                element.style.outline = '2px solid #3b82f6';
                element.style.outlineOffset = '2px';
            });
            
            element.addEventListener('blur', () => {
                element.style.outline = '';
                element.style.outlineOffset = '';
            });
        });
    }

    setupScreenReaderSupport() {
        // Enhanced screen reader support for dark mode
        const announcements = document.createElement('div');
        announcements.setAttribute('aria-live', 'polite');
        announcements.setAttribute('aria-atomic', 'true');
        announcements.className = 'sr-only';
        document.body.appendChild(announcements);
    }

    setupDarkModeToggle() {
        // Dark mode toggle functionality
        const darkModeToggle = document.querySelector('[data-dark-mode-toggle]');
        if (darkModeToggle) {
            darkModeToggle.addEventListener('click', () => {
                this.toggleDarkMode();
            });
        }
    }

    toggleDarkMode() {
        const isDark = document.documentElement.getAttribute('data-theme') === 'valido-dark';
        const newTheme = isDark ? 'valido-white' : 'valido-dark';
        
        // Switch theme
        if (typeof switchTheme === 'function') {
            switchTheme(newTheme);
        }
        
        // Announce to screen readers
        this.announceToScreenReader(`Switched to ${newTheme} theme`);
    }

    handleSystemThemeChange(event) {
        // Handle system theme preference changes
        const prefersDark = event.matches;
        const currentTheme = localStorage.getItem('valido-theme') || 'valido-white';
        
        // Only auto-switch if user hasn't manually set a preference
        if (!localStorage.getItem('valido-theme-manual')) {
            const newTheme = prefersDark ? 'valido-dark' : 'valido-white';
            if (typeof switchTheme === 'function') {
                switchTheme(newTheme);
            }
        }
    }

    announceToScreenReader(message) {
        const announcements = document.querySelector('[aria-live="polite"]');
        if (announcements) {
            announcements.textContent = message;
            setTimeout(() => {
                announcements.textContent = '';
            }, 1000);
        }
    }

    setupThemeSwitcher() {
        const themeButtons = document.querySelectorAll('[onclick*="switchTheme"]');
        themeButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                const themeName = button.getAttribute('data-theme') || 'valido-dark';
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

        // Update theme fonts
        const themeFonts = document.getElementById('theme-fonts');
        if (themeFonts) {
            themeFonts.href = `/static/themes/${themeName}/fonts/fonts.css`;
        }

        // Update theme JS
        this.loadThemeScript(themeName);

        // Update theme images
        this.loadThemeImages(themeName);

        // Update document attributes
        document.documentElement.setAttribute('data-theme', themeName);

        // Save to localStorage
        localStorage.setItem('valido-theme', themeName);
        localStorage.setItem('valido-theme-manual', 'true');

        // Trigger theme change event
        this.triggerThemeChangeEvent(themeName);

        // Show success toast
        this.showToast('success', `Theme switched to ${themeName}`);

        // Announce to screen readers
        this.announceToScreenReader(`Theme changed to ${themeName}`);
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
        const logos = document.querySelectorAll('img[src*="valido.svg"]');
        logos.forEach(logo => {
            logo.src = `/static/themes/${themeName}/images/logo.svg`;
        });

        // Update other theme-specific images
        const themeImages = document.querySelectorAll('[data-theme-image]');
        themeImages.forEach(img => {
            const imageName = img.getAttribute('data-theme-image');
            img.src = `/static/themes/${themeName}/images/${imageName}`;
        });
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
                this.announceToScreenReader('Sidebar opened');
            } else {
                sidebar.classList.add('-translate-x-full');
                overlay.classList.add('hidden');
                this.announceToScreenReader('Sidebar closed');
            }
        }
    }

    setupModalSystem() {
        // Enhanced modal system for dark mode
        this.setupModalAccessibility();
        this.setupModalAnimations();
    }

    setupModalAccessibility() {
        // Trap focus in modals
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeActiveModal();
            }
        });
    }

    setupModalAnimations() {
        // Dark mode specific modal animations
        const modalContainer = document.getElementById('modal-container');
        if (modalContainer) {
            modalContainer.addEventListener('click', (e) => {
                if (e.target === modalContainer) {
                    this.closeActiveModal();
                }
            });
        }
    }

    closeActiveModal() {
        const modalContainer = document.getElementById('modal-container');
        if (modalContainer && !modalContainer.classList.contains('hidden')) {
            modalContainer.classList.add('hidden');
            this.announceToScreenReader('Modal closed');
        }
    }

    setupToastSystem() {
        // Enhanced toast system for dark mode
        this.setupToastAccessibility();
        this.setupToastAnimations();
    }

    setupToastAccessibility() {
        // Auto-announce toasts to screen readers
        const originalShowToast = window.showToast;
        if (originalShowToast) {
            window.showToast = (type, message) => {
                originalShowToast(type, message);
                this.announceToScreenReader(`${type}: ${message}`);
            };
        }
    }

    setupToastAnimations() {
        // Dark mode specific toast animations
        const toastContainer = document.getElementById('toast-container');
        if (toastContainer) {
            toastContainer.addEventListener('animationend', (e) => {
                if (e.animationName === 'slideUp') {
                    e.target.classList.add('toast-visible');
                }
            });
        }
    }

    setupFormValidation() {
        // Enhanced form validation for dark mode
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            form.addEventListener('submit', (e) => {
                this.validateForm(form, e);
            });
        });
    }

    validateForm(form, event) {
        const inputs = form.querySelectorAll('input, textarea, select');
        let isValid = true;

        inputs.forEach(input => {
            if (input.hasAttribute('required') && !input.value.trim()) {
                this.showFieldError(input, 'This field is required');
                isValid = false;
            } else {
                this.clearFieldError(input);
            }
        });

        if (!isValid) {
            event.preventDefault();
            this.announceToScreenReader('Form validation failed');
        }
    }

    showFieldError(input, message) {
        input.classList.add('error');
        input.setAttribute('aria-invalid', 'true');
        
        let errorElement = input.parentNode.querySelector('.field-error');
        if (!errorElement) {
            errorElement = document.createElement('div');
            errorElement.className = 'field-error text-danger-500 text-sm mt-1';
            input.parentNode.appendChild(errorElement);
        }
        errorElement.textContent = message;
    }

    clearFieldError(input) {
        input.classList.remove('error');
        input.setAttribute('aria-invalid', 'false');
        
        const errorElement = input.parentNode.querySelector('.field-error');
        if (errorElement) {
            errorElement.remove();
        }
    }

    setupNavigation() {
        // Enhanced navigation for dark mode
        this.setupKeyboardNavigation();
        this.setupActiveStateManagement();
    }

    setupKeyboardNavigation() {
        // Enhanced keyboard navigation
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Tab') {
                this.handleTabNavigation(e);
            }
        });
    }

    handleTabNavigation(event) {
        const focusableElements = document.querySelectorAll('a, button, input, textarea, select, [tabindex]:not([tabindex="-1"])');
        const firstElement = focusableElements[0];
        const lastElement = focusableElements[focusableElements.length - 1];

        if (event.shiftKey && document.activeElement === firstElement) {
            event.preventDefault();
            lastElement.focus();
        } else if (!event.shiftKey && document.activeElement === lastElement) {
            event.preventDefault();
            firstElement.focus();
        }
    }

    setupActiveStateManagement() {
        // Manage active states for navigation
        const navLinks = document.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                navLinks.forEach(l => l.classList.remove('active'));
                link.classList.add('active');
            });
        });
    }

    setupAnimations() {
        // Dark mode specific animations
        this.setupPageTransitions();
        this.setupHoverEffects();
    }

    setupPageTransitions() {
        // Smooth page transitions for dark mode
        document.addEventListener('DOMContentLoaded', () => {
            document.body.classList.add('page-loaded');
        });
    }

    setupHoverEffects() {
        // Enhanced hover effects for dark mode
        const interactiveElements = document.querySelectorAll('button, a, .card, .nav-link');
        interactiveElements.forEach(element => {
            element.addEventListener('mouseenter', () => {
                element.classList.add('hover-effect');
            });
            
            element.addEventListener('mouseleave', () => {
                element.classList.remove('hover-effect');
            });
        });
    }

    setupAccessibility() {
        // Enhanced accessibility features for dark mode
        this.setupSkipLinks();
        this.setupARIALabels();
        this.setupFocusManagement();
    }

    setupSkipLinks() {
        // Ensure skip links work properly in dark mode
        const skipLinks = document.querySelectorAll('a[href^="#"]');
        skipLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                const targetId = link.getAttribute('href').substring(1);
                const target = document.getElementById(targetId);
                if (target) {
                    e.preventDefault();
                    target.focus();
                    target.scrollIntoView();
                }
            });
        });
    }

    setupARIALabels() {
        // Add ARIA labels for better accessibility
        const buttons = document.querySelectorAll('button:not([aria-label])');
        buttons.forEach(button => {
            const icon = button.querySelector('i');
            if (icon && icon.className.includes('fa-')) {
                const action = icon.className.match(/fa-(\w+)/)?.[1];
                if (action) {
                    button.setAttribute('aria-label', action.replace('-', ' '));
                }
            }
        });
    }

    setupFocusManagement() {
        // Manage focus for better accessibility
        document.addEventListener('focusin', (e) => {
            e.target.classList.add('focused');
        });
        
        document.addEventListener('focusout', (e) => {
            e.target.classList.remove('focused');
        });
    }

    handleKeyboardShortcuts(e) {
        // Dark mode specific keyboard shortcuts
        if (e.ctrlKey || e.metaKey) {
            switch (e.key) {
                case 'k':
                    e.preventDefault();
                    this.toggleDarkMode();
                    break;
                case 'm':
                    e.preventDefault();
                    this.toggleSidebar();
                    break;
                case 'n':
                    e.preventDefault();
                    this.toggleNotifications();
                    break;
            }
        }
    }

    toggleNotifications() {
        const panel = document.getElementById('notification-panel');
        if (panel) {
            panel.classList.toggle('hidden');
            this.announceToScreenReader(
                panel.classList.contains('hidden') ? 'Notifications closed' : 'Notifications opened'
            );
        }
    }

    handleResize() {
        // Handle responsive behavior for dark mode
        const isMobile = window.innerWidth < 1024;
        const sidebar = document.getElementById('sidebar');
        const overlay = document.getElementById('mobile-overlay');

        if (isMobile && sidebar && !sidebar.classList.contains('-translate-x-full')) {
            sidebar.classList.add('-translate-x-full');
            if (overlay) overlay.classList.add('hidden');
        }
    }

    showToast(type, message) {
        // Enhanced toast for dark mode
        if (typeof window.showToast === 'function') {
            window.showToast(type, message);
        } else {
            console.log(`${type}: ${message}`);
        }
    }
}

// Initialize theme when DOM is loaded
let validoDarkTheme;
document.addEventListener('DOMContentLoaded', () => {
    validoDarkTheme = new ValidoDarkTheme();
});

// Export for global access
window.ValidoDarkTheme = ValidoDarkTheme;
window.validoDarkTheme = validoDarkTheme;
