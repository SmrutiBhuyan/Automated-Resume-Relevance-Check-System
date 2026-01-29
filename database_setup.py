"""
Database Setup Script
Creates database tables and initial data
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def create_database():
    """Create PostgreSQL database if it doesn't exist"""
    # Database configuration
    db_name = "resume_evaluation"
    db_user = os.getenv('DB_USER', 'postgres')
    db_password = os.getenv('DB_PASSWORD', 'password')
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '5432')
    
    try:
        # Connect to PostgreSQL server
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
        exists = cursor.fetchone()
        
        if not exists:
            # Create database
            cursor.execute(f'CREATE DATABASE "{db_name}"')
            print(f"✅ Database '{db_name}' created successfully")
        else:
            print(f"✅ Database '{db_name}' already exists")
        
        cursor.close()
        conn.close()
        
    except psycopg2.Error as e:
        print(f"❌ Error creating database: {e}")
        sys.exit(1)

def create_tables():
    """Create database tables"""
    from app import app, db
    
    with app.app_context():
        try:
            # Create all tables
            db.create_all()
            print("✅ Database tables created successfully")
            
            # Create indexes for better performance
            from sqlalchemy import text
            
            # Index on evaluations for faster queries
            db.engine.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_evaluations_job_id 
                ON evaluations(job_id)
            """))
            
            db.engine.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_evaluations_resume_id 
                ON evaluations(resume_id)
            """))
            
            db.engine.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_evaluations_relevance_score 
                ON evaluations(relevance_score)
            """))
            
            db.engine.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_evaluations_verdict 
                ON evaluations(verdict)
            """))
            
            # Index on resumes
            db.engine.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_resumes_student_email 
                ON resumes(student_email)
            """))
            
            db.engine.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_resumes_is_processed 
                ON resumes(is_processed)
            """))
            
            # Index on jobs
            db.engine.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_jobs_is_active 
                ON jobs(is_active)
            """))
            
            print("✅ Database indexes created successfully")
            
        except Exception as e:
            print(f"❌ Error creating tables: {e}")
            sys.exit(1)

def main():
    """Main setup function"""
    print("🚀 Setting up Resume Evaluation Database...")
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Create database
    create_database()
    
    # Create tables
    create_tables()
    
    print("✅ Database setup completed successfully!")
    print("\nNext steps:")
    print("1. Start Redis server: redis-server")
    print("2. Start Celery worker: celery -A tasks worker --loglevel=info")
    print("3. Start Flask app: python app.py")
    print("4. Start Streamlit dashboard: streamlit run streamlit_app.py")

if __name__ == "__main__":
    main()
