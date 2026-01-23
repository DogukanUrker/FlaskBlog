let initialSpendTime = 0;

if (visitorID != null) {
  setInterval(() => {
    initialSpendTime += 5;

    const data = {
      visitorID: visitorID,
      spendTime: initialSpendTime,
    };

    fetch("/api/v1/timeSpendsDuration", {
      method: "POST",
      headers: { "X-CSRFToken": csrfToken, "Content-Type": "application/json" },
      body: JSON.stringify(data),
      keepalive: true,
    });
  }, 5000);
}

// Favorite functionality
let isFavorited = false;

// Check favorite status on page load
document.addEventListener('DOMContentLoaded', function() {
  if (document.getElementById('favorite-btn')) {
    checkFavoriteStatus();
  }
});

function checkFavoriteStatus() {
  fetch(`/article/${postId}/favorite/status`)
    .then(response => response.json())
    .then(data => {
      isFavorited = data.favorited;
      updateFavoriteButton();
    })
    .catch(error => console.error('Error checking favorite status:', error));
}

function toggleFavorite() {
  fetch(`/article/${postId}/favorite`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrfToken
    }
  })
  .then(response => response.json())
  .then(data => {
    if (data.status === 'success') {
      isFavorited = data.favorited;
      updateFavoriteButton();
      
      // Show success message
      const message = document.createElement('div');
      message.className = 'fixed top-4 right-4 bg-base-100 border border-rose-500 rounded-lg p-4 shadow-lg z-50';
      message.innerHTML = `
        <div class="flex items-center">
          <i class="ti ti-${isFavorited ? 'heart-filled' : 'heart'} text-rose-500 mr-2"></i>
          <span>${data.message}</span>
        </div>
      `;
      document.body.appendChild(message);
      
      setTimeout(() => {
        message.remove();
      }, 3000);
    } else {
      console.error('Error toggling favorite:', data.message);
    }
  })
  .catch(error => {
    console.error('Error:', error);
  });
}

function updateFavoriteButton() {
  const favoriteIcon = document.getElementById('favorite-icon');
  const favoriteBtn = document.getElementById('favorite-btn');
  
  if (isFavorited) {
    favoriteIcon.className = 'ti ti-heart-filled text-2xl text-rose-500';
    favoriteBtn.title = '{{ translations.favorites.removeFromFavorites }}';
  } else {
    favoriteIcon.className = 'ti ti-heart text-2xl';
    favoriteBtn.title = '{{ translations.favorites.addToFavorites }}';
  }
}
