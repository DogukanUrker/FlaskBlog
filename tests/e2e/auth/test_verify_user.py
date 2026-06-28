"""
Tests for the user verification flow.
"""

import pytest
from playwright.sync_api import Page

from tests.e2e.pages.verify_user_page import VerifyUserPage
from tests.e2e.pages.login_page import LoginPage
from tests.e2e.helpers.database_helpers import get_user_by_username


@pytest.mark.auth
def test_verify_user_flow(
    page: Page, flask_server: dict, unverified_test_user, db_path
):
    """Test the complete verify user email flow."""

    # Login as unverified user first since verify-user is login_required
    login_page = LoginPage(page, flask_server["base_url"])
    login_page.navigate()
    login_page.login(unverified_test_user.username, unverified_test_user.password)
    page.wait_for_url("**/", timeout=10000)

    verify_page = VerifyUserPage(page, flask_server["base_url"])
    verify_page.navigate()

    # Step 1: Request verification code email
    verify_page.request_verification_code()

    # Wait for redirect to verification code entry step
    page.wait_for_url("**/verify-user/codesent=true", timeout=10000)

    # Step 2: Submit verification code (123456 set by E2E_TESTING=1)
    verify_page.submit_verification_code("123456")

    # Wait for redirect back to home upon success
    page.wait_for_url("**/", timeout=10000)

    # Verify that the user state is updated in the database
    user_in_db = get_user_by_username(str(db_path), unverified_test_user.username)
    assert user_in_db["is_verified"] == "True"
