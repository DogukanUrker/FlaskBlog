"""
This module contains all the general application settings.
"""

import secrets


class Settings:
    """
    Configuration settings for the Flask Blog application.

    Attributes:
        APP_NAME (str): Name of the Flask application.
        APP_VERSION (str): Version of the Flask application.
        APP_ROOT_PATH (str): Path to the root of the application files.
        APP_HOST (str): Hostname or IP address for the Flask application.
        APP_PORT (int): Port number for the Flask application.
        DEBUG_MODE (bool): Toggle debug mode for the Flask application.
        LOG_IN (bool): Toggle user login feature.
        REGISTRATION (bool): Toggle user registration feature.
        LANGUAGES (list): Supported languages for the application.
        TAMGA_LOGGER (bool): Toggle custom logging feature.
        WERKZEUG_LOGGER (bool): Toggle werkzeug logging feature.
        LOG_TO_FILE (bool): Toggle logging to file feature.
        LOG_TO_JSON (bool): Toggle logging to JSON feature.
        LOG_FOLDER_ROOT (str): Root path of the log folder.
        LOG_FILE_ROOT (str): Root path of the log file.
        LOG_JSON_ROOT (str): Root path of the log JSON file.
        BREAKER_TEXT (str): Separator text used in log files.
        APP_SECRET_KEY (str): Secret key for Flask sessions.
        SESSION_PERMANENT (bool): Toggle permanent sessions for the Flask application.
        DB_FOLDER_ROOT (str): Root path of the database folder.
        DB_USERS_ROOT (str): Root path of the users database.
        DB_POSTS_ROOT (str): Root path of the posts database.
        DB_COMMENTS_ROOT (str): Root path of the comments database.

        SMTP_SERVER (str): SMTP server address.
        SMTP_PORT (int): SMTP server port.
        SMTP_MAIL (str): SMTP mail address.
        SMTP_PASSWORD (str): SMTP mail password.
        DEFAULT_ADMIN (bool): Toggle creation of default admin account.
        DEFAULT_ADMIN_USERNAME (str): Default admin username.
        DEFAULT_ADMIN_EMAIL (str): Default admin email address.
        DEFAULT_ADMIN_PASSWORD (str): Default admin password.
        DEFAULT_ADMIN_POINT (int): Default starting point score for admin.
        DEFAULT_ADMIN_PROFILE_PICTURE (str): Default admin profile picture URL.
        RECAPTCHA (bool): Toggle reCAPTCHA verification.
        RECAPTCHA_SITE_KEY (str): reCAPTCHA site key.
        RECAPTCHA_SECRET_KEY (str): reCAPTCHA secret key.
        RECAPTCHA_VERIFY_URL (str): reCAPTCHA verify URL.
    """

    # Application Configuration
    APP_NAME = "FlaskBlog"
    APP_VERSION = "3.0.0dev"
    APP_ROOT_PATH = "."
    APP_HOST = "localhost"
    APP_PORT = 1283
    DEBUG_MODE = True

    # Feature Toggles
    LOG_IN = True
    REGISTRATION = True

    # Internationalization
    LANGUAGES = ["en", "tr", "es", "de", "zh", "fr", "uk", "ru", "pt", "ja", "pl", "hi"]

    # Theme Configuration
    THEMES = [
        "light",
        "dark",
        "cupcake",
        "bumblebee",
        "emerald",
        "corporate",
        "synthwave",
        "retro",
        "cyberpunk",
        "valentine",
        "halloween",
        "garden",
        "forest",
        "aqua",
        "lofi",
        "pastel",
        "fantasy",
        "wireframe",
        "black",
        "luxury",
        "dracula",
        "cmyk",
        "autumn",
        "business",
        "acid",
        "lemonade",
        "night",
        "coffee",
        "winter",
        "dim",
        "nord",
        "sunset",
        "caramellatte",
        "abyss",
        "silk",
    ]

    # Logging Configuration
    TAMGA_LOGGER = True
    WERKZEUG_LOGGER = False
    LOG_TO_FILE = True
    LOG_TO_JSON = True
    LOG_FOLDER_ROOT = "log/"
    LOG_FILE_ROOT = LOG_FOLDER_ROOT + "log.log"
    LOG_JSON_ROOT = LOG_FOLDER_ROOT + "log.json"
    BREAKER_TEXT = "\n"

    # Session Configuration
    APP_SECRET_KEY = secrets.token_urlsafe(32)
    SESSION_PERMANENT = True

    # Database Configuration
    DB_FOLDER_ROOT = "db/"
    DB_USERS_ROOT = DB_FOLDER_ROOT + "users.db"
    DB_POSTS_ROOT = DB_FOLDER_ROOT + "posts.db"
    DB_COMMENTS_ROOT = DB_FOLDER_ROOT + "comments.db"

    # SMTP Mail Configuration
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    SMTP_MAIL = "flaskblogdogukanurker@gmail.com"
    SMTP_PASSWORD = "lsooxsmnsfnhnixy"  # replace this with your actual password

    # Default Admin Account Configuration
    DEFAULT_ADMIN = True
    DEFAULT_ADMIN_USERNAME = "admin"
    DEFAULT_ADMIN_EMAIL = "admin@flaskblog.com"
    DEFAULT_ADMIN_PASSWORD = "admin"
    DEFAULT_ADMIN_POINT = 0
    DEFAULT_ADMIN_PROFILE_PICTURE = f"https://api.dicebear.com/7.x/identicon/svg?seed={DEFAULT_ADMIN_USERNAME}&radius=10"

    # reCAPTCHA Configuration
    RECAPTCHA = False
    RECAPTCHA_SITE_KEY = ""
    RECAPTCHA_SECRET_KEY = ""
    RECAPTCHA_VERIFY_URL = "https://www.google.com/recaptcha/api/siteverify"
