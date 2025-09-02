"""
This file contains the blueprint for the logout page.

The functions and methods used in this blueprint are imported from their actual sources.
"""

from flask import Blueprint, redirect, session

from utils.flash_message import flash_message

logout_blueprint = Blueprint("logout", __name__)


@logout_blueprint.route("/logout")
def logout():
    """
    This function is the route for the logout page.
    It is used to log out the user.

    Returns:
        redirect: a redirect to the homepage
    """

    if "username" in session:
        language = session.get("language", "en")  # Get language before clearing session
        session.clear()
        flash_message(
            page="logout",
            message="success",
            category="success",
            language=language,
        )

    return redirect("/")
