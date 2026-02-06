"""
Post Page Object for interacting with post detail and comments.
"""

from playwright.sync_api import Page, expect

from tests.e2e.pages.base_page import BasePage


class PostPage(BasePage):
    """Page object for the post detail page."""

    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)

        self.post_title = "article h1"
        self.views_count = "i.ti-eye + span"
        self.comment_input = 'textarea[name="comment"]'
        self.comment_submit_button = (
            'form:has(textarea[name="comment"]) button[type="submit"]'
        )
        self.post_delete_button = 'button[name="post_delete_button"]'
        self.edit_post_link = 'a[href^="/edit-post/"]'

    def navigate(self, url_id: str, slug: str | None = None):
        """Navigate to a post by URL ID, optionally with slug."""
        if slug:
            return super().navigate(f"/post/{slug}-{url_id}")
        return super().navigate(f"/post/{url_id}")

    def expect_page_loaded(self, timeout: int = 5000):
        expect(self.page.locator(self.post_title).first).to_be_visible(timeout=timeout)
        return self

    def get_views_count(self) -> int:
        views_text = self.page.locator(self.views_count).first.inner_text().strip()
        return int(views_text)

    def fill_comment(self, comment: str):
        self.page.fill(self.comment_input, comment)
        return self

    def submit_comment(self):
        self.page.click(self.comment_submit_button)
        return self

    def add_comment(self, comment: str):
        self.fill_comment(comment)
        self.submit_comment()
        return self

    def expect_comment_visible(self, comment: str, timeout: int = 5000):
        expect(self.page.get_by_text(comment, exact=False).first).to_be_visible(
            timeout=timeout
        )
        return self

    def delete_post(self):
        self.page.click(self.post_delete_button)
        return self

    def click_edit_post(self):
        self.page.click(self.edit_post_link)
        return self
