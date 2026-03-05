/**
 * Dracula Theme - JavaScript
 */

class DraculaTheme {
    constructor() {
        this.themeName = 'dracula';
        this.init();
    }

    init() {
        console.log('Dracula theme loaded');
    }
}

// Initialize theme
document.addEventListener('DOMContentLoaded', () => {
    new DraculaTheme();
});
