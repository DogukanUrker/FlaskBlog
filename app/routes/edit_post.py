from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    session,
)

from database import db
from models import Post
from utils.flash_message import flash_message
from utils.forms.create_post_form import CreatePostForm
from utils.log import Log
from utils.route_guards import login_required
from utils.time import current_time_stamp

edit_post_blueprint = Blueprint("edit_post", __name__)


@edit_post_blueprint.route("/edit-post/<url_id>", methods=["GET", "POST"])
@login_required(
    "edit post",
    redirect_to=lambda url_id: f"/login/redirect=&edit-post&{url_id}",
    flash_page="edit_post",
)
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

    post = Post.query.filter_by(url_id=url_id).first()

    if post:
        Log.success(f'POST: "{url_id}" FOUND')

        if post.author == session["username"] or session.get("user_role") == "admin":
            form = CreatePostForm(request.form)
            form.post_title.data = post.title
            form.post_tags.data = post.tags
            form.post_abstract.data = post.abstract
            form.post_content.data = post.content
            form.post_category.data = post.category

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
                    post.title = post_title
                    post.tags = post_tags
                    post.content = post_content
                    post.abstract = post_abstract
                    post.category = post_category

                    if post_banner != b"":
                        post.banner = post_banner

                    post.last_edit_time_stamp = current_time_stamp()

                    db.session.commit()

                    Log.success(f'Post: "{post_title}" edited')
                    flash_message(
                        page="edit_post",
                        message="success",
                        category="success",
                        language=session["language"],
                    )
                    return redirect(f"/post/{post.url_id}")

            return render_template(
                "/edit_post.html",
                id=post.id,
                title=post.title,
                tags=post.tags,
                content=post.content,
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
