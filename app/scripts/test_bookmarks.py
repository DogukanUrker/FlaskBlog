"""
Test script for bookmark functionality
Run this script to test the bookmark feature
"""

import os
import sys

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import db, init_db
from models import User, Post, Bookmark
from app import create_app
from utils.log import Log

def test_bookmark_functionality():
    """Test the bookmark functionality"""
    try:
        app = create_app()
        with app.app_context():
            Log.info("Starting bookmark functionality test...")
            
            # Test 1: Check if bookmarks table exists
            Log.info("Test 1: Checking if bookmarks table exists...")
            try:
                # Try to query the bookmarks table
                Bookmark.query.first()
                Log.success("✓ Bookmarks table exists")
            except Exception as e:
                Log.error(f"✗ Bookmarks table does not exist: {e}")
                return False
            
            # Test 2: Check if we can create a bookmark
            Log.info("Test 2: Testing bookmark creation...")
            try:
                # Get a test user and post
                user = User.query.first()
                post = Post.query.first()
                
                if not user or not post:
                    Log.warning("No users or posts found in database for testing")
                    return True
                
                # Create a test bookmark
                bookmark = Bookmark(
                    user_id=user.user_id,
                    post_id=post.id
                )
                db.session.add(bookmark)
                db.session.commit()
                Log.success(f"✓ Bookmark created successfully for user {user.username} on post {post.title}")
                
                # Clean up test bookmark
                db.session.delete(bookmark)
                db.session.commit()
                Log.success("✓ Test bookmark cleaned up")
                
            except Exception as e:
                Log.error(f"✗ Error creating bookmark: {e}")
                db.session.rollback()
                return False
            
            Log.success("All bookmark functionality tests passed!")
            return True
            
    except Exception as e:
        Log.error(f"Error during bookmark testing: {e}")
        return False

if __name__ == "__main__":
    success = test_bookmark_functionality()
    if success:
        Log.success("Bookmark functionality is ready!")
    else:
        Log.error("Bookmark functionality test failed!")