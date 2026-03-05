/* ==========================================================================
   Theme Loader System
   ========================================================================== */

window.ThemeLoader = {
  // Available themes
  themes: {
    'valido-white': '/static/css/themes/valido-white.css',
    'valido-dark': '/static/css/themes/valido-dark.css',
    'light': '/static/css/themes/light.css',
    'dark': '/static/css/themes/dark.css',
    'adwaita': '/static/css/themes/adwaita.css',
    'dracula': '/static/css/themes/dracula.css',
    'material': '/static/css/themes/material.css',
    'nord': '/static/css/themes/nord.css',
    'solarized-light': '/static/css/themes/solarized-light.css',
    'monokai': '/static/css/themes/monokai.css',
    'one-light': '/static/css/themes/one-light.css',
    'tokyo-night-light': '/static/css/themes/tokyo-night-light.css',
    'catppuccin-latte': '/static/css/themes/catppuccin-latte.css',
    'gruvbox-light': '/static/css/themes/gruvbox-light.css'
  },
  
  // Loaded themes cache
  loadedThemes: new Set(),
  
  // Initialize theme loader
  init: function() {
    this.loadCurrentTheme();
    this.initThemeSwitcher();
  },
  
  // Load current theme from localStorage
  loadCurrentTheme: function() {
    const currentTheme = localStorage.getItem('valido-theme') || 'valido-white';
    this.loadTheme(currentTheme);
  },
  
  // Load a specific theme
  loadTheme: function(themeName) {
    if (!this.themes[themeName]) {
      console.warn(`Theme "${themeName}" not found`);
      return;
    }
    
    // If theme is already loaded, just apply it
    if (this.loadedThemes.has(themeName)) {
      this.applyTheme(themeName);
      return;
    }
    
    // Load theme CSS file
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = this.themes[themeName];
    link.id = `theme-${themeName}`;
    
    link.onload = () => {
      this.loadedThemes.add(themeName);
      this.applyTheme(themeName);
      console.log(`Theme "${themeName}" loaded successfully`);
    };
    
    link.onerror = () => {
      console.error(`Failed to load theme "${themeName}"`);
    };
    
    document.head.appendChild(link);
  },
  
  // Apply theme to document
  applyTheme: function(themeName) {
    document.documentElement.setAttribute('data-theme', themeName);
    localStorage.setItem('valido-theme', themeName);
    
    // Update meta theme-color for mobile browsers
    this.updateThemeColor(themeName);
    
    // Trigger theme change event
    window.dispatchEvent(new CustomEvent('themeChanged', {
      detail: { theme: themeName }
    }));
  },
  
  // Update meta theme-color
  updateThemeColor: function(themeName) {
    let metaThemeColor = document.querySelector('meta[name="theme-color"]');
    
    if (!metaThemeColor) {
      metaThemeColor = document.createElement('meta');
      metaThemeColor.name = 'theme-color';
      document.head.appendChild(metaThemeColor);
    }
    
    const themeColors = {
      'valido-white': '#ffffff',
      'valido-dark': '#0f172a',
      'light': '#ffffff',
      'dark': '#1f2937',
      'adwaita': '#f6f5f4',
      'dracula': '#282a36',
      'material': '#fafafa',
      'nord': '#eceff4',
      'solarized-light': '#fdf6e3',
      'monokai': '#272822',
      'one-light': '#fafafa',
      'tokyo-night-light': '#d5d6db',
      'catppuccin-latte': '#eff1f5',
      'gruvbox-light': '#fbf1c7'
    };
    
    metaThemeColor.content = themeColors[themeName] || '#ffffff';
  },
  
  // Initialize theme switcher
  initThemeSwitcher: function() {
    document.addEventListener('click', (e) => {
      if (e.target.matches('[data-theme]')) {
        const themeName = e.target.getAttribute('data-theme');
        this.switchTheme(themeName);
      }
    });
  },
  
  // Switch to a different theme
  switchTheme: function(themeName) {
    if (themeName === this.getCurrentTheme()) {
      return;
    }
    
    this.loadTheme(themeName);
  },
  
  // Get current theme
  getCurrentTheme: function() {
    return document.documentElement.getAttribute('data-theme') || 'valido-white';
  },
  
  // Preload themes for better performance
  preloadThemes: function(themes = []) {
    themes.forEach(themeName => {
      if (this.themes[themeName] && !this.loadedThemes.has(themeName)) {
        this.loadTheme(themeName);
      }
    });
  },
  
  // Unload unused themes to save memory
  unloadUnusedThemes: function(keepTheme = null) {
    const currentTheme = keepTheme || this.getCurrentTheme();
    
    Object.keys(this.themes).forEach(themeName => {
      if (themeName !== currentTheme && this.loadedThemes.has(themeName)) {
        const link = document.getElementById(`theme-${themeName}`);
        if (link) {
          link.remove();
          this.loadedThemes.delete(themeName);
        }
      }
    });
  },
  
  // Get theme preview colors
  getThemePreview: function(themeName) {
    const previewColors = {
      'valido-white': { bg: '#ffffff', border: '#3b82f6' },
      'valido-dark': { bg: '#0f172a', border: '#60a5fa' },
      'light': { bg: '#ffffff', border: '#e5e7eb' },
      'dark': { bg: '#1f2937', border: '#6b7280' },
      'adwaita': { bg: '#f6f5f4', border: '#e8e6e3' },
      'dracula': { bg: '#282a36', border: '#44475a' },
      'material': { bg: '#fafafa', border: '#e0e0e0' },
      'nord': { bg: '#eceff4', border: '#e5e9f0' },
      'solarized-light': { bg: '#fdf6e3', border: '#eee8d5' },
      'monokai': { bg: '#272822', border: '#3e3d32' },
      'one-light': { bg: '#fafafa', border: '#f0f0f0' },
      'tokyo-night-light': { bg: '#d5d6db', border: '#c0c1c6' },
      'catppuccin-latte': { bg: '#eff1f5', border: '#e6e9ef' },
      'gruvbox-light': { bg: '#fbf1c7', border: '#f2e5bc' }
    };
    
    return previewColors[themeName] || { bg: '#ffffff', border: '#e5e7eb' };
  }
};

// Initialize theme loader when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
  ThemeLoader.init();
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
  module.exports = ThemeLoader;
}
