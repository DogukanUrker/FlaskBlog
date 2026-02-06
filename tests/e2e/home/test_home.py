"""
E2E tests for the home page.
"""

import uuid

import pytest
from playwright.sync_api import expect

from tests.e2e.helpers.database_helpers import create_test_post


def _suffix() -> str:
    return uuid.uuid4().hex[:8]


class TestHomePage:
    """Tests for home page rendering and sorting."""

    @pytest.mark.smoke
    def test_home_page_loads_and_shows_posts(self, page, flask_server, db_path):
        """Home page should display a recently created post when sorted by newest."""
        seed = _suffix()
        title = f"Home Test Post {seed}"
        create_test_post(
            db_path=str(db_path),
            title=title,
            content=f"Content for home test {seed}",
            abstract=f"Abstract for home test {seed}. " + "A" * 160,
        )

        page.goto(
            f"{flask_server['base_url']}/by=time_stamp/sort=desc",
            wait_until="domcontentloaded",
        )

        expect(page.locator("body")).to_contain_text(title, timeout=5000)

    def test_home_page_sorting_by_views(self, page, flask_server, db_path):
        """Posts sorted by views descending should show the highest-views post on page 1."""
        seed = _suffix()
        high_title = f"High Views Post {seed}"

        create_test_post(
            db_path=str(db_path),
            title=high_title,
            content=f"Content for high views {seed}",
            abstract=f"Abstract for high views {seed}. " + "A" * 160,
            views=999999,
        )

        page.goto(
            f"{flask_server['base_url']}/by=views/sort=desc",
            wait_until="domcontentloaded",
        )

        expect(page.locator("body")).to_contain_text(high_title, timeout=5000)

    def test_home_page_invalid_sort_redirects(self, page, flask_server):
        """Invalid sort parameters should redirect back to /."""
        page.goto(
            f"{flask_server['base_url']}/by=invalid/sort=desc",
            wait_until="domcontentloaded",
        )

        expect(page).to_have_url(f"{flask_server['base_url']}/", timeout=5000)
