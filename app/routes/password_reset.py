import smtplib
import ssl
import time
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
from sqlalchemy import func

from database import db
from models import User
from settings import Settings
from utils.flash_message import flash_message
from utils.forms.password_reset_form import PasswordResetForm
from utils.log import Log

password_reset_blueprint = Blueprint("password_reset", __name__)

# Rate limiting constants
MAX_RESET_ATTEMPTS = 5
LOCKOUT_DURATION = 900  # 15 minutes in seconds
CODE_EXPIRY = 900  # 15 minutes in seconds


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
        if request.method == "POST":
            username = request.form["username"]
            username = username.replace(" ", "")
            code = request.form["code"]
            password = request.form["password"]
            password_confirm = request.form["password_confirm"]

            # Check rate limiting
            lockout_until = session.get("password_reset_lockout_until", 0)
            if time.time() < lockout_until:
                flash_message(
                    page="password_reset",
                    message="too_many_attempts",
                    category="error",
                    language=session.get("language", "en"),
                )
                return render_template(
                    "password_reset.html",
                    form=form,
                    mail_sent=True,
                )

            # Check code expiry
            code_timestamp = session.get("password_reset_timestamp", 0)
            if time.time() - code_timestamp > CODE_EXPIRY:
                session.pop("password_reset_code", None)
                session.pop("password_reset_username", None)
                session.pop("password_reset_timestamp", None)
                session.pop("password_reset_attempts", None)
                flash_message(
                    page="password_reset",
                    message="code_expired",
                    category="error",
                    language=session.get("language", "en"),
                )
                return redirect("/password-reset/codesent=false")

            stored_code = session.get("password_reset_code", "")
            stored_username = session.get("password_reset_username", "")

            if code == stored_code and username.lower() == stored_username.lower():
                user = User.query.filter(
                    func.lower(User.username) == username.lower()
                ).first()

                if not user:
                    flash_message(
                        page="password_reset",
                        message="invalid_credentials",
                        category="error",
                        language=session.get("language", "en"),
                    )
                else:
                    if password == password_confirm:
                        if encryption.verify(password, user.password):
                            flash_message(
                                page="password_reset",
                                message="same",
                                category="error",
                                language=session.get("language", "en"),
                            )
                        else:
                            # Clear all password reset session data
                            session.pop("password_reset_code", None)
                            session.pop("password_reset_username", None)
                            session.pop("password_reset_timestamp", None)
                            session.pop("password_reset_attempts", None)
                            session.pop("password_reset_lockout_until", None)

                            user.password = encryption.hash(password)
                            db.session.commit()

                            Log.success(f'User: "{username}" changed his password')
                            flash_message(
                                page="password_reset",
                                message="success",
                                category="success",
                                language=session.get("language", "en"),
                            )
                            return redirect("/login/redirect=&")
                    else:
                        flash_message(
                            page="password_reset",
                            message="match",
                            category="error",
                            language=session.get("language", "en"),
                        )
            else:
                # Track failed attempts
                attempts = session.get("password_reset_attempts", 0) + 1
                session["password_reset_attempts"] = attempts

                if attempts >= MAX_RESET_ATTEMPTS:
                    session["password_reset_lockout_until"] = (
                        time.time() + LOCKOUT_DURATION
                    )
                    session.pop("password_reset_code", None)
                    session.pop("password_reset_username", None)
                    session.pop("password_reset_timestamp", None)
                    session["password_reset_attempts"] = 0
                    Log.error(
                        f'Too many failed password reset attempts for user: "{username}"'
                    )
                    flash_message(
                        page="password_reset",
                        message="too_many_attempts",
                        category="error",
                        language=session.get("language", "en"),
                    )
                else:
                    flash_message(
                        page="password_reset",
                        message="invalid_credentials",
                        category="error",
                        language=session.get("language", "en"),
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

            # Check rate limiting
            lockout_until = session.get("password_reset_lockout_until", 0)
            if time.time() < lockout_until:
                flash_message(
                    page="password_reset",
                    message="too_many_attempts",
                    category="error",
                    language=session.get("language", "en"),
                )
                return render_template(
                    "password_reset.html",
                    form=form,
                    mail_sent=False,
                )

            user = User.query.filter(
                func.lower(User.username) == username.lower(),
                func.lower(User.email) == email.lower(),
            ).first()

            if user:
                context = ssl.create_default_context()
                server = smtplib.SMTP(Settings.SMTP_SERVER, Settings.SMTP_PORT)
                server.ehlo()
                server.starttls(context=context)
                server.ehlo()
                server.login(Settings.SMTP_MAIL, Settings.SMTP_PASSWORD)
                password_reset_code = str(randint(100000, 999999))
                session["password_reset_code"] = password_reset_code
                session["password_reset_username"] = username
                session["password_reset_timestamp"] = time.time()
                session["password_reset_attempts"] = 0
                message = EmailMessage()
                message.set_content(
                    f"Hi {username},\nForgot your password? No problem.\nHere is your password reset code:\n{password_reset_code}"
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
                        <p style="font-family: Arial, sans-serif; font-size: 16px;">This code will expire in 15 minutes.</p>
                        <p>Thank you for using {Settings.APP_NAME}.</p>
                        </div>
                    </div>
                    </body>
                    </html>
                """,
                    subtype="html",
                )
                message["Subject"] = "Forget Password?"
                message["From"] = Settings.SMTP_MAIL
                message["To"] = email
                server.send_message(message)
                server.quit()
                Log.success(
                    f'Password reset code sent to "{email}" for user: "{username}"'
                )
                flash_message(
                    page="password_reset",
                    message="code",
                    category="success",
                    language=session.get("language", "en"),
                )
                return redirect("/password-reset/codesent=true")
            else:
                Log.error(f'User: "{username}" with email: "{email}" not found')
                flash_message(
                    page="password_reset",
                    message="invalid_credentials",
                    category="error",
                    language=session.get("language", "en"),
                )

        return render_template(
            "password_reset.html",
            form=form,
            mail_sent=False,
        )
