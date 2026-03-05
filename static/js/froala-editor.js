/**
 * Froala WYSIWYG Editor Integration
 * Professional rich text editor with theme support
 */

class FroalaEditorManager {
    constructor() {
        this.editor = null;
        this.currentTheme = 'valido-white';
        this.init();
    }

    init() {
        // Load Froala CSS and JS dynamically
        this.loadFroalaAssets();

        // Initialize theme detection
        this.detectTheme();

        // Listen for theme changes
        window.addEventListener('themeChanged', (e) => {
            // Use setTimeout to avoid synchronous recursion
            setTimeout(() => {
                this.currentTheme = e.detail.theme;
                this.updateEditorTheme();
            }, 10);
        });
    }

    loadFroalaAssets() {
        // Load Froala CSS
        const cssLink = document.createElement('link');
        cssLink.rel = 'stylesheet';
        cssLink.href = 'https://cdn.jsdelivr.net/npm/froala-editor@4.0.15/css/froala_editor.pkgd.min.css';
        document.head.appendChild(cssLink);

        // Load Froala JS
        const script = document.createElement('script');
        script.src = 'https://cdn.jsdelivr.net/npm/froala-editor@4.0.15/js/froala_editor.pkgd.min.js';
        script.onload = () => this.initializeEditor();
        document.head.appendChild(script);
    }

    detectTheme() {
        // Get current theme from data-theme attribute
        const body = document.querySelector('body');
        const theme = body.getAttribute('data-theme');
        if (theme) {
            this.currentTheme = theme;
        }
    }

    initializeEditor() {
        // Wait for Froala to be available
        if (typeof FroalaEditor === 'undefined') {
            setTimeout(() => this.initializeEditor(), 100);
            return;
        }

        // Initialize Froala on all elements with data-froala-editor attribute
        const editorElements = document.querySelectorAll('[data-froala-editor]');

        editorElements.forEach(element => {
            this.createEditor(element);
        });
    }

    createEditor(element) {
        const toolbarButtons = [
            'bold', 'italic', 'underline', 'strikeThrough', '|',
            'fontSize', 'color', '|',
            'paragraphFormat', 'align', 'formatOL', 'formatUL', '|',
            'insertLink', 'insertImage', 'insertTable', '|',
            'undo', 'redo', '|',
            'html'
        ];

        // Theme-specific configuration
        const themeConfig = this.getThemeConfig();

        this.editor = new FroalaEditor(element, {
            height: 300,
            toolbarButtons: toolbarButtons,
            toolbarButtonsMD: toolbarButtons,
            toolbarButtonsSM: toolbarButtons,
            toolbarButtonsXS: ['bold', 'italic', 'underline', 'insertLink', 'insertImage'],

            // Theme integration
            theme: themeConfig.theme,

            // Placeholder
            placeholderText: 'Start writing your content...',

            // Events
            events: {
                'contentChanged': () => this.onContentChanged(element),
                'initialized': () => this.onEditorInitialized(element),
                'blur': () => this.onEditorBlur(element)
            },

            // Image upload
            imageUpload: true,
            imageUploadURL: '/api/upload/image',
            imageMaxSize: 5 * 1024 * 1024, // 5MB

            // Link configuration
            linkAlwaysBlank: true,
            linkAutoPrefix: 'https://',

            // Table configuration
            tableResizer: true,
            tableResizerOffset: 10,

            // Code view
            codeView: true,
            codeMirror: true,
            codeMirrorOptions: {
                lineNumbers: true,
                theme: themeConfig.codeTheme
            },

            // Quick insert
            quickInsertTags: ['p', 'div', 'h1', 'h2', 'h3', 'blockquote'],

            // Word counter
            wordCounter: true,
            wordCounterMax: 10000,

            // Character counter
            charCounter: true,
            charCounterMax: 50000
        });
    }

    getThemeConfig() {
        const configs = {
            'valido-white': {
                theme: 'light',
                codeTheme: 'default'
            },
            'valido-dark': {
                theme: 'dark',
                codeTheme: 'monokai'
            },
            'material-light': {
                theme: 'light',
                codeTheme: 'material'
            },
            'material-dark': {
                theme: 'dark',
                codeTheme: 'material-ocean'
            },
            'dracula': {
                theme: 'dark',
                codeTheme: 'dracula'
            },
            'monokai': {
                theme: 'dark',
                codeTheme: 'monokai'
            },
            'nord': {
                theme: 'dark',
                codeTheme: 'nord'
            },
            'solarized-light': {
                theme: 'light',
                codeTheme: 'solarized'
            }
        };

        return configs[this.currentTheme] || configs['valido-white'];
    }

    updateEditorTheme() {
        if (this.editor) {
            const themeConfig = this.getThemeConfig();
            this.editor.opts.theme = themeConfig.theme;
            this.editor.opts.codeMirrorOptions.theme = themeConfig.codeTheme;

            // Reinitialize editor with new theme
            this.editor.destroy();
            this.initializeEditor();
        }
    }

    onContentChanged(element) {
        // Trigger custom event for content changes
        const event = new CustomEvent('froalaContentChanged', {
            detail: {
                element: element,
                content: this.editor.html.get()
            }
        });
        document.dispatchEvent(event);
    }

    onEditorInitialized(element) {
        // Add custom styling
        this.applyCustomStyling();

        // Trigger custom event
        const event = new CustomEvent('froalaInitialized', {
            detail: { element: element }
        });
        document.dispatchEvent(event);
    }

    onEditorBlur(element) {
        // Auto-save content
        const content = this.editor.html.get();
        localStorage.setItem(`froala-content-${element.id}`, content);

        // Trigger custom event
        const event = new CustomEvent('froalaBlur', {
            detail: {
                element: element,
                content: content
            }
        });
        document.dispatchEvent(event);
    }

    applyCustomStyling() {
        // Add custom CSS for better theme integration
        const customCSS = `
            <style>
                .fr-toolbar {
                    background: var(--bg-surface) !important;
                    border-color: var(--border-primary) !important;
                    color: var(--text-primary) !important;
                }

                .fr-toolbar .fr-btn {
                    color: var(--text-primary) !important;
                }

                .fr-toolbar .fr-btn:hover {
                    background: var(--bg-primary) !important;
                }

                .fr-box {
                    border-color: var(--border-primary) !important;
                }

                .fr-wrapper {
                    background: var(--bg-surface) !important;
                    color: var(--text-primary) !important;
                }

                .fr-element {
                    color: var(--text-primary) !important;
                }

                .fr-placeholder {
                    color: var(--text-secondary) !important;
                }
            </style>
        `;

        if (!document.querySelector('#froala-custom-styles')) {
            document.head.insertAdjacentHTML('beforeend', customCSS);
        }
    }

    // Utility methods
    getContent(element) {
        return this.editor ? this.editor.html.get() : element.innerHTML;
    }

    setContent(element, content) {
        if (this.editor) {
            this.editor.html.set(content);
        } else {
            element.innerHTML = content;
        }
    }

    destroy() {
        if (this.editor) {
            this.editor.destroy();
        }
    }

    // API methods for external integration
    insertText(text) {
        if (this.editor) {
            this.editor.html.insert(text);
        }
    }

    getWordCount() {
        return this.editor ? this.editor.wordCounter.count() : 0;
    }

    getCharCount() {
        return this.editor ? this.editor.charCounter.count() : 0;
    }

    toggleCodeView() {
        if (this.editor) {
            this.editor.codeView.toggle();
        }
    }
}

// Initialize Froala Editor Manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.froalaEditorManager = new FroalaEditorManager();
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = FroalaEditorManager;
}