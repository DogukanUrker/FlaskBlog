import sqlite3

from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    session,
)
from settings import Settings
from utils.fileUploadValidator import FileUploadValidator
from utils.flashMessage import flashMessage
from utils.forms.CreatePostForm import CreatePostForm
from utils.log import Log
from utils.time import currentTimeStamp

editPostBlueprint = Blueprint("editPost", __name__)


@editPostBlueprint.route("/editpost/<urlID>", methods=["GET", "POST"])
def editPost(urlID):
    """
    This function handles the edit post route.

    Args:
        postID (string): the ID of the post to edit

    Returns:
        The rendered edit post template or a redirect to the homepage if the user is not authorized to edit the post

    Raises:
        abort(404): if the post does not exist
        abort(401): if the user is not authorized to edit the post
    """

    if "userName" in session:
        Log.database(f"Connecting to '{Settings.DB_POSTS_ROOT}' database")

        connection = sqlite3.connect(Settings.DB_POSTS_ROOT)
        connection.set_trace_callback(Log.database)
        cursor = connection.cursor()
        cursor.execute("select urlID from posts where urlID = ?", (urlID,))
        posts = str(cursor.fetchall())

        if str(urlID) in posts:
            Log.database(f"Connecting to '{Settings.DB_POSTS_ROOT}' database")

            connection = sqlite3.connect(Settings.DB_POSTS_ROOT)
            connection.set_trace_callback(Log.database)
            cursor = connection.cursor()
            cursor.execute(
                """select * from posts where urlID = ? """,
                [(urlID)],
            )
            post = cursor.fetchone()

            Log.success(f'POST: "{urlID}" FOUND')

            if post[5] == session["userName"] or session["userRole"] == "admin":
                form = CreatePostForm(request.form)
                form.postTitle.data = post[1]
                form.postTags.data = post[2]
                form.postAbstract.data = post[11]
                form.postContent.data = post[3]
                form.postCategory.data = post[9]

                if request.method == "POST":
                    postTitle = request.form["postTitle"]
                    postTags = request.form["postTags"]
                    postContent = request.form["postContent"]
                    postAbstract = request.form["postAbstract"]
                    postCategory = request.form["postCategory"]
                    postBannerFile = request.files.get("postBanner")

                    if postContent == "" or postAbstract == "":
                        flashMessage(
                            page="editPost",
                            message="empty",
                            category="error",
                            language=session["language"],
                        )
                        Log.error(
                            f'User: "{session["userName"]}" tried to edit a post with empty content',
                        )
                    else:
                        # Validate file upload if a new file is provided
                        is_valid, error_msg, postBanner = FileUploadValidator.validate_file(
                            postBannerFile
                        )
                        if not is_valid:
                            flashMessage(
                                page="editPost",
                                message=error_msg or "Invalid file upload",
                                category="error",
                                language=session["language"],
                            )
                            return render_template(
                                "/editPost.html",
                                id=post[0],
                                title=post[1],
                                tags=post[2],
                                content=post[3],
                                form=form,
                            )
                        connection = sqlite3.connect(Settings.DB_POSTS_ROOT)
                        connection.set_trace_callback(Log.database)
                        cursor = connection.cursor()
                        cursor.execute(
                            """update posts set title = ? where id = ? """,
                            (postTitle, post[0]),
                        )
                        cursor.execute(
                            """update posts set tags = ? where id = ? """,
                            (postTags, post[0]),
                        )
                        cursor.execute(
                            """update posts set content = ? where id = ? """,
                            (postContent, post[0]),
                        )
                        cursor.execute(
                            """update posts set abstract = ? where id = ? """,
                            (postAbstract, post[0]),
                        )
                        cursor.execute(
                            """update posts set category = ? where id = ? """,
                            (postCategory, post[0]),
                        )
                        if postBanner != b"":
                            cursor.execute(
                                """update posts set banner = ? where id = ? """,
                                (postBanner, post[0]),
                            )
                        cursor.execute(
                            """update posts set lastEditTimeStamp = ? where id = ? """,
                            [(currentTimeStamp()), (post[0])],
                        )

                        connection.commit()
                        Log.success(f'Post: "{postTitle}" edited')
                        flashMessage(
                            page="editPost",
                            message="success",
                            category="success",
                            language=session["language"],
                        )
                        return redirect(f"/post/{post[10]}")

                return render_template(
                    "/editPost.html",
                    id=post[0],
                    title=post[1],
                    tags=post[2],
                    content=post[3],
                    form=form,
                )
            else:
                flashMessage(
                    page="editPost",
                    message="author",
                    category="error",
                    language=session["language"],
                )
                Log.error(
                    f'User: "{session["userName"]}" tried to edit another authors post',
                )
                return redirect("/")
        else:
            Log.error(f'Post: "{urlID}" not found')
            return render_template("notFound.html")
    else:
        Log.error(f"{request.remote_addr} tried to edit post without login")
        flashMessage(
            page="editPost",
            message="login",
            category="error",
            language=session["language"],
        )
        return redirect(f"/login/redirect=&editpost&{urlID}")
