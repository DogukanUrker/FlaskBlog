"""
This module contains the routes for article favorite functionality.
"""

import sqlite3

from flask import Blueprint, jsonify, request, session
from settings import Settings
from utils.log import Log
from utils.time import currentTimeStamp

favoriteBlueprint = Blueprint("favorite", __name__)


@favoriteBlueprint.route("/article/<int:article_id>/favorite", methods=["POST"])
def toggle_favorite(article_id):
    """
    Toggle favorite status for an article.
    
    :param article_id: The ID of the article to favorite/unfavorite
    :type article_id: int
    :return: JSON response with status and message
    :rtype: flask.Response
    """
    if "userName" not in session:
        return jsonify({"status": "error", "message": "User not logged in"}), 401
    
    user_name = session["userName"]
    
    try:
        # Get user ID
        Log.database(f"Connecting to '{Settings.DB_USERS_ROOT}' database")
        connection = sqlite3.connect(Settings.DB_USERS_ROOT)
        connection.set_trace_callback(Log.database)
        cursor = connection.cursor()
        
        cursor.execute("SELECT userID FROM users WHERE userName = ?", (user_name,))
        user_result = cursor.fetchone()
        
        if not user_result:
            return jsonify({"status": "error", "message": "User not found"}), 404
        
        user_id = user_result[0]
        
        # Check if post exists
        Log.database(f"Connecting to '{Settings.DB_POSTS_ROOT}' database")
        connection_posts = sqlite3.connect(Settings.DB_POSTS_ROOT)
        connection_posts.set_trace_callback(Log.database)
        cursor_posts = connection_posts.cursor()
        
        cursor_posts.execute("SELECT id FROM posts WHERE id = ?", (article_id,))
        post_result = cursor_posts.fetchone()
        connection_posts.close()
        
        if not post_result:
            return jsonify({"status": "error", "message": "Article not found"}), 404
        
        # Check if favorite already exists
        cursor.execute(
            "SELECT id FROM favorites WHERE userID = ? AND postID = ?",
            (user_id, article_id)
        )
        existing_favorite = cursor.fetchone()
        
        if existing_favorite:
            # Remove favorite
            cursor.execute(
                "DELETE FROM favorites WHERE userID = ? AND postID = ?",
                (user_id, article_id)
            )
            connection.commit()
            connection.close()
            
            Log.success(f'User: "{user_name}" removed favorite from post: "{article_id}"')
            return jsonify({
                "status": "success", 
                "message": "Article removed from favorites",
                "favorited": False
            })
        else:
            # Add favorite
            cursor.execute(
                "INSERT INTO favorites (userID, postID, timeStamp) VALUES (?, ?, ?)",
                (user_id, article_id, currentTimeStamp())
            )
            connection.commit()
            connection.close()
            
            Log.success(f'User: "{user_name}" favorited post: "{article_id}"')
            return jsonify({
                "status": "success", 
                "message": "Article added to favorites",
                "favorited": True
            })
            
    except Exception as e:
        Log.error(f"Error toggling favorite: {str(e)}")
        return jsonify({"status": "error", "message": "Internal server error"}), 500


@favoriteBlueprint.route("/article/<int:article_id>/favorite/status", methods=["GET"])
def favorite_status(article_id):
    """
    Check if an article is favorited by the current user.
    
    :param article_id: The ID of the article to check
    :type article_id: int
    :return: JSON response with favorite status
    :rtype: flask.Response
    """
    if "userName" not in session:
        return jsonify({"favorited": False})
    
    user_name = session["userName"]
    
    try:
        Log.database(f"Connecting to '{Settings.DB_USERS_ROOT}' database")
        connection = sqlite3.connect(Settings.DB_USERS_ROOT)
        connection.set_trace_callback(Log.database)
        cursor = connection.cursor()
        
        # Get user ID
        cursor.execute("SELECT userID FROM users WHERE userName = ?", (user_name,))
        user_result = cursor.fetchone()
        
        if not user_result:
            return jsonify({"favorited": False})
        
        user_id = user_result[0]
        
        # Check if favorite exists
        cursor.execute(
            "SELECT id FROM favorites WHERE userID = ? AND postID = ?",
            (user_id, article_id)
        )
        existing_favorite = cursor.fetchone()
        connection.close()
        
        return jsonify({"favorited": existing_favorite is not None})
        
    except Exception as e:
        Log.error(f"Error checking favorite status: {str(e)}")
        return jsonify({"favorited": False})


@favoriteBlueprint.route("/user/favorites")
def user_favorites():
    """
    Display the current user's favorite articles.
    
    :return: Rendered template with favorite articles
    :rtype: flask.Response
    """
    if "userName" not in session:
        from flask import redirect, url_for
        return redirect(url_for("login.login"))
    
    user_name = session["userName"]
    
    try:
        Log.database(f"Connecting to '{Settings.DB_USERS_ROOT}' database")
        connection = sqlite3.connect(Settings.DB_USERS_ROOT)
        connection.set_trace_callback(Log.database)
        cursor = connection.cursor()
        
        # Get user ID
        cursor.execute("SELECT userID FROM users WHERE userName = ?", (user_name,))
        user_result = cursor.fetchone()
        
        if not user_result:
            from flask import render_template
            return render_template("notFound.html")
        
        user_id = user_result[0]
        
        # Get favorite posts
        cursor.execute("""
            SELECT p.id, p.title, p.abstract, p.author, p.timeStamp, f.timeStamp as favoriteTime
            FROM favorites f
            JOIN posts p ON f.postID = p.id
            WHERE f.userID = ?
            ORDER BY f.timeStamp DESC
        """, (user_id,))
        
        favorites = cursor.fetchall()
        connection.close()
        
        from flask import render_template
        return render_template(
            "favorites.html",
            favorites=favorites,
            userName=user_name
        )
        
    except Exception as e:
        Log.error(f"Error loading user favorites: {str(e)}")
        from flask import render_template
        return render_template("notFound.html")