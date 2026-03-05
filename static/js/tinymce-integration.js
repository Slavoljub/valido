/**
 * TinyMCE Integration for ValidoAI
 * Most Trusted and Feature-rich WYSIWYG Rich Text Editor
 */

class ValidoAITinyMCE {
    constructor() {
        this.editors = new Map();
        this.defaultConfig = {
            height: 500,
            menubar: true,
            plugins: [
                'advlist', 'autolink', 'lists', 'link', 'image', 'charmap', 'preview',
                'anchor', 'searchreplace', 'visualblocks', 'code', 'fullscreen',
                'insertdatetime', 'media', 'table', 'help', 'wordcount',
                'emoticons', 'template', 'codesample', 'quickbars', 'directionality',
                'nonbreaking', 'visualchars', 'hr', 'pagebreak', 'autoresize',
                'save', 'contextmenu', 'paste', 'textcolor', 'colorpicker'
            ],
            toolbar: 'undo redo | blocks | ' +
                'bold italic underline strikethrough | forecolor backcolor | ' +
                'alignleft aligncenter alignright alignjustify | ' +
                'bullist numlist outdent indent | removeformat | ' +
                'link image media table | code fullscreen preview save | ' +
                'template codesample emoticons charmap | ' +
                'ltr rtl | visualblocks visualchars nonbreaking pagebreak hr | ' +
                'searchreplace wordcount help',
            toolbar_mode: 'sliding',
            contextmenu: 'link image table configurepermanentpen',
            quickbars_selection_toolbar: 'bold italic underline | quicklink h2 h3 blockquote quickimage quicktable',
            quickbars_insert_toolbar: 'quickimage quicktable media codesample',
            image_advtab: true,
            image_title: true,
            automatic_uploads: true,
            file_picker_types: 'image media',
            images_upload_url: '/api/upload/image',
            images_upload_handler: this.handleImageUpload.bind(this),
            templates: [
                { title: 'Welcome Email', description: 'Professional welcome email template', content: this.getWelcomeEmailTemplate() },
                { title: 'Newsletter', description: 'Newsletter template with sections', content: this.getNewsletterTemplate() },
                { title: 'Report', description: 'Professional report template', content: this.getReportTemplate() }
            ],
            codesample_languages: [
                { text: 'HTML/XML', value: 'markup' },
                { text: 'JavaScript', value: 'javascript' },
                { text: 'CSS', value: 'css' },
                { text: 'PHP', value: 'php' },
                { text: 'Python', value: 'python' },
                { text: 'Java', value: 'java' },
                { text: 'C#', value: 'csharp' },
                { text: 'SQL', value: 'sql' },
                { text: 'JSON', value: 'json' }
            ],
            content_css: [
                '//fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap'
            ],
            content_style: `
                body {
                    font-family: 'Inter', sans-serif;
                    font-size: 14px;
                    line-height: 1.6;
                    color: #374151;
                }
                .mce-content-body[data-mce-placeholder]:not(.mce-visualblocks)::before {
                    color: #9ca3af;
                    font-style: italic;
                }
            `,
            placeholder: 'Start writing your content here...',
            branding: false,
            promotion: false,
            paste_data_images: true,
            paste_as_text: false,
            paste_auto_cleanup_on_paste: true,
            paste_remove_styles: false,
            paste_remove_styles_if_webkit: false,
            paste_merge_formats: true,
            smart_paste: true,
            valid_elements: '*[*]',
            extended_valid_elements: '*[*]',
            valid_children: '+body[style]',
            setup: this.setupEditor.bind(this)
        };
    }

    async init(selector, options = {}) {
        const editorId = this.generateId();
        const config = this.mergeConfig(options);

        // Wait for TinyMCE to be loaded
        if (!window.tinymce) {
            await this.loadTinyMCE();
        }

        return new Promise((resolve, reject) => {
            tinymce.init({
                selector: selector,
                ...config,
                init_instance_callback: (editor) => {
                    this.editors.set(editorId, {
                        editor: editor,
                        selector: selector,
                        config: config
                    });

                    this.applyThemeIntegration(editorId);
                    this.addCustomFeatures(editorId);

                    resolve(editorId);
                },
                setup: (editor) => {
                    // Call original setup
                    if (config.setup) {
                        config.setup(editor);
                    }

                    // Add our custom setup
                    this.setupEditor(editor);
                }
            }).catch(reject);
        });
    }

