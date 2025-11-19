"""
Context processor to inject site logo path into all templates.
"""

import sqlite3
from settings import Settings


def siteLogo():
    """
    Returns the site logo path from database settings.

    Returns:
        dict: A dictionary with siteLogo path.
    """
    try:
        connection = sqlite3.connect(Settings.DB_USERS_ROOT)
        cursor = connection.cursor()

        cursor.execute(
            "SELECT setting_value FROM site_settings WHERE setting_key = ?",
            ("site_logo",)
        )

        result = cursor.fetchone()
        connection.close()

        if result:
            return dict(siteLogo=result[0])
        else:
            # Fallback to default if not found
            return dict(siteLogo="/static/uploads/site_logo.ico")

    except Exception:
        # Fallback to default on error
        return dict(siteLogo="/static/uploads/site_logo.ico")
