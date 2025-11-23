"""
This module handles disabling Two-Factor Authentication (2FA) for users.
"""

import sqlite3

from flask import (
    Blueprint,
    redirect,
    request,
    session,
)
from passlib.hash import sha512_crypt as encryption
from settings import Settings
from utils.flashMessage import flashMessage
from utils.log import Log

disable2faBlueprint = Blueprint("disable2fa", __name__)


@disable2faBlueprint.route("/disable-2fa", methods=["POST"])
def disable2fa():
    """
    Disable 2FA for a user account.
    Requires password confirmation for security.

    Returns:
        redirect: Redirect to account settings
    """

    if "userName" not in session:
        Log.error(f"{request.remote_addr} tried to disable 2FA without logging in")
        flashMessage(
            page="disable2fa",
            message="loginRequired",
            category="error",
            language=session.get("language", "en"),
        )
        return redirect("/login/redirect=&accountsettings")

    userName = session["userName"]
    password = request.form.get("password", "")

    if not password:
        flashMessage(
            page="disable2fa",
            message="passwordRequired",
            category="error",
            language=session.get("language", "en"),
        )
        return redirect("/accountsettings")

    Log.database(f"Connecting to '{Settings.DB_USERS_ROOT}' database")

    connection = sqlite3.connect(Settings.DB_USERS_ROOT)
    connection.set_trace_callback(Log.database)
    cursor = connection.cursor()

    try:
        # Verify password
        cursor.execute(
            "SELECT password, twofa_enabled FROM Users WHERE userName = ?",
            (userName,),
        )
        user = cursor.fetchone()

        if not user:
            Log.error(f'User: "{userName}" not found')
            flashMessage(
                page="disable2fa",
                message="userNotFound",
                category="error",
                language=session.get("language", "en"),
            )
            return redirect("/accountsettings")

        stored_password, twofa_enabled = user

        if not encryption.verify(password, stored_password):
            Log.error(f'User: "{userName}" provided incorrect password to disable 2FA')
            flashMessage(
                page="disable2fa",
                message="incorrectPassword",
                category="error",
                language=session.get("language", "en"),
            )
            return redirect("/accountsettings")

        if twofa_enabled != "True":
            Log.warning(f'User: "{userName}" attempted to disable 2FA when it was not enabled')
            flashMessage(
                page="disable2fa",
                message="notEnabled",
                category="info",
                language=session.get("language", "en"),
            )
            return redirect("/accountsettings")

        # Disable 2FA and clear secrets
        cursor.execute(
            """UPDATE Users
               SET twofa_secret = NULL, twofa_enabled = 'False', backup_codes = NULL
               WHERE userName = ?""",
            (userName,),
        )
        connection.commit()

        Log.success(f'User: "{userName}" disabled 2FA')
        flashMessage(
            page="disable2fa",
            message="disabled",
            category="success",
            language=session.get("language", "en"),
        )

    finally:
        connection.close()

    return redirect("/accountsettings")
