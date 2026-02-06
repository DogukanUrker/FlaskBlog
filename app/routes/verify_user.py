import smtplib
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
from sqlalchemy import func

from database import db
from models import User
from settings import Settings
from utils.flash_message import flash_message
from utils.forms.verify_user_form import VerifyUserForm
from utils.log import Log
from utils.route_guards import login_required

verify_user_blueprint = Blueprint("verify_user", __name__)


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
        global verification_code

        form = VerifyUserForm(request.form)

        if code_sent == "true":
            if request.method == "POST":
                code = request.form["code"]

                if code == verification_code:
                    user.is_verified = "True"
                    db.session.commit()

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
                if user:
                    context = ssl.create_default_context()
                    server = smtplib.SMTP(Settings.SMTP_SERVER, Settings.SMTP_PORT)
                    server.ehlo()
                    server.starttls(context=context)
                    server.ehlo()
                    server.login(Settings.SMTP_MAIL, Settings.SMTP_PASSWORD)

                    verification_code = str(randint(1000, 9999))

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
                    message["To"] = user.email

                    server.send_message(message)
                    server.quit()
                    Log.success(
                        f'Verification code sent to "{user.email}" for user: "{username}"'
                    )

                    return redirect("/verify-user/codesent=true")

            return render_template(
                "verify_user.html",
                form=form,
                mail_sent=False,
            )
