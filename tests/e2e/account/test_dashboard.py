"""
E2E tests for the user dashboard.
"""

import re
import uuid

import pytest
from playwright.sync_api import expect

from tests.e2e.helpers.database_helpers import (
    create_test_comment,
    create_test_post,
    get_post_by_url_id,
)
from tests.e2e.pages.login_page import LoginPage


def _suffix() -> str:
    return uuid.uuid4().hex[:8]


def _login(page, flask_server, username: str, password: str):
    login_page = LoginPage(page, flask_server["base_url"])
    login_page.navigate("/login/redirect=&")
    login_page.login(username, password)
    page.wait_for_url("**/", timeout=5000)


def _get_csrf_token(page) -> str:
    token = page.locator('input[name="csrf_token"]').first.get_attribute("value")
    assert token is not None and token != ""
    return token


class TestDashboard:
    """Tests for user dashboard functionality."""

    def test_dashboard_shows_user_posts_and_comments(
        self, page, flask_server, test_user, db_path
    ):
        """Dashboard should display the user's posts and comments."""
        seed = _suffix()
        post = create_test_post(
            db_path=str(db_path),
            title=f"Dashboard Post {seed}",
            content=f"Content for dashboard test {seed}",
            abstract=f"Abstract for dashboard test {seed}. " + "A" * 160,
            author=test_user.username,
        )

        comment_text = f"Dashboard comment {seed} with enough text to display."
        create_test_comment(
            db_path=str(db_path),
            post_id=post["id"],
            comment=comment_text,
            username=test_user.username,
        )

        _login(page, flask_server, test_user.username, test_user.password)

        page.goto(
            f"{flask_server['base_url']}/dashboard/{test_user.username}",
            wait_until="domcontentloaded",
        )

        expect(page.locator("body")).to_contain_text(
            f"Dashboard Post {seed}", timeout=5000
        )
        expect(page.locator("body")).to_contain_text(comment_text, timeout=5000)

    @pytest.mark.auth
    def test_dashboard_requires_login(self, page, flask_server):
        """Accessing dashboard without login should redirect to login page."""
        page.goto(
            f"{flask_server['base_url']}/dashboard/someuser",
            wait_until="domcontentloaded",
        )

        expect(page).to_have_url(
            re.compile(rf"^{re.escape(flask_server['base_url'])}/login/.*$"),
            timeout=10000,
        )

    @pytest.mark.auth
    def test_dashboard_redirects_to_own_dashboard(self, page, flask_server, test_user):
        """Accessing another user's dashboard should redirect to your own."""
        _login(page, flask_server, test_user.username, test_user.password)

        page.goto(
            f"{flask_server['base_url']}/dashboard/admin",
            wait_until="domcontentloaded",
        )

        expect(page).to_have_url(
            re.compile(
                rf"^{re.escape(flask_server['base_url'])}/dashboard/{re.escape(test_user.username.lower())}.*$"
            ),
            timeout=5000,
        )

    def test_dashboard_can_delete_post(self, page, flask_server, test_user, db_path):
        """User should be able to delete their own post from the dashboard."""
        seed = _suffix()
        post = create_test_post(
            db_path=str(db_path),
            title=f"Deletable Dashboard Post {seed}",
            content=f"Content for delete test {seed}",
            abstract=f"Abstract for delete test {seed}. " + "A" * 160,
            author=test_user.username,
        )

        _login(page, flask_server, test_user.username, test_user.password)

        page.goto(
            f"{flask_server['base_url']}/dashboard/{test_user.username}",
            wait_until="domcontentloaded",
        )

        post_card = page.locator(
            ".card.bg-base-200", has_text=f"Deletable Dashboard Post {seed}"
        )
        expect(post_card).to_be_visible(timeout=5000)

        post_card.locator('button[name="post_delete_button"]').click()
        page.wait_for_load_state("domcontentloaded")

        deleted_post = get_post_by_url_id(str(db_path), post["url_id"])
        assert deleted_post is None, "post should be deleted from database"

    @pytest.mark.auth
    def test_dashboard_forged_request_cannot_delete_another_users_post(
        self, page, flask_server, test_user, db_path
    ):
        """Forged dashboard POST must not delete a post owned by another user."""
        seed = _suffix()
        protected_post = create_test_post(
            db_path=str(db_path),
            title=f"Protected Dashboard Post {seed}",
            content=f"Protected content {seed}",
            abstract=f"Protected abstract {seed}. " + "A" * 160,
            author="admin",
        )

        create_test_post(
            db_path=str(db_path),
            title=f"Owned Dashboard Post {seed}",
            content=f"Owned content {seed}",
            abstract=f"Owned abstract {seed}. " + "A" * 160,
            author=test_user.username,
        )

        _login(page, flask_server, test_user.username, test_user.password)

        dashboard_url = f"{flask_server['base_url']}/dashboard/{test_user.username}"
        page.goto(dashboard_url, wait_until="domcontentloaded")
        csrf_token = _get_csrf_token(page)

        response = page.request.post(
            dashboard_url,
            form={
                "csrf_token": csrf_token,
                "post_delete_button": "1",
                "post_id": str(protected_post["id"]),
            },
        )
        assert response.ok

        still_exists = get_post_by_url_id(str(db_path), protected_post["url_id"])
        assert still_exists is not None, (
            "Dashboard delete must not remove posts owned by another user"
        )
