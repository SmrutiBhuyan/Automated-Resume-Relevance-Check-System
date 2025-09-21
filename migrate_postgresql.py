#!/usr/bin/env python3
"""
PostgreSQL Database Migration Script
Adds new columns to resume_evaluations table for enhanced features
"""

import os
import sys
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv

load_dotenv()

def get_database_url():
    """Get database URL from environment or config"""
    db_url = os.getenv('DB_URL')
    if not db_url:
        print("Error: DB_URL environment variable not set")
        print("Please set DB_URL in your .env file or environment")
        sys.exit(1)
    return db_url

def check_column_exists(engine, table_name, column_name):
    """Check if a column exists in the table"""
    try:
        inspector = inspect(engine)
        columns = [col['name'] for col in inspector.get_columns(table_name)]
        return column_name in columns
    except Exception as e:
        print(f"Error checking column {column_name}: {e}")
        return False

def migrate_database():
    """Run PostgreSQL database migration"""
    print("Starting PostgreSQL database migration...")
    
    try:
        # Get database URL
        db_url = get_database_url()
        print(f"Connecting to database: {db_url.split('@')[1] if '@' in db_url else 'local'}")
        
        # Create engine
        engine = create_engine(db_url)
        
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✓ Database connection successful")
        
        # Check if resume_evaluations table exists
        inspector = inspect(engine)
        if 'resume_evaluations' not in inspector.get_table_names():
            print("Error: resume_evaluations table does not exist")
            print("Please run the Flask app first to create the initial tables")
            sys.exit(1)
        
        # List of columns to add
        columns_to_add = [
            ('strengths', 'JSON'),
            ('ats_feedback', 'JSON')
        ]
        
        migrations_applied = 0
        
        # Add each column if it doesn't exist
        for column_name, column_type in columns_to_add:
            if not check_column_exists(engine, 'resume_evaluations', column_name):
                print(f"Adding column '{column_name}' to resume_evaluations...")
                
                with engine.connect() as conn:
                    # Use transaction for safety
                    trans = conn.begin()
                    try:
                        # Add column
                        alter_sql = f"ALTER TABLE resume_evaluations ADD COLUMN {column_name} {column_type}"
                        conn.execute(text(alter_sql))
                        trans.commit()
                        print(f"✓ Column '{column_name}' added successfully")
                        migrations_applied += 1
                    except Exception as e:
                        trans.rollback()
                        print(f"✗ Error adding column '{column_name}': {e}")
            else:
                print(f"Column '{column_name}' already exists, skipping...")
        
        # Update existing rows to have default values for new columns
        if migrations_applied > 0:
            print("Updating existing rows with default values...")
            with engine.connect() as conn:
                trans = conn.begin()
                try:
                    # Update existing rows to have default empty JSON arrays
                    update_sql = """
                    UPDATE resume_evaluations 
                    SET 
                        strengths = COALESCE(strengths, '[]'::json),
                        ats_feedback = COALESCE(ats_feedback, '[]'::json)
                    WHERE 
                        strengths IS NULL OR ats_feedback IS NULL
                    """
                    result = conn.execute(text(update_sql))
                    trans.commit()
                    print(f"✓ Updated {result.rowcount} existing rows")
                except Exception as e:
                    trans.rollback()
                    print(f"✗ Error updating existing rows: {e}")
        
        if migrations_applied > 0:
            print(f"\n🎉 Successfully applied {migrations_applied} migrations")
        else:
            print("\n✓ Database is already up to date")
        
        print("PostgreSQL migration completed successfully!")
        
    except SQLAlchemyError as e:
        print(f"Database error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    migrate_database()
