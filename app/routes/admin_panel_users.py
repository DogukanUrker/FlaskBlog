import sqlite3

from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    session,
)

from settings import Settings
from utils.change_user_role import change_user_role
from utils.delete import delete_user
from utils.log import Log
from utils.paginate import paginate_query

admin_panel_users_blueprint = Blueprint("admin_panel_users", __name__)


@admin_panel_users_blueprint.route("/admin/users", methods=["GET", "POST"])
@admin_panel_users_blueprint.route("/admin-panel/users", methods=["GET", "POST"])
def admin_panel_users():
    if "username" in session:
        Log.info(f"Admin: {session['username']} reached to users admin panel")
        Log.database(f"Connecting to '{Settings.DB_USERS_ROOT}' database")

        connection = sqlite3.connect(Settings.DB_USERS_ROOT)
        connection.set_trace_callback(Log.database)
        cursor = connection.cursor()
        cursor.execute(
            """select role from users where username = ? """,
            [(session["username"])],
        )
        role = cursor.fetchone()[0]

        if request.method == "POST":
            if "user_delete_button" in request.form:
                Log.info(
                    f"Admin: {session['username']} deleted user: {request.form['username']}"
                )

                delete_user(request.form["username"])

            if "user_role_change_button" in request.form:
                Log.info(
                    f"Admin: {session['username']} changed {request.form['username']}'s role"
                )

                change_user_role(request.form["username"])

        if role == "admin":
            users, page, total_pages = paginate_query(
                Settings.DB_USERS_ROOT,
                "select count(*) from users",
                "select * from users",
            )

            Log.info(f"Rendering admin_panel_users.html: params: users={users}")

            return render_template(
                "admin_panel_users.html",
                users=users,
                page=page,
                total_pages=total_pages,
            )
        else:
            Log.error(
                f"{request.remote_addr} tried to reach user admin panel without being admin"
            )

            return redirect("/")
    else:
        Log.error(
            f"{request.remote_addr} tried to reach user admin panel being logged in"
        )

        return redirect("/")
