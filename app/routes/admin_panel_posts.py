from flask import (
    Blueprint,
    render_template,
    session,
)

from models import Post
from utils.log import Log
from utils.paginate import paginate_query
from utils.route_guards import admin_required

admin_panel_posts_blueprint = Blueprint("admin_panel_posts", __name__)


@admin_panel_posts_blueprint.route("/admin/posts", methods=["GET", "POST"])
@admin_required("post admin panel")
def admin_panel_posts():
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
