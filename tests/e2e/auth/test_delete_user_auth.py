"""
E2E tests for delete_user() authorization checks.

Covers the authorization matrix:
- Admin deleting non-admin
- Admin deleting another admin (with >= 2 admins)
- Admin deleting last admin (blocked)
- Non-admin deleting own account
- Non-admin trying to delete another user (blocked)
"""

import uuid

import pytest

from tests.e2e.helpers.database_helpers import (
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


class TestDeleteUserAuth:
    """Tests for delete_user() authorization checks."""

    @pytest.mark.admin
    def test_admin_can_delete_other_user(
        self, page, flask_server, app_settings, db_path
    ):
        """Admin should be able to delete a regular user."""
        seed = _suffix()
        username = f"deladmin{seed}"
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

        page.goto(
            f"{flask_server['base_url']}/admin/users", wait_until="domcontentloaded"
        )
        csrf_token = page.locator('input[name="csrf_token"]').first.get_attribute(
            "value"
        )

        response = page.request.post(
            f"{flask_server['base_url']}/admin/users",
            form={
                "csrf_token": csrf_token,
                "username": username,
                "user_delete_button": "1",
            },
        )
        assert response.ok

        deleted_user = get_user_by_username(str(db_path), username)
        assert deleted_user is None, "Deleted user should no longer exist in database"

    @pytest.mark.admin
    def test_admin_can_delete_other_admin(
        self, page, flask_server, app_settings, db_path
    ):
        """Admin should be able to delete another admin if >= 2 admins remain."""
        seed = _suffix()
        username = f"admin_del{seed}"
        # Create a second admin
        create_test_user(
            db_path=str(db_path),
            username=username,
            email=f"{username}@test.com",
            password="TestPassword123!",
            role="admin",
        )

        _login(
            page,
            flask_server,
            app_settings["default_admin"]["username"],
            app_settings["default_admin"]["password"],
        )

        page.goto(
            f"{flask_server['base_url']}/admin/users", wait_until="domcontentloaded"
        )
        csrf_token = page.locator('input[name="csrf_token"]').first.get_attribute(
            "value"
        )

        response = page.request.post(
            f"{flask_server['base_url']}/admin/users",
            form={
                "csrf_token": csrf_token,
                "username": username,
                "user_delete_button": "1",
            },
        )
        assert response.ok

        deleted_user = get_user_by_username(str(db_path), username)
        assert deleted_user is None, "Deleted admin should no longer exist in database"

    @pytest.mark.admin
    def test_admin_cannot_delete_last_admin(
        self, page, flask_server, app_settings, db_path
    ):
        """Admin cannot delete the last admin (would leave no admins)."""
        # Create a test admin
        seed = _suffix()
        username = f"lastadmin{seed}"
        create_test_user(
            db_path=str(db_path),
            username=username,
            email=f"{username}@test.com",
            password="TestPassword123!",
            role="admin",
        )

        # Verify there are 2 admins now
        admin_count = get_user_by_username(str(db_path), username)
        assert admin_count is not None

        _login(
            page,
            flask_server,
            username,  # Login as the test admin (last admin)
            "TestPassword123!",
        )

        page.goto(
            f"{flask_server['base_url']}/admin/users", wait_until="domcontentloaded"
        )
        csrf_token = page.locator('input[name="csrf_token"]').first.get_attribute(
            "value"
        )

        response = page.request.post(
            f"{flask_server['base_url']}/admin/users",
            form={
                "csrf_token": csrf_token,
                "username": username,
                "user_delete_button": "1",
            },
        )
        # Should be blocked
        assert response.ok

        # User should still exist
        still_exists = get_user_by_username(str(db_path), username)
        assert still_exists is not None, "Last admin should not be deletable"

    @pytest.mark.admin
    def test_non_admin_cannot_delete_other_user(
        self, page, flask_server, app_settings, db_path
    ):
        """Non-admin user cannot delete another user."""
        seed = _suffix()
        target_username = f"target{seed}"
        victim_username = f"victim{seed}"

        # Create a victim user
        create_test_user(
            db_path=str(db_path),
            username=victim_username,
            email=f"{victim_username}@test.com",
            password="TestPassword123!",
            role="user",
        )

        # Login as a non-admin user
        _login(
            page,
            flask_server,
            target_username,
            "TestPassword123!",
        )

        # Try to delete another user via admin endpoint (forged request)
        page.goto(
            f"{flask_server['base_url']}/admin/users", wait_until="domcontentloaded"
        )
        csrf_token = page.locator('input[name="csrf_token"]').first.get_attribute(
            "value"
        )

        response = page.request.post(
            f"{flask_server['base_url']}/admin/users",
            form={
                "csrf_token": csrf_token,
                "username": victim_username,
                "user_delete_button": "1",
            },
        )

        # Should be redirected (not authorized)
        assert response.status in [302, 303]

        # Victim should still exist
        still_exists = get_user_by_username(str(db_path), victim_username)
        assert still_exists is not None, "Non-admin cannot delete other users"

    @pytest.mark.admin
    def test_user_can_delete_own_account(
        self, page, flask_server, app_settings, db_path
    ):
        """Non-admin user can delete their own account."""
        seed = _suffix()
        username = f"selfdel{seed}"
        create_test_user(
            db_path=str(db_path),
            username=username,
            email=f"{username}@test.com",
            password="TestPassword123!",
            role="user",
        )

        _login(page, flask_server, username, "TestPassword123!")

        page.goto(
            f"{flask_server['base_url']}/account-settings",
            wait_until="domcontentloaded",
        )
        csrf_token = page.locator('input[name="csrf_token"]').first.get_attribute(
            "value"
        )

        response = page.request.post(
            f"{flask_server['base_url']}/account-settings",
            form={
                "csrf_token": csrf_token,
                "username": username,
                "user_delete_button": "1",
            },
        )

        # Should redirect to home
        assert response.status in [302, 303]

        # User should be deleted
        deleted_user = get_user_by_username(str(db_path), username)
        assert deleted_user is None, "Self-deleted user should no longer exist"
