"""
This file contains class that are used to create ChangeProfilePictureForm for the application.
"""

from wtforms import (
    FileField,
    Form,
    StringField,
    validators,
)


class ChangeProfilePictureForm(Form):
    """
    This class creates a form for changing the profile picture.
    """

    newProfilePictureSeed = StringField(
        "ProfilePictureSeed",
        [validators.Optional()],
    )

    profilePictureFile = FileField(
        "Profile Picture File"
    )
