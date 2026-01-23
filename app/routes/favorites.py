import sqlite3
from flask import (
    Blueprint,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from settings import Settings
from utils.flashMessage import flashMessage
from utils.log import Log
from utils.time import currentTimeStamp

favoritesBlueprint = Blueprint("favorites", __name__)


@favoritesBlueprint.route("/article/<int:article_id>/favorite", methods=["POST"])
def favorite_article(article_id):
    if "userName" not in session:
        flashMessage("You need to be logged in to favorite articles", "error")
        return redirect(url_for("login.login"))

    Log.database(f"Connecting to '{Settings.DB_FAVORITES_ROOT}' database")
    connection = sqlite3.connect(Settings.DB_FAVORITES_ROOT)
    connection.set_trace_callback(Log.database)
    cursor = connection.cursor()

    try:
        cursor.execute(
            "SELECT id FROM favorites WHERE postID = ? AND userName = ?",
            (article_id, session["userName"]),
        )
        existing_favorite = cursor.fetchone()

        if existing_favorite:
            cursor.execute(
                "DELETE FROM favorites WHERE id = ?",
                (existing_favorite[0],),
            )
            connection.commit()
            connection.close()
            Log.success(f'User: "{session["userName"]}" unfavorited post: "{article_id}"')
            return jsonify({"status": "unfavorited"})
        else:
            cursor.execute(
                "INSERT INTO favorites(postID, userName, timeStamp) VALUES (?, ?, ?)",
                (article_id, session["userName"], currentTimeStamp()),
            )
            connection.commit()
            connection.close()
            Log.success(f'User: "{session["userName"]}" favorited post: "{article_id}"')
            return jsonify({"status": "favorited"})
    except Exception as e:
        Log.error(f"Error favoriting post: {str(e)}")
        connection.close()
        return jsonify({"status": "error"})


@favoritesBlueprint.route("/user/favorites")
def user_favorites():
    if "userName" not in session:
        flashMessage("You need to be logged in to view your favorites", "error")
        return redirect(url_for("login.login"))

    Log.database(f"Connecting to '{Settings.DB_FAVORITES_ROOT}' database")
    favorites_connection = sqlite3.connect(Settings.DB_FAVORITES_ROOT)
    favorites_connection.set_trace_callback(Log.database)
    favorites_cursor = favorites_connection.cursor()

    favorites_cursor.execute(
        "SELECT postID, timeStamp FROM favorites WHERE userName = ? ORDER BY timeStamp DESC",
        (session["userName"],),
    )
    favorites = favorites_cursor.fetchall()
    favorites_connection.close()

    favorite_posts = []
    Log.database(f"Connecting to '{Settings.DB_POSTS_ROOT}' database")
    posts_connection = sqlite3.connect(Settings.DB_POSTS_ROOT)
    posts_connection.set_trace_callback(Log.database)
    posts_cursor = posts_connection.cursor()

    for favorite in favorites:
        post_id, timestamp = favorite
        posts_cursor.execute(
            "SELECT id, title, content, timeStamp FROM posts WHERE id = ?",
            (post_id,),
        )
        post = posts_cursor.fetchone()
        if post:
            favorite_posts.append({
                "id": post[0],
                "title": post[1],
                "content": post[2],
                "timeStamp": post[3],
                "favorite_time": timestamp
            })

    posts_connection.close()

    return render_template("favorites.html", favorite_posts=favorite_posts)


@favoritesBlueprint.route("/article/<int:article_id>/is_favorited", methods=["GET"])
def is_favorited(article_id):
    if "userName" not in session:
        return jsonify({"is_favorited": False})

    Log.database(f"Connecting to '{Settings.DB_FAVORITES_ROOT}' database")
    connection = sqlite3.connect(Settings.DB_FAVORITES_ROOT)
    connection.set_trace_callback(Log.database)
    cursor = connection.cursor()

    cursor.execute(
        "SELECT id FROM favorites WHERE postID = ? AND userName = ?",
        (article_id, session["userName"]),
    )
    existing_favorite = cursor.fetchone()
    connection.close()

    return jsonify({"is_favorited": existing_favorite is not None})