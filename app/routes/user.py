"""
This module contains the route for viewing user profiles.
"""

import sqlite3

from flask import Blueprint, render_template

from settings import Settings
from utils.log import Log

user_blueprint = Blueprint("user", __name__)


@user_blueprint.route("/user/<username>")
def user(username):
    """
    This function is used to render the user page.

    :param username: The username of the user.
    :type username: str
    :return: The rendered user page.
    :rtype: flask.Response
    """
    username = username.lower()
    Log.database(f"Connecting to '{Settings.DB_USERS_ROOT}' database")
    connection = sqlite3.connect(Settings.DB_USERS_ROOT)
    connection.set_trace_callback(Log.database)
    cursor = connection.cursor()
    cursor.execute("select username from users")
    users = cursor.fetchall()
    """
    This if statement checks if the given username exists in the database.
    If the username exists, the function fetches the user details and the number of views their posts have received.
    It also fetches all the posts made by the user and all the comments made by the user.
    """
    if username in str(users).lower():
        Log.success(f'User: "{username}" found')
        cursor.execute(
            """select * from users where lower(username) = ? """,
            [(username)],
        )
        user = cursor.fetchone()
        Log.database(f"Connecting to '{Settings.DB_POSTS_ROOT}' database")
        connection = sqlite3.connect(Settings.DB_POSTS_ROOT)
        connection.set_trace_callback(Log.database)
        cursor = connection.cursor()
        cursor.execute(
            """select views from posts where author = ? order by time_stamp desc""",
            [(user[1])],
        )
        views_data = cursor.fetchall()
        views = 0
        for view in views_data:
            views += int(view[0])
        cursor.execute(
            """select * from posts where author = ? order by time_stamp desc""",
            [(user[1])],
        )
        posts = cursor.fetchall()
        connection = sqlite3.connect(Settings.DB_COMMENTS_ROOT)
        connection.set_trace_callback(Log.database)
        cursor = connection.cursor()
        cursor.execute(
            """select * from comments where lower(user) = ? """,
            [(username.lower())],
        )
        comments = cursor.fetchall()
        """
        This if statement checks if the user has any posts or comments.
        If the user has any posts, the variable show_posts is set to True.
        If the user has any comments, the variable show_comments is set to True.
        """
        if posts == []:
            show_posts = False
        else:
            show_posts = True
        if comments == []:
            show_comments = False
        else:
            show_comments = True
        Log.success(f'User: "{username}"s data loaded')
        return render_template(
            "user.html",
            user=user,
            views=views,
            posts=posts,
            comments=comments,
            show_posts=show_posts,
            show_comments=show_comments,
        )
    else:
        Log.error(f'User: "{username}" not found')
        return render_template("not_found.html")
