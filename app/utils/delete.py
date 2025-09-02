"""
This module contains the database delete functions for the app.

The functions in this module are responsible for managing the database
and interacting with the posts, users, and comments tables.

The functions in this module are:

- delete_post(post_id): This function deletes a post and all associated comments
from the database.
- delete_user(username): This function deletes a user and all associated data
from the database.
- delete_comment(comment_id): This function deletes a comment from the database.

The functions in this module use the following helper functions:

- flash(message, category): This function flashes a message to the user.
- Log.{type}(message): This function sends a message to the server.
- session: This variable stores information about the current user's session.
- redirect(url): This function redirects the user to a new URL.
- DB_POSTS_ROOT: This variable stores the path to the posts database.
- DB_USERS_ROOT: This variable stores the path to the users database.
- DB_COMMENTS_ROOT: This variable stores the path to the comments database.
"""

import sqlite3

from flask import redirect, session
from settings import Settings
from utils.flash_message import flash_message
from utils.log import Log


def delete_post(post_id):
    """
    This function deletes a post and all associated comments from the database.

    Parameters:
    post_id (str): The ID of the post to be deleted.

    Returns:
    None
    """
    Log.database(f"Connecting to '{Settings.DB_POSTS_ROOT}' database")
    connection = sqlite3.connect(Settings.DB_POSTS_ROOT)
    connection.set_trace_callback(Log.database)
    cursor = connection.cursor()
    cursor.execute(
        """select username from posts where id = ? """,
        [(post_id)],
    )
    cursor.execute(
        """delete from posts where id = ? """,
        [(post_id)],
    )
    cursor.execute("update sqlite_sequence set seq = seq-1")
    connection.commit()
    connection.close()
    connection = sqlite3.connect(Settings.DB_COMMENTS_ROOT)
    connection.set_trace_callback(Log.database)
    cursor = connection.cursor()
    cursor.execute(
        """select count(*) from comments where post_id = ? """,
        [(post_id)],
    )
    comment_count = list(cursor)[0][0]
    cursor.execute(
        """delete from comments where post_id = ? """,
        [(post_id)],
    )
    cursor.execute(
        """update sqlite_sequence set seq = seq - ? """,
        [(comment_count)],
    )
    connection.commit()

    flash_message(
        page="delete",
        message="post",
        category="error",
        language=session["language"],
    )
    Log.success(f'Post: "{post_id}" deleted')


def delete_user(username):
    """
    This function deletes a user and all associated data from the database.

    Parameters:
    username (str): The username of the user to be deleted.

    Returns:
    None
    """
    Log.database(f"Connecting to '{Settings.DB_USERS_ROOT}' database")
    connection = sqlite3.connect(Settings.DB_USERS_ROOT)
    connection.set_trace_callback(Log.database)
    cursor = connection.cursor()
    cursor.execute(
        """select * from users where lower(username) = ? """,
        [(username.lower())],
    )
    cursor.execute(
        """select role from users where username = ? """,
        [(session["username"])],
    )
    perpetrator = cursor.fetchone()
    cursor.execute(
        """delete from users where lower(username) = ? """,
        [(username.lower())],
    )
    cursor.execute("update sqlite_sequence set seq = seq-1")
    connection.commit()
    flash_message(
        page="delete",
        message="user",
        category="error",
        language=session["language"],
    )
    Log.success(f'User: "{username}" deleted')
    if perpetrator[0] == "admin":
        return redirect("/admin/users")
    else:
        session.clear()
        return redirect("/")


def delete_comment(comment_id):
    """
    This function deletes a comment from the database.

    Parameters:
    comment_id (str): The ID of the comment to be deleted.

    Returns:
    None
    """
    connection = sqlite3.connect(Settings.DB_COMMENTS_ROOT)
    connection.set_trace_callback(Log.database)
    cursor = connection.cursor()
    cursor.execute(
        """select username from comments where id = ? """,
        [(comment_id)],
    )
    cursor.execute(
        """delete from comments where id = ? """,
        [(comment_id)],
    )
    cursor.execute("update sqlite_sequence set seq = seq-1")
    connection.commit()
    flash_message(
        page="delete",
        message="comment",
        category="error",
        language=session["language"],
    )
    Log.success(f'Comment: "{comment_id}" deleted')
