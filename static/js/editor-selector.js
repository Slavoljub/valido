/**
 * Editor Selector for ValidoAI
 * Unified interface for choosing and switching between different WYSIWYG editors
 */

class ValidoAIEditorSelector {
    constructor() {
        this.editors = {
            'ckeditor5': {
                name: 'CKEditor 5',
                description: 'Modern, feature-rich editor with advanced capabilities',
                class: 'ValidoAICKEditor5',
                icon: '📝',
                features: ['Advanced formatting', 'Image upload', 'Export to Word/PDF', 'Word count', 'Auto-save']
            },
            'tinymce': {
                name: 'TinyMCE',
                description: 'Most trusted WYSIWYG editor with 30+ plugins',
                class: 'ValidoAITinyMCE',
                icon: '⭐',
                features: ['Rich plugins', 'Templates', 'Image management', 'Code editor', 'Voice features']
            },
            'froala': {
                name: 'Froala',
                description: 'Beautiful and intuitive WYSIWYG editor',
                class: 'ValidoAIFroala',
                icon: '✨',
                features: ['Intuitive UI', 'Image editing', 'Tables', 'Lists', 'Quick toolbar']
            },
            'quill': {
                name: 'Quill',
                description: 'Lightweight, flexible editor with clean interface',
                class: 'ValidoAIQuill',
                icon: '🪶',
                features: ['Fast performance', 'Clean design', 'Basic formatting', 'Customizable']
            },
            'summernote': {
                name: 'Summernote',
                description: 'Bootstrap-based editor with intuitive interface',
                class: 'ValidoAISummernote',
                icon: '🌞',
                features: ['Bootstrap integration', 'Simple UI', 'Air mode', 'Fullscreen']
            },
            'trix': {
                name: 'Trix',
                description: 'Modern editor from Basecamp with clean design',
                class: 'ValidoAITrix',
                icon: '🏔️',
                features: ['Clean interface', 'File attachments', 'No dependencies', 'Modern UX']
            }
        };

        this.currentEditor = null;
        this.currentEditorId = null;
        this.container = null;
    }

    async init(containerSelector, defaultEditor = 'tinymce') {
        this.container = document.querySelector(containerSelector);
        if (!this.container) {
            throw new Error(`Container with selector '${containerSelector}' not found`);
        }

        // Create selector UI
        this.createSelectorUI();

        // Set default editor
        if (defaultEditor && this.editors[defaultEditor]) {
            await this.switchEditor(defaultEditor);
        }

        // Add theme integration
        this.applyThemeIntegration();
    }

    createSelectorUI() {
        const selectorHTML = `
            <div class="editor-selector-container">
                <div class="editor-selector-header">
                    <h3 class="editor-selector-title">Choose Your Editor</h3>
                    <div class="editor-selector-controls">
                        <select class="form-control editor-dropdown" id="editor-selector-dropdown">
                            <option value="">Select an editor...</option>
                            ${Object.entries(this.editors).map(([key, editor]) =>
                                `<option value="${key}">${editor.icon} ${editor.name}</option>`
                            ).join('')}
                        </select>
                        <button class="btn btn-outline-primary" id="refresh-editor-btn" title="Refresh current editor">
                            🔄
                        </button>
                    </div>
                </div>

                <div class="editor-info-panel" id="editor-info-panel" style="display: none;">
                    <div class="editor-info-content">
                        <h4 class="editor-info-name" id="editor-info-name"></h4>
                        <p class="editor-info-description" id="editor-info-description"></p>
                        <div class="editor-features" id="editor-features">
                            <strong>Features:</strong>
                            <ul class="editor-features-list" id="editor-features-list"></ul>
                        </div>
                    </div>
                </div>

                <div class="current-editor-status" id="current-editor-status" style="display: none;">
                    <span class="status-indicator"></span>
                    <span class="status-text">Current: <strong id="current-editor-name"></strong></span>
                </div>

                <div class="editor-workspace" id="editor-workspace">
                    <!-- Editor will be loaded here -->
                </div>
            </div>
        `;

        this.container.innerHTML = selectorHTML;

        // Add event listeners
        this.addEventListeners();

        // Add custom CSS
        this.addCustomCSS();
    }

    addEventListeners() {
        const dropdown = document.getElementById('editor-selector-dropdown');
        const refreshBtn = document.getElementById('refresh-editor-btn');

        dropdown.addEventListener('change', async (e) => {
            const editorKey = e.target.value;
            if (editorKey) {
                await this.switchEditor(editorKey);
            }
        });

        refreshBtn.addEventListener('click', async () => {
            if (this.currentEditor) {
                const editorKey = Object.keys(this.editors).find(key =>
                    this.editors[key].class === this.currentEditor.constructor.name
                );
                if (editorKey) {
                    await this.switchEditor(editorKey);
                }
            }
        });
    }

