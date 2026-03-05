/**
 * Quill.js Integration for ValidoAI
 * Lightweight, flexible WYSIWYG editor
 */

class ValidoAIQuill {
    constructor() {
        this.editors = new Map();
        this.Quill = null;
    }

    async init(selector, config = {}) {
        const editorId = this.generateId();
        const mergedConfig = this.mergeConfig(config);

        // Load Quill.js if not already loaded
        if (!window.Quill) {
            await this.loadQuill();
        }

        try {
            const editor = this.createEditor(selector, mergedConfig);
            this.editors.set(editorId, {
                editor: editor,
                selector: selector,
                config: mergedConfig,
                quill: null
            });

            this.applyThemeIntegration(editorId);
            this.addCustomFeatures(editorId);

            return editorId;
        } catch (error) {
            console.error('Quill editor initialization failed:', error);
            throw error;
        }
    }

    async loadQuill() {
        return new Promise((resolve, reject) => {
            // Load Quill.js from CDN
            const link = document.createElement('link');
            link.rel = 'stylesheet';
            link.href = 'https://cdn.quilljs.com/1.3.7/quill.snow.css';
            document.head.appendChild(link);

            const script = document.createElement('script');
            script.src = 'https://cdn.quilljs.com/1.3.7/quill.js';
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        });
    }

    mergeConfig(userConfig) {
        const defaultConfig = {
            theme: 'snow',
            placeholder: 'Start writing your content here...',
            modules: {
                toolbar: [
                    [{ 'header': [1, 2, 3, 4, 5, 6, false] }],
                    ['bold', 'italic', 'underline', 'strike'],
                    [{ 'color': [] }, { 'background': [] }],
                    [{ 'script': 'sub'}, { 'script': 'super' }],
                    [{ 'list': 'ordered'}, { 'list': 'bullet' }],
                    [{ 'indent': '-1'}, { 'indent': '+1' }],
                    [{ 'align': [] }],
                    ['blockquote', 'code-block'],
                    ['link', 'image', 'video'],
                    ['clean']
                ],
                clipboard: {
                    matchVisual: false
                },
                history: {
                    delay: 1000,
                    maxStack: 50,
                    userOnly: false
                },
                keyboard: {
                    bindings: {
                        tab: {
                            key: 9,
                            handler: function(range, context) {
                                return true;
                            }
                        }
                    }
                }
            },
            formats: [
                'header', 'bold', 'italic', 'underline', 'strike', 'blockquote',
                'list', 'bullet', 'indent', 'link', 'image', 'color', 'background',
                'align', 'script', 'code-block', 'video'
            ],
            ...userConfig
        };

        return defaultConfig;
    }

    createEditor(selector, config) {
        const element = document.querySelector(selector);
        if (!element) {
            throw new Error(`Element with selector '${selector}' not found`);
        }

        // Create editor container
        const editorContainer = document.createElement('div');
        editorContainer.className = 'quill-editor-container';
        element.parentNode.insertBefore(editorContainer, element);
        element.style.display = 'none';

        // Create toolbar and editor divs
        const toolbar = document.createElement('div');
        toolbar.className = 'ql-toolbar';
        editorContainer.appendChild(toolbar);

        const editorDiv = document.createElement('div');
        editorDiv.className = 'ql-editor';
        editorDiv.style.minHeight = '200px';
        editorContainer.appendChild(editorDiv);

        // Initialize Quill
        const quill = new Quill(editorDiv, {
            ...config,
            modules: {
                ...config.modules,
                toolbar: toolbar
            }
        });

        // Store reference to quill instance
        const editorData = this.editors.get(this.editors.size);
        if (editorData) {
            editorData.quill = quill;
        }

        // Add custom CSS
        this.addCustomCSS(editorContainer);

        return {
            container: editorContainer,
            toolbar: toolbar,
            editor: editorDiv,
            quill: quill
        };
    }

