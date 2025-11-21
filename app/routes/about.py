"""
This module contains the about page blueprint.
"""

import sqlite3
from flask import Blueprint, render_template
from settings import Settings
from utils.log import Log
from utils.markdown_renderer import SafeMarkdownRenderer

aboutBlueprint = Blueprint("about", __name__)


@aboutBlueprint.route("/about")
def about():
    """
    This function is used to render the about page.

    :param appName: The name of the application
    :type appName: str
    :return: The rendered about page
    :rtype: flask.Response
    """

    # Fetch custom about page settings from database
    about_settings = {}
    try:
        connection = sqlite3.connect(Settings.DB_USERS_ROOT)
        connection.set_trace_callback(Log.database)
        cursor = connection.cursor()

        setting_keys = [
            "about_title", "about_content", "about_show_version", "about_show_github",
            "about_github_url", "about_author_url", "about_credits"
        ]
        for key in setting_keys:
            cursor.execute(
                "SELECT setting_value FROM site_settings WHERE setting_key = ?",
                (key,)
            )
            result = cursor.fetchone()
            if result:
                about_settings[key] = result[0]

        connection.close()
    except Exception as e:
        Log.error(f"Error fetching about page settings: {e}")

    # Process custom content with markdown if provided
    custom_content = about_settings.get("about_content", "")
    if custom_content:
        renderer = SafeMarkdownRenderer()
        custom_content = renderer.render(custom_content)

    Log.info(
        f"Rendering about.html: params: appName={Settings.APP_NAME} and appVersion={Settings.APP_VERSION}"
    )

    return render_template(
        "about.html",
        appName=Settings.APP_NAME,
        appVersion=Settings.APP_VERSION,
        customTitle=about_settings.get("about_title", ""),
        customContent=custom_content,
        showVersion=about_settings.get("about_show_version", "True") == "True",
        showGithub=about_settings.get("about_show_github", "True") == "True",
        githubUrl=about_settings.get("about_github_url", ""),
        authorUrl=about_settings.get("about_author_url", ""),
        customCredits=about_settings.get("about_credits", "")
    )
