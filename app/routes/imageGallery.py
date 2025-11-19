"""
Image gallery route for uploading and displaying user images.
"""

import sqlite3
import os
from flask import Blueprint, redirect, render_template, request, session
from werkzeug.utils import secure_filename
from settings import Settings
from utils.log import Log
from utils.flashMessage import flashMessage
from utils.fileUploadValidator import FileUploadValidator
from utils.forms.ImageUploadForm import ImageUploadForm
from utils.time import currentTimeStamp

imageGalleryBlueprint = Blueprint("imageGallery", __name__)


@imageGalleryBlueprint.route("/gallery/<userName>", methods=["GET"])
def userGallery(userName):
    """
    Display a user's image gallery.
    Public - anyone can view.

    Args:
        userName (str): Username whose gallery to display

    Returns:
        Rendered template with user's images
    """
    Log.info(f"Loading gallery for user: {userName}")

    # Connect to database
    connection = sqlite3.connect(Settings.DB_USERS_ROOT)
    connection.set_trace_callback(Log.database)
    cursor = connection.cursor()

    # Check if user exists
    cursor.execute("SELECT userName FROM Users WHERE userName = ?", (userName,))
    user = cursor.fetchone()

    if not user:
        connection.close()
        Log.warning(f"Gallery requested for non-existent user: {userName}")
        flashMessage(
            page="imageGallery",
            message="userNotFound",
            category="error",
            language=session.get("language", "en")
        )
        return redirect("/")

    # Get user's images (newest first)
    cursor.execute(
        """
        SELECT image_id, title, description, file_path, timeStamp
        FROM user_images
        WHERE userName = ?
        ORDER BY timeStamp DESC
        """,
        (userName,)
    )
    images = cursor.fetchall()
    connection.close()

    # Convert to list of dicts for easier template handling
    images_list = [
        {
            "image_id": img[0],
            "title": img[1] or "Untitled",
            "description": img[2] or "",
            "file_path": img[3],
            "timeStamp": img[4]
        }
        for img in images
    ]

    Log.success(f"Loaded {len(images_list)} images for user: {userName}")

    return render_template(
        "imageGallery.html",
        userName=userName,
        images=images_list,
        isOwner=session.get("userName") == userName
    )


@imageGalleryBlueprint.route("/gallery/upload", methods=["GET", "POST"])
def uploadImage():
    """
    Upload image to authenticated user's gallery.
    Requires authentication.

    Returns:
        GET: Upload form
        POST: Process upload and redirect to gallery
    """
    # Check authentication
    if "userName" not in session:
        Log.warning(f"{request.remote_addr} tried to upload image without authentication")
        flashMessage(
            page="imageGallery",
            message="loginRequired",
            category="error",
            language=session.get("language", "en")
        )
        return redirect("/login/redirect=&gallery&upload")

    form = ImageUploadForm(request.form)

    if request.method == "POST":
        # Check if file was uploaded
        if "imageFile" not in request.files:
            flashMessage(
                page="imageGallery",
                message="noFileProvided",
                category="error",
                language=session.get("language", "en")
            )
            return redirect("/gallery/upload")

        file = request.files["imageFile"]

        if file.filename == "":
            flashMessage(
                page="imageGallery",
                message="noFileSelected",
                category="error",
                language=session.get("language", "en")
            )
            return redirect("/gallery/upload")

        # Validate file
        is_valid, error_code, file_data = FileUploadValidator.validate_file(file)
        if not is_valid:
            Log.error(f"Image upload failed for {session['userName']}: {error_code}")
            flashMessage(
                page="imageGallery",
                message="invalidFile",
                category="error",
                language=session.get("language", "en")
            )
            return redirect("/gallery/upload")

        # Get form data
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()

        # Save file
        try:
            upload_dir = os.path.join(
                Settings.APP_ROOT_PATH,
                "static",
                "uploads",
                "user_gallery",
                session["userName"]
            )
            os.makedirs(upload_dir, exist_ok=True)

            # Generate unique filename with timestamp
            timestamp = currentTimeStamp()
            file_extension = os.path.splitext(secure_filename(file.filename))[1]
            filename = f"{timestamp}{file_extension}"
            upload_path = os.path.join(upload_dir, filename)

            file.save(upload_path)
            Log.success(f"Image saved to: {upload_path}")

            # Save to database
            file_path = f"/static/uploads/user_gallery/{session['userName']}/{filename}"
            connection = sqlite3.connect(Settings.DB_USERS_ROOT)
            connection.set_trace_callback(Log.database)
            cursor = connection.cursor()

            cursor.execute(
                """
                INSERT INTO user_images(userName, title, description, file_path, timeStamp)
                VALUES(?, ?, ?, ?, ?)
                """,
                (session["userName"], title, description, file_path, timestamp)
            )
            connection.commit()
            connection.close()

            flashMessage(
                page="imageGallery",
                message="uploadSuccess",
                category="success",
                language=session.get("language", "en")
            )
            Log.success(f"User {session['userName']} uploaded image: {filename}")

            return redirect(f"/gallery/{session['userName']}")

        except Exception as e:
            flashMessage(
                page="imageGallery",
                message="uploadError",
                category="error",
                language=session.get("language", "en")
            )
            Log.error(f"Image upload failed for {session['userName']}: {e}")
            return redirect("/gallery/upload")

    # GET request - show upload form
    return render_template("uploadImage.html", form=form)


@imageGalleryBlueprint.route("/gallery/delete/<int:image_id>", methods=["POST"])
def deleteImage(image_id):
    """
    Delete an image from user's gallery.
    Requires authentication and ownership.

    Args:
        image_id (int): Image ID to delete

    Returns:
        Redirect to user's gallery
    """
    # Check authentication
    if "userName" not in session:
        Log.warning(f"{request.remote_addr} tried to delete image without authentication")
        return redirect("/login")

    connection = sqlite3.connect(Settings.DB_USERS_ROOT)
    connection.set_trace_callback(Log.database)
    cursor = connection.cursor()

    # Get image details
    cursor.execute(
        "SELECT userName, file_path FROM user_images WHERE image_id = ?",
        (image_id,)
    )
    image = cursor.fetchone()

    if not image:
        connection.close()
        flashMessage(
            page="imageGallery",
            message="imageNotFound",
            category="error",
            language=session.get("language", "en")
        )
        return redirect(f"/gallery/{session['userName']}")

    # Check ownership
    if image[0] != session["userName"]:
        connection.close()
        Log.warning(f"User {session['userName']} tried to delete image belonging to {image[0]}")
        flashMessage(
            page="imageGallery",
            message="unauthorized",
            category="error",
            language=session.get("language", "en")
        )
        return redirect(f"/gallery/{session['userName']}")

    # Delete file from filesystem
    try:
        file_path = image[1].lstrip("/")  # Remove leading slash
        full_path = os.path.join(Settings.APP_ROOT_PATH, file_path)
        if os.path.exists(full_path):
            os.remove(full_path)
            Log.info(f"Deleted file: {full_path}")
    except Exception as e:
        Log.error(f"Failed to delete file: {e}")

    # Delete from database
    cursor.execute("DELETE FROM user_images WHERE image_id = ?", (image_id,))
    connection.commit()
    connection.close()

    flashMessage(
        page="imageGallery",
        message="deleteSuccess",
        category="success",
        language=session.get("language", "en")
    )
    Log.success(f"User {session['userName']} deleted image ID {image_id}")

    return redirect(f"/gallery/{session['userName']}")
