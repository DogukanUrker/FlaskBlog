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
    about_blueprint,
)
from routes.account_settings import (
    account_settings_blueprint,
)
from routes.admin_panel import (
    admin_panel_blueprint,
)
from routes.admin_panel_comments import (
    admin_panel_comments_blueprint,
)
from routes.admin_panel_posts import (
    admin_panel_posts_blueprint,
)
from routes.admin_panel_users import (
    admin_panel_users_blueprint,
)
from routes.category import (
    category_blueprint,
)
from routes.change_language import (
    change_language_blueprint,
)
from routes.change_password import (
    change_password_blueprint,
)
from routes.change_profile_picture import (
    change_profile_picture_blueprint,
)
from routes.change_username import (
    change_username_blueprint,
)
from routes.create_post import (
    create_post_blueprint,
)
from routes.dashboard import (
    dashboard_blueprint,
)
from routes.edit_post import (
    edit_post_blueprint,
)
from routes.index import (
    index_blueprint,
)
from routes.login import (
    login_blueprint,
)
from routes.logout import (
    logout_blueprint,
)
from routes.password_reset import (
    password_reset_blueprint,
)
from routes.post import post_blueprint

from routes.privacy_policy import (
    privacy_policy_blueprint,
)

from routes.return_post_banner import (
    return_post_banner_blueprint,
)
from routes.search import (
    search_blueprint,
)
from routes.search_bar import (
    search_bar_blueprint,
)
from routes.set_language import (
    set_language_blueprint,
)
from routes.set_theme import (
    set_theme_blueprint,
)
from routes.signup import (
    sign_up_blueprint,
)
from routes.user import user_blueprint
from routes.verify_user import (
    verify_user_blueprint,
)
from settings import Settings
from utils.after_request import after_request_logger
from utils.before_request.browser_language import browser_language
from utils.context_processor.is_login import is_login
from utils.context_processor.is_registration import is_registration
from utils.context_processor.markdown import markdown_processor
from utils.context_processor.return_post_url_id import return_post_url_id
from utils.context_processor.return_post_url_slug import return_post_url_slug
from utils.context_processor.return_user_profile_picture import (
    return_user_profile_picture,
)
from utils.context_processor.translations import inject_translations
from utils.db_checker import (
    comments_table,
    db_folder,
    posts_table,
    users_table,
)
from utils.error_handlers.csrf_error_handler import (
    csrf_error_handler,
)
from utils.error_handlers.not_found_error_handler import (
    not_found_error_handler,
)
from utils.error_handlers.unauthorized_error_handler import (
    unauthorized_error_handler,
)
from utils.generate_url_id_from_post import get_slug_from_post_title
from utils.log import Log
from utils.terminal_ascii import terminal_ascii
from utils.time import current_time_stamp

start_time = current_time_stamp()


print(terminal_ascii())


Log.info("Starting...")


app = Flask(
    import_name=Settings.APP_NAME,
    root_path=Settings.APP_ROOT_PATH,
)


app.jinja_options["autoescape"] = True


app.secret_key = Settings.APP_SECRET_KEY
app.config["SESSION_PERMANENT"] = Settings.SESSION_PERMANENT


csrf = CSRFProtect(app)


app.context_processor(is_login)

app.context_processor(is_registration)
app.context_processor(return_user_profile_picture)
app.context_processor(return_post_url_id)
app.context_processor(return_post_url_slug)
app.context_processor(inject_translations)
app.context_processor(markdown_processor)
app.before_request(browser_language)
app.jinja_env.globals.update(get_slug_from_post_title=get_slug_from_post_title)

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


db_folder()
users_table()
posts_table()
comments_table()


@app.errorhandler(404)
def not_found(e):
    return not_found_error_handler(e)


@app.errorhandler(401)
def unauthorized(e):
    return unauthorized_error_handler(e)


@app.errorhandler(CSRFError)
def csrf_error(e):
    return csrf_error_handler(e)


@app.after_request
def after_request(response):
    response = after_request_logger(response)
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://code.jquery.com https://cdn.tailwindcss.com; "
        "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdn.tailwindcss.com; "
        "img-src 'self' data: https: blob:; "
        "font-src 'self' https://cdn.jsdelivr.net;"
    )
    return response


app.register_blueprint(post_blueprint)
app.register_blueprint(user_blueprint)
app.register_blueprint(index_blueprint)
app.register_blueprint(about_blueprint)
app.register_blueprint(login_blueprint)
app.register_blueprint(sign_up_blueprint)
app.register_blueprint(logout_blueprint)
app.register_blueprint(search_blueprint)
app.register_blueprint(category_blueprint)
app.register_blueprint(edit_post_blueprint)
app.register_blueprint(dashboard_blueprint)
app.register_blueprint(search_bar_blueprint)
app.register_blueprint(admin_panel_blueprint)
app.register_blueprint(create_post_blueprint)
app.register_blueprint(verify_user_blueprint)
app.register_blueprint(set_language_blueprint)
app.register_blueprint(set_theme_blueprint)
app.register_blueprint(privacy_policy_blueprint)
app.register_blueprint(password_reset_blueprint)
app.register_blueprint(change_username_blueprint)
app.register_blueprint(change_password_blueprint)
app.register_blueprint(change_language_blueprint)
app.register_blueprint(admin_panel_users_blueprint)
app.register_blueprint(admin_panel_posts_blueprint)
app.register_blueprint(account_settings_blueprint)
app.register_blueprint(return_post_banner_blueprint)
app.register_blueprint(admin_panel_comments_blueprint)
app.register_blueprint(change_profile_picture_blueprint)


if __name__ == "__main__":
    Log.info(f"Running on http://{Settings.APP_HOST}:{Settings.APP_PORT}")
    Log.success("App started")

    print(terminal_ascii())
    app.run(debug=Settings.DEBUG_MODE, host=Settings.APP_HOST, port=Settings.APP_PORT)

    end_time = current_time_stamp()
    run_time = end_time - start_time
    run_time = str(timedelta(seconds=run_time))

    Log.info(f"Run time: {run_time} ")
    Log.info("Shut down")
    Log.warning("App shut down")

    print(terminal_ascii())
