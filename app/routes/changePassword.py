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
from utils.flashMessage import flashMessage
from utils.forms.ChangePasswordForm import ChangePasswordForm
from utils.log import Log

changePasswordBlueprint = Blueprint("changePassword", __name__)


@changePasswordBlueprint.route("/changepassword", methods=["GET", "POST"])
def changePassword():
    """
    This function is the route for the change password page.
    It is used to change the user's password.

    Args:
        request.form (dict): the form data from the request

    Returns:
        render_template: a rendered template with the form
    """

    if "userName" in session:
        form = ChangePasswordForm(request.form)

        if request.method == "POST" and form.validate():
            oldPassword = request.form["oldPassword"]
            password = request.form["password"]
            passwordConfirm = request.form["passwordConfirm"]

            # Store language before potential session clear
            user_language = session.get("language", "en")

            Log.database(f"Connecting to '{Settings.DB_USERS_ROOT}' database")

            connection = sqlite3.connect(Settings.DB_USERS_ROOT)
            connection.set_trace_callback(Log.database)
            cursor = connection.cursor()

            try:
                cursor.execute(
                    """select password from users where userName = ? """,
                    (session["userName"],),
                )

                user_password_row = cursor.fetchone()
                if not user_password_row:
                    Log.error(f'User: "{session["userName"]}" not found in database')
                    flashMessage(
                        page="changePassword",
                        message="old",
                        category="error",
                        language=user_language,
                    )
                    return render_template("changePassword.html", form=form)

                stored_password_hash = user_password_row[0]

                # Verify old password is correct
                if not encryption.verify(oldPassword, stored_password_hash):
                    Log.error(f'User: "{session["userName"]}" entered incorrect old password')
                    flashMessage(
                        page="changePassword",
                        message="old",
                        category="error",
                        language=user_language,
                    )
                    return render_template("changePassword.html", form=form)

                # Check if new password is same as old password
                if oldPassword == password:
                    flashMessage(
                        page="changePassword",
                        message="same",
                        category="error",
                        language=user_language,
                    )
                    return render_template("changePassword.html", form=form)

                # Check if new passwords match
                if password != passwordConfirm:
                    flashMessage(
                        page="changePassword",
                        message="match",
                        category="error",
                        language=user_language,
                    )
                    return render_template("changePassword.html", form=form)

                # All validations passed - update password
                newPassword = encryption.hash(password)
                cursor.execute(
                    """update users set password = ? where userName = ? """,
                    (newPassword, session["userName"]),
                )

                connection.commit()

                Log.success(
                    f'User: "{session["userName"]}" changed their password',
                )

                session.clear()
                flashMessage(
                    page="changePassword",
                    message="success",
                    category="success",
                    language=user_language,  # Use stored language after session.clear()
                )

                return redirect("/login/redirect=&")

            finally:
                # Always close database connection
                connection.close()

        return render_template(
            "changePassword.html",
            form=form,
        )
    else:
        Log.error(
            f"{request.remote_addr} tried to change his password without logging in"
        )
        flashMessage(
            page="changePassword",
            message="login",
            category="error",
            language=session.get("language", "en"),
        )

        return redirect("/login/redirect=&changepassword")
