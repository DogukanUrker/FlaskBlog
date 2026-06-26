from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    session,
)
from passlib.hash import sha512_crypt as encryption
from sqlalchemy import func
from urllib.parse import urlparse

from models import User
from settings import Settings
from utils.add_points import add_points
from utils.flash_message import flash_message
from utils.forms.login_form import LoginForm
from utils.log import Log

login_blueprint = Blueprint("login", __name__)


@login_blueprint.route("/login/redirect=<direct>", methods=["GET", "POST"])
def login(direct):
    """
    This function handles the login process for the website.

    Args:
        direct (str): The direct link to redirect to after login.

    Returns:
        tuple: A tuple containing the redirect response and status code.

    Raises:
        401: If the login is unsuccessful.
    """
    direct = direct.replace("&", "/")
    if direct:
        parsed = urlparse(direct)
        if parsed.netloc or parsed.scheme or not direct.startswith("/"):
            direct = "/"
    else:
        direct = "/"
    if Settings.LOG_IN:
        if "username" in session:
            Log.error(f'User: "{session["username"]}" already logged in')
            return (
                redirect(direct),
                301,
            )
        else:
            form = LoginForm(request.form)
            if request.method == "POST":
                username = request.form["username"]
                password = request.form["password"]
                username = username.replace(" ", "")

                user = User.query.filter(
                    func.lower(User.username) == username.lower()
                ).first()

                if not user:
                    Log.error(f'User: "{username}" not found')
                    flash_message(
                        page="login",
                        message="not_found",
                        category="error",
                        language=session["language"],
                    )
                else:
                    if encryption.verify(password, user.password):
                        session["username"] = user.username
                        session["user_role"] = user.role
                        add_points(1, session["username"])
                        Log.success(f'User: "{user.username}" logged in')
                        flash_message(
                            page="login",
                            message="success",
                            category="success",
                            language=session["language"],
                        )

                        return (
                            redirect(direct),
                            301,
                        )

                    else:
                        Log.error("Wrong password")
                        flash_message(
                            page="login",
                            message="password",
                            category="error",
                            language=session["language"],
                        )

            return render_template(
                "login.html",
                form=form,
                hide_login=True,
            )
    else:
        return (
            redirect(direct),
            301,
        )
