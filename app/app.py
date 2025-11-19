"""
This file contains the main function
"""

from datetime import timedelta

from flask import Flask
from flask_wtf.csrf import (
    CSRFError,
    CSRFProtect,
)
from routes.about import (
    aboutBlueprint,
)
from routes.accountSettings import (
    accountSettingsBlueprint,
)
from routes.adminPanel import (
    adminPanelBlueprint,
)
from routes.adminPanelComments import (
    adminPanelCommentsBlueprint,
)
from routes.adminPanelPosts import (
    adminPanelPostsBlueprint,
)
from routes.adminPanelUsers import (
    adminPanelUsersBlueprint,
)
from routes.adminPanelSecurityAudit import (
    adminPanelSecurityAuditBlueprint,
)
from routes.adminPanelSiteSettings import (
    adminPanelSiteSettingsBlueprint,
)
from routes.category import (
    categoryBlueprint,
)
from routes.changeLanguage import (
    changeLanguageBlueprint,
)
from routes.changePassword import (
    changePasswordBlueprint,
)
from routes.changeProfilePicture import (
    changeProfilePictureBlueprint,
)
from routes.changeUserName import (
    changeUserNameBlueprint,
)
from routes.createPost import (
    createPostBlueprint,
)
from routes.setup2fa import (
    setup2faBlueprint,
)
from routes.disable2fa import (
    disable2faBlueprint,
)
from routes.verify2fa import (
    verify2faBlueprint,
)
from routes.dashboard import (
    dashboardBlueprint,
)
from routes.editPost import (
    editPostBlueprint,
)
from routes.index import (
    indexBlueprint,
)
from routes.markdownPreview import (
    markdownPreviewBlueprint,
)
from routes.login import (
    loginBlueprint,
)
from routes.logout import (
    logoutBlueprint,
)
from routes.passwordReset import (
    passwordResetBlueprint,
)
from routes.post import postBlueprint
from routes.postsAnalytics import (
    analyticsBlueprint,
)
from routes.privacyPolicy import (
    privacyPolicyBlueprint,
)
from routes.returnPostAnalyticsData import (
    returnPostAnalyticsDataBlueprint,
)
from routes.returnPostBanner import (
    returnPostBannerBlueprint,
)
from routes.search import (
    searchBlueprint,
)
from routes.searchBar import (
    searchBarBlueprint,
)
from routes.setLanguage import (
    setLanguageBlueprint,
)
from routes.setTheme import (
    setThemeBlueprint,
)
from routes.signup import (
    signUpBlueprint,
)
from routes.user import userBlueprint
from routes.verifyUser import (
    verifyUserBlueprint,
)
from settings import Settings
from utils.afterRequest import (
    afterRequestLogger,
)
from utils.beforeRequest.browserLanguage import browserLanguage
from utils.contextProcessor.isLogin import isLogin
from utils.contextProcessor.isRegistration import isRegistration
from utils.contextProcessor.returnPostUrlID import returnPostUrlID
from utils.contextProcessor.returnPostUrlSlug import returnPostUrlSlug
from utils.contextProcessor.returnUserProfilePicture import returnUserProfilePicture
from utils.contextProcessor.siteLogo import siteLogo
from utils.contextProcessor.socialSharing import socialSharing
from utils.contextProcessor.translations import injectTranslations
from utils.contextProcessor.markdown import markdown_processor
from utils.dbChecker import (
    analyticsTable,
    commentsTable,
    dbFolder,
    postsTable,
    securityAuditLogTable,
    siteSettingsTable,
    twoFactorAuthFields,
    usersTable,
)
from utils.errorHandlers.csrfErrorHandler import (
    csrfErrorHandler,
)
from utils.errorHandlers.notFoundErrorHandler import (
    notFoundErrorHandler,
)
from utils.errorHandlers.unauthorizedErrorHandler import (
    unauthorizedErrorHandler,
)
from utils.generateUrlIdFromPost import getSlugFromPostTitle
from utils.log import Log
from utils.terminalASCII import terminalASCII
from utils.time import currentTimeStamp

