import sqlite3

from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    session,
)

from settings import Settings
from utils.flash_message import flash_message
from utils.forms.create_post_form import CreatePostForm
from utils.log import Log
from utils.time import current_time_stamp

edit_post_blueprint = Blueprint("edit_post", __name__)


@edit_post_blueprint.route("/edit-post/<url_id>", methods=["GET", "POST"])
def edit_post(url_id):
    """
    This function handles the edit post route.

    Args:
        url_id (string): the ID of the post to edit

    Returns:
        The rendered edit post template or a redirect to the homepage if the user is not authorized to edit the post

    Raises:
        abort(404): if the post does not exist
        abort(401): if the user is not authorized to edit the post
    """

    if "username" in session:
        Log.database(f"Connecting to '{Settings.DB_POSTS_ROOT}' database")

        connection = sqlite3.connect(Settings.DB_POSTS_ROOT)
        connection.set_trace_callback(Log.database)
        cursor = connection.cursor()
        cursor.execute("select url_id from posts where url_id = ?", (url_id,))
        posts = str(cursor.fetchall())

        if str(url_id) in posts:
            Log.database(f"Connecting to '{Settings.DB_POSTS_ROOT}' database")

            connection = sqlite3.connect(Settings.DB_POSTS_ROOT)
            connection.set_trace_callback(Log.database)
            cursor = connection.cursor()
            cursor.execute(
                """select * from posts where url_id = ? """,
                [(url_id)],
            )
            post = cursor.fetchone()

            Log.success(f'POST: "{url_id}" FOUND')

            if post[5] == session["username"] or session["user_role"] == "admin":
                form = CreatePostForm(request.form)
                form.post_title.data = post[1]
                form.post_tags.data = post[2]
                form.post_abstract.data = post[11]
                form.post_content.data = post[3]
                form.post_category.data = post[9]

                if request.method == "POST":
                    post_title = request.form["post_title"]
                    post_tags = request.form["post_tags"]
                    post_content = request.form["post_content"]
                    post_abstract = request.form["post_abstract"]
                    post_category = request.form["post_category"]
                    post_banner = request.files["post_banner"].read()

                    if post_content == "" or post_abstract == "":
                        flash_message(
                            page="edit_post",
                            message="empty",
                            category="error",
                            language=session["language"],
                        )
                        Log.error(
                            f'User: "{session["username"]}" tried to edit a post with empty content',
                        )
                    else:
                        connection = sqlite3.connect(Settings.DB_POSTS_ROOT)
                        connection.set_trace_callback(Log.database)
                        cursor = connection.cursor()
                        cursor.execute(
                            """update posts set title = ? where id = ? """,
                            (post_title, post[0]),
                        )
                        cursor.execute(
                            """update posts set tags = ? where id = ? """,
                            (post_tags, post[0]),
                        )
                        cursor.execute(
                            """update posts set content = ? where id = ? """,
                            (post_content, post[0]),
                        )
                        cursor.execute(
                            """update posts set abstract = ? where id = ? """,
                            (post_abstract, post[0]),
                        )
                        cursor.execute(
                            """update posts set category = ? where id = ? """,
                            (post_category, post[0]),
                        )
                        if post_banner != b"":
                            cursor.execute(
                                """update posts set banner = ? where id = ? """,
                                (post_banner, post[0]),
                            )
                        cursor.execute(
                            """update posts set last_edit_time_stamp = ? where id = ? """,
                            [(current_time_stamp()), (post[0])],
                        )

                        connection.commit()
                        Log.success(f'Post: "{post_title}" edited')
                        flash_message(
                            page="edit_post",
                            message="success",
                            category="success",
                            language=session["language"],
                        )
                        return redirect(f"/post/{post[10]}")

                return render_template(
                    "/edit_post.html",
                    id=post[0],
                    title=post[1],
                    tags=post[2],
                    content=post[3],
                    form=form,
                )
            else:
                flash_message(
                    page="edit_post",
                    message="author",
                    category="error",
                    language=session["language"],
                )
                Log.error(
                    f'User: "{session["username"]}" tried to edit another authors post',
                )
                return redirect("/")
        else:
            Log.error(f'Post: "{url_id}" not found')
            return redirect("/not-found")
    else:
        Log.error(f"{request.remote_addr} tried to edit post without login")
        flash_message(
            page="edit_post",
            message="login",
            category="error",
            language=session["language"],
        )
        return redirect(f"/login/redirect=&edit-post&{url_id}")
