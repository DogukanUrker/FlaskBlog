import sqlite3
from json import load

from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from settings import Settings
from utils.delete import delete_post
from utils.flash_message import flash_message
from utils.log import Log
from utils.paginate import paginate_query

dashboard_blueprint = Blueprint("dashboard", __name__)


@dashboard_blueprint.route("/dashboard/<username>", methods=["GET", "POST"])
def dashboard(username):
    if "username" in session:
        if session["username"].lower() == username.lower():
            if request.method == "POST":
                if "post_delete_button" in request.form:
                    delete_post(request.form["post_id"])

                    return (
                        redirect(url_for("dashboard.dashboard", username=username)),
                        301,
                    )
            posts, page, total_pages = paginate_query(
                Settings.DB_POSTS_ROOT,
                "select count(*) from posts where author = ?",
                "select * from posts where author = ? order by time_stamp desc",
                [session["username"]],
            )
            Log.database(f"Connecting to '{Settings.DB_COMMENTS_ROOT}' database")

            connection = sqlite3.connect(Settings.DB_COMMENTS_ROOT)
            connection.set_trace_callback(Log.database)
            cursor = connection.cursor()

            cursor.execute(
                """select * from comments where lower(user) = ? order by time_stamp desc""",
                [(username.lower())],
            )
            comments = cursor.fetchall()

            if posts == []:
                show_posts = False
            else:
                show_posts = True

            if comments == []:
                show_comments = False
            else:
                show_comments = True

            posts = list(posts)

            for i in range(len(posts)):
                posts[i] = list(posts[i])

            language = session.get("language")
            translation_file = f"./translations/{language}.json"

            with open(translation_file, "r", encoding="utf-8") as file:
                translations = load(file)

            for post in posts:
                post[9] = translations["categories"][post[9].lower()]

            return render_template(
                "/dashboard.html",
                posts=posts,
                comments=comments,
                show_posts=show_posts,
                show_comments=show_comments,
                page=page,
                total_pages=total_pages,
            )
        else:
            Log.error(
                f'User: "{session["username"]}" tried to login to another users dashboard',
            )

            return redirect(f"/dashboard/{session['username'].lower()}")
    else:
        Log.error(f"{request.remote_addr} tried to access the dashboard without login")
        flash_message(
            page="dashboard",
            message="login",
            category="error",
            language=session["language"],
        )

        return redirect("/login/redirect=&dashboard&user")