startTime = currentTimeStamp()


print(terminalASCII())


Log.info("Starting...")


app = Flask(
    import_name=Settings.APP_NAME,
    root_path=Settings.APP_ROOT_PATH,
)


app.jinja_options["autoescape"] = True


app.secret_key = Settings.APP_SECRET_KEY
app.config["SESSION_PERMANENT"] = Settings.SESSION_PERMANENT
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(seconds=Settings.PERMANENT_SESSION_LIFETIME)
app.config["SESSION_COOKIE_SECURE"] = Settings.SESSION_COOKIE_SECURE
app.config["SESSION_COOKIE_HTTPONLY"] = Settings.SESSION_COOKIE_HTTPONLY
app.config["SESSION_COOKIE_SAMESITE"] = Settings.SESSION_COOKIE_SAMESITE
app.config["MAX_CONTENT_LENGTH"] = Settings.MAX_UPLOAD_SIZE


csrf = CSRFProtect(app)


app.context_processor(isLogin)

app.context_processor(isRegistration)
app.context_processor(returnUserProfilePicture)
app.context_processor(returnPostUrlID)
app.context_processor(returnPostUrlSlug)
app.context_processor(siteLogo)
app.context_processor(socialSharing)
app.context_processor(injectTranslations)
app.context_processor(markdown_processor)
app.before_request(browserLanguage)
app.jinja_env.globals.update(getSlugFromPostTitle=getSlugFromPostTitle)

if Settings.WERKZEUG_LOGGER:
    Log.warning("Werkzeug default logger is enabled")
else:
    from logging import getLogger

    Log.info("Werkzeug default logger is disabled")

    getLogger("werkzeug").disabled = True


if Settings.TAMGA_LOGGER:
    Log.info("Custom logger is enabled")
else:
    Log.info("Custom logger is disabled")


Log.info(f"Debug mode: {Settings.DEBUG_MODE}")
Log.info(f"Name: {Settings.APP_NAME}")
Log.info(f"Version: {Settings.APP_VERSION}")
Log.info(f"Host: {Settings.APP_HOST}")
Log.info(f"Port: {Settings.APP_PORT}")
Log.info(f"Session permanent: {Settings.SESSION_PERMANENT}")
Log.info(f"Root path: {Settings.APP_ROOT_PATH}")
Log.info(f"Log folder root: {Settings.LOG_FOLDER_ROOT}")
Log.info(f"Log file root: {Settings.LOG_FILE_ROOT}")
Log.info(f"Log in: {Settings.LOG_IN}")
Log.info(f"Registration: {Settings.REGISTRATION}")

Log.info(f"SMTP server: {Settings.SMTP_SERVER}")
Log.info(f"SMTP port: {Settings.SMTP_PORT}")
Log.info(f"SMTP mail: {Settings.SMTP_MAIL}")


if Settings.RECAPTCHA:
    if Settings.RECAPTCHA_SITE_KEY == "" or Settings.RECAPTCHA_SECRET_KEY == "":
        Log.error(
            "reCAPTCHA keys is unvalid this may cause the application to crash",
        )
        Log.error(
            "Please check your recaptcha keys or set recaptcha to false from true in 'settings.py'",
        )
    else:
        Log.info("reCAPTCHA is on for login and signup pages")
        Log.info(f"reCAPTCHA recaptcha site key: {Settings.RECAPTCHA_SITE_KEY}")
        Log.info(f"reCAPTCHA verify url: {Settings.RECAPTCHA_VERIFY_URL}")

else:
    Log.info("reCAPTCHA is off")


