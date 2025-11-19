"""
Form for uploading images to user gallery.
"""

from wtforms import FileField, Form, StringField, validators


class ImageUploadForm(Form):
    """This class creates a form for uploading images to user gallery."""

    imageFile = FileField("Image File")

    title = StringField(
        "Image Title",
        [validators.Optional(), validators.Length(max=100)],
    )

    description = StringField(
        "Image Description",
        [validators.Optional(), validators.Length(max=500)],
    )