    addCustomCSS(container) {
        const style = document.createElement('style');
        style.textContent = `
            .quill-editor-container {
                border: 1px solid var(--border-primary, #e5e7eb);
                border-radius: 8px;
                overflow: hidden;
                background: var(--bg-primary, #ffffff);
            }

            .quill-editor-container .ql-toolbar {
                border: none;
                border-bottom: 1px solid var(--border-primary, #e5e7eb);
                background: var(--bg-secondary, #f9fafb);
            }

            .quill-editor-container .ql-editor {
                border: none;
                font-family: 'Inter', sans-serif;
                font-size: 14px;
                line-height: 1.6;
                color: var(--text-primary, #374151);
                padding: 1rem;
            }

            .quill-editor-container .ql-editor.ql-blank::before {
                color: var(--text-muted, #9ca3af);
                font-style: normal;
            }

            .quill-editor-container .ql-toolbar .ql-picker-label,
            .quill-editor-container .ql-toolbar .ql-stroke,
            .quill-editor-container .ql-toolbar .ql-fill {
                color: var(--text-secondary, #6b7280);
            }

            .quill-editor-container .ql-toolbar button:hover,
            .quill-editor-container .ql-toolbar .ql-picker-label:hover,
            .quill-editor-container .ql-toolbar .ql-stroke:hover,
            .quill-editor-container .ql-toolbar .ql-fill:hover {
                color: var(--text-primary, #374151);
            }

            .quill-editor-container .ql-toolbar button.ql-active,
            .quill-editor-container .ql-toolbar .ql-picker-label.ql-active,
            .quill-editor-container .ql-toolbar .ql-stroke.ql-active,
            .quill-editor-container .ql-toolbar .ql-fill.ql-active {
                color: var(--primary-600, #3b82f6);
            }

            .quill-editor-container .ql-toolbar .ql-picker-options {
                background: var(--bg-primary, #ffffff);
                border: 1px solid var(--border-primary, #e5e7eb);
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
                z-index: 9999;
            }

            .quill-editor-container .ql-toolbar .ql-picker-item {
                color: var(--text-primary, #374151);
            }

            .quill-editor-container .ql-toolbar .ql-picker-item:hover {
                background: var(--bg-secondary, #f9fafb);
            }

            /* Dark theme support */
            .quill-dark-theme .quill-editor-container {
                background: #1f2937;
                border-color: #4b5563;
            }

            .quill-dark-theme .quill-editor-container .ql-toolbar {
                background: #374151;
                border-color: #4b5563;
            }

            .quill-dark-theme .quill-editor-container .ql-editor {
                background: #1f2937;
                color: #f9fafb;
            }

            .quill-dark-theme .quill-editor-container .ql-editor.ql-blank::before {
                color: #9ca3af;
            }

            .quill-dark-theme .quill-editor-container .ql-toolbar .ql-picker-label,
            .quill-dark-theme .quill-editor-container .ql-toolbar .ql-stroke,
            .quill-dark-theme .quill-editor-container .ql-toolbar .ql-fill {
                color: #d1d5db;
            }

            .quill-dark-theme .quill-editor-container .ql-toolbar button:hover,
            .quill-dark-theme .quill-editor-container .ql-toolbar .ql-picker-label:hover,
            .quill-dark-theme .quill-editor-container .ql-toolbar .ql-stroke:hover,
            .quill-dark-theme .quill-editor-container .ql-toolbar .ql-fill:hover {
                color: #f9fafb;
            }

            .quill-dark-theme .quill-editor-container .ql-toolbar .ql-picker-options {
                background: #374151;
                border-color: #4b5563;
            }

            .quill-dark-theme .quill-editor-container .ql-toolbar .ql-picker-item {
                color: #f9fafb;
            }

            .quill-dark-theme .quill-editor-container .ql-toolbar .ql-picker-item:hover {
                background: #4b5563;
            }
        `;
        document.head.appendChild(style);
    }

    applyThemeIntegration(editorId) {
        const editorData = this.editors.get(editorId);
        if (!editorData) return;

        // Listen for theme changes
        document.addEventListener('themeChanged', (event) => {
            this.updateEditorTheme(editorId, event.detail.theme);
        });

        // Initial theme application
        const currentTheme = localStorage.getItem('valido-theme') || 'valido-white';
        this.updateEditorTheme(editorId, currentTheme);
    }

