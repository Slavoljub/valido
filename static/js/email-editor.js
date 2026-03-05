/**
 * Enhanced WYSIWYG Email Editor
 * Features: Rich text editing, template insertion, image upload, color picker
 */

class EmailEditor {
    constructor(elementId, options = {}) {
        this.elementId = elementId;
        this.editor = document.getElementById(elementId);
        this.options = {
            height: options.height || 400,
            placeholder: options.placeholder || 'Start writing your email...',
            templates: options.templates || [],
            ...options
        };
        
        this.init();
    }
    
    init() {
        if (!this.editor) {
            console.error(`Editor element with ID '${this.elementId}' not found`);
            return;
        }
        
        this.createToolbar();
        this.setupEditor();
        this.bindEvents();
        this.loadTemplates();
    }
    
    createToolbar() {
        const toolbar = document.createElement('div');
        toolbar.className = 'email-editor-toolbar';
        toolbar.innerHTML = `
            <div class="toolbar-group">
                <button type="button" class="toolbar-btn" data-command="bold" title="Bold (Ctrl+B)">
                    <i class="bi bi-type-bold"></i>
                </button>
                <button type="button" class="toolbar-btn" data-command="italic" title="Italic (Ctrl+I)">
                    <i class="bi bi-type-italic"></i>
                </button>
                <button type="button" class="toolbar-btn" data-command="underline" title="Underline (Ctrl+U)">
                    <i class="bi bi-type-underline"></i>
                </button>
                <button type="button" class="toolbar-btn" data-command="strikeThrough" title="Strikethrough">
                    <i class="bi bi-type-strikethrough"></i>
                </button>
            </div>
            
            <div class="toolbar-group">
                <button type="button" class="toolbar-btn" data-command="justifyLeft" title="Align Left">
                    <i class="bi bi-text-left"></i>
                </button>
                <button type="button" class="toolbar-btn" data-command="justifyCenter" title="Align Center">
                    <i class="bi bi-text-center"></i>
                </button>
                <button type="button" class="toolbar-btn" data-command="justifyRight" title="Align Right">
                    <i class="bi bi-text-right"></i>
                </button>
                <button type="button" class="toolbar-btn" data-command="justifyFull" title="Justify">
                    <i class="bi bi-text-paragraph"></i>
                </button>
            </div>
            
            <div class="toolbar-group">
                <button type="button" class="toolbar-btn" data-command="insertUnorderedList" title="Bullet List">
                    <i class="bi bi-list-ul"></i>
                </button>
                <button type="button" class="toolbar-btn" data-command="insertOrderedList" title="Numbered List">
                    <i class="bi bi-list-ol"></i>
                </button>
                <button type="button" class="toolbar-btn" data-command="outdent" title="Decrease Indent">
                    <i class="bi bi-indent"></i>
                </button>
                <button type="button" class="toolbar-btn" data-command="indent" title="Increase Indent">
                    <i class="bi bi-indent"></i>
                </button>
            </div>
            
            <div class="toolbar-group">
                <button type="button" class="toolbar-btn" data-command="createLink" title="Insert Link">
                    <i class="bi bi-link-45deg"></i>
                </button>
                <button type="button" class="toolbar-btn" data-command="insertImage" title="Insert Image">
                    <i class="bi bi-image"></i>
                </button>
                <button type="button" class="toolbar-btn" data-command="insertTable" title="Insert Table">
                    <i class="bi bi-table"></i>
                </button>
                <button type="button" class="toolbar-btn" data-command="insertHorizontalRule" title="Insert Line">
                    <i class="bi bi-dash-lg"></i>
                </button>
            </div>
            
            <div class="toolbar-group">
                <select class="toolbar-select" data-command="formatBlock">
                    <option value="p">Paragraph</option>
                    <option value="h1">Heading 1</option>
                    <option value="h2">Heading 2</option>
                    <option value="h3">Heading 3</option>
                    <option value="h4">Heading 4</option>
                    <option value="h5">Heading 5</option>
                    <option value="h6">Heading 6</option>
                </select>
                
                <select class="toolbar-select" data-command="fontSize">
                    <option value="1">Very Small</option>
                    <option value="2">Small</option>
                    <option value="3" selected>Normal</option>
                    <option value="4">Large</option>
                    <option value="5">Very Large</option>
                    <option value="6">Extra Large</option>
                    <option value="7">Maximum</option>
                </select>
                
                <input type="color" class="toolbar-color" data-command="foreColor" title="Text Color">
                <input type="color" class="toolbar-color" data-command="hiliteColor" title="Background Color">
            </div>
            
            <div class="toolbar-group">
                <button type="button" class="toolbar-btn" data-command="undo" title="Undo (Ctrl+Z)">
                    <i class="bi bi-arrow-counterclockwise"></i>
                </button>
                <button type="button" class="toolbar-btn" data-command="redo" title="Redo (Ctrl+Y)">
                    <i class="bi bi-arrow-clockwise"></i>
                </button>
                <button type="button" class="toolbar-btn" data-command="removeFormat" title="Clear Formatting">
                    <i class="bi bi-eraser"></i>
                </button>
            </div>
            
            <div class="toolbar-group">
                <button type="button" class="toolbar-btn template-btn" title="Insert Template">
                    <i class="bi bi-file-earmark-text"></i>
                </button>
                <button type="button" class="toolbar-btn emoji-btn" title="Insert Emoji">
                    😊
                </button>
            </div>
        `;
        
        this.editor.parentNode.insertBefore(toolbar, this.editor);
        this.toolbar = toolbar;
    }
    
