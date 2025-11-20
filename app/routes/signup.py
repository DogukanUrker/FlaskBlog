import smtplib
import sqlite3
import ssl
from email.message import EmailMessage
from random import randint

from flask import (
    Blueprint,
    abort,
    redirect,
    render_template,
    request,
    session,
)
from passlib.hash import sha512_crypt as encryption
from requests import post as requestsPost
from settings import Settings
from utils.addPoints import addPoints
from utils.flashMessage import flashMessage
from utils.forms.SignUpForm import SignUpForm
from utils.log import Log
from utils.time import currentTimeStamp
from utils.smtpSettings import SMTPSettings

signUpBlueprint = Blueprint("signup", __name__)


@signUpBlueprint.route("/signup", methods=["GET", "POST"])
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
        if "userName" in session:
            Log.error(f'USER: "{session["userName"]}" ALREADY LOGGED IN')
            return redirect("/")
        else:
            form = SignUpForm(request.form)

            if request.method == "POST":
                userName = request.form["userName"]
                email = request.form["email"]
                password = request.form["password"]
                passwordConfirm = request.form["passwordConfirm"]

                userName = userName.replace(" ", "")
                Log.database(f"Connecting to '{Settings.DB_USERS_ROOT}' database")

                connection = sqlite3.connect(Settings.DB_USERS_ROOT)
                connection.set_trace_callback(Log.database)
                cursor = connection.cursor()

                cursor.execute("select userName from users")
                users = str(cursor.fetchall())
                cursor.execute("select email from users")
                mails = str(cursor.fetchall())

                if userName not in users and email not in mails:
                    if passwordConfirm == password:
                        if userName.isascii():
                            password = encryption.hash(password)

                            if Settings.RECAPTCHA:
                                secretResponse = request.form["g-recaptcha-response"]
                                verifyResponse = requestsPost(
                                    url=f"{Settings.RECAPTCHA_VERIFY_URL}?secret={Settings.RECAPTCHA_SECRET_KEY}&response={secretResponse}"
                                ).json()
                                if not (
                                    verifyResponse["success"] is True
                                    or verifyResponse.get("score", 0) > 0.5
                                ):
                                    Log.error(
                                        f"Signup reCAPTCHA | verification: {verifyResponse.get('success')} | score: {verifyResponse.get('score')}",
                                    )
                                    abort(401)

                                Log.success(
                                    f"Signup reCAPTCHA | verification: {verifyResponse['success']} | score: {verifyResponse.get('score')}",
                                )

                            # Create user account
                            connection = sqlite3.connect(Settings.DB_USERS_ROOT)
                            connection.set_trace_callback(Log.database)
                            cursor = connection.cursor()
                            cursor.execute(
                                """
                                insert into users(userName,email,password,profilePicture,role,points,timeStamp,isVerified) \
                                values(?, ?, ?, ?, ?, ?, ?, ?)
                                """,
                                (
                                    userName,
                                    email,
                                    password,
                                    f"https://api.dicebear.com/7.x/identicon/svg?seed={userName}&radius=10",
                                    "user",
                                    0,
                                    currentTimeStamp(),
                                    "False",
                                ),
                            )
                            connection.commit()

                            Log.success(f'User: "{userName}" added to database')

                            session["userName"] = userName
                            addPoints(1, session["userName"])
                            Log.success(f'User: "{userName}" logged in')

                            flashMessage(
                                page="signup",
                                message="success",
                                category="success",
                                language=session["language"],
                            )

                            # Generate verification code
                            verificationCode = str(randint(1000, 9999))

                            # Store verification code in session for verification
                            session["verificationCode"] = verificationCode

                            # Get SMTP settings from database
                            smtp_settings = SMTPSettings.get_settings()

                            # Send verification email
                            try:
                                context = ssl.create_default_context()
                                server = smtplib.SMTP(
                                    smtp_settings["smtp_server"], smtp_settings["smtp_port"]
                                )
                                server.ehlo()
                                server.starttls(context=context)
                                server.ehlo()
                                server.login(smtp_settings["smtp_mail"], smtp_settings["smtp_password"])

                                mail = EmailMessage()
                                mail.set_content(
                                    f"Hi {userName},\n\nWelcome to {Settings.APP_NAME}!\n\nPlease verify your email address using this code: {verificationCode}\n\nThis code is valid for a limited time."
                                )
                                mail.add_alternative(
                                    f"""\
                                <html>
                                <body>
                                    <div
                                    style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background-color: #ffffff; padding: 20px; border-radius:0.5rem;"
                                    >
                                    <div style="text-align: center;">
                                        <h1 style="color: #F43F5E;">
                                        Welcome to {Settings.APP_NAME}!
                                        </h1>
                                        <p style="font-size: 16px;">
                                        Hi {userName}, thank you for creating an account.
                                        </p>
                                        <p style="font-size: 16px;">
                                        Please verify your email address using the code below:
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
                                mail["Subject"] = f"Verify your {Settings.APP_NAME} account"
                                mail["From"] = smtp_settings["smtp_mail"]
                                mail["To"] = email

                                server.send_message(mail)
                                server.quit()

                                Log.success(f'Verification email sent to "{email}" for user: "{userName}"')

                            except Exception as e:
                                Log.error(f'Failed to send verification email: {e}')

                            return redirect("/verifyUser/codesent=true")
                        else:
                            Log.error(
                                f'Username: "{userName}" do not fits to ascii characters',
                            )
                            flashMessage(
                                page="signup",
                                message="ascii",
                                category="error",
                                language=session["language"],
                            )
                    else:
                        Log.error("Passwords do not match")

                        flashMessage(
                            page="signup",
                            message="password",
                            category="error",
                            language=session["language"],
                        )

                if userName in users and email in mails:
                    Log.error(f'"{userName}" & "{email}" is unavailable ')
                    flashMessage(
                        page="signup",
                        message="taken",
                        category="error",
                        language=session["language"],
                    )
                if userName not in users and email in mails:
                    Log.error(f'This email "{email}" is unavailable')

                    flashMessage(
                        page="signup",
                        message="email",
                        category="error",
                        language=session["language"],
                    )
                if userName in users and email not in mails:
                    Log.error(f'This username "{userName}" is unavailable')

                    flashMessage(
                        page="signup",
                        message="username",
                        category="error",
                        language=session["language"],
                    )

            return render_template(
                "signup.html",
                form=form,
                hideSignUp=True,
                siteKey=Settings.RECAPTCHA_SITE_KEY,
                recaptcha=Settings.RECAPTCHA,
            )
    else:
        return redirect("/")
