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


def delete_user(username):
    """
    This function deletes a user and all associated data from the database.

    Parameters:
    username (str): The username of the user to be deleted.

    Returns:
    None
    """
    from sqlalchemy import func

    user = User.query.filter(func.lower(User.username) == username.lower()).first()

    if not user:
        Log.error(f'User: "{username}" not found')
        return redirect("/")

    perpetrator = User.query.filter_by(username=session["username"]).first()
    perpetrator_role = perpetrator.role if perpetrator else None

    db.session.delete(user)
    db.session.commit()

    flash_message(
        page="delete",
        message="user",
        category="error",
        language=session.get("language", "en"),
    )
    Log.success(f'User: "{username}" deleted')

    if perpetrator_role == "admin":
        return redirect("/admin/users")
    else:
        session.clear()
        return redirect("/")


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
