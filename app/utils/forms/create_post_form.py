"""
This file contains class that are used to create CreatePostForm for the application.
"""

from wtforms import (
    FileField,
    Form,
    SelectField,
    StringField,
    TextAreaField,
    validators,
)


class CreatePostForm(Form):
    """
    This class creates a form for creating a post.
    """

    post_title = StringField(
        "Post Title",
        [validators.Length(min=4, max=75), validators.InputRequired()],
    )

    post_content = TextAreaField(
        "Post Content",
        [validators.Length(min=50)],
    )

    post_banner = FileField("Post Banner")

    post_category = StringField(
        "Post Category",
        [validators.InputRequired()],
    )
