/**
 * Monokai Theme - JavaScript
 */

class MonokaiTheme {
    constructor() {
        this.themeName = 'monokai';
        this.init();
    }

    init() {
        console.log('Monokai theme loaded');
    }
}

// Initialize theme
document.addEventListener('DOMContentLoaded', () => {
    new MonokaiTheme();
});
