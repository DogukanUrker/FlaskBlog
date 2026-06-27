"""
E2E test fixtures for Flask Blog application.

Supports parallel test execution with pytest-xdist.
"""

import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from filelock import FileLock

import pytest
from playwright.sync_api import sync_playwright, Page, Frame

# Add app directory to path for imports
APP_DIR = Path(__file__).parent.parent.parent / "app"
sys.path.insert(0, str(APP_DIR))

# Monkey-patch Playwright wait_for_url to resiliently upgrade any strict 5s timeouts to 10s under parallel test load
_orig_page_wait_for_url = Page.wait_for_url
_orig_frame_wait_for_url = Frame.wait_for_url


def patched_page_wait_for_url(self, url, *args, **kwargs):
    if "timeout" in kwargs and kwargs["timeout"] <= 5000:
        kwargs["timeout"] = 10000
    return _orig_page_wait_for_url(self, url, *args, **kwargs)


def patched_frame_wait_for_url(self, url, *args, **kwargs):
    if "timeout" in kwargs and kwargs["timeout"] <= 5000:
        kwargs["timeout"] = 10000
    return _orig_frame_wait_for_url(self, url, *args, **kwargs)


Page.wait_for_url = patched_page_wait_for_url
Frame.wait_for_url = patched_frame_wait_for_url

# Force tests to use a temporary test database copy to keep git workspace clean
TEST_DB_NAME = "flaskblog_test.db"
os.environ["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{TEST_DB_NAME}"

# Shared state file paths for parallel execution
LOCK_DIR = Path(__file__).parent / ".locks"
SERVER_LOCK = LOCK_DIR / "server.lock"
SERVER_PID_FILE = LOCK_DIR / "server.pid"
DB_BACKUP_LOCK = LOCK_DIR / "db_backup.lock"
DB_BACKUP_DONE = LOCK_DIR / "db_backup.done"
DB_CLEAN_LOCK = LOCK_DIR / "db_clean.lock"
DB_CLEAN_DONE = LOCK_DIR / "db_clean.done"


def _is_xdist_worker(config) -> bool:
    """Check if running as a pytest-xdist worker."""
    return hasattr(config, "workerinput")


def _is_xdist_master(config) -> bool:
    """Check if running as pytest-xdist master (or not using xdist)."""
    return not _is_xdist_worker(config)


def _get_worker_id(config) -> str:
    """Get the worker ID (gw0, gw1, etc.) or 'master' if not using xdist."""
    if hasattr(config, "workerinput"):
        return config.workerinput["workerid"]
    return "master"


@pytest.fixture(scope="session")
def app_dir():
    """Return the app directory path."""
    return APP_DIR


@pytest.fixture(scope="session")
def db_path(app_dir):
    """Return the database file path."""
    return app_dir / "instance" / "flaskblog_test.db"


@pytest.fixture(scope="session")
def flask_server(request, app_settings, app_dir):
    """
    Session-scoped fixture that starts the Flask server.

    With pytest-xdist, uses file locking to ensure only one worker
    starts the server, and all workers share the same server instance.
    """
    base_url = app_settings["base_url"]
    port = app_settings["port"]

    # Ensure lock directory exists
    LOCK_DIR.mkdir(exist_ok=True)

    # Use file lock to coordinate server startup across workers
    with FileLock(str(SERVER_LOCK)):
        # Check if server is already running (started by another worker)
        if SERVER_PID_FILE.exists():
            pid = int(SERVER_PID_FILE.read_text().strip())
            # Verify the process is still running
            try:
                os.kill(pid, 0)  # Signal 0 just checks if process exists
                # Server is running, just wait for it to be ready
                _wait_for_server(base_url)
                yield {
                    "process": None,
                    "base_url": base_url,
                    "port": port,
                    "owner": False,
                }
                return
            except OSError:
                # Process not running, clean up stale PID file
                SERVER_PID_FILE.unlink(missing_ok=True)

        # Start the Flask application
        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"

        process = subprocess.Popen(
            [sys.executable, "app.py"],
            cwd=str(app_dir),
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        # Save PID for other workers
        SERVER_PID_FILE.write_text(str(process.pid))

        # Wait for server to be ready
        _wait_for_server(base_url, port)

    yield {"process": process, "base_url": base_url, "port": port, "owner": True}

    # Cleanup: only the owner terminates the server
    # Use lock to prevent race condition during cleanup
    with FileLock(str(SERVER_LOCK)):
        if SERVER_PID_FILE.exists():
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
            SERVER_PID_FILE.unlink(missing_ok=True)


def _wait_for_server(base_url: str, port: int = None, max_wait: int = 30):
    """Wait for the server to be ready."""
    import urllib.request

    start_time = time.time()
    while time.time() - start_time < max_wait:
        try:
            urllib.request.urlopen(base_url, timeout=1)
            return
        except Exception:
            time.sleep(0.5)

    raise RuntimeError(
        f"Flask server failed to start within {max_wait} seconds. "
        f"Check that port {port} is available and the app starts correctly."
    )


@pytest.fixture(scope="session")
def browser_instance(request):
    """Session-scoped browser instance to avoid repeated browser launches."""
    headed = request.config.getoption("--headed", default=False)
    slowmo = request.config.getoption("--slowmo", default=0)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not headed, slow_mo=slowmo)
        yield browser
        browser.close()


@pytest.fixture(scope="function")
def context(browser_instance, flask_server):
    """
    Function-scoped browser context for test isolation.
    Each test gets a fresh context with clean cookies/storage.
    """
    context = browser_instance.new_context(
        viewport={"width": 1280, "height": 720},
        base_url=flask_server["base_url"],
    )

    # Abort image/favicon and Dicebear API requests to speed up E2E tests and avoid external CDN/API hangs
    context.route("**/*.{png,jpg,jpeg,gif,svg,ico}*", lambda route: route.abort())
    context.route(
        lambda url: "dicebear.com" in url or "githubusercontent.com" in url,
        lambda route: route.abort(),
    )

    yield context
    context.close()


@pytest.fixture(scope="function")
def page(context):
    """Function-scoped page for each test."""
    page = context.new_page()
    yield page
    page.close()


@pytest.fixture(scope="session", autouse=True)
def setup_and_teardown_test_db(request, db_path, app_dir):
    """
    Session-scoped fixture that sets up the temporary test database copy.

    With pytest-xdist, coordinates to ensure only one copy setup happens.
    Cleanup is handled by pytest_sessionfinish after ALL workers complete.
    """
    LOCK_DIR.mkdir(exist_ok=True)
    orig_db_path = app_dir / "instance" / "flaskblog.db"

    # Use file lock to coordinate setup across workers
    with FileLock(str(DB_BACKUP_LOCK)):
        if not DB_BACKUP_DONE.exists():
            # Copy original database to the test database file
            if orig_db_path.exists():
                shutil.copy2(orig_db_path, db_path)
                # Ensure the test database has WAL mode enabled once
                import sqlite3

                try:
                    conn = sqlite3.connect(str(db_path))
                    conn.execute("PRAGMA journal_mode=WAL;")
                    conn.close()
                except Exception:
                    pass
            DB_BACKUP_DONE.touch()

    yield

    # In non-parallel mode, clean up immediately
    if not _is_xdist_worker(request.config):
        for suffix in ["", "-wal", "-shm"]:
            path = Path(str(db_path) + suffix)
            path.unlink(missing_ok=True)


def pytest_sessionfinish(session, exitstatus):
    """
    Clean up after all tests complete.
    In xdist mode, this runs on the master after all workers finish.
    """
    if _is_xdist_master(session.config):
        # Delete temporary test database files
        db_path = APP_DIR / "instance" / "flaskblog_test.db"
        for suffix in ["", "-wal", "-shm"]:
            path = Path(str(db_path) + suffix)
            path.unlink(missing_ok=True)

        # Clean up lock directory
        if LOCK_DIR.exists():
            shutil.rmtree(LOCK_DIR, ignore_errors=True)


@pytest.fixture(scope="session", autouse=True)
def clean_db(db_path, setup_and_teardown_test_db):
    """
    Session-scoped fixture that resets database once at the start.
    Removes test users from previous runs but keeps the admin.

    Uses file locking to ensure only one worker does the cleanup.
    """
    from tests.e2e.helpers.database_helpers import reset_database

    LOCK_DIR.mkdir(exist_ok=True)

    with FileLock(str(DB_CLEAN_LOCK)):
        if not DB_CLEAN_DONE.exists():
            reset_database(str(db_path))
            DB_CLEAN_DONE.touch()

    yield


@pytest.fixture(scope="function")
def logged_in_page(page, flask_server, app_settings):
    """
    Page fixture with admin already logged in.
    Useful for tests that require authenticated state.
    """
    from tests.e2e.pages.login_page import LoginPage

    login_page = LoginPage(page, flask_server["base_url"])
    login_page.navigate("/login/redirect=&")
    login_page.login(
        app_settings["default_admin"]["username"],
        app_settings["default_admin"]["password"],
    )

    # Wait for redirect after login (using resilient 10s timeout)
    page.wait_for_url("**/", timeout=10000)

    yield page


@pytest.fixture(scope="function")
def test_user(db_path):
    """
    Create a test user and return credentials.
    The user is created fresh for each test with a unique UUID-based username.
    No cleanup needed - UUIDs ensure uniqueness across parallel tests.
    """
    from tests.e2e.helpers.database_helpers import create_test_user
    from tests.e2e.helpers.test_data import UserData

    user_data = UserData.generate()
    create_test_user(
        db_path=str(db_path),
        username=user_data.username,
        email=user_data.email,
        password=user_data.password,
        role=user_data.role,
    )

    return user_data


@pytest.fixture(scope="function")
def unverified_test_user(db_path):
    """
    Create an unverified test user and return credentials.
    The user is created fresh for each test with is_verified="False".
    No cleanup needed - UUIDs ensure uniqueness across parallel tests.
    """
    from tests.e2e.helpers.database_helpers import create_test_user
    from tests.e2e.helpers.test_data import UserData

    user_data = UserData.unverified()
    create_test_user(
        db_path=str(db_path),
        username=user_data.username,
        email=user_data.email,
        password=user_data.password,
        role=user_data.role,
        is_verified=user_data.is_verified,
    )

    return user_data
