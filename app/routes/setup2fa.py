"""
This module handles the setup of Two-Factor Authentication (2FA) for users.
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
from utils.twoFactorAuth import TwoFactorAuth

setup2faBlueprint = Blueprint("setup2fa", __name__)


@setup2faBlueprint.route("/setup-2fa", methods=["GET", "POST"])
def setup2fa():
    """
    Handle 2FA setup for users.

    GET: Display QR code and backup codes for 2FA setup
    POST: Verify token and enable 2FA

    Returns:
        render_template: Setup page with QR code or redirect after success
    """

    if "userName" not in session:
        Log.error(f"{request.remote_addr} tried to access 2FA setup without logging in")
        flashMessage(
            page="setup2fa",
            message="loginRequired",
            category="error",
            language=session.get("language", "en"),
        )
        return redirect("/login/redirect=&setup-2fa")

    userName = session["userName"]
    Log.database(f"Connecting to '{Settings.DB_USERS_ROOT}' database")

    connection = sqlite3.connect(Settings.DB_USERS_ROOT)
    connection.set_trace_callback(Log.database)
    cursor = connection.cursor()

    try:
        # Check if 2FA is already enabled
        cursor.execute(
            "SELECT twofa_enabled FROM Users WHERE userName = ?",
            (userName,),
        )
        user = cursor.fetchone()

        if user and user[0] == "True":
            Log.warning(f'User: "{userName}" already has 2FA enabled')
            flashMessage(
                page="setup2fa",
                message="alreadyEnabled",
                category="info",
                language=session.get("language", "en"),
            )
            return redirect("/accountsettings")

        if request.method == "POST":
            # Verify the token provided by user
            token = request.form.get("token", "").strip()
            secret = session.get("temp_2fa_secret")
            backup_codes_json = session.get("temp_backup_codes")

            if not secret or not backup_codes_json:
                Log.error(f'User: "{userName}" session data missing for 2FA setup')
                flashMessage(
                    page="setup2fa",
                    message="sessionExpired",
                    category="error",
                    language=session.get("language", "en"),
                )
                return redirect("/setup-2fa")

            if TwoFactorAuth.verify_token(secret, token):
                # Token is valid - enable 2FA
                cursor.execute(
                    """UPDATE Users
                       SET twofa_secret = ?, twofa_enabled = ?, backup_codes = ?
                       WHERE userName = ?""",
                    (secret, "True", backup_codes_json, userName),
                )
                connection.commit()

                # Clear temporary session data
                session.pop("temp_2fa_secret", None)
                session.pop("temp_backup_codes", None)

                Log.success(f'User: "{userName}" enabled 2FA')
                flashMessage(
                    page="setup2fa",
                    message="success",
                    category="success",
                    language=session.get("language", "en"),
                )
                return redirect("/accountsettings")
            else:
                Log.error(f'User: "{userName}" provided invalid 2FA token during setup')
                flashMessage(
                    page="setup2fa",
                    message="invalidToken",
                    category="error",
                    language=session.get("language", "en"),
                )

        # GET request - generate new secret and backup codes
        secret = TwoFactorAuth.generate_secret()
        uri = TwoFactorAuth.get_totp_uri(userName, secret)
        qr_code = TwoFactorAuth.generate_qr_code(uri)
        backup_codes = TwoFactorAuth.generate_backup_codes()

        # Store in session temporarily until user verifies
        session["temp_2fa_secret"] = secret
        session["temp_backup_codes"] = TwoFactorAuth.codes_to_json(backup_codes)

        Log.info(f'User: "{userName}" initiated 2FA setup')

        return render_template(
            "setup2fa.html",
            qr_code=qr_code,
            secret=secret,
            backup_codes=backup_codes,
        )

    finally:
        connection.close()
