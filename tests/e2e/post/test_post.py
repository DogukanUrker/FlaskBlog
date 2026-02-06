"""
E2E tests for post-related functionality.
"""

import re
import uuid

import pytest
from playwright.sync_api import expect

from tests.e2e.helpers.database_helpers import (
    create_test_comment,
    create_test_post,
    get_comment_by_id,
    get_comment_for_post,
    get_post_by_title,
    get_post_by_url_id,
    get_post_views,
    get_user_points,
)
from tests.e2e.pages.base_page import BasePage
from tests.e2e.pages.create_post_page import CreatePostPage
from tests.e2e.pages.login_page import LoginPage
from tests.e2e.pages.post_page import PostPage


def _suffix() -> str:
    return uuid.uuid4().hex[:8]


def _valid_abstract(seed: str) -> str:
    return (f"Abstract for {seed}. " + ("A" * 170))[:180]


def _valid_content(seed: str) -> str:
    return f"Content for {seed}. " + ("B" * 140)


def _login(page, flask_server, username: str, password: str):
    login_page = LoginPage(page, flask_server["base_url"])
    login_page.navigate("/login/redirect=&")
    login_page.login(username, password)
    page.wait_for_url("**/", timeout=5000)


def _get_csrf_token(page) -> str:
    token = page.locator('input[name="csrf_token"]').first.get_attribute("value")
    assert token is not None and token != ""
    return token


class TestCreatePostAccess:
    """Tests for create-post access and rendering."""

    @pytest.mark.auth
    def test_create_post_requires_login(self, page, flask_server):
        """Unauthenticated users should be redirected to login for /create-post."""
        create_post_page = CreatePostPage(page, flask_server["base_url"])
        create_post_page.navigate()

        expect(page).to_have_url(
            re.compile(rf"^{re.escape(flask_server['base_url'])}/login/.*$"),
            timeout=10000,
        )

    @pytest.mark.smoke
    @pytest.mark.auth
    def test_create_post_page_renders_for_logged_in_user(
        self, logged_in_page, flask_server
    ):
        """Authenticated users can load the create-post page."""
        create_post_page = CreatePostPage(logged_in_page, flask_server["base_url"])
        create_post_page.navigate()
        create_post_page.expect_page_loaded()


class TestCreatePostFlow:
    """Tests for post creation success and errors."""

    @pytest.mark.smoke
    @pytest.mark.auth
    def test_create_post_with_valid_data_persists_in_database(
        self, page, flask_server, test_user, db_path
    ):
        """Valid create-post submission should save a new post and award points."""
        db_path_str = str(db_path)
        _login(page, flask_server, test_user.username, test_user.password)

        points_before = get_user_points(db_path_str, test_user.username)
        assert points_before is not None

        seed = _suffix()
        post_title = f"E2E Post {seed}"

        create_post_page = CreatePostPage(page, flask_server["base_url"])
        create_post_page.navigate()
        create_post_page.create_post(
            title=post_title,
            tags="e2e,test,post",
            abstract=_valid_abstract(seed),
            content=_valid_content(seed),
            category="Technology",
        )

        page.wait_for_url("**/", timeout=5000)
        create_post_page.expect_success_flash()

        post = get_post_by_title(db_path_str, post_title)
        assert post is not None, "Created post should exist in database"
        assert post["author"] == test_user.username
        assert post["category"] == "Technology"
        assert post["views"] == 0

        points_after = get_user_points(db_path_str, test_user.username)
        assert points_after == points_before + 20

    @pytest.mark.auth
    def test_create_post_with_empty_content_shows_error(
        self, page, flask_server, test_user, db_path
    ):
        """Submitting create-post with empty content should fail and not create a post."""
        db_path_str = str(db_path)
        _login(page, flask_server, test_user.username, test_user.password)

        seed = _suffix()
        post_title = f"Invalid Empty Content Post {seed}"

        create_post_page = CreatePostPage(page, flask_server["base_url"])
        create_post_page.navigate()
        create_post_page.fill_title(post_title)
        create_post_page.fill_tags("invalid,e2e")
        create_post_page.fill_abstract(_valid_abstract(seed))
        create_post_page.fill_content("")
        create_post_page.select_category("Technology")
        create_post_page.click_submit()

        create_post_page.expect_error_flash()
        post = get_post_by_title(db_path_str, post_title)
        assert post is None, "Post should not be created when content is empty"


