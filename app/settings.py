"""
This module contains all the general application settings.
"""

import os
import secrets
from pathlib import Path


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
        ANALYTICS (bool): Enable or disable analytics feature for posts.
        TAMGA_LOGGER (bool): Toggle custom logging feature.
        WERKZEUG_LOGGER (bool): Toggle werkzeug logging feature.
        LOG_TO_FILE (bool): Toggle logging to file feature.
        LOG_FOLDER_ROOT (str): Root path of the log folder.
        LOG_FILE_ROOT (str): Root path of the log file.
        BREAKER_TEXT (str): Separator text used in log files.
        APP_SECRET_KEY (str): Secret key for Flask sessions.
        SESSION_PERMANENT (bool): Toggle permanent sessions for the Flask application.
        DB_FOLDER_ROOT (str): Root path of the database folder.
        DB_USERS_ROOT (str): Root path of the users database.
        DB_POSTS_ROOT (str): Root path of the posts database.
        DB_COMMENTS_ROOT (str): Root path of the comments database.
        DB_ANALYTICS_ROOT (str): Root path of the analytics database.
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
        SHARE_ENABLED (bool): Toggle social sharing button on posts.
        SHARE_URL (str): Base URL for social sharing (default: X/Twitter).
        SHARE_ICON (str): Tabler icon class for sharing button.
    """

    # Application Configuration
    APP_NAME = "flaskBlog"
    APP_VERSION = "3.0.0dev"
    APP_ROOT_PATH = "."
    APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
    APP_PORT = int(os.getenv("APP_PORT", "1283"))
    DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"

    # Feature Toggles
    LOG_IN = True
    REGISTRATION = True
    ANALYTICS = True

    # Internationalization
    LANGUAGES = ["en", "zh"]

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
    LOG_FOLDER_ROOT = "log/"
    LOG_FILE_ROOT = LOG_FOLDER_ROOT + "log.log"
    BREAKER_TEXT = "\n"

    # Session Configuration
    # Load secret key from environment or generate and save once
    _secret_key_file = Path(".secret_key")
    if os.getenv("APP_SECRET_KEY"):
        APP_SECRET_KEY = os.getenv("APP_SECRET_KEY")
    elif _secret_key_file.exists():
        APP_SECRET_KEY = _secret_key_file.read_text().strip()
    else:
        APP_SECRET_KEY = secrets.token_urlsafe(32)
        _secret_key_file.write_text(APP_SECRET_KEY)
        _secret_key_file.chmod(0o600)

    SESSION_PERMANENT = True
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "False").lower() == "true"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour in seconds

    # Database Configuration
    DB_FOLDER_ROOT = os.getenv("DB_FOLDER_ROOT", "db/")
    DB_USERS_ROOT = DB_FOLDER_ROOT + "users.db"
    DB_POSTS_ROOT = DB_FOLDER_ROOT + "posts.db"
    DB_COMMENTS_ROOT = DB_FOLDER_ROOT + "comments.db"
    DB_ANALYTICS_ROOT = DB_FOLDER_ROOT + "analytics.db"

    # SMTP Mail Configuration
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_MAIL = os.getenv("SMTP_MAIL", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

    # Default Admin Account Configuration
    DEFAULT_ADMIN = True
    DEFAULT_ADMIN_USERNAME = "admin"
    DEFAULT_ADMIN_EMAIL = "admin@flaskblog.com"
    DEFAULT_ADMIN_PASSWORD = "admin"
    DEFAULT_ADMIN_POINT = 0
    DEFAULT_ADMIN_PROFILE_PICTURE = f"https://api.dicebear.com/7.x/identicon/svg?seed={DEFAULT_ADMIN_USERNAME}&radius=10"

    # reCAPTCHA Configuration
    RECAPTCHA = os.getenv("RECAPTCHA", "False").lower() == "true"
    RECAPTCHA_SITE_KEY = os.getenv("RECAPTCHA_SITE_KEY", "")
    RECAPTCHA_SECRET_KEY = os.getenv("RECAPTCHA_SECRET_KEY", "")
    RECAPTCHA_VERIFY_URL = "https://www.google.com/recaptcha/api/siteverify"

    # Upload Security Configuration
    MAX_UPLOAD_SIZE = int(os.getenv("MAX_UPLOAD_SIZE", "5242880"))  # 5MB default
    ALLOWED_UPLOAD_EXTENSIONS = set(
        os.getenv("ALLOWED_UPLOAD_EXTENSIONS", "jpg,jpeg,png,webp").split(",")
    )

    # Social Sharing Configuration
    SHARE_ENABLED = os.getenv("SHARE_ENABLED", "True").lower() == "true"
    SHARE_URL = os.getenv("SHARE_URL", "https://x.com/intent/tweet?text=")
    SHARE_ICON = os.getenv("SHARE_ICON", "ti-brand-x")  # Tabler icon class

    # Security Configuration
    RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "True").lower() == "true"
    MAX_LOGIN_ATTEMPTS = int(os.getenv("MAX_LOGIN_ATTEMPTS", "3"))
    LOCKOUT_DURATION = int(os.getenv("LOCKOUT_DURATION", "1800"))  # 30 minutes
