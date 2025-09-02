import sqlite3

from settings import Settings
from utils.log import Log


def get_post_url_id_from_post(post_id: int):
    """
    Returns the post's url_id from post's id.
    Args:
        post_id (int): The post's primary key/id whose url_id to be retrieved.

    Returns:
        str or None: The post's url_id of the post, or None if not found.
    """
    Log.database(f"Connecting to '{Settings.DB_POSTS_ROOT}' database")

    connection = sqlite3.connect(Settings.DB_POSTS_ROOT)
    connection.set_trace_callback(Log.database)

    cursor = connection.cursor()

    cursor.execute("""select url_id from posts where id = ?""", (post_id,))
    try:
        url_id = cursor.fetchone()[0]
        Log.info(f"Returning post's id {post_id} and post's url_id: {url_id}")
    except Exception:
        url_id = None
        Log.error(f"Failed to retrieve post's url_id for post id : {post_id}")

    cursor.close()
    connection.close()

    return url_id
