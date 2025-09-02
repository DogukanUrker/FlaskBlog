import sqlite3

from flask import (
    Blueprint,
    abort,
    redirect,
    render_template,
    request,
    session,
)
from passlib.hash import sha512_crypt as encryption
from requests import post as requests_post

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
                Log.database(f"Connecting to '{Settings.DB_USERS_ROOT}' database")
                connection = sqlite3.connect(Settings.DB_USERS_ROOT)
                connection.set_trace_callback(Log.database)
                cursor = connection.cursor()
                cursor.execute(
                    """select * from users where lower(username) = ? """,
                    [(username.lower())],
                )
                user = cursor.fetchone()
                if not user:
                    Log.error(f'User: "{username}" not found')
                    flash_message(
                        page="login",
                        message="not_found",
                        category="error",
                        language=session["language"],
                    )
                else:
                    if encryption.verify(password, user[3]):
                        if Settings.RECAPTCHA:
                            secret_response = request.form["g-recaptcha-response"]
                            verify_response = requests_post(
                                url=f"{Settings.RECAPTCHA_VERIFY_URL}?secret={Settings.RECAPTCHA_SECRET_KEY}&response={secret_response}"
                            ).json()
                            if not (
                                verify_response["success"] is True
                                or verify_response.get("score", 0) > 0.5
                            ):
                                Log.error(
                                    f"Login reCAPTCHA | verification: {verify_response.get('success')} | score: {verify_response.get('score')}",
                                )
                                abort(401)

                            Log.success(
                                f"Login reCAPTCHA | verification: {verify_response['success']} | score: {verify_response.get('score')}",
                            )

                        session["username"] = user[1]
                        session["user_role"] = user[5]
                        add_points(1, session["username"])
                        Log.success(f'User: "{user[1]}" logged in')
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
                site_key=Settings.RECAPTCHA_SITE_KEY,
                recaptcha=Settings.RECAPTCHA,
            )
    else:
        return (
            redirect(direct),
            301,
        )
