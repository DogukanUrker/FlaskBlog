import os
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
from sqlalchemy import func

from database import db
from models import User
from settings import Settings
from utils.flash_message import flash_message
from utils.forms.verify_user_form import VerifyUserForm
from utils.log import Log
from utils.route_guards import login_required

verify_user_blueprint = Blueprint("verify_user", __name__)

# Rate limiting constants
MAX_VERIFY_ATTEMPTS = 5
LOCKOUT_DURATION = 900  # 15 minutes in seconds
CODE_EXPIRY = 900  # 15 minutes in seconds


@verify_user_blueprint.route(
    "/verify-user/codesent=<code_sent>", methods=["GET", "POST"]
)
@login_required("verify user")
def verify_user(code_sent):
    """
    This function handles the verification of the user's account.

    Args:
        code_sent (str): A string indicating whether the verification code has been sent or not.

    Returns:
        redirect: A redirect to the homepage if the user is verified, or a rendered template with the verification form.

    """

    username = session["username"]

    user = User.query.filter(func.lower(User.username) == username.lower()).first()

    if not user:
        return redirect("/")

    if user.is_verified == "True":
        return redirect("/")
    elif user.is_verified == "False":
        form = VerifyUserForm(request.form)

        if code_sent == "true":
            if request.method == "POST":
                code = request.form["code"]

                # Check rate limiting
                lockout_until = session.get("verify_user_lockout_until", 0)
                if time.time() < lockout_until:
                    flash_message(
                        page="verify_user",
                        message="too_many_attempts",
                        category="error",
                        language=session.get("language", "en"),
                    )
                    return render_template(
                        "verify_user.html",
                        form=form,
                        mail_sent=True,
                    )

                # Check code expiry
                code_timestamp = session.get("verification_code_timestamp", 0)
                if time.time() - code_timestamp > CODE_EXPIRY:
                    session.pop("verification_code", None)
                    session.pop("verification_code_timestamp", None)
                    session.pop("verify_user_attempts", None)
                    flash_message(
                        page="verify_user",
                        message="code_expired",
                        category="error",
                        language=session.get("language", "en"),
                    )
                    return redirect("/verify-user/codesent=false")

                if code == session.get("verification_code"):
                    # Clear verification session data
                    session.pop("verification_code", None)
                    session.pop("verification_code_timestamp", None)
                    session.pop("verify_user_attempts", None)
                    session.pop("verify_user_lockout_until", None)

                    user.is_verified = "True"
                    db.session.commit()

                    Log.success(f'User: "{username}" has been verified')
                    flash_message(
                        page="verify_user",
                        message="success",
                        category="success",
                        language=session.get("language", "en"),
                    )
                    return redirect("/")
                else:
                    # Track failed attempts
                    attempts = session.get("verify_user_attempts", 0) + 1
                    session["verify_user_attempts"] = attempts

                    if attempts >= MAX_VERIFY_ATTEMPTS:
                        session["verify_user_lockout_until"] = (
                            time.time() + LOCKOUT_DURATION
                        )
                        session.pop("verification_code", None)
                        session.pop("verification_code_timestamp", None)
                        session["verify_user_attempts"] = 0
                        Log.error(
                            f'Too many failed verification attempts for user: "{username}"'
                        )
                        flash_message(
                            page="verify_user",
                            message="too_many_attempts",
                            category="error",
                            language=session.get("language", "en"),
                        )
                    else:
                        flash_message(
                            page="verify_user",
                            message="wrong",
                            category="error",
                            language=session.get("language", "en"),
                        )

            return render_template(
                "verify_user.html",
                form=form,
                mail_sent=True,
            )
        elif code_sent == "false":
            if request.method == "POST":
                # Check rate limiting
                lockout_until = session.get("verify_user_lockout_until", 0)
                if time.time() < lockout_until:
                    flash_message(
                        page="verify_user",
                        message="too_many_attempts",
                        category="error",
                        language=session.get("language", "en"),
                    )
                    return render_template(
                        "verify_user.html",
                        form=form,
                        mail_sent=False,
                    )

                if user:
                    verification_code = (
                        "123456"
                        if os.environ.get("E2E_TESTING") == "1"
                        else str(randint(100000, 999999))
                    )
                    session["verification_code"] = verification_code
                    session["verification_code_timestamp"] = time.time()
                    session["verify_user_attempts"] = 0

                    try:
                        context = ssl.create_default_context()
                        server = smtplib.SMTP(Settings.SMTP_SERVER, Settings.SMTP_PORT)
                        server.ehlo()
                        server.starttls(context=context)
                        server.ehlo()
                        server.login(Settings.SMTP_MAIL, Settings.SMTP_PASSWORD)

                        message = EmailMessage()
                        message.set_content(
                            f"Hi {username},\nHere is your account verification code:\n{verification_code}"
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
                                            This verification code expires in 15 minutes. Please do not share this code with anyone.
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
                        message["To"] = user.email

                        server.send_message(message)
                        server.quit()
                        Log.success(
                            f'Verification code sent to "{user.email}" for user: "{username}"'
                        )
                    except Exception as e:
                        Log.error(
                            f'Failed to send verification email to "{user.email}" for user "{username}": {str(e)}'
                        )

                    return redirect("/verify-user/codesent=true")

            return render_template(
                "verify_user.html",
                form=form,
                mail_sent=False,
            )
