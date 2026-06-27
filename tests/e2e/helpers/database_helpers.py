"""
Database helper functions for E2E tests.
"""

import sqlite3
import time
import uuid

from passlib.hash import sha512_crypt as encryption


def get_db_connection(db_path: str):
    """Create a database connection."""
    return sqlite3.connect(db_path)


def reset_database(db_path: str):
    """
    Reset database to known state.
    Removes all test users (keeps admin), clears posts and comments created by test users.
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    try:
        # Delete all users except the default admin
        cursor.execute("DELETE FROM users WHERE LOWER(username) != 'admin'")

        # Reset admin points to 0
        cursor.execute("UPDATE users SET points = 0 WHERE LOWER(username) = 'admin'")

        # Delete test posts (posts by users other than admin)
        cursor.execute("DELETE FROM posts WHERE LOWER(author) != 'admin'")

        # Delete test comments (comments by users other than admin)
        cursor.execute("DELETE FROM comments WHERE LOWER(username) != 'admin'")

        conn.commit()
    finally:
        conn.close()


def create_test_user(
    db_path: str,
    username: str,
    email: str,
    password: str,
    role: str = "user",
    is_verified: str = "True",
    points: int = 0,
) -> int:
    """
    Create a test user in the database.
    Returns the user_id of the created user.
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    try:
        hashed_password = encryption.hash(password)
        profile_picture = (
            f"https://api.dicebear.com/7.x/identicon/svg?seed={username}&radius=10"
        )

        cursor.execute(
            """
            INSERT INTO users (username, email, password, profile_picture, role, points, is_verified)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                username,
                email,
                hashed_password,
                profile_picture,
                role,
                points,
                is_verified,
            ),
        )

        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def get_user_by_username(db_path: str, username: str) -> dict | None:
    """
    Get user data by username.
    Returns a dictionary with user fields or None if not found.
    """
    conn = get_db_connection(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT * FROM users WHERE LOWER(username) = LOWER(?)",
            (username,),
        )
        row = cursor.fetchone()

        if row:
            return dict(row)
        return None
    finally:
        conn.close()


def get_user_by_email(db_path: str, email: str) -> dict | None:
    """
    Get user data by email.
    Returns a dictionary with user fields or None if not found.
    """
    conn = get_db_connection(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT * FROM users WHERE LOWER(email) = LOWER(?)",
            (email,),
        )
        row = cursor.fetchone()

        if row:
            return dict(row)
        return None
    finally:
        conn.close()


def get_user_points(db_path: str, username: str) -> int | None:
    """
    Get user points by username.
    Returns the points value or None if user not found.
    """
    user = get_user_by_username(db_path, username)
    if user:
        return user.get("points", 0)
    return None


def create_test_post(
    db_path: str,
    title: str,
    content: str,
    abstract: str,
    author: str = "admin",
    tags: str = "test,post",
    category: str = "Technology",
    url_id: str | None = None,
    banner: bytes | None = None,
    views: int = 0,
) -> dict:
    """
    Create a test post in the database.
    Returns a dictionary with id, url_id, and title.
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    try:
        now = int(time.time())
        resolved_url_id = url_id or f"testpost_{uuid.uuid4().hex[:12]}"
        resolved_banner = banner if banner is not None else b"test-banner-image"

        cursor.execute(
            """
            INSERT INTO posts (
                title,
                tags,
                content,
                banner,
                author,
                views,
                time_stamp,
                last_edit_time_stamp,
                category,
                url_id,
                abstract
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                title,
                tags,
                content,
                resolved_banner,
                author,
                views,
                now,
                now,
                category,
                resolved_url_id,
                abstract,
            ),
        )
        conn.commit()

        return {
            "id": cursor.lastrowid,
            "url_id": resolved_url_id,
            "title": title,
        }
    finally:
        conn.close()


def get_post_by_title(db_path: str, title: str) -> dict | None:
    """
    Get post data by exact title match.
    Returns a dictionary with post fields or None if not found.
    """
    conn = get_db_connection(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM posts WHERE title = ?", (title,))
        row = cursor.fetchone()

        if row:
            return dict(row)
        return None
    finally:
        conn.close()


def get_post_by_url_id(db_path: str, url_id: str) -> dict | None:
    """
    Get post data by URL ID.
    Returns a dictionary with post fields or None if not found.
    """
    conn = get_db_connection(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM posts WHERE url_id = ?", (url_id,))
        row = cursor.fetchone()

        if row:
            return dict(row)
        return None
    finally:
        conn.close()


def get_post_views(db_path: str, url_id: str) -> int | None:
    """
    Get post view count by URL ID.
    Returns the views value or None if post not found.
    """
    post = get_post_by_url_id(db_path, url_id)
    if post:
        return post.get("views", 0)
    return None


def get_comment_for_post(db_path: str, post_id: int, comment_text: str) -> dict | None:
    """
    Get a specific comment by post ID and exact comment text.
    Returns a dictionary with comment fields or None if not found.
    """
    conn = get_db_connection(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            SELECT * FROM comments
            WHERE post_id = ? AND comment = ?
            ORDER BY time_stamp DESC
            LIMIT 1
            """,
            (post_id, comment_text),
        )
        row = cursor.fetchone()

        if row:
            return dict(row)
        return None
    finally:
        conn.close()


def create_test_comment(
    db_path: str,
    post_id: int,
    comment: str,
    username: str = "admin",
) -> int:
    """
    Create a test comment for a post.
    Returns the created comment ID.
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO comments (post_id, comment, username, time_stamp)
            VALUES (?, ?, ?, ?)
            """,
            (post_id, comment, username, int(time.time())),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def get_comment_by_id(db_path: str, comment_id: int) -> dict | None:
    """
    Get comment data by comment ID.
    Returns a dictionary with comment fields or None if not found.
    """
    conn = get_db_connection(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM comments WHERE id = ?", (comment_id,))
        row = cursor.fetchone()

        if row:
            return dict(row)
        return None
    finally:
        conn.close()
