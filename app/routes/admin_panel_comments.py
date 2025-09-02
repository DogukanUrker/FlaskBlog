from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    session,
)

from settings import Settings
from utils.log import Log
from utils.paginate import paginate_query

admin_panel_comments_blueprint = Blueprint("admin_panel_comments", __name__)


@admin_panel_comments_blueprint.route("/admin/comments", methods=["GET", "POST"])
@admin_panel_comments_blueprint.route("/admin-panel/comments", methods=["GET", "POST"])
def admin_panel_comments():
    if "username" in session:
        Log.info(f"Admin: {session['username']} reached to comments admin panel")
        Log.database(f"Connecting to '{Settings.DB_COMMENTS_ROOT}' database")

        comments, page, total_pages = paginate_query(
            Settings.DB_COMMENTS_ROOT,
            "select count(*) from comments",
            "select * from comments order by time_stamp desc",
        )

        Log.info(f"Rendering admin_panel_comments.html: params: comments={comments}")

        return render_template(
            "admin_panel_comments.html",
            comments=comments,
            page=page,
            total_pages=total_pages,
        )
    else:
        Log.error(
            f"{request.remote_addr} tried to reach comment admin panel being logged in"
        )

        return redirect("/")