    async switchEditor(editorKey) {
        const editorInfo = this.editors[editorKey];
        if (!editorInfo) return;

        try {
            // Show loading state
            this.showLoadingState();

            // Destroy current editor if exists
            if (this.currentEditor && this.currentEditorId) {
                this.currentEditor.destroy(this.currentEditorId);
            }

            // Get or create editor instance
            const editorClass = window[editorInfo.class];
            if (!editorClass) {
                throw new Error(`Editor class ${editorInfo.class} not found. Make sure the editor script is loaded.`);
            }

            const editorInstance = new editorClass();

            // Generate unique selector for this editor
            const editorSelector = `editor-${editorKey}-${Date.now()}`;

            // Create editor container
            const workspace = document.getElementById('editor-workspace');
            workspace.innerHTML = `
                <textarea id="${editorSelector}" name="content" class="editor-textarea">
                    Welcome to ${editorInfo.name}!

                    This is a sample content to demonstrate the editor's capabilities.
                    You can edit this text, format it, and see how the editor works.

                    Try the different formatting options available in the toolbar above.
                </textarea>
            `;

            // Initialize the editor
            this.currentEditorId = await editorInstance.init(`#${editorSelector}`);
            this.currentEditor = editorInstance;

            // Update UI
            this.updateEditorInfo(editorKey);
            this.updateCurrentStatus(editorKey);
            this.hideLoadingState();

            // Update dropdown
            const dropdown = document.getElementById('editor-selector-dropdown');
            dropdown.value = editorKey;

            if (window.showToast) {
                showToast('success', `Switched to ${editorInfo.name}`, { duration: 2000 });
            }

        } catch (error) {
            console.error('Failed to switch editor:', error);
            this.hideLoadingState();
            if (window.showToast) {
                showToast('error', `Failed to load ${editorInfo.name}: ${error.message}`);
            }
        }
    }

    showLoadingState() {
        const workspace = document.getElementById('editor-workspace');
        workspace.innerHTML = `
            <div class="editor-loading">
                <div class="loading-spinner"></div>
                <p>Loading editor...</p>
            </div>
        `;
    }

    hideLoadingState() {
        // Loading state will be replaced by the editor content
    }

    updateEditorInfo(editorKey) {
        const editorInfo = this.editors[editorKey];
        const infoPanel = document.getElementById('editor-info-panel');
        const infoName = document.getElementById('editor-info-name');
        const infoDescription = document.getElementById('editor-info-description');
        const featuresList = document.getElementById('editor-features-list');

        infoName.textContent = `${editorInfo.icon} ${editorInfo.name}`;
        infoDescription.textContent = editorInfo.description;

        featuresList.innerHTML = editorInfo.features.map(feature =>
            `<li>${feature}</li>`
        ).join('');

        infoPanel.style.display = 'block';
    }

    updateCurrentStatus(editorKey) {
        const editorInfo = this.editors[editorKey];
        const statusElement = document.getElementById('current-editor-status');
        const statusName = document.getElementById('current-editor-name');

        statusName.textContent = `${editorInfo.icon} ${editorInfo.name}`;
        statusElement.style.display = 'flex';
    }

