import sqlite3

from settings import Settings
from utils.log import Log


def get_profile_picture(username):
    """
    Returns the profile picture of the user with the specified username.

    Parameters:
        username (str): The username of the user whose profile picture is to be retrieved.

    Returns:
        str or None: The profile picture URL of the user, or None if not found.
    """
    Log.database(f"Connecting to '{Settings.DB_USERS_ROOT}' database")

    connection = sqlite3.connect(Settings.DB_USERS_ROOT)
    connection.set_trace_callback(Log.database)

    cursor = connection.cursor()

    cursor.execute(
        """select profile_picture from users where lower(username) = ? """,
        [(username.lower())],
    )
    try:
        profile_picture = cursor.fetchone()[0]

        Log.info(f"Returning {username}'s profile picture: {profile_picture}")
    except Exception:
        profile_picture = None
        Log.error(f"Failed to retrieve profile picture for user: {username}")

    return profile_picture
