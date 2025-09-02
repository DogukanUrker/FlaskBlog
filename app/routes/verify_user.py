import smtplib
import sqlite3
import ssl
from email.message import EmailMessage
from random import randint

from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    session,
)

from settings import Settings
from utils.flash_message import flash_message
from utils.forms.verify_user_form import VerifyUserForm
from utils.log import Log

verify_user_blueprint = Blueprint("verify_user", __name__)


@verify_user_blueprint.route(
    "/verify-user/codesent=<code_sent>", methods=["GET", "POST"]
)
def verify_user(code_sent):
    """
    This function handles the verification of the user's account.

    Args:
        code_sent (str): A string indicating whether the verification code has been sent or not.

    Returns:
        redirect: A redirect to the homepage if the user is verified, or a rendered template with the verification form.

    """

    if "username" in session:
        username = session["username"]
        Log.database(f"Connecting to '{Settings.DB_USERS_ROOT}' database")
        Log.database(f"Connecting to '{Settings.DB_USERS_ROOT}' database")

        connection = sqlite3.connect(Settings.DB_USERS_ROOT)
        connection.set_trace_callback(Log.database)
        cursor = connection.cursor()

        cursor.execute(
            """select is_verified from users where lower(username) = ? """,
            [(username.lower())],
        )
        is_verified = cursor.fetchone()[0]

        if is_verified == "True":
            return redirect("/")
        elif is_verified == "False":
            global verification_code

            form = VerifyUserForm(request.form)

            if code_sent == "true":
                if request.method == "POST":
                    code = request.form["code"]

                    if code == verification_code:
                        cursor.execute(
                            """update users set is_verified = "True" where lower(username) = ? """,
                            [(username.lower())],
                        )
                        connection.commit()
                        Log.success(f'User: "{username}" has been verified')
                        flash_message(
                            page="verify_user",
                            message="success",
                            category="success",
                            language=session["language"],
                        )
                        return redirect("/")
                    else:
                        flash_message(
                            page="verify_user",
                            message="wrong",
                            category="error",
                            language=session["language"],
                        )

                return render_template(
                    "verify_user.html",
                    form=form,
                    mail_sent=True,
                )
            elif code_sent == "false":
                if request.method == "POST":
                    cursor.execute(
                        """select * from users where lower(username) = ? """,
                        [(username.lower())],
                    )
                    username_db = cursor.fetchone()

                    cursor.execute(
                        """select email from users where lower(username) = ? """,
                        [(username.lower())],
                    )
                    email = cursor.fetchone()

                    if username_db:
                        context = ssl.create_default_context()
                        server = smtplib.SMTP(Settings.SMTP_SERVER, Settings.SMTP_PORT)
                        server.ehlo()
                        server.starttls(context=context)
                        server.ehlo()
                        server.login(Settings.SMTP_MAIL, Settings.SMTP_PASSWORD)

                        verification_code = str(randint(1000, 9999))

                        message = EmailMessage()
                        message.set_content(
                            f"Hi {username}👋,\nHere is your account verification code🔢:\n{verification_code}"
                        )
                        message.add_alternative(
                            f"""\
                                <html>
                                <body>
                                    <div
                                    style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background-color: #ffffff; padding: 20px; border-radius:0.5rem;"
                                    >
                                    <div style="text-align: center;">
                                        <h1 style="color: #F43F5E;">Thank you for creating an account!</h1>
                                        <p style="font-size: 16px;">
                                        Hello, {username}.
                                        </p>
                                        <p style="font-size: 16px;">
                                        Please enter the verification code below to verify your account.
                                        </p>
                                        <div
                                        style="background-color: #f0f0f0; padding: 10px; border-radius: 5px; margin: 20px 0;"
                                        >
                                        <p style="font-size: 24px; font-weight: bold; margin: 0;">
                                            {verification_code}
                                        </p>
                                        </div>
                                        <p style="font-size: 14px; color: #888888;">
                                        This verification code is valid for a limited time. Please do not share this code with anyone.
                                        </p>
                                    </div>
                                    </div>
                                </body>
                                </html>
                            """,
                            subtype="html",
                        )
                        message["Subject"] = f"Verify your {Settings.APP_NAME} account!"
                        message["From"] = Settings.SMTP_MAIL
                        message["To"] = email[0]

                        server.send_message(message)
                        server.quit()
                        Log.success(
                            f'Verification code sent to "{email[0]}" for user: "{username}"'
                        )

                        return redirect("/verify-user/codesent=true")

                return render_template(
                    "verify_user.html",
                    form=form,
                    mail_sent=False,
                )
    else:
        Log.error(f"{request.remote_addr} tried to verify user without being logged in")
        return redirect("/")
