"""
Security Audit Logger

This module provides functionality to log security-related events to the database
for admin monitoring and security analysis.

Event Types:
- admin_login: Admin user login attempts (success/failure)
- user_login: Regular user login attempts
- admin_action: Admin panel actions (delete user, change role, etc.)
- page_access: Client page access tracking
- failed_auth: Failed authentication attempts
- rate_limit: Rate limiting triggered
"""

import sqlite3

from settings import Settings
from utils.log import Log
from utils.time import currentTimeStamp


class SecurityAuditLogger:
    """
    Security audit logging utility for tracking security events.
    """

    @staticmethod
    def log_event(
        event_type,
        userName=None,
        ip_address=None,
        user_agent=None,
        path=None,
        method=None,
        status_code=None,
        details=None,
    ):
        """
        Log a security event to the database.

        Args:
            event_type (str): Type of event (admin_login, user_login, admin_action, page_access, etc.)
            userName (str, optional): Username associated with the event
            ip_address (str, optional): IP address of the client
            user_agent (str, optional): User agent string
            path (str, optional): Request path
            method (str, optional): HTTP method (GET, POST, etc.)
            status_code (int, optional): HTTP status code
            details (str, optional): Additional details about the event

        Returns:
            bool: True if logging was successful, False otherwise
        """
        try:
            Log.database(f"Connecting to '{Settings.DB_USERS_ROOT}' database")
            connection = sqlite3.connect(Settings.DB_USERS_ROOT)
            connection.set_trace_callback(Log.database)
            cursor = connection.cursor()

            cursor.execute(
                """
                INSERT INTO security_audit_log
                (event_type, userName, ip_address, user_agent, path, method, status_code, details, timeStamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event_type,
                    userName,
                    ip_address,
                    user_agent,
                    path,
                    method,
                    status_code,
                    details,
                    currentTimeStamp(),
                ),
            )

            connection.commit()
            connection.close()

            Log.info(
                f"Security event logged: {event_type} | User: {userName} | IP: {ip_address}"
            )
            return True

        except Exception as e:
            Log.error(f"Failed to log security event: {e}")
            return False

    @staticmethod
    def log_admin_login(userName, ip_address, user_agent, success=True):
        """
        Log an admin login attempt.

        Args:
            userName (str): Username attempting login
            ip_address (str): IP address of the client
            user_agent (str): User agent string
            success (bool): Whether login was successful

        Returns:
            bool: True if logging was successful, False otherwise
        """
        event_type = "admin_login_success" if success else "admin_login_failure"
        details = "Successful admin login" if success else "Failed admin login attempt"

        return SecurityAuditLogger.log_event(
            event_type=event_type,
            userName=userName,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details,
        )

    @staticmethod
    def log_user_login(userName, ip_address, user_agent, success=True):
        """
        Log a user login attempt.

        Args:
            userName (str): Username attempting login
            ip_address (str): IP address of the client
            user_agent (str): User agent string
            success (bool): Whether login was successful

        Returns:
            bool: True if logging was successful, False otherwise
        """
        event_type = "user_login_success" if success else "user_login_failure"
        details = "Successful user login" if success else "Failed user login attempt"

        return SecurityAuditLogger.log_event(
            event_type=event_type,
            userName=userName,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details,
        )

    @staticmethod
    def log_admin_action(userName, ip_address, action, target=None):
        """
        Log an admin panel action.

        Args:
            userName (str): Admin username performing the action
            ip_address (str): IP address of the admin
            action (str): Description of the action (e.g., "deleted user", "changed role")
            target (str, optional): Target of the action (e.g., username being modified)

        Returns:
            bool: True if logging was successful, False otherwise
        """
        details = f"{action}"
        if target:
            details += f" | Target: {target}"

        return SecurityAuditLogger.log_event(
            event_type="admin_action",
            userName=userName,
            ip_address=ip_address,
            details=details,
        )

    @staticmethod
    def log_page_access(userName, ip_address, user_agent, path, method, status_code):
        """
        Log a page access event.

        Args:
            userName (str): Username accessing the page (None if not logged in)
            ip_address (str): IP address of the client
            user_agent (str): User agent string
            path (str): Request path
            method (str): HTTP method
            status_code (int): HTTP status code

        Returns:
            bool: True if logging was successful, False otherwise
        """
        return SecurityAuditLogger.log_event(
            event_type="page_access",
            userName=userName,
            ip_address=ip_address,
            user_agent=user_agent,
            path=path,
            method=method,
            status_code=status_code,
        )

    @staticmethod
    def log_rate_limit(identifier, ip_address, details=None):
        """
        Log a rate limiting event.

        Args:
            identifier (str): Identifier that triggered rate limit
            ip_address (str): IP address of the client
            details (str, optional): Additional details

        Returns:
            bool: True if logging was successful, False otherwise
        """
        return SecurityAuditLogger.log_event(
            event_type="rate_limit_triggered",
            userName=identifier,
            ip_address=ip_address,
            details=details or "Rate limit threshold exceeded",
        )
