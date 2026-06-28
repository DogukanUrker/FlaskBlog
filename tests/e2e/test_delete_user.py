"""
Unit tests for the delete_user utility function to ensure authorization is enforced at the function level.
"""

from utils.delete import delete_user
from tests.e2e.helpers.database_helpers import create_test_user, get_user_by_username


def test_admin_cannot_delete_themselves(flask_server, db_path):
    """An admin should not be able to delete their own account via delete_user()."""
    from app import app

    username = "admin_self_delete"
    create_test_user(
        db_path=str(db_path),
        username=username,
        email=f"{username}@test.com",
        password="TestPassword123!",
        role="admin",
    )

    with app.test_request_context():
        from flask import session

        session["username"] = username

        result = delete_user(username)

        assert result is False
        user = get_user_by_username(str(db_path), username)
        assert user is not None


def test_non_admin_cannot_delete_other_user(flask_server, db_path):
    """A non-admin user should not be able to delete another user via delete_user()."""
    from app import app

    attacker = "attacker_user"
    create_test_user(
        db_path=str(db_path),
        username=attacker,
        email=f"{attacker}@test.com",
        password="TestPassword123!",
        role="user",
    )

    target = "target_user"
    create_test_user(
        db_path=str(db_path),
        username=target,
        email=f"{target}@test.com",
        password="TestPassword123!",
        role="user",
    )

    with app.test_request_context():
        from flask import session

        session["username"] = attacker

        result = delete_user(target)

        assert result is False
        user = get_user_by_username(str(db_path), target)
        assert user is not None


def test_non_admin_can_delete_themselves(flask_server, db_path):
    """A non-admin user should be able to delete their own account via delete_user()."""
    from app import app

    username = "self_delete_user"
    create_test_user(
        db_path=str(db_path),
        username=username,
        email=f"{username}@test.com",
        password="TestPassword123!",
        role="user",
    )

    with app.test_request_context():
        from flask import session

        session["username"] = username

        result = delete_user(username)

        assert result is True
        user = get_user_by_username(str(db_path), username)
        assert user is None


def test_admin_can_delete_other_user(flask_server, db_path):
    """An admin should be able to delete another user via delete_user()."""
    from app import app

    admin = "admin_deleter"
    create_test_user(
        db_path=str(db_path),
        username=admin,
        email=f"{admin}@test.com",
        password="TestPassword123!",
        role="admin",
    )

    target = "target_to_delete"
    create_test_user(
        db_path=str(db_path),
        username=target,
        email=f"{target}@test.com",
        password="TestPassword123!",
        role="user",
    )

    with app.test_request_context():
        from flask import session

        session["username"] = admin

        result = delete_user(target)

        assert result is True
        user = get_user_by_username(str(db_path), target)
        assert user is None


def test_admin_can_delete_other_admin(flask_server, db_path):
    """An admin should be able to delete another admin via delete_user()."""
    from app import app

    admin = "admin_deleter2"
    create_test_user(
        db_path=str(db_path),
        username=admin,
        email=f"{admin}@test.com",
        password="TestPassword123!",
        role="admin",
    )

    target_admin = "target_admin_to_delete"
    create_test_user(
        db_path=str(db_path),
        username=target_admin,
        email=f"{target_admin}@test.com",
        password="TestPassword123!",
        role="admin",
    )

    with app.test_request_context():
        from flask import session

        session["username"] = admin

        result = delete_user(target_admin)

        assert result is True
        user = get_user_by_username(str(db_path), target_admin)
        assert user is None
