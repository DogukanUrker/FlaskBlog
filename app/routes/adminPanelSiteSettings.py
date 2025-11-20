"""
Admin panel route for site settings (logo upload, etc.)
"""

import sqlite3
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Blueprint, redirect, render_template, request, session
from werkzeug.utils import secure_filename
from settings import Settings
from utils.log import Log
from utils.flashMessage import flashMessage
from utils.fileUploadValidator import FileUploadValidator
from utils.time import currentTimeStamp
from utils.encryption import EncryptionUtil

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
                flashMessage(
                    page="adminSiteSettings",
                    message="logoNoFile",
                    category="error",
                    language=session.get("language", "en")
                )
                connection.close()
                return redirect("/admin/site-settings")

            file = request.files["site_logo"]

            if file.filename == "":
                flashMessage(
                    page="adminSiteSettings",
                    message="logoNoSelection",
                    category="error",
                    language=session.get("language", "en")
                )
                connection.close()
                return redirect("/admin/site-settings")

            # Validate file extension (manually for logo since we support .ico)
            allowed_extensions = {"ico", "png", "jpg", "jpeg", "webp"}
            file_ext = os.path.splitext(secure_filename(file.filename))[1].lower().lstrip(".")

            if file_ext not in allowed_extensions:
                flashMessage(
                    page="adminSiteSettings",
                    message="logoInvalidType",
                    category="error",
                    language=session.get("language", "en")
                )
                connection.close()
                return redirect("/admin/site-settings")

            # Validate file size
            file_data = file.read()
            file.seek(0)
            if len(file_data) > Settings.MAX_UPLOAD_SIZE:
                flashMessage(
                    page="adminSiteSettings",
                    message="logoTooLarge",
                    category="error",
                    language=session.get("language", "en")
                )
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

                flashMessage(
                    page="adminSiteSettings",
                    message="logoSuccess",
                    category="success",
                    language=session.get("language", "en")
                )
                Log.success(f"Admin {session['userName']} updated site logo")

            except Exception as e:
                flashMessage(
                    page="adminSiteSettings",
                    message="logoError",
                    category="error",
                    language=session.get("language", "en")
                )
                Log.error(f"Logo upload failed: {e}")

            connection.close()
            return redirect("/admin/site-settings")

        # Handle default profile picture upload
        elif upload_type == "default_profile_picture":
            if "default_profile_picture" not in request.files:
                flashMessage(
                    page="adminSiteSettings",
                    message="profileNoFile",
                    category="error",
                    language=session.get("language", "en")
                )
                connection.close()
                return redirect("/admin/site-settings")

            file = request.files["default_profile_picture"]

            if file.filename == "":
                flashMessage(
                    page="adminSiteSettings",
                    message="profileNoSelection",
                    category="error",
                    language=session.get("language", "en")
                )
                connection.close()
                return redirect("/admin/site-settings")

            # Validate file
            is_valid, error_code, file_data = FileUploadValidator.validate_file(file)
            if not is_valid:
                Log.error(f"Default profile picture upload failed: {error_code}")
                flashMessage(
                    page="adminSiteSettings",
                    message="profileInvalid",
                    category="error",
                    language=session.get("language", "en")
                )
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

                flashMessage(
                    page="adminSiteSettings",
                    message="profileSuccess",
                    category="success",
                    language=session.get("language", "en")
                )
                Log.success(f"Admin {session['userName']} updated default profile picture")

            except Exception as e:
                flashMessage(
                    page="adminSiteSettings",
                    message="profileError",
                    category="error",
                    language=session.get("language", "en")
                )
                Log.error(f"Default profile picture upload failed: {e}")

            connection.close()
            return redirect("/admin/site-settings")

        # Handle SMTP configuration
        elif upload_type == "smtp_config":
            smtp_server = request.form.get("smtp_server", "").strip()
            smtp_port = request.form.get("smtp_port", "").strip()
            smtp_mail = request.form.get("smtp_mail", "").strip()
            smtp_password = request.form.get("smtp_password", "").strip()

            try:
                # Validate port
                if smtp_port:
                    smtp_port_int = int(smtp_port)
                    if smtp_port_int < 1 or smtp_port_int > 65535:
                        raise ValueError("Invalid port number")

                # Save SMTP settings to database
                smtp_settings = [
                    ("smtp_server", smtp_server),
                    ("smtp_port", smtp_port),
                    ("smtp_mail", smtp_mail),
                ]

                # Only update password if provided (to allow keeping existing password)
                # Encrypt the password before storing
                if smtp_password:
                    encrypted_password = EncryptionUtil.encrypt(smtp_password)
                    smtp_settings.append(("smtp_password", encrypted_password))

                for key, value in smtp_settings:
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
                    page="adminSiteSettings",
                    message="smtpSuccess",
                    category="success",
                    language=session.get("language", "en")
                )
                Log.success(f"Admin {session['userName']} updated SMTP configuration")

            except ValueError as e:
                flashMessage(
                    page="adminSiteSettings",
                    message="smtpInvalidPort",
                    category="error",
                    language=session.get("language", "en")
                )
                Log.error(f"SMTP configuration failed: {e}")
            except Exception as e:
                flashMessage(
                    page="adminSiteSettings",
                    message="smtpError",
                    category="error",
                    language=session.get("language", "en")
                )
                Log.error(f"SMTP configuration failed: {e}")

            connection.close()
            return redirect("/admin/site-settings")

        # Handle SMTP test email
        elif upload_type == "smtp_test":
            test_email = request.form.get("test_email", "").strip()

            if not test_email:
                flashMessage(
                    page="adminSiteSettings",
                    message="smtpTestNoEmail",
                    category="error",
                    language=session.get("language", "en")
                )
                connection.close()
                return redirect("/admin/site-settings")

            try:
                # Get SMTP settings from database
                smtp_config = {}
                for key in ["smtp_server", "smtp_port", "smtp_mail", "smtp_password"]:
                    cursor.execute(
                        "SELECT setting_value FROM site_settings WHERE setting_key = ?",
                        (key,)
                    )
                    result = cursor.fetchone()
                    if result and result[0]:
                        smtp_config[key] = result[0]
                    else:
                        # Fall back to Settings defaults
                        if key == "smtp_server":
                            smtp_config[key] = Settings.SMTP_SERVER
                        elif key == "smtp_port":
                            smtp_config[key] = str(Settings.SMTP_PORT)
                        elif key == "smtp_mail":
                            smtp_config[key] = Settings.SMTP_MAIL
                        else:
                            smtp_config[key] = Settings.SMTP_PASSWORD

                # Decrypt the password
                if smtp_config.get("smtp_password"):
                    smtp_config["smtp_password"] = EncryptionUtil.decrypt(smtp_config["smtp_password"])

                # Check if SMTP is configured
                if not smtp_config.get("smtp_mail") or not smtp_config.get("smtp_password"):
                    flashMessage(
                        page="adminSiteSettings",
                        message="smtpTestNotConfigured",
                        category="error",
                        language=session.get("language", "en")
                    )
                    connection.close()
                    return redirect("/admin/site-settings")

                # Create test email
                msg = MIMEMultipart()
                msg['From'] = smtp_config['smtp_mail']
                msg['To'] = test_email
                msg['Subject'] = "FlaskBlog SMTP Test"

                body = """
This is a test email from FlaskBlog.

If you received this email, your SMTP configuration is working correctly!

Configuration:
- Server: {server}
- Port: {port}
- Email: {email}

Best regards,
FlaskBlog Admin Panel
                """.format(
                    server=smtp_config['smtp_server'],
                    port=smtp_config['smtp_port'],
                    email=smtp_config['smtp_mail']
                )

                msg.attach(MIMEText(body, 'plain'))

                # Send email
                server = smtplib.SMTP(smtp_config['smtp_server'], int(smtp_config['smtp_port']))
                server.starttls()
                server.login(smtp_config['smtp_mail'], smtp_config['smtp_password'])
                server.sendmail(smtp_config['smtp_mail'], test_email, msg.as_string())
                server.quit()

                flashMessage(
                    page="adminSiteSettings",
                    message="smtpTestSuccess",
                    category="success",
                    language=session.get("language", "en")
                )
                Log.success(f"Admin {session['userName']} sent test email to {test_email}")

            except smtplib.SMTPAuthenticationError as e:
                flashMessage(
                    page="adminSiteSettings",
                    message="smtpTestAuthError",
                    category="error",
                    language=session.get("language", "en")
                )
                Log.error(f"SMTP test failed - authentication error: {e}")
            except smtplib.SMTPException as e:
                flashMessage(
                    page="adminSiteSettings",
                    message="smtpTestError",
                    category="error",
                    language=session.get("language", "en")
                )
                Log.error(f"SMTP test failed: {e}")
            except Exception as e:
                flashMessage(
                    page="adminSiteSettings",
                    message="smtpTestError",
                    category="error",
                    language=session.get("language", "en")
                )
                Log.error(f"SMTP test failed: {e}")

            connection.close()
            return redirect("/admin/site-settings")

        # Handle default banner upload
        elif upload_type == "default_banner":
            if "default_banner" not in request.files:
                flashMessage(
                    page="adminSiteSettings",
                    message="bannerNoFile",
                    category="error",
                    language=session.get("language", "en")
                )
                connection.close()
                return redirect("/admin/site-settings")

            file = request.files["default_banner"]

            if file.filename == "":
                flashMessage(
                    page="adminSiteSettings",
                    message="bannerNoSelection",
                    category="error",
                    language=session.get("language", "en")
                )
                connection.close()
                return redirect("/admin/site-settings")

            # Validate file
            is_valid, error_code, file_data = FileUploadValidator.validate_file(file)
            if not is_valid:
                Log.error(f"Default banner upload failed: {error_code}")
                flashMessage(
                    page="adminSiteSettings",
                    message="bannerInvalid",
                    category="error",
                    language=session.get("language", "en")
                )
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

                flashMessage(
                    page="adminSiteSettings",
                    message="bannerSuccess",
                    category="success",
                    language=session.get("language", "en")
                )
                Log.success(f"Admin {session['userName']} updated default banner")

            except Exception as e:
                flashMessage(
                    page="adminSiteSettings",
                    message="bannerError",
                    category="error",
                    language=session.get("language", "en")
                )
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

    # Get SMTP settings
    smtp_settings = {}
    for key in ["smtp_server", "smtp_port", "smtp_mail", "smtp_password"]:
        cursor.execute(
            "SELECT setting_value FROM site_settings WHERE setting_key = ?",
            (key,)
        )
        result = cursor.fetchone()
        if result:
            smtp_settings[key] = result[0]
        else:
            # Fall back to Settings defaults
            if key == "smtp_server":
                smtp_settings[key] = Settings.SMTP_SERVER
            elif key == "smtp_port":
                smtp_settings[key] = str(Settings.SMTP_PORT)
            elif key == "smtp_mail":
                smtp_settings[key] = Settings.SMTP_MAIL
            else:
                smtp_settings[key] = ""

    connection.close()

    Log.info(f"Admin {session['userName']} viewing site settings page")

    return render_template(
        "adminPanelSiteSettings.html",
        currentLogo=current_logo,
        currentDefaultProfile=current_default_profile,
        currentDefaultBanner=current_default_banner,
        smtpServer=smtp_settings.get("smtp_server", ""),
        smtpPort=smtp_settings.get("smtp_port", ""),
        smtpMail=smtp_settings.get("smtp_mail", ""),
        smtpPasswordSet=bool(smtp_settings.get("smtp_password", ""))
    )
