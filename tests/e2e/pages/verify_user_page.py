"""
Verify User Page Object for interacting with the verification flow.
"""

from playwright.sync_api import Page

from tests.e2e.pages.base_page import BasePage


class VerifyUserPage(BasePage):
    """Page object for the verify user page."""

    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)

        self.code_input = 'input[name="code"]'
        self.submit_button = 'button[type="submit"]'

    def navigate(self, path: str = "/verify-user/codesent=false"):
        """Navigate to the verify user page."""
        return super().navigate(path)

    def request_verification_code(self):
        """Click the button to request a verification code."""
        self.page.click(self.submit_button)
        return self

    def submit_verification_code(self, code: str):
        """Submit the received verification code."""
        self.page.fill(self.code_input, code)
        self.page.click(self.submit_button)
        return self
