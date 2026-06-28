"""
User Profile Page Object for interacting with the public user profile.
"""

from playwright.sync_api import Page, expect

from tests.e2e.pages.base_page import BasePage


class UserProfilePage(BasePage):
    """Page object for the user profile page."""

    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)

        self.username_heading = "h2.card-title"
        self.stats_container = ".stats"
        self.post_cards = ".grid .card"
        self.comment_cards = ".space-y-4 .card"

    def navigate(self, username: str):
        """Navigate to a specific user's profile page."""
        return super().navigate(f"/user/{username}")

    def expect_user_loaded(self, username: str):
        """Verify that the user profile is loaded correctly."""
        expect(self.page.locator(self.username_heading)).to_have_text(username)
        expect(self.page.locator(self.stats_container)).to_be_visible()
        return self

    def expect_not_found(self):
        """Verify that a 404/Not Found page is displayed."""
        expect(self.page.locator("h1")).to_contain_text("404")
        return self
