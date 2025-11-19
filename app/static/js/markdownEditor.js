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
        <button type="button" class="tab-btn tab-btn-action" id="share-settings-btn" title="Configure social sharing">
            <i class="ti ti-share"></i> Share Settings
        </button>
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

    // Share settings button functionality
    const shareSettingsBtn = document.getElementById('share-settings-btn');
    if (shareSettingsBtn) {
        shareSettingsBtn.addEventListener('click', function() {
            openShareSettingsModal();
        });
    }

    // Open preview button functionality
    const previewButton = tabNav.querySelector('[data-tab="full-preview"]');
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

    // Function to open share settings modal
    function openShareSettingsModal() {
        // Get current settings from localStorage or defaults
        const shareEnabled = localStorage.getItem('shareEnabled') !== 'false';
        const shareUrl = localStorage.getItem('shareUrl') || 'https://x.com/intent/tweet?text=';
        const shareIcon = localStorage.getItem('shareIcon') || 'ti-brand-x';

        // Create modal HTML
        const modalHTML = `
            <div id="share-settings-modal" class="modal modal-open">
                <div class="modal-box">
                    <h3 class="font-bold text-lg mb-4">
                        <i class="ti ti-share mr-2"></i>
                        Social Sharing Settings
                    </h3>

                    <div class="form-control mb-4">
                        <label class="label cursor-pointer">
                            <span class="label-text">Enable sharing button</span>
                            <input type="checkbox" id="share-enabled" class="checkbox checkbox-primary" ${shareEnabled ? 'checked' : ''} />
                        </label>
                    </div>

                    <div class="form-control mb-4">
                        <label class="label">
                            <span class="label-text">Share URL</span>
                        </label>
                        <input type="text" id="share-url" value="${shareUrl}" class="input input-bordered w-full" placeholder="https://x.com/intent/tweet?text=" />
                        <label class="label">
                            <span class="label-text-alt">Examples:</span>
                        </label>
                        <div class="text-xs space-y-1">
                            <button type="button" class="btn btn-xs btn-ghost" onclick="document.getElementById('share-url').value='https://x.com/intent/tweet?text='; document.getElementById('share-icon').value='ti-brand-x';">X/Twitter</button>
                            <button type="button" class="btn btn-xs btn-ghost" onclick="document.getElementById('share-url').value='https://www.facebook.com/sharer/sharer.php?u='; document.getElementById('share-icon').value='ti-brand-facebook';">Facebook</button>
                            <button type="button" class="btn btn-xs btn-ghost" onclick="document.getElementById('share-url').value='https://www.linkedin.com/sharing/share-offsite/?url='; document.getElementById('share-icon').value='ti-brand-linkedin';">LinkedIn</button>
                        </div>
                    </div>

                    <div class="form-control mb-4">
                        <label class="label">
                            <span class="label-text">Icon class (Tabler Icons)</span>
                        </label>
                        <input type="text" id="share-icon" value="${shareIcon}" class="input input-bordered w-full" placeholder="ti-brand-x" />
                        <label class="label">
                            <span class="label-text-alt">Browse icons at <a href="https://tabler-icons.io/" target="_blank" class="link">tabler-icons.io</a></span>
                        </label>
                    </div>

                    <div class="modal-action">
                        <button type="button" class="btn" onclick="closeShareSettingsModal()">Cancel</button>
                        <button type="button" class="btn btn-primary" onclick="saveShareSettings()">Save</button>
                    </div>
                </div>
            </div>
        `;

        // Remove existing modal if any
        const existingModal = document.getElementById('share-settings-modal');
        if (existingModal) existingModal.remove();

        // Add modal to page
        document.body.insertAdjacentHTML('beforeend', modalHTML);
    }

    // Global functions for modal
    window.closeShareSettingsModal = function() {
        const modal = document.getElementById('share-settings-modal');
        if (modal) modal.remove();
    };

    window.saveShareSettings = function() {
        const shareEnabled = document.getElementById('share-enabled').checked;
        const shareUrl = document.getElementById('share-url').value;
        const shareIcon = document.getElementById('share-icon').value;

        // Save to localStorage
        localStorage.setItem('shareEnabled', shareEnabled);
        localStorage.setItem('shareUrl', shareUrl);
        localStorage.setItem('shareIcon', shareIcon);

        // Close modal
        closeShareSettingsModal();

        // Show success message
        alert('Share settings saved! These settings will apply to your browser.');
    };

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