"""
This module handles secure token generation and validation for password resets.
"""

import secrets
import sqlite3
from datetime import datetime, timedelta
from settings import Settings
from utils.log import Log


class SecureTokenManager:
    """
    Manages secure tokens for password reset and other authentication flows.
    Tokens are stored in the database with expiration times.
    """

    @staticmethod
    def _init_tokens_table():
        """
        Initialize the password reset tokens table if it doesn't exist.
        """
        connection = sqlite3.connect(Settings.DB_USERS_ROOT)
        cursor = connection.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS password_reset_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                userName TEXT NOT NULL,
                token TEXT NOT NULL UNIQUE,
                created_at INTEGER NOT NULL,
                expires_at INTEGER NOT NULL,
                used INTEGER DEFAULT 0
            )
            """
        )
        connection.commit()
        connection.close()

    @staticmethod
    def generate_reset_token(userName, expiry_minutes=15):
        """
        Generate a cryptographically secure password reset token.

        Args:
            userName: Username for whom to generate the token
            expiry_minutes: Token validity duration in minutes (default 15)

        Returns:
            str: The generated token
        """
        SecureTokenManager._init_tokens_table()

        # Generate a cryptographically secure random token
        token = secrets.token_urlsafe(32)

        # Calculate expiry time
        now = int(datetime.now().timestamp())
        expires_at = int((datetime.now() + timedelta(minutes=expiry_minutes)).timestamp())

        # Store token in database
        connection = sqlite3.connect(Settings.DB_USERS_ROOT)
        cursor = connection.cursor()

        # Invalidate any existing tokens for this user
        cursor.execute(
            """UPDATE password_reset_tokens SET used = 1 WHERE userName = ? AND used = 0""",
            (userName,),
        )

        # Insert new token
        cursor.execute(
            """
            INSERT INTO password_reset_tokens (userName, token, created_at, expires_at, used)
            VALUES (?, ?, ?, ?, 0)
            """,
            (userName, token, now, expires_at),
        )
        connection.commit()
        connection.close()

        Log.success(
            f"Password reset token generated for user: {userName} (expires in {expiry_minutes} minutes)"
        )
        return token

    @staticmethod
    def validate_reset_token(token):
        """
        Validate a password reset token.

        Args:
            token: The token to validate

        Returns:
            tuple: (is_valid: bool, userName: str or None, error_message: str or None)
        """
        SecureTokenManager._init_tokens_table()

        connection = sqlite3.connect(Settings.DB_USERS_ROOT)
        cursor = connection.cursor()

        # Fetch token info
        cursor.execute(
            """
            SELECT userName, expires_at, used
            FROM password_reset_tokens
            WHERE token = ?
            """,
            (token,),
        )
        result = cursor.fetchone()
        connection.close()

        if not result:
            Log.error("Invalid password reset token attempt")
            return False, None, "Invalid or expired token"

        userName, expires_at, used = result

        # Check if token has been used
        if used:
            Log.error(f"Attempt to reuse password reset token for user: {userName}")
            return False, None, "Token has already been used"

        # Check if token has expired
        now = int(datetime.now().timestamp())
        if now > expires_at:
            Log.error(f"Expired password reset token used for user: {userName}")
            return False, None, "Token has expired"

        Log.success(f"Valid password reset token for user: {userName}")
        return True, userName, None

    @staticmethod
    def mark_token_used(token):
        """
        Mark a token as used after successful password reset.

        Args:
            token: The token to mark as used
        """
        SecureTokenManager._init_tokens_table()

        connection = sqlite3.connect(Settings.DB_USERS_ROOT)
        cursor = connection.cursor()
        cursor.execute(
            """UPDATE password_reset_tokens SET used = 1 WHERE token = ?""",
            (token,),
        )
        connection.commit()
        connection.close()

        Log.info(f"Password reset token marked as used")

    @staticmethod
    def cleanup_expired_tokens():
        """
        Remove expired tokens from the database (cleanup task).
        Should be called periodically (e.g., daily cron job).
        """
        SecureTokenManager._init_tokens_table()

        now = int(datetime.now().timestamp())
        connection = sqlite3.connect(Settings.DB_USERS_ROOT)
        cursor = connection.cursor()
        cursor.execute(
            """DELETE FROM password_reset_tokens WHERE expires_at < ? OR used = 1""",
            (now - 86400,),  # Keep used tokens for 24 hours for audit
        )
        deleted = cursor.rowcount
        connection.commit()
        connection.close()

        if deleted > 0:
            Log.info(f"Cleaned up {deleted} expired password reset tokens")
