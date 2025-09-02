"""
This file contains class that are used to create PasswordResetForm for the application.
"""

from wtforms import (
    EmailField,
    Form,
    PasswordField,
    StringField,
    validators,
)


class PasswordResetForm(Form):
    """
    This class creates a form for resetting the password.
    """

    username = StringField(
        "Username",
        [validators.Length(min=4, max=25), validators.InputRequired()],
    )

    email = EmailField(
        "Email",
        [validators.Length(min=6, max=50), validators.InputRequired()],
    )

    code = StringField(
        "code",
        [validators.Length(min=4, max=4), validators.InputRequired()],
    )

    password = PasswordField(
        "Password",
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
