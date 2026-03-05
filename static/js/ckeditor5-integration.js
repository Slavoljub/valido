/**
 * CKEditor 5 Integration for ValidoAI
 * Modern, feature-rich WYSIWYG editor with advanced capabilities
 */

class ValidoAICKEditor5 {
    constructor() {
        this.editors = new Map();
        this.ClassicEditor = null;
        this.InlineEditor = null;
        this.BalloonEditor = null;
        this.DocumentEditor = null;
    }

    async init(selector, config = {}) {
        const editorId = this.generateId();
        const mergedConfig = this.mergeConfig(config);

        // Load CKEditor 5 if not already loaded
        if (!window.ClassicEditor) {
            await this.loadCKEditor5();
        }

        try {
            const editor = await this.createEditor(selector, mergedConfig);
            this.editors.set(editorId, {
                editor: editor,
                selector: selector,
                config: mergedConfig
            });

            this.applyThemeIntegration(editorId);
            this.addCustomFeatures(editorId);

            return editorId;
        } catch (error) {
            console.error('CKEditor 5 initialization failed:', error);
            throw error;
        }
    }

    async loadCKEditor5() {
        return new Promise((resolve, reject) => {
            // Load CKEditor 5 from CDN
            const script = document.createElement('script');
            script.src = 'https://cdn.ckeditor.com/ckeditor5/42.0.0/classic/ckeditor.js';
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        });
    }

    mergeConfig(userConfig) {
        const defaultConfig = {
            toolbar: [
                'heading', '|',
                'bold', 'italic', 'underline', 'strikethrough', '|',
                'link', 'bulletedList', 'numberedList', '|',
                'alignment', 'indent', 'outdent', '|',
                'imageUpload', 'blockQuote', 'insertTable', 'mediaEmbed', '|',
                'undo', 'redo', '|',
                'code', 'codeBlock', 'htmlEmbed', '|',
                'fontSize', 'fontFamily', 'fontColor', 'fontBackgroundColor', '|',
                'todoList', 'highlight', 'removeFormat', '|',
                'pageBreak', 'horizontalLine', 'specialCharacters', '|',
                'findAndReplace', 'selectAll', '|',
                'sourceEditing'
            ],
            language: 'en',
            image: {
                toolbar: [
                    'imageTextAlternative',
                    'toggleImageCaption',
                    'imageStyle:inline',
                    'imageStyle:block',
                    'imageStyle:side'
                ]
            },
            table: {
                contentToolbar: [
                    'tableColumn',
                    'tableRow',
                    'mergeTableCells',
                    'tableCellProperties',
                    'tableProperties'
                ]
            },
            mediaEmbed: {
                previewsInData: true
            },
            placeholder: 'Start writing your content here...',
            ckfinder: {
                uploadUrl: '/api/upload/image'
            },
            fontSize: {
                options: [9, 11, 13, 'default', 17, 19, 21]
            },
            fontFamily: {
                options: [
                    'default',
                    'Arial, Helvetica, sans-serif',
                    'Courier New, Courier, monospace',
                    'Georgia, serif',
                    'Lucida Sans Unicode, Lucida Grande, sans-serif',
                    'Tahoma, Geneva, sans-serif',
                    'Times New Roman, Times, serif',
                    'Trebuchet MS, Helvetica, sans-serif',
                    'Verdana, Geneva, sans-serif'
                ]
            },
            heading: {
                options: [
                    { model: 'paragraph', title: 'Paragraph', class: 'ck-heading_paragraph' },
                    { model: 'heading1', view: 'h1', title: 'Heading 1', class: 'ck-heading_heading1' },
                    { model: 'heading2', view: 'h2', title: 'Heading 2', class: 'ck-heading_heading2' },
                    { model: 'heading3', view: 'h3', title: 'Heading 3', class: 'ck-heading_heading3' },
                    { model: 'heading4', view: 'h4', title: 'Heading 4', class: 'ck-heading_heading4' },
                    { model: 'heading5', view: 'h5', title: 'Heading 5', class: 'ck-heading_heading5' },
                    { model: 'heading6', view: 'h6', title: 'Heading 6', class: 'ck-heading_heading6' }
                ]
            },
            htmlEmbed: {
                showPreviews: true
            },
            codeBlock: {
                languages: [
                    { language: 'plaintext', label: 'Plain text' },
                    { language: 'html', label: 'HTML' },
                    { language: 'css', label: 'CSS' },
                    { language: 'javascript', label: 'JavaScript' },
                    { language: 'python', label: 'Python' },
                    { language: 'php', label: 'PHP' },
                    { language: 'sql', label: 'SQL' },
                    { language: 'json', label: 'JSON' },
                    { language: 'xml', label: 'XML' }
                ]
            },
            alignment: {
                options: ['left', 'center', 'right', 'justify']
            },
            indentBlock: {
                offset: 1,
                unit: 'em'
            },
            highlight: {
                options: [
                    {
                        model: 'yellowMarker',
                        class: 'marker-yellow',
                        title: 'Yellow marker',
                        color: 'var(--ck-highlight-marker-yellow)',
                        type: 'marker'
                    },
                    {
                        model: 'greenMarker',
                        class: 'marker-green',
                        title: 'Green marker',
                        color: 'var(--ck-highlight-marker-green)',
                        type: 'marker'
                    },
                    {
                        model: 'pinkMarker',
                        class: 'marker-pink',
                        title: 'Pink marker',
                        color: 'var(--ck-highlight-marker-pink)',
                        type: 'marker'
                    },
                    {
                        model: 'blueMarker',
                        class: 'marker-blue',
                        title: 'Blue marker',
                        color: 'var(--ck-highlight-marker-blue)',
                        type: 'marker'
                    }
                ]
            },
            ...userConfig
        };

        return defaultConfig;
    }

