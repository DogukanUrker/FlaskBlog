from flask import Blueprint, redirect, render_template, request, session

from models import User
from utils.delete import delete_user
from utils.route_guards import login_required

account_settings_blueprint = Blueprint("account_settings", __name__)


@account_settings_blueprint.route("/account-settings", methods=["GET", "POST"])
@login_required("account settings", redirect_to="/login/redirect=&account-settings")
def account_settings():
    user = User.query.filter_by(username=session["username"]).first()

    if not user:
        return redirect("/")

    if request.method == "POST":
        delete_user(user.username)
        return redirect("/")

    return render_template(
        "account_settings.html",
        user=(user.username,),
    )
