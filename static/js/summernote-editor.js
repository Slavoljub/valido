/**
 * Summernote Integration for ValidoAI
 * Bootstrap-based WYSIWYG editor with intuitive interface
 */

class ValidoAISummernote {
    constructor() {
        this.editors = new Map();
        this.Summernote = null;
    }

    async init(selector, config = {}) {
        const editorId = this.generateId();
        const mergedConfig = this.mergeConfig(config);

        // Load Summernote if not already loaded
        if (!window.jQuery || !window.jQuery.fn.summernote) {
            await this.loadSummernote();
        }

        try {
            const editor = this.createEditor(selector, mergedConfig);
            this.editors.set(editorId, {
                editor: editor,
                selector: selector,
                config: mergedConfig,
                summernote: null
            });

            this.applyThemeIntegration(editorId);
            this.addCustomFeatures(editorId);

            return editorId;
        } catch (error) {
            console.error('Summernote editor initialization failed:', error);
            throw error;
        }
    }

    async loadSummernote() {
        return new Promise((resolve, reject) => {
            // Load jQuery first if not available
            if (!window.jQuery) {
                const jqueryScript = document.createElement('script');
                jqueryScript.src = 'https://code.jquery.com/jquery-3.6.0.min.js';
                jqueryScript.onload = () => this.loadSummernoteCSSAndJS(resolve, reject);
                jqueryScript.onerror = reject;
                document.head.appendChild(jqueryScript);
            } else {
                this.loadSummernoteCSSAndJS(resolve, reject);
            }
        });
    }

    loadSummernoteCSSAndJS(resolve, reject) {
        // Load Summernote CSS
        const cssLink = document.createElement('link');
        cssLink.rel = 'stylesheet';
        cssLink.href = 'https://cdn.jsdelivr.net/npm/summernote@0.8.20/dist/summernote-lite.min.css';
        document.head.appendChild(cssLink);

        // Load Summernote JS
        const script = document.createElement('script');
        script.src = 'https://cdn.jsdelivr.net/npm/summernote@0.8.20/dist/summernote-lite.min.js';
        script.onload = resolve;
        script.onerror = reject;
        document.head.appendChild(script);
    }

    mergeConfig(userConfig) {
        const defaultConfig = {
            height: 300,
            placeholder: 'Start writing your content here...',
            toolbar: [
                ['style', ['style']],
                ['font', ['bold', 'underline', 'clear']],
                ['fontname', ['fontname']],
                ['color', ['color']],
                ['para', ['ul', 'ol', 'paragraph']],
                ['table', ['table']],
                ['insert', ['link', 'picture', 'video']],
                ['view', ['fullscreen', 'codeview', 'help']]
            ],
            callbacks: {
                onInit: function() {
                    // Custom initialization
                },
                onChange: function(contents, $editable) {
                    // Handle content changes
                },
                onImageUpload: function(files) {
                    // Handle image uploads
                }
            },
            ...userConfig
        };

        return defaultConfig;
    }

    createEditor(selector, config) {
        const element = document.querySelector(selector);
        if (!element) {
            throw new Error(`Element with selector '${selector}' not found`);
        }

        // Initialize Summernote
        const $element = window.jQuery(element);
        $element.summernote(config);

        // Store reference
        const editorData = this.editors.get(this.editors.size);
        if (editorData) {
            editorData.summernote = $element;
        }

        // Add custom CSS
        this.addCustomCSS(element);

        return {
            element: element,
            $element: $element
        };
    }

