"""
Force Password Change Before Request Hook

This hook checks if the current admin user must change their password
and redirects them to the force-change-password page if necessary.
"""

import sqlite3

from flask import redirect, request, session
from settings import Settings
from utils.log import Log


def forcePasswordChangeCheck():
    """
    Before request hook that checks if admin user must change password.

    Returns:
        redirect or None: Redirects to force-change-password if required
    """

    # Skip check for certain endpoints to prevent redirect loops
    allowed_endpoints = [
        "/force-change-password",
        "/logout",
        "/static/",
        "/changelanguage",
        "/setlanguage",
        "/settheme",
    ]

    # Check if current path should be skipped
    current_path = request.path
    for endpoint in allowed_endpoints:
        if current_path.startswith(endpoint):
            return None

    # Only check if user is logged in
    if "userName" not in session:
        return None

    # Only check admin users
    if session.get("userRole") != "admin":
        return None

    # Check must_change_password in database
    try:
        connection = sqlite3.connect(Settings.DB_USERS_ROOT)
        cursor = connection.cursor()

        cursor.execute(
            "SELECT must_change_password FROM Users WHERE userName = ?",
            (session["userName"],)
        )
        result = cursor.fetchone()

        connection.close()

        if result and result[0] == "True":
            Log.info(f'Redirecting admin "{session["userName"]}" to force-change-password')
            return redirect("/force-change-password")

    except Exception as e:
        Log.error(f"Error checking must_change_password: {e}")

    return None
