"""
This file contains class that are used to create ChangeBannerForm for the application.
"""

from wtforms import (
    FileField,
    Form,
)


class ChangeBannerForm(Form):
    """
    This class creates a form for changing the profile banner.
    """

    bannerFile = FileField("Profile Banner File")
