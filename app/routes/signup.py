import smtplib
import sqlite3
import ssl
from email.message import EmailMessage

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
from utils.forms.sign_up_form import SignUpForm
from utils.log import Log
from utils.time import current_time_stamp

sign_up_blueprint = Blueprint("signup", __name__)


@sign_up_blueprint.route("/signup", methods=["GET", "POST"])
def signup():
    """
    This function handles the sign up route.

    If the user is already signed in, they will be redirected to the homepage.
    If the user submits the sign up form, their information is checked to ensure it is valid.
    If the information is valid, their account is created and they are signed in.

    Returns:
    The sign up page with any errors or a confirmation message.
    """

    if Settings.REGISTRATION:
        if "username" in session:
            Log.error(f'USER: "{session["username"]}" ALREADY LOGGED IN')
            return redirect("/")
        else:
            form = SignUpForm(request.form)

            if request.method == "POST":
                username = request.form["username"]
                email = request.form["email"]
                password = request.form["password"]
                password_confirm = request.form["password_confirm"]

                username = username.replace(" ", "")
                Log.database(f"Connecting to '{Settings.DB_USERS_ROOT}' database")

                connection = sqlite3.connect(Settings.DB_USERS_ROOT)
                connection.set_trace_callback(Log.database)
                cursor = connection.cursor()

                cursor.execute("select username from users")
                users = str(cursor.fetchall())
                cursor.execute("select email from users")
                mails = str(cursor.fetchall())

                if username not in users and email not in mails:
                    if password_confirm == password:
                        if username.isascii():
                            password = encryption.hash(password)

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
                                        f"Signup reCAPTCHA | verification: {verify_response.get('success')} | score: {verify_response.get('score')}",
                                    )
                                    abort(401)

                                Log.success(
                                    f"Signup reCAPTCHA | verification: {verify_response['success']} | score: {verify_response.get('score')}",
                                )

                            # Create user account
                            connection = sqlite3.connect(Settings.DB_USERS_ROOT)
                            connection.set_trace_callback(Log.database)
                            cursor = connection.cursor()
                            cursor.execute(
                                """
                                insert into users(username,email,password,profile_picture,role,points,time_stamp,is_verified) \
                                values(?, ?, ?, ?, ?, ?, ?, ?)
                                """,
                                (
                                    username,
                                    email,
                                    password,
                                    f"https://api.dicebear.com/7.x/identicon/svg?seed={username}&radius=10",
                                    "user",
                                    0,
                                    current_time_stamp(),
                                    "False",
                                ),
                            )
                            connection.commit()

                            Log.success(f'User: "{username}" added to database')

                            session["username"] = username
                            add_points(1, session["username"])
                            Log.success(f'User: "{username}" logged in')

                            flash_message(
                                page="signup",
                                message="success",
                                category="success",
                                language=session["language"],
                            )

                            # Send welcome email
                            context = ssl.create_default_context()
                            server = smtplib.SMTP(
                                Settings.SMTP_SERVER, Settings.SMTP_PORT
                            )
                            server.ehlo()
                            server.starttls(context=context)
                            server.ehlo()
                            server.login(Settings.SMTP_MAIL, Settings.SMTP_PASSWORD)

                            mail = EmailMessage()
                            mail.set_content(
                                f"Hi {username}👋,\n Welcome to {Settings.APP_NAME}"
                            )
                            mail.add_alternative(
                                f"""\
                            <html>
                            <body>
                                <div
                                style="font-family: Arial, sans-serif;  max-width: 600px; margin: 0 auto; background-color: #ffffff; padding: 20px; border-radius:0.5rem;"
                                >
                                <div style="text-align: center;">
                                    <h1 style="color: #F43F5E;">
                                    Hi {username}, <br />
                                    Welcome to {Settings.APP_NAME}!
                                    </h1>
                                    <p style="font-size: 16px;">
                                    We are glad you joined us.
                                    </p>
                                </div>
                                </div>
                            </body>
                            </html>
                            """,
                                subtype="html",
                            )
                            mail["Subject"] = f"Welcome to {Settings.APP_NAME}"
                            mail["From"] = Settings.SMTP_MAIL
                            mail["To"] = email

                            server.send_message(mail)
                            server.quit()

                            return redirect("/verify-user/codesent=false")
                        else:
                            Log.error(
                                f'Username: "{username}" do not fits to ascii characters',
                            )
                            flash_message(
                                page="signup",
                                message="ascii",
                                category="error",
                                language=session["language"],
                            )
                    else:
                        Log.error("Passwords do not match")

                        flash_message(
                            page="signup",
                            message="password",
                            category="error",
                            language=session["language"],
                        )

                if username in users and email in mails:
                    Log.error(f'"{username}" & "{email}" is unavailable ')
                    flash_message(
                        page="signup",
                        message="taken",
                        category="error",
                        language=session["language"],
                    )
                if username not in users and email in mails:
                    Log.error(f'This email "{email}" is unavailable')

                    flash_message(
                        page="signup",
                        message="email",
                        category="error",
                        language=session["language"],
                    )

                if username in users and email not in mails:
                    Log.error(f'This username "{username}" is unavailable')

                    flash_message(
                        page="signup",
                        message="username",
                        category="error",
                        language=session["language"],
                    )

            return render_template(
                "signup.html",
                form=form,
                hide_sign_up=True,
                site_key=Settings.RECAPTCHA_SITE_KEY,
                recaptcha=Settings.RECAPTCHA,
            )
    else:
        return redirect("/")
