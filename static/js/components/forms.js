/**
 * Form Component JavaScript
 * Modular JavaScript for form components - loaded on demand
 */

class FormComponent {
    constructor() {
        this.forms = new Map();
        this.autoSaveTimers = new Map();
        this.init();
    }

    init() {
        this.initFormValidation();
        this.initAutoSave();
        this.initFloatingLabels();
        this.initPasswordToggles();
        this.initFileUploads();
        this.initAutocomplete();
        this.initFormWizards();
        this.initFormAnalytics();
    }

    /**
     * Initialize form validation
     */
    initFormValidation() {
        document.addEventListener('input', (e) => {
            const input = e.target;
            if (input.closest('form')) {
                this.validateField(input);
            }
        });

        document.addEventListener('blur', (e) => {
            const input = e.target;
            if (input.closest('form')) {
                this.validateField(input);
            }
        });

        document.addEventListener('submit', (e) => {
            const form = e.target;
            if (!this.validateForm(form)) {
                e.preventDefault();
                this.showFormErrors(form);
            }
        });
    }

    /**
     * Validate a single field
     */
    validateField(field) {
        const rules = this.getValidationRules(field);
        const value = field.value.trim();
        let isValid = true;
        let errorMessage = '';

        // Clear previous validation state
        this.clearFieldValidation(field);

        // Required validation
        if (rules.required && !value) {
            isValid = false;
            errorMessage = rules.requiredMessage || 'This field is required';
        }

        // Email validation
        if (isValid && rules.email && value) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(value)) {
                isValid = false;
                errorMessage = rules.emailMessage || 'Please enter a valid email address';
            }
        }

        // URL validation
        if (isValid && rules.url && value) {
            try {
                new URL(value);
            } catch {
                isValid = false;
                errorMessage = rules.urlMessage || 'Please enter a valid URL';
            }
        }

        // Phone validation
        if (isValid && rules.phone && value) {
            const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;
            if (!phoneRegex.test(value.replace(/\s/g, ''))) {
                isValid = false;
                errorMessage = rules.phoneMessage || 'Please enter a valid phone number';
            }
        }

        // Min length validation
        if (isValid && rules.minLength && value.length < rules.minLength) {
            isValid = false;
            errorMessage = rules.minLengthMessage || `Minimum length is ${rules.minLength} characters`;
        }

        // Max length validation
        if (isValid && rules.maxLength && value.length > rules.maxLength) {
            isValid = false;
            errorMessage = rules.maxLengthMessage || `Maximum length is ${rules.maxLength} characters`;
        }

        // Pattern validation
        if (isValid && rules.pattern && value) {
            const regex = new RegExp(rules.pattern);
            if (!regex.test(value)) {
                isValid = false;
                errorMessage = rules.patternMessage || 'Please match the required format';
            }
        }

        // Custom validation
        if (isValid && rules.custom && typeof rules.custom === 'function') {
            const customResult = rules.custom(value, field);
            if (customResult !== true) {
                isValid = false;
                errorMessage = customResult || 'Invalid value';
            }
        }

        // Apply validation state
        if (!isValid) {
            this.showFieldError(field, errorMessage);
        } else {
            this.showFieldSuccess(field);
        }

        return isValid;
    }

    /**
     * Get validation rules for a field
     */
    getValidationRules(field) {
        const rules = {};
        
        // Required
        if (field.hasAttribute('required')) {
            rules.required = true;
            rules.requiredMessage = field.dataset.requiredMessage;
        }

        // Email
        if (field.type === 'email') {
            rules.email = true;
            rules.emailMessage = field.dataset.emailMessage;
        }

        // URL
        if (field.type === 'url') {
            rules.url = true;
            rules.urlMessage = field.dataset.urlMessage;
        }

        // Phone
        if (field.dataset.phone) {
            rules.phone = true;
            rules.phoneMessage = field.dataset.phoneMessage;
        }

        // Min length
        if (field.minLength) {
            rules.minLength = parseInt(field.minLength);
            rules.minLengthMessage = field.dataset.minLengthMessage;
        }

        // Max length
        if (field.maxLength) {
            rules.maxLength = parseInt(field.maxLength);
            rules.maxLengthMessage = field.dataset.maxLengthMessage;
        }

        // Pattern
        if (field.pattern) {
            rules.pattern = field.pattern;
            rules.patternMessage = field.dataset.patternMessage;
        }

        // Custom validation function
        if (field.dataset.customValidation) {
            rules.custom = window[field.dataset.customValidation];
        }

        return rules;
    }

    /**
     * Clear field validation state
     */
    clearFieldValidation(field) {
        field.classList.remove('input-error', 'input-success');
        const errorElement = field.parentNode.querySelector('.form-error');
        if (errorElement) {
            errorElement.remove();
        }
    }

    /**
     * Show field error
     */
    showFieldError(field, message) {
        field.classList.add('input-error');
        field.classList.remove('input-success');
        
        const errorElement = document.createElement('div');
        errorElement.className = 'form-error';
        errorElement.textContent = message;
        
        field.parentNode.appendChild(errorElement);
    }

    /**
     * Show field success
     */
    showFieldSuccess(field) {
        field.classList.add('input-success');
        field.classList.remove('input-error');
    }

    /**
     * Validate entire form
     */
    validateForm(form) {
        const fields = form.querySelectorAll('input, textarea, select');
        let isValid = true;

        fields.forEach(field => {
            if (!this.validateField(field)) {
                isValid = false;
            }
        });

        return isValid;
    }

    /**
     * Show form errors
     */
    showFormErrors(form) {
        const firstError = form.querySelector('.input-error');
        if (firstError) {
            firstError.focus();
            firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }

    /**
     * Initialize auto-save functionality
     */
    initAutoSave() {
        document.addEventListener('input', (e) => {
            const input = e.target;
            const form = input.closest('form[data-auto-save]');
            
            if (form) {
                this.scheduleAutoSave(form);
            }
        });
    }

    /**
     * Schedule auto-save for a form
     */
    scheduleAutoSave(form) {
        const formId = form.id || 'form-' + Math.random().toString(36).substr(2, 9);
        const delay = parseInt(form.dataset.autoSaveDelay) || 2000;

        // Clear existing timer
        if (this.autoSaveTimers.has(formId)) {
            clearTimeout(this.autoSaveTimers.get(formId));
        }

        // Set new timer
        const timer = setTimeout(() => {
            this.performAutoSave(form);
        }, delay);

        this.autoSaveTimers.set(formId, timer);
    }

    /**
     * Perform auto-save
     */
    async performAutoSave(form) {
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());
        
        try {
            // Show saving indicator
            this.showSavingIndicator(form);
            
            // Send data to server (implement your endpoint)
            const response = await fetch('/api/auto-save', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });

            if (response.ok) {
                this.showSaveSuccess(form);
            } else {
                throw new Error('Auto-save failed');
            }
        } catch (error) {
            console.error('Auto-save error:', error);
            this.showSaveError(form);
        }
    }

    /**
     * Show saving indicator
     */
    showSavingIndicator(form) {
        const indicator = form.querySelector('.auto-save-indicator') || this.createAutoSaveIndicator();
        indicator.textContent = 'Saving...';
        indicator.classList.add('saving');
        form.appendChild(indicator);
    }

    /**
     * Show save success
     */
    showSaveSuccess(form) {
        const indicator = form.querySelector('.auto-save-indicator');
        if (indicator) {
            indicator.textContent = 'Saved';
            indicator.classList.remove('saving');
            indicator.classList.add('saved');
            
            setTimeout(() => {
                indicator.remove();
            }, 2000);
        }
    }

    /**
     * Show save error
     */
    showSaveError(form) {
        const indicator = form.querySelector('.auto-save-indicator');
        if (indicator) {
            indicator.textContent = 'Save failed';
            indicator.classList.remove('saving');
            indicator.classList.add('error');
            
            setTimeout(() => {
                indicator.remove();
            }, 3000);
        }
    }

    /**
     * Create auto-save indicator
     */
    createAutoSaveIndicator() {
        const indicator = document.createElement('div');
        indicator.className = 'auto-save-indicator';
        indicator.style.cssText = `
            position: absolute;
            top: 10px;
            right: 10px;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            background: #f3f4f6;
            color: #6b7280;
        `;
        return indicator;
    }

    /**
     * Initialize floating labels
     */
    initFloatingLabels() {
        document.querySelectorAll('.form-floating input, .form-floating textarea, .form-floating select').forEach(field => {
            this.updateFloatingLabel(field);
            
            field.addEventListener('focus', () => this.updateFloatingLabel(field));
            field.addEventListener('blur', () => this.updateFloatingLabel(field));
            field.addEventListener('input', () => this.updateFloatingLabel(field));
        });
    }

    /**
     * Update floating label state
     */
    updateFloatingLabel(field) {
        const label = field.parentNode.querySelector('.label');
        if (label) {
            const hasValue = field.value.length > 0;
            const isFocused = field === document.activeElement;
            
            if (hasValue || isFocused) {
                label.classList.add('floating');
            } else {
                label.classList.remove('floating');
            }
        }
    }

    /**
     * Initialize password toggles
     */
    initPasswordToggles() {
        document.querySelectorAll('.password-input input[type="password"]').forEach(input => {
            const toggle = document.createElement('button');
            toggle.type = 'button';
            toggle.className = 'password-toggle';
            toggle.innerHTML = '<i class="fas fa-eye"></i>';
            
            toggle.addEventListener('click', () => {
                if (input.type === 'password') {
                    input.type = 'text';
                    toggle.innerHTML = '<i class="fas fa-eye-slash"></i>';
                } else {
                    input.type = 'password';
                    toggle.innerHTML = '<i class="fas fa-eye"></i>';
                }
            });
            
            input.parentNode.appendChild(toggle);
        });
    }

    /**
     * Initialize file uploads
     */
    initFileUploads() {
        document.querySelectorAll('input[type="file"]').forEach(input => {
            input.addEventListener('change', (e) => {
                this.handleFileUpload(e.target);
            });
        });
    }

    /**
     * Handle file upload
     */
    handleFileUpload(input) {
        const files = Array.from(input.files);
        const container = input.parentNode;
        
        // Remove existing previews
        container.querySelectorAll('.file-preview').forEach(preview => preview.remove());
        
        files.forEach(file => {
            const preview = this.createFilePreview(file);
            container.appendChild(preview);
        });
    }

    /**
     * Create file preview
     */
    createFilePreview(file) {
        const preview = document.createElement('div');
        preview.className = 'file-preview';
        preview.style.cssText = `
            display: flex;
            align-items: center;
            padding: 8px;
            margin: 4px 0;
            background: #f9fafb;
            border-radius: 4px;
            font-size: 14px;
        `;
        
        const icon = document.createElement('i');
        icon.className = 'fas fa-file mr-2';
        icon.style.marginRight = '8px';
        
        const name = document.createElement('span');
        name.textContent = file.name;
        name.style.flex = '1';
        
        const size = document.createElement('span');
        size.textContent = this.formatFileSize(file.size);
        size.style.color = '#6b7280';
        size.style.fontSize = '12px';
        
        preview.appendChild(icon);
        preview.appendChild(name);
        preview.appendChild(size);
        
        return preview;
    }

    /**
     * Format file size
     */
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    /**
     * Initialize autocomplete
     */
    initAutocomplete() {
        document.querySelectorAll('.autocomplete input').forEach(input => {
            input.addEventListener('input', (e) => {
                this.handleAutocomplete(e.target);
            });
            
            input.addEventListener('focus', (e) => {
                this.showAutocompleteDropdown(e.target);
            });
            
            input.addEventListener('blur', (e) => {
                setTimeout(() => {
                    this.hideAutocompleteDropdown(e.target);
                }, 200);
            });
        });
    }

    /**
     * Handle autocomplete input
     */
    async handleAutocomplete(input) {
        const query = input.value.trim();
        if (query.length < 2) {
            this.hideAutocompleteDropdown(input);
            return;
        }

        try {
            const suggestions = await this.getAutocompleteSuggestions(query, input);
            this.showAutocompleteSuggestions(input, suggestions);
        } catch (error) {
            console.error('Autocomplete error:', error);
        }
    }

    /**
     * Get autocomplete suggestions
     */
    async getAutocompleteSuggestions(query, input) {
        // Implement your autocomplete API call here
        const endpoint = input.dataset.autocompleteEndpoint || '/api/autocomplete';
        
        const response = await fetch(`${endpoint}?q=${encodeURIComponent(query)}`);
        if (response.ok) {
            return await response.json();
        }
        
        return [];
    }

    /**
     * Show autocomplete suggestions
     */
    showAutocompleteSuggestions(input, suggestions) {
        const dropdown = this.getOrCreateAutocompleteDropdown(input);
        dropdown.innerHTML = '';
        
        suggestions.forEach(suggestion => {
            const item = document.createElement('div');
            item.className = 'autocomplete-item';
            item.textContent = suggestion;
            item.addEventListener('click', () => {
                input.value = suggestion;
                this.hideAutocompleteDropdown(input);
            });
            dropdown.appendChild(item);
        });
        
        dropdown.style.display = suggestions.length > 0 ? 'block' : 'none';
    }

    /**
     * Get or create autocomplete dropdown
     */
    getOrCreateAutocompleteDropdown(input) {
        let dropdown = input.parentNode.querySelector('.autocomplete-dropdown');
        
        if (!dropdown) {
            dropdown = document.createElement('div');
            dropdown.className = 'autocomplete-dropdown';
            input.parentNode.appendChild(dropdown);
        }
        
        return dropdown;
    }

    /**
     * Show autocomplete dropdown
     */
    showAutocompleteDropdown(input) {
        const dropdown = input.parentNode.querySelector('.autocomplete-dropdown');
        if (dropdown && dropdown.children.length > 0) {
            dropdown.style.display = 'block';
        }
    }

    /**
     * Hide autocomplete dropdown
     */
    hideAutocompleteDropdown(input) {
        const dropdown = input.parentNode.querySelector('.autocomplete-dropdown');
        if (dropdown) {
            dropdown.style.display = 'none';
        }
    }

    /**
     * Initialize form wizards
     */
    initFormWizards() {
        document.querySelectorAll('.form-wizard').forEach(wizard => {
            this.initWizard(wizard);
        });
    }

    /**
     * Initialize a form wizard
     */
    initWizard(wizard) {
        const steps = wizard.querySelectorAll('.wizard-step');
        const nextButtons = wizard.querySelectorAll('.wizard-next');
        const prevButtons = wizard.querySelectorAll('.wizard-prev');
        const progressBar = wizard.querySelector('.wizard-progress');
        
        let currentStep = 0;
        
        // Initialize progress
        this.updateWizardProgress(wizard, currentStep, steps.length);
        
        // Next button handlers
        nextButtons.forEach(button => {
            button.addEventListener('click', () => {
                if (this.validateWizardStep(steps[currentStep])) {
                    currentStep++;
                    this.showWizardStep(wizard, currentStep);
                    this.updateWizardProgress(wizard, currentStep, steps.length);
                }
            });
        });
        
        // Previous button handlers
        prevButtons.forEach(button => {
            button.addEventListener('click', () => {
                currentStep--;
                this.showWizardStep(wizard, currentStep);
                this.updateWizardProgress(wizard, currentStep, steps.length);
            });
        });
    }

    /**
     * Show wizard step
     */
    showWizardStep(wizard, stepIndex) {
        const steps = wizard.querySelectorAll('.wizard-step');
        const nextButtons = wizard.querySelectorAll('.wizard-next');
        const prevButtons = wizard.querySelectorAll('.wizard-prev');
        
        steps.forEach((step, index) => {
            step.style.display = index === stepIndex ? 'block' : 'none';
        });
        
        // Update button visibility
        nextButtons.forEach(button => {
            button.style.display = stepIndex < steps.length - 1 ? 'block' : 'none';
        });
        
        prevButtons.forEach(button => {
            button.style.display = stepIndex > 0 ? 'block' : 'none';
        });
    }

    /**
     * Validate wizard step
     */
    validateWizardStep(step) {
        const fields = step.querySelectorAll('input, textarea, select');
        let isValid = true;
        
        fields.forEach(field => {
            if (!this.validateField(field)) {
                isValid = false;
            }
        });
        
        return isValid;
    }

    /**
     * Update wizard progress
     */
    updateWizardProgress(wizard, currentStep, totalSteps) {
        const progressBar = wizard.querySelector('.wizard-progress');
        if (progressBar) {
            const progress = ((currentStep + 1) / totalSteps) * 100;
            progressBar.style.width = progress + '%';
        }
    }

    /**
     * Initialize form analytics
     */
    initFormAnalytics() {
        document.addEventListener('submit', (e) => {
            this.trackFormSubmission(e.target);
        });
        
        document.addEventListener('input', (e) => {
            this.trackFieldInteraction(e.target);
        });
    }

    /**
     * Track form submission
     */
    trackFormSubmission(form) {
        const analyticsData = {
            formId: form.id || 'unknown',
            formAction: form.action,
            timestamp: new Date().toISOString(),
            url: window.location.href
        };
        
        console.log('Form Submission:', analyticsData);
        
        // Send to analytics service
        if (typeof gtag !== 'undefined') {
            gtag('event', 'form_submit', analyticsData);
        }
    }

    /**
     * Track field interaction
     */
    trackFieldInteraction(field) {
        const form = field.closest('form');
        if (!form) return;
        
        const analyticsData = {
            formId: form.id || 'unknown',
            fieldName: field.name || field.id || 'unknown',
            fieldType: field.type,
            timestamp: new Date().toISOString()
        };
        
        // Debounce tracking to avoid spam
        clearTimeout(this.fieldTrackingTimers.get(field));
        const timer = setTimeout(() => {
            console.log('Field Interaction:', analyticsData);
            
            if (typeof gtag !== 'undefined') {
                gtag('event', 'form_field_interaction', analyticsData);
            }
        }, 1000);
        
        this.fieldTrackingTimers.set(field, timer);
    }
}

// Initialize form component when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.formComponent = new FormComponent();
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = FormComponent;
}
