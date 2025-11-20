"""
This file contains the form class for forced password change.
Used when admin users must change their password on first login.
"""

from wtforms import (
    Form,
    PasswordField,
    validators,
)


class ForceChangePasswordForm(Form):
    """
    This class creates a form for forced password change with complexity requirements.
    """

    password = PasswordField(
        "password",
        [
            validators.Length(min=12, message="Password must be at least 12 characters long"),
            validators.InputRequired(),
        ],
    )

    passwordConfirm = PasswordField(
        "passwordConfirm",
        [
            validators.Length(min=12, message="Password must be at least 12 characters long"),
            validators.InputRequired(),
        ],
    )
