"""
Tests for pagination functionality on the home page.
"""

from playwright.sync_api import Page, expect

from tests.e2e.helpers.database_helpers import create_test_post


class TestPagination:
    """Test suite for pagination across list views."""

    def test_homepage_pagination(self, page: Page, flask_server: dict, db_path: str):
        """Test that homepage correctly paginates when there are more than 12 posts."""

        # Create 13 posts to trigger a second page (per_page=12 in paginate.py)
        for i in range(13):
            create_test_post(
                db_path=str(db_path),
                title=f"Pagination Test Post {i + 1:02d}",
                content=f"Content for post {i + 1}",
                abstract=f"Abstract for post {i + 1}",
                # Ensure they sort properly by giving them massively high views
                # to override any posts created by parallel tests
                views=2000000 + i,
            )

        # Navigate to homepage sorted by views descending
        page.goto(f"{flask_server['base_url']}/by=views/sort=desc")

        # We should see posts 2 to 13 (highest views 12 down to 1, total 12 posts)
        # Because views=12 is the 13th post (0-indexed loop)
        expect(page.locator(".grid .card")).to_have_count(12)
        expect(page.locator("body")).to_contain_text("Pagination Test Post 13")

        # Pagination should be visible and indicate "1 / 2"
        pagination_text = page.locator("button.btn-active:has-text('1 / 2')")
        expect(pagination_text).to_be_visible()

        # Click the next page button
        page.locator(".join-item:has(.ti-chevron-right)").first.click()

        # Wait for the next page to load
        page.wait_for_url("**/by=views/sort=desc?page=2")

        # We should now see our 13th post (lowest views of our batch: 2000000).
        # We DO NOT assert exact card count here, because page 2 will also
        # contain posts created by other parallel workers.
        expect(page.locator("body")).to_contain_text("Pagination Test Post 01")
