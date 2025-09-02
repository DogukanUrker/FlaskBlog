"""
This file contains class that are used to create ChangeProfilePictureForm for the application.
"""

from wtforms import (
    Form,
    StringField,
    validators,
)


class ChangeProfilePictureForm(Form):
    """
    This class creates a form for changing the profile picture.
    """

    new_profile_picture_seed = StringField(
        "profile_picture_seed",
        [validators.InputRequired()],
    )
