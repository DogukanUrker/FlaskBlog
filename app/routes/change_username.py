from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    session,
)
from sqlalchemy import func
from utils.forms.change_username_form import ChangeUserNameForm

from database import db
from models import Comment, Post, User
from utils.flash_message import flash_message
from utils.log import Log
from utils.route_guards import login_required

change_username_blueprint = Blueprint("change_username", __name__)


@change_username_blueprint.route("/change-username", methods=["GET", "POST"])
@login_required(
    "change username",
    redirect_to="/login/redirect=change-username",
    flash_page="change_username",
)
def change_username():
    """
    This function is the route for the change username page.
    It is used to change the user's username.

    Args:
        request.form (dict): the form data from the request

    Returns:
        render_template: a rendered template with the form
    """

    form = ChangeUserNameForm(request.form)

    if request.method == "POST":
        new_username = request.form["new_username"]
        new_username = new_username.replace(" ", "")

        # Check if new username already exists
        existing_user = User.query.filter(
            func.lower(User.username) == new_username.lower()
        ).first()

        if not existing_user:
            old_username = session["username"]

            # Update username in users table
            user = User.query.filter_by(username=old_username).first()
            if user:
                user.username = new_username

            # Update author in posts table
            Post.query.filter_by(author=old_username).update({"author": new_username})

            # Update username in comments table
            Comment.query.filter_by(username=old_username).update(
                {"username": new_username}
            )

            db.session.commit()

            Log.success(
                f"User: {old_username} changed his username to {new_username}",
            )

            session["username"] = new_username
            flash_message(
                page="change_username",
                message="success",
                category="success",
                language=session["language"],
            )

            return redirect("/account-settings")
        else:
            Log.error(f'User: "{new_username}" already exists')
            flash_message(
                page="change_username",
                message="taken",
                category="error",
                language=session["language"],
            )

    return render_template(
        "change_username.html",
        form=form,
    )
