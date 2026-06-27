"""
E2E tests for the category page.
"""

import uuid

from playwright.sync_api import expect

from tests.e2e.helpers.database_helpers import create_test_post


def _suffix() -> str:
    return uuid.uuid4().hex[:8]


class TestCategory:
    """Tests for category page filtering and error handling."""

    def test_category_page_shows_posts_from_category(self, page, flask_server, db_path):
        """Category page should display posts belonging to that category."""
        seed = _suffix()
        title = f"Science Post {seed}"
        create_test_post(
            db_path=str(db_path),
            title=title,
            content=f"Content for category test {seed}",
            abstract=f"Abstract for category test {seed}. " + "A" * 160,
            category="Science",
        )

        page.goto(
            f"{flask_server['base_url']}/category/Science",
            wait_until="domcontentloaded",
        )

        expect(page.locator("body")).to_contain_text(title, timeout=5000)

    def test_category_excludes_other_categories(self, page, flask_server, db_path):
        """Category page should not display posts from other categories."""
        seed = _suffix()
        title = f"Science Only Post {seed}"
        create_test_post(
            db_path=str(db_path),
            title=title,
            content=f"Content for exclusion test {seed}",
            abstract=f"Abstract for exclusion test {seed}. " + "A" * 160,
            category="Science",
        )

        page.goto(
            f"{flask_server['base_url']}/category/Technology",
            wait_until="domcontentloaded",
        )

        expect(page.locator("body")).not_to_contain_text(title, timeout=5000)

    def test_invalid_category_returns_404(self, page, flask_server):
        """Navigating to a nonexistent category should return a 404 page."""
        page.goto(
            f"{flask_server['base_url']}/category/nonexistent",
            wait_until="domcontentloaded",
        )

        expect(page.locator("h1")).to_contain_text("404", timeout=5000)