    addCustomCSS() {
        const style = document.createElement('style');
        style.textContent = `
            .editor-selector-container {
                border: 1px solid var(--border-primary, #e5e7eb);
                border-radius: 8px;
                background: var(--bg-primary, #ffffff);
                overflow: hidden;
            }

            .editor-selector-header {
                padding: 1rem;
                border-bottom: 1px solid var(--border-primary, #e5e7eb);
                background: var(--bg-secondary, #f9fafb);
                display: flex;
                justify-content: space-between;
                align-items: center;
                flex-wrap: wrap;
                gap: 1rem;
            }

            .editor-selector-title {
                margin: 0;
                font-size: 1.25rem;
                font-weight: 600;
                color: var(--text-primary, #374151);
            }

            .editor-selector-controls {
                display: flex;
                gap: 0.5rem;
                align-items: center;
            }

            .editor-dropdown {
                min-width: 200px;
                font-size: 14px;
            }

            .editor-info-panel {
                padding: 1rem;
                border-bottom: 1px solid var(--border-primary, #e5e7eb);
                background: var(--bg-primary, #ffffff);
            }

            .editor-info-name {
                margin: 0 0 0.5rem 0;
                font-size: 1.1rem;
                font-weight: 600;
                color: var(--text-primary, #374151);
            }

            .editor-info-description {
                margin: 0 0 1rem 0;
                color: var(--text-secondary, #6b7280);
                font-size: 14px;
            }

            .editor-features {
                font-size: 14px;
                color: var(--text-primary, #374151);
            }

            .editor-features-list {
                margin: 0.5rem 0 0 0;
                padding-left: 1.5rem;
            }

            .editor-features-list li {
                margin-bottom: 0.25rem;
                color: var(--text-secondary, #6b7280);
            }

            .current-editor-status {
                padding: 0.5rem 1rem;
                background: var(--primary-50, #eff6ff);
                border-bottom: 1px solid var(--primary-200, #bfdbfe);
                display: flex;
                align-items: center;
                gap: 0.5rem;
                font-size: 14px;
                color: var(--primary-700, #1d4ed8);
            }

            .status-indicator {
                width: 8px;
                height: 8px;
                background: var(--success-500, #10b981);
                border-radius: 50%;
                animation: pulse 2s infinite;
            }

            .editor-workspace {
                min-height: 400px;
                position: relative;
            }

            .editor-loading {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                min-height: 300px;
                color: var(--text-secondary, #6b7280);
            }

            .loading-spinner {
                width: 40px;
                height: 40px;
                border: 4px solid var(--border-primary, #e5e7eb);
                border-top: 4px solid var(--primary-600, #2563eb);
                border-radius: 50%;
                animation: spin 1s linear infinite;
                margin-bottom: 1rem;
            }

            .editor-textarea {
                width: 100%;
                min-height: 300px;
                border: none;
                padding: 1rem;
                font-family: 'Inter', sans-serif;
                font-size: 14px;
                line-height: 1.6;
                color: var(--text-primary, #374151);
                background: var(--bg-primary, #ffffff);
                resize: vertical;
            }

            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }

            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.5; }
            }

            /* Dark theme support */
            .editor-selector-dark-theme .editor-selector-container {
                background: #1f2937;
                border-color: #4b5563;
            }

            .editor-selector-dark-theme .editor-selector-header {
                background: #374151;
                border-color: #4b5563;
            }

            .editor-selector-dark-theme .editor-selector-title {
                color: #f9fafb;
            }

            .editor-selector-dark-theme .editor-info-panel {
                background: #1f2937;
                border-color: #4b5563;
            }

            .editor-selector-dark-theme .editor-info-name {
                color: #f9fafb;
            }

            .editor-selector-dark-theme .editor-info-description {
                color: #d1d5db;
            }

            .editor-selector-dark-theme .editor-features {
                color: #f9fafb;
            }

            .editor-selector-dark-theme .editor-features-list li {
                color: #d1d5db;
            }

            .editor-selector-dark-theme .current-editor-status {
                background: #1e3a8a;
                border-color: #3b82f6;
                color: #dbeafe;
            }

            .editor-selector-dark-theme .editor-loading {
                color: #d1d5db;
            }

            .editor-selector-dark-theme .editor-textarea {
                background: #1f2937;
                color: #f9fafb;
            }

            .editor-selector-dark-theme .loading-spinner {
                border-color: #4b5563;
                border-top-color: #3b82f6;
            }

            /* Responsive design */
            @media (max-width: 768px) {
                .editor-selector-header {
                    flex-direction: column;
                    align-items: stretch;
                }

                .editor-selector-controls {
                    flex-direction: column;
                    width: 100%;
                }

                .editor-dropdown {
                    width: 100%;
                }

                .editor-workspace {
                    min-height: 300px;
                }
            }
        `;
        document.head.appendChild(style);
    }

    applyThemeIntegration() {
        // Listen for theme changes
        document.addEventListener('themeChanged', (event) => {
            this.updateTheme(event.detail.theme);
        });

        // Initial theme application
        const currentTheme = localStorage.getItem('valido-theme') || 'valido-white';
        this.updateTheme(currentTheme);
    }

    updateTheme(theme) {
        if (!this.container) return;

        // Remove existing theme classes
        this.container.classList.remove('editor-selector-dark-theme');

        // Add theme class for dark themes
        const isDark = ['valido-dark', 'material-dark', 'dracula', 'monokai'].includes(theme);
        if (isDark) {
            this.container.classList.add('editor-selector-dark-theme');
        }
    }

    // Public API methods
    async setEditor(editorKey) {
        if (this.editors[editorKey]) {
            await this.switchEditor(editorKey);
        }
    }

    getCurrentEditor() {
        return {
            editor: this.currentEditor,
            editorId: this.currentEditorId,
            type: this.currentEditor ? this.currentEditor.constructor.name : null
        };
    }

    getContent() {
        if (this.currentEditor && this.currentEditorId) {
            return this.currentEditor.getContent(this.currentEditorId);
        }
        return '';
    }

    setContent(content) {
        if (this.currentEditor && this.currentEditorId) {
            this.currentEditor.setContent(this.currentEditorId, content);
        }
    }

    getText() {
        if (this.currentEditor && this.currentEditorId) {
            return this.currentEditor.getText(this.currentEditorId);
        }
        return '';
    }

    destroy() {
        if (this.currentEditor && this.currentEditorId) {
            this.currentEditor.destroy(this.currentEditorId);
        }
        if (this.container) {
            this.container.innerHTML = '';
        }
    }

    // Utility method to get editor info
    getEditorInfo(editorKey) {
        return this.editors[editorKey] || null;
    }

    // Get all available editors
    getAvailableEditors() {
        return Object.keys(this.editors);
    }

    // Check if an editor is available
    isEditorAvailable(editorKey) {
        return !!this.editors[editorKey] && !!window[this.editors[editorKey].class];
    }
}

// Global instance
window.ValidoAIEditorSelector = new ValidoAIEditorSelector();
