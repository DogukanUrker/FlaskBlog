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
from utils.flashMessage import flashMessage
from utils.forms.PasswordResetForm import PasswordResetForm
from utils.log import Log
from utils.smtpSettings import SMTPSettings

passwordResetBlueprint = Blueprint("passwordReset", __name__)


passwordResetCodesStorage = {}


@passwordResetBlueprint.route(
    "/passwordreset/codesent=<codeSent>", methods=["GET", "POST"]
)
def passwordReset(codeSent):
    """
    This function handles the password reset process.

    Args:
        codeSent (str): A string indicating whether the code has been sent or not.

    Returns:
        A rendered template with the appropriate form and messages.


    """

    form = PasswordResetForm(request.form)

    if codeSent == "true":
        Log.database(f"Connecting to '{Settings.DB_USERS_ROOT}' database")

        connection = sqlite3.connect(Settings.DB_USERS_ROOT)
        connection.set_trace_callback(Log.database)
        cursor = connection.cursor()
        if request.method == "POST":
            userName = request.form["userName"]
            userName = userName.replace(" ", "")
            code = request.form["code"]
            password = request.form["password"]
            passwordConfirm = request.form["passwordConfirm"]
            if code == passwordResetCodesStorage.get(userName, ""):
                cursor.execute(
                    """select password from users where lower(userName) = ? """,
                    [(userName.lower())],
                )
                oldPassword = cursor.fetchone()[0]
                if password == passwordConfirm:
                    if encryption.verify(password, oldPassword):
                        flashMessage(
                            page="passwordReset",
                            message="same",
                            category="error",
                            language=session["language"],
                        )
                    else:
                        passwordResetCodesStorage.pop(userName)

                        password = encryption.hash(password)
                        cursor.execute(
                            """update users set password = ? where lower(userName) = ? """,
                            [(password), (userName.lower())],
                        )
                        connection.commit()
                        Log.success(f'User: "{userName}" changed his password')
                        flashMessage(
                            page="passwordReset",
                            message="success",
                            category="success",
                            language=session["language"],
                        )
                        return redirect("/login/redirect=&")
                else:
                    flashMessage(
                        page="passwordReset",
                        message="match",
                        category="error",
                        language=session["language"],
                    )
            else:
                flashMessage(
                    page="passwordReset",
                    message="wrong",
                    category="error",
                    language=session["language"],
                )

        return render_template(
            "passwordReset.html",
            form=form,
            mailSent=True,
        )
    elif codeSent == "false":
        if request.method == "POST":
            userName = request.form["userName"]
            email = request.form["email"]
            userName = userName.replace(" ", "")
            Log.database(f"Connecting to '{Settings.DB_USERS_ROOT}' database")
            connection = sqlite3.connect(Settings.DB_USERS_ROOT)
            connection.set_trace_callback(Log.database)
            cursor = connection.cursor()
            cursor.execute(
                """select * from users where lower(userName) = ? and lower(email) = ? """,
                [userName.lower(), email.lower()],
            )
            userDB = cursor.fetchone()
            if userDB:
                # Get SMTP settings from database
                smtp_settings = SMTPSettings.get_settings()

                context = ssl.create_default_context()
                server = smtplib.SMTP(smtp_settings["smtp_server"], smtp_settings["smtp_port"])
                server.ehlo()
                server.starttls(context=context)
                server.ehlo()
                server.login(smtp_settings["smtp_mail"], smtp_settings["smtp_password"])
                passwordResetCode = str(randint(1000, 9999))
                passwordResetCodesStorage[userName] = passwordResetCode
                message = EmailMessage()
                message.set_content(
                    f"Hi {userName}👋,\nForgot your password😶‍🌫️? No problem👌.\nHere is your password reset code🔢:\n{passwordResetCode}"
                )
                message.add_alternative(
                    f"""\
                    <html>
                    <body style="font-family: Arial, sans-serif;">
                    <div style="max-width: 600px;margin: 0 auto;background-color: #ffffff;padding: 20px; border-radius:0.5rem;">
                        <div style="text-align: center;">
                        <h1 style="color: #F43F5E;">Password Reset</h1>
                        <p>Hello, {userName}.</p>
                        <p>We received a request to reset your password for your account. If you did not request this, please ignore this email.</p>
                        <p>To reset your password, enter the following code in the app:</p>
                        <span style="display: inline-block; background-color: #e0e0e0; color: #000000;padding: 10px 20px;font-size: 24px;font-weight: bold; border-radius: 0.5rem;">{passwordResetCode}</span>
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
                message["From"] = smtp_settings["smtp_mail"]
                message["To"] = email
                server.send_message(message)
                server.quit()
                Log.success(
                    f'Password reset code: "{passwordResetCode}" sent to "{email}" for user: "{userName}"'
                )
                flashMessage(
                    page="passwordReset",
                    message="code",
                    category="success",
                    language=session["language"],
                )
                return redirect("/passwordreset/codesent=true")
            else:
                Log.error(f'User: "{userName}" with email: "{email}" not found')
                flashMessage(
                    page="passwordReset",
                    message="notFound",
                    category="error",
                    language=session["language"],
                )

        return render_template(
            "passwordReset.html",
            form=form,
            mailSent=False,
        )
