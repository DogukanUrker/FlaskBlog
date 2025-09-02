"""
This module contains the route for category pages.

DISCLAIMER: This code is the property of the repository owner and is not intended for
use without explicit permission from the owner. The code is provided as-is and is
subject to change without notice. Use of this code for commercial or non-commercial
purposes without permission is strictly prohibited.
"""

from json import load

from flask import Blueprint, abort, redirect, render_template, session

from settings import Settings
from utils.log import Log
from utils.paginate import paginate_query

category_blueprint = Blueprint("category", __name__)


@category_blueprint.route("/category/<category>")
@category_blueprint.route("/category/<category>/by=<by>/sort=<sort>")
def category(category, by="time_stamp", sort="desc"):
    """
    This function handles requests for the category route.

    :param category: The category name that is requested
    :param by: The field to sort the posts by
    :param sort: The sorting order of the posts
    :return: A rendered template with the posts and the category as context
    """

    categories = [
        "games",
        "history",
        "science",
        "code",
        "technology",
        "education",
        "sports",
        "foods",
        "health",
        "apps",
        "movies",
        "series",
        "travel",
        "books",
        "music",
        "nature",
        "art",
        "finance",
        "business",
        "web",
        "other",
    ]

    by_options = ["time_stamp", "title", "views", "category", "last_edit_time_stamp"]
    sort_options = ["asc", "desc"]

    if by not in by_options or sort not in sort_options:
        Log.warning(
            f"The provided sorting options are not valid: By: {by} Sort: {sort}"
        )
        return redirect(f"/category/{category}")

    if category.lower() not in categories:
        abort(404)

    posts, page, total_pages = paginate_query(
        Settings.DB_POSTS_ROOT,
        "select count(*) from posts where lower(category) = ?",
        f"select * from posts where lower(category) = ? order by {by} {sort}",
        [category.lower()],
    )

    if by == "time_stamp":
        by = "create"
    elif by == "last_edit_time_stamp":
        by = "edit"

    language = session.get("language")
    translation_file = f"./translations/{language}.json"
    with open(translation_file, "r", encoding="utf-8") as file:
        translations = load(file)

    sort_name = translations["sort_menu"][by] + " - " + translations["sort_menu"][sort]

    Log.info(f"Sorting posts on category/{category} page by: {sort_name}")

    return render_template(
        "category.html",
        posts=posts,
        category=translations["categories"][category.lower()],
        sort_name=sort_name,
        source=f"/category/{category}",
        page=page,
        total_pages=total_pages,
    )
