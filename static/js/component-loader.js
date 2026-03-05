/* ==========================================================================
   Component Loader System
   ========================================================================== */

window.ComponentLoader = {
  // Component definitions
  components: {
    // CSS Components
    'buttons': {
      css: '/static/css/components/buttons.css',
      js: '/static/js/components/buttons.js'
    },
    'forms': {
      css: '/static/css/components/forms.css',
      js: '/static/js/components/forms.js'
    },
    'tables': {
      css: '/static/css/components/tables.css',
      js: '/static/js/components/tables.js'
    },
    'charts': {
      css: '/static/css/components/charts.css',
      js: '/static/js/components/charts.js'
    },
    'modals': {
      css: '/static/css/components/modals.css',
      js: '/static/js/components/modals.js'
    },
    'navigation': {
      css: '/static/css/components/navigation.css',
      js: '/static/js/components/navigation.js'
    },
    'notifications': {
      css: '/static/css/components/notifications.css',
      js: '/static/js/components/notifications.js'
    },
    'animations': {
      css: '/static/css/components/animations.css',
      js: '/static/js/components/animations.js'
    },
    
    // Page-specific components
    'dashboard': {
      css: '/static/css/pages/dashboard.css',
      js: '/static/js/pages/dashboard.js'
    },
    'chat': {
      css: '/static/css/pages/chat.css',
      js: '/static/js/pages/chat.js'
    },
    'tickets': {
      css: '/static/css/pages/tickets.css',
      js: '/static/js/pages/tickets.js'
    },
    'profile': {
      css: '/static/css/pages/profile.css',
      js: '/static/js/pages/profile.js'
    },
    'settings': {
      css: '/static/css/pages/settings.css',
      js: '/static/js/pages/settings.js'
    }
  },
  
  // Loaded components cache
  loadedComponents: new Set(),
  
  // Loading promises cache
  loadingPromises: new Map(),
  
  // Initialize component loader
  init: function() {
    this.autoLoadComponents();
  },
  
  // Auto-load components based on page content
  autoLoadComponents: function() {
    // Check for components in the DOM
    const componentSelectors = {
      'buttons': '.btn, button',
      'forms': 'form, .form-group, .form-input',
      'tables': 'table, .table',
      'charts': '.chart, canvas[data-chart]',
      'modals': '.modal, [data-modal]',
      'navigation': '.nav, .sidebar, .breadcrumb',
      'notifications': '.notification, .alert, .toast',
      'animations': '[data-animate], .animate'
    };
    
    Object.keys(componentSelectors).forEach(componentName => {
      if (document.querySelector(componentSelectors[componentName])) {
        this.loadComponent(componentName);
      }
    });
    
    // Load page-specific components based on URL
    this.loadPageComponents();
  },
  
  // Load page-specific components
  loadPageComponents: function() {
    const path = window.location.pathname;
    
    if (path.includes('/dashboard')) {
      this.loadComponent('dashboard');
    } else if (path.includes('/chat')) {
      this.loadComponent('chat');
    } else if (path.includes('/ticket')) {
      this.loadComponent('tickets');
    } else if (path.includes('/profile')) {
      this.loadComponent('profile');
    } else if (path.includes('/settings')) {
      this.loadComponent('settings');
    }
  },
  
  // Load a specific component
  loadComponent: function(componentName) {
    if (!this.components[componentName]) {
      console.warn(`Component "${componentName}" not found`);
      return Promise.reject(new Error(`Component "${componentName}" not found`));
    }
    
    // If component is already loaded, return resolved promise
    if (this.loadedComponents.has(componentName)) {
      return Promise.resolve();
    }
    
    // If component is currently loading, return existing promise
    if (this.loadingPromises.has(componentName)) {
      return this.loadingPromises.get(componentName);
    }
    
    // Create loading promise
    const loadPromise = this.loadComponentFiles(componentName);
    this.loadingPromises.set(componentName, loadPromise);
    
    // Clean up promise after loading
    loadPromise.finally(() => {
      this.loadingPromises.delete(componentName);
    });
    
    return loadPromise;
  },
  
  // Load component CSS and JS files
  loadComponentFiles: function(componentName) {
    const component = this.components[componentName];
    const promises = [];
    
    // Load CSS file
    if (component.css) {
      promises.push(this.loadCSS(component.css));
    }
    
    // Load JS file
    if (component.js) {
      promises.push(this.loadJS(component.js));
    }
    
    return Promise.all(promises).then(() => {
      this.loadedComponents.add(componentName);
      console.log(`Component "${componentName}" loaded successfully`);
      
      // Trigger component loaded event
      window.dispatchEvent(new CustomEvent('componentLoaded', {
        detail: { component: componentName }
      }));
    });
  },
  
  // Load CSS file
  loadCSS: function(href) {
    return new Promise((resolve, reject) => {
      // Check if CSS is already loaded
      if (document.querySelector(`link[href="${href}"]`)) {
        resolve();
        return;
      }
      
      const link = document.createElement('link');
      link.rel = 'stylesheet';
      link.href = href;
      
      link.onload = () => resolve();
      link.onerror = () => reject(new Error(`Failed to load CSS: ${href}`));
      
      document.head.appendChild(link);
    });
  },
  
  // Load JS file
  loadJS: function(src) {
    return new Promise((resolve, reject) => {
      // Check if JS is already loaded
      if (document.querySelector(`script[src="${src}"]`)) {
        resolve();
        return;
      }
      
      const script = document.createElement('script');
      script.src = src;
      script.async = true;
      
      script.onload = () => resolve();
      script.onerror = () => reject(new Error(`Failed to load JS: ${src}`));
      
      document.head.appendChild(script);
    });
  },
  
  // Load multiple components
  loadComponents: function(componentNames) {
    const promises = componentNames.map(name => this.loadComponent(name));
    return Promise.all(promises);
  },
  
  // Unload component (remove from DOM)
  unloadComponent: function(componentName) {
    if (!this.loadedComponents.has(componentName)) {
      return;
    }
    
    const component = this.components[componentName];
    
    // Remove CSS
    if (component.css) {
      const cssLink = document.querySelector(`link[href="${component.css}"]`);
      if (cssLink) {
        cssLink.remove();
      }
    }
    
    // Remove JS
    if (component.js) {
      const jsScript = document.querySelector(`script[src="${component.js}"]`);
      if (jsScript) {
        jsScript.remove();
      }
    }
    
    this.loadedComponents.delete(componentName);
    console.log(`Component "${componentName}" unloaded`);
  },
  
  // Get loaded components
  getLoadedComponents: function() {
    return Array.from(this.loadedComponents);
  },
  
  // Check if component is loaded
  isComponentLoaded: function(componentName) {
    return this.loadedComponents.has(componentName);
  },
  
  // Preload components for better performance
  preloadComponents: function(componentNames) {
    componentNames.forEach(name => {
      if (!this.loadedComponents.has(name) && !this.loadingPromises.has(name)) {
        this.loadComponent(name);
      }
    });
  },
  
  // Load components on demand based on user interaction
  loadOnDemand: function() {
    // Load buttons when user hovers over button areas
    document.addEventListener('mouseenter', (e) => {
      if (e.target.matches('.btn, button') && !this.isComponentLoaded('buttons')) {
        this.loadComponent('buttons');
      }
    }, { once: true });
    
    // Load forms when user focuses on form elements
    document.addEventListener('focusin', (e) => {
      if (e.target.matches('input, select, textarea') && !this.isComponentLoaded('forms')) {
        this.loadComponent('forms');
      }
    }, { once: true });
    
    // Load tables when user scrolls to table areas
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const target = entry.target;
          if (target.matches('table, .table') && !this.isComponentLoaded('tables')) {
            this.loadComponent('tables');
          }
        }
      });
    });
    
    document.querySelectorAll('table, .table').forEach(table => {
      observer.observe(table);
    });
  },
  
  // Initialize lazy loading for components
  initLazyLoading: function() {
    // Load components when they come into view
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const componentName = entry.target.getAttribute('data-component');
          if (componentName && !this.isComponentLoaded(componentName)) {
            this.loadComponent(componentName);
          }
        }
      });
    });
    
    document.querySelectorAll('[data-component]').forEach(element => {
      observer.observe(element);
    });
  }
};

// Initialize component loader when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
  ComponentLoader.init();
  ComponentLoader.loadOnDemand();
  ComponentLoader.initLazyLoading();
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
  module.exports = ComponentLoader;
}