    updateEditorTheme(editorId, theme) {
        const editorData = this.editors.get(editorId);
        if (!editorData) return;

        const container = editorData.editor.container;

        // Remove existing theme classes
        container.classList.remove('quill-dark-theme');

        // Add theme class for dark themes
        const isDark = ['valido-dark', 'material-dark', 'dracula', 'monokai'].includes(theme);
        if (isDark) {
            container.classList.add('quill-dark-theme');
        }
    }

    addCustomFeatures(editorId) {
        const editorData = this.editors.get(editorId);
        if (!editorData || !editorData.quill) return;

        const quill = editorData.quill;

        // Add auto-save functionality
        this.addAutoSave(quill, editorId);

        // Add word count
        this.addWordCount(quill, editorId);

        // Add export functionality
        this.addExportFeatures(quill, editorId);

        // Add custom toolbar buttons
        this.addCustomToolbarButtons(quill, editorId);

        // Add image upload handler
        this.addImageHandler(quill);

        // Add keyboard shortcuts
        this.addKeyboardShortcuts(quill);
    }

    addAutoSave(quill, editorId) {
        let saveTimeout;
        quill.on('text-change', () => {
            clearTimeout(saveTimeout);
            saveTimeout = setTimeout(() => {
                const content = quill.root.innerHTML;
                const timestamp = new Date().toISOString();

                localStorage.setItem(`quill_autosave_${editorId}`, JSON.stringify({
                    content: content,
                    timestamp: timestamp
                }));

                if (window.showToast) {
                    showToast('success', 'Content auto-saved', { position: 'top-right', duration: 2000 });
                }
            }, 1000);
        });
    }

    addWordCount(quill, editorId) {
        const wordCountElement = document.createElement('div');
        wordCountElement.className = 'quill-word-count';
        wordCountElement.style.cssText = `
            position: absolute;
            bottom: 10px;
            right: 10px;
            background: rgba(0, 0, 0, 0.7);
            color: white;
            padding: 5px 10px;
            border-radius: 4px;
            font-size: 12px;
            z-index: 1000;
        `;

        const updateWordCount = () => {
            const text = quill.getText();
            const words = text.trim().split(/\s+/).filter(word => word.length > 0).length;
            const chars = text.length;
            wordCountElement.textContent = `${words} words, ${chars} chars`;
        };

        quill.root.parentNode.appendChild(wordCountElement);
        quill.on('text-change', updateWordCount);
        updateWordCount();
    }

    addExportFeatures(quill, editorId) {
        // Add export buttons to toolbar
        const toolbar = quill.getModule('toolbar');
        if (toolbar) {
            // Add custom button for HTML export
            const htmlButton = document.createElement('button');
            htmlButton.innerHTML = '📄';
            htmlButton.title = 'Export as HTML';
            htmlButton.onclick = () => this.exportAsHTML(quill);
            htmlButton.className = 'ql-custom-button';
            toolbar.container.appendChild(htmlButton);

            // Add custom button for plain text export
            const textButton = document.createElement('button');
            textButton.innerHTML = '📝';
            textButton.title = 'Export as Text';
            textButton.onclick = () => this.exportAsText(quill);
            textButton.className = 'ql-custom-button';
            toolbar.container.appendChild(textButton);
        }
    }

    addCustomToolbarButtons(quill, editorId) {
        // Add custom format buttons
        const toolbar = quill.getModule('toolbar');

        // Add clear formatting button
        const clearButton = document.createElement('button');
        clearButton.innerHTML = '🧹';
        clearButton.title = 'Clear all formatting';
        clearButton.onclick = () => {
            const range = quill.getSelection();
            if (range) {
                quill.formatText(range.index, range.length, 'bold', false);
                quill.formatText(range.index, range.length, 'italic', false);
                quill.formatText(range.index, range.length, 'underline', false);
                quill.formatText(range.index, range.length, 'strike', false);
                quill.formatText(range.index, range.length, 'color', false);
                quill.formatText(range.index, range.length, 'background', false);
            }
        };
        clearButton.className = 'ql-custom-button';
        toolbar.container.appendChild(clearButton);
    }

