/* ==========================================================================
   ValidoAI JavaScript - DRY Implementation (Consolidated)
   Single comprehensive JavaScript file with all functionality
   ========================================================================== */

/* ==========================================================================
   GLOBAL CONFIGURATION & UTILITIES
   ========================================================================== */

window.ValidoAI = window.ValidoAI || {};

// Global configuration
ValidoAI.config = {
  apiBase: '/api',
  theme: localStorage.getItem('valido-theme') || 'valido-white',
  language: localStorage.getItem('valido-language') || 'en',
  debug: false,
  csrfToken: document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '',
  userId: document.querySelector('meta[name="user-id"]')?.getAttribute('content') || null
};

// Utility functions
ValidoAI.utils = {
  // Debounce function
  debounce: function(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  },

  // Throttle function
  throttle: function(func, limit) {
    let inThrottle;
    return function(...args) {
      if (!inThrottle) {
        func.apply(this, args);
        inThrottle = true;
        setTimeout(() => inThrottle = false, limit);
      }
    };
  },

  // Deep merge objects
  merge: function(target, source) {
    const result = { ...target };
    for (const key in source) {
      if (source[key] instanceof Object && key in target) {
        result[key] = this.merge(target[key], source[key]);
      } else {
        result[key] = source[key];
      }
    }
    return result;
  },

  // Generate unique ID
  generateId: function(prefix = 'id') {
    return `${prefix}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  },

  // Format date
  formatDate: function(date, format = 'YYYY-MM-DD') {
    const d = new Date(date);
    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    const hours = String(d.getHours()).padStart(2, '0');
    const minutes = String(d.getMinutes()).padStart(2, '0');

    switch (format) {
      case 'YYYY-MM-DD': return `${year}-${month}-${day}`;
      case 'DD/MM/YYYY': return `${day}/${month}/${year}`;
      case 'MM/DD/YYYY': return `${month}/${day}/${year}`;
      case 'YYYY-MM-DD HH:mm': return `${year}-${month}-${day} ${hours}:${minutes}`;
      default: return d.toLocaleDateString();
    }
  },

  // Validate email
  validateEmail: function(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
  },

  // Validate URL
  validateUrl: function(url) {
    try {
      new URL(url);
      return true;
    } catch {
      return false;
    }
  },

  // Sanitize HTML
  sanitizeHtml: function(html) {
    const div = document.createElement('div');
    div.textContent = html;
    return div.innerHTML;
  },

  // Check if element is in viewport
  isInViewport: function(element) {
    const rect = element.getBoundingClientRect();
    return (
      rect.top >= 0 &&
      rect.left >= 0 &&
      rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
      rect.right <= (window.innerWidth || document.documentElement.clientWidth)
    );
  },

  // Copy to clipboard
  copyToClipboard: async function(text) {
    try {
      await navigator.clipboard.writeText(text);
      return true;
    } catch (err) {
      // Fallback for older browsers
      const textArea = document.createElement('textarea');
      textArea.value = text;
      document.body.appendChild(textArea);
      textArea.focus();
      textArea.select();
      const success = document.execCommand('copy');
      document.body.removeChild(textArea);
      return success;
    }
  },

  // Show loading spinner
  showLoading: function(element) {
    element.classList.add('loading');
    element.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
  },

  // Hide loading spinner
  hideLoading: function(element, originalText) {
    element.classList.remove('loading');
    if (originalText) element.innerHTML = originalText;
  }
};

/* ==========================================================================
   API COMMUNICATION SYSTEM
   ========================================================================== */

ValidoAI.api = {
  // Make API request
  request: async function(endpoint, options = {}) {
    const {
      method = 'GET',
      data = null,
      headers = {},
      showLoader = false,
      loaderElement = null
    } = options;

    const url = `${ValidoAI.config.apiBase}${endpoint}`;
    const config = {
      method,
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': ValidoAI.config.csrfToken,
        ...headers
      }
    };

    if (data) {
      config.body = JSON.stringify(data);
    }

    if (showLoader && loaderElement) {
      ValidoAI.utils.showLoading(loaderElement);
    }

    try {
      const response = await fetch(url, config);
      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.message || `HTTP ${response.status}`);
      }

      return result;
    } catch (error) {
      console.error('API Request failed:', error);
      throw error;
    } finally {
      if (showLoader && loaderElement) {
        ValidoAI.utils.hideLoading(loaderElement);
      }
    }
  },

  // GET request
  get: function(endpoint, options = {}) {
    return this.request(endpoint, { ...options, method: 'GET' });
  },

  // POST request
  post: function(endpoint, data, options = {}) {
    return this.request(endpoint, { ...options, method: 'POST', data });
  },

  // PUT request
  put: function(endpoint, data, options = {}) {
    return this.request(endpoint, { ...options, method: 'PUT', data });
  },

  // DELETE request
  delete: function(endpoint, options = {}) {
    return this.request(endpoint, { ...options, method: 'DELETE' });
  },

  // Upload file
  upload: async function(endpoint, file, options = {}) {
    const formData = new FormData();
    formData.append('file', file);

    return this.request(endpoint, {
      ...options,
      method: 'POST',
      data: formData,
      headers: {} // Let browser set content-type for FormData
    });
  }
};

/* ==========================================================================
   TOAST NOTIFICATION SYSTEM
   ========================================================================== */

ValidoAI.toast = {
  // Show toast notification
  show: function(type, message, options = {}) {
    const {
      position = 'top-right',
      duration = 4000,
      showIcon = true,
      showClose = true,
      autoClose = true
    } = options;

    // Create toast container if it doesn't exist
    let toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
      toastContainer = document.createElement('div');
      toastContainer.id = 'toast-container';
      toastContainer.className = 'fixed z-50 flex flex-col gap-2 p-4 pointer-events-none';
      document.body.appendChild(toastContainer);

      // Position the container
      switch (position) {
        case 'top-right':
          toastContainer.className += ' top-20 right-4';
          break;
        case 'top-left':
          toastContainer.className += ' top-20 left-4';
          break;
        case 'bottom-right':
          toastContainer.className += ' bottom-4 right-4';
          break;
        case 'bottom-left':
          toastContainer.className += ' bottom-4 left-4';
          break;
        case 'top-center':
          toastContainer.className += ' top-20 left-1/2 transform -translate-x-1/2';
          break;
        case 'bottom-center':
          toastContainer.className += ' bottom-4 left-1/2 transform -translate-x-1/2';
          break;
      }
    }

    // Create toast element
    const toast = document.createElement('div');
    toast.className = 'toast pointer-events-auto max-w-sm w-full bg-white shadow-lg rounded-lg ring-1 ring-black ring-opacity-5';

    // Toast styles based on type
    const typeStyles = {
      success: 'bg-green-50 border-green-200 text-green-800',
      error: 'bg-red-50 border-red-200 text-red-800',
      warning: 'bg-yellow-50 border-yellow-200 text-yellow-800',
      info: 'bg-blue-50 border-blue-200 text-blue-800'
    };

    toast.className += ` ${typeStyles[type] || typeStyles.info}`;

    // Toast content
    toast.innerHTML = `
      <div class="p-4">
        <div class="flex items-start">
          ${showIcon ? `
            <div class="flex-shrink-0">
              ${this.getIcon(type)}
            </div>
          ` : ''}
          <div class="ml-3 w-0 flex-1 pt-0.5">
            <p class="text-sm font-medium">${message}</p>
          </div>
          ${showClose ? `
            <div class="ml-4 flex-shrink-0 flex">
              <button class="bg-white rounded-md inline-flex text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500" onclick="this.closest('.toast').remove()">
                <span class="sr-only">Close</span>
                <svg class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                </svg>
              </button>
            </div>
          ` : ''}
        </div>
      </div>
    `;

    // Add to container
    toastContainer.appendChild(toast);

    // Auto remove after duration
    if (autoClose) {
      setTimeout(() => {
        if (toast.parentNode) {
          toast.remove();
        }
      }, duration);
    }

    // Add slide-in animation
    setTimeout(() => toast.classList.add('animate-slide-in-right'), 10);

    return toast;
  },

  // Get icon for toast type
  getIcon: function(type) {
    const icons = {
      success: '<svg class="h-5 w-5 text-green-400" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" /></svg>',
      error: '<svg class="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" /></svg>',
      warning: '<svg class="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" /></svg>',
      info: '<svg class="h-5 w-5 text-blue-400" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" /></svg>'
    };
    return icons[type] || icons.info;
  },

  // Success toast
  success: function(message, options = {}) {
    return this.show('success', message, options);
  },

  // Error toast
  error: function(message, options = {}) {
    return this.show('error', message, options);
  },

  // Warning toast
  warning: function(message, options = {}) {
    return this.show('warning', message, options);
  },

  // Info toast
  info: function(message, options = {}) {
    return this.show('info', message, options);
  }
};

/* ==========================================================================
   MODAL SYSTEM
   ========================================================================== */

ValidoAI.modal = {
  // Current modal state
  currentModal: null,
  modalStack: [],

  // Create modal
  create: function(options = {}) {
    const {
      title = '',
      content = '',
      size = 'md',
      closable = true,
      actions = [],
      onClose = null,
      onOpen = null
    } = options;

    // Create modal element
    const modal = document.createElement('div');
    modal.className = 'modal-overlay fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4';

    const sizeClasses = {
      sm: 'max-w-md',
      md: 'max-w-lg',
      lg: 'max-w-2xl',
      xl: 'max-w-4xl',
      full: 'max-w-full mx-4'
    };

    modal.innerHTML = `
      <div class="modal-content bg-white rounded-lg shadow-xl ${sizeClasses[size]} w-full max-h-full overflow-auto">
        ${(title || closable) ? `
          <div class="modal-header flex items-center justify-between p-6 border-b">
            ${title ? `<h3 class="text-lg font-semibold text-gray-900">${title}</h3>` : '<div></div>'}
            ${closable ? `
              <button class="modal-close text-gray-400 hover:text-gray-600" onclick="ValidoAI.modal.close()">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
              </button>
            ` : ''}
          </div>
        ` : ''}
        <div class="modal-body p-6">
          ${content}
        </div>
        ${actions.length > 0 ? `
          <div class="modal-footer flex justify-end space-x-3 p-6 border-t bg-gray-50 rounded-b-lg">
            ${actions.map(action => `
              <button class="btn ${action.class || 'btn-secondary'}" onclick="${action.onClick || ''}">
                ${action.text}
              </button>
            `).join('')}
          </div>
        ` : ''}
      </div>
    `;

    // Add event listeners
    if (closable) {
      modal.addEventListener('click', (e) => {
        if (e.target === modal) {
          this.close();
        }
      });
    }

    return modal;
  },

  // Show modal
  show: function(modalElement) {
    this.currentModal = modalElement;
    this.modalStack.push(modalElement);
    document.body.appendChild(modalElement);
    document.body.style.overflow = 'hidden';

    // Trigger onOpen callback
    if (modalElement.onOpen) {
      modalElement.onOpen();
    }

    // Add slide-in animation
    setTimeout(() => {
      modalElement.classList.add('opacity-100');
      modalElement.querySelector('.modal-content').classList.add('animate-bounce-in');
    }, 10);
  },

  // Close modal
  close: function() {
    if (this.currentModal) {
      const modal = this.currentModal;

      // Trigger onClose callback
      if (modal.onClose) {
        modal.onClose();
      }

      // Remove modal
      modal.classList.remove('opacity-100');
      setTimeout(() => {
        if (modal.parentNode) {
          modal.parentNode.removeChild(modal);
        }
      }, 300);

      this.modalStack.pop();
      this.currentModal = this.modalStack.length > 0 ? this.modalStack[this.modalStack.length - 1] : null;

      // Restore body scroll if no more modals
      if (this.modalStack.length === 0) {
        document.body.style.overflow = '';
      }
    }
  },

  // Alert modal
  alert: function(message, options = {}) {
    const modal = this.create({
      title: options.title || 'Alert',
      content: `<p class="text-gray-700">${message}</p>`,
      actions: [
        {
          text: options.confirmText || 'OK',
          class: 'btn-primary',
          onClick: 'ValidoAI.modal.close()'
        }
      ],
      ...options
    });

    this.show(modal);
  },

  // Confirm modal
  confirm: function(message, options = {}) {
    const {
      onConfirm = () => {},
      onCancel = () => {},
      confirmText = 'Confirm',
      cancelText = 'Cancel'
    } = options;

    const modal = this.create({
      title: options.title || 'Confirm',
      content: `<p class="text-gray-700">${message}</p>`,
      actions: [
        {
          text: cancelText,
          class: 'btn-secondary',
          onClick: 'ValidoAI.modal.close()'
        },
        {
          text: confirmText,
          class: 'btn-primary',
          onClick: `ValidoAI.modal.close(); (${onConfirm.toString()})()`
        }
      ],
      ...options
    });

    this.show(modal);
  }
};

/* ==========================================================================
   FORM HANDLING SYSTEM
   ========================================================================== */

ValidoAI.forms = {
  // Validate form
  validate: function(formElement, rules = {}) {
    const errors = [];
    const formData = new FormData(formElement);

    for (const [field, rule] of Object.entries(rules)) {
      const element = formElement.querySelector(`[name="${field}"]`);
      if (!element) continue;

      const value = formData.get(field) || element.value || '';

      // Required validation
      if (rule.required && !value.trim()) {
        errors.push({
          field,
          element,
          message: rule.message || `${field} is required`
        });
        continue;
      }

      // Skip other validations if empty and not required
      if (!rule.required && !value.trim()) continue;

      // Email validation
      if (rule.email && !ValidoAI.utils.validateEmail(value)) {
        errors.push({
          field,
          element,
          message: rule.message || 'Please enter a valid email address'
        });
        continue;
      }

      // URL validation
      if (rule.url && !ValidoAI.utils.validateUrl(value)) {
        errors.push({
          field,
          element,
          message: rule.message || 'Please enter a valid URL'
        });
        continue;
      }

      // Minimum length validation
      if (rule.minLength && value.length < rule.minLength) {
        errors.push({
          field,
          element,
          message: rule.message || `Minimum length is ${rule.minLength} characters`
        });
        continue;
      }

      // Maximum length validation
      if (rule.maxLength && value.length > rule.maxLength) {
        errors.push({
          field,
          element,
          message: rule.message || `Maximum length is ${rule.maxLength} characters`
        });
        continue;
      }

      // Pattern validation
      if (rule.pattern && !rule.pattern.test(value)) {
        errors.push({
          field,
          element,
          message: rule.message || 'Invalid format'
        });
        continue;
      }

      // Custom validation
      if (rule.custom && !rule.custom(value)) {
        errors.push({
          field,
          element,
          message: rule.message || 'Invalid value'
        });
        continue;
      }
    }

    return errors;
  },

  // Show validation errors
  showErrors: function(errors) {
    // Clear previous errors
    document.querySelectorAll('.form-error').forEach(el => el.remove());
    document.querySelectorAll('.error').forEach(el => el.classList.remove('error'));

    errors.forEach(error => {
      const { element, message } = error;

      // Add error class to element
      element.classList.add('error');

      // Create error message
      const errorElement = document.createElement('div');
      errorElement.className = 'form-error text-red-500 text-sm mt-1';
      errorElement.textContent = message;

      // Insert after element
      element.parentNode.insertBefore(errorElement, element.nextSibling);
    });
  },

  // Clear validation errors
  clearErrors: function(formElement) {
    formElement.querySelectorAll('.form-error').forEach(el => el.remove());
    formElement.querySelectorAll('.error').forEach(el => el.classList.remove('error'));
  },

  // Submit form with validation
  submit: async function(formElement, options = {}) {
    const {
      rules = {},
      beforeSubmit = () => {},
      afterSubmit = () => {},
      showErrors = true,
      clearErrors = true
    } = options;

    // Clear previous errors if requested
    if (clearErrors) {
      this.clearErrors(formElement);
    }

    // Validate form
    const errors = this.validate(formElement, rules);

    if (errors.length > 0) {
      if (showErrors) {
        this.showErrors(errors);
      }
      return { success: false, errors };
    }

    // Before submit callback
    beforeSubmit(formElement);

    try {
      // Get form data
      const formData = new FormData(formElement);
      const data = Object.fromEntries(formData.entries());

      // Submit form
      const response = await fetch(formElement.action, {
        method: formElement.method || 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': ValidoAI.config.csrfToken
        },
        body: JSON.stringify(data)
      });

      const result = await response.json();

      // After submit callback
      afterSubmit(result, formElement);

      return { success: response.ok, data: result };

    } catch (error) {
      console.error('Form submission error:', error);
      afterSubmit({ success: false, message: error.message }, formElement);
      return { success: false, error };
    }
  },

  // Initialize form validation
  initValidation: function(formElement, rules = {}) {
    const inputs = formElement.querySelectorAll('input, textarea, select');

    inputs.forEach(input => {
      const fieldRules = rules[input.name];
      if (!fieldRules) return;

      // Real-time validation
      input.addEventListener('blur', () => {
        const errors = this.validate(formElement, { [input.name]: fieldRules });
        this.clearErrors(formElement);
        this.showErrors(errors);
      });

      // Clear errors on focus
      input.addEventListener('focus', () => {
        const errorElement = input.parentNode.querySelector('.form-error');
        if (errorElement) {
          errorElement.remove();
        }
        input.classList.remove('error');
      });
    });

    // Form submit handler
    formElement.addEventListener('submit', async (e) => {
      e.preventDefault();

      const result = await this.submit(formElement, { rules });

      if (!result.success) {
        ValidoAI.toast.error('Please correct the errors in the form');
      }
    });
  }
};

/* ==========================================================================
   THEME MANAGEMENT SYSTEM
   ========================================================================== */

ValidoAI.theme = {
  // Current theme
  current: localStorage.getItem('valido-theme') || 'valido-white',

  // Available themes
  themes: {
    'valido-white': {
      name: 'Valido White',
      colors: {
        primary: '#3b82f6',
        background: '#ffffff',
        surface: '#f8fafc',
        text: '#0f172a'
      }
    },
    'valido-dark': {
      name: 'Valido Dark',
      colors: {
        primary: '#3b82f6',
        background: '#0f172a',
        surface: '#1e293b',
        text: '#f1f5f9'
      }
    },
    'dracula': {
      name: 'Dracula',
      colors: {
        primary: '#bd93f9',
        background: '#282a36',
        surface: '#44475a',
        text: '#f8f8f2'
      }
    },
    'material': {
      name: 'Material',
      colors: {
        primary: '#2196f3',
        background: '#263238',
        surface: '#37474f',
        text: '#ffffff'
      }
    },
    'nord': {
      name: 'Nord',
      colors: {
        primary: '#88c0d0',
        background: '#2e3440',
        surface: '#3b4252',
        text: '#eceff4'
      }
    }
  },

  // Set theme
  set: function(themeName) {
    if (!this.themes[themeName]) {
      console.warn(`Theme "${themeName}" not found. Using default theme.`);
      themeName = 'valido-white';
    }

    this.current = themeName;
    localStorage.setItem('valido-theme', themeName);

    // Update document class
    document.documentElement.setAttribute('data-theme', themeName);

    // Update CSS custom properties
    const theme = this.themes[themeName];
    if (theme.colors) {
      Object.entries(theme.colors).forEach(([property, value]) => {
        document.documentElement.style.setProperty(`--theme-${property}`, value);
      });
    }

    // Dispatch theme change event
    window.dispatchEvent(new CustomEvent('themeChanged', {
      detail: { theme: themeName, themeData: theme }
    }));

    return theme;
  },

  // Get current theme
  get: function() {
    return this.current;
  },

  // Get theme data
  getData: function(themeName = null) {
    return this.themes[themeName || this.current];
  },

  // Toggle between light and dark
  toggle: function() {
    const isDark = this.current.includes('dark') || this.current === 'dracula';
    const newTheme = isDark ? 'valido-white' : 'valido-dark';
    return this.set(newTheme);
  },

  // Initialize theme system
  init: function() {
    // Set initial theme
    this.set(this.current);

    // Listen for system theme changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
      if (this.current === 'auto') {
        this.set(e.matches ? 'valido-dark' : 'valido-white');
      }
    });
  }
};

/* ==========================================================================
   INITIALIZATION
   ========================================================================== */

document.addEventListener('DOMContentLoaded', function() {
  // Initialize theme system
  ValidoAI.theme.init();

  // Add global error handler
  window.addEventListener('error', function(e) {
    console.error('JavaScript error:', e.error);
    if (ValidoAI.config.debug) {
      ValidoAI.toast.error(`JavaScript Error: ${e.error.message}`);
    }
  });

  // Add unhandled promise rejection handler
  window.addEventListener('unhandledrejection', function(e) {
    console.error('Unhandled promise rejection:', e.reason);
    if (ValidoAI.config.debug) {
      ValidoAI.toast.error(`Promise Error: ${e.reason.message || e.reason}`);
    }
  });

  // Initialize performance monitoring
  if ('performance' in window && 'mark' in window.performance) {
    performance.mark('app-init-start');
  }

  console.log('ValidoAI JavaScript initialized successfully');
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
  module.exports = ValidoAI;
}