if Settings.DEFAULT_ADMIN:
    Log.info("Default admin is on")
    Log.info(f"Default admin username: {Settings.DEFAULT_ADMIN_USERNAME}")
    Log.info(f"Default admin email: {Settings.DEFAULT_ADMIN_EMAIL}")
    Log.info(f"Default admin point: {Settings.DEFAULT_ADMIN_POINT}")
    Log.info(f"Default admin profile picture: {Settings.DEFAULT_ADMIN_PROFILE_PICTURE}")
else:
    Log.info("Default admin is off")


dbFolder()
usersTable()
postsTable()
commentsTable()
analyticsTable()
securityAuditLogTable()
twoFactorAuthFields()
siteSettingsTable()


@app.errorhandler(404)
def notFound(e):
    return notFoundErrorHandler(e)


@app.errorhandler(401)
def unauthorized(e):
    return unauthorizedErrorHandler(e)


@app.errorhandler(CSRFError)
def csrfError(e):
    return csrfErrorHandler(e)


@app.after_request
def afterRequest(response):
    response = afterRequestLogger(response)

    # Content Security Policy (using local assets only, no CDN)
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://www.google.com https://www.gstatic.com; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https: blob:; "
        "font-src 'self'; "
        "connect-src 'self'; "
        "frame-ancestors 'none'; "
        "base-uri 'self'; "
        "form-action 'self';"
    )

    # Additional security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

    # HSTS (only if using HTTPS)
    if Settings.SESSION_COOKIE_SECURE:
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )

    return response


app.register_blueprint(postBlueprint)
app.register_blueprint(userBlueprint)
app.register_blueprint(indexBlueprint)
app.register_blueprint(aboutBlueprint)
app.register_blueprint(loginBlueprint)
app.register_blueprint(signUpBlueprint)
app.register_blueprint(logoutBlueprint)
app.register_blueprint(searchBlueprint)
app.register_blueprint(categoryBlueprint)
app.register_blueprint(editPostBlueprint)
app.register_blueprint(dashboardBlueprint)
app.register_blueprint(searchBarBlueprint)
app.register_blueprint(adminPanelBlueprint)
app.register_blueprint(createPostBlueprint)
app.register_blueprint(verifyUserBlueprint)
app.register_blueprint(setLanguageBlueprint)
app.register_blueprint(setThemeBlueprint)
app.register_blueprint(privacyPolicyBlueprint)
app.register_blueprint(passwordResetBlueprint)
app.register_blueprint(changeUserNameBlueprint)
app.register_blueprint(changePasswordBlueprint)
app.register_blueprint(changeLanguageBlueprint)
app.register_blueprint(adminPanelUsersBlueprint)
app.register_blueprint(adminPanelPostsBlueprint)
app.register_blueprint(adminPanelSecurityAuditBlueprint)
app.register_blueprint(adminPanelSiteSettingsBlueprint)
app.register_blueprint(accountSettingsBlueprint)
app.register_blueprint(returnPostBannerBlueprint)
app.register_blueprint(adminPanelCommentsBlueprint)
app.register_blueprint(changeProfilePictureBlueprint)
app.register_blueprint(analyticsBlueprint)
app.register_blueprint(returnPostAnalyticsDataBlueprint)
app.register_blueprint(setup2faBlueprint)
app.register_blueprint(disable2faBlueprint)
app.register_blueprint(verify2faBlueprint)
app.register_blueprint(markdownPreviewBlueprint)


if __name__ == "__main__":
    Log.info(f"Running on http://{Settings.APP_HOST}:{Settings.APP_PORT}")
    Log.success("App started")

    print(terminalASCII())
    app.run(debug=Settings.DEBUG_MODE, host=Settings.APP_HOST, port=Settings.APP_PORT)

    endTime = currentTimeStamp()
    runTime = endTime - startTime
    runTime = str(timedelta(seconds=runTime))

    Log.info(f"Run time: {runTime} ")
    Log.info("Shut down")
    Log.warning("App shut down")

    print(terminalASCII())
