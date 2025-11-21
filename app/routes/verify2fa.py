"""
This module handles verification of Two-Factor Authentication (2FA) tokens during login.
"""

import sqlite3

from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    session,
)
from settings import Settings
from utils.flashMessage import flashMessage
from utils.log import Log
from utils.redirectValidator import RedirectValidator
from utils.twoFactorAuth import TwoFactorAuth

verify2faBlueprint = Blueprint("verify2fa", __name__)


@verify2faBlueprint.route("/verify-2fa/redirect=<direct>", methods=["GET", "POST"])
def verify2fa(direct):
    """
    Verify 2FA token or backup code during login.

    Args:
        direct (str): The redirect path after successful verification

    Returns:
        render_template or redirect: Verification page or redirect after success
    """

    # Check if user has passed password verification
    if "pending_2fa_userName" not in session:
        Log.error(f"{request.remote_addr} accessed 2FA verification without password auth")
        return redirect("/login/redirect=&")

    userName = session["pending_2fa_userName"]
    safe_redirect = RedirectValidator.safe_redirect_path(direct)

    if request.method == "POST":
        token = request.form.get("token", "").strip()
        use_backup = request.form.get("use_backup", "") == "true"

        if not token:
            flashMessage(
                page="verify2fa",
                message="tokenRequired",
                category="error",
                language=session.get("language", "en"),
            )
            return render_template("verify2fa.html", userName=userName)

        Log.database(f"Connecting to '{Settings.DB_USERS_ROOT}' database")

        connection = sqlite3.connect(Settings.DB_USERS_ROOT)
        connection.set_trace_callback(Log.database)
        cursor = connection.cursor()

        try:
            cursor.execute(
                "SELECT twofa_secret, backup_codes, role FROM Users WHERE userName = ?",
                (userName,),
            )
            user = cursor.fetchone()

            if not user:
                Log.error(f'User: "{userName}" not found during 2FA verification')
                session.pop("pending_2fa_userName", None)
                return redirect("/login/redirect=&")

            twofa_secret, backup_codes, userRole = user

            verified = False

            if use_backup:
                # Verify backup code
                is_valid, updated_codes = TwoFactorAuth.verify_backup_code(
                    backup_codes, token
                )

                if is_valid:
                    # Update backup codes in database (remove used code)
                    cursor.execute(
                        "UPDATE Users SET backup_codes = ? WHERE userName = ?",
                        (updated_codes, userName),
                    )
                    connection.commit()
                    verified = True
                    Log.info(f'User: "{userName}" verified with backup code')
                else:
                    Log.error(f'User: "{userName}" provided invalid backup code')
            else:
                # Verify TOTP token
                if TwoFactorAuth.verify_token(twofa_secret, token):
                    verified = True
                    Log.info(f'User: "{userName}" verified with TOTP token')
                else:
                    Log.error(f'User: "{userName}" provided invalid TOTP token')

            if verified:
                # Complete login
                session["userName"] = userName
                session["userRole"] = userRole
                session.pop("pending_2fa_userName", None)

                Log.success(f'User: "{userName}" logged in successfully with 2FA')
                flashMessage(
                    page="verify2fa",
                    message="success",
                    category="success",
                    language=session.get("language", "en"),
                )

                return redirect(safe_redirect)
            else:
                flashMessage(
                    page="verify2fa",
                    message="invalidToken",
                    category="error",
                    language=session.get("language", "en"),
                )

        finally:
            connection.close()

    return render_template("verify2fa.html", userName=userName)
