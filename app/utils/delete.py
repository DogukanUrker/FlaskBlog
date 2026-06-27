"""
This module contains the database delete functions for the app.

The functions in this module are responsible for managing the database
and interacting with the posts, users, and comments tables using SQLAlchemy.

The functions in this module are:

- delete_post(post_id): This function deletes a post and all associated comments
from the database.
- delete_user(username): This function deletes a user and all associated data
from the database.
- delete_comment(comment_id): This function deletes a comment from the database.
"""

from flask import redirect, session

from database import db
from models import Comment, Post, User
from utils.flash_message import flash_message
from utils.log import Log


def delete_post(post_id, username=None):
    """
    This function deletes a post and all associated comments from the database.

    Parameters:
    post_id (str): The ID of the post to be deleted.
    username (str): The username of the user requesting deletion (for authorization).

    Returns:
    bool: True if deleted, False if not authorized or not found
    """
    post = Post.query.get(post_id)

    if not post:
        Log.error(f'Post: "{post_id}" not found')
        return False

    user = User.query.filter_by(username=username).first() if username else None
    is_admin = user and user.role == "admin"
    is_author = username and post.author.lower() == username.lower()

    if not is_admin and not is_author:
        Log.error(
            f'User: "{username}" tried to delete post: "{post_id}" without authorization'
        )
        return False

    db.session.delete(post)
    db.session.commit()

    flash_message(
        page="delete",
        message="post",
        category="error",
        language=session.get("language", "en"),
    )
    Log.success(f'Post: "{post_id}" deleted by "{username}"')
    return True


def delete_user(target_username, perpetrator_username=None):
    """
    This function deletes a user and all associated data from the database.

    Authorization rules:
      - Non-admin users may only delete their own account.
      - Admins may delete any non-admin user.
      - Admins may delete another admin only if >= 2 admins remain after deletion.
      - No user (admin or not) may delete themselves via the admin panel
        (admin self-deletion is blocked at the account-settings page).

    Parameters:
    target_username (str): The username of the user to be deleted.
    perpetrator_username (str, optional): The username of the calling user,
        taken from session["username"]. If None, falls back to session.

    Returns:
    bool: True if deleted, False if unauthorized, not found, or blocked.
    """
    from sqlalchemy import func, text

    if perpetrator_username is None:
        perpetrator_username = session.get("username")

    target = User.query.filter(func.lower(User.username) == target_username.lower()).first()

    if not target:
        Log.error(f'User: "{target_username}" not found')
        return False

    perpetrator = User.query.filter_by(username=perpetrator_username).first()
    if not perpetrator:
        Log.error(f'Perpetrator: "{perpetrator_username}" not found')
        return False

    # Gate 1: Authorization
    is_admin = perpetrator.role == "admin"
    is_self = target.username.lower() == perpetrator.username.lower()

    if not is_admin and not is_self:
        Log.error(
            f'User: "{perpetrator_username}" (role={perpetrator.role}) '
            f'tried to delete user: "{target_username}" without authorization'
        )
        flash_message(
            page="delete",
            message="not_authorized",
            category="error",
            language=session.get("language", "en"),
        )
        return False

    # Gate 2: Last-admin guard — never let admin count drop to zero
    if target.role == "admin":
        admin_count = (
            db.session.query(func.count(User.user_id))
            .filter(User.role == "admin")
            .scalar()
        )
        if admin_count <= 1:
            Log.error(
                f'User: "{perpetrator_username}" tried to delete last admin: '
                f'"{target_username}" — would leave no admins'
            )
            flash_message(
                page="delete",
                message="last_admin",
                category="error",
                language=session.get("language", "en"),
            )
            return False

    db.session.delete(target)
    db.session.commit()

    flash_message(
        page="delete",
        message="user",
        category="error",
        language=session.get("language", "en"),
    )
    Log.success(f'User: "{target.username}" deleted by "{perpetrator.username}"')

    if is_self:
        session.clear()
        return redirect("/")
    else:
        return redirect("/admin/users")


def delete_comment(comment_id, username=None):
    """
    This function deletes a comment from the database.

    Parameters:
    comment_id (str): The ID of the comment to be deleted.
    username (str): The username of the user requesting deletion (for authorization).

    Returns:
    bool: True if deleted, False if not authorized or not found
    """
    comment = Comment.query.get(comment_id)

    if not comment:
        Log.error(f'Comment: "{comment_id}" not found')
        return False

    user = User.query.filter_by(username=username).first() if username else None
    is_admin = user and user.role == "admin"
    is_author = username and comment.username.lower() == username.lower()

    if not is_admin and not is_author:
        Log.error(
            f'User: "{username}" tried to delete comment: "{comment_id}" without authorization'
        )
        return False

    db.session.delete(comment)
    db.session.commit()

    flash_message(
        page="delete",
        message="comment",
        category="error",
        language=session.get("language", "en"),
    )
    Log.success(f'Comment: "{comment_id}" deleted by "{username}"')
    return True