    async createEditor(selector, config) {
        const element = document.querySelector(selector);
        if (!element) {
            throw new Error(`Element with selector '${selector}' not found`);
        }

        // Determine editor type based on config
        let EditorClass = window.ClassicEditor;

        if (config.editorType === 'inline') {
            EditorClass = window.InlineEditor || EditorClass;
        } else if (config.editorType === 'balloon') {
            EditorClass = window.BalloonEditor || EditorClass;
        } else if (config.editorType === 'document') {
            EditorClass = window.DocumentEditor || EditorClass;
        }

        const editor = await EditorClass.create(element, config);

        // Add custom CSS for theme support
        this.addCustomCSS(editor);

        return editor;
    }

    addCustomCSS(editor) {
        const style = document.createElement('style');
        style.textContent = `
            .ck.ck-editor__main .ck-content {
                min-height: 200px;
                padding: 1rem;
                font-family: 'Inter', sans-serif;
                font-size: 14px;
                line-height: 1.6;
            }

            .ck.ck-editor__top .ck-toolbar {
                background: var(--bg-primary, #ffffff);
                border: 1px solid var(--border-primary, #e5e7eb);
                border-bottom: none;
            }

            .ck.ck-toolbar .ck-toolbar__items {
                flex-wrap: wrap;
            }

            .ck.ck-button {
                color: var(--text-primary, #374151);
            }

            .ck.ck-button:hover {
                background: var(--bg-secondary, #f9fafb);
            }

            .ck.ck-button.ck-on {
                background: var(--primary-600, #3b82f6);
                color: white;
            }

            .ck.ck-dropdown__panel {
                background: var(--bg-primary, #ffffff);
                border: 1px solid var(--border-primary, #e5e7eb);
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            }

            .ck.ck-list__item {
                color: var(--text-primary, #374151);
            }

            .ck.ck-list__item:hover {
                background: var(--bg-secondary, #f9fafb);
            }

            /* Dark theme support */
            .ckeditor-dark-theme .ck.ck-editor__main .ck-content {
                background: #1f2937;
                color: #f9fafb;
            }

            .ckeditor-dark-theme .ck.ck-editor__top .ck-toolbar {
                background: #374151;
                border-color: #4b5563;
            }

            .ckeditor-dark-theme .ck.ck-button {
                color: #f9fafb;
            }

            .ckeditor-dark-theme .ck.ck-button:hover {
                background: #4b5563;
            }

            .ckeditor-dark-theme .ck.ck-dropdown__panel {
                background: #374151;
                border-color: #4b5563;
            }

            .ckeditor-dark-theme .ck.ck-list__item {
                color: #f9fafb;
            }

            .ckeditor-dark-theme .ck.ck-list__item:hover {
                background: #4b5563;
            }
        `;
        document.head.appendChild(style);
    }

    applyThemeIntegration(editorId) {
        const editorData = this.editors.get(editorId);
        if (!editorData) return;

        const editor = editorData.editor;

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

        const editor = editorData.editor;
        const editorElement = editor.ui.view.element;

        // Remove existing theme classes
        editorElement.classList.remove('ckeditor-dark-theme');

        // Add theme class for dark themes
        const isDark = ['valido-dark', 'material-dark', 'dracula', 'monokai'].includes(theme);
        if (isDark) {
            editorElement.classList.add('ckeditor-dark-theme');
        }

        // Update editor content styles
        const contentElement = editor.ui.view.editable.element;
        if (isDark) {
            contentElement.style.background = '#1f2937';
            contentElement.style.color = '#f9fafb';
        } else {
            contentElement.style.background = '';
            contentElement.style.color = '';
        }
    }

    addCustomFeatures(editorId) {
        const editorData = this.editors.get(editorId);
        if (!editorData) return;

        const editor = editorData.editor;

        // Add custom plugins
        this.addExportPlugin(editor);
        this.addWordCountPlugin(editor);
        this.addAutoSavePlugin(editor);
        this.addImageUploadHandler(editor);
    }

