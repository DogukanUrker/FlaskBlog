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
from passlib.hash import sha512_crypt as encryption

from settings import Settings
from utils.flash_message import flash_message
from utils.forms.password_reset_form import PasswordResetForm
from utils.log import Log

password_reset_blueprint = Blueprint("password_reset", __name__)


password_reset_codes_storage = {}


@password_reset_blueprint.route(
    "/password-reset/codesent=<code_sent>", methods=["GET", "POST"]
)
def password_reset(code_sent):
    """
    This function handles the password reset process.

    Args:
        code_sent (str): A string indicating whether the code has been sent or not.

    Returns:
        A rendered template with the appropriate form and messages.


    """

    form = PasswordResetForm(request.form)

    if code_sent == "true":
        Log.database(f"Connecting to '{Settings.DB_USERS_ROOT}' database")

        connection = sqlite3.connect(Settings.DB_USERS_ROOT)
        connection.set_trace_callback(Log.database)
        cursor = connection.cursor()
        if request.method == "POST":
            username = request.form["username"]
            username = username.replace(" ", "")
            code = request.form["code"]
            password = request.form["password"]
            password_confirm = request.form["password_confirm"]
            if code == password_reset_codes_storage.get(username, ""):
                cursor.execute(
                    """select password from users where lower(username) = ? """,
                    [(username.lower())],
                )
                old_password = cursor.fetchone()[0]
                if password == password_confirm:
                    if encryption.verify(password, old_password):
                        flash_message(
                            page="password_reset",
                            message="same",
                            category="error",
                            language=session["language"],
                        )
                    else:
                        password_reset_codes_storage.pop(username)

                        password = encryption.hash(password)
                        cursor.execute(
                            """update users set password = ? where lower(username) = ? """,
                            [(password), (username.lower())],
                        )
                        connection.commit()
                        Log.success(f'User: "{username}" changed his password')
                        flash_message(
                            page="password_reset",
                            message="success",
                            category="success",
                            language=session["language"],
                        )
                        return redirect("/login/redirect=&")
                else:
                    flash_message(
                        page="password_reset",
                        message="match",
                        category="error",
                        language=session["language"],
                    )
            else:
                flash_message(
                    page="password_reset",
                    message="wrong",
                    category="error",
                    language=session["language"],
                )

        return render_template(
            "password_reset.html",
            form=form,
            mail_sent=True,
        )
    elif code_sent == "false":
        if request.method == "POST":
            username = request.form["username"]
            email = request.form["email"]
            username = username.replace(" ", "")
            Log.database(f"Connecting to '{Settings.DB_USERS_ROOT}' database")
            connection = sqlite3.connect(Settings.DB_USERS_ROOT)
            connection.set_trace_callback(Log.database)
            cursor = connection.cursor()
            cursor.execute(
                """select * from users where lower(username) = ? and lower(email) = ? """,
                [username.lower(), email.lower()],
            )
            user_db = cursor.fetchone()
            if user_db:
                context = ssl.create_default_context()
                server = smtplib.SMTP(Settings.SMTP_SERVER, Settings.SMTP_PORT)
                server.ehlo()
                server.starttls(context=context)
                server.ehlo()
                server.login(Settings.SMTP_MAIL, Settings.SMTP_PASSWORD)
                password_reset_code = str(randint(1000, 9999))
                password_reset_codes_storage[username] = password_reset_code
                message = EmailMessage()
                message.set_content(
                    f"Hi {username}👋,\nForgot your password😶‍🌫️? No problem👌.\nHere is your password reset code🔢:\n{password_reset_code}"
                )
                message.add_alternative(
                    f"""\
                    <html>
                    <body style="font-family: Arial, sans-serif;">
                    <div style="max-width: 600px;margin: 0 auto;background-color: #ffffff;padding: 20px; border-radius:0.5rem;">
                        <div style="text-align: center;">
                        <h1 style="color: #F43F5E;">Password Reset</h1>
                        <p>Hello, {username}.</p>
                        <p>We received a request to reset your password for your account. If you did not request this, please ignore this email.</p>
                        <p>To reset your password, enter the following code in the app:</p>
                        <span style="display: inline-block; background-color: #e0e0e0; color: #000000;padding: 10px 20px;font-size: 24px;font-weight: bold; border-radius: 0.5rem;">{password_reset_code}</span>
                        <p style="font-family: Arial, sans-serif; font-size: 16px;">This code will expire when you refresh the page.</p>
                        <p>Thank you for using {Settings.APP_NAME}.</p>
                        </div>
                    </div>
                    </body>
                    </html>
                """,
                    subtype="html",
                )
                message["Subject"] = "Forget Password?🔒"
                message["From"] = Settings.SMTP_MAIL
                message["To"] = email
                server.send_message(message)
                server.quit()
                Log.success(
                    f'Password reset code: "{password_reset_code}" sent to "{email}" for user: "{username}"'
                )
                flash_message(
                    page="password_reset",
                    message="code",
                    category="success",
                    language=session["language"],
                )
                return redirect("/password-reset/codesent=true")
            else:
                Log.error(f'User: "{username}" with email: "{email}" not found')
                flash_message(
                    page="password_reset",
                    message="not_found",
                    category="error",
                    language=session["language"],
                )

        return render_template(
            "password_reset.html",
            form=form,
            mail_sent=False,
        )
