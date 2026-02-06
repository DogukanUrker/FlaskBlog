from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    session,
)

from database import db
from models import User
from utils.flash_message import flash_message
from utils.forms.change_profile_picture_form import ChangeProfilePictureForm
from utils.log import Log
from utils.route_guards import login_required

change_profile_picture_blueprint = Blueprint("change_profile_picture", __name__)


@change_profile_picture_blueprint.route(
    "/change-profile-picture", methods=["GET", "POST"]
)
@login_required(
    "change profile picture",
    redirect_to="/login/redirect=change-profile-picture",
    flash_page="change_profile_picture",
)
def change_profile_picture():
    """
    This function is the route for the change profile picture page.
    It is used to change the user's profile picture.

    Args:
        request.form (dict): the form data from the request

    Returns:
        render_template: a rendered template with the form
    """

    form = ChangeProfilePictureForm(request.form)

    if request.method == "POST":
        new_profile_picture_seed = request.form["new_profile_picture_seed"]
        new_profile_picture = f"https://api.dicebear.com/7.x/identicon/svg?seed={new_profile_picture_seed}&radius=10"

        user = User.query.filter_by(username=session["username"]).first()

        if user:
            user.profile_picture = new_profile_picture
            db.session.commit()

            Log.success(
                f"User: {session['username']} changed his profile picture",
            )

            flash_message(
                page="change_profile_picture",
                message="success",
                category="success",
                language=session["language"],
            )

        return redirect("/account-settings")

    return render_template(
        "change_profile_picture.html",
        form=form,
    )
