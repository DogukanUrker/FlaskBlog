from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    session,
)

from models import Comment, User
from utils.log import Log
from utils.paginate import paginate_query

admin_panel_comments_blueprint = Blueprint("admin_panel_comments", __name__)


@admin_panel_comments_blueprint.route("/admin/comments", methods=["GET", "POST"])
def admin_panel_comments():
    if "username" in session:
        user = User.query.filter_by(username=session["username"]).first()
        if not user:
            return redirect("/")

        if user.role != "admin":
            Log.error(
                f"{request.remote_addr} tried to reach comment admin panel without being admin"
            )
            return redirect("/")

        Log.info(f"Admin: {session['username']} reached to comments admin panel")

        query = Comment.query.order_by(Comment.time_stamp.desc())
        comments_objects, page, total_pages = paginate_query(query)

        comments = [
            (c.id, c.post_id, c.comment, c.username, c.time_stamp)
            for c in comments_objects
        ]

        Log.info(
            f"Rendering admin_panel_comments.html: params: comments={len(comments)}"
        )

        return render_template(
            "admin_panel_comments.html",
            comments=comments,
            page=page,
            total_pages=total_pages,
        )
    else:
        Log.error(
            f"{request.remote_addr} tried to reach comment admin panel without being logged in"
        )

        return redirect("/")
