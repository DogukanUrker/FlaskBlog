"""
Password Complexity Validator

This module provides functions to validate password complexity
according to cryptographic security best practices.

Requirements:
- Minimum 12 characters
- At least 1 uppercase letter
- At least 1 lowercase letter
- At least 1 digit
- At least 1 special character
"""

import re
from typing import Tuple, List


class PasswordComplexityValidator:
    """
    Validates password complexity for cryptographic security.
    """

    # Minimum password length
    MIN_LENGTH = 12

    # Regular expressions for character type checks
    UPPERCASE_PATTERN = re.compile(r'[A-Z]')
    LOWERCASE_PATTERN = re.compile(r'[a-z]')
    DIGIT_PATTERN = re.compile(r'[0-9]')
    SPECIAL_PATTERN = re.compile(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?`~]')

    @classmethod
    def validate(cls, password: str) -> Tuple[bool, List[str]]:
        """
        Validates a password against complexity requirements.

        Args:
            password (str): The password to validate.

        Returns:
            Tuple[bool, List[str]]: A tuple containing:
                - bool: True if password meets all requirements, False otherwise
                - List[str]: List of error codes for failed requirements
        """
        errors = []

        if len(password) < cls.MIN_LENGTH:
            errors.append("minLength")

        if not cls.UPPERCASE_PATTERN.search(password):
            errors.append("uppercase")

        if not cls.LOWERCASE_PATTERN.search(password):
            errors.append("lowercase")

        if not cls.DIGIT_PATTERN.search(password):
            errors.append("digit")

        if not cls.SPECIAL_PATTERN.search(password):
            errors.append("special")

        return (len(errors) == 0, errors)

    @classmethod
    def get_requirements_list(cls) -> List[str]:
        """
        Returns a list of all password requirements.

        Returns:
            List[str]: List of requirement descriptions
        """
        return [
            f"At least {cls.MIN_LENGTH} characters",
            "At least 1 uppercase letter (A-Z)",
            "At least 1 lowercase letter (a-z)",
            "At least 1 digit (0-9)",
            "At least 1 special character (!@#$%^&*...)"
        ]
