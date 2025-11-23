"""
This module handles the 2FA reset confirmation process via email token.
"""

import sqlite3
from flask import Blueprint, render_template, redirect, request
from settings import Settings
from utils.flashMessage import flashMessage
from utils.log import Log
from utils.twofaResetTokenManager import TwoFAResetTokenManager
from utils.securityAuditLogger import SecurityAuditLogger

confirm2faResetBlueprint = Blueprint("confirm2faReset", __name__)


@confirm2faResetBlueprint.route("/confirm-2fa-reset/<token>", methods=["GET", "POST"])
def confirm2faReset(token):
    """
    Handle 2FA reset confirmation from email link.

    Args:
        token: The secure token from the email

    Returns:
        Rendered template or redirect
    """
    # Validate the token
    is_valid, userName, error_message = TwoFAResetTokenManager.validate_reset_token(token)

    if not is_valid:
        Log.error(f"Invalid 2FA reset token: {error_message}")
        return render_template(
            "confirm2faReset.html",
            valid=False,
            error=error_message,
            userName=None
        )

    if request.method == "POST":
        # User confirmed the 2FA reset
        if "confirmReset" in request.form:
            try:
                # Reset 2FA for the user
                connection = sqlite3.connect(Settings.DB_USERS_ROOT)
                connection.set_trace_callback(Log.database)
                cursor = connection.cursor()

                cursor.execute(
                    """UPDATE users SET twofa_enabled = 'False', twofa_secret = NULL, backup_codes = NULL WHERE userName = ?""",
                    (userName,)
                )
                connection.commit()
                connection.close()

                # Mark token as used
                TwoFAResetTokenManager.mark_token_used(token)

                # Log the action
                SecurityAuditLogger.log_admin_action(
                    userName=userName,
                    ip_address=request.remote_addr,
                    action="Confirmed 2FA reset via email",
                    target=userName
                )

                Log.success(f"2FA reset confirmed for user: {userName}")

                return render_template(
                    "confirm2faReset.html",
                    valid=True,
                    confirmed=True,
                    userName=userName
                )

            except Exception as e:
                Log.error(f"Error resetting 2FA for {userName}: {e}")
                return render_template(
                    "confirm2faReset.html",
                    valid=False,
                    error="An error occurred while resetting 2FA",
                    userName=userName
                )

        # User cancelled the reset
        elif "cancelReset" in request.form:
            TwoFAResetTokenManager.mark_token_used(token)
            Log.info(f"2FA reset cancelled by user: {userName}")
            return render_template(
                "confirm2faReset.html",
                valid=True,
                cancelled=True,
                userName=userName
            )

    # GET request - show confirmation page
    return render_template(
        "confirm2faReset.html",
        valid=True,
        confirmed=False,
        cancelled=False,
        userName=userName,
        token=token
    )
