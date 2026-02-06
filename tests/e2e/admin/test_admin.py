"""
E2E tests for the admin panel.
"""

import uuid

import pytest
from playwright.sync_api import expect

from tests.e2e.helpers.database_helpers import (
    create_test_comment,
    create_test_post,
    create_test_user,
    get_user_by_username,
)
from tests.e2e.pages.login_page import LoginPage


def _suffix() -> str:
    return uuid.uuid4().hex[:8]


def _login(page, flask_server, username: str, password: str):
    login_page = LoginPage(page, flask_server["base_url"])
    login_page.navigate("/login/redirect=&")
    login_page.login(username, password)
    page.wait_for_url("**/", timeout=5000)


class TestAdminPanelAccess:
    """Tests for admin panel access control."""

    @pytest.mark.smoke
    @pytest.mark.admin
    def test_admin_panel_loads_for_admin(self, logged_in_page, flask_server):
        """Admin user should see the admin panel with users, posts, and comments links."""
        logged_in_page.goto(
            f"{flask_server['base_url']}/admin", wait_until="domcontentloaded"
        )

        expect(logged_in_page.locator('a[href="admin/users"]')).to_be_visible(
            timeout=5000
        )
        expect(logged_in_page.locator('a[href="admin/posts"]')).to_be_visible(
            timeout=5000
        )
        expect(logged_in_page.locator('a[href="admin/comments"]')).to_be_visible(
            timeout=5000
        )

    @pytest.mark.admin
    def test_admin_panel_redirects_non_admin(self, page, flask_server, test_user):
        """Non-admin user should be redirected away from admin panel to /."""
        _login(page, flask_server, test_user.username, test_user.password)

        page.goto(f"{flask_server['base_url']}/admin", wait_until="domcontentloaded")

        expect(page).to_have_url(f"{flask_server['base_url']}/", timeout=5000)


class TestAdminUsers:
    """Tests for admin user management page."""

    @pytest.mark.admin
    def test_admin_users_page_lists_users(self, logged_in_page, flask_server, db_path):
        """Admin users page should display user cards with the admin user visible."""
        logged_in_page.goto(
            f"{flask_server['base_url']}/admin/users", wait_until="domcontentloaded"
        )

        # admin user is always on page 1
        expect(logged_in_page.locator("body")).to_contain_text("admin", timeout=5000)
        expect(logged_in_page.locator(".card.bg-base-200").first).to_be_visible(
            timeout=5000
        )

    @pytest.mark.admin
    def test_admin_can_change_user_role(
        self, page, flask_server, app_settings, db_path
    ):
        """Admin should be able to change a user's role from user to admin via POST."""
        seed = _suffix()
        username = f"roletest{seed}"
        create_test_user(
            db_path=str(db_path),
            username=username,
            email=f"{username}@test.com",
            password="TestPassword123!",
            role="user",
        )

        _login(
            page,
            flask_server,
            app_settings["default_admin"]["username"],
            app_settings["default_admin"]["password"],
        )

        # navigate to admin/users to get a valid csrf token
        page.goto(
            f"{flask_server['base_url']}/admin/users", wait_until="domcontentloaded"
        )

        csrf_token = page.locator('input[name="csrf_token"]').first.get_attribute(
            "value"
        )

        # submit role change via POST directly (avoids pagination)
        page.request.post(
            f"{flask_server['base_url']}/admin/users",
            form={
                "csrf_token": csrf_token,
                "username": username,
                "user_role_change_button": "1",
            },
        )

        user = get_user_by_username(str(db_path), username)
        assert user is not None
        assert user["role"] == "admin"


class TestAdminContent:
    """Tests for admin content management pages."""

    @pytest.mark.admin
    def test_admin_comments_page_shows_comments(
        self, logged_in_page, flask_server, db_path
    ):
        """Admin comments page should display created comments."""
        seed = _suffix()
        post = create_test_post(
            db_path=str(db_path),
            title=f"Admin Comment Post {seed}",
            content=f"Content for admin comment test {seed}",
            abstract=f"Abstract for admin comment test {seed}. " + "A" * 160,
        )

        comment_text = f"Admin visible comment {seed} with enough text to display."
        create_test_comment(
            db_path=str(db_path),
            post_id=post["id"],
            comment=comment_text,
            username="admin",
        )

        logged_in_page.goto(
            f"{flask_server['base_url']}/admin/comments", wait_until="domcontentloaded"
        )

        expect(logged_in_page.locator("body")).to_contain_text(
            comment_text, timeout=5000
        )
