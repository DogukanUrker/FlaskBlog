import sqlite3

from settings import Settings
from utils.log import Log


def add_points(points, user):
    """
    Adds the specified number of points to the user with the specified username.
    """
    Log.database(f"Connecting to '{Settings.DB_USERS_ROOT}' database")
    connection = sqlite3.connect(Settings.DB_USERS_ROOT)
    connection.set_trace_callback(Log.database)
    cursor = connection.cursor()
    cursor.execute(
        """update users set points = points+? where username = ? """,
        [(points), (user)],
    )
    connection.commit()
    Log.info(f'{points} points added to "{user}"')
