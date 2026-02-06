"""
Create Post Page Object for interacting with the create-post form.
"""

from playwright.sync_api import Page, expect

from tests.e2e.pages.base_page import BasePage


class CreatePostPage(BasePage):
    """Page object for the create-post page."""

    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)

        self.title_input = 'input[name="post_title"]'
        self.tags_input = 'input[name="post_tags"]'
        self.abstract_input = 'textarea[name="post_abstract"]'
        self.banner_input = 'input[name="post_banner"]'
        self.category_select = 'select[name="post_category"]'
        self.content_input = 'textarea[name="post_content"]'
        self.submit_button = 'button[type="submit"]'
        self.csrf_token = 'input[name="csrf_token"]'

    def navigate(self, path: str = "/create-post"):
        """Navigate to the create-post page."""
        return super().navigate(path)

    def fill_title(self, title: str):
        self.page.fill(self.title_input, title)
        return self

    def fill_tags(self, tags: str):
        self.page.fill(self.tags_input, tags)
        return self

    def fill_abstract(self, abstract: str):
        self.page.fill(self.abstract_input, abstract)
        return self

    def fill_content(self, content: str):
        self.page.fill(self.content_input, content)
        return self

    def select_category(self, category: str):
        self.page.select_option(self.category_select, category)
        return self

    def click_submit(self):
        self.page.click(self.submit_button)
        return self

    def create_post(
        self,
        title: str,
        tags: str,
        abstract: str,
        content: str,
        category: str = "Technology",
    ):
        self.fill_title(title)
        self.fill_tags(tags)
        self.fill_abstract(abstract)
        self.fill_content(content)
        self.select_category(category)
        self.click_submit()
        return self

    def expect_page_loaded(self):
        expect(self.page.locator(self.title_input)).to_be_visible()
        expect(self.page.locator(self.tags_input)).to_be_visible()
        expect(self.page.locator(self.abstract_input)).to_be_visible()
        expect(self.page.locator(self.content_input)).to_be_visible()
        expect(self.page.locator(self.category_select)).to_be_visible()
        expect(self.page.locator(self.submit_button)).to_be_visible()
        expect(self.page.locator(self.csrf_token)).to_be_attached()
        return self
