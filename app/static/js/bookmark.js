// Bookmark functionality
async function toggleBookmark(postId, button) {
    try {
        const response = await fetch(`/api/bookmark/${postId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken || ''
            }
        });

        if (response.ok) {
            const data = await response.json();
            
            // Update button appearance
            if (data.bookmarked) {
                button.classList.remove('btn-ghost');
                button.classList.add('btn-primary');
                button.innerHTML = '<i class="ti ti-bookmark-filled text-xl"></i>';
                button.title = 'Remove bookmark';
            } else {
                button.classList.remove('btn-primary');
                button.classList.add('btn-ghost');
                button.innerHTML = '<i class="ti ti-bookmark text-xl"></i>';
                button.title = 'Add bookmark';
            }
            
            // Show success message (optional)
            console.log(data.message);
        } else {
            console.error('Failed to toggle bookmark');
            alert('Please login to bookmark posts');
        }
    } catch (error) {
        console.error('Error toggling bookmark:', error);
        alert('An error occurred. Please try again.');
    }
}

// Check bookmark status for a post
async function checkBookmarkStatus(postId, button) {
    try {
        const response = await fetch(`/api/bookmark/status/${postId}`, {
            headers: {
                'X-CSRFToken': csrfToken || ''
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            
            // Update button appearance based on status
            if (data.bookmarked) {
                button.classList.remove('btn-ghost');
                button.classList.add('btn-primary');
                button.innerHTML = '<i class="ti ti-bookmark-filled text-xl"></i>';
                button.title = 'Remove bookmark';
            } else {
                button.classList.remove('btn-primary');
                button.classList.add('btn-ghost');
                button.innerHTML = '<i class="ti ti-bookmark text-xl"></i>';
                button.title = 'Add bookmark';
            }
        }
    } catch (error) {
        console.error('Error checking bookmark status:', error);
    }
}

// Initialize bookmark buttons on page load
document.addEventListener('DOMContentLoaded', function() {
    // Check all bookmark buttons on the page
    const bookmarkButtons = document.querySelectorAll('.bookmark-btn');
    bookmarkButtons.forEach(button => {
        const postId = button.getAttribute('data-post-id');
        if (postId) {
            checkBookmarkStatus(postId, button);
        }
    });
});