    addExportPlugin(editor) {
        // Add export functionality
        editor.ui.registry.addButton('exportWord', {
            text: 'Export Word',
            icon: 'new-document',
            onAction: () => this.exportAsWord(editor)
        });

        editor.ui.registry.addButton('exportPDF', {
            text: 'Export PDF',
            icon: 'print',
            onAction: () => this.exportAsPDF(editor)
        });
    }

    addWordCountPlugin(editor) {
        // Add word count display
        const wordCountElement = document.createElement('div');
        wordCountElement.className = 'ck-word-count';
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
            const content = editor.getData();
            const words = content.replace(/<[^>]*>/g, ' ').trim().split(/\s+/).filter(word => word.length > 0).length;
            const chars = content.replace(/<[^>]*>/g, '').length;
            wordCountElement.textContent = `${words} words, ${chars} chars`;
        };

        editor.ui.view.element.appendChild(wordCountElement);
        editor.model.document.on('change:data', updateWordCount);
        updateWordCount();
    }

    addAutoSavePlugin(editor) {
        let saveTimeout;
        editor.model.document.on('change:data', () => {
            clearTimeout(saveTimeout);
            saveTimeout = setTimeout(() => {
                const content = editor.getData();
                const timestamp = new Date().toISOString();

                localStorage.setItem(`ckeditor_autosave_${editor.id}`, JSON.stringify({
                    content: content,
                    timestamp: timestamp
                }));

                if (window.showToast) {
                    showToast('success', 'Content auto-saved', { position: 'top-right', duration: 2000 });
                }
            }, 1000);
        });
    }

    addImageUploadHandler(editor) {
        editor.plugins.get('FileRepository').createUploadAdapter = (loader) => {
            return new CKEditorUploadAdapter(loader);
        };
    }

    exportAsWord(editor) {
        const content = editor.getData();
        const htmlContent = `
            <!DOCTYPE html>
            <html xmlns:o='urn:schemas-microsoft-com:office:office' xmlns:w='urn:schemas-microsoft-com:office:word' xmlns='http://www.w3.org/TR/REC-html40'>
            <head>
                <meta charset='utf-8'>
                <title>Document</title>
                <!--[if gte mso 9]>
                <xml>
                    <w:WordDocument>
                        <w:View>Print</w:View>
                        <w:Zoom>90</w:Zoom>
                    </w:WordDocument>
                </xml>
                <![endif]-->
                <style>
                    body { font-family: 'Inter', sans-serif; }
                    img { max-width: 100%; height: auto; }
                </style>
            </head>
            <body>
                ${content}
            </body>
            </html>
        `;

        const blob = new Blob([htmlContent], { type: 'application/msword' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'ckeditor-document.doc';
        a.click();
        URL.revokeObjectURL(url);

        if (window.showToast) {
            showToast('success', 'Document exported as Word');
        }
    }

    exportAsPDF(editor) {
        const content = editor.getData();
        const printWindow = window.open('', '_blank');

        printWindow.document.write(`
            <!DOCTYPE html>
            <html>
            <head>
                <title>Export to PDF</title>
                <style>
                    body { font-family: 'Inter', sans-serif; padding: 20px; }
                    @media print { body { padding: 0; } }
                    img { max-width: 100%; height: auto; }
                </style>
            </head>
            <body>
                ${content}
                <script>
                    window.onload = function() {
                        window.print();
                        setTimeout(() => window.close(), 1000);
                    };
                </script>
            </body>
            </html>
        `);

        if (window.showToast) {
            showToast('success', 'Document exported as PDF');
        }
    }

    // Utility methods
    generateId() {
        return 'ckeditor_' + Math.random().toString(36).substr(2, 9);
    }

    destroy(editorId) {
        const editorData = this.editors.get(editorId);
        if (editorData) {
            editorData.editor.destroy();
            this.editors.delete(editorId);
        }
    }

    getEditor(editorId) {
        const editorData = this.editors.get(editorId);
        return editorData ? editorData.editor : null;
    }

    setContent(editorId, content) {
        const editorData = this.editors.get(editorId);
        if (editorData) {
            editorData.editor.setData(content);
        }
    }

    getContent(editorId) {
        const editorData = this.editors.get(editorId);
        if (editorData) {
            return editorData.editor.getData();
        }
        return '';
    }
}

// CKEditor Upload Adapter
class CKEditorUploadAdapter {
    constructor(loader) {
        this.loader = loader;
    }

    upload() {
        return this.loader.file
            .then(file => new Promise((resolve, reject) => {
                const formData = new FormData();
                formData.append('file', file);

                fetch('/api/upload/image', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    resolve({ default: data.location });
                })
                .catch(error => {
                    reject(error);
                });
            }));
    }

    abort() {
        // Abort the upload process
    }
}

// Global instance
window.ValidoAICKEditor5 = new ValidoAICKEditor5();
