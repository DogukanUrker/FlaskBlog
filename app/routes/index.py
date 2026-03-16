"""
This file contains the routes for the Flask application.

The Blueprint "index" is used to define the home page of the application.
The route "/" maps the index function to the home page.

The index function retrieves all posts from the database and passes them to the index.html template.

The posts variable is passed to the index.html template as a list of dictionaries.

The index.html template displays the title and content of each post.
"""

from json import load

from flask import Blueprint, redirect, render_template, session

from models import Post
from utils.log import Log
from utils.paginate import paginate_query

index_blueprint = Blueprint("index", __name__)


@index_blueprint.route("/")
@index_blueprint.route("/by=<by>/sort=<sort>")
def index(by="hot", sort="desc"):
    if "username" not in session:
        return redirect("/login/redirect=&")

    user = User.query.filter_by(username=session["username"]).first()
    if not user:
        return redirect("/login/redirect=&")

    by_options = [
        "time_stamp",
        "title",
        "views",
        "category",
        "last_edit_time_stamp",
        "hot",
    ]
    sort_options = ["asc", "desc"]

    if by not in by_options or sort not in sort_options:
        Log.warning(
            f"The provided sorting options are not valid: By: {by} Sort: {sort}"
        )
        return redirect("/")

    if by == "hot":
        if sort == "desc":
            query = Post.query.order_by(Post.hot_score.desc())
        else:
            query = Post.query.order_by(Post.hot_score.asc())
    else:
        sort_field = getattr(Post, by)
        if sort == "desc":
            query = Post.query.order_by(sort_field.desc())
        else:
            query = Post.query.order_by(sort_field.asc())

    posts_objects, page, total_pages = paginate_query(query)

    posts = [
        (
            p.id,
            p.title,
            p.tags,
            p.content,
            p.banner,
            p.author,
            p.views,
            p.time_stamp,
            p.last_edit_time_stamp,
            p.category,
            p.url_id,
            p.abstract,
        )
        for p in posts_objects
    ]

    display_by = by
    if by == "time_stamp":
        display_by = "create"
    elif by == "last_edit_time_stamp":
        display_by = "edit"

    language = session.get("language")
    translation_file = f"./translations/{language}.json"
    with open(translation_file, "r", encoding="utf-8") as file:
        translations = load(file)

    translations = translations["sort_menu"]

    sort_name = translations[display_by] + " - " + translations[sort]

    Log.info(f"Sorting posts on index page by: {sort_name}")

    return render_template(
        "index.html",
        posts=posts,
        sort_name=sort_name,
        source="",
        page=page,
        total_pages=total_pages,
    )
