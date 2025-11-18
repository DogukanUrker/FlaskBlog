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

    oldPassword = PasswordField(
        "oldPassword",
        [
            validators.InputRequired(),
        ],
    )

    password = PasswordField(
        "password",
        [
            validators.Length(min=8, message="Password must be at least 8 characters long"),
            validators.InputRequired(),
        ],
    )

    passwordConfirm = PasswordField(
        "passwordConfirm",
        [
            validators.Length(min=8, message="Password must be at least 8 characters long"),
            validators.InputRequired(),
        ],
    )
