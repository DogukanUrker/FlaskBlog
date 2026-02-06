"""
E2E tests for static pages (about, privacy policy).
"""

import pytest
from playwright.sync_api import expect


class TestStaticPages:
    """Tests for static pages that require no authentication or database setup."""

    @pytest.mark.smoke
    def test_about_page_loads(self, page, flask_server):
        """About page should render with github button and version badge."""
        page.goto(f"{flask_server['base_url']}/about", wait_until="domcontentloaded")

        expect(page.locator(".btn-primary").first).to_be_visible(timeout=5000)
        expect(page.locator(".badge-ghost").first).to_be_visible(timeout=5000)

    @pytest.mark.smoke
    def test_privacy_policy_page_loads(self, page, flask_server):
        """Privacy policy page should render with article content and heading."""
        page.goto(
            f"{flask_server['base_url']}/privacy-policy",
            wait_until="domcontentloaded",
        )

        expect(page.locator("article.prose")).to_be_visible(timeout=5000)
        expect(page.locator("h1").first).to_be_visible(timeout=5000)
