"""
E2E tests for the logout functionality.
"""

import re

import pytest
from playwright.sync_api import expect

from tests.e2e.pages.base_page import BasePage
from tests.e2e.pages.login_page import LoginPage
from tests.e2e.pages.navbar_component import NavbarComponent


class TestLogoutBasicFunctionality:
    """Tests for basic logout functionality."""

    @pytest.mark.smoke
    @pytest.mark.auth
    def test_logout_clears_session_and_redirects_to_home(
        self, logged_in_page, flask_server
    ):
        """Test that clicking logout redirects to home page."""
        navbar = NavbarComponent(logged_in_page)

        # Perform logout
        navbar.logout()

        # Wait for redirect to home
        logged_in_page.wait_for_url("**/", timeout=5000)

        # Verify redirected to home page
        assert (
            logged_in_page.url.rstrip("/").endswith(str(flask_server["port"]))
            or logged_in_page.url == flask_server["base_url"] + "/"
        )

        # Verify logged out state
        navbar.expect_logged_out()

    @pytest.mark.auth
    def test_logout_shows_success_flash_message(self, logged_in_page, flask_server):
        """Test that success flash message appears after logout."""
        navbar = NavbarComponent(logged_in_page)
        base_page = BasePage(logged_in_page, flask_server["base_url"])

        # Perform logout
        navbar.logout()

        # Wait for redirect
        logged_in_page.wait_for_url("**/", timeout=5000)

        # Verify success flash is shown
        base_page.expect_success_flash()

    @pytest.mark.auth
    def test_logout_button_not_visible_when_logged_out(self, page, flask_server):
        """Test that logout link is hidden when not logged in."""
        # Navigate to home without logging in
        page.goto(flask_server["base_url"])

        navbar = NavbarComponent(page)

        # Logout link should not be visible
        assert not navbar.is_logged_in()
        navbar.expect_logged_out()


class TestLogoutSessionState:
    """Tests for session state after logout."""

    @pytest.mark.auth
    def test_logout_removes_session_navbar_shows_login(
        self, logged_in_page, flask_server
    ):
        """Test that after logout, navbar shows login link."""
        navbar = NavbarComponent(logged_in_page)

        # Verify logged in first
        navbar.expect_logged_in()

        # Perform logout
        navbar.logout()
        logged_in_page.wait_for_url("**/", timeout=5000)

        # Navbar should show login link
        navbar.expect_logged_out()

    @pytest.mark.auth
    def test_logout_session_does_not_persist_after_navigation(
        self, logged_in_page, flask_server
    ):
        """Test that session remains cleared after navigating to other pages."""
        navbar = NavbarComponent(logged_in_page)

        # Perform logout
        navbar.logout()
        logged_in_page.wait_for_url("**/", timeout=5000)

        # Navigate to another page (home again)
        logged_in_page.goto(flask_server["base_url"])

        # Should still be logged out
        navbar.expect_logged_out()

    @pytest.mark.auth
    def test_cannot_access_create_post_after_logout(self, logged_in_page, flask_server):
        """Test that /create-post redirects to login after logout."""
        navbar = NavbarComponent(logged_in_page)

        # Perform logout
        navbar.logout()
        logged_in_page.wait_for_url("**/", timeout=5000)

        # Try to access create-post
        logged_in_page.goto(f"{flask_server['base_url']}/create-post")

        # Should be redirected to login page
        assert "/login" in logged_in_page.url


class TestLogoutEdgeCases:
    """Tests for edge cases in logout functionality."""

    @pytest.mark.auth
    def test_logout_when_not_logged_in_redirects_to_home(self, page, flask_server):
        """Test that direct /logout when not logged in just redirects to home."""
        # Navigate directly to logout without being logged in
        page.goto(f"{flask_server['base_url']}/logout")

        # Wait for redirect
        page.wait_for_url("**/", timeout=5000)

        # Should be on home page
        assert (
            page.url.rstrip("/").endswith(str(flask_server["port"]))
            or page.url == flask_server["base_url"] + "/"
        )

    @pytest.mark.auth
    def test_logout_when_not_logged_in_no_success_flash(self, page, flask_server):
        """Test that no success flash appears when logging out while not logged in."""
        base_page = BasePage(page, flask_server["base_url"])

        # Navigate directly to logout without being logged in
        page.goto(f"{flask_server['base_url']}/logout")

        # Wait for redirect
        page.wait_for_url("**/", timeout=5000)

        # Success flash should NOT be visible (no session to clear)
        success_flash = page.locator(base_page.flash_success)
        assert success_flash.count() == 0

    @pytest.mark.auth
    def test_double_logout_does_not_error(self, logged_in_page, flask_server):
        """Test that calling /logout twice is safe and doesn't cause errors."""
        navbar = NavbarComponent(logged_in_page)

        # First logout
        navbar.logout()
        logged_in_page.wait_for_url("**/", timeout=5000)

        # Second logout (direct navigation)
        logged_in_page.goto(f"{flask_server['base_url']}/logout")
        logged_in_page.wait_for_url("**/", timeout=5000)

        # Should still be on home page without errors
        assert (
            logged_in_page.url.rstrip("/").endswith(str(flask_server["port"]))
            or logged_in_page.url == flask_server["base_url"] + "/"
        )

        # Page should load without error (check for navbar)
        navbar.expect_logged_out()


