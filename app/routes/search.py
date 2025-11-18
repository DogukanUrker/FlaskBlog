import sqlite3
from math import ceil

from flask import Blueprint, render_template, request
from settings import Settings
from utils.log import Log

searchBlueprint = Blueprint("search", __name__)


@searchBlueprint.route("/search/<query>", methods=["GET"])
def search(query):
    # Decode URL-encoded query
    query = query.replace("%20", " ")
    queryNoWhiteSpace = query.replace("+", "").replace(" ", "")
    query = query.replace("+", " ")

    page = request.args.get("page", 1, type=int)
    per_page = 9

    Log.info(f"Searching for query: '{query}' (normalized: '{queryNoWhiteSpace}')")

    Log.database(f"Connecting to '{Settings.DB_USERS_ROOT}' database")

    userConnection = sqlite3.connect(Settings.DB_USERS_ROOT)
    userConnection.set_trace_callback(Log.database)
    userCursor = userConnection.cursor()

    # Search users by username (with and without whitespace)
    queryUsers = userCursor.execute(
        """SELECT * FROM Users WHERE userName LIKE ? OR userName LIKE ? """,
        ("%" + query + "%", "%" + queryNoWhiteSpace + "%"),
    ).fetchall()

    userConnection.close()
    Log.database(f"Connecting to '{Settings.DB_POSTS_ROOT}' database")

    postConnection = sqlite3.connect(Settings.DB_POSTS_ROOT)
    postConnection.set_trace_callback(Log.database)
    postCursor = postConnection.cursor()

    # Search posts by tags, title, or author (consolidated query)
    queryPosts = postCursor.execute(
        """SELECT * FROM posts
           WHERE tags LIKE ? OR tags LIKE ?
              OR title LIKE ? OR title LIKE ?
              OR author LIKE ? OR author LIKE ?
           ORDER BY timeStamp DESC""",
        (
            "%" + query + "%", "%" + queryNoWhiteSpace + "%",
            "%" + query + "%", "%" + queryNoWhiteSpace + "%",
            "%" + query + "%", "%" + queryNoWhiteSpace + "%"
        ),
    ).fetchall()

    # Remove duplicate posts (based on ID)
    seen_post_ids = set()
    unique_posts = []
    for post in queryPosts:
        if post[0] not in seen_post_ids:
            seen_post_ids.add(post[0])
            unique_posts.append([post])  # Wrap in list for template compatibility

    postConnection.close()

    # Organize results
    posts = unique_posts
    users = [queryUsers] if queryUsers else []
    empty = not posts and not users

    # Pagination
    total_posts = len(posts)
    total_pages = max(ceil(total_posts / per_page), 1)
    offset = (page - 1) * per_page
    posts = posts[offset : offset + per_page]

    Log.info(
        f"Rendering search.html: query='{query}' | users={len(users)} | posts={len(posts)} | total={total_posts} | empty={empty}"
    )

    return render_template(
        "search.html",
        posts=posts,
        users=users,
        query=query,
        empty=empty,
        page=page,
        total_pages=total_pages,
    )
