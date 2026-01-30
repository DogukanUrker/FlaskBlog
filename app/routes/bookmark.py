"""
Bookmark routes for handling post bookmarks
"""

from flask import Blueprint, jsonify, session, request
from database import db
from models import Bookmark, Post, User
from utils.log import Log

bookmark_blueprint = Blueprint("bookmark", __name__)


@bookmark_blueprint.route("/api/bookmark/<int:post_id>", methods=["POST"])
def toggle_bookmark(post_id):
    """Toggle bookmark status for a post"""
    try:
        # Check if user is logged in
        if "username" not in session:
            return jsonify({"error": "User not logged in"}), 401
        
        # Get user ID
        user = User.query.filter_by(username=session["username"]).first()
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Check if post exists
        post = Post.query.get(post_id)
        if not post:
            return jsonify({"error": "Post not found"}), 404
        
        # Check if bookmark already exists
        existing_bookmark = Bookmark.query.filter_by(
            user_id=user.user_id, 
            post_id=post_id
        ).first()
        
        if existing_bookmark:
            # Remove bookmark
            db.session.delete(existing_bookmark)
            db.session.commit()
            Log.info(f"Bookmark removed for user {user.username} on post {post_id}")
            return jsonify({"bookmarked": False, "message": "Bookmark removed"}), 200
        else:
            # Add bookmark
            new_bookmark = Bookmark(
                user_id=user.user_id,
                post_id=post_id
            )
            db.session.add(new_bookmark)
            db.session.commit()
            Log.info(f"Bookmark added for user {user.username} on post {post_id}")
            return jsonify({"bookmarked": True, "message": "Bookmark added"}), 201
            
    except Exception as e:
        db.session.rollback()
        Log.error(f"Error toggling bookmark: {e}")
        return jsonify({"error": "Internal server error"}), 500


@bookmark_blueprint.route("/api/bookmark/status/<int:post_id>", methods=["GET"])
def get_bookmark_status(post_id):
    """Get bookmark status for a specific post"""
    try:
        # Check if user is logged in
        if "username" not in session:
            return jsonify({"bookmarked": False}), 200
        
        # Get user ID
        user = User.query.filter_by(username=session["username"]).first()
        if not user:
            return jsonify({"bookmarked": False}), 200
        
        # Check if bookmark exists
        bookmark = Bookmark.query.filter_by(
            user_id=user.user_id, 
            post_id=post_id
        ).first()
        
        return jsonify({"bookmarked": bookmark is not None}), 200
        
    except Exception as e:
        Log.error(f"Error getting bookmark status: {e}")
        return jsonify({"error": "Internal server error"}), 500


@bookmark_blueprint.route("/my-bookmarks")
def my_bookmarks():
    """Display user's bookmarked posts"""
    try:
        # Check if user is logged in
        if "username" not in session:
            return jsonify({"error": "User not logged in"}), 401
        
        # Get user ID
        user = User.query.filter_by(username=session["username"]).first()
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Get user's bookmarks with post details
        bookmarks = db.session.query(Bookmark, Post).join(
            Post, Bookmark.post_id == Post.id
        ).filter(
            Bookmark.user_id == user.user_id
        ).order_by(
            Bookmark.time_stamp.desc()
        ).all()
        
        # Format data for template
        bookmarked_posts = []
        for bookmark, post in bookmarks:
            bookmarked_posts.append({
                'id': post.id,
                'title': post.title,
                'tags': post.tags,
                'content': post.content,
                'banner': post.banner,
                'author': post.author,
                'views': post.views,
                'time_stamp': post.time_stamp,
                'last_edit_time_stamp': post.last_edit_time_stamp,
                'category': post.category,
                'url_id': post.url_id,
                'abstract': post.abstract,
                'bookmark_time': bookmark.time_stamp
            })
        
        return jsonify({
            "bookmarked_posts": bookmarked_posts,
            "username": user.username
        }), 200
        
    except Exception as e:
        Log.error(f"Error getting user bookmarks: {e}")
        return jsonify({"error": "Internal server error"}), 500