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
from utils.flashMessage import flashMessage
from utils.forms.VerifyUserForm import VerifyUserForm
from utils.log import Log
from utils.smtpSettings import SMTPSettings

verifyUserBlueprint = Blueprint("verifyUser", __name__)


@verifyUserBlueprint.route("/verifyUser/codesent=<codeSent>", methods=["GET", "POST"])
def verifyUser(codeSent):
    """
    This function handles the verification of the user's account.

    Args:
        codeSent (str): A string indicating whether the verification code has been sent or not.

    Returns:
        redirect: A redirect to the homepage if the user is verified, or a rendered template with the verification form.

    """

    if "userName" in session:
        userName = session["userName"]
        Log.database(f"Connecting to '{Settings.DB_USERS_ROOT}' database")
        Log.database(f"Connecting to '{Settings.DB_USERS_ROOT}' database")

        connection = sqlite3.connect(Settings.DB_USERS_ROOT)
        connection.set_trace_callback(Log.database)
        cursor = connection.cursor()

        cursor.execute(
            """select isVerified from users where lower(username) = ? """,
            [(userName.lower())],
        )
        isVerfied = cursor.fetchone()[0]

        if isVerfied == "True":
            return redirect("/")
        elif isVerfied == "False":
            form = VerifyUserForm(request.form)

            if codeSent == "true":
                if request.method == "POST":
                    code = request.form["code"]

                    # Get verification code from session
                    verificationCode = session.get("verificationCode", "")

                    if code == verificationCode:
                        cursor.execute(
                            """update users set isVerified = "True" where lower(userName) = ? """,
                            [(userName.lower())],
                        )
                        connection.commit()
                        Log.success(f'User: "{userName}" has been verified')
                        flashMessage(
                            page="verifyUser",
                            message="success",
                            category="success",
                            language=session["language"],
                        )
                        return redirect("/")
                    else:
                        flashMessage(
                            page="verifyUser",
                            message="wrong",
                            category="error",
                            language=session["language"],
                        )

                return render_template(
                    "verifyUser.html",
                    form=form,
                    mailSent=True,
                )
            elif codeSent == "false":
                if request.method == "POST":
                    cursor.execute(
                        """select * from users where lower(userName) = ? """,
                        [(userName.lower())],
                    )
                    userNameDB = cursor.fetchone()

                    cursor.execute(
                        """select email from users where lower(username) = ? """,
                        [(userName.lower())],
                    )
                    email = cursor.fetchone()

                    if userNameDB:
                        # Get SMTP settings from database
                        smtp_settings = SMTPSettings.get_settings()

                        try:
                            context = ssl.create_default_context()
                            server = smtplib.SMTP(smtp_settings["smtp_server"], smtp_settings["smtp_port"])
                            server.ehlo()
                            server.starttls(context=context)
                            server.ehlo()
                            server.login(smtp_settings["smtp_mail"], smtp_settings["smtp_password"])

                            verificationCode = str(randint(1000, 9999))

                            # Store verification code in session
                            session["verificationCode"] = verificationCode

                            message = EmailMessage()
                            message.set_content(
                                f"Hi {userName},\n\nHere is your account verification code:\n{verificationCode}\n\nThis code is valid for a limited time."
                            )
                            message.add_alternative(
                                f"""\
                                    <html>
                                    <body>
                                        <div
                                        style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background-color: #ffffff; padding: 20px; border-radius:0.5rem;"
                                        >
                                        <div style="text-align: center;">
                                            <h1 style="color: #F43F5E;">Verify Your Account</h1>
                                            <p style="font-size: 16px;">
                                            Hello, {userName}.
                                            </p>
                                            <p style="font-size: 16px;">
                                            Please enter the verification code below to verify your account.
                                            </p>
                                            <div
                                            style="background-color: #f0f0f0; padding: 10px; border-radius: 5px; margin: 20px 0;"
                                            >
                                            <p style="font-size: 24px; font-weight: bold; margin: 0;">
                                                {verificationCode}
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
                            message["Subject"] = f"Verify your {Settings.APP_NAME} account"
                            message["From"] = smtp_settings["smtp_mail"]
                            message["To"] = email[0]

                            server.send_message(message)
                            server.quit()
                            Log.success(
                                f'Verification code sent to "{email[0]}" for user: "{userName}"'
                            )

                            flashMessage(
                                page="verifyUser",
                                message="code",
                                category="success",
                                language=session.get("language", "en"),
                            )

                        except Exception as e:
                            Log.error(f'Failed to send verification email: {e}')

                        return redirect("/verifyUser/codesent=true")

                return render_template(
                    "verifyUser.html",
                    form=form,
                    mailSent=False,
                )
    else:
        Log.error(f"{request.remote_addr} tried to verify user without being logged in")
        return redirect("/")
