import sqlite3
import os

from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    session,
)
from werkzeug.utils import secure_filename
from settings import Settings
from utils.flashMessage import flashMessage
from utils.forms.ChangeBannerForm import ChangeBannerForm
from utils.log import Log
from utils.fileUploadValidator import FileUploadValidator

changeBannerBlueprint = Blueprint("changeBanner", __name__)


@changeBannerBlueprint.route("/changebanner", methods=["GET", "POST"])
def changeBanner():
    """
    Route for users to change their profile banner.
    Supports uploading local image files (jpg, jpeg, png, webp).
    """
    if "userName" in session:
        form = ChangeBannerForm(request.form)

        if request.method == "POST":
            newBanner = None

            # Check if file was uploaded
            if "bannerFile" in request.files:
                file = request.files["bannerFile"]

                if file and file.filename != "":
                    # Validate file
                    is_valid, error_code, file_data = FileUploadValidator.validate_file(
                        file
                    )
                    if not is_valid:
                        Log.error(f"Banner upload failed: {error_code}")
                        flashMessage(
                            page="changeBanner",
                            message="error",
                            category="error",
                            language=session["language"],
                        )
                        return redirect("/changebanner")

                    # Create profile_banners directory if it doesn't exist
                    upload_dir = os.path.join(
                        Settings.APP_ROOT_PATH, "static", "uploads", "profile_banners"
                    )
                    os.makedirs(upload_dir, exist_ok=True)

                    # Generate filename based on username
                    file_extension = os.path.splitext(secure_filename(file.filename))[1]
                    filename = f"{session['userName']}_banner{file_extension}"
                    upload_path = os.path.join(upload_dir, filename)

                    # Remove old banner if exists
                    for ext in [".jpg", ".jpeg", ".png", ".webp"]:
                        old_file = os.path.join(
                            upload_dir, f"{session['userName']}_banner{ext}"
                        )
                        if os.path.exists(old_file):
                            os.remove(old_file)
                            Log.info(f"Removed old banner: {old_file}")

                    # Save new file
                    try:
                        file.save(upload_path)
                        newBanner = f"/static/uploads/profile_banners/{filename}"
                        Log.success(f"Banner saved to: {upload_path}")
                    except Exception as e:
                        Log.error(f"Failed to save banner: {e}")
                        flashMessage(
                            page="changeBanner",
                            message="error",
                            category="error",
                            language=session["language"],
                        )
                        return redirect("/changebanner")

            # If no file uploaded, show error
            if not newBanner:
                flashMessage(
                    page="changeBanner",
                    message="error",
                    category="error",
                    language=session["language"],
                )
                return redirect("/changebanner")

            # Update database
            Log.database(f"Connecting to '{Settings.DB_USERS_ROOT}' database")

            connection = sqlite3.connect(Settings.DB_USERS_ROOT)
            connection.set_trace_callback(Log.database)
            cursor = connection.cursor()

            cursor.execute(
                """update users set banner = ? where userName = ? """,
                [(newBanner), (session["userName"])],
            )
            connection.commit()
            connection.close()

            Log.success(
                f'User: "{session["userName"]}" changed banner to "{newBanner}"',
            )
            flashMessage(
                page="changeBanner",
                message="success",
                category="success",
                language=session["language"],
            )

            return redirect("/changebanner")

        return render_template(
            "changeBanner.html",
            form=form,
        )
    else:
        Log.error(
            f"{request.remote_addr} tried to change banner without being logged in"
        )

        return redirect("/")


@changeBannerBlueprint.route("/removebanner", methods=["POST"])
def removeBanner():
    """
    Route for users to remove their profile banner.
    """
    if "userName" in session:
        # Remove banner file if exists
        upload_dir = os.path.join(
            Settings.APP_ROOT_PATH, "static", "uploads", "profile_banners"
        )

        for ext in [".jpg", ".jpeg", ".png", ".webp"]:
            banner_file = os.path.join(upload_dir, f"{session['userName']}_banner{ext}")
            if os.path.exists(banner_file):
                os.remove(banner_file)
                Log.info(f"Removed banner file: {banner_file}")

        # Update database to set banner to NULL
        Log.database(f"Connecting to '{Settings.DB_USERS_ROOT}' database")

        connection = sqlite3.connect(Settings.DB_USERS_ROOT)
        connection.set_trace_callback(Log.database)
        cursor = connection.cursor()

        cursor.execute(
            """update users set banner = NULL where userName = ? """,
            [(session["userName"])],
        )
        connection.commit()
        connection.close()

        Log.success(f'User: "{session["userName"]}" removed their banner')
        flashMessage(
            page="changeBanner",
            message="success",
            category="success",
            language=session["language"],
        )

        return redirect("/changebanner")
    else:
        Log.error(
            f"{request.remote_addr} tried to remove banner without being logged in"
        )

        return redirect("/")
