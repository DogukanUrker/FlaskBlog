import sqlite3

from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    session,
)

from settings import Settings
from utils.add_points import add_points
from utils.flash_message import flash_message
from utils.forms.create_post_form import CreatePostForm
from utils.generate_url_id_from_post import generate_url_id
from utils.log import Log
from utils.time import current_time_stamp

create_post_blueprint = Blueprint("create_post", __name__)


@create_post_blueprint.route("/create-post", methods=["GET", "POST"])
def create_post():
    """
    This function creates a new post for the user.

    Args:
        request (Request): The request object from the user.

    Returns:
        Response: The response object with the HTML template for the create post page.

    Raises:
        401: If the user is not authenticated.
    """

    if "username" in session:
        form = CreatePostForm(request.form)

        if request.method == "POST":
            post_title = request.form["post_title"]
            post_tags = request.form["post_tags"]
            post_abstract = request.form["post_abstract"]
            post_content = request.form["post_content"]
            post_banner = request.files["post_banner"].read()
            post_category = request.form["post_category"]

            if post_content == "" or post_abstract == "":
                flash_message(
                    page="create_post",
                    message="empty",
                    category="error",
                    language=session["language"],
                )
                Log.error(
                    f'User: "{session["username"]}" tried to create a post with empty content',
                )
            else:
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
                        time_stamp,
                        last_edit_time_stamp,
                        category,
                        url_id,
                        abstract
                    ) VALUES (
                        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                    )
                    """,
                    (
                        post_title,
                        post_tags,
                        post_content,
                        post_banner,
                        session["username"],
                        0,
                        current_time_stamp(),
                        current_time_stamp(),
                        post_category,
                        generate_url_id(),
                        post_abstract,
                    ),
                )
                connection.commit()
                Log.success(
                    f'Post: "{post_title}" posted by "{session["username"]}"',
                )

                add_points(20, session["username"])
                flash_message(
                    page="create_post",
                    message="success",
                    category="success",
                    language=session["language"],
                )
                return redirect("/")

        return render_template(
            "create_post.html",
            form=form,
        )
    else:
        Log.error(f"{request.remote_addr} tried to create a new post without login")
        flash_message(
            page="create_post",
            message="login",
            category="error",
            language=session["language"],
        )
        return redirect("/login/redirect=&create-post")