class TestPostRoutingAndViews:
    """Tests for post routing and view counting behavior."""

    @pytest.mark.auth
    def test_post_url_redirects_to_canonical_slug(self, page, flask_server, db_path):
        """Visiting /post/<url_id> should redirect to /post/<slug>-<url_id>."""
        seed = _suffix()
        post = create_test_post(
            db_path=str(db_path),
            title=f"Canonical URL Post {seed}",
            content=_valid_content(seed),
            abstract=_valid_abstract(seed),
        )

        page.goto(f"{flask_server['base_url']}/post/{post['url_id']}")
        expect(page).to_have_url(
            re.compile(
                rf"^{re.escape(flask_server['base_url'])}/post/.+-{re.escape(post['url_id'])}/?$"
            ),
            timeout=10000,
        )

    @pytest.mark.auth
    def test_post_views_increment_when_post_is_opened(
        self, page, flask_server, db_path
    ):
        """Opening a post should increment its views by 1."""
        seed = _suffix()
        post = create_test_post(
            db_path=str(db_path),
            title=f"Views Counter Post {seed}",
            content=_valid_content(seed),
            abstract=_valid_abstract(seed),
            views=7,
        )

        post_page = PostPage(page, flask_server["base_url"])
        post_page.navigate(post["url_id"])
        post_page.expect_page_loaded()

        updated_views = get_post_views(str(db_path), post["url_id"])
        assert updated_views == 8
        assert post_page.get_views_count() == 8


class TestPostComments:
    """Tests for post comment behavior."""

    @pytest.mark.auth
    def test_logged_in_user_can_comment_on_post(
        self, page, flask_server, test_user, db_path
    ):
        """Authenticated user can comment on a post and comment is persisted."""
        seed = _suffix()
        post = create_test_post(
            db_path=str(db_path),
            title=f"Commentable Post {seed}",
            content=_valid_content(seed),
            abstract=_valid_abstract(seed),
            author="admin",
        )

        _login(page, flask_server, test_user.username, test_user.password)

        post_page = PostPage(page, flask_server["base_url"])
        post_page.navigate(post["url_id"])
        post_page.expect_page_loaded()

        comment_text = f"This is a valid E2E comment {seed} with enough characters."
        post_page.add_comment(comment_text)

        base_page = BasePage(page, flask_server["base_url"])
        base_page.expect_success_flash()
        page.wait_for_url("**/post/**", timeout=5000)
        post_page.expect_comment_visible(comment_text)

        stored_post = get_post_by_url_id(str(db_path), post["url_id"])
        assert stored_post is not None

        stored_comment = get_comment_for_post(
            db_path=str(db_path),
            post_id=stored_post["id"],
            comment_text=comment_text,
        )
        assert stored_comment is not None, "Comment should be saved in database"
        assert stored_comment["username"] == test_user.username


