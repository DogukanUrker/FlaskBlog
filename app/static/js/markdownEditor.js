// Markdown Editor with Toolbar and Preview
document.addEventListener('DOMContentLoaded', function() {
    const textarea = document.getElementById('markdown-editor');
    if (!textarea) return;

    // Create editor container
    const container = document.createElement('div');
    container.className = 'markdown-editor-container';

    // Create tab navigation
    const tabNav = document.createElement('div');
    tabNav.className = 'editor-tabs';
    tabNav.innerHTML = `
        <button type="button" class="tab-btn tab-btn-action" data-tab="full-preview" title="Open preview in new window">
            <i class="ti ti-external-link"></i> Open Preview
        </button>
    `;

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
    container.appendChild(tabNav);
    container.appendChild(toolbar);
    container.appendChild(textarea);
    container.appendChild(statusBar);

    // Open preview button functionality
    const previewButton = tabNav.querySelector('.tab-btn');
    if (previewButton) {
        previewButton.addEventListener('click', function() {
            openFullPreview();
        });
    }

    // Function to open full preview in new window
    function openFullPreview() {
        // Collect all form fields
        const titleInput = document.getElementById('postTitle') || document.querySelector('input[name="postTitle"]');
        const tagsInput = document.getElementById('postTags') || document.querySelector('input[name="postTags"]');
        const abstractInput = document.getElementById('postAbstract') || document.querySelector('textarea[name="postAbstract"]');
        const categoryInput = document.getElementById('postCategory') || document.querySelector('select[name="postCategory"]');

        const title = titleInput ? titleInput.value : '';
        const tags = tagsInput ? tagsInput.value : '';
        const abstract = abstractInput ? abstractInput.value : '';
        const category = categoryInput ? categoryInput.value : '';
        const content = textarea.value;

        // Get CSRF token
        const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') ||
                         document.querySelector('input[name="csrf_token"]')?.value;

        // Create form data
        const formData = new FormData();
        formData.append('postTitle', title);
        formData.append('postTags', tags);
        formData.append('postAbstract', abstract);
        formData.append('postContent', content);
        formData.append('postCategory', category);
        formData.append('csrf_token', csrfToken);

        // Send to preview endpoint
        fetch('/preview/post', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                // Open preview in new window
                window.open('/preview/post', '_blank', 'width=1200,height=800,scrollbars=yes,resizable=yes');
            } else {
                throw new Error('Preview request failed');
            }
        })
        .catch(error => {
            console.error('Error opening preview:', error);
            alert('Failed to open preview. Please try again.');
        });
    }

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