    addCustomCSS(element) {
        const style = document.createElement('style');
        style.textContent = `
            .note-editor {
                border: 1px solid var(--border-primary, #e5e7eb) !important;
                border-radius: 8px !important;
                overflow: hidden !important;
                background: var(--bg-primary, #ffffff) !important;
            }

            .note-toolbar {
                background: var(--bg-secondary, #f9fafb) !important;
                border-bottom: 1px solid var(--border-primary, #e5e7eb) !important;
                padding: 8px !important;
            }

            .note-toolbar .btn {
                border: 1px solid var(--border-primary, #e5e7eb) !important;
                background: var(--bg-primary, #ffffff) !important;
                color: var(--text-primary, #374151) !important;
                border-radius: 4px !important;
                padding: 4px 8px !important;
                font-size: 12px !important;
                margin-right: 2px !important;
            }

            .note-toolbar .btn:hover {
                background: var(--bg-hover, #f3f4f6) !important;
                border-color: var(--primary-500, #3b82f6) !important;
            }

            .note-toolbar .btn.active,
            .note-toolbar .btn:active {
                background: var(--primary-600, #2563eb) !important;
                border-color: var(--primary-600, #2563eb) !important;
                color: white !important;
            }

            .note-editing-area {
                background: var(--bg-primary, #ffffff) !important;
            }

            .note-editing-area .note-editable {
                background: var(--bg-primary, #ffffff) !important;
                color: var(--text-primary, #374151) !important;
                font-family: 'Inter', sans-serif !important;
                font-size: 14px !important;
                line-height: 1.6 !important;
                padding: 1rem !important;
                min-height: 200px !important;
            }

            .note-editing-area .note-editable:focus {
                outline: none !important;
            }

            .note-statusbar {
                background: var(--bg-secondary, #f9fafb) !important;
                border-top: 1px solid var(--border-primary, #e5e7eb) !important;
                padding: 4px 8px !important;
                font-size: 12px !important;
                color: var(--text-muted, #9ca3af) !important;
            }

            .note-popover {
                background: var(--bg-primary, #ffffff) !important;
                border: 1px solid var(--border-primary, #e5e7eb) !important;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
                border-radius: 6px !important;
            }

            .note-popover .popover-content {
                background: var(--bg-primary, #ffffff) !important;
                color: var(--text-primary, #374151) !important;
            }

            /* Dropdown menus */
            .note-dropdown-menu {
                background: var(--bg-primary, #ffffff) !important;
                border: 1px solid var(--border-primary, #e5e7eb) !important;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
            }

            .note-dropdown-menu li a {
                color: var(--text-primary, #374151) !important;
                padding: 8px 12px !important;
            }

            .note-dropdown-menu li a:hover {
                background: var(--bg-secondary, #f9fafb) !important;
                color: var(--text-primary, #374151) !important;
            }

            /* Color picker */
            .note-color-palette .note-color-btn {
                border: 1px solid var(--border-primary, #e5e7eb) !important;
            }

            .note-color-palette .note-color-btn:hover {
                border-color: var(--primary-500, #3b82f6) !important;
            }

            /* Dark theme support */
            .summernote-dark-theme .note-editor {
                background: #1f2937 !important;
                border-color: #4b5563 !important;
            }

            .summernote-dark-theme .note-toolbar {
                background: #374151 !important;
                border-color: #4b5563 !important;
            }

            .summernote-dark-theme .note-toolbar .btn {
                background: #4b5563 !important;
                border-color: #6b7280 !important;
                color: #f9fafb !important;
            }

            .summernote-dark-theme .note-toolbar .btn:hover {
                background: #6b7280 !important;
                border-color: #9ca3af !important;
            }

            .summernote-dark-theme .note-toolbar .btn.active,
            .summernote-dark-theme .note-toolbar .btn:active {
                background: var(--primary-600, #2563eb) !important;
                border-color: var(--primary-600, #2563eb) !important;
            }

            .summernote-dark-theme .note-editing-area .note-editable {
                background: #1f2937 !important;
                color: #f9fafb !important;
            }

            .summernote-dark-theme .note-statusbar {
                background: #374151 !important;
                border-color: #4b5563 !important;
                color: #d1d5db !important;
            }

            .summernote-dark-theme .note-popover {
                background: #374151 !important;
                border-color: #4b5563 !important;
            }

            .summernote-dark-theme .note-popover .popover-content {
                background: #374151 !important;
                color: #f9fafb !important;
            }

            .summernote-dark-theme .note-dropdown-menu {
                background: #374151 !important;
                border-color: #4b5563 !important;
            }

            .summernote-dark-theme .note-dropdown-menu li a {
                color: #f9fafb !important;
            }

            .summernote-dark-theme .note-dropdown-menu li a:hover {
                background: #4b5563 !important;
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

        const element = editorData.editor.element;
        const $element = editorData.summernote;

        // Remove existing theme classes
        $element.parent().removeClass('summernote-dark-theme');

        // Add theme class for dark themes
        const isDark = ['valido-dark', 'material-dark', 'dracula', 'monokai'].includes(theme);
        if (isDark) {
            $element.parent().addClass('summernote-dark-theme');
        }
    }

    addCustomFeatures(editorId) {
        const editorData = this.editors.get(editorId);
        if (!editorData || !editorData.summernote) return;

        const $element = editorData.summernote;

        // Add auto-save functionality
        this.addAutoSave($element, editorId);

        // Add word count
        this.addWordCount($element, editorId);

        // Add export functionality
        this.addExportFeatures($element, editorId);

        // Add custom toolbar buttons
        this.addCustomToolbarButtons($element, editorId);

        // Add keyboard shortcuts
        this.addKeyboardShortcuts($element, editorId);

        // Add custom image upload handler
        this.addImageUploadHandler($element, editorId);
    }

    addAutoSave($element, editorId) {
        let saveTimeout;
        $element.on('summernote.change', () => {
            clearTimeout(saveTimeout);
            saveTimeout = setTimeout(() => {
                const content = $element.summernote('code');
                const timestamp = new Date().toISOString();

                localStorage.setItem(`summernote_autosave_${editorId}`, JSON.stringify({
                    content: content,
                    timestamp: timestamp
                }));

                if (window.showToast) {
                    showToast('success', 'Content auto-saved', { position: 'top-right', duration: 2000 });
                }
            }, 1000);
        });
    }

    addWordCount($element, editorId) {
        const wordCountElement = document.createElement('div');
        wordCountElement.className = 'summernote-word-count';
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
            const text = $element.summernote('code').replace(/<[^>]*>/g, ' ').replace(/\s+/g, ' ').trim();
            const words = text.split(' ').filter(word => word.length > 0).length;
            const chars = $element.summernote('code').replace(/<[^>]*>/g, '').length;
            wordCountElement.textContent = `${words} words, ${chars} chars`;
        };

        $element.parent().append(wordCountElement);
        $element.on('summernote.change', updateWordCount);
        updateWordCount();
    }

    addExportFeatures($element, editorId) {
        // Add export buttons to toolbar
        const toolbar = $element.parent().find('.note-toolbar');
        if (toolbar.length) {
            // Add custom button for HTML export
            const htmlButton = document.createElement('button');
            htmlButton.innerHTML = '📄';
            htmlButton.title = 'Export as HTML';
            htmlButton.className = 'btn btn-sm btn-outline-secondary note-btn';
            htmlButton.onclick = () => this.exportAsHTML($element);
            toolbar.append(htmlButton);

            // Add custom button for plain text export
            const textButton = document.createElement('button');
            textButton.innerHTML = '📝';
            textButton.title = 'Export as Text';
            textButton.className = 'btn btn-sm btn-outline-secondary note-btn';
            textButton.onclick = () => this.exportAsText($element);
            toolbar.append(textButton);

            // Add custom button for PDF export
            const pdfButton = document.createElement('button');
            pdfButton.innerHTML = '📕';
            pdfButton.title = 'Export as PDF';
            pdfButton.className = 'btn btn-sm btn-outline-secondary note-btn';
            pdfButton.onclick = () => this.exportAsPDF($element);
            toolbar.append(pdfButton);
        }
    }

    addCustomToolbarButtons($element, editorId) {
        // Add custom format buttons
        const toolbar = $element.parent().find('.note-toolbar');

        // Add clear formatting button
        const clearButton = document.createElement('button');
        clearButton.innerHTML = '🧹';
        clearButton.title = 'Clear all formatting';
        clearButton.className = 'btn btn-sm btn-outline-secondary note-btn';
        clearButton.onclick = () => {
            $element.summernote('removeFormat');
            $element.summernote('formatPara');
        };
        toolbar.append(clearButton);

        // Add timestamp button
        const timestampButton = document.createElement('button');
        timestampButton.innerHTML = '🕐';
        timestampButton.title = 'Insert timestamp';
        timestampButton.className = 'btn btn-sm btn-outline-secondary note-btn';
        timestampButton.onclick = () => {
            const timestamp = new Date().toLocaleString();
            $element.summernote('editor.insertText', timestamp);
        };
        toolbar.append(timestampButton);
    }

    addKeyboardShortcuts($element, editorId) {
        // Add custom keyboard shortcuts
        $element.on('summernote.keydown', (e) => {
            if (e.ctrlKey || e.metaKey) {
                switch (e.key) {
                    case 's':
                        e.preventDefault();
                        this.saveContent($element);
                        break;
                    case 'e':
                        if (e.shiftKey) {
                            e.preventDefault();
                            this.exportAsHTML($element);
                        }
                        break;
                }
            }
        });
    }

    addImageUploadHandler($element, editorId) {
        $element.summernote({
            callbacks: {
                onImageUpload: (files) => {
                    for (let i = 0; i < files.length; i++) {
                        this.uploadImage($element, files[i]);
                    }
                }
            }
        });
    }

    async uploadImage($element, file) {
        try {
            const formData = new FormData();
            formData.append('file', file);

            const response = await fetch('/api/upload/image', {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                const data = await response.json();
                $element.summernote('insertImage', data.location);
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

    saveContent($element) {
        const content = $element.summernote('code');

        fetch('/api/editor/save', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                content: content,
                editorType: 'summernote'
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

    exportAsHTML($element) {
        const content = $element.summernote('code');
        const htmlContent = `
            <!DOCTYPE html>
            <html>
            <head>
                <title>Summernote Export</title>
                <style>
                    body { font-family: 'Inter', sans-serif; padding: 20px; max-width: 800px; margin: 0 auto; }
                    img { max-width: 100%; height: auto; }
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
        a.download = 'summernote-export.html';
        a.click();
        URL.revokeObjectURL(url);

        if (window.showToast) {
            showToast('success', 'Exported as HTML');
        }
    }

