import sqlite3

from flask import Blueprint, redirect, render_template, request, session
from settings import Settings
from utils.delete import Delete
from utils.log import Log

accountSettingsBlueprint = Blueprint("accountSettings", __name__)


@accountSettingsBlueprint.route("/accountsettings", methods=["GET", "POST"])
def accountSettings():
    if "userName" in session:
        Log.database(f"Connecting to '{Settings.DB_USERS_ROOT}' database")

        connection = sqlite3.connect(Settings.DB_USERS_ROOT)
        connection.set_trace_callback(Log.database)
        cursor = connection.cursor()
        cursor.execute(
            """select userName, twofa_enabled from users where userName = ? """,
            [(session["userName"])],
        )
        user_data = cursor.fetchone()

        if request.method == "POST":
            Delete.user(user_data[0])
            return redirect("/")

        # Extract 2FA status (default to False if column doesn't exist)
        twofa_enabled = user_data[1] if user_data and len(user_data) > 1 else "False"

        return render_template(
            "accountSettings.html",
            user=[[user_data[0]]] if user_data else [],
            twofa_enabled=(twofa_enabled == "True"),
        )
    else:
        Log.error(
            f"{request.remote_addr} tried to reach account settings without being logged in"
        )

        return redirect("/login/redirect=&accountsettings")
