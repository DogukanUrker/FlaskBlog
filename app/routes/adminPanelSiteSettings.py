"""
Admin panel route for site settings (logo upload, etc.)
"""

import sqlite3
import os
from flask import Blueprint, redirect, render_template, request, session
from werkzeug.utils import secure_filename
from settings import Settings
from utils.log import Log
from utils.flashMessage import flashMessage
from utils.fileUploadValidator import FileUploadValidator
from utils.time import currentTimeStamp

adminPanelSiteSettingsBlueprint = Blueprint("adminPanelSiteSettings", __name__)


@adminPanelSiteSettingsBlueprint.route("/admin/site-settings", methods=["GET", "POST"])
def adminPanelSiteSettings():
    """
    Admin panel page for managing site settings like logo.
    Only accessible by admin users.
    """
    if "userName" not in session:
        Log.error(f"{request.remote_addr} tried to reach admin site settings without being logged in")
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
        Log.error(f"{request.remote_addr} ({session['userName']}) tried to reach admin site settings without admin role")
        return redirect("/")

    # Handle POST request (logo upload)
    if request.method == "POST":
        if "site_logo" not in request.files:
            flashMessage("error", "No logo file provided")
            connection.close()
            return redirect("/admin/site-settings")

        file = request.files["site_logo"]

        if file.filename == "":
            flashMessage("error", "No file selected")
            connection.close()
            return redirect("/admin/site-settings")

        # Validate file extension (manually for logo since we support .ico)
        allowed_extensions = {"ico", "png", "jpg", "jpeg", "webp"}
        file_ext = os.path.splitext(secure_filename(file.filename))[1].lower().lstrip(".")

        if file_ext not in allowed_extensions:
            flashMessage("error", "Invalid file type. Allowed: .ico, .png, .jpg, .jpeg, .webp")
            connection.close()
            return redirect("/admin/site-settings")

        # Validate file size
        file_data = file.read()
        file.seek(0)
        if len(file_data) > Settings.MAX_UPLOAD_SIZE:
            flashMessage("error", f"File too large. Maximum size: {Settings.MAX_UPLOAD_SIZE / (1024*1024):.1f}MB")
            connection.close()
            return redirect("/admin/site-settings")

        # Save file
        try:
            filename = "site_logo" + os.path.splitext(secure_filename(file.filename))[1]
            upload_path = os.path.join(Settings.APP_ROOT_PATH, "static", "uploads", filename)

            # Remove old logo if exists
            for ext in [".ico", ".png", ".jpg", ".jpeg", ".svg", ".webp"]:
                old_logo = os.path.join(Settings.APP_ROOT_PATH, "static", "uploads", f"site_logo{ext}")
                if os.path.exists(old_logo):
                    os.remove(old_logo)
                    Log.info(f"Removed old logo: {old_logo}")

            file.save(upload_path)
            Log.success(f"Logo saved to: {upload_path}")

            # Update database
            logo_path = f"/static/uploads/{filename}"
            cursor.execute(
                "UPDATE site_settings SET setting_value = ?, updated_at = ? WHERE setting_key = ?",
                (logo_path, currentTimeStamp(), "site_logo")
            )
            connection.commit()

            flashMessage("success", "Site logo updated successfully")
            Log.success(f"Admin {session['userName']} updated site logo")

        except Exception as e:
            flashMessage("error", f"Failed to upload logo: {str(e)}")
            Log.error(f"Logo upload failed: {e}")

        connection.close()
        return redirect("/admin/site-settings")

    # GET request - show current settings
    cursor.execute(
        "SELECT setting_value FROM site_settings WHERE setting_key = ?",
        ("site_logo",)
    )

    logo_result = cursor.fetchone()
    current_logo = logo_result[0] if logo_result else "/static/uploads/site_logo.ico"

    connection.close()

    Log.info(f"Admin {session['userName']} viewing site settings page")

    return render_template(
        "adminPanelSiteSettings.html",
        currentLogo=current_logo
    )