    exportAsText($element) {
        const text = $element.summernote('code').replace(/<[^>]*>/g, ' ').replace(/\s+/g, ' ').trim();
        const blob = new Blob([text], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'summernote-export.txt';
        a.click();
        URL.revokeObjectURL(url);

        if (window.showToast) {
            showToast('success', 'Exported as text');
        }
    }

    exportAsPDF($element) {
        const content = $element.summernote('code');
        const htmlContent = `
            <!DOCTYPE html>
            <html>
            <head>
                <title>Summernote Export</title>
                <style>
                    @page { margin: 1in; }
                    body { font-family: 'Inter', sans-serif; font-size: 12pt; line-height: 1.4; }
                    img { max-width: 100%; height: auto; }
                    h1, h2, h3, h4, h5, h6 { page-break-after: avoid; }
                    p { margin-bottom: 0.5em; }
                </style>
            </head>
            <body>
                ${content}
            </body>
            </html>
        `;

        // For PDF export, we'll use a simple approach with print styles
        // In a real application, you might want to use a library like jsPDF
        const printWindow = window.open('', '_blank');
        printWindow.document.write(htmlContent);
        printWindow.document.close();
        printWindow.print();

        if (window.showToast) {
            showToast('success', 'PDF export initiated - use browser print to save as PDF');
        }
    }

    // Utility methods
    generateId() {
        return 'summernote_' + Math.random().toString(36).substr(2, 9);
    }

    destroy(editorId) {
        const editorData = this.editors.get(editorId);
        if (editorData) {
            if (editorData.summernote) {
                editorData.summernote.summernote('destroy');
            }
            this.editors.delete(editorId);
        }
    }

    getEditor(editorId) {
        const editorData = this.editors.get(editorId);
        return editorData ? editorData.summernote : null;
    }

    setContent(editorId, content) {
        const editorData = this.editors.get(editorId);
        if (editorData && editorData.summernote) {
            editorData.summernote.summernote('code', content);
        }
    }

    getContent(editorId) {
        const editorData = this.editors.get(editorId);
        if (editorData && editorData.summernote) {
            return editorData.summernote.summernote('code');
        }
        return '';
    }

    getText(editorId) {
        const editorData = this.editors.get(editorId);
        if (editorData && editorData.summernote) {
            return editorData.summernote.summernote('code').replace(/<[^>]*>/g, ' ').replace(/\s+/g, ' ').trim();
        }
        return '';
    }
}

// Global instance
window.ValidoAISummernote = new ValidoAISummernote();
