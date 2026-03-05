/**
 * Trix Editor Integration for ValidoAI
 * Modern, lightweight WYSIWYG editor from Basecamp
 */

class ValidoAITrix {
    constructor() {
        this.editors = new Map();
        this.Trix = null;
    }

    async init(selector, config = {}) {
        const editorId = this.generateId();
        const mergedConfig = this.mergeConfig(config);

        // Load Trix if not already loaded
        if (!window.Trix) {
            await this.loadTrix();
        }

        try {
            const editor = this.createEditor(selector, mergedConfig);
            this.editors.set(editorId, {
                editor: editor,
                selector: selector,
                config: mergedConfig,
                trixEditor: null,
                element: null
            });

            this.applyThemeIntegration(editorId);
            this.addCustomFeatures(editorId);

            return editorId;
        } catch (error) {
            console.error('Trix editor initialization failed:', error);
            throw error;
        }
    }

    async loadTrix() {
        return new Promise((resolve, reject) => {
            // Load Trix CSS
            const cssLink = document.createElement('link');
            cssLink.rel = 'stylesheet';
            cssLink.href = 'https://unpkg.com/trix@2.0.8/dist/trix.css';
            document.head.appendChild(cssLink);

            // Load Trix JS
            const script = document.createElement('script');
            script.src = 'https://unpkg.com/trix@2.0.8/dist/trix.umd.min.js';
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        });
    }

    mergeConfig(userConfig) {
        const defaultConfig = {
            placeholder: 'Start writing your content here...',
            autofocus: false,
            className: 'trix-editor',
            ...userConfig
        };

        return defaultConfig;
    }

    createEditor(selector, config) {
        const element = document.querySelector(selector);
        if (!element) {
            throw new Error(`Element with selector '${selector}' not found`);
        }

        // Create Trix editor container
        const editorContainer = document.createElement('div');
        editorContainer.className = 'trix-editor-container';
        element.parentNode.insertBefore(editorContainer, element);
        element.style.display = 'none';

        // Create toolbar
        const toolbar = document.createElement('div');
        toolbar.className = 'trix-toolbar';
        editorContainer.appendChild(toolbar);

        // Create editor
        const editor = document.createElement('div');
        editor.className = 'trix-editor';
        editor.contentEditable = true;
        editor.setAttribute('data-trix-placeholder', config.placeholder);
        editorContainer.appendChild(editor);

        // Add custom CSS
        this.addCustomCSS(editorContainer);

        // Initialize Trix editor
        const trixEditor = new Trix.Editor({
            element: editor,
            toolbarElement: toolbar
        });

        // Store references
        const editorData = this.editors.get(this.editors.size);
        if (editorData) {
            editorData.trixEditor = trixEditor;
            editorData.element = editor;
        }

        return {
            container: editorContainer,
            toolbar: toolbar,
            editor: editor,
            trixEditor: trixEditor
        };
    }

