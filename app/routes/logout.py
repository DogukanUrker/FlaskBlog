"""
This file contains the blueprint for the logout page.

The functions and methods used in this blueprint are imported from their actual sources.
"""

from flask import Blueprint, redirect, request, session
from utils.flashMessage import flashMessage
from utils.log import Log

logoutBlueprint = Blueprint("logout", __name__)


@logoutBlueprint.route("/logout")
def logout():
    """
    This function handles the logout process.

    It checks if the user is logged in. If they are, their session is cleared and they are redirected
    to the homepage. A message is also displayed indicating that the user has been logged out.

    If the user is not logged in, a message is displayed indicating that they are not logged in.
    The user is then redirected to the homepage.
    """
    if "userName" in session:
        Log.success(f"User: {session['userName']} logged out")
        flashMessage(
            page="logout",
            message="success",
            category="success",
            language=session["language"],
        )
        session.pop("userName", None)
        session.pop("userRole", None)
        return redirect("/")
    else:
        Log.error(f"{request.remote_addr} tried to logout without being logged in")
        return redirect("/")
