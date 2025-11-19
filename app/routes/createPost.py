import sqlite3

from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    session,
)
from settings import Settings
from utils.addPoints import addPoints
from utils.defaultBanner import DefaultBanner
from utils.flashMessage import flashMessage
from utils.fileUploadValidator import FileUploadValidator
from utils.forms.CreatePostForm import CreatePostForm
from utils.generateUrlIdFromPost import generateurlID
from utils.log import Log
from utils.time import currentTimeStamp

createPostBlueprint = Blueprint("createPost", __name__)


@createPostBlueprint.route("/createpost", methods=["GET", "POST"])
def createPost():
    """
    This function creates a new post for the user.

    Args:
        request (Request): The request object from the user.

    Returns:
        Response: The response object with the HTML template for the create post page.

    Raises:
        401: If the user is not authenticated.
    """

    if "userName" in session:
        form = CreatePostForm(request.form)

        if request.method == "POST":
            postTitle = request.form["postTitle"]
            postTags = request.form["postTags"]
            postAbstract = request.form["postAbstract"]
            postContent = request.form["postContent"]
            postBannerFile = request.files.get("postBanner")
            postCategory = request.form["postCategory"]

            if postContent == "" or postAbstract == "":
                flashMessage(
                    page="createPost",
                    message="empty",
                    category="error",
                    language=session.get("language", "en"),
                )
                Log.error(
                    f'User: "{session["userName"]}" tried to create a post with empty content',
                )
            else:
                # Validate file upload
                is_valid, error_code, postBanner = FileUploadValidator.validate_file(
                    postBannerFile
                )
                if not is_valid:
                    # Map error codes to translation keys
                    error_key_mapping = {
                        FileUploadValidator.ERROR_FILE_SIZE_EXCEEDED: "fileSizeExceeded",
                        FileUploadValidator.ERROR_INVALID_FILE_TYPE: "invalidFileType",
                        FileUploadValidator.ERROR_INVALID_IMAGE_FILE: "invalidImageFile",
                        FileUploadValidator.ERROR_FILE_TYPE_MISMATCH: "fileTypeMismatch",
                        FileUploadValidator.ERROR_SVG_NOT_SUPPORTED: "svgNotSupported",
                    }

                    error_key = error_key_mapping.get(error_code, "invalidImageFile")

                    flashMessage(
                        page="fileUpload",
                        message=error_key,
                        category="error",
                        language=session.get("language", "en"),
                    )
                    return render_template(
                        "createPost.html",
                        form=form,
                    )

                # Use default banner if no file was uploaded
                if postBanner == b"":
                    postBanner = DefaultBanner.get_cached_default_banner()
                    Log.info("Using default banner for post")

                Log.database(f"Connecting to '{Settings.DB_POSTS_ROOT}' database")
                connection = sqlite3.connect(Settings.DB_POSTS_ROOT)
                connection.set_trace_callback(Log.database)
                cursor = connection.cursor()
                cursor.execute(
                    """
                    INSERT INTO posts (
                        title,
                        tags,
                        content,
                        banner,
                        author,
                        views,
                        timeStamp,
                        lastEditTimeStamp,
                        category,
                        urlID,
                        abstract
                    ) VALUES (
                        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                    )
                    """,
                    (
                        postTitle,
                        postTags,
                        postContent,
                        postBanner,
                        session["userName"],
                        0,
                        currentTimeStamp(),
                        currentTimeStamp(),
                        postCategory,
                        generateurlID(),
                        postAbstract,
                    ),
                )
                connection.commit()
                Log.success(
                    f'Post: "{postTitle}" posted by "{session["userName"]}"',
                )

                addPoints(20, session["userName"])
                flashMessage(
                    page="createPost",
                    message="success",
                    category="success",
                    language=session.get("language", "en"),
                )
                return redirect("/")

        return render_template(
            "createPost.html",
            form=form,
        )
    else:
        Log.error(f"{request.remote_addr} tried to create a new post without login")
        flashMessage(
            page="createPost",
            message="login",
            category="error",
            language=session.get("language", "en"),
        )
        return redirect("/login/redirect=&createpost")
