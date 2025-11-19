function searchBar() {
  const input = document.querySelector("#searchBarInput").value;
  if (input === "" || input.trim() === "") {
    // Do nothing if input is empty
  } else {
    // Use encodeURIComponent to properly encode the search query
    window.location.href = `/search/${encodeURIComponent(input.trim())}`;
  }
}

// Allow Enter key to trigger search
document.addEventListener('DOMContentLoaded', function() {
  const searchInput = document.querySelector("#searchBarInput");
  if (searchInput) {
    searchInput.addEventListener('keypress', function(event) {
      if (event.key === 'Enter') {
        event.preventDefault();
        searchBar();
      }
    });
  }
});
