"""
This module handles secure token generation and validation for 2FA resets.
"""

import secrets
import sqlite3
from datetime import datetime, timedelta
from settings import Settings
from utils.log import Log


class TwoFAResetTokenManager:
    """
    Manages secure tokens for 2FA reset flows initiated by admins.
    Tokens are stored in the database with expiration times.
    """

    @staticmethod
    def _init_tokens_table():
        """
        Initialize the 2FA reset tokens table if it doesn't exist.
        """
        connection = sqlite3.connect(Settings.DB_USERS_ROOT)
        cursor = connection.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS twofa_reset_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                userName TEXT NOT NULL,
                token TEXT NOT NULL UNIQUE,
                admin_userName TEXT NOT NULL,
                created_at INTEGER NOT NULL,
                expires_at INTEGER NOT NULL,
                used INTEGER DEFAULT 0
            )
            """
        )
        connection.commit()
        connection.close()

    @staticmethod
    def generate_reset_token(userName, admin_userName, expiry_hours=24):
        """
        Generate a cryptographically secure 2FA reset token.

        Args:
            userName: Username for whom to generate the token
            admin_userName: Admin who initiated the reset
            expiry_hours: Token validity duration in hours (default 24)

        Returns:
            str: The generated token
        """
        TwoFAResetTokenManager._init_tokens_table()

        # Generate a cryptographically secure random token
        token = secrets.token_urlsafe(32)

        # Calculate expiry time
        now = int(datetime.now().timestamp())
        expires_at = int((datetime.now() + timedelta(hours=expiry_hours)).timestamp())

        # Store token in database
        connection = sqlite3.connect(Settings.DB_USERS_ROOT)
        cursor = connection.cursor()

        # Invalidate any existing tokens for this user
        cursor.execute(
            """UPDATE twofa_reset_tokens SET used = 1 WHERE userName = ? AND used = 0""",
            (userName,),
        )

        # Insert new token
        cursor.execute(
            """
            INSERT INTO twofa_reset_tokens (userName, token, admin_userName, created_at, expires_at, used)
            VALUES (?, ?, ?, ?, ?, 0)
            """,
            (userName, token, admin_userName, now, expires_at),
        )
        connection.commit()
        connection.close()

        Log.success(
            f"2FA reset token generated for user: {userName} by admin: {admin_userName} (expires in {expiry_hours} hours)"
        )
        return token

    @staticmethod
    def validate_reset_token(token):
        """
        Validate a 2FA reset token.

        Args:
            token: The token to validate

        Returns:
            tuple: (is_valid: bool, userName: str or None, error_message: str or None)
        """
        TwoFAResetTokenManager._init_tokens_table()

        connection = sqlite3.connect(Settings.DB_USERS_ROOT)
        cursor = connection.cursor()

        # Fetch token info
        cursor.execute(
            """
            SELECT userName, expires_at, used, admin_userName
            FROM twofa_reset_tokens
            WHERE token = ?
            """,
            (token,),
        )
        result = cursor.fetchone()
        connection.close()

        if not result:
            Log.error("Invalid 2FA reset token attempt")
            return False, None, "Invalid or expired token"

        userName, expires_at, used, admin_userName = result

        # Check if token has been used
        if used:
            Log.error(f"Attempt to reuse 2FA reset token for user: {userName}")
            return False, None, "Token has already been used"

        # Check if token has expired
        now = int(datetime.now().timestamp())
        if now > expires_at:
            Log.error(f"Expired 2FA reset token used for user: {userName}")
            return False, None, "Token has expired"

        Log.success(f"Valid 2FA reset token for user: {userName}")
        return True, userName, None

    @staticmethod
    def mark_token_used(token):
        """
        Mark a token as used after successful 2FA reset.

        Args:
            token: The token to mark as used
        """
        TwoFAResetTokenManager._init_tokens_table()

        connection = sqlite3.connect(Settings.DB_USERS_ROOT)
        cursor = connection.cursor()
        cursor.execute(
            """UPDATE twofa_reset_tokens SET used = 1 WHERE token = ?""",
            (token,),
        )
        connection.commit()
        connection.close()

        Log.info("2FA reset token marked as used")

    @staticmethod
    def cleanup_expired_tokens():
        """
        Remove expired tokens from the database (cleanup task).
        Should be called periodically (e.g., daily cron job).
        """
        TwoFAResetTokenManager._init_tokens_table()

        now = int(datetime.now().timestamp())
        connection = sqlite3.connect(Settings.DB_USERS_ROOT)
        cursor = connection.cursor()
        cursor.execute(
            """DELETE FROM twofa_reset_tokens WHERE expires_at < ? OR used = 1""",
            (now - 86400,),  # Keep used tokens for 24 hours for audit
        )
        deleted = cursor.rowcount
        connection.commit()
        connection.close()

        if deleted > 0:
            Log.info(f"Cleaned up {deleted} expired 2FA reset tokens")
