import sqlite3

from flask import redirect, session
from settings import Settings
from utils.log import Log


def change_user_role(username):
    """
    Changes the role of the user with the specified username.
    """
    username = username.lower()
    Log.database(f"Connecting to '{Settings.DB_USERS_ROOT}' database")
    connection = sqlite3.connect(Settings.DB_USERS_ROOT)
    connection.set_trace_callback(Log.database)
    cursor = connection.cursor()
    cursor.execute(
        """select role from users where lower(username) = ? """,
        [(username)],
    )
    role = cursor.fetchone()[0]
    if role == "admin":
        new_role = "user"
    elif role == "user":
        new_role = "admin"
    cursor.execute(
        """update users set role = ? where lower(username) = ? """,
        [(new_role), (username)],
    )
    Log.success(
        f'Admin: "{session["username"]}" changed user: "{username}"s role to "{new_role}" ',
    )
    connection.commit()
    if session["username"].lower() == username:
        Log.success(f'Admin: "{session["username"]}" changed his role to "user"')
        return redirect("/")
