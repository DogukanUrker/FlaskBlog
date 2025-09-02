from flask import Blueprint, render_template

from utils.log import Log

search_bar_blueprint = Blueprint("search_bar", __name__)


@search_bar_blueprint.route("/search-bar")
def search_bar():
    """
    This function returns the search bar HTML page.

    Returns:
        The search bar HTML page.
    """

    Log.info("Rendering search_bar.html")
    return render_template("search_bar.html")
