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

    # Handle POST request (file uploads)
    if request.method == "POST":
        upload_type = request.form.get("upload_type")

        # Handle site logo upload
        if upload_type == "site_logo":
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

        # Handle default profile picture upload
        elif upload_type == "default_profile_picture":
            if "default_profile_picture" not in request.files:
                flashMessage("error", "No profile picture file provided")
                connection.close()
                return redirect("/admin/site-settings")

            file = request.files["default_profile_picture"]

            if file.filename == "":
                flashMessage("error", "No file selected")
                connection.close()
                return redirect("/admin/site-settings")

            # Validate file
            is_valid, error_code, file_data = FileUploadValidator.validate_file(file)
            if not is_valid:
                Log.error(f"Default profile picture upload failed: {error_code}")
                flashMessage("error", f"Invalid file. Error: {error_code}")
                connection.close()
                return redirect("/admin/site-settings")

            # Save file
            try:
                upload_dir = os.path.join(Settings.APP_ROOT_PATH, "static", "uploads", "defaults")
                os.makedirs(upload_dir, exist_ok=True)

                file_extension = os.path.splitext(secure_filename(file.filename))[1]
                filename = f"default_profile_picture{file_extension}"
                upload_path = os.path.join(upload_dir, filename)

                # Remove old default profile picture if exists
                for ext in [".jpg", ".jpeg", ".png", ".webp"]:
                    old_file = os.path.join(upload_dir, f"default_profile_picture{ext}")
                    if os.path.exists(old_file):
                        os.remove(old_file)
                        Log.info(f"Removed old default profile picture: {old_file}")

                file.save(upload_path)
                Log.success(f"Default profile picture saved to: {upload_path}")

                # Update or insert database setting
                picture_path = f"/static/uploads/defaults/{filename}"
                cursor.execute(
                    "SELECT setting_id FROM site_settings WHERE setting_key = ?",
                    ("default_profile_picture",)
                )
                if cursor.fetchone():
                    cursor.execute(
                        "UPDATE site_settings SET setting_value = ?, updated_at = ? WHERE setting_key = ?",
                        (picture_path, currentTimeStamp(), "default_profile_picture")
                    )
                else:
                    cursor.execute(
                        "INSERT INTO site_settings(setting_key, setting_value, updated_at) VALUES(?, ?, ?)",
                        ("default_profile_picture", picture_path, currentTimeStamp())
                    )
                connection.commit()

                flashMessage("success", "Default profile picture updated successfully")
                Log.success(f"Admin {session['userName']} updated default profile picture")

            except Exception as e:
                flashMessage("error", f"Failed to upload default profile picture: {str(e)}")
                Log.error(f"Default profile picture upload failed: {e}")

            connection.close()
            return redirect("/admin/site-settings")

        # Handle default banner upload
        elif upload_type == "default_banner":
            if "default_banner" not in request.files:
                flashMessage("error", "No banner file provided")
                connection.close()
                return redirect("/admin/site-settings")

            file = request.files["default_banner"]

            if file.filename == "":
                flashMessage("error", "No file selected")
                connection.close()
                return redirect("/admin/site-settings")

            # Validate file
            is_valid, error_code, file_data = FileUploadValidator.validate_file(file)
            if not is_valid:
                Log.error(f"Default banner upload failed: {error_code}")
                flashMessage("error", f"Invalid file. Error: {error_code}")
                connection.close()
                return redirect("/admin/site-settings")

            # Save file
            try:
                upload_dir = os.path.join(Settings.APP_ROOT_PATH, "static", "uploads", "defaults")
                os.makedirs(upload_dir, exist_ok=True)

                file_extension = os.path.splitext(secure_filename(file.filename))[1]
                filename = f"default_banner{file_extension}"
                upload_path = os.path.join(upload_dir, filename)

                # Remove old default banner if exists
                for ext in [".jpg", ".jpeg", ".png", ".webp"]:
                    old_file = os.path.join(upload_dir, f"default_banner{ext}")
                    if os.path.exists(old_file):
                        os.remove(old_file)
                        Log.info(f"Removed old default banner: {old_file}")

                file.save(upload_path)
                Log.success(f"Default banner saved to: {upload_path}")

                # Update or insert database setting
                banner_path = f"/static/uploads/defaults/{filename}"
                cursor.execute(
                    "SELECT setting_id FROM site_settings WHERE setting_key = ?",
                    ("default_banner",)
                )
                if cursor.fetchone():
                    cursor.execute(
                        "UPDATE site_settings SET setting_value = ?, updated_at = ? WHERE setting_key = ?",
                        (banner_path, currentTimeStamp(), "default_banner")
                    )
                else:
                    cursor.execute(
                        "INSERT INTO site_settings(setting_key, setting_value, updated_at) VALUES(?, ?, ?)",
                        ("default_banner", banner_path, currentTimeStamp())
                    )
                connection.commit()

                flashMessage("success", "Default banner updated successfully")
                Log.success(f"Admin {session['userName']} updated default banner")

            except Exception as e:
                flashMessage("error", f"Failed to upload default banner: {str(e)}")
                Log.error(f"Default banner upload failed: {e}")

            connection.close()
            return redirect("/admin/site-settings")

    # GET request - show current settings
    cursor.execute(
        "SELECT setting_value FROM site_settings WHERE setting_key = ?",
        ("site_logo",)
    )
    logo_result = cursor.fetchone()
    current_logo = logo_result[0] if logo_result else "/static/uploads/site_logo.ico"

    cursor.execute(
        "SELECT setting_value FROM site_settings WHERE setting_key = ?",
        ("default_profile_picture",)
    )
    profile_result = cursor.fetchone()
    current_default_profile = profile_result[0] if profile_result else None

    cursor.execute(
        "SELECT setting_value FROM site_settings WHERE setting_key = ?",
        ("default_banner",)
    )
    banner_result = cursor.fetchone()
    current_default_banner = banner_result[0] if banner_result else None

    connection.close()

    Log.info(f"Admin {session['userName']} viewing site settings page")

    return render_template(
        "adminPanelSiteSettings.html",
        currentLogo=current_logo,
        currentDefaultProfile=current_default_profile,
        currentDefaultBanner=current_default_banner
    )
