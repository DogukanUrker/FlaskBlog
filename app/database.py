from flask_sqlalchemy import SQLAlchemy
from passlib.hash import sha512_crypt as encryption
from sqlalchemy import event
from sqlalchemy.engine import Engine
import sqlite3

from settings import Settings
from utils.log import Log
from utils.time import current_time_stamp

db = SQLAlchemy()


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA busy_timeout=30000;")
        cursor.close()


def init_db(app):
    app.config["SQLALCHEMY_DATABASE_URI"] = Settings.SQLALCHEMY_DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = (
        Settings.SQLALCHEMY_TRACK_MODIFICATIONS
    )
    if "sqlite" in Settings.SQLALCHEMY_DATABASE_URI:
        app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"connect_args": {"timeout": 30}}

    db.init_app(app)

    with app.app_context():
        # Set journal mode to WAL on the database once at startup
        if "sqlite" in Settings.SQLALCHEMY_DATABASE_URI:
            with db.engine.connect() as connection:
                connection.exec_driver_sql("PRAGMA journal_mode=WAL;")
        db.create_all()
        Log.success("Database tables created/verified")
        _create_default_admin()


def _create_default_admin():
    if not Settings.DEFAULT_ADMIN:
        return

    from models import User

    existing_admin = User.query.filter_by(
        username=Settings.DEFAULT_ADMIN_USERNAME
    ).first()

    if existing_admin:
        # Update the password hash if it doesn't match the current environment setting
        if not encryption.verify(
            Settings.DEFAULT_ADMIN_PASSWORD, existing_admin.password
        ):
            existing_admin.password = encryption.hash(Settings.DEFAULT_ADMIN_PASSWORD)
            db.session.commit()
            Log.success(
                "Admin password updated in database to match DEFAULT_ADMIN_PASSWORD"
            )
        else:
            Log.info(f'Admin: "{Settings.DEFAULT_ADMIN_USERNAME}" already exists')
        return

    admin = User(
        username=Settings.DEFAULT_ADMIN_USERNAME,
        email=Settings.DEFAULT_ADMIN_EMAIL,
        password=encryption.hash(Settings.DEFAULT_ADMIN_PASSWORD),
        profile_picture=Settings.DEFAULT_ADMIN_PROFILE_PICTURE,
        role="admin",
        points=Settings.DEFAULT_ADMIN_POINT,
        time_stamp=current_time_stamp(),
        is_verified="True",
    )

    db.session.add(admin)
    db.session.commit()

    Log.success(
        f'Admin: "{Settings.DEFAULT_ADMIN_USERNAME}" added to database as initial admin',
    )
