from json import load

from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from sqlalchemy import func

from models import Comment, Post
from utils.delete import delete_post
from utils.log import Log
from utils.paginate import paginate_query
from utils.route_guards import login_required

dashboard_blueprint = Blueprint("dashboard", __name__)


@dashboard_blueprint.route("/dashboard/<username>", methods=["GET", "POST"])
@login_required(
    "dashboard",
    redirect_to="/login/redirect=&dashboard&user",
    flash_page="dashboard",
)
def dashboard(username):
    if session["username"].lower() == username.lower():
        if request.method == "POST":
            if "post_delete_button" in request.form:
                post_id = request.form["post_id"]
                post_to_delete = Post.query.get(post_id)

                if not post_to_delete:
                    Log.error(
                        f'User: "{session["username"]}" tried to delete unknown post "{post_id}" from dashboard',
                    )
                    return redirect(url_for("dashboard.dashboard", username=username))

                if post_to_delete.author.lower() != session["username"].lower():
                    Log.error(
                        f'User: "{session["username"]}" tried to delete post "{post_id}" owned by "{post_to_delete.author}" from dashboard',
                    )
                    return redirect(url_for("dashboard.dashboard", username=username))

                delete_post(post_to_delete.id)

                return (
                    redirect(url_for("dashboard.dashboard", username=username)),
                    301,
                )

        query = Post.query.filter_by(author=session["username"]).order_by(
            Post.time_stamp.desc()
        )
        posts_objects, page, total_pages = paginate_query(query)

        posts = [
            [
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
            ]
            for p in posts_objects
        ]

        comments_objects = (
            Comment.query.filter(func.lower(Comment.username) == username.lower())
            .order_by(Comment.time_stamp.desc())
            .all()
        )

        comments = [
            (c.id, c.post_id, c.comment, c.username, c.time_stamp)
            for c in comments_objects
        ]

        show_posts = len(posts) > 0
        show_comments = len(comments) > 0

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
