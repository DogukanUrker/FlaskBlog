from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    session,
)

from models import User
from utils.change_user_role import change_user_role
from utils.delete import delete_user
from utils.log import Log
from utils.paginate import paginate_query

admin_panel_users_blueprint = Blueprint("admin_panel_users", __name__)


@admin_panel_users_blueprint.route("/admin/users", methods=["GET", "POST"])
def admin_panel_users():
    if "username" in session:
        Log.info(f"Admin: {session['username']} reached to users admin panel")

        user = User.query.filter_by(username=session["username"]).first()

        if not user:
            return redirect("/")

        if user.role != "admin":
            Log.error(
                f"{request.remote_addr} tried to reach user admin panel without being admin"
            )
            return redirect("/")

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

        if user.role == "admin":
            query = User.query
            users_objects, page, total_pages = paginate_query(query)

            users = [
                (
                    u.user_id,
                    u.username,
                    u.email,
                    u.password,
                    u.profile_picture,
                    u.role,
                    u.points,
                    u.time_stamp,
                    u.is_verified,
                )
                for u in users_objects
            ]

            Log.info(f"Rendering admin_panel_users.html: params: users={len(users)}")

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
