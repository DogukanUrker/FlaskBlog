"""
This module contains the about page blueprint.
"""

from flask import Blueprint, render_template

from settings import Settings
from utils.log import Log

about_blueprint = Blueprint("about", __name__)


@about_blueprint.route("/about")
def about():
    """
    This function is used to render the about page.

    :param app_name: The name of the application
    :type app_name: str
    :return: The rendered about page
    :rtype: flask.Response
    """

    Log.info(
        f"Rendering about.html: params: app_name={Settings.APP_NAME} and app_version={Settings.APP_VERSION}"
    )

    return render_template(
        "about.html", app_name=Settings.APP_NAME, app_version=Settings.APP_VERSION
    )
