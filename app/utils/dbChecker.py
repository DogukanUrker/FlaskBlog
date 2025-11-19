"""
This file contains the database schemas for the app.

The database consists of three tables:
1. Users: stores information about the users, including their username, email, password, profile picture, role, points, creation date, creation time, and verification status.
2. Posts: stores information about the posts, including their title, tags, content, author, date, time, views, last edit date, and last edit time.
3. Comments: stores information about the comments, including the post they are associated with, the comment text, the user who wrote the comment, the date, and the time.

This file contains functions to create the tables if they do not already exist, and to ensure that they have the correct structure.
"""

import sqlite3
from os import mkdir
from os.path import exists

from passlib.hash import sha512_crypt as encryption
from settings import Settings
from utils.log import Log
from utils.time import currentTimeStamp


def dbFolder():
    """
    Checks if the database folder exists, and create it if it does not.

    Returns:
        None
    """

    if exists(Settings.DB_FOLDER_ROOT):
        Log.info(f'Database folder: "/{Settings.DB_FOLDER_ROOT}" found')
    else:
        Log.error(f'Database folder: "/{Settings.DB_FOLDER_ROOT}" not found')

        mkdir(Settings.DB_FOLDER_ROOT)

        Log.success(f'Database folder: "/{Settings.DB_FOLDER_ROOT}" created')


def usersTable():
    """
    Checks if the users' table exists in the database, and create it if it does not.
    Checks if default admin is true create an admin user with custom admin account settings if it is.

    Returns:
        None
    """

    if exists(Settings.DB_USERS_ROOT):
        Log.info(f'Users database: "{Settings.DB_USERS_ROOT}" found')
    else:
        Log.error(f'Users database: "{Settings.DB_USERS_ROOT}" not found')

        open(Settings.DB_USERS_ROOT, "x")

        Log.success(f'Users database: "{Settings.DB_USERS_ROOT}" created')
    Log.database(f"Connecting to '{Settings.DB_USERS_ROOT}' database")

    connection = sqlite3.connect(Settings.DB_USERS_ROOT)
    connection.set_trace_callback(Log.database)
    cursor = connection.cursor()
    try:
        cursor.execute("""select userID from users; """).fetchall()

        Log.info(f'Table: "users" found in "{Settings.DB_USERS_ROOT}"')

        connection.close()
    except Exception:
        Log.error(f'Table: "users" not found in "{Settings.DB_USERS_ROOT}"')

        usersTable = """
        create table if not exists Users(
            "userID"    integer not null unique,
            "userName"  text unique,
            "email" text unique,
            "password"  text,
            "profilePicture" text,
            "role"  text,
            "points"    integer,
            "timeStamp" integer,
            "isVerified"    text,
            primary key("userID" autoincrement)
        );"""

        cursor.execute(usersTable)

        if Settings.DEFAULT_ADMIN:
            password = encryption.hash(Settings.DEFAULT_ADMIN_PASSWORD)

            cursor.execute(
                """
                insert into Users(userName,email,password,profilePicture,role,points,timeStamp,isVerified) \
                values(?,?,?,?,?,?,?,?)
                """,
                (
                    Settings.DEFAULT_ADMIN_USERNAME,
                    Settings.DEFAULT_ADMIN_EMAIL,
                    password,
                    Settings.DEFAULT_ADMIN_PROFILE_PICTURE,
                    "admin",
                    Settings.DEFAULT_ADMIN_POINT,
                    currentTimeStamp(),
                    "True",
                ),
            )

            connection.commit()

            Log.success(
                f'Admin: "{Settings.DEFAULT_ADMIN_USERNAME}" added to database as initial admin',
            )

        connection.commit()

        connection.close()

        Log.success(f'Table: "users" created in "{Settings.DB_USERS_ROOT}"')


