"""
My Bookmarks page route
"""

from flask import Blueprint, render_template, session, redirect, url_for
from database import db
from models import Bookmark, Post, User
from utils.log import Log
from utils.get_profile_picture import get_profile_picture

my_bookmarks_blueprint = Blueprint("my_bookmarks", __name__)


@my_bookmarks_blueprint.route("/my-bookmarks")
def my_bookmarks():
    """Display user's bookmarked posts page"""
    try:
        # Check if user is logged in
        if "username" not in session:
            return redirect("/login/redirect=&my-bookmarks")
        
        # Get user ID
        user = User.query.filter_by(username=session["username"]).first()
        if not user:
            return redirect("/login/redirect=&my-bookmarks")
        
        # Get user's bookmarks with post details
        bookmarks = db.session.query(Bookmark, Post).join(
            Post, Bookmark.post_id == Post.id
        ).filter(
            Bookmark.user_id == user.user_id
        ).order_by(
            Bookmark.time_stamp.desc()
        ).all()
        
        # Format data for template (match the expected tuple format)
        bookmarked_posts = []
        for bookmark, post in bookmarks:
            bookmarked_posts.append([
                post.id,
                post.title,
                post.tags,
                post.content,
                post.banner,
                post.author,
                post.views,
                post.time_stamp,
                post.last_edit_time_stamp,
                post.category,
                post.url_id,
                post.abstract,
            ])
        
        return render_template(
            "my_bookmarks.html",
            bookmarked_posts=bookmarked_posts,
            username=user.username,
            get_profile_picture=get_profile_picture
        )
        
    except Exception as e:
        Log.error(f"Error loading my bookmarks page: {e}")
        return redirect(url_for("index.index"))