"""
This file contains class that are used to create LoginForm for the application.
"""

from wtforms import (
    Form,
    PasswordField,
    StringField,
    validators,
)


class LoginForm(Form):
    """
    This class creates a form for logging in.
    """

    username = StringField(
        "Username",
        [validators.Length(min=4, max=25), validators.InputRequired()],
    )

    password = PasswordField(
        "Password",
        [validators.Length(min=5), validators.InputRequired()],
    )