    setupEditor() {
        this.editor.contentEditable = true;
        this.editor.className = 'email-editor-content';
        this.editor.style.minHeight = `${this.options.height}px`;
        this.editor.setAttribute('data-placeholder', this.options.placeholder);
        
        // Add CSS for placeholder
        if (!document.getElementById('email-editor-styles')) {
            const style = document.createElement('style');
            style.id = 'email-editor-styles';
            style.textContent = `
                .email-editor-toolbar {
                    background: #f8f9fa;
                    border: 1px solid #dee2e6;
                    border-bottom: none;
                    padding: 8px;
                    display: flex;
                    flex-wrap: wrap;
                    gap: 4px;
                    border-radius: 6px 6px 0 0;
                }
                
                .toolbar-group {
                    display: flex;
                    gap: 2px;
                    align-items: center;
                    padding: 0 4px;
                    border-right: 1px solid #dee2e6;
                }
                
                .toolbar-group:last-child {
                    border-right: none;
                }
                
                .toolbar-btn {
                    background: white;
                    border: 1px solid #dee2e6;
                    border-radius: 4px;
                    padding: 6px 8px;
                    cursor: pointer;
                    transition: all 0.2s;
                    font-size: 14px;
                }
                
                .toolbar-btn:hover {
                    background: #e9ecef;
                    border-color: #adb5bd;
                }
                
                .toolbar-btn.active {
                    background: #007bff;
                    color: white;
                    border-color: #007bff;
                }
                
                .toolbar-select {
                    background: white;
                    border: 1px solid #dee2e6;
                    border-radius: 4px;
                    padding: 4px 8px;
                    font-size: 12px;
                }
                
                .toolbar-color {
                    width: 30px;
                    height: 30px;
                    border: 1px solid #dee2e6;
                    border-radius: 4px;
                    cursor: pointer;
                }
                
                .email-editor-content {
                    border: 1px solid #dee2e6;
                    border-radius: 0 0 6px 6px;
                    padding: 16px;
                    outline: none;
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                }
                
                .email-editor-content:empty:before {
                    content: attr(data-placeholder);
                    color: #6c757d;
                    font-style: italic;
                }
                
                .email-editor-content:focus {
                    border-color: #007bff;
                    box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
                }
                
                .template-dropdown {
                    position: absolute;
                    background: white;
                    border: 1px solid #dee2e6;
                    border-radius: 4px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    z-index: 1000;
                    max-height: 200px;
                    overflow-y: auto;
                }
                
                .template-item {
                    padding: 8px 12px;
                    cursor: pointer;
                    border-bottom: 1px solid #f8f9fa;
                }
                
                .template-item:hover {
                    background: #f8f9fa;
                }
                
                .emoji-picker {
                    position: absolute;
                    background: white;
                    border: 1px solid #dee2e6;
                    border-radius: 4px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    z-index: 1000;
                    padding: 8px;
                    display: grid;
                    grid-template-columns: repeat(8, 1fr);
                    gap: 4px;
                }
                
                .emoji-item {
                    cursor: pointer;
                    padding: 4px;
                    border-radius: 2px;
                    text-align: center;
                    font-size: 16px;
                }
                
                .emoji-item:hover {
                    background: #f8f9fa;
                }
            `;
            document.head.appendChild(style);
        }
    }
    