def postsTable():
    """
    Checks if the posts table exists in the database, and creates it if it does not.

    Returns:
        None
    """

    if exists(Settings.DB_POSTS_ROOT):
        Log.info(f'Posts database: "{Settings.DB_POSTS_ROOT}" found')
    else:
        Log.error(f'Posts database: "{Settings.DB_POSTS_ROOT}" not found')

        open(Settings.DB_POSTS_ROOT, "x")

        Log.success(f'Posts database: "{Settings.DB_POSTS_ROOT}" created')
    Log.database(f"Connecting to '{Settings.DB_POSTS_ROOT}' database")

    connection = sqlite3.connect(Settings.DB_POSTS_ROOT)
    connection.set_trace_callback(Log.database)
    cursor = connection.cursor()
    try:
        cursor.execute("""select id from posts; """).fetchall()

        Log.info(f'Table: "posts" found in "{Settings.DB_POSTS_ROOT}"')

        connection.close()
    except Exception:
        Log.error(f'Table: "posts" not found in "{Settings.DB_POSTS_ROOT}"')

        postsTable = """
        CREATE TABLE "posts" (
            "id"    integer not null unique,
            "title" text not null,
            "tags"  text not null,
            "content"   text not null,
            "banner"    BLOB not null,
            "author"    text not null,
            "views" integer,
            "timeStamp" integer,
            "lastEditTimeStamp" integer,
            "category"  text not null,
            "urlID" TEXT NOT NULL,
            "abstract" text not null default "",
            primary key("id" autoincrement)
        );"""

        cursor.execute(postsTable)

        connection.commit()

        connection.close()

        Log.success(f'Table: "posts" created in "{Settings.DB_POSTS_ROOT}"')


def commentsTable():
    """
    Checks if the comments table exists in the database, and creates it if it does not.

    Returns:
        None
    """

    if exists(Settings.DB_COMMENTS_ROOT):
        Log.info(f'Comments database: "{Settings.DB_COMMENTS_ROOT}" found')
    else:
        Log.error(f'Comments database: "{Settings.DB_COMMENTS_ROOT}" not found')

        open(Settings.DB_COMMENTS_ROOT, "x")

        Log.success(f'Comments database: "{Settings.DB_COMMENTS_ROOT}" created')
    Log.database(f"Connecting to '{Settings.DB_COMMENTS_ROOT}' database")

    connection = sqlite3.connect(Settings.DB_COMMENTS_ROOT)
    connection.set_trace_callback(Log.database)
    cursor = connection.cursor()
    try:
        cursor.execute("""select id from comments; """).fetchall()

        Log.info(f'Table: "comments" found in "{Settings.DB_COMMENTS_ROOT}"')

        connection.close()
    except Exception:
        Log.error(f'Table: "comments" not found in "{Settings.DB_COMMENTS_ROOT}"')

        commentsTable = """
        create table if not exists comments(
            "id"    integer not null,
            "post"  integer,
            "comment"   text,
            "user"  text,
            "timeStamp" integer,
            primary key("id" autoincrement)
        );"""

        cursor.execute(commentsTable)

        connection.commit()

        connection.close()

        Log.success(f'Table: "comments" created in "{Settings.DB_COMMENTS_ROOT}"')


