import sqlite3
from io import BytesIO

from flask import Blueprint, request, send_file
from settings import Settings
from utils.defaultBanner import DefaultBanner
from utils.log import Log

returnPostBannerBlueprint = Blueprint("returnPostBanner", __name__)


@returnPostBannerBlueprint.route("/postImage/<int:postID>")
def returnPostBanner(postID):
    """
    This function returns the banner image for a given post ID.

    Args:
        postID (int): The ID of the post for which the banner image is requested.

    Returns:
        The banner image for the given post ID as a Flask Response object.

    """
    Log.database(f"Connecting to '{Settings.DB_POSTS_ROOT}' database")

    connection = sqlite3.connect(Settings.DB_POSTS_ROOT)
    connection.set_trace_callback(Log.database)

    cursor = connection.cursor()

    cursor.execute(
        """select banner from posts where id = ? """,
        [(postID)],
    )

    banner_data = cursor.fetchone()[0]

    # Use default banner if the post has no banner or empty banner
    if not banner_data or banner_data == b"":
        banner_data = DefaultBanner.get_cached_default_banner()
        Log.info(f"Post: {postID} | Using default banner")
    else:
        Log.info(f"Post: {postID} | Custom banner loaded")

    image = BytesIO(banner_data)

    return send_file(image, mimetype="image/png")
