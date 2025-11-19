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
from utils.forms.ChangeProfilePictureForm import ChangeProfilePictureForm
from utils.log import Log
from utils.fileUploadValidator import FileUploadValidator

changeProfilePictureBlueprint = Blueprint("changeProfilePicture", __name__)


@changeProfilePictureBlueprint.route("/changeprofilepicture", methods=["GET", "POST"])
def changeProfilePicture():
    if "userName" in session:
        form = ChangeProfilePictureForm(request.form)

        if request.method == "POST":
            newProfilePicture = None

            # Check if file was uploaded
            if "profilePictureFile" in request.files:
                file = request.files["profilePictureFile"]

                if file and file.filename != "":
                    # Validate file
                    is_valid, error_code, file_data = FileUploadValidator.validate_file(file)
                    if not is_valid:
                        Log.error(f"Profile picture upload failed: {error_code}")
                        flashMessage(
                            page="changeProfilePicture",
                            message="error",
                            category="error",
                            language=session["language"],
                        )
                        return redirect("/changeprofilepicture")

                    # Create profile_pictures directory if it doesn't exist
                    upload_dir = os.path.join(Settings.APP_ROOT_PATH, "static", "uploads", "profile_pictures")
                    os.makedirs(upload_dir, exist_ok=True)

                    # Generate filename based on username
                    file_extension = os.path.splitext(secure_filename(file.filename))[1]
                    filename = f"{session['userName']}_profile{file_extension}"
                    upload_path = os.path.join(upload_dir, filename)

                    # Remove old profile picture if exists
                    for ext in [".jpg", ".jpeg", ".png", ".webp"]:
                        old_file = os.path.join(upload_dir, f"{session['userName']}_profile{ext}")
                        if os.path.exists(old_file):
                            os.remove(old_file)
                            Log.info(f"Removed old profile picture: {old_file}")

                    # Save new file
                    try:
                        file.save(upload_path)
                        newProfilePicture = f"/static/uploads/profile_pictures/{filename}"
                        Log.success(f"Profile picture saved to: {upload_path}")
                    except Exception as e:
                        Log.error(f"Failed to save profile picture: {e}")
                        flashMessage(
                            page="changeProfilePicture",
                            message="error",
                            category="error",
                            language=session["language"],
                        )
                        return redirect("/changeprofilepicture")

            # If no file uploaded, check for DiceBear seed
            if not newProfilePicture:
                newProfilePictureSeed = request.form.get("newProfilePictureSeed", "").strip()
                if newProfilePictureSeed:
                    newProfilePicture = f"https://api.dicebear.com/7.x/identicon/svg?seed={newProfilePictureSeed}&radius=10"
                else:
                    flashMessage(
                        page="changeProfilePicture",
                        message="error",
                        category="error",
                        language=session["language"],
                    )
                    return redirect("/changeprofilepicture")

            # Update database
            Log.database(f"Connecting to '{Settings.DB_USERS_ROOT}' database")

            connection = sqlite3.connect(Settings.DB_USERS_ROOT)
            connection.set_trace_callback(Log.database)
            cursor = connection.cursor()

            cursor.execute(
                """update users set profilePicture = ? where userName = ? """,
                [(newProfilePicture), (session["userName"])],
            )
            connection.commit()
            connection.close()

            Log.success(
                f'User: "{session["userName"]}" changed profile picture to "{newProfilePicture}"',
            )
            flashMessage(
                page="changeProfilePicture",
                message="success",
                category="success",
                language=session["language"],
            )

            return redirect("/changeprofilepicture")

        return render_template(
            "changeProfilePicture.html",
            form=form,
        )
    else:
        Log.error(
            f"{request.remote_addr} tried to change profile picture without being logged in"
        )

        return redirect("/")
