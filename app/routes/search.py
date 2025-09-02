import sqlite3
from math import ceil

from flask import Blueprint, render_template, request

from settings import Settings
from utils.log import Log

search_blueprint = Blueprint("search", __name__)


@search_blueprint.route("/search/<query>", methods=["GET", "POST"])
def search(query):
    query = query.replace("%20", " ")
    query_no_white_space = query.replace("+", "")
    query = query.replace("+", " ")

    page = request.args.get("page", 1, type=int)
    per_page = 9

    Log.info(f"Searching for query: {query}")

    Log.database(f"Connecting to '{Settings.DB_USERS_ROOT}' database")

    connection = sqlite3.connect(Settings.DB_USERS_ROOT)
    connection.set_trace_callback(Log.database)
    cursor = connection.cursor()

    query_users = cursor.execute(
        """select * from users where username like ? """,
        [
            ("%" + query + "%"),
        ],
    ).fetchall()

    query_users = cursor.execute(
        """select * from users where username like ? """,
        [
            ("%" + query_no_white_space + "%"),
        ],
    ).fetchall()
    Log.database(f"Connecting to '{Settings.DB_POSTS_ROOT}' database")

    connection = sqlite3.connect(Settings.DB_POSTS_ROOT)
    connection.set_trace_callback(Log.database)
    cursor = connection.cursor()

    query_tags = cursor.execute(
        """select * from posts where tags like ? order by time_stamp desc""",
        [
            ("%" + query + "%"),
        ],
    ).fetchall()

    query_titles = cursor.execute(
        """select * from posts where title like ? order by time_stamp desc""",
        [
            ("%" + query + "%"),
        ],
    ).fetchall()

    query_authors = cursor.execute(
        """select * from posts where author like ? order by time_stamp desc""",
        [
            ("%" + query + "%"),
        ],
    ).fetchall()

    query_tags = cursor.execute(
        """select * from posts where tags like ? order by time_stamp desc""",
        [
            ("%" + query_no_white_space + "%"),
        ],
    ).fetchall()

    query_titles = cursor.execute(
        """select * from posts where title like ? order by time_stamp desc""",
        [
            ("%" + query_no_white_space + "%"),
        ],
    ).fetchall()

    query_authors = cursor.execute(
        """select * from posts where author like ? order by time_stamp desc""",
        [
            ("%" + query_no_white_space + "%"),
        ],
    ).fetchall()

    posts = []

    users = []

    empty = False

    if query_tags != []:
        posts.append(query_tags)

    if query_titles != []:
        posts.append(query_titles)

    if query_authors != []:
        posts.append(query_authors)

    if query_users != []:
        users.append(query_users)

    if not posts and not users:
        empty = True

    results_id = []

    for post in posts:
        for post in post:
            if post[0] not in results_id:
                results_id.append(post[0])

    posts = []

    for post_id in results_id:
        cursor.execute(
            """select * from posts where id = ? """,
            [(post_id)],
        )

        posts.append(cursor.fetchall())

    total_posts = len(posts)
    total_pages = max(ceil(total_posts / per_page), 1)
    offset = (page - 1) * per_page
    posts = posts[offset : offset + per_page]

    Log.info(
        f"Rendering search.html: params: query={query} | users={users} | posts={len(posts)} | empty={empty}"
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
