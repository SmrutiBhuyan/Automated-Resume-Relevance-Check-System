"""
Test script for Resume Evaluation System
Tests basic functionality without requiring full setup
"""

import os
import sys
from pathlib import Path

def test_imports():
    """Test if all modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        # Test basic imports
        import flask
        print("✅ Flask imported")
        
        import celery
        print("✅ Celery imported")
        
        import streamlit
        print("✅ Streamlit imported")
        
        import openai
        print("✅ OpenAI imported")
        
        import spacy
        print("✅ spaCy imported")
        
        import pymupdf
        print("✅ PyMuPDF imported")
        
        import docx
        print("✅ python-docx imported")
        
        import sentence_transformers
        print("✅ Sentence Transformers imported")
        
        import sklearn
        print("✅ scikit-learn imported")
        
        import pandas
        print("✅ Pandas imported")
        
        import plotly
        print("✅ Plotly imported")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_spacy_model():
    """Test if spaCy model is available"""
    print("🧪 Testing spaCy model...")
    
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
        print("✅ spaCy model loaded successfully")
        return True
    except OSError:
        print("❌ spaCy model not found. Install with: python -m spacy download en_core_web_sm")
        return False

def test_file_creation():
    """Test if required files exist"""
    print("🧪 Testing file structure...")
    
    required_files = [
        'app.py',
        'models.py',
        'routes.py',
        'resume_parser.py',
        'jd_parser.py',
        'relevance_engine.py',
        'tasks.py',
        'streamlit_app.py',
        'config.py',
        'utils.py',
        'requirements.txt',
        'README.md'
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing files: {', '.join(missing_files)}")
        return False
    else:
        print("✅ All required files present")
        return True

def test_basic_functionality():
    """Test basic functionality of core modules"""
    print("🧪 Testing basic functionality...")
    
    try:
        # Test config
        from config import Config
        config = Config()
        print("✅ Config loaded")
        
        # Test utils
        from utils import clean_text, extract_skills_from_text
        test_text = "I have experience with Python, JavaScript, and React."
        cleaned = clean_text(test_text)
        skills = extract_skills_from_text(test_text)
        print(f"✅ Utils working - Found skills: {skills}")
        
        # Test resume parser (without file)
        from resume_parser import ResumeParser
        parser = ResumeParser()
        print("✅ Resume parser initialized")
        
        # Test JD parser
        from jd_parser import JobDescriptionParser
        jd_parser = JobDescriptionParser()
        print("✅ JD parser initialized")
        
        return True
        
    except Exception as e:
        print(f"❌ Functionality test failed: {e}")
        return False

def test_environment():
    """Test environment setup"""
    print("🧪 Testing environment...")
    
    # Check if .env file exists
    if Path('.env').exists():
        print("✅ .env file found")
    else:
        print("⚠️  .env file not found. Using defaults")
    
    # Check Python version
    python_version = sys.version_info
    if python_version >= (3, 8):
        print(f"✅ Python version {python_version.major}.{python_version.minor} is compatible")
    else:
        print(f"❌ Python version {python_version.major}.{python_version.minor} is too old. Need 3.8+")
        return False
    
    return True

def main():
    """Run all tests"""
    print("🚀 Resume Evaluation System - Test Suite")
    print("=" * 50)
    
    tests = [
        test_environment,
        test_file_creation,
        test_imports,
        test_spacy_model,
        test_basic_functionality
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print()
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready to run.")
        print("\nNext steps:")
        print("1. Set up your .env file with API keys")
        print("2. Install spaCy model: python -m spacy download en_core_web_sm")
        print("3. Set up PostgreSQL database")
        print("4. Run: python start_services.py")
    else:
        print("❌ Some tests failed. Please fix the issues before running the system.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
