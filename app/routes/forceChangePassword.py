"""
Force Change Password Route

This route handles the forced password change for admin users on their first login.
Admin users must change their password to meet cryptographic complexity requirements.
"""

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
from utils.forms.ForceChangePasswordForm import ForceChangePasswordForm
from utils.log import Log
from utils.passwordComplexityValidator import PasswordComplexityValidator

forceChangePasswordBlueprint = Blueprint("forceChangePassword", __name__)


@forceChangePasswordBlueprint.route("/force-change-password", methods=["GET", "POST"])
def forceChangePassword():
    """
    This function is the route for the forced password change page.
    It is used when admin users must change their password on first login.

    Returns:
        render_template: a rendered template with the form
    """

    if "userName" not in session:
        Log.error("Unauthenticated user tried to access force-change-password")
        return redirect("/login/redirect=&")

    # Check if user actually needs to change password
    Log.database(f"Connecting to '{Settings.DB_USERS_ROOT}' database")
    connection = sqlite3.connect(Settings.DB_USERS_ROOT)
    connection.set_trace_callback(Log.database)
    cursor = connection.cursor()

    try:
        cursor.execute(
            "SELECT must_change_password, role FROM Users WHERE userName = ?",
            (session["userName"],)
        )
        user_data = cursor.fetchone()

        if not user_data:
            Log.error(f'User: "{session["userName"]}" not found in database')
            session.clear()
            return redirect("/login/redirect=&")

        must_change_password = user_data[0]
        user_role = user_data[1]

        # Only admin users with must_change_password = 'True' should be here
        if must_change_password != "True" or user_role != "admin":
            Log.info(f'User: "{session["userName"]}" does not need to change password')
            return redirect("/")

        form = ForceChangePasswordForm(request.form)

        if request.method == "POST" and form.validate():
            password = request.form["password"]
            passwordConfirm = request.form["passwordConfirm"]

            # Store language before potential error messages
            user_language = session.get("language", "en")

            # Check if new passwords match
            if password != passwordConfirm:
                flashMessage(
                    page="forceChangePassword",
                    message="match",
                    category="error",
                    language=user_language,
                )
                return render_template("forceChangePassword.html", form=form)

            # Validate password complexity
            is_valid, errors = PasswordComplexityValidator.validate(password)

            if not is_valid:
                # Flash message for each failed requirement
                for error in errors:
                    flashMessage(
                        page="forceChangePassword",
                        message=error,
                        category="error",
                        language=user_language,
                    )
                return render_template("forceChangePassword.html", form=form)

            # All validations passed - update password
            newPassword = encryption.hash(password)
            cursor.execute(
                """UPDATE Users SET password = ?, must_change_password = 'False' WHERE userName = ?""",
                (newPassword, session["userName"]),
            )

            connection.commit()

            Log.success(
                f'Admin user: "{session["userName"]}" changed their password (first login requirement)',
            )

            flashMessage(
                page="forceChangePassword",
                message="success",
                category="success",
                language=user_language,
            )

            return redirect("/")

        return render_template(
            "forceChangePassword.html",
            form=form,
        )

    finally:
        connection.close()
