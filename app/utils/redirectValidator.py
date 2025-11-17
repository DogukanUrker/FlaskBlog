"""
This module contains redirect URL validation utilities for security.
"""

from urllib.parse import urlparse
from flask import request
from utils.log import Log


class RedirectValidator:
    """
    Validates redirect URLs to prevent open redirect vulnerabilities.
    """

    @staticmethod
    def is_safe_url(target):
        """
        Check if the target URL is safe for redirecting.

        A URL is considered safe if:
        1. It's a relative URL (no scheme or netloc)
        2. It's an absolute URL to the same host

        Args:
            target: The URL to validate

        Returns:
            bool: True if safe, False otherwise
        """
        if not target:
            return False

        # Parse the target URL
        target_parsed = urlparse(target)

        # Parse the request URL to get current host
        request_parsed = urlparse(request.host_url)

        # Check if it's a relative URL (no scheme and no netloc)
        if not target_parsed.scheme and not target_parsed.netloc:
            # It's a relative URL, which is safe
            return True

        # If it has a scheme or netloc, check if it matches the current host
        if target_parsed.netloc == request_parsed.netloc:
            return True

        # Otherwise, it's not safe
        Log.warning(f"Unsafe redirect attempt to: {target}")
        return False

    @staticmethod
    def safe_redirect_path(encoded_path):
        """
        Safely decode a redirect path parameter.

        The application uses & as / replacement in redirect parameters.
        This function validates and sanitizes the decoded path.

        Args:
            encoded_path: Path with & instead of /

        Returns:
            str: Safe redirect path or "/" if invalid
        """
        if not encoded_path:
            return "/"

        # Decode the path (& -> /)
        decoded_path = encoded_path.replace("&", "/")

        # Ensure it starts with /
        if not decoded_path.startswith("/"):
            decoded_path = "/" + decoded_path

        # Validate the decoded path
        if RedirectValidator.is_safe_url(decoded_path):
            return decoded_path
        else:
            # If validation fails, redirect to home
            Log.error(
                f"Invalid redirect path: {encoded_path} (decoded: {decoded_path}), redirecting to /"
            )
            return "/"
