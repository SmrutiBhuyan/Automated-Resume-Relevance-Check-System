#!/usr/bin/env python3
"""
Database migration script to add new columns to existing tables
Run this script to update the database schema with new fields
"""

import os
import sys
from sqlalchemy import text

# Add the app directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db

def migrate_database():
    """Add new columns to the database"""
    app = create_app()
    
    with app.app_context():
        try:
            # Check if the new columns already exist
            inspector = db.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('resume_evaluations')]
            
            migrations = []
            
            # Add ats_score column if it doesn't exist
            if 'ats_score' not in columns:
                migrations.append("ALTER TABLE resume_evaluations ADD COLUMN ats_score FLOAT")
            
            # Add strengths column if it doesn't exist
            if 'strengths' not in columns:
                migrations.append("ALTER TABLE resume_evaluations ADD COLUMN strengths JSON")
            
            # Add ats_feedback column if it doesn't exist
            if 'ats_feedback' not in columns:
                migrations.append("ALTER TABLE resume_evaluations ADD COLUMN ats_feedback JSON")
            
            # Execute migrations
            for migration in migrations:
                print(f"Executing: {migration}")
                db.session.execute(text(migration))
            
            if migrations:
                print(f"Successfully applied {len(migrations)} migrations")
            else:
                print("Database is already up to date")
                
        except Exception as e:
            print(f"Error during migration: {e}")
            return False
    
    return True

if __name__ == "__main__":
    print("Starting database migration...")
    success = migrate_database()
    if success:
        print("Migration completed successfully!")
    else:
        print("Migration failed!")
        sys.exit(1)
