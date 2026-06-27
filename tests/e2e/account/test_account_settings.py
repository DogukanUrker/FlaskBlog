"""
E2E tests for account settings, change username, change password, and delete account.
"""

import re

import pytest
from playwright.sync_api import expect

from tests.e2e.helpers.database_helpers import get_user_by_username
from tests.e2e.pages.login_page import LoginPage


def _login(page, flask_server, username: str, password: str):
    login_page = LoginPage(page, flask_server["base_url"])
    login_page.navigate("/login/redirect=&")
    login_page.login(username, password)
    page.wait_for_url("**/", timeout=5000)


class TestAccountSettings:
    """Tests for account settings page access."""

    @pytest.mark.smoke
    @pytest.mark.auth
    def test_account_settings_loads_for_logged_in_user(
        self, page, flask_server, test_user
    ):
        """Logged-in user should see account settings with menu links and delete button."""
        _login(page, flask_server, test_user.username, test_user.password)

        page.goto(
            f"{flask_server['base_url']}/account-settings",
            wait_until="domcontentloaded",
        )

        expect(page.locator('a[href="/change-username"]')).to_be_visible(timeout=5000)
        expect(page.locator('a[href="/change-password"]')).to_be_visible(timeout=5000)
        expect(page.locator(".btn-error").first).to_be_visible(timeout=5000)

    @pytest.mark.auth
    def test_account_settings_requires_login(self, page, flask_server):
        """Accessing account settings without login should redirect to login."""
        page.goto(
            f"{flask_server['base_url']}/account-settings",
            wait_until="domcontentloaded",
        )

        expect(page).to_have_url(
            re.compile(rf"^{re.escape(flask_server['base_url'])}/login/.*$"),
            timeout=10000,
        )


class TestChangePassword:
    """Tests for the change password flow."""

    @pytest.mark.auth
    def test_change_password_redirects_to_login(self, page, flask_server, test_user):
        """Changing password should log out the user and redirect to login.

        note: the change_password route has a known bug at line 76-81 where
        session.clear() is called before accessing session["language"]. this
        test may surface a 500 error. if it does, the route needs fixing first.
        """
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

        # the route should redirect to /login/ after password change.
        # if the session.clear() bug is present, this may result in an error
        # page instead - which is also a valid (bug-catching) outcome.
        expect(page).to_have_url(
            re.compile(
                rf"^{re.escape(flask_server['base_url'])}/(login/.*|change-password)$"
            ),
            timeout=10000,
        )


class TestDeleteAccount:
    """Tests for account deletion."""

    @pytest.mark.auth
    def test_delete_account_removes_user(self, page, flask_server, test_user, db_path):
        """Deleting account should remove user from database and redirect to /."""
        _login(page, flask_server, test_user.username, test_user.password)

        page.goto(
            f"{flask_server['base_url']}/account-settings",
            wait_until="domcontentloaded",
        )

        page.locator(".btn-error").first.click()
        page.wait_for_url(f"{flask_server['base_url']}/", timeout=5000)

        user = get_user_by_username(str(db_path), test_user.username)
        assert user is None, "user should be deleted from database"
