/**
 * Material-Dark Theme - JavaScript
 */

class MaterialdarkTheme {
    constructor() {
        this.themeName = 'material-dark';
        this.init();
    }

    init() {
        console.log('Material-Dark theme loaded');
    }
}

// Initialize theme
document.addEventListener('DOMContentLoaded', () => {
    new MaterialdarkTheme();
});
