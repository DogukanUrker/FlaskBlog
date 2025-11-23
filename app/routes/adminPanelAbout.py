"""
Admin panel route for editing the about page content.
"""

import sqlite3
from flask import Blueprint, redirect, render_template, request, session
from settings import Settings
from utils.log import Log
from utils.flashMessage import flashMessage
from utils.time import currentTimeStamp

adminPanelAboutBlueprint = Blueprint("adminPanelAbout", __name__)


@adminPanelAboutBlueprint.route("/admin/about", methods=["GET", "POST"])
def adminPanelAbout():
    """
    Admin panel page for managing about page content.
    Only accessible by admin users.
    """
    if "userName" not in session:
        Log.error(f"{request.remote_addr} tried to reach admin about settings without being logged in")
        return redirect("/")

    # Check if user is admin
    connection = sqlite3.connect(Settings.DB_USERS_ROOT)
    connection.set_trace_callback(Log.database)
    cursor = connection.cursor()

    cursor.execute(
        "SELECT role FROM users WHERE userName = ?",
        (session["userName"],)
    )

    user_data = cursor.fetchone()

    if not user_data or user_data[0] != "admin":
        connection.close()
        Log.error(f"{request.remote_addr} ({session['userName']}) tried to reach admin about settings without admin role")
        return redirect("/")

    # Handle POST request (save about page content)
    if request.method == "POST":
        about_title = request.form.get("about_title", "").strip()
        about_content = request.form.get("about_content", "").strip()
        about_show_version = "True" if request.form.get("about_show_version") else "False"
        about_show_github = "True" if request.form.get("about_show_github") else "False"
        about_github_url = request.form.get("about_github_url", "").strip()
        about_author_url = request.form.get("about_author_url", "").strip()
        about_credits = request.form.get("about_credits", "").strip()

        try:
            # Save about page settings to database
            about_settings = [
                ("about_title", about_title),
                ("about_content", about_content),
                ("about_show_version", about_show_version),
                ("about_show_github", about_show_github),
                ("about_github_url", about_github_url),
                ("about_author_url", about_author_url),
                ("about_credits", about_credits),
            ]

            for key, value in about_settings:
                cursor.execute(
                    "SELECT setting_id FROM site_settings WHERE setting_key = ?",
                    (key,)
                )
                if cursor.fetchone():
                    cursor.execute(
                        "UPDATE site_settings SET setting_value = ?, updated_at = ? WHERE setting_key = ?",
                        (value, currentTimeStamp(), key)
                    )
                else:
                    cursor.execute(
                        "INSERT INTO site_settings(setting_key, setting_value, updated_at) VALUES(?, ?, ?)",
                        (key, value, currentTimeStamp())
                    )

            connection.commit()

            flashMessage(
                page="adminAbout",
                message="saveSuccess",
                category="success",
                language=session.get("language", "en")
            )
            Log.success(f"Admin {session['userName']} updated about page content")

        except Exception as e:
            flashMessage(
                page="adminAbout",
                message="saveError",
                category="error",
                language=session.get("language", "en")
            )
            Log.error(f"About page update failed: {e}")

        connection.close()
        return redirect("/admin/about")

    # GET request - retrieve current about page settings
    about_settings = {}
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
        else:
            # Set defaults
            about_settings[key] = ""
            if key == "about_show_version":
                about_settings[key] = "True"
            elif key == "about_show_github":
                about_settings[key] = "True"

    connection.close()

    Log.info(f"Admin {session['userName']} viewing about page editor")

    return render_template(
        "adminPanelAbout.html",
        aboutTitle=about_settings.get("about_title", ""),
        aboutContent=about_settings.get("about_content", ""),
        aboutShowVersion=about_settings.get("about_show_version", "True") == "True",
        aboutShowGithub=about_settings.get("about_show_github", "True") == "True",
        aboutGithubUrl=about_settings.get("about_github_url", ""),
        aboutAuthorUrl=about_settings.get("about_author_url", ""),
        aboutCredits=about_settings.get("about_credits", ""),
        appName=Settings.APP_NAME,
        appVersion=Settings.APP_VERSION
    )
