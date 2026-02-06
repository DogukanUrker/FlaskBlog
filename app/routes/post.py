from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from markupsafe import escape

from database import db
from models import Comment, Post
from settings import Settings
from utils.add_points import add_points
from utils.calculate_read_time import calculate_read_time
from utils.delete import delete_comment, delete_post
from utils.flash_message import flash_message
from utils.forms.comment_form import CommentForm
from utils.generate_url_id_from_post import get_slug_from_post_title
from utils.log import Log
from utils.time import current_time_stamp

post_blueprint = Blueprint("post", __name__)


@post_blueprint.route("/post/<url_id>", methods=["GET", "POST"])
@post_blueprint.route("/post/<slug>-<url_id>", methods=["GET", "POST"])
def post(url_id=None, slug=None):
    form = CommentForm(request.form)

    post = Post.query.filter_by(url_id=url_id).first()

    if post:
        post_slug = get_slug_from_post_title(post.title)

        if slug != post_slug:
            return redirect(url_for("post.post", url_id=url_id, slug=post_slug))

        Log.success(f'post: "{url_id}" loaded')

        post.views = (post.views or 0) + 1
        db.session.commit()

        if request.method == "POST":
            if "username" not in session:
                Log.error(
                    f'{request.remote_addr} attempted to submit to post "{url_id}" without login',
                )
                return redirect(f"/login/redirect=&post&{url_id}")

            if "post_delete_button" in request.form:
                if (
                    post.author != session["username"]
                    and session.get("user_role") != "admin"
                ):
                    Log.error(
                        f'User: "{session["username"]}" tried to delete post "{url_id}" without permission',
                    )
                    return redirect(url_for("post.post", url_id=url_id)), 301

                delete_post(post.id)
                return redirect("/")

            if "comment_delete_button" in request.form:
                comment_id = request.form["comment_id"]
                comment = Comment.query.get(comment_id)

                if not comment:
                    Log.error(f'Comment: "{comment_id}" not found for post "{url_id}"')
                    return redirect(url_for("post.post", url_id=url_id)), 301

                if (
                    comment.username != session["username"]
                    and session.get("user_role") != "admin"
                ):
                    Log.error(
                        f'User: "{session["username"]}" tried to delete comment "{comment_id}" without permission',
                    )
                    return redirect(url_for("post.post", url_id=url_id)), 301

                delete_comment(comment_id)
                return redirect(url_for("post.post", url_id=url_id)), 301

            comment_text = escape(request.form["comment"])

            new_comment = Comment(
                post_id=post.id,
                comment=comment_text,
                username=session["username"],
                time_stamp=current_time_stamp(),
            )
            db.session.add(new_comment)
            db.session.commit()

            Log.success(
                f'User: "{session["username"]}" commented to post: "{url_id}"',
            )

            add_points(5, session["username"])

            flash_message(
                page="post",
                message="success",
                category="success",
                language=session["language"],
            )

            return redirect(url_for("post.post", url_id=url_id)), 301

        comments = (
            Comment.query.filter_by(post_id=post.id)
            .order_by(Comment.time_stamp.desc())
            .all()
        )

        comments_tuples = [
            (c.id, c.post_id, c.comment, c.username, c.time_stamp) for c in comments
        ]

        return render_template(
            "post.html",
            id=post.id,
            title=post.title,
            tags=post.tags,
            abstract=post.abstract,
            content=post.content,
            author=post.author,
            views=post.views,
            time_stamp=post.time_stamp,
            last_edit_time_stamp=post.last_edit_time_stamp,
            url_id=post.url_id,
            form=form,
            comments=comments_tuples,
            app_name=Settings.APP_NAME,
            blog_post_url=request.root_url,
            reading_time=calculate_read_time(post.content),
        )

    else:
        Log.error(f"{request.remote_addr} tried to reach unknown post")
        return render_template("not_found.html")