class TestLogoutWithDifferentUsers:
    """Tests for logout with different user types."""

    @pytest.mark.smoke
    @pytest.mark.auth
    @pytest.mark.admin
    def test_logout_admin_user(self, page, flask_server, app_settings):
        """Test that admin user can logout successfully."""
        login_page = LoginPage(page, flask_server["base_url"])
        navbar = NavbarComponent(page)
        base_page = BasePage(page, flask_server["base_url"])

        # Login as admin
        login_page.navigate("/login/redirect=&")
        login_page.login(
            app_settings["default_admin"]["username"],
            app_settings["default_admin"]["password"],
        )
        page.wait_for_url("**/", timeout=5000)

        # Verify logged in
        navbar.expect_logged_in()

        # Logout
        navbar.logout()
        page.wait_for_url("**/", timeout=5000)

        # Verify logged out with success message
        base_page.expect_success_flash()
        navbar.expect_logged_out()

    @pytest.mark.auth
    def test_logout_regular_user(self, page, flask_server, test_user):
        """Test that regular test user can logout successfully."""
        login_page = LoginPage(page, flask_server["base_url"])
        navbar = NavbarComponent(page)
        base_page = BasePage(page, flask_server["base_url"])

        # Login as test user
        login_page.navigate("/login/redirect=&")
        login_page.login(test_user.username, test_user.password)
        expect(page).to_have_url(
            re.compile(rf"^{re.escape(flask_server['base_url'])}/?$"), timeout=10000
        )

        # Verify logged in
        navbar.expect_logged_in()

        # Logout
        navbar.logout()
        page.wait_for_url("**/", timeout=5000)

        # Verify logged out with success message
        base_page.expect_success_flash()
        navbar.expect_logged_out()

    @pytest.mark.auth
    def test_logout_and_login_as_different_user(
        self, page, flask_server, app_settings, test_user
    ):
        """Test that after logout, user can login as a different user."""
        login_page = LoginPage(page, flask_server["base_url"])
        navbar = NavbarComponent(page)

        # Login as admin first
        login_page.navigate("/login/redirect=&")
        login_page.login(
            app_settings["default_admin"]["username"],
            app_settings["default_admin"]["password"],
        )
        page.wait_for_url("**/", timeout=5000)
        navbar.expect_logged_in()

        # Logout
        navbar.logout()
        page.wait_for_url("**/", timeout=5000)
        navbar.expect_logged_out()

        # Login as test user
        login_page.navigate("/login/redirect=&")
        login_page.login(test_user.username, test_user.password)
        # Use expect().to_have_url() which polls current URL (handles both fast and slow redirects)
        expect(page).to_have_url(
            re.compile(rf"^{re.escape(flask_server['base_url'])}/?$"), timeout=10000
        )

        # Verify logged in as different user
        navbar.expect_logged_in()


class TestLogoutUIBehavior:
    """Tests for UI behavior after logout."""

    @pytest.mark.auth
    def test_login_link_appears_after_logout(self, logged_in_page, flask_server):
        """Test that login link becomes visible after logout."""
        navbar = NavbarComponent(logged_in_page)

        # Before logout - login link should not be visible (logged in state)
        assert navbar.is_logged_in()

        # Perform logout
        navbar.logout()
        logged_in_page.wait_for_url("**/", timeout=5000)

        # Login link should now be visible
        navbar.expect_logged_out()

    @pytest.mark.auth
    def test_profile_avatar_hidden_after_logout(self, logged_in_page, flask_server):
        """Test that profile avatar is hidden after logout."""
        navbar = NavbarComponent(logged_in_page)

        # Before logout - verify profile avatar visible
        navbar.expect_profile_avatar_visible()

        # Perform logout
        navbar.logout()
        logged_in_page.wait_for_url("**/", timeout=5000)

        # Profile avatar should be hidden
        avatar = logged_in_page.locator(navbar.profile_avatar)
        assert avatar.count() == 0

    @pytest.mark.auth
    def test_create_post_button_hidden_after_logout(self, logged_in_page, flask_server):
        """Test that create post button is hidden after logout."""
        navbar = NavbarComponent(logged_in_page)

        # Before logout - verify create post link visible
        navbar.expect_create_post_visible()

        # Perform logout
        navbar.logout()
        logged_in_page.wait_for_url("**/", timeout=5000)

        # Create post link should be hidden
        create_post = logged_in_page.locator(navbar.create_post_link)
        assert create_post.count() == 0