def analyticsTable():
    """
    Checks if the analytics table exists in the database, and creates it if it does not.

    Returns:
        None
    """

    if exists(Settings.DB_ANALYTICS_ROOT):
        Log.info(f'Analytics database: "{Settings.DB_ANALYTICS_ROOT}" found')
    else:
        Log.error(f'Analytics database: "{Settings.DB_ANALYTICS_ROOT}" not found')

        open(Settings.DB_ANALYTICS_ROOT, "x")

        Log.success(f'Analytics database: "{Settings.DB_ANALYTICS_ROOT}" created')
    Log.database(f"Connecting to '{Settings.DB_ANALYTICS_ROOT}' database")

    connection = sqlite3.connect(Settings.DB_ANALYTICS_ROOT)
    connection.set_trace_callback(Log.database)
    cursor = connection.cursor()
    try:
        cursor.execute("""select id from postsAnalytics; """).fetchall()

        Log.info(f'Table: "postsAnalytics" found in "{Settings.DB_ANALYTICS_ROOT}"')

        connection.close()
    except Exception:
        Log.error(
            f'Table: "postsAnalytics" not found in "{Settings.DB_ANALYTICS_ROOT}"'
        )

        analyticsTable = """
        create table if not exists postsAnalytics(
            "id"    integer not null,
            "postID"  integer,
            "visitorUserName"  text,
            "country" text,
            "os" text,
            "continent" text,
            "timeSpendDuration" int default 0,
            "timeStamp" integer,
            primary key("id" autoincrement)
        );"""

        cursor.execute(analyticsTable)

        connection.commit()

        connection.close()

        Log.success(
            f'Table: "postsAnalytics" created in "{Settings.DB_ANALYTICS_ROOT}"'
        )


def securityAuditLogTable():
    """
    Checks if the security audit log table exists in the database, and creates it if it does not.

    Returns:
        None
    """

    Log.database(f"Connecting to '{Settings.DB_USERS_ROOT}' database")

    connection = sqlite3.connect(Settings.DB_USERS_ROOT)
    connection.set_trace_callback(Log.database)
    cursor = connection.cursor()
    try:
        cursor.execute("""select id from security_audit_log; """).fetchall()

        Log.info(f'Table: "security_audit_log" found in "{Settings.DB_USERS_ROOT}"')

        connection.close()
    except Exception:
        Log.error(
            f'Table: "security_audit_log" not found in "{Settings.DB_USERS_ROOT}"'
        )

        securityAuditLogTable = """
        create table if not exists security_audit_log(
            "id"    integer not null,
            "event_type"  text not null,
            "userName"  text,
            "ip_address" text,
            "user_agent" text,
            "path" text,
            "method" text,
            "status_code" integer,
            "details" text,
            "timeStamp" integer,
            primary key("id" autoincrement)
        );"""

        cursor.execute(securityAuditLogTable)

        connection.commit()

        connection.close()

        Log.success(
            f'Table: "security_audit_log" created in "{Settings.DB_USERS_ROOT}"'
        )


def twoFactorAuthFields():
    """
    Checks if the 2FA fields exist in the Users table, and adds them if they do not.

    Fields added:
    - twofa_secret: TOTP secret key for generating 2FA codes
    - twofa_enabled: Boolean flag indicating if 2FA is enabled for the user
    - backup_codes: JSON string of backup recovery codes

    Returns:
        None
    """

    Log.database(f"Connecting to '{Settings.DB_USERS_ROOT}' database")

    connection = sqlite3.connect(Settings.DB_USERS_ROOT)
    connection.set_trace_callback(Log.database)
    cursor = connection.cursor()

    try:
        # Check if twofa_secret column exists
        cursor.execute("PRAGMA table_info(Users)")
        columns = [column[1] for column in cursor.fetchall()]

        if "twofa_secret" not in columns:
            Log.error('Column: "twofa_secret" not found in Users table')
            cursor.execute("ALTER TABLE Users ADD COLUMN twofa_secret TEXT DEFAULT NULL")
            connection.commit()
            Log.success('Column: "twofa_secret" added to Users table')
        else:
            Log.info('Column: "twofa_secret" found in Users table')

        if "twofa_enabled" not in columns:
            Log.error('Column: "twofa_enabled" not found in Users table')
            cursor.execute("ALTER TABLE Users ADD COLUMN twofa_enabled TEXT DEFAULT 'False'")
            connection.commit()
            Log.success('Column: "twofa_enabled" added to Users table')
        else:
            Log.info('Column: "twofa_enabled" found in Users table')

        if "backup_codes" not in columns:
            Log.error('Column: "backup_codes" not found in Users table')
            cursor.execute("ALTER TABLE Users ADD COLUMN backup_codes TEXT DEFAULT NULL")
            connection.commit()
            Log.success('Column: "backup_codes" added to Users table')
        else:
            Log.info('Column: "backup_codes" found in Users table')

    finally:
        connection.close()


