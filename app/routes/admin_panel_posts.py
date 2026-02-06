from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    session,
)

from models import Post, User
from utils.log import Log
from utils.paginate import paginate_query

admin_panel_posts_blueprint = Blueprint("admin_panel_posts", __name__)


@admin_panel_posts_blueprint.route("/admin/posts", methods=["GET", "POST"])
def admin_panel_posts():
    if "username" in session:
        user = User.query.filter_by(username=session["username"]).first()
        if not user:
            return redirect("/")

        if user.role != "admin":
            Log.error(
                f"{request.remote_addr} tried to reach post admin panel without being admin"
            )
            return redirect("/")

        Log.info(f"Admin: {session['username']} reached to posts admin panel")

        query = Post.query.order_by(Post.time_stamp.desc())
        posts_objects, page, total_pages = paginate_query(query)

        posts = [
            (
                p.id,
                p.title,
                p.tags,
                p.content,
                p.banner,
                p.author,
                p.views,
                p.time_stamp,
                p.last_edit_time_stamp,
                p.category,
                p.url_id,
                p.abstract,
            )
            for p in posts_objects
        ]

        Log.info(
            f"Rendering dashboard.html: params: posts={len(posts)} and show_posts=True"
        )

        return render_template(
            "dashboard.html",
            posts=posts,
            show_posts=True,
            page=page,
            total_pages=total_pages,
        )
    else:
        Log.error(
            f"{request.remote_addr} tried to reach post admin panel without being logged in"
        )

        return redirect("/")
