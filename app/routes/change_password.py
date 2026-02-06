from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    session,
)
from passlib.hash import sha512_crypt as encryption

from database import db
from models import User
from utils.flash_message import flash_message
from utils.forms.change_password_form import ChangePasswordForm
from utils.log import Log
from utils.route_guards import login_required

change_password_blueprint = Blueprint("change_password", __name__)


@change_password_blueprint.route("/change-password", methods=["GET", "POST"])
@login_required(
    "change password",
    redirect_to="/login/redirect=change-password",
    flash_page="change_password",
)
def change_password():
    """
    This function is the route for the change password page.
    It is used to change the user's password.

    Args:
        request.form (dict): the form data from the request

    Returns:
        render_template: a rendered template with the form
    """

    form = ChangePasswordForm(request.form)

    if request.method == "POST":
        old_password = request.form["old_password"]
        password = request.form["password"]
        password_confirm = request.form["password_confirm"]

        user = User.query.filter_by(username=session["username"]).first()

        if not user:
            flash_message(
                page="change_password",
                message="login",
                category="error",
                language=session["language"],
            )
            return redirect("/login/redirect=change-password")

        if encryption.verify(old_password, user.password):
            if old_password == password:
                flash_message(
                    page="change_password",
                    message="same",
                    category="error",
                    language=session["language"],
                )

            if password != password_confirm:
                flash_message(
                    page="change_password",
                    message="match",
                    category="error",
                    language=session["language"],
                )

            if old_password != password and password == password_confirm:
                user.password = encryption.hash(password)
                db.session.commit()

                Log.success(
                    f'User: "{session["username"]}" changed his password',
                )

                language = session.get("language", "en")
                session.clear()
                flash_message(
                    page="change_password",
                    message="success",
                    category="success",
                    language=language,
                )

                return redirect("/login/redirect=&")
        else:
            flash_message(
                page="change_password",
                message="old",
                category="error",
                language=session["language"],
            )

    return render_template(
        "change_password.html",
        form=form,
    )
