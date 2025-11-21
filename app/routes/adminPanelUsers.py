import smtplib
import sqlite3
import ssl
from email.message import EmailMessage

from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    session,
)
from settings import Settings
from utils.changeUserRole import changeUserRole
from utils.delete import Delete
from utils.flashMessage import flashMessage
from utils.log import Log
from utils.paginate import paginate_query
from utils.securityAuditLogger import SecurityAuditLogger
from utils.smtpSettings import SMTPSettings
from utils.twofaResetTokenManager import TwoFAResetTokenManager

adminPanelUsersBlueprint = Blueprint("adminPanelUsers", __name__)


@adminPanelUsersBlueprint.route("/admin/users", methods=["GET", "POST"])
@adminPanelUsersBlueprint.route("/adminpanel/users", methods=["GET", "POST"])
def adminPanelUsers():
    if "userName" in session:
        Log.info(f"Admin: {session['userName']} reached to users admin panel")
        Log.database(f"Connecting to '{Settings.DB_USERS_ROOT}' database")

        connection = sqlite3.connect(Settings.DB_USERS_ROOT)
        connection.set_trace_callback(Log.database)
        cursor = connection.cursor()
        cursor.execute(
            """select role from users where userName = ? """,
            [(session["userName"])],
        )
        role = cursor.fetchone()[0]

        if request.method == "POST":
            if "userDeleteButton" in request.form:
                Log.info(
                    f"Admin: {session['userName']} deleted user: {request.form['userName']}"
                )

                # Log admin action to security audit
                SecurityAuditLogger.log_admin_action(
                    userName=session['userName'],
                    ip_address=request.remote_addr,
                    action="Deleted user",
                    target=request.form['userName']
                )

                Delete.user(request.form["userName"])

            if "userRoleChangeButton" in request.form:
                Log.info(
                    f"Admin: {session['userName']} changed {request.form['userName']}'s role"
                )

                # Log admin action to security audit
                SecurityAuditLogger.log_admin_action(
                    userName=session['userName'],
                    ip_address=request.remote_addr,
                    action="Changed user role",
                    target=request.form['userName']
                )

                changeUserRole(request.form["userName"])

            if "reset2faButton" in request.form:
                target_user = request.form["userName"]
                Log.info(
                    f"Admin: {session['userName']} initiated 2FA reset for user: {target_user}"
                )

                # Get user's email
                cursor.execute(
                    """SELECT email FROM users WHERE userName = ?""",
                    (target_user,)
                )
                user_result = cursor.fetchone()

                if user_result and user_result[0]:
                    user_email = user_result[0]

                    # Generate reset token
                    token = TwoFAResetTokenManager.generate_reset_token(
                        target_user,
                        session['userName'],
                        expiry_hours=24
                    )

                    # Create reset URL
                    reset_url = f"{request.host_url}confirm-2fa-reset/{token}"

                    try:
                        # Get SMTP settings
                        smtp_settings = SMTPSettings.get_settings()

                        # Send email
                        context = ssl.create_default_context()
                        server = smtplib.SMTP(smtp_settings["smtp_server"], smtp_settings["smtp_port"])
                        server.ehlo()
                        server.starttls(context=context)
                        server.ehlo()
                        server.login(smtp_settings["smtp_mail"], smtp_settings["smtp_password"])

                        message = EmailMessage()
                        message.set_content(
                            f"Hi {target_user},\n\n"
                            f"An administrator has requested to reset two-factor authentication (2FA) for your account.\n\n"
                            f"If you requested this reset, please click the link below to confirm:\n"
                            f"{reset_url}\n\n"
                            f"This link will expire in 24 hours.\n\n"
                            f"If you did NOT request this reset, please ignore this email and contact an administrator immediately.\n\n"
                            f"Best regards,\n{Settings.APP_NAME}"
                        )
                        message.add_alternative(
                            f"""\
                            <html>
                            <body style="font-family: Arial, sans-serif;">
                            <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; padding: 20px; border-radius: 0.5rem;">
                                <div style="text-align: center;">
                                    <h1 style="color: #F43F5E;">2FA Reset Request</h1>
                                    <p>Hello, {target_user}.</p>
                                    <p>An administrator has requested to reset two-factor authentication (2FA) for your account.</p>
                                    <p>If you requested this reset, click the button below to confirm:</p>
                                    <a href="{reset_url}" style="display: inline-block; background-color: #F43F5E; color: #ffffff; padding: 12px 24px; font-size: 16px; font-weight: bold; border-radius: 0.5rem; text-decoration: none; margin: 20px 0;">Confirm 2FA Reset</a>
                                    <p style="font-size: 14px; color: #666;">This link will expire in 24 hours.</p>
                                    <p style="font-size: 14px; color: #dc2626; font-weight: bold;">If you did NOT request this reset, please ignore this email and contact an administrator immediately.</p>
                                    <hr style="margin: 20px 0; border: none; border-top: 1px solid #e0e0e0;">
                                    <p style="font-size: 12px; color: #999;">Thank you for using {Settings.APP_NAME}.</p>
                                </div>
                            </div>
                            </body>
                            </html>
                        """,
                            subtype="html",
                        )
                        message["Subject"] = "2FA Reset Request"
                        message["From"] = smtp_settings["smtp_mail"]
                        message["To"] = user_email
                        server.send_message(message)
                        server.quit()

                        # Log admin action to security audit
                        SecurityAuditLogger.log_admin_action(
                            userName=session['userName'],
                            ip_address=request.remote_addr,
                            action="Sent 2FA reset email",
                            target=target_user
                        )

                        Log.success(f"2FA reset email sent to {user_email} for user: {target_user}")
                        flashMessage(
                            page="adminPanelUsers",
                            message="reset2faEmailSent",
                            category="success",
                            language=session.get("language", "en")
                        )

                    except Exception as e:
                        Log.error(f"Failed to send 2FA reset email: {e}")
                        flashMessage(
                            page="adminPanelUsers",
                            message="reset2faEmailFailed",
                            category="error",
                            language=session.get("language", "en")
                        )
                else:
                    Log.error(f"User {target_user} not found or has no email")
                    flashMessage(
                        page="adminPanelUsers",
                        message="userNotFound",
                        category="error",
                        language=session.get("language", "en")
                    )

        if role == "admin":
            users, page, total_pages = paginate_query(
                Settings.DB_USERS_ROOT,
                "select count(*) from users",
                "select * from users",
            )

            Log.info(f"Rendering adminPanelUsers.html: params: users={users}")

            return render_template(
                "adminPanelUsers.html",
                users=users,
                page=page,
                total_pages=total_pages,
            )
        else:
            Log.error(
                f"{request.remote_addr} tried to reach user admin panel without being admin"
            )

            return redirect("/")
    else:
        Log.error(
            f"{request.remote_addr} tried to reach user admin panel being logged in"
        )

        return redirect("/")
