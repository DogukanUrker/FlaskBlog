"""
Password Reset Page Object for interacting with the password reset flow.
"""

from playwright.sync_api import Page

from tests.e2e.pages.base_page import BasePage


class PasswordResetPage(BasePage):
    """Page object for the password reset page."""

    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)

        # Form selectors - Request Code
        self.username_input = 'input[name="username"]'
        self.email_input = 'input[name="email"]'

        # Form selectors - Reset Password
        self.code_input = 'input[name="code"]'
        self.password_input = 'input[name="password"]'
        self.password_confirm_input = 'input[name="password_confirm"]'

        self.submit_button = 'button[type="submit"]'

    def navigate(self, path: str = "/password-reset/codesent=false"):
        """Navigate to the password reset page."""
        return super().navigate(path)

    def request_reset_code(self, username: str, email: str):
        """Submit the first step of password reset to request a code."""
        self.page.fill(self.username_input, username)
        self.page.fill(self.email_input, email)
        self.page.click(self.submit_button)
        return self

    def submit_new_password(self, username: str, code: str, password: str):
        """Submit the second step with the verification code and new password."""
        self.page.fill(self.username_input, username)
        self.page.fill(self.code_input, code)
        self.page.fill(self.password_input, password)
        self.page.fill(self.password_confirm_input, password)
        self.page.click(self.submit_button)
        return self