    addImageHandler(quill) {
        const toolbar = quill.getModule('toolbar');
        const imageButton = toolbar.container.querySelector('.ql-image');

        if (imageButton) {
            imageButton.addEventListener('click', (e) => {
                e.preventDefault();

                const input = document.createElement('input');
                input.type = 'file';
                input.accept = 'image/*';
                input.onchange = (event) => {
                    const file = event.target.files[0];
                    if (file) {
                        this.uploadImage(quill, file);
                    }
                };
                input.click();
            });
        }
    }

    async uploadImage(quill, file) {
        try {
            const formData = new FormData();
            formData.append('file', file);

            const response = await fetch('/api/upload/image', {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                const data = await response.json();
                const range = quill.getSelection();
                if (range) {
                    quill.insertEmbed(range.index, 'image', data.location);
                }
            } else {
                throw new Error('Upload failed');
            }
        } catch (error) {
            console.error('Image upload failed:', error);
            if (window.showToast) {
                showToast('error', 'Image upload failed');
            }
        }
    }

    addKeyboardShortcuts(quill) {
        // Add custom keyboard shortcuts
        quill.keyboard.addBinding({
            key: 'S',
            ctrlKey: true
        }, () => {
            this.saveContent(quill);
            return false;
        });

        quill.keyboard.addBinding({
            key: 'E',
            ctrlKey: true,
            shiftKey: true
        }, () => {
            this.exportAsHTML(quill);
            return false;
        });
    }

    saveContent(quill) {
        const content = quill.root.innerHTML;

        fetch('/api/editor/save', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                content: content,
                editorType: 'quill'
            })
        }).then(response => {
            if (response.ok) {
                if (window.showToast) {
                    showToast('success', 'Content saved successfully');
                }
            }
        }).catch(error => {
            if (window.showToast) {
                showToast('error', 'Save failed: ' + error.message);
            }
        });
    }

    exportAsHTML(quill) {
        const content = quill.root.innerHTML;
        const htmlContent = `
            <!DOCTYPE html>
            <html>
            <head>
                <title>Quill Export</title>
                <style>
                    body { font-family: 'Inter', sans-serif; padding: 20px; }
                    img { max-width: 100%; height: auto; }
                </style>
            </head>
            <body>
                ${content}
            </body>
            </html>
        `;

        const blob = new Blob([htmlContent], { type: 'text/html' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'quill-export.html';
        a.click();
        URL.revokeObjectURL(url);

        if (window.showToast) {
            showToast('success', 'Exported as HTML');
        }
    }

    exportAsText(quill) {
        const text = quill.getText();
        const blob = new Blob([text], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'quill-export.txt';
        a.click();
        URL.revokeObjectURL(url);

        if (window.showToast) {
            showToast('success', 'Exported as text');
        }
    }

    // Utility methods
    generateId() {
        return 'quill_' + Math.random().toString(36).substr(2, 9);
    }

    destroy(editorId) {
        const editorData = this.editors.get(editorId);
        if (editorData) {
            if (editorData.quill) {
                // Quill doesn't have a destroy method, but we can remove the container
                editorData.editor.container.remove();
            }
            this.editors.delete(editorId);
        }
    }

    getEditor(editorId) {
        const editorData = this.editors.get(editorId);
        return editorData ? editorData.quill : null;
    }

    setContent(editorId, content) {
        const editorData = this.editors.get(editorId);
        if (editorData && editorData.quill) {
            editorData.quill.root.innerHTML = content;
        }
    }

    getContent(editorId) {
        const editorData = this.editors.get(editorId);
        if (editorData && editorData.quill) {
            return editorData.quill.root.innerHTML;
        }
        return '';
    }

    getText(editorId) {
        const editorData = this.editors.get(editorId);
        if (editorData && editorData.quill) {
            return editorData.quill.getText();
        }
        return '';
    }
}

// Global instance
window.ValidoAIQuill = new ValidoAIQuill();