class TestPostEditAndDelete:
    """Tests for post edit and delete authorization/behavior."""

    @pytest.mark.auth
    def test_author_can_edit_own_post(self, page, flask_server, test_user, db_path):
        """Post author can edit their own post."""
        seed = _suffix()
        post = create_test_post(
            db_path=str(db_path),
            title=f"Editable Post {seed}",
            content=_valid_content(seed),
            abstract=_valid_abstract(seed),
            author=test_user.username,
        )

        _login(page, flask_server, test_user.username, test_user.password)

        editor_page = CreatePostPage(page, flask_server["base_url"])
        editor_page.navigate(f"/edit-post/{post['url_id']}")
        editor_page.expect_page_loaded()

        updated_seed = _suffix()
        updated_title = f"Updated Post {updated_seed}"
        updated_abstract = _valid_abstract(updated_seed)
        updated_content = _valid_content(updated_seed)
        editor_page.create_post(
            title=updated_title,
            tags="updated,e2e,post",
            abstract=updated_abstract,
            content=updated_content,
            category="Science",
        )

        expect(page).to_have_url(
            re.compile(rf"^{re.escape(flask_server['base_url'])}/post/.*$"),
            timeout=10000,
        )

        updated_post = get_post_by_url_id(str(db_path), post["url_id"])
        assert updated_post is not None
        assert updated_post["title"] == updated_title
        assert updated_post["tags"] == "updated,e2e,post"
        assert updated_post["category"] == "Science"
        assert updated_post["abstract"] == updated_abstract

    @pytest.mark.auth
    def test_non_author_cannot_edit_post(self, page, flask_server, test_user, db_path):
        """Non-author user should be redirected away from edit-post page."""
        seed = _suffix()
        post = create_test_post(
            db_path=str(db_path),
            title=f"Admin Owned Post {seed}",
            content=_valid_content(seed),
            abstract=_valid_abstract(seed),
            author="admin",
        )

        _login(page, flask_server, test_user.username, test_user.password)
        page.goto(f"{flask_server['base_url']}/edit-post/{post['url_id']}")

        page.wait_for_url("**/", timeout=5000)
        assert "/edit-post/" not in page.url

        base_page = BasePage(page, flask_server["base_url"])
        base_page.expect_error_flash()

    @pytest.mark.auth
    def test_author_can_delete_own_post(self, page, flask_server, test_user, db_path):
        """Post author can delete their own post from the post page."""
        seed = _suffix()
        post = create_test_post(
            db_path=str(db_path),
            title=f"Deletable Post {seed}",
            content=_valid_content(seed),
            abstract=_valid_abstract(seed),
            author=test_user.username,
        )

        _login(page, flask_server, test_user.username, test_user.password)

        post_page = PostPage(page, flask_server["base_url"])
        post_page.navigate(post["url_id"])
        post_page.expect_page_loaded()
        post_page.delete_post()

        page.wait_for_url("**/", timeout=5000)
        deleted_post = get_post_by_url_id(str(db_path), post["url_id"])
        assert deleted_post is None, "Post should be deleted from database"


class TestPostAuthorizationEdgeCases:
    """Tests for permission checks on forged post/comment deletion requests."""

    @pytest.mark.auth
    def test_non_author_cannot_delete_post_via_forged_request(
        self, page, flask_server, test_user, db_path
    ):
        """Non-author should not be able to delete a post by forging POST payload."""
        seed = _suffix()
        post = create_test_post(
            db_path=str(db_path),
            title=f"Protected Post {seed}",
            content=_valid_content(seed),
            abstract=_valid_abstract(seed),
            author="admin",
        )

        _login(page, flask_server, test_user.username, test_user.password)

        post_page = PostPage(page, flask_server["base_url"])
        post_page.navigate(post["url_id"])
        post_page.expect_page_loaded()

        csrf_token = _get_csrf_token(page)
        canonical_url = page.url

        response = page.request.post(
            canonical_url,
            form={
                "csrf_token": csrf_token,
                "post_delete_button": "1",
            },
        )
        assert response.ok

        page.goto(canonical_url)
        protected_post = get_post_by_url_id(str(db_path), post["url_id"])
        assert protected_post is not None, "Post must remain when deleted by non-author"

    @pytest.mark.auth
    def test_non_owner_cannot_delete_comment_via_forged_request(
        self, page, flask_server, test_user, db_path
    ):
        """Non-owner should not be able to delete another user's comment by forging POST payload."""
        seed = _suffix()
        post = create_test_post(
            db_path=str(db_path),
            title=f"Comment Protected Post {seed}",
            content=_valid_content(seed),
            abstract=_valid_abstract(seed),
            author="admin",
        )

        saved_post = get_post_by_url_id(str(db_path), post["url_id"])
        assert saved_post is not None

        comment_text = f"Admin owned comment {seed} with enough text to be realistic."
        comment_id = create_test_comment(
            db_path=str(db_path),
            post_id=saved_post["id"],
            comment=comment_text,
            username="admin",
        )

        _login(page, flask_server, test_user.username, test_user.password)

        post_page = PostPage(page, flask_server["base_url"])
        post_page.navigate(post["url_id"])
        post_page.expect_page_loaded()
        post_page.expect_comment_visible(comment_text)

        csrf_token = _get_csrf_token(page)
        canonical_url = page.url

        response = page.request.post(
            canonical_url,
            form={
                "csrf_token": csrf_token,
                "comment_delete_button": "1",
                "comment_id": str(comment_id),
            },
        )
        assert response.ok

        page.goto(canonical_url)
        protected_comment = get_comment_by_id(str(db_path), comment_id)
        assert protected_comment is not None, (
            "Comment must remain when deleted by non-owner"
        )
