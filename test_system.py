#!/usr/bin/env python3
"""
Test script to verify the system functionality
"""

import os
import sys
from app import create_app, db
from app.services.evaluation_service import EvaluationService
from app.services.embedding_service import EmbeddingService
from app.services.llm_service import LLMService
from app.services.ats_compatibility_service import ATSCompatibilityChecker

def test_embedding_service():
    """Test embedding service functionality"""
    print("Testing Embedding Service...")
    try:
        embedding_service = EmbeddingService()
        
        # Test similarity calculation
        text1 = "Python developer with machine learning experience"
        text2 = "Software engineer skilled in Python and AI"
        
        similarity = embedding_service.calculate_similarity(text1, text2)
        print(f"✓ Similarity calculation: {similarity:.3f}")
        
        return True
    except Exception as e:
        print(f"✗ Embedding service test failed: {e}")
        return False

def test_llm_service():
    """Test LLM service functionality"""
    print("Testing LLM Service...")
    try:
        llm_service = LLMService()
        
        # Test basic feedback generation
        resume_data = {
            'skills': ['Python', 'Machine Learning', 'Data Analysis'],
            'education': ['Bachelor in Computer Science'],
            'experience': ['2 years software development'],
            'projects': ['ML project using Python']
        }
        
        jd_data = {
            'title': 'Data Scientist',
            'must_have_skills': ['Python', 'Machine Learning', 'Statistics'],
            'good_to_have_skills': ['Deep Learning', 'SQL'],
            'qualifications': ['Bachelor in Computer Science or related field']
        }
        
        missing_elements = {
            'missing_skills': ['Statistics', 'Deep Learning'],
            'missing_qualifications': []
        }
        
        feedback = llm_service.generate_improvement_feedback(
            resume_data, jd_data, missing_elements, 75.0
        )
        print(f"✓ LLM feedback generation: {len(feedback)} characters")
        
        return True
    except Exception as e:
        print(f"✗ LLM service test failed: {e}")
        return False

def test_ats_service():
    """Test ATS compatibility service"""
    print("Testing ATS Compatibility Service...")
    try:
        ats_checker = ATSCompatibilityChecker()
        
        resume_text = "John Doe\nSoftware Engineer\nPython, Java, SQL\nBachelor in Computer Science"
        resume_data = {
            'skills': ['Python', 'Java', 'SQL'],
            'education': ['Bachelor in Computer Science'],
            'experience': ['Software Engineer']
        }
        
        result = ats_checker.check_compatibility(resume_text, resume_data)
        print(f"✓ ATS compatibility check: Score {result.score}, Friendly: {result.is_ats_friendly}")
        
        return True
    except Exception as e:
        print(f"✗ ATS service test failed: {e}")
        return False

def test_evaluation_service():
    """Test complete evaluation service"""
    print("Testing Evaluation Service...")
    try:
        evaluation_service = EvaluationService()
        
        resume_data = {
            'extracted_text': 'John Doe is a Python developer with 2 years experience in machine learning and data analysis. He has a Bachelor degree in Computer Science and has worked on several ML projects.',
            'skills': ['Python', 'Machine Learning', 'Data Analysis'],
            'education': ['Bachelor in Computer Science'],
            'experience': ['2 years software development'],
            'projects': ['ML project using Python']
        }
        
        jd_data = {
            'title': 'Data Scientist',
            'description': 'We are looking for a Data Scientist with Python skills, machine learning experience, and statistical knowledge.',
            'must_have_skills': ['Python', 'Machine Learning', 'Statistics'],
            'good_to_have_skills': ['Deep Learning', 'SQL'],
            'qualifications': ['Bachelor in Computer Science or related field']
        }
        
        result = evaluation_service.evaluate_resume(resume_data, jd_data)
        
        print(f"✓ Evaluation completed:")
        print(f"  - Keyword Score: {result['keyword_score']:.1f}")
        print(f"  - Semantic Score: {result['semantic_score']:.1f}")
        print(f"  - Final Score: {result['final_score']:.1f}")
        print(f"  - Verdict: {result['verdict']}")
        print(f"  - Missing Skills: {len(result['missing_elements']['missing_skills'])}")
        
        return True
    except Exception as e:
        print(f"✗ Evaluation service test failed: {e}")
        return False

def test_database_connection():
    """Test database connection"""
    print("Testing Database Connection...")
    try:
        app = create_app()
        with app.app_context():
            # Test database connection with updated SQLAlchemy syntax
            from sqlalchemy import text
            db.session.execute(text("SELECT 1"))
            print("✓ Database connection successful")
            return True
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 50)
    print("Automated Resume Relevance Check System - Test Suite")
    print("=" * 50)
    
    tests = [
        test_database_connection,
        test_embedding_service,
        test_llm_service,
        test_ats_service,
        test_evaluation_service
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print()
        except Exception as e:
            print(f"✗ Test {test.__name__} crashed: {e}")
            print()
    
    print("=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready to use.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the configuration.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