    addCustomCSS(container) {
        const style = document.createElement('style');
        style.textContent = `
            .trix-editor-container {
                border: 1px solid var(--border-primary, #e5e7eb);
                border-radius: 8px;
                overflow: hidden;
                background: var(--bg-primary, #ffffff);
                font-family: 'Inter', sans-serif;
            }

            .trix-toolbar {
                background: var(--bg-secondary, #f9fafb);
                border-bottom: 1px solid var(--border-primary, #e5e7eb);
                padding: 8px;
                display: flex;
                flex-wrap: wrap;
                gap: 4px;
            }

            .trix-button-group {
                display: flex;
                gap: 2px;
                margin-right: 8px;
            }

            .trix-button {
                background: var(--bg-primary, #ffffff);
                border: 1px solid var(--border-primary, #e5e7eb);
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 12px;
                color: var(--text-primary, #374151);
                cursor: pointer;
                transition: all 0.2s ease;
                min-width: 28px;
                height: 28px;
                display: flex;
                align-items: center;
                justify-content: center;
            }

            .trix-button:hover {
                background: var(--bg-hover, #f3f4f6);
                border-color: var(--primary-500, #3b82f6);
            }

            .trix-button.trix-active {
                background: var(--primary-600, #2563eb);
                border-color: var(--primary-600, #2563eb);
                color: white;
            }

            .trix-button[data-trix-attribute="href"] {
                position: relative;
            }

            .trix-editor {
                min-height: 200px;
                padding: 1rem;
                background: var(--bg-primary, #ffffff);
                color: var(--text-primary, #374151);
                font-size: 14px;
                line-height: 1.6;
                outline: none;
            }

            .trix-editor::before {
                color: var(--text-muted, #9ca3af);
                font-style: normal;
            }

            .trix-editor:focus {
                outline: none;
            }

            .trix-dialog {
                background: var(--bg-primary, #ffffff);
                border: 1px solid var(--border-primary, #e5e7eb);
                border-radius: 6px;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
                padding: 1rem;
                position: absolute;
                z-index: 1000;
            }

            .trix-dialog input {
                width: 100%;
                padding: 8px;
                border: 1px solid var(--border-primary, #e5e7eb);
                border-radius: 4px;
                margin-bottom: 8px;
                font-size: 14px;
            }

            .trix-dialog button {
                background: var(--primary-600, #2563eb);
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 14px;
            }

            .trix-dialog button:hover {
                background: var(--primary-700, #1d4ed8);
            }

            /* File tools */
            .trix-attachment {
                background: var(--bg-secondary, #f9fafb);
                border: 1px solid var(--border-primary, #e5e7eb);
                border-radius: 4px;
                padding: 8px;
                margin: 8px 0;
                display: inline-flex;
                align-items: center;
                gap: 8px;
            }

            .trix-attachment__name {
                color: var(--text-primary, #374151);
                font-size: 14px;
            }

            .trix-attachment__size {
                color: var(--text-muted, #9ca3af);
                font-size: 12px;
            }

            .trix-attachment__remove {
                background: none;
                border: none;
                color: var(--error-500, #ef4444);
                cursor: pointer;
                font-size: 18px;
                line-height: 1;
                padding: 0;
            }

            /* Dark theme support */
            .trix-dark-theme .trix-editor-container {
                background: #1f2937;
                border-color: #4b5563;
            }

            .trix-dark-theme .trix-toolbar {
                background: #374151;
                border-color: #4b5563;
            }

            .trix-dark-theme .trix-button {
                background: #4b5563;
                border-color: #6b7280;
                color: #f9fafb;
            }

            .trix-dark-theme .trix-button:hover {
                background: #6b7280;
                border-color: #9ca3af;
            }

            .trix-dark-theme .trix-button.trix-active {
                background: var(--primary-600, #2563eb);
                border-color: var(--primary-600, #2563eb);
            }

            .trix-dark-theme .trix-editor {
                background: #1f2937;
                color: #f9fafb;
            }

            .trix-dark-theme .trix-editor::before {
                color: #9ca3af;
            }

            .trix-dark-theme .trix-dialog {
                background: #374151;
                border-color: #4b5563;
            }

            .trix-dark-theme .trix-dialog input {
                background: #4b5563;
                border-color: #6b7280;
                color: #f9fafb;
            }

            .trix-dark-theme .trix-attachment {
                background: #374151;
                border-color: #4b5563;
            }

            .trix-dark-theme .trix-attachment__name {
                color: #f9fafb;
            }

            .trix-dark-theme .trix-attachment__size {
                color: #d1d5db;
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
        container.classList.remove('trix-dark-theme');

        // Add theme class for dark themes
        const isDark = ['valido-dark', 'material-dark', 'dracula', 'monokai'].includes(theme);
        if (isDark) {
            container.classList.add('trix-dark-theme');
        }
    }

    addCustomFeatures(editorId) {
        const editorData = this.editors.get(editorId);
        if (!editorData || !editorData.trixEditor) return;

        const trixEditor = editorData.trixEditor;
        const element = editorData.editor.editor;

        // Add auto-save functionality
        this.addAutoSave(trixEditor, editorId);

        // Add word count
        this.addWordCount(trixEditor, editorId);

        // Add export functionality
        this.addExportFeatures(trixEditor, editorId);

        // Add custom toolbar buttons
        this.addCustomToolbarButtons(trixEditor, editorId);

        // Add keyboard shortcuts
        this.addKeyboardShortcuts(trixEditor, editorId);

        // Add custom attachment handling
        this.addAttachmentHandler(trixEditor, editorId);

        // Add content validation
        this.addContentValidation(trixEditor, editorId);
    }

    addAutoSave(trixEditor, editorId) {
        let saveTimeout;
        trixEditor.element.addEventListener('input', () => {
            clearTimeout(saveTimeout);
            saveTimeout = setTimeout(() => {
                const content = trixEditor.element.innerHTML;
                const timestamp = new Date().toISOString();

                localStorage.setItem(`trix_autosave_${editorId}`, JSON.stringify({
                    content: content,
                    timestamp: timestamp
                }));

                if (window.showToast) {
                    showToast('success', 'Content auto-saved', { position: 'top-right', duration: 2000 });
                }
            }, 1000);
        });
    }

    addWordCount(trixEditor, editorId) {
        const wordCountElement = document.createElement('div');
        wordCountElement.className = 'trix-word-count';
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
            const text = trixEditor.element.textContent || '';
            const words = text.trim().split(/\s+/).filter(word => word.length > 0).length;
            const chars = text.length;
            wordCountElement.textContent = `${words} words, ${chars} chars`;
        };

        trixEditor.element.parentNode.appendChild(wordCountElement);
        trixEditor.element.addEventListener('input', updateWordCount);
        updateWordCount();
    }

    addExportFeatures(trixEditor, editorId) {
        // Add export buttons to toolbar
        const toolbar = trixEditor.element.previousElementSibling;
        if (toolbar) {
            // Add custom button for HTML export
            const htmlButton = document.createElement('button');
            htmlButton.innerHTML = '📄';
            htmlButton.title = 'Export as HTML';
            htmlButton.className = 'trix-button';
            htmlButton.onclick = () => this.exportAsHTML(trixEditor);
            toolbar.appendChild(htmlButton);

            // Add custom button for plain text export
            const textButton = document.createElement('button');
            textButton.innerHTML = '📝';
            textButton.title = 'Export as Text';
            textButton.className = 'trix-button';
            textButton.onclick = () => this.exportAsText(trixEditor);
            toolbar.appendChild(textButton);
        }
    }

    addCustomToolbarButtons(trixEditor, editorId) {
        // Add custom format buttons
        const toolbar = trixEditor.element.previousElementSibling;

        // Add clear formatting button
        const clearButton = document.createElement('button');
        clearButton.innerHTML = '🧹';
        clearButton.title = 'Clear all formatting';
        clearButton.className = 'trix-button';
        clearButton.onclick = () => {
            trixEditor.setSelectedRange([0, trixEditor.getDocument().getLength()]);
            trixEditor.deleteInDirection('forward');
            trixEditor.insertHTML('');
        };
        toolbar.appendChild(clearButton);

        // Add timestamp button
        const timestampButton = document.createElement('button');
        timestampButton.innerHTML = '🕐';
        timestampButton.title = 'Insert timestamp';
        timestampButton.className = 'trix-button';
        timestampButton.onclick = () => {
            const timestamp = new Date().toLocaleString();
            trixEditor.insertString(timestamp);
        };
        toolbar.appendChild(timestampButton);
    }

    addKeyboardShortcuts(trixEditor, editorId) {
        // Add custom keyboard shortcuts
        trixEditor.element.addEventListener('keydown', (e) => {
            if (e.ctrlKey || e.metaKey) {
                switch (e.key) {
                    case 's':
                        e.preventDefault();
                        this.saveContent(trixEditor);
                        break;
                    case 'e':
                        if (e.shiftKey) {
                            e.preventDefault();
                            this.exportAsHTML(trixEditor);
                        }
                        break;
                }
            }
        });
    }

    addAttachmentHandler(trixEditor, editorId) {
        trixEditor.element.addEventListener('trix-attachment-add', (event) => {
            const attachment = event.attachment;
            if (attachment.file) {
                this.uploadFile(trixEditor, attachment);
            }
        });
    }

    async uploadFile(trixEditor, attachment) {
        try {
            const formData = new FormData();
            formData.append('file', attachment.file);

            const response = await fetch('/api/upload/file', {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                const data = await response.json();
                attachment.setAttributes({
                    url: data.location,
                    href: data.location
                });
            } else {
                throw new Error('Upload failed');
            }
        } catch (error) {
            console.error('File upload failed:', error);
            attachment.remove();
            if (window.showToast) {
                showToast('error', 'File upload failed');
            }
        }
    }

    addContentValidation(trixEditor, editorId) {
        trixEditor.element.addEventListener('trix-change', () => {
            const content = trixEditor.element.innerHTML;
            const textLength = trixEditor.element.textContent.length;

            // Example validation: warn if content is too long
            if (textLength > 10000) {
                if (window.showToast) {
                    showToast('warning', 'Content is getting long', { duration: 3000 });
                }
            }
        });
    }

    saveContent(trixEditor) {
        const content = trixEditor.element.innerHTML;

        fetch('/api/editor/save', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                content: content,
                editorType: 'trix'
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

    exportAsHTML(trixEditor) {
        const content = trixEditor.element.innerHTML;
        const htmlContent = `
            <!DOCTYPE html>
            <html>
            <head>
                <title>Trix Export</title>
                <style>
                    body { font-family: 'Inter', sans-serif; padding: 20px; max-width: 800px; margin: 0 auto; }
                    img { max-width: 100%; height: auto; }
                    figure { margin: 1rem 0; }
                    figcaption { font-style: italic; color: #666; }
                    * { box-sizing: border-box; }
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
        a.download = 'trix-export.html';
        a.click();
        URL.revokeObjectURL(url);

        if (window.showToast) {
            showToast('success', 'Exported as HTML');
        }
    }

    exportAsText(trixEditor) {
        const text = trixEditor.element.textContent || '';
        const blob = new Blob([text], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'trix-export.txt';
        a.click();
        URL.revokeObjectURL(url);

        if (window.showToast) {
            showToast('success', 'Exported as text');
        }
    }

    // Utility methods
    generateId() {
        return 'trix_' + Math.random().toString(36).substr(2, 9);
    }

    destroy(editorId) {
        const editorData = this.editors.get(editorId);
        if (editorData) {
            if (editorData.trixEditor) {
                // Trix doesn't have a destroy method, but we can remove the container
                editorData.editor.container.remove();
            }
            this.editors.delete(editorId);
        }
    }

    getEditor(editorId) {
        const editorData = this.editors.get(editorId);
        return editorData ? editorData.trixEditor : null;
    }

    setContent(editorId, content) {
        const editorData = this.editors.get(editorId);
        if (editorData && editorData.trixEditor) {
            editorData.trixEditor.loadHTML(content);
        }
    }

    getContent(editorId) {
        const editorData = this.editors.get(editorId);
        if (editorData && editorData.trixEditor) {
            return editorData.trixEditor.element.innerHTML;
        }
        return '';
    }

    getText(editorId) {
        const editorData = this.editors.get(editorId);
        if (editorData && editorData.trixEditor) {
            return editorData.trixEditor.element.textContent || '';
        }
        return '';
    }

    // Additional Trix-specific methods
    insertImage(editorId, url, attributes = {}) {
        const editorData = this.editors.get(editorId);
        if (editorData && editorData.trixEditor) {
            const attachment = new Trix.Attachment({
                contentType: 'image',
                filename: attributes.filename || 'image',
                filesize: attributes.filesize || 0,
                url: url,
                ...attributes
            });
            editorData.trixEditor.insertAttachment(attachment);
        }
    }

    insertFile(editorId, url, attributes = {}) {
        const editorData = this.editors.get(editorId);
        if (editorData && editorData.trixEditor) {
            const attachment = new Trix.Attachment({
                contentType: attributes.contentType || 'application/octet-stream',
                filename: attributes.filename || 'file',
                filesize: attributes.filesize || 0,
                url: url,
                ...attributes
            });
            editorData.trixEditor.insertAttachment(attachment);
        }
    }

    setPlaceholder(editorId, placeholder) {
        const editorData = this.editors.get(editorId);
        if (editorData && editorData.editor.editor) {
            editorData.editor.editor.setAttribute('data-trix-placeholder', placeholder);
        }
    }

    focus(editorId) {
        const editorData = this.editors.get(editorId);
        if (editorData && editorData.trixEditor) {
            editorData.trixEditor.element.focus();
        }
    }

    blur(editorId) {
        const editorData = this.editors.get(editorId);
        if (editorData && editorData.trixEditor) {
            editorData.trixEditor.element.blur();
        }
    }
}

// Global instance
window.ValidoAITrix = new ValidoAITrix();
