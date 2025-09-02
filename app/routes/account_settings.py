import sqlite3

from flask import Blueprint, redirect, render_template, request, session

from settings import Settings
from utils.delete import delete_user
from utils.log import Log

account_settings_blueprint = Blueprint("account_settings", __name__)


@account_settings_blueprint.route("/account-settings", methods=["GET", "POST"])
def account_settings():
    if "username" in session:
        Log.database(f"Connecting to '{Settings.DB_USERS_ROOT}' database")

        connection = sqlite3.connect(Settings.DB_USERS_ROOT)
        connection.set_trace_callback(Log.database)
        cursor = connection.cursor()
        cursor.execute(
            """select username from users where username = ? """,
            [(session["username"])],
        )
        user = cursor.fetchall()

        if request.method == "POST":
            delete_user(user[0][0])
            return redirect("/")

        return render_template(
            "account_settings.html",
            user=user,
        )
    else:
        Log.error(
            f"{request.remote_addr} tried to reach account settings without being logged in"
        )

        return redirect("/login/redirect=&account-settings")
