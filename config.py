import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    
    # Database configuration - use SQLite as fallback
    DB_URL = os.environ.get('DB_URL')
    if DB_URL:
        SQLALCHEMY_DATABASE_URI = DB_URL
    else:
        # Use SQLite as fallback
        SQLALCHEMY_DATABASE_URI = 'sqlite:///instance/database.db'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # API Keys
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    HUGGINGFACE_API_KEY = os.environ.get('HUGGINGFACE_API_KEY')
    HUGGINGFACE_TOKEN = os.environ.get('HUGGINGFACE_TOKEN')  # Alternative name
    
    # LangSmith Configuration
    LANGSMITH_API_KEY = os.environ.get('LANGSMITH_API_KEY')
    LANGSMITH_PROJECT = os.environ.get('LANGSMITH_PROJECT', 'resume-evaluation-system')

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}