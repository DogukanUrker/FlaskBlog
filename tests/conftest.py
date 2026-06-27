"""
Root-level pytest configuration for Flask Blog tests.
"""

import os
import pytest
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "slow: marks tests as slow")
    config.addinivalue_line("markers", "auth: marks tests related to authentication")
    config.addinivalue_line("markers", "admin: marks tests requiring admin privileges")
    config.addinivalue_line("markers", "smoke: marks tests for smoke testing")


@pytest.fixture(scope="session")
def app_settings():
    """Session-scoped fixture with app configuration."""
    return {
        "base_url": "http://localhost:1283",
        "port": 1283,
        "default_admin": {
            "username": "admin",
            "password": os.environ.get("DEFAULT_ADMIN_PASSWORD", "admin"),
            "email": "admin@flaskblog.com",
        },
    }
