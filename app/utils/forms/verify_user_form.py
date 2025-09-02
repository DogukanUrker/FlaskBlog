"""
This file contains class that are used to create VerifyUserForm for the application.
"""

from wtforms import (
    Form,
    StringField,
    validators,
)


class VerifyUserForm(Form):
    """
    This class creates a form for verifying the user.
    """

    code = StringField(
        "code",
        [validators.Length(min=4, max=4), validators.InputRequired()],
    )