    bindEvents() {
        // Toolbar button events
        this.toolbar.addEventListener('click', (e) => {
            const button = e.target.closest('.toolbar-btn');
            if (button) {
                e.preventDefault();
                const command = button.dataset.command;
                this.executeCommand(command);
                this.editor.focus();
            }
        });
        
        // Select events
        this.toolbar.addEventListener('change', (e) => {
            const select = e.target.closest('.toolbar-select');
            if (select) {
                const command = select.dataset.command;
                const value = select.value;
                this.executeCommand(command, value);
                this.editor.focus();
            }
        });
        
        // Color picker events
        this.toolbar.addEventListener('change', (e) => {
            const colorInput = e.target.closest('.toolbar-color');
            if (colorInput) {
                const command = colorInput.dataset.command;
                const value = colorInput.value;
                this.executeCommand(command, value);
                this.editor.focus();
            }
        });
        
        // Template button
        this.toolbar.addEventListener('click', (e) => {
            if (e.target.closest('.template-btn')) {
                e.preventDefault();
                this.showTemplateDropdown(e.target);
            }
        });
        
        // Emoji button
        this.toolbar.addEventListener('click', (e) => {
            if (e.target.closest('.emoji-btn')) {
                e.preventDefault();
                this.showEmojiPicker(e.target);
            }
        });
        
        // Keyboard shortcuts
        this.editor.addEventListener('keydown', (e) => {
            if (e.ctrlKey || e.metaKey) {
                switch (e.key.toLowerCase()) {
                    case 'b':
                        e.preventDefault();
                        this.executeCommand('bold');
                        break;
                    case 'i':
                        e.preventDefault();
                        this.executeCommand('italic');
                        break;
                    case 'u':
                        e.preventDefault();
                        this.executeCommand('underline');
                        break;
                    case 'z':
                        if (e.shiftKey) {
                            e.preventDefault();
                            this.executeCommand('redo');
                        } else {
                            e.preventDefault();
                            this.executeCommand('undo');
                        }
                        break;
                }
            }
        });
        
        // Auto-save
        let saveTimeout;
        this.editor.addEventListener('input', () => {
            clearTimeout(saveTimeout);
            saveTimeout = setTimeout(() => {
                this.autoSave();
            }, 1000);
        });
    }
    
    executeCommand(command, value = null) {
        switch (command) {
            case 'createLink':
                const url = prompt('Enter URL:');
                if (url) {
                    document.execCommand(command, false, url);
                }
                break;
            case 'insertImage':
                const imageUrl = prompt('Enter image URL:');
                if (imageUrl) {
                    document.execCommand(command, false, imageUrl);
                }
                break;
            case 'insertTable':
                this.insertTable();
                break;
            case 'insertHorizontalRule':
                document.execCommand(command, false, null);
                break;
            default:
                document.execCommand(command, false, value);
        }
        
        this.updateToolbarState();
    }
    
    insertTable() {
        const rows = prompt('Number of rows:', '3');
        const cols = prompt('Number of columns:', '3');
        
        if (rows && cols) {
            let table = '<table border="1" style="border-collapse: collapse; width: 100%;">';
            for (let i = 0; i < rows; i++) {
                table += '<tr>';
                for (let j = 0; j < cols; j++) {
                    table += '<td style="padding: 8px; border: 1px solid #ddd;">&nbsp;</td>';
                }
                table += '</tr>';
            }
            table += '</table>';
            
            document.execCommand('insertHTML', false, table);
        }
    }
    
    showTemplateDropdown(button) {
        // Remove existing dropdown
        const existing = document.querySelector('.template-dropdown');
        if (existing) existing.remove();
        
        const dropdown = document.createElement('div');
        dropdown.className = 'template-dropdown';
        
        const templates = [
            { name: 'Newsletter Template', content: this.getNewsletterTemplate() },
            { name: 'Promotion Template', content: this.getPromotionTemplate() },
            { name: 'Welcome Template', content: this.getWelcomeTemplate() },
            { name: 'Notification Template', content: this.getNotificationTemplate() }
        ];
        
        templates.forEach(template => {
            const item = document.createElement('div');
            item.className = 'template-item';
            item.textContent = template.name;
            item.addEventListener('click', () => {
                this.insertTemplate(template.content);
                dropdown.remove();
            });
            dropdown.appendChild(item);
        });
        
        // Position dropdown
        const rect = button.getBoundingClientRect();
        dropdown.style.left = rect.left + 'px';
        dropdown.style.top = (rect.bottom + 5) + 'px';
        
        document.body.appendChild(dropdown);
        
        // Close on outside click
        document.addEventListener('click', function closeDropdown(e) {
            if (!dropdown.contains(e.target) && !button.contains(e.target)) {
                dropdown.remove();
                document.removeEventListener('click', closeDropdown);
            }
        });
    }
    
    showEmojiPicker(button) {
        // Remove existing picker
        const existing = document.querySelector('.emoji-picker');
        if (existing) existing.remove();
        
        const picker = document.createElement('div');
        picker.className = 'emoji-picker';
        
        const emojis = ['😊', '😂', '❤️', '👍', '🎉', '🔥', '💯', '✨', '🌟', '💪', '🎯', '🚀', '💡', '📈', '🎊', '🏆', '💎', '⭐', '🎨', '🎭', '🎪', '🎟️', '🎫', '🎬', '🎤', '🎧', '🎼', '🎹', '🎸', '🎺', '🎻', '🥁', '🎮', '🎲', '🎯', '🎳', '🎰', '🎲', '🃏', '🀄', '🎴'];
        
        emojis.forEach(emoji => {
            const item = document.createElement('div');
            item.className = 'emoji-item';
            item.textContent = emoji;
            item.addEventListener('click', () => {
                this.insertText(emoji);
                picker.remove();
            });
            picker.appendChild(item);
        });
        
        // Position picker
        const rect = button.getBoundingClientRect();
        picker.style.left = rect.left + 'px';
        picker.style.top = (rect.bottom + 5) + 'px';
        
        document.body.appendChild(picker);
        
        // Close on outside click
        document.addEventListener('click', function closePicker(e) {
            if (!picker.contains(e.target) && !button.contains(e.target)) {
                picker.remove();
                document.removeEventListener('click', closePicker);
            }
        });
    }
    
    insertTemplate(content) {
        document.execCommand('insertHTML', false, content);
    }
    
    insertText(text) {
        document.execCommand('insertText', false, text);
    }
    
    updateToolbarState() {
        // Update button states based on current selection
        const buttons = this.toolbar.querySelectorAll('.toolbar-btn[data-command]');
        buttons.forEach(button => {
            const command = button.dataset.command;
            if (['bold', 'italic', 'underline', 'strikeThrough'].includes(command)) {
                if (document.queryCommandState(command)) {
                    button.classList.add('active');
                } else {
                    button.classList.remove('active');
                }
            }
        });
    }
    
    autoSave() {
        const content = this.getContent();
        localStorage.setItem(`email_editor_draft_${this.elementId}`, content);
    }
    
    loadDraft() {
        const draft = localStorage.getItem(`email_editor_draft_${this.elementId}`);
        if (draft && !this.editor.innerHTML.trim()) {
            this.setContent(draft);
        }
    }
    
    getContent() {
        return this.editor.innerHTML;
    }
    
    setContent(content) {
        this.editor.innerHTML = content;
    }
    
    clear() {
        this.editor.innerHTML = '';
    }
    
    getText() {
        return this.editor.textContent;
    }
    
    // Template methods
    getNewsletterTemplate() {
        return `
            <h2 style="color: #2d3748; margin-bottom: 20px;">Newsletter Title</h2>
            <p style="margin-bottom: 15px;">Dear valued customer,</p>
            <p style="margin-bottom: 15px;">We're excited to share our latest updates with you.</p>
            <ul style="margin-bottom: 15px;">
                <li>Feature update 1</li>
                <li>Feature update 2</li>
                <li>Feature update 3</li>
            </ul>
            <p style="margin-bottom: 15px;">Best regards,<br>The Team</p>
        `;
    }
    
    getPromotionTemplate() {
        return `
            <h2 style="color: #e53e3e; margin-bottom: 20px;">🔥 Special Offer!</h2>
            <p style="margin-bottom: 15px;">Don't miss out on our amazing promotion!</p>
            <div style="background: #fed7d7; border: 2px solid #f56565; padding: 20px; border-radius: 8px; margin: 20px 0; text-align: center;">
                <h3 style="color: #c53030; margin-top: 0;">Special Price: $99</h3>
                <p style="color: #2d3748; margin-bottom: 0;">This offer is valid until the end of the month!</p>
            </div>
            <p style="margin-bottom: 15px;">Click the button below to claim your offer!</p>
        `;
    }
    
    getWelcomeTemplate() {
        return `
            <h2 style="color: #38a169; margin-bottom: 20px;">🎉 Welcome!</h2>
            <p style="margin-bottom: 15px;">Thank you for joining us!</p>
            <p style="margin-bottom: 15px;">We're thrilled to have you as part of our community.</p>
            <div style="background: #f0fff4; border: 2px solid #68d391; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h3 style="color: #38a169; margin-top: 0;">Getting Started</h3>
                <p style="color: #2d3748; margin-bottom: 0;">Here are some resources to help you get started...</p>
            </div>
        `;
    }
    
    getNotificationTemplate() {
        return `
            <h2 style="color: #4299e1; margin-bottom: 20px;">🔔 Important Notification</h2>
            <p style="margin-bottom: 15px;">This is an important notification for all users.</p>
            <div style="background: #ebf8ff; border-left: 4px solid #4299e1; padding: 20px; margin: 20px 0;">
                <h3 style="color: #2b6cb0; margin-top: 0;">Key Information:</h3>
                <ul style="color: #2d3748;">
                    <li>Important point 1</li>
                    <li>Important point 2</li>
                    <li>Important point 3</li>
                </ul>
            </div>
        `;
    }
    
    loadTemplates() {
        // Load any saved templates from localStorage or API
        this.loadDraft();
    }
}

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = EmailEditor;
} else {
    window.EmailEditor = EmailEditor;
}
