# Tests

End-to-end tests for Flask Blog using Pytest and Playwright.

## Quick Start

Use Make targets from the repository root:

```bash
make install       # Install app + dev + test deps and Playwright browser
make test          # Run all E2E tests (parallel)
make test-slow     # Run headed browser with slow-mo (sequential)
```

## Run Specific Tests

If you need targeted runs, execute pytest from `app/`:

```bash
cd app

# Full E2E suite (parallel by default via pytest.ini)
uv run pytest ../tests/e2e/ -v

# Specific domain
uv run pytest ../tests/e2e/post/ -v
uv run pytest ../tests/e2e/account/ -v

# Specific file / class / test
uv run pytest ../tests/e2e/auth/test_login.py -v
uv run pytest ../tests/e2e/auth/test_login.py::TestLoginSuccess -v
uv run pytest ../tests/e2e/post/test_post.py::TestPostComments::test_logged_in_user_can_comment_on_post -v
```

## Current Suite Coverage

Current local suite size: **110 tests** across **14 test files**.

| Suite | Files | Tests | Focus |
| ----- | ----- | ----- | ----- |
| `e2e/auth/` | 3 | 62 | Login, signup, logout, session handling |
| `e2e/account/` | 5 | 17 | Account settings, username/profile updates, password change flow, dashboard, static pages, preferences |
| `e2e/post/` | 1 | 14 | Create/edit/delete post, comments, authorization, admin moderation via protected POST flows |
| `e2e/admin/` | 1 | 8 | Admin access control, users (role + delete), comments management |
| `e2e/search/` | 2 | 6 | Search results and category filtering |
| `e2e/home/` | 1 | 3 | Home rendering and sorting routes |

Recently added high-impact coverage:

- Dashboard forged delete requests cannot remove posts owned by other users.
- Admin can delete users from `/admin/users`.
- Non-admin users are blocked from `/admin/comments`.
- Admin can delete other users' posts through the post route with valid CSRF.
- Admin can delete other users' comments through the post route with valid CSRF.

## Parallel Execution

Tests run in parallel by default using `pytest-xdist` (`-n auto` from `pytest.ini`).

```bash
cd app

# Override worker count
uv run pytest ../tests/e2e/ -n 4 -v

# Disable parallel
uv run pytest ../tests/e2e/ -n 0 -v

# Headed + slow motion for debugging
uv run pytest ../tests/e2e/ --headed --slowmo 500 -n 0 -v
```

Parallel behavior:

- One shared Flask server is started with file-lock coordination.
- Database is backed up before the session and restored at the end.
- UUID-based user data avoids collisions between workers.
- Each test gets an isolated browser context and page.

## Project Structure

```text
tests/
├── conftest.py                       # Root fixtures (markers, app_settings)
├── README.md
└── e2e/
    ├── conftest.py                   # Server, browser, DB coordination
    ├── account/
    │   ├── test_account_settings.py
    │   ├── test_change_password_flow.py
    │   ├── test_dashboard.py
    │   ├── test_profile_and_preferences.py
    │   └── test_static_pages.py
    ├── admin/
    │   └── test_admin.py
    ├── auth/
    │   ├── test_login.py
    │   ├── test_logout.py
    │   └── test_signup.py
    ├── home/
    │   └── test_home.py
    ├── post/
    │   └── test_post.py
    ├── search/
    │   ├── test_category.py
    │   └── test_search.py
    ├── helpers/
    │   ├── database_helpers.py
    │   └── test_data.py
    └── pages/
        ├── base_page.py
        ├── create_post_page.py
        ├── login_page.py
        ├── navbar_component.py
        ├── post_page.py
        └── signup_page.py
```

## Architecture

### Page Object Model

Page objects encapsulate UI interactions (`tests/e2e/pages/`), including:

- `LoginPage`
- `SignupPage`
- `CreatePostPage`
- `PostPage`
- `NavbarComponent`

Example:

```python
from tests.e2e.pages.create_post_page import CreatePostPage

def test_create_post(page, flask_server):
    create_post_page = CreatePostPage(page, flask_server["base_url"])
    create_post_page.navigate()
    create_post_page.expect_page_loaded()
```

### Key Fixtures

| Fixture | Scope | Purpose |
| ------- | ----- | ------- |
| `flask_server` | session | Starts/stops Flask app and shares it across workers |
| `browser_instance` | session | Single Chromium browser instance |
| `context` | function | Fresh isolated browser context per test |
| `page` | function | Fresh page per test |
| `clean_db` | session | One-time DB cleanup before tests |
| `test_user` | function | Creates unique UUID-based user |
| `unverified_test_user` | function | Creates unique unverified user |
| `logged_in_page` | function | Page pre-authenticated as default admin |

### Test Data Helpers

`UserData` factory:

```python
from tests.e2e.helpers.test_data import UserData

user = UserData.generate()
unverified = UserData.unverified()
```

Database helpers (`tests/e2e/helpers/database_helpers.py`) are used for test setup/assertions, for example:

```python
from tests.e2e.helpers.database_helpers import create_test_user, get_user_by_username

create_test_user(db_path, "testuser", "test@example.com", "Password123!")
assert get_user_by_username(db_path, "testuser") is not None
```

## Markers

Registered markers:

- `auth`
- `admin`
- `smoke`
- `slow`

Usage:

```bash
cd app
uv run pytest ../tests/e2e/ -m auth -v
uv run pytest ../tests/e2e/ -m smoke -v
uv run pytest ../tests/e2e/ -m "admin and not smoke" -v
uv run pytest ../tests/e2e/ -m "not slow" -v
```

## CI

E2E tests run in GitHub Actions (`.github/workflows/e2e-tests.yaml`) on:

- Push to `main` (when `app/**`, `tests/**`, or workflow file changes)
- Pull requests to `main`
- Manual dispatch (`workflow_dispatch`) with optional `test_path`
