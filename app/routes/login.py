import sqlite3

from flask import (
    Blueprint,
    abort,
    flash,
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
from utils.forms.LoginForm import LoginForm
from utils.log import Log
from utils.rateLimiter import RateLimiter
from utils.redirectValidator import RedirectValidator
from utils.securityAuditLogger import SecurityAuditLogger

loginBlueprint = Blueprint("login", __name__)


@loginBlueprint.route("/login", methods=["GET", "POST"])
@loginBlueprint.route("/login/", methods=["GET", "POST"])
def login_redirect():
    """
    Redirect /login to /login/redirect=& for compatibility.
    """
    return redirect("/login/redirect=&")


@loginBlueprint.route("/login/redirect=<direct>", methods=["GET", "POST"])
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
    # Validate redirect URL to prevent open redirect attacks
    safe_redirect = RedirectValidator.safe_redirect_path(direct)
    if Settings.LOG_IN:
        if "userName" in session:
            Log.error(f'User: "{session["userName"]}" already logged in')
            return (
                redirect(safe_redirect),
                301,
            )
        else:
            form = LoginForm(request.form)
            if request.method == "POST":
                userName = request.form["userName"]
                password = request.form["password"]
                userName = userName.replace(" ", "")

                # Check rate limiting
                is_allowed, retry_after, rate_limit_msg = RateLimiter.check_rate_limit(
                    userName
                )
                if not is_allowed:
                    # Use flash directly since rate_limit_msg contains dynamic content
                    flash(rate_limit_msg, "error")
                    return render_template(
                        "login.html",
                        form=form,
                        hideLogin=True,
                        siteKey=Settings.RECAPTCHA_SITE_KEY,
                        recaptcha=Settings.RECAPTCHA,
                    )

                Log.database(f"Connecting to '{Settings.DB_USERS_ROOT}' database")
                connection = sqlite3.connect(Settings.DB_USERS_ROOT)
                connection.set_trace_callback(Log.database)
                cursor = connection.cursor()
                cursor.execute(
                    """select * from users where lower(userName) = ? """,
                    [(userName.lower())],
                )
                user = cursor.fetchone()

                # Use generic error message to prevent username enumeration
                login_failed = False
                if not user:
                    Log.error(f'User: "{userName}" not found')
                    login_failed = True
                elif not encryption.verify(password, user[3]):
                    Log.error(f'Wrong password for user: "{userName}"')
                    login_failed = True

                if login_failed:
                    # Record failed attempt
                    RateLimiter.record_attempt(userName, success=False)

                    # Log failed login attempt to security audit
                    if user and user[5] == "admin":
                        SecurityAuditLogger.log_admin_login(
                            userName=userName,
                            ip_address=request.remote_addr,
                            user_agent=request.headers.get('User-Agent', ''),
                            success=False
                        )
                    else:
                        SecurityAuditLogger.log_user_login(
                            userName=userName,
                            ip_address=request.remote_addr,
                            user_agent=request.headers.get('User-Agent', ''),
                            success=False
                        )

                    flashMessage(
                        page="login",
                        message="invalid",
                        category="error",
                        language=session.get("language", "en"),
                    )
                else:
                    # Password is correct
                    if user:
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
                                    f"Login reCAPTCHA | verification: {verifyResponse.get('success')} | score: {verifyResponse.get('score')}",
                                )
                                abort(401)

                            Log.success(
                                f"Login reCAPTCHA | verification: {verifyResponse['success']} | score: {verifyResponse.get('score')}",
                            )

                        # Record successful login
                        RateLimiter.record_attempt(userName, success=True)

                        # Check if 2FA is enabled (index 11 in user tuple)
                        twofa_enabled = user[11] if len(user) > 11 else "False"

                        if twofa_enabled == "True":
                            # User has 2FA enabled - redirect to verification
                            session["pending_2fa_userName"] = user[1]
                            Log.info(f'User: "{user[1]}" requires 2FA verification')

                            flashMessage(
                                page="login",
                                message="2faRequired",
                                category="info",
                                language=session.get("language", "en"),
                            )

                            return redirect(f"/verify-2fa/redirect={direct}")

                        # No 2FA - complete login normally
                        session["userName"] = user[1]
                        session["userRole"] = user[5]
                        addPoints(1, session["userName"])
                        Log.success(f'User: "{user[1]}" logged in')

                        # Log successful login to security audit
                        if user[5] == "admin":
                            SecurityAuditLogger.log_admin_login(
                                userName=user[1],
                                ip_address=request.remote_addr,
                                user_agent=request.headers.get('User-Agent', ''),
                                success=True
                            )
                        else:
                            SecurityAuditLogger.log_user_login(
                                userName=user[1],
                                ip_address=request.remote_addr,
                                user_agent=request.headers.get('User-Agent', ''),
                                success=True
                            )

                        # Check if admin user must change password on first login
                        must_change_password = user[13] if len(user) > 13 else "False"
                        if user[5] == "admin" and must_change_password == "True":
                            Log.info(f'Admin user: "{user[1]}" must change password on first login')
                            flashMessage(
                                page="login",
                                message="mustChangePassword",
                                category="warning",
                                language=session.get("language", "en"),
                            )
                            return redirect("/force-change-password")

                        flashMessage(
                            page="login",
                            message="success",
                            category="success",
                            language=session.get("language", "en"),
                        )

                        return (
                            redirect(safe_redirect),
                            301,
                        )

            return render_template(
                "login.html",
                form=form,
                hideLogin=True,
                siteKey=Settings.RECAPTCHA_SITE_KEY,
                recaptcha=Settings.RECAPTCHA,
            )
    else:
        return (
            redirect(safe_redirect),
            301,
        )
