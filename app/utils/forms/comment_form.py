"""
This file contains class that are used to create CommentForm for the application.
"""

from wtforms import (
    Form,
    TextAreaField,
    validators,
)


class CommentForm(Form):
    """
    This class creates a form for commenting.
    """

    comment = TextAreaField(
        "Comment",
        [validators.Length(min=20, max=500), validators.InputRequired()],
    )