    async loadTinyMCE() {
        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = 'https://cdn.tiny.cloud/1/no-api-key/tinymce/6/tinymce.min.js';
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        });
    }

    mergeConfig(options) {
        return {
            ...this.defaultConfig,
            ...options
        };
    }

    setupEditor(editor) {
        // Auto-save functionality
        let saveTimeout;
        editor.on('change', () => {
            clearTimeout(saveTimeout);
            saveTimeout = setTimeout(() => {
                this.autoSave(editor);
            }, 1000);
        });

        // Theme change handling
        document.addEventListener('themeChanged', () => {
            setTimeout(() => {
                this.updateEditorTheme(editor);
            }, 100);
        });

        // Custom shortcuts
        editor.addShortcut('ctrl+s', 'Save content', () => {
            this.saveContent(editor);
        });

        editor.addShortcut('ctrl+shift+preview', 'Toggle preview', () => {
            this.togglePreview(editor);
        });

        // Add custom menu items
        editor.ui.registry.addMenuItem('exportpdf', {
            text: 'Export as PDF',
            icon: 'print',
            onAction: () => this.exportAsPDF(editor)
        });

        editor.ui.registry.addMenuItem('wordcount', {
            text: 'Word Count',
            icon: 'character-count',
            onAction: () => this.showWordCount(editor)
        });

        // Add custom toolbar buttons
        editor.ui.registry.addButton('savecontent', {
            text: 'Save',
            icon: 'save',
            onAction: () => this.saveContent(editor)
        });

        editor.ui.registry.addButton('exportword', {
            text: 'Export Word',
            icon: 'new-document',
            onAction: () => this.exportAsWord(editor)
        });

        // Add custom formats
        editor.formatter.register('customformats', {
            inline: 'span',
            styles: { color: '#e53e3e' },
            classes: 'text-red-600'
        });

        // Custom paste handling
        editor.on('paste', (e) => {
            this.handlePaste(editor, e);
        });

        // Custom drop handling for files
        editor.on('drop', (e) => {
            this.handleFileDrop(editor, e);
        });

        // Add spellcheck integration
        if ('webkitSpeechRecognition' in window || 'speechSynthesis' in window) {
            this.addVoiceFeatures(editor);
        }
    }

    async handleImageUpload(blobInfo, success, failure) {
        try {
            const formData = new FormData();
            formData.append('file', blobInfo.blob(), blobInfo.filename());

            const response = await fetch('/api/upload/image', {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                const data = await response.json();
                success(data.location);
            } else {
                failure('Image upload failed');
            }
        } catch (error) {
            failure('Image upload error: ' + error.message);
        }
    }

    autoSave(editor) {
        const content = editor.getContent();
        const timestamp = new Date().toISOString();

        // Store in localStorage with timestamp
        localStorage.setItem(`tinymce_autosave_${editor.id}`, JSON.stringify({
            content: content,
            timestamp: timestamp
        }));

        // Visual feedback
        if (window.showToast) {
            showToast('success', 'Content auto-saved', { position: 'top-right', duration: 2000 });
        }
    }

    saveContent(editor) {
        const content = editor.getContent();

        // Save to server
        fetch('/api/editor/save', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                content: content,
                editorId: editor.id
            })
        }).then(response => {
            if (response.ok) {
                if (window.showToast) {
                    showToast('success', 'Content saved successfully', { position: 'top-right' });
                }
            }
        }).catch(error => {
            if (window.showToast) {
                showToast('error', 'Save failed: ' + error.message, { position: 'top-right' });
            }
        });
    }

    togglePreview(editor) {
        const content = editor.getContent();
        const previewWindow = window.open('', '_blank');

        previewWindow.document.write(`
            <!DOCTYPE html>
            <html>
            <head>
                <title>Content Preview</title>
                <style>
                    body { font-family: 'Inter', sans-serif; padding: 20px; max-width: 800px; margin: 0 auto; }
                    img { max-width: 100%; height: auto; }
                </style>
            </head>
            <body>
                ${content}
            </body>
            </html>
        `);
    }

    exportAsPDF(editor) {
        const content = editor.getContent();
        const printWindow = window.open('', '_blank');

        printWindow.document.write(`
            <!DOCTYPE html>
            <html>
            <head>
                <title>Export to PDF</title>
                <style>
                    body { font-family: 'Inter', sans-serif; padding: 20px; }
                    @media print { body { padding: 0; } }
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
    }

    exportAsWord(editor) {
        const content = editor.getContent();
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
                </style>
            </head>
            <body>
                ${content}
            </body>
            </html>
        `;

        const blob = new Blob([htmlContent], { type: 'application/msword' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'document.doc';
        a.click();
        window.URL.revokeObjectURL(url);
    }

    showWordCount(editor) {
        const content = editor.getContent({ format: 'text' });
        const words = content.trim().split(/\s+/).length;
        const chars = content.length;

        if (window.showGlobalModal) {
            showGlobalModal({
                title: 'Word Count',
                content: `
                    <div class="text-center">
                        <div class="text-4xl font-bold text-primary-600 mb-2">${words.toLocaleString()}</div>
                        <div class="text-lg text-neutral-600 mb-4">Words</div>
                        <div class="text-2xl font-semibold text-neutral-700 mb-2">${chars.toLocaleString()}</div>
                        <div class="text-sm text-neutral-500">Characters</div>
                    </div>
                `,
                size: 'max-w-sm'
            });
        }
    }

    handlePaste(editor, e) {
        // Custom paste handling for better formatting
        const clipboardData = e.clipboardData || window.clipboardData;
        if (clipboardData) {
            const pastedData = clipboardData.getData('Text');

            // If pasting URL, convert to link
            if (this.isValidUrl(pastedData)) {
                e.preventDefault();
                editor.insertContent(`<a href="${pastedData}" target="_blank">${pastedData}</a>`);
            }
        }
    }

    handleFileDrop(editor, e) {
        e.preventDefault();

        const files = e.dataTransfer.files;
        for (let file of files) {
            if (file.type.startsWith('image/')) {
                this.uploadDroppedImage(editor, file);
            }
        }
    }

    async uploadDroppedImage(editor, file) {
        try {
            const formData = new FormData();
            formData.append('file', file);

            const response = await fetch('/api/upload/image', {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                const data = await response.json();
                editor.insertContent(`<img src="${data.location}" alt="${file.name}" />`);
            }
        } catch (error) {
            console.error('Image upload failed:', error);
        }
    }

    addVoiceFeatures(editor) {
        // Add voice typing button
        editor.ui.registry.addButton('voicetype', {
            text: 'Voice',
            icon: 'microphone',
            onAction: () => this.startVoiceTyping(editor)
        });

        // Add text-to-speech button
        editor.ui.registry.addButton('texttospeech', {
            text: 'Speak',
            icon: 'volume-up',
            onAction: () => this.textToSpeech(editor)
        });
    }

    startVoiceTyping(editor) {
        if (!('webkitSpeechRecognition' in window)) {
            alert('Voice typing is not supported in your browser');
            return;
        }

        const recognition = new webkitSpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            editor.insertContent(transcript + ' ');
        };

        recognition.start();
    }

    textToSpeech(editor) {
        const content = editor.getContent({ format: 'text' });
        if ('speechSynthesis' in window) {
            const utterance = new SpeechSynthesisUtterance(content);
            window.speechSynthesis.speak(utterance);
        }
    }

    isValidUrl(string) {
        try {
            new URL(string);
            return true;
        } catch (_) {
            return false;
        }
    }

    applyThemeIntegration(editorId) {
        const editorData = this.editors.get(editorId);
        if (!editorData) return;

        const editor = editorData.editor;

        // Initial theme application
        const currentTheme = localStorage.getItem('valido-theme') || 'valido-white';
        this.updateEditorTheme(editor, currentTheme);
    }

    updateEditorTheme(editor, theme) {
        const isDark = ['valido-dark', 'material-dark', 'dracula', 'monokai'].includes(theme);

        // Update editor body styles
        const body = editor.getBody();
        if (body) {
            body.style.backgroundColor = isDark ? '#1f2937' : '#ffffff';
            body.style.color = isDark ? '#f9fafb' : '#374151';
        }

        // Update toolbar theme
        const container = editor.getContainer();
        container.classList.toggle('tinymce-dark-theme', isDark);
    }

    addCustomFeatures(editorId) {
        const editorData = this.editors.get(editorId);
        if (!editorData) return;

        const editor = editorData.editor;

        // Add custom plugins
        this.addMentionsPlugin(editor);
        this.addEmojiPlugin(editor);
        this.addTableToolsPlugin(editor);
        this.addCodeEditorPlugin(editor);
    }

    addMentionsPlugin(editor) {
        // Custom mentions functionality
        editor.on('keydown', (e) => {
            if (e.key === '@') {
                this.showMentionsDropdown(editor);
            }
        });
    }

    addEmojiPlugin(editor) {
        const emojis = ['😀', '👍', '🎉', '🔥', '❤️', '💯', '🚀', '⭐', '✨', '💪'];

        editor.ui.registry.addMenuButton('emoji', {
            text: 'Emoji',
            fetch: (callback) => {
                const items = emojis.map(emoji => ({
                    type: 'menuitem',
                    text: emoji,
                    onAction: () => editor.insertContent(emoji)
                }));
                callback(items);
            }
        });
    }

    addTableToolsPlugin(editor) {
        editor.ui.registry.addMenuItem('tabletools', {
            text: 'Table Tools',
            getSubmenuItems: () => [
                {
                    type: 'menuitem',
                    text: 'Import CSV',
                    onAction: () => this.importTableFromCSV(editor)
                },
                {
                    type: 'menuitem',
                    text: 'Export as CSV',
                    onAction: () => this.exportTableAsCSV(editor)
                },
                {
                    type: 'menuitem',
                    text: 'Sort Table',
                    onAction: () => this.sortTable(editor)
                }
            ]
        });
    }

    addCodeEditorPlugin(editor) {
        editor.ui.registry.addButton('codeeditor', {
            text: 'Code Editor',
            icon: 'code',
            onAction: () => this.openCodeEditor(editor)
        });
    }

    openCodeEditor(editor) {
        const content = editor.getContent();
        const codeEditorWindow = window.open('', '_blank', 'width=800,height=600');

        codeEditorWindow.document.write(`
            <!DOCTYPE html>
            <html>
            <head>
                <title>Code Editor</title>
                <style>
                    body { margin: 0; padding: 20px; }
                    textarea { width: 100%; height: calc(100vh - 100px); font-family: 'Courier New', monospace; }
                    .toolbar { margin-bottom: 10px; }
                </style>
            </head>
            <body>
                <div class="toolbar">
                    <button onclick="saveAndClose()">Save & Close</button>
                    <button onclick="closeWindow()">Cancel</button>
                </div>
                <textarea id="codeEditor">${content.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</textarea>
                <script>
                    function saveAndClose() {
                        const content = document.getElementById('codeEditor').value;
                        window.opener.postMessage({ type: 'code-editor-save', content: content }, '*');
                        window.close();
                    }
                    function closeWindow() {
                        window.close();
                    }
                </script>
            </body>
            </html>
        `);

        window.addEventListener('message', (event) => {
            if (event.data.type === 'code-editor-save') {
                editor.setContent(event.data.content);
            }
        });
    }

    showMentionsDropdown(editor) {
        // Simple mentions implementation
        const mentions = ['@john', '@sarah', '@mike', '@anna'];
        let dropdown = editor.getContainer().querySelector('.mentions-dropdown');

        if (!dropdown) {
            dropdown = document.createElement('div');
            dropdown.className = 'mentions-dropdown';
            dropdown.style.cssText = `
                position: absolute; background: white; border: 1px solid #ddd;
                border-radius: 4px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                z-index: 9999; max-height: 200px; overflow-y: auto;
            `;

            mentions.forEach(mention => {
                const item = document.createElement('div');
                item.textContent = mention;
                item.style.cssText = 'padding: 8px; cursor: pointer; border-bottom: 1px solid #eee;';
                item.onmouseover = () => item.style.background = '#f5f5f5';
                item.onmouseout = () => item.style.background = 'white';
                item.onclick = () => {
                    editor.insertContent(mention + ' ');
                    dropdown.remove();
                };
                dropdown.appendChild(item);
            });

            editor.getContainer().appendChild(dropdown);
        }

        // Position dropdown
        const selection = editor.selection.getRng();
        const rect = selection.getBoundingClientRect();
        dropdown.style.left = rect.left + 'px';
        dropdown.style.top = (rect.bottom + 5) + 'px';

        // Remove dropdown on click outside
        setTimeout(() => {
            document.addEventListener('click', function removeDropdown(e) {
                if (!dropdown.contains(e.target)) {
                    dropdown.remove();
                    document.removeEventListener('click', removeDropdown);
                }
            });
        }, 100);
    }

    importTableFromCSV(editor) {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.csv';
        input.onchange = (e) => {
            const file = e.target.files[0];
            const reader = new FileReader();
            reader.onload = (event) => {
                const csv = event.target.result;
                const rows = csv.split('\n');
                let tableHtml = '<table border="1"><tbody>';

                rows.forEach((row, index) => {
                    if (index === 0) {
                        tableHtml += '<thead><tr>';
                        row.split(',').forEach(cell => {
                            tableHtml += `<th>${cell.trim()}</th>`;
                        });
                        tableHtml += '</tr></thead><tbody>';
                    } else {
                        tableHtml += '<tr>';
                        row.split(',').forEach(cell => {
                            tableHtml += `<td>${cell.trim()}</td>`;
                        });
                        tableHtml += '</tr>';
                    }
                });

                tableHtml += '</tbody></table>';
                editor.insertContent(tableHtml);
            };
            reader.readAsText(file);
        };
        input.click();
    }

    exportTableAsCSV(editor) {
        const tables = editor.dom.select('table');
        if (tables.length === 0) {
            alert('No tables found in the content');
            return;
        }

        const table = tables[0];
        let csv = '';

        // Get headers
        const headers = table.querySelectorAll('thead th, thead td');
        if (headers.length > 0) {
            csv += Array.from(headers).map(h => h.textContent.trim()).join(',') + '\n';
        }

        // Get rows
        const rows = table.querySelectorAll('tbody tr');
        rows.forEach(row => {
            const cells = row.querySelectorAll('td, th');
            csv += Array.from(cells).map(cell => cell.textContent.trim()).join(',') + '\n';
        });

        // Download CSV
        const blob = new Blob([csv], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'table-export.csv';
        a.click();
        window.URL.revokeObjectURL(url);
    }

    sortTable(editor) {
        const tables = editor.dom.select('table');
        if (tables.length === 0) {
            alert('No tables found to sort');
            return;
        }

        if (window.showGlobalModal) {
            showGlobalModal({
                title: 'Sort Table',
                content: `
                    <div class="mb-4">
                        <label class="block text-sm font-medium mb-2">Sort by Column:</label>
                        <select class="form-control" id="sortColumn">
                            <option value="0">Column 1</option>
                            <option value="1">Column 2</option>
                            <option value="2">Column 3</option>
                        </select>
                    </div>
                    <div class="mb-4">
                        <label class="block text-sm font-medium mb-2">Sort Order:</label>
                        <select class="form-control" id="sortOrder">
                            <option value="asc">Ascending</option>
                            <option value="desc">Descending</option>
                        </select>
                    </div>
                `,
                actions: true,
                actionText: 'Sort',
                onAction: () => {
                    const column = document.getElementById('sortColumn').value;
                    const order = document.getElementById('sortOrder').value;
                    this.performTableSort(editor, column, order);
                }
            });
        }
    }

    performTableSort(editor, columnIndex, order) {
        const tables = editor.dom.select('table');
        if (tables.length === 0) return;

        const table = tables[0];
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));

        rows.sort((a, b) => {
            const aText = a.querySelectorAll('td, th')[columnIndex]?.textContent.trim() || '';
            const bText = b.querySelectorAll('td, th')[columnIndex]?.textContent.trim() || '';

            if (order === 'asc') {
                return aText.localeCompare(bText);
            } else {
                return bText.localeCompare(aText);
            }
        });

        // Rebuild tbody
        tbody.innerHTML = '';
        rows.forEach(row => tbody.appendChild(row));

        editor.setDirty(true);
    }

    // Template methods
    getWelcomeEmailTemplate() {
        return `
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px 20px; text-align: center; border-radius: 10px 10px 0 0;">
                    <h1 style="margin: 0; font-size: 28px;">Welcome to ValidoAI!</h1>
                    <p style="margin: 10px 0 0 0; opacity: 0.9;">Your account has been successfully created</p>
                </div>
                <div style="background: white; padding: 30px; border-radius: 0 0 10px 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <p>Hi <strong>[First Name]</strong>,</p>
                    <p>Welcome to ValidoAI! We're excited to have you join our community of financial professionals.</p>

                    <div style="background: #f8fafc; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <h3 style="margin: 0 0 15px 0; color: #374151;">What's next?</h3>
                        <ul style="color: #6b7280; padding-left: 20px;">
                            <li>✅ Complete your profile setup</li>
                            <li>✅ Explore our AI financial tools</li>
                            <li>✅ Connect your financial accounts</li>
                            <li>✅ Set up your first dashboard</li>
                        </ul>
                    </div>

                    <div style="text-align: center; margin: 30px 0;">
                        <a href="#" style="background: #3b82f6; color: white; padding: 12px 30px; text-decoration: none; border-radius: 6px; font-weight: 500;">Get Started</a>
                        <a href="#" style="background: #f1f5f9; color: #374151; padding: 12px 30px; text-decoration: none; border-radius: 6px; font-weight: 500; margin-left: 10px;">View Dashboard</a>
                    </div>
                </div>
            </div>
        `;
    }

    getNewsletterTemplate() {
        return `
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background: linear-gradient(135deg, #8b5cf6 0%, #06b6d4 100%); color: white; padding: 40px 20px; text-align: center; border-radius: 10px 10px 0 0;">
                    <h1 style="margin: 0; font-size: 32px;">ValidoAI Newsletter</h1>
                    <p style="margin: 10px 0 0 0; opacity: 0.9;">Your weekly financial insights</p>
                </div>
                <div style="background: white; padding: 30px; border-radius: 0 0 10px 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <p>Hello <strong>[Subscriber Name]</strong>,</p>
                    <p>Here are the latest updates from ValidoAI this week:</p>

                    <div style="margin: 30px 0;">
                        <div style="background: #f0f9ff; padding: 20px; border-radius: 8px; margin: 15px 0;">
                            <h3 style="margin: 0 0 10px 0; color: #0369a1;">📊 New AI Analytics Features</h3>
                            <p style="color: #075985;">We've added advanced predictive analytics to help forecast trends.</p>
                        </div>

                        <div style="background: #f0fdf4; padding: 20px; border-radius: 8px; margin: 15px 0;">
                            <h3 style="margin: 0 0 10px 0; color: #166534;">💡 Financial Tips</h3>
                            <p style="color: #14532d;">Learn how to optimize your cash flow management.</p>
                        </div>

                        <div style="background: #fef3f2; padding: 20px; border-radius: 8px; margin: 15px 0;">
                            <h3 style="margin: 0 0 10px 0; color: #991b1b;">👥 Community Spotlight</h3>
                            <p style="color: #7f1d1d;">Meet successful users who've transformed their businesses.</p>
                        </div>
                    </div>

                    <div style="text-align: center; margin: 30px 0;">
                        <a href="#" style="background: #3b82f6; color: white; padding: 10px 20px; text-decoration: none; border-radius: 6px; margin: 0 5px;">View Analytics</a>
                        <a href="#" style="background: #10b981; color: white; padding: 10px 20px; text-decoration: none; border-radius: 6px; margin: 0 5px;">Read Tips</a>
                        <a href="#" style="background: #8b5cf6; color: white; padding: 10px 20px; text-decoration: none; border-radius: 6px; margin: 0 5px;">Join Community</a>
                    </div>
                </div>
            </div>
        `;
    }

    getReportTemplate() {
        return `
            <div style="font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px;">
                <header style="border-bottom: 2px solid #e5e7eb; padding-bottom: 20px; margin-bottom: 30px;">
                    <h1 style="margin: 0; color: #111827; font-size: 36px;">Financial Report</h1>
                    <p style="margin: 10px 0 0 0; color: #6b7280; font-size: 16px;">Generated on ${new Date().toLocaleDateString()}</p>
                </header>

                <section style="margin-bottom: 40px;">
                    <h2 style="color: #374151; font-size: 24px; margin-bottom: 20px;">Executive Summary</h2>
                    <p style="color: #4b5563; line-height: 1.6; font-size: 16px;">This report provides a comprehensive analysis of your financial performance over the past quarter.</p>
                </section>

                <section style="margin-bottom: 40px;">
                    <h2 style="color: #374151; font-size: 24px; margin-bottom: 20px;">Key Metrics</h2>
                    <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                        <thead>
                            <tr style="background: #f9fafb;">
                                <th style="border: 1px solid #d1d5db; padding: 12px; text-align: left; font-weight: 600; color: #374151;">Metric</th>
                                <th style="border: 1px solid #d1d5db; padding: 12px; text-align: left; font-weight: 600; color: #374151;">Value</th>
                                <th style="border: 1px solid #d1d5db; padding: 12px; text-align: left; font-weight: 600; color: #374151;">Change</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td style="border: 1px solid #d1d5db; padding: 12px; color: #4b5563;">Revenue</td>
                                <td style="border: 1px solid #d1d5db; padding: 12px; color: #4b5563;">$1,234,567</td>
                                <td style="border: 1px solid #d1d5db; padding: 12px; color: #059669;">+12.5%</td>
                            </tr>
                            <tr>
                                <td style="border: 1px solid #d1d5db; padding: 12px; color: #4b5563;">Expenses</td>
                                <td style="border: 1px solid #d1d5db; padding: 12px; color: #4b5563;">$987,654</td>
                                <td style="border: 1px solid #d1d5db; padding: 12px; color: #dc2626;">+8.2%</td>
                            </tr>
                            <tr>
                                <td style="border: 1px solid #d1d5db; padding: 12px; color: #4b5563;">Profit Margin</td>
                                <td style="border: 1px solid #d1d5db; padding: 12px; color: #4b5563;">23.4%</td>
                                <td style="border: 1px solid #d1d5db; padding: 12px; color: #059669;">+2.1%</td>
                            </tr>
                        </tbody>
                    </table>
                </section>

                <section style="margin-bottom: 40px;">
                    <h2 style="color: #374151; font-size: 24px; margin-bottom: 20px;">Recommendations</h2>
                    <ul style="color: #4b5563; line-height: 1.6; font-size: 16px;">
                        <li>Consider optimizing operational expenses in Q4</li>
                        <li>Invest in marketing campaigns to boost revenue</li>
                        <li>Review pricing strategy for key products</li>
                        <li>Explore new market opportunities</li>
                    </ul>
                </section>

                <footer style="border-top: 1px solid #e5e7eb; padding-top: 20px; margin-top: 40px; color: #6b7280; font-size: 14px;">
                    <p>Generated by ValidoAI Financial Analysis System</p>
                    <p>For questions or concerns, please contact support@valido.online</p>
                </footer>
            </div>
        `;
    }

    generateId() {
        return 'tinymce_' + Math.random().toString(36).substr(2, 9);
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
            editorData.editor.setContent(content);
        }
    }

    getContent(editorId) {
        const editorData = this.editors.get(editorId);
        if (editorData) {
            return editorData.editor.getContent();
        }
        return '';
    }
}

// Global instance
window.ValidoAITinyMCE = new ValidoAITinyMCE();
