"""
E2E test for password change credential rotation flow.
"""

import re

import pytest
from playwright.sync_api import expect

from tests.e2e.pages.login_page import LoginPage
from tests.e2e.pages.navbar_component import NavbarComponent


def _login(page, flask_server, username: str, password: str):
    login_page = LoginPage(page, flask_server["base_url"])
    login_page.navigate("/login/redirect=&")
    login_page.login(username, password)
    page.wait_for_url("**/", timeout=5000)


class TestChangePasswordCredentialRotation:
    """Tests that password changes update real authentication behavior."""

    @pytest.mark.auth
    def test_change_password_invalidates_old_password_and_accepts_new_password(
        self, page, flask_server, test_user
    ):
        """After password change, old password should fail and new password should work."""
        _login(page, flask_server, test_user.username, test_user.password)

        page.goto(
            f"{flask_server['base_url']}/change-password",
            wait_until="domcontentloaded",
        )

        new_password = "NewPassword456!"
        page.fill('input[name="old_password"]', test_user.password)
        page.fill('input[name="password"]', new_password)
        page.fill('input[name="password_confirm"]', new_password)
        page.click('button[type="submit"]')

        expect(page).to_have_url(
            re.compile(rf"^{re.escape(flask_server['base_url'])}/login/.*$"),
            timeout=10000,
        )

        login_page = LoginPage(page, flask_server["base_url"])

        login_page.login(test_user.username, test_user.password)
        login_page.expect_error_flash()

        login_page.login(test_user.username, new_password)
        expect(page).to_have_url(
            re.compile(rf"^{re.escape(flask_server['base_url'])}/?$"),
            timeout=10000,
        )

        navbar = NavbarComponent(page)
        navbar.expect_logged_in()
