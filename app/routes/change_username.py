import sqlite3

from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    session,
)

from settings import Settings
from utils.flash_message import flash_message
from utils.forms.change_user_name_form import ChangeUserNameForm
from utils.log import Log

change_username_blueprint = Blueprint("change_username", __name__)


@change_username_blueprint.route("/change-username", methods=["GET", "POST"])
def change_username():
    """
    This function is the route for the change username page.
    It is used to change the user's username.

    Args:
        request.form (dict): the form data from the request

    Returns:
        render_template: a rendered template with the form
    """

    if "username" in session:
        form = ChangeUserNameForm(request.form)

        if request.method == "POST":
            new_username = request.form["new_username"]
            new_username = new_username.replace(" ", "")
            Log.database(f"Connecting to '{Settings.DB_USERS_ROOT}' database")

            connection = sqlite3.connect(Settings.DB_USERS_ROOT)
            connection.set_trace_callback(Log.database)
            cursor = connection.cursor()
            cursor.execute(
                """select * from users where lower(username) = ? """,
                [(new_username.lower())],
            )
            user = cursor.fetchone()

            if not user:
                Log.database(f"Connecting to '{Settings.DB_USERS_ROOT}' database")

                connection = sqlite3.connect(Settings.DB_USERS_ROOT)
                connection.set_trace_callback(Log.database)
                cursor = connection.cursor()
                cursor.execute(
                    """update users set username = ? where username = ? """,
                    [(new_username), (session["username"])],
                )

                connection.commit()

                Log.database(f"Connecting to '{Settings.DB_POSTS_ROOT}' database")

                connection = sqlite3.connect(Settings.DB_POSTS_ROOT)
                connection.set_trace_callback(Log.database)
                cursor = connection.cursor()
                cursor.execute(
                    """update posts set username = ? where username = ? """,
                    [(new_username), (session["username"])],
                )

                connection.commit()

                Log.database(f"Connecting to '{Settings.DB_COMMENTS_ROOT}' database")

                connection = sqlite3.connect(Settings.DB_COMMENTS_ROOT)
                connection.set_trace_callback(Log.database)
                cursor = connection.cursor()
                cursor.execute(
                    """update comments set username = ? where username = ? """,
                    [(new_username), (session["username"])],
                )

                connection.commit()

                Log.success(
                    f"User: {session['username']} changed his username to {new_username}",
                )

                session["username"] = new_username
                flash_message(
                    page="change_username",
                    message="success",
                    category="success",
                    language=session["language"],
                )

                return redirect("/account-settings")
            else:
                Log.error(f'User: "{new_username}" already exists')
                flash_message(
                    page="change_username",
                    message="exists",
                    category="error",
                    language=session["language"],
                )

        return render_template(
            "change_username.html",
            form=form,
        )
    else:
        Log.error(
            f"{request.remote_addr} tried to change his username without logging in"
        )
        flash_message(
            page="change_username",
            message="login",
            category="error",
            language=session["language"],
        )

        return redirect("/login/redirect=change-username")
