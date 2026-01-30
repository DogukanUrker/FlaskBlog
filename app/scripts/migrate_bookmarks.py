"""
Database migration script for adding bookmarks table
Run this script to create the bookmarks table in the database
"""

import os
import sys

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import db, init_db
from models import Bookmark
from app import create_app
from utils.log import Log

def migrate_bookmarks():
    """Create the bookmarks table"""
    try:
        app = create_app()
        with app.app_context():
            # Create all tables (this will only create the new bookmarks table)
            db.create_all()
            Log.success("Bookmarks table created successfully!")
            return True
    except Exception as e:
        Log.error(f"Error creating bookmarks table: {e}")
        return False

if __name__ == "__main__":
    migrate_bookmarks()