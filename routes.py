"""
API Routes for Resume Evaluation System
"""

from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
import uuid
from models import Job, Resume, Evaluation, db
from resume_parser import ResumeParser
from jd_parser import JobDescriptionParser
from relevance_engine import RelevanceEngine
from tasks import process_resume_evaluation
from utils import allowed_file, generate_unique_filename, validate_email, validate_phone

api_bp = Blueprint('api', __name__)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf', 'docx'}

# Job Description Routes
@api_bp.route('/jobs', methods=['POST'])
def create_job():
    """Create a new job posting"""
    try:
        data = request.get_json()
        
        # Parse job description
        jd_parser = JobDescriptionParser()
        parsed_jd = jd_parser.parse_job_description(data['description'])
        
        job = Job(
            title=data['title'],
            company=data['company'],
            location=data['location'],
            description=data['description'],
            requirements=parsed_jd
        )
        
        db.session.add(job)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Job created successfully',
            'job': job.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error creating job: {str(e)}'
        }), 400

@api_bp.route('/jobs', methods=['GET'])
def get_jobs():
    """Get all job postings"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        active_only = request.args.get('active_only', 'true').lower() == 'true'
        
        query = Job.query
        if active_only:
            query = query.filter_by(is_active=True)
        
        jobs = query.order_by(Job.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'success': True,
            'jobs': [job.to_dict() for job in jobs.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': jobs.total,
                'pages': jobs.pages
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching jobs: {str(e)}'
        }), 500

@api_bp.route('/jobs/<job_id>', methods=['GET'])
def get_job(job_id):
    """Get a specific job posting"""
    try:
        job = Job.query.get_or_404(job_id)
        return jsonify({
            'success': True,
            'job': job.to_dict()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching job: {str(e)}'
        }), 500

# Resume Routes
@api_bp.route('/resumes', methods=['POST'])
def upload_resume():
    """Upload a new resume"""
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'message': 'No file provided'
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'message': 'No file selected'
            }), 400
        
        if not allowed_file(file.filename, ALLOWED_EXTENSIONS):
            return jsonify({
                'success': False,
                'message': 'Invalid file type. Only PDF and DOCX files are allowed'
            }), 400
        
        # Get form data
        student_name = request.form.get('student_name', '')
        student_email = request.form.get('student_email', '')
        student_phone = request.form.get('student_phone', '')
        
        if not student_name or not student_email:
            return jsonify({
                'success': False,
                'message': 'Student name and email are required'
            }), 400
        
        # Validate email format
        if not validate_email(student_email):
            return jsonify({
                'success': False,
                'message': 'Invalid email format'
            }), 400
        
        # Validate phone if provided
        if student_phone and not validate_phone(student_phone):
            return jsonify({
                'success': False,
                'message': 'Invalid phone number format'
            }), 400
        
        # Save file
        unique_filename = generate_unique_filename(file.filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'resumes', unique_filename)
        file.save(file_path)
        
        # Create resume record
        resume = Resume(
            filename=unique_filename,
            original_filename=file.filename,
            file_path=file_path,
            file_type=file.filename.rsplit('.', 1)[1].lower(),
            student_name=student_name,
            student_email=student_email,
            student_phone=student_phone
        )
        
        db.session.add(resume)
        db.session.commit()
        
        # Process resume in background
        process_resume_evaluation.delay(resume.id)
        
        return jsonify({
            'success': True,
            'message': 'Resume uploaded successfully',
            'resume': resume.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error uploading resume: {str(e)}'
        }), 400

@api_bp.route('/resumes', methods=['GET'])
def get_resumes():
    """Get all resumes"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        resumes = Resume.query.order_by(Resume.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'success': True,
            'resumes': [resume.to_dict() for resume in resumes.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': resumes.total,
                'pages': resumes.pages
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching resumes: {str(e)}'
        }), 500

# Evaluation Routes
@api_bp.route('/evaluations', methods=['POST'])
def create_evaluation():
    """Create evaluation for a resume against a job"""
    try:
        data = request.get_json()
        job_id = data.get('job_id')
        resume_id = data.get('resume_id')
        
        if not job_id or not resume_id:
            return jsonify({
                'success': False,
                'message': 'Job ID and Resume ID are required'
            }), 400
        
        # Check if evaluation already exists
        existing_evaluation = Evaluation.query.filter_by(
            job_id=job_id, resume_id=resume_id
        ).first()
        
        if existing_evaluation:
            return jsonify({
                'success': False,
                'message': 'Evaluation already exists for this resume and job'
            }), 400
        
        # Process evaluation in background
        task = process_resume_evaluation.delay(resume_id, job_id)
        
        return jsonify({
            'success': True,
            'message': 'Evaluation started',
            'task_id': task.id
        }), 202
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error creating evaluation: {str(e)}'
        }), 400

@api_bp.route('/evaluations', methods=['GET'])
def get_evaluations():
    """Get all evaluations with filtering"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        job_id = request.args.get('job_id')
        verdict = request.args.get('verdict')
        min_score = request.args.get('min_score', type=float)
        
        query = Evaluation.query
        
        if job_id:
            query = query.filter_by(job_id=job_id)
        if verdict:
            query = query.filter_by(verdict=verdict)
        if min_score is not None:
            query = query.filter(Evaluation.relevance_score >= min_score)
        
        evaluations = query.order_by(Evaluation.relevance_score.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'success': True,
            'evaluations': [evaluation.to_dict() for evaluation in evaluations.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': evaluations.total,
                'pages': evaluations.pages
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching evaluations: {str(e)}'
        }), 500

@api_bp.route('/evaluations/<evaluation_id>', methods=['GET'])
def get_evaluation(evaluation_id):
    """Get a specific evaluation"""
    try:
        evaluation = Evaluation.query.get_or_404(evaluation_id)
        return jsonify({
            'success': True,
            'evaluation': evaluation.to_dict()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching evaluation: {str(e)}'
        }), 500

# Dashboard Routes
@api_bp.route('/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        total_jobs = Job.query.count()
        total_resumes = Resume.query.count()
        total_evaluations = Evaluation.query.count()
        
        # Evaluation distribution
        high_fit = Evaluation.query.filter_by(verdict='High').count()
        medium_fit = Evaluation.query.filter_by(verdict='Medium').count()
        low_fit = Evaluation.query.filter_by(verdict='Low').count()
        
        # Recent activity
        recent_evaluations = Evaluation.query.order_by(
            Evaluation.created_at.desc()
        ).limit(5).all()
        
        return jsonify({
            'success': True,
            'stats': {
                'total_jobs': total_jobs,
                'total_resumes': total_resumes,
                'total_evaluations': total_evaluations,
                'evaluation_distribution': {
                    'high_fit': high_fit,
                    'medium_fit': medium_fit,
                    'low_fit': low_fit
                },
                'recent_evaluations': [eval.to_dict() for eval in recent_evaluations]
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching dashboard stats: {str(e)}'
        }), 500
