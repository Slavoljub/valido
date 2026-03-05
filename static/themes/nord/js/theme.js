/**
 * Nord Theme - JavaScript
 */

class NordTheme {
    constructor() {
        this.themeName = 'nord';
        this.init();
    }

    init() {
        console.log('Nord theme loaded');
    }
}

// Initialize theme
document.addEventListener('DOMContentLoaded', () => {
    new NordTheme();
});