def siteSettingsTable():
    """
    Checks if the site_settings table exists in the users database, and creates it if it does not.
    This table stores global site configuration like logo path.

    Returns:
        None
    """
    Log.database(f"Connecting to '{Settings.DB_USERS_ROOT}' database for site settings")

    connection = sqlite3.connect(Settings.DB_USERS_ROOT)
    connection.set_trace_callback(Log.database)
    cursor = connection.cursor()

    try:
        cursor.execute("SELECT setting_key FROM site_settings LIMIT 1;").fetchall()
        Log.info('Table: "site_settings" found in users database')
    except Exception:
        Log.error('Table: "site_settings" not found in users database')

        siteSettingsTableSQL = """
        CREATE TABLE IF NOT EXISTS site_settings(
            "setting_id"    INTEGER NOT NULL UNIQUE,
            "setting_key"   TEXT UNIQUE NOT NULL,
            "setting_value" TEXT,
            "updated_at"    INTEGER,
            PRIMARY KEY("setting_id" AUTOINCREMENT)
        );"""

        cursor.execute(siteSettingsTableSQL)

        # Insert default logo path
        cursor.execute(
            """
            INSERT INTO site_settings(setting_key, setting_value, updated_at)
            VALUES(?, ?, ?)
            """,
            ("site_logo", "/static/uploads/site_logo.ico", currentTimeStamp())
        )

        connection.commit()
        Log.success('Table: "site_settings" created and default logo set')
    finally:
        connection.close()


def addBannerColumn():
    """
    Adds banner column to Users table if it doesn't exist.
    This function handles migration for existing databases.

    Returns:
        None
    """
    Log.database(f"Connecting to '{Settings.DB_USERS_ROOT}' database to check for banner column")

    connection = sqlite3.connect(Settings.DB_USERS_ROOT)
    connection.set_trace_callback(Log.database)
    cursor = connection.cursor()

    try:
        # Check if banner column exists
        cursor.execute("PRAGMA table_info(Users);")
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]

        if "banner" not in column_names:
            Log.info('Column "banner" not found in Users table, adding it...')
            cursor.execute("ALTER TABLE Users ADD COLUMN banner TEXT DEFAULT NULL;")
            connection.commit()
            Log.success('Column "banner" added to Users table')
        else:
            Log.info('Column "banner" already exists in Users table')
    finally:
        connection.close()


def userImagesTable():
    """
    Checks if the user_images table exists in the database, and creates it if it does not.
    This table stores user-uploaded images for their personal galleries.

    Returns:
        None
    """
    Log.database(f"Connecting to '{Settings.DB_USERS_ROOT}' database to check user_images table")

    connection = sqlite3.connect(Settings.DB_USERS_ROOT)
    connection.set_trace_callback(Log.database)
    cursor = connection.cursor()

    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user_images'")

        if cursor.fetchone():
            Log.info('Table: "user_images" found in users database')
        else:
            Log.error('Table: "user_images" not found in users database')

            userImagesTableSQL = """
            CREATE TABLE IF NOT EXISTS user_images(
                "image_id"      INTEGER NOT NULL UNIQUE,
                "userName"      TEXT NOT NULL,
                "title"         TEXT,
                "description"   TEXT,
                "file_path"     TEXT NOT NULL,
                "timeStamp"     INTEGER NOT NULL,
                PRIMARY KEY("image_id" AUTOINCREMENT)
            );"""

            cursor.execute(userImagesTableSQL)
            connection.commit()
            Log.success('Table: "user_images" created in users database')
    except Exception as e:
        Log.error(f'Error checking/creating user_images table: {e}')
    finally:
        connection.close()
