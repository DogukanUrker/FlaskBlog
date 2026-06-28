"""
Tests for the public user profile page.
"""

from playwright.sync_api import Page, expect

from tests.e2e.pages.user_profile_page import UserProfilePage
from tests.e2e.helpers.database_helpers import create_test_post, create_test_comment


def test_user_profile_displays_info_and_posts(
    page: Page, flask_server: dict, test_user, db_path
):
    """Test that a user's public profile correctly displays their info, posts, and comments."""

    # Setup: create a post and a comment for the test user
    post = create_test_post(
        db_path=str(db_path),
        title="Test Profile Post",
        content="This is a test post for the profile.",
        abstract="Test abstract",
        author=test_user.username,
        views=42,
    )

    create_test_comment(
        db_path=str(db_path),
        post_id=post["id"],
        comment="Test profile comment",
        username=test_user.username,
    )

    profile_page = UserProfilePage(page, flask_server["base_url"])
    profile_page.navigate(test_user.username)

    # Verify user details are loaded
    profile_page.expect_user_loaded(test_user.username)

    # Verify the stats are displayed (we created 1 post with 42 views)
    expect(page.locator(profile_page.stats_container)).to_contain_text("42")

    # Verify posts and comments are listed
    expect(page.locator(profile_page.post_cards)).to_have_count(1)
    expect(page.locator(profile_page.post_cards).first).to_contain_text(
        "Test Profile Post"
    )

    expect(page.locator(profile_page.comment_cards)).to_have_count(1)
    expect(page.locator(profile_page.comment_cards).first).to_contain_text(
        "Test profile comment"
    )


def test_user_profile_not_found(page: Page, flask_server: dict):
    """Test that visiting a non-existent user profile returns a 404."""

    profile_page = UserProfilePage(page, flask_server["base_url"])
    profile_page.navigate("this_user_does_not_exist_at_all_123")

    profile_page.expect_not_found()
