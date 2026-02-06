"""
E2E tests for the search page.
"""

import uuid

from playwright.sync_api import expect

from tests.e2e.helpers.database_helpers import create_test_post, create_test_user


def _suffix() -> str:
    return uuid.uuid4().hex[:8]


class TestSearch:
    """Tests for search functionality."""

    def test_search_finds_post_by_title(self, page, flask_server, db_path):
        """Searching for a post title should show the matching post."""
        seed = _suffix()
        title = f"Searchable Post {seed}"
        create_test_post(
            db_path=str(db_path),
            title=title,
            content=f"Content for search test {seed}",
            abstract=f"Abstract for search test {seed}. " + "A" * 160,
        )

        page.goto(
            f"{flask_server['base_url']}/search/{title}",
            wait_until="domcontentloaded",
        )

        expect(page.locator("body")).to_contain_text(title, timeout=5000)

    def test_search_finds_user_by_username(self, page, flask_server, db_path):
        """Searching for a username should show the matching user."""
        seed = _suffix()
        username = f"searchuser{seed}"
        create_test_user(
            db_path=str(db_path),
            username=username,
            email=f"{username}@test.com",
            password="TestPassword123!",
        )

        page.goto(
            f"{flask_server['base_url']}/search/{username}",
            wait_until="domcontentloaded",
        )

        expect(page.locator("body")).to_contain_text(username, timeout=5000)

    def test_search_no_results_shows_empty_state(self, page, flask_server):
        """Searching for a nonexistent term should show an empty state alert."""
        random_query = uuid.uuid4().hex

        page.goto(
            f"{flask_server['base_url']}/search/{random_query}",
            wait_until="domcontentloaded",
        )

        expect(page.locator(".alert-warning").first).to_be_visible(timeout=5000)
