"""
Celery Background Tasks
Process resume evaluations asynchronously
"""

from celery import Celery
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Celery
celery = Celery(
    'resume_evaluation',
    broker=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    backend=os.getenv('REDIS_URL', 'redis://localhost:6379/0')
)

# Configure Celery
celery.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

# Import after Celery is configured to avoid circular imports
from app import db
from models import Job, Resume, Evaluation
from resume_parser import ResumeParser
from relevance_engine import RelevanceEngine

@celery.task
def process_resume_evaluation(resume_id: str, job_id: str = None):
    """Process resume evaluation task"""
    start_time = time.time()
    
    try:
        # Get resume from database
        resume = Resume.query.get(resume_id)
        if not resume:
            raise Exception(f"Resume with ID {resume_id} not found")
        
        # Parse resume if not already processed
        if not resume.is_processed:
            parser = ResumeParser()
            parsed_data = parser.parse_resume(resume.file_path)
            
            # Update resume with parsed data
            resume.extracted_text = parsed_data['raw_text']
            resume.parsed_data = parsed_data['structured_data']
            resume.is_processed = True
            db.session.commit()
        
        # If job_id is provided, evaluate against specific job
        if job_id:
            job = Job.query.get(job_id)
            if not job:
                raise Exception(f"Job with ID {job_id} not found")
            
            # Check if evaluation already exists
            existing_evaluation = Evaluation.query.filter_by(
                job_id=job_id, resume_id=resume_id
            ).first()
            
            if existing_evaluation:
                return {
                    'status': 'already_exists',
                    'evaluation_id': existing_evaluation.id,
                    'message': 'Evaluation already exists'
                }
            
            # Perform evaluation
            relevance_engine = RelevanceEngine()
            evaluation_result = relevance_engine.evaluate_relevance(
                {
                    'raw_text': resume.extracted_text,
                    'structured_data': resume.parsed_data
                },
                job.requirements
            )
            
            # Create evaluation record
            evaluation = Evaluation(
                job_id=job_id,
                resume_id=resume_id,
                relevance_score=evaluation_result['relevance_score'],
                hard_match_score=evaluation_result['hard_match_score'],
                semantic_match_score=evaluation_result['semantic_match_score'],
                verdict=evaluation_result['verdict'],
                missing_skills=evaluation_result['missing_skills'],
                missing_certifications=evaluation_result['missing_certifications'],
                missing_projects=evaluation_result['missing_projects'],
                strengths=evaluation_result['strengths'],
                weaknesses=evaluation_result['weaknesses'],
                improvement_suggestions=evaluation_result['improvement_suggestions'],
                detailed_feedback=evaluation_result['detailed_feedback'],
                processing_time=time.time() - start_time
            )
            
            db.session.add(evaluation)
            db.session.commit()
            
            return {
                'status': 'completed',
                'evaluation_id': evaluation.id,
                'relevance_score': evaluation.relevance_score,
                'verdict': evaluation.verdict,
                'processing_time': evaluation.processing_time
            }
        
        else:
            # Process resume parsing only
            return {
                'status': 'parsed',
                'resume_id': resume_id,
                'message': 'Resume parsed successfully'
            }
    
    except Exception as e:
        db.session.rollback()
        return {
            'status': 'error',
            'message': str(e),
            'processing_time': time.time() - start_time
        }

@celery.task
def batch_evaluate_resumes(job_id: str):
    """Evaluate all resumes against a specific job"""
    try:
        job = Job.query.get(job_id)
        if not job:
            raise Exception(f"Job with ID {job_id} not found")
        
        # Get all processed resumes
        resumes = Resume.query.filter_by(is_processed=True).all()
        
        results = []
        for resume in resumes:
            # Check if evaluation already exists
            existing_evaluation = Evaluation.query.filter_by(
                job_id=job_id, resume_id=resume.id
            ).first()
            
            if not existing_evaluation:
                # Process evaluation
                result = process_resume_evaluation.delay(resume.id, job_id)
                results.append({
                    'resume_id': resume.id,
                    'student_name': resume.student_name,
                    'task_id': result.id
                })
            else:
                results.append({
                    'resume_id': resume.id,
                    'student_name': resume.student_name,
                    'status': 'already_exists',
                    'evaluation_id': existing_evaluation.id
                })
        
        return {
            'status': 'batch_started',
            'job_id': job_id,
            'total_resumes': len(resumes),
            'results': results
        }
    
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }

@celery.task
def cleanup_old_files():
    """Clean up old uploaded files"""
    try:
        import os
        from datetime import datetime, timedelta
        
        upload_folder = os.path.join(os.getcwd(), 'uploads')
        cutoff_date = datetime.now() - timedelta(days=30)  # 30 days old
        
        cleaned_files = 0
        for root, dirs, files in os.walk(upload_folder):
            for file in files:
                file_path = os.path.join(root, file)
                file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                
                if file_time < cutoff_date:
                    try:
                        os.remove(file_path)
                        cleaned_files += 1
                    except:
                        pass
        
        return {
            'status': 'completed',
            'cleaned_files': cleaned_files,
            'message': f'Cleaned up {cleaned_files} old files'
        }
    
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }
