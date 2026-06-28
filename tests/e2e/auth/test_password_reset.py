"""
Tests for the password reset flow.
"""

from playwright.sync_api import Page

from tests.e2e.pages.password_reset_page import PasswordResetPage
from tests.e2e.pages.login_page import LoginPage


def test_password_reset_flow(page: Page, flask_server: dict, test_user):
    """Test the complete password reset flow."""
    reset_page = PasswordResetPage(page, flask_server["base_url"])
    reset_page.navigate()

    # Step 1: Request reset code
    reset_page.request_reset_code(test_user.username, test_user.email)

    # Wait for redirect to verification code entry step
    page.wait_for_url("**/password-reset/codesent=true", timeout=10000)

    # Step 2: Submit verification code (123456 set by E2E_TESTING=1) and new password
    new_password = "NewStrongPassword123!"
    reset_page.submit_new_password(test_user.username, "123456", new_password)

    # Wait for redirect back to login upon success
    page.wait_for_url("**/login/redirect=*", timeout=10000)

    # Verify login works with the new password
    login_page = LoginPage(page, flask_server["base_url"])
    login_page.login(test_user.username, new_password)

    # Should redirect to home successfully
    page.wait_for_url("**/", timeout=10000)
