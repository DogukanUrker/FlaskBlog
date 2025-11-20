"""
SMTP Settings Utility

This module provides functions to retrieve SMTP settings from the database,
with fallback to environment variables/Settings defaults.
"""

import sqlite3
from settings import Settings
from utils.log import Log
from utils.encryption import EncryptionUtil


class SMTPSettings:
    """
    Retrieves SMTP configuration from database or falls back to Settings defaults.
    """

    @staticmethod
    def get_settings():
        """
        Get SMTP settings from database, falling back to Settings defaults.

        Returns:
            dict: Dictionary containing smtp_server, smtp_port, smtp_mail, smtp_password
        """
        settings = {
            "smtp_server": Settings.SMTP_SERVER,
            "smtp_port": Settings.SMTP_PORT,
            "smtp_mail": Settings.SMTP_MAIL,
            "smtp_password": Settings.SMTP_PASSWORD,
        }

        try:
            connection = sqlite3.connect(Settings.DB_USERS_ROOT)
            cursor = connection.cursor()

            # Get each SMTP setting from database
            for key in ["smtp_server", "smtp_port", "smtp_mail", "smtp_password"]:
                cursor.execute(
                    "SELECT setting_value FROM site_settings WHERE setting_key = ?",
                    (key,)
                )
                result = cursor.fetchone()
                if result and result[0]:
                    if key == "smtp_port":
                        try:
                            settings[key] = int(result[0])
                        except ValueError:
                            pass  # Keep default if invalid
                    elif key == "smtp_password":
                        # Decrypt the password
                        settings[key] = EncryptionUtil.decrypt(result[0])
                    else:
                        settings[key] = result[0]

            connection.close()

        except Exception as e:
            Log.error(f"Error retrieving SMTP settings from database: {e}")
            # Fall back to Settings defaults (already set above)

        return settings

    @staticmethod
    def get_server():
        """Get SMTP server address."""
        return SMTPSettings.get_settings()["smtp_server"]

    @staticmethod
    def get_port():
        """Get SMTP server port."""
        return SMTPSettings.get_settings()["smtp_port"]

    @staticmethod
    def get_mail():
        """Get SMTP email address."""
        return SMTPSettings.get_settings()["smtp_mail"]

    @staticmethod
    def get_password():
        """Get SMTP password."""
        return SMTPSettings.get_settings()["smtp_password"]
