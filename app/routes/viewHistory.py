import sqlite3
from datetime import datetime, timedelta

from flask import Blueprint, redirect, render_template, session, url_for
from settings import Settings
from utils.log import Log
from utils.time import currentTimeStamp

viewHistoryBlueprint = Blueprint("viewHistory", __name__)


@viewHistoryBlueprint.route("/history")
def viewHistory():
    """
    View user's browsing history.
    Only accessible to logged-in users.
    Shows the user's recently viewed posts in reverse chronological order.
    Only shows posts viewed within the last month.
    """
    # Check if user is logged in
    if "userName" not in session:
        return redirect(url_for("login.login", redirect="/history"))
    
    userName = session["userName"]
    
    # Calculate timestamp for one month ago
    oneMonthAgo = currentTimeStamp() - (30 * 24 * 60 * 60)  # 30 days in seconds
    
    try:
        # Connect to analytics database to get user history
        Log.database(f"Connecting to '{Settings.DB_ANALYTICS_ROOT}' database for user history")
        history_conn = sqlite3.connect(Settings.DB_ANALYTICS_ROOT)
        history_conn.set_trace_callback(Log.database)
        history_cursor = history_conn.cursor()
        
        # Get user's browsing history from the last month, ordered by timestamp descending
        history_cursor.execute(
            """
            SELECT postID, timeStamp FROM userHistory 
            WHERE userName = ? AND timeStamp > ? 
            ORDER BY timeStamp DESC
            """,
            (userName, oneMonthAgo)
        )
        history_records = history_cursor.fetchall()
        history_conn.close()
        
        # If no history, return empty page
        if not history_records:
            return render_template(
                "history.html",
                posts=[],
                appName=Settings.APP_NAME
            )
        
        # Extract post IDs from history records
        post_ids = [record[0] for record in history_records]
        timestamp_map = {record[0]: record[1] for record in history_records}
        
        # Connect to posts database to get post details
        Log.database(f"Connecting to '{Settings.DB_POSTS_ROOT}' database for post details")
        posts_conn = sqlite3.connect(Settings.DB_POSTS_ROOT)
        posts_conn.set_trace_callback(Log.database)
        posts_cursor = posts_conn.cursor()
        
        # Create placeholders for SQL query
        placeholders = ','.join(['?'] * len(post_ids))
        
        # Get post details
        posts_cursor.execute(
            f"""
            SELECT id, title, category, urlID, author, timeStamp, lastEditTimeStamp 
            FROM posts 
            WHERE id IN ({placeholders})
            """,
            post_ids
        )
        posts = posts_cursor.fetchall()
        posts_conn.close()
        
        # Create a list of post data with history timestamp
        post_data = []
        for post in posts:
            post_data.append({
                'id': post[0],
                'title': post[1],
                'category': post[2],
                'urlID': post[3],
                'author': post[4],
                'postTimeStamp': post[5],
                'lastEditTimeStamp': post[6],
                'viewTimeStamp': timestamp_map[post[0]]
            })
        
        # Sort posts by view timestamp in descending order
        post_data.sort(key=lambda x: x['viewTimeStamp'], reverse=True)
        
        return render_template(
            "history.html",
            posts=post_data,
            appName=Settings.APP_NAME
        )
        
    except Exception as e:
        Log.error(f"Error retrieving user history: {str(e)}")
        return render_template(
            "history.html",
            posts=[],
            appName=Settings.APP_NAME
        )