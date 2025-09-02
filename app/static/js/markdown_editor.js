// Markdown Editor with Toolbar
document.addEventListener('DOMContentLoaded', function() {
    const textarea = document.getElementById('markdown-editor');
    if (!textarea) return;
    
    // Create editor container
    const container = document.createElement('div');
    container.className = 'markdown-editor-container';
    
    // Create toolbar
    const toolbar = document.createElement('div');
    toolbar.className = 'editor-toolbar';
    toolbar.innerHTML = `
        <button type="button" class="editor-btn" onclick="insertText('**', '**')" title="Bold">
            <strong>B</strong>
        </button>
        <button type="button" class="editor-btn" onclick="insertText('*', '*')" title="Italic">
            <em>I</em>
        </button>
        <button type="button" class="editor-btn" onclick="insertText('~~', '~~')" title="Strikethrough">
            <s>S</s>
        </button>
        <div class="editor-separator"></div>
        <button type="button" class="editor-btn" onclick="insertText('# ', '')" title="Heading 1">
            H1
        </button>
        <button type="button" class="editor-btn" onclick="insertText('## ', '')" title="Heading 2">
            H2
        </button>
        <button type="button" class="editor-btn" onclick="insertText('### ', '')" title="Heading 3">
            H3
        </button>
        <div class="editor-separator"></div>
        <button type="button" class="editor-btn" onclick="insertText('> ', '')" title="Quote">
            " "
        </button>
        <button type="button" class="editor-btn" onclick="insertText('- ', '')" title="List">
            •
        </button>
        <button type="button" class="editor-btn" onclick="insertText('1. ', '')" title="Numbered List">
            1.
        </button>
        <div class="editor-separator"></div>
        <button type="button" class="editor-btn" onclick="insertText('[', '](url)')" title="Link">
            🔗
        </button>
        <button type="button" class="editor-btn" onclick="insertText('![', '](url)')" title="Image">
            🖼️
        </button>
        <button type="button" class="editor-btn" onclick="insertText('\`', '\`')" title="Code">
            &lt;/&gt;
        </button>
        <button type="button" class="editor-btn" onclick="insertText('\`\`\`\n', '\n\`\`\`')" title="Code Block">
            { }
        </button>
        <div class="editor-separator"></div>
        <button type="button" class="editor-btn" onclick="insertText('\n---\n', '')" title="Horizontal Rule">
            ───
        </button>
    `;
    
    // Create status bar
    const statusBar = document.createElement('div');
    statusBar.className = 'editor-status';
    statusBar.innerHTML = '<span id="char-count">0 characters</span><span>Markdown supported</span>';
    
    // Insert toolbar before textarea
    textarea.parentNode.insertBefore(container, textarea);
    container.appendChild(toolbar);
    container.appendChild(textarea);
    container.appendChild(statusBar);
    
    // Add placeholder
    textarea.placeholder = `Write your amazing blog post here... 📝

## Start writing!

Use **bold**, *italic*, and other markdown features.

### Tips:
- Use # for headings
- Use **text** for bold
- Use *text* for italic
- Use [text](url) for links
- Use ![alt](url) for images`;
    
    // Character count
    function updateCharCount() {
        const count = textarea.value.length;
        document.getElementById('char-count').textContent = count + ' characters';
    }
    
    textarea.addEventListener('input', updateCharCount);
    updateCharCount();
    
    // Global function for toolbar buttons
    window.insertText = function(before, after) {
        const start = textarea.selectionStart;
        const end = textarea.selectionEnd;
        const selectedText = textarea.value.substring(start, end);
        const newText = before + selectedText + after;
        
        textarea.value = textarea.value.substring(0, start) + newText + textarea.value.substring(end);
        
        // Set cursor position
        const newCursorPos = start + before.length + selectedText.length;
        textarea.setSelectionRange(newCursorPos, newCursorPos);
        textarea.focus();
        updateCharCount();
    };
    
    // Keyboard shortcuts
    textarea.addEventListener('keydown', function(e) {
        if (e.ctrlKey || e.metaKey) {
            switch(e.key) {
                case 'b':
                    e.preventDefault();
                    insertText('**', '**');
                    break;
                case 'i':
                    e.preventDefault();
                    insertText('*', '*');
                    break;
                case 'k':
                    e.preventDefault();
                    insertText('[', '](url)');
                    break;
            }
        }
        
        // Tab support
        if (e.key === 'Tab') {
            e.preventDefault();
            insertText('    ', '');
        }
    });
}); 