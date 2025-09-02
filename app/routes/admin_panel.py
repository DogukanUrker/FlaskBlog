import sqlite3

from flask import Blueprint, redirect, render_template, request, session

from settings import Settings
from utils.log import Log

admin_panel_blueprint = Blueprint("admin_panel", __name__)


@admin_panel_blueprint.route("/admin")
def admin_panel():
    if "username" in session:
        Log.success(f"Connecting to '{Settings.DB_USERS_ROOT}' database")

        connection = sqlite3.connect(Settings.DB_USERS_ROOT)
        connection.set_trace_callback(Log.database)
        cursor = connection.cursor()
        cursor.execute(
            """select role from users where username = ? """,
            [(session["username"])],
        )
        role = cursor.fetchone()[0]

        if role == "admin":
            Log.info(f"Admin: {session['username']} reached to the admin panel")

            Log.info("Rendering admin_panel.html: params: None")

            return render_template("admin_panel.html")
        else:
            Log.error(
                f"{request.remote_addr} tried to reach admin panel without being admin"
            )

            return redirect("/")
    else:
        Log.error(f"{request.remote_addr} tried to reach admin panel being logged in")

        return redirect("/")
