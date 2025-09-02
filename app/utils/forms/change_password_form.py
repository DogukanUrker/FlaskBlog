"""
This file contains class that are used to create ChangePasswordForm for the application.
"""

from wtforms import (
    Form,
    PasswordField,
    validators,
)


class ChangePasswordForm(Form):
    """
    This class creates a form for changing the password.
    """

    old_password = PasswordField(
        "old_password",
        [
            validators.Length(min=8),
            validators.InputRequired(),
        ],
    )

    password = PasswordField(
        "password",
        [
            validators.Length(min=8),
            validators.InputRequired(),
        ],
    )

    password_confirm = PasswordField(
        "password_confirm",
        [
            validators.Length(min=8),
            validators.InputRequired(),
        ],
    )
