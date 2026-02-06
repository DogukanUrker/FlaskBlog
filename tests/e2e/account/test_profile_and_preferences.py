"""
E2E tests for profile/account settings and personalization routes.
"""

import re
import uuid

import pytest
from playwright.sync_api import expect

from tests.e2e.helpers.database_helpers import (
    create_test_comment,
    create_test_post,
    get_comment_by_id,
    get_post_by_url_id,
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


class TestChangeUsername:
    """Tests for the change username flow."""

    @pytest.mark.auth
    def test_change_username_updates_user_posts_comments_and_session(
        self, page, flask_server, test_user, db_path
    ):
        """Changing username should migrate author/comment ownership and update session."""
        original_username = test_user.username
        seed = _suffix()
        new_username = f"renamed_{seed}"

        post = create_test_post(
            db_path=str(db_path),
            title=f"Rename Post {seed}",
            content=f"Content for rename test {seed}",
            abstract=f"Abstract for rename test {seed}. " + "A" * 160,
            author=original_username,
        )
        comment_id = create_test_comment(
            db_path=str(db_path),
            post_id=post["id"],
            comment=f"Rename comment {seed} with enough text.",
            username=original_username,
        )

        _login(page, flask_server, original_username, test_user.password)

        page.goto(
            f"{flask_server['base_url']}/change-username",
            wait_until="domcontentloaded",
        )
        page.fill('input[name="new_username"]', new_username)
        page.click('button[type="submit"]')
        expect(page).to_have_url(
            f"{flask_server['base_url']}/account-settings", timeout=10000
        )

        updated_user = get_user_by_username(str(db_path), new_username)
        assert updated_user is not None, "Renamed user should exist in database"
        assert get_user_by_username(str(db_path), original_username) is None, (
            "Old username should no longer exist in users table"
        )

        updated_post = get_post_by_url_id(str(db_path), post["url_id"])
        assert updated_post is not None
        assert updated_post["author"] == new_username

        updated_comment = get_comment_by_id(str(db_path), comment_id)
        assert updated_comment is not None
        assert updated_comment["username"] == new_username

        expect(page.locator(f'a[href="/user/{new_username.lower()}"]')).to_be_visible(
            timeout=5000
        )

        page.goto(
            f"{flask_server['base_url']}/dashboard/{new_username}",
            wait_until="domcontentloaded",
        )
        expect(page).to_have_url(
            re.compile(
                rf"^{re.escape(flask_server['base_url'])}/dashboard/{re.escape(new_username.lower())}/?$"
            ),
            timeout=5000,
        )

    @pytest.mark.auth
    def test_change_username_rejects_existing_username_case_insensitive(
        self, page, flask_server, test_user, app_settings, db_path
    ):
        """Changing username to an existing username should fail without DB mutation."""
        _login(page, flask_server, test_user.username, test_user.password)

        page.goto(
            f"{flask_server['base_url']}/change-username",
            wait_until="domcontentloaded",
        )
        csrf_token = page.locator('input[name="csrf_token"]').first.get_attribute(
            "value"
        )
        assert csrf_token is not None and csrf_token != ""

        response = page.request.post(
            f"{flask_server['base_url']}/change-username",
            form={
                "csrf_token": csrf_token,
                "new_username": app_settings["default_admin"]["username"].upper(),
            },
        )
        assert response.ok

        page.goto(
            f"{flask_server['base_url']}/dashboard/{test_user.username}",
            wait_until="domcontentloaded",
        )
        expect(page).to_have_url(
            re.compile(
                rf"^{re.escape(flask_server['base_url'])}/dashboard/{re.escape(test_user.username.lower())}/?$"
            ),
            timeout=5000,
        )

        still_exists = get_user_by_username(str(db_path), test_user.username)
        assert still_exists is not None, "Username should remain unchanged on failure"


class TestChangeProfilePicture:
    """Tests for profile picture updates."""

    @pytest.mark.auth
    def test_change_profile_picture_persists_new_dicebear_url(
        self, page, flask_server, test_user, db_path
    ):
        """Changing profile picture should store the expected Dicebear URL."""
        seed = f"profile_{_suffix()}"
        expected_profile_picture = (
            f"https://api.dicebear.com/7.x/identicon/svg?seed={seed}&radius=10"
        )

        _login(page, flask_server, test_user.username, test_user.password)

        page.goto(
            f"{flask_server['base_url']}/change-profile-picture",
            wait_until="domcontentloaded",
        )
        page.fill('input[name="new_profile_picture_seed"]', seed)
        page.click('button[type="submit"]')

        expect(page).to_have_url(
            f"{flask_server['base_url']}/account-settings", timeout=10000
        )

        updated_user = get_user_by_username(str(db_path), test_user.username)
        assert updated_user is not None
        assert updated_user["profile_picture"] == expected_profile_picture


class TestPreferences:
    """Tests for language/theme preference routes."""

    def test_set_language_redirects_and_persists_html_lang(self, page, flask_server):
        """Selecting a language should redirect to change-language and persist in session."""
        page.goto(
            f"{flask_server['base_url']}/set-language/tr",
            wait_until="domcontentloaded",
        )
        expect(page).to_have_url(f"{flask_server['base_url']}/change-language")
        expect(page.locator("html")).to_have_attribute("lang", "tr", timeout=5000)

        page.goto(f"{flask_server['base_url']}/about", wait_until="domcontentloaded")
        expect(page.locator("html")).to_have_attribute("lang", "tr", timeout=5000)

    def test_set_theme_redirects_to_referrer_and_persists_theme(
        self, page, flask_server
    ):
        """Selecting a theme should return to previous page and keep theme across pages."""
        page.goto(f"{flask_server['base_url']}/about", wait_until="domcontentloaded")
        page.eval_on_selector("#theme_modal", "modal => modal.showModal()")
        page.click('a[href="/set-theme/cupcake"]')

        expect(page).to_have_url(f"{flask_server['base_url']}/about", timeout=5000)
        expect(page.locator("html")).to_have_attribute(
            "data-theme",
            "cupcake",
            timeout=5000,
        )

        page.goto(
            f"{flask_server['base_url']}/search-bar",
            wait_until="domcontentloaded",
        )
        expect(page.locator("html")).to_have_attribute(
            "data-theme",
            "cupcake",
            timeout=5000,
        )
