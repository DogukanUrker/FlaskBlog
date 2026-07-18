"""
This module contains all the general application settings.
"""

import os
import secrets

from dotenv import load_dotenv

load_dotenv()


def _bool(value):
    """Parse a string value to boolean."""
    return str(value).lower() in ("true", "1", "yes")


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
        LOG_ENABLE_BACKUP (bool): Toggle Tamga rotation backup (.bak) files.
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
    """

    # Application Configuration
    APP_NAME = os.environ.get("APP_NAME", "FlaskBlog")
    APP_VERSION = os.environ.get("APP_VERSION", "3.0.0dev")
    APP_ROOT_PATH = os.environ.get("APP_ROOT_PATH", ".")
    APP_HOST = os.environ.get("APP_HOST", "localhost")
    APP_PORT = int(os.environ.get("APP_PORT", 1283))
    DEBUG_MODE = _bool(os.environ.get("DEBUG_MODE", "False"))

    # Feature Toggles
    LOG_IN = _bool(os.environ.get("LOG_IN", "True"))
    REGISTRATION = _bool(os.environ.get("REGISTRATION", "True"))

    # Internationalization
    LANGUAGES = os.environ.get(
        "LANGUAGES", "en,tr,es,de,zh,fr,uk,ru,pt,ja,pl,hi"
    ).split(",")

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
    TAMGA_LOGGER = _bool(os.environ.get("TAMGA_LOGGER", "True"))
    WERKZEUG_LOGGER = _bool(os.environ.get("WERKZEUG_LOGGER", "False"))
    LOG_TO_FILE = _bool(os.environ.get("LOG_TO_FILE", "True"))
    LOG_TO_JSON = _bool(os.environ.get("LOG_TO_JSON", "True"))
    LOG_FOLDER_ROOT = os.environ.get("LOG_FOLDER_ROOT", "log/")
    LOG_FILE_ROOT = LOG_FOLDER_ROOT + "log.log"
    LOG_JSON_ROOT = LOG_FOLDER_ROOT + "log.json"
    LOG_ENABLE_BACKUP = _bool(os.environ.get("LOG_ENABLE_BACKUP", "True"))

    # Session Configuration
    APP_SECRET_KEY = os.environ.get("APP_SECRET_KEY", secrets.token_urlsafe(32))
    SESSION_PERMANENT = _bool(os.environ.get("SESSION_PERMANENT", "True"))

    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "SQLALCHEMY_DATABASE_URI", "sqlite:///flaskblog.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = _bool(
        os.environ.get("SQLALCHEMY_TRACK_MODIFICATIONS", "False")
    )

    # SMTP Mail Configuration
    SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))
    SMTP_MAIL = os.environ.get("SMTP_MAIL", "")
    SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")

    # Default Admin Account Configuration
    DEFAULT_ADMIN = _bool(os.environ.get("DEFAULT_ADMIN", "True"))
    DEFAULT_ADMIN_USERNAME = os.environ.get("DEFAULT_ADMIN_USERNAME", "admin")
    DEFAULT_ADMIN_EMAIL = os.environ.get("DEFAULT_ADMIN_EMAIL", "admin@flaskblog.com")
    DEFAULT_ADMIN_PASSWORD = os.environ.get("DEFAULT_ADMIN_PASSWORD")
    if DEFAULT_ADMIN and not DEFAULT_ADMIN_PASSWORD:
        raise RuntimeError(
            "DEFAULT_ADMIN_PASSWORD must be set when DEFAULT_ADMIN=True. "
            "Set a strong password via the environment variable."
        )
    DEFAULT_ADMIN_POINT = int(os.environ.get("DEFAULT_ADMIN_POINT", 0))
    DEFAULT_ADMIN_PROFILE_PICTURE = os.environ.get(
        "DEFAULT_ADMIN_PROFILE_PICTURE",
        f"https://api.dicebear.com/7.x/identicon/svg?seed={DEFAULT_ADMIN_USERNAME}&radius=10",
    )
