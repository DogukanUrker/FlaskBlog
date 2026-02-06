from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    session,
)

from database import db
from models import Post
from utils.add_points import add_points
from utils.flash_message import flash_message
from utils.forms.create_post_form import CreatePostForm
from utils.generate_url_id_from_post import generate_url_id
from utils.log import Log
from utils.route_guards import login_required
from utils.time import current_time_stamp

create_post_blueprint = Blueprint("create_post", __name__)


@create_post_blueprint.route("/create-post", methods=["GET", "POST"])
@login_required(
    "create post",
    redirect_to="/login/redirect=&create-post",
    flash_page="create_post",
)
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
            new_post = Post(
                title=post_title,
                tags=post_tags,
                content=post_content,
                banner=post_banner,
                author=session["username"],
                views=0,
                time_stamp=current_time_stamp(),
                last_edit_time_stamp=current_time_stamp(),
                category=post_category,
                url_id=generate_url_id(),
                abstract=post_abstract,
            )
            db.session.add(new_post)
            db.session.commit()

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
