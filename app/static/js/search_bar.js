function searchBar() {
  const input = document.querySelector("#search-bar-input").value;
  if (input === "" || input.trim() === "") {
  } else {
    window.location.href = `/search/${encodeURIComponent(
      escape(input.trim()),
    )}`;
  }
}
