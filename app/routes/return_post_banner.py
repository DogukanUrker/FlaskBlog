import sqlite3
from io import BytesIO

from flask import Blueprint, request, send_file

from settings import Settings
from utils.log import Log

return_post_banner_blueprint = Blueprint("return_post_banner", __name__)


@return_post_banner_blueprint.route("/post-image/<int:post_id>")
def return_post_banner(post_id):
    """
    This function returns the banner image for a given post ID.

    Args:
        post_id (int): The ID of the post for which the banner image is requested.

    Returns:
        The banner image for the given post ID as a Flask Response object.

    """
    Log.database(f"Connecting to '{Settings.DB_POSTS_ROOT}' database")

    connection = sqlite3.connect(Settings.DB_POSTS_ROOT)
    connection.set_trace_callback(Log.database)

    cursor = connection.cursor()

    cursor.execute(
        """select banner from posts where id = ? """,
        [(post_id)],
    )

    image = BytesIO(cursor.fetchone()[0])

    Log.info(f"Post: {post_id} | Image: {request.base_url} loaded")

    return send_file(image, mimetype="image/png")
