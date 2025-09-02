import sqlite3

from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    session,
)
from passlib.hash import sha512_crypt as encryption

from settings import Settings
from utils.flash_message import flash_message
from utils.forms.change_password_form import ChangePasswordForm
from utils.log import Log

change_password_blueprint = Blueprint("change_password", __name__)


@change_password_blueprint.route("/change-password", methods=["GET", "POST"])
def change_password():
    """
    This function is the route for the change password page.
    It is used to change the user's password.

    Args:
        request.form (dict): the form data from the request

    Returns:
        render_template: a rendered template with the form
    """

    if "username" in session:
        form = ChangePasswordForm(request.form)

        if request.method == "POST":
            old_password = request.form["old_password"]
            password = request.form["password"]
            password_confirm = request.form["password_confirm"]
            Log.database(f"Connecting to '{Settings.DB_USERS_ROOT}' database")

            connection = sqlite3.connect(Settings.DB_USERS_ROOT)
            connection.set_trace_callback(Log.database)
            cursor = connection.cursor()

            cursor.execute(
                """select password from users where username = ? """,
                [(session["username"])],
            )

            if encryption.verify(old_password, cursor.fetchone()[0]):
                if old_password == password:
                    flash_message(
                        page="change_password",
                        message="same",
                        category="error",
                        language=session["language"],
                    )

                if password != password_confirm:
                    flash_message(
                        page="change_password",
                        message="match",
                        category="error",
                        language=session["language"],
                    )

                if old_password != password and password == password_confirm:
                    new_password = encryption.hash(password)
                    Log.database(f"Connecting to '{Settings.DB_USERS_ROOT}' database")

                    connection = sqlite3.connect(Settings.DB_USERS_ROOT)
                    connection.set_trace_callback(Log.database)
                    cursor = connection.cursor()
                    cursor.execute(
                        """update users set password = ? where username = ? """,
                        [(new_password), (session["username"])],
                    )

                    connection.commit()

                    Log.success(
                        f'User: "{session["username"]}" changed his password',
                    )

                    session.clear()
                    flash_message(
                        page="change_password",
                        message="success",
                        category="success",
                        language=session["language"],
                    )

                    return redirect("/login/redirect=&")
            else:
                flash_message(
                    page="change_password",
                    message="old",
                    category="error",
                    language=session["language"],
                )

        return render_template(
            "change_password.html",
            form=form,
        )
    else:
        Log.error(
            f"{request.remote_addr} tried to change his password without logging in"
        )
        flash_message(
            page="change_password",
            message="login",
            category="error",
            language=session["language"],
        )

        return redirect("/login/redirect=change-password")
