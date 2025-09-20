from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
import os
from werkzeug.utils import secure_filename
from app import db
from app.models import JobDescription, Resume, ResumeEvaluation
from app.utils.file_processor import FileProcessor
from app.services.jd_parser import JDParser
from app.services.resume_parser import ResumeParser
from app.services.evaluation_service import EvaluationService
import uuid

main_bp = Blueprint('main', __name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/upload', methods=['GET', 'POST'])
def upload():
    job_descriptions = JobDescription.query.all()
    
    if request.method == 'POST':
        upload_type = request.form.get('upload_type')
        
        # Handle JD upload
        if upload_type == 'jd' and 'jd_file' in request.files:
            jd_file = request.files['jd_file']
            if jd_file and allowed_file(jd_file.filename):
                # Save JD file
                filename = secure_filename(jd_file.filename)
                file_path = os.path.join(UPLOAD_FOLDER, f"jd_{uuid.uuid4()}_{filename}")
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                jd_file.save(file_path)
                
                # Extract text and parse JD
                jd_text = FileProcessor.extract_text(file_path)
                if not jd_text:
                    flash('Could not extract text from the job description file.', 'error')
                    return render_template('upload.html', job_descriptions=job_descriptions)
                
                jd_parser = JDParser()
                jd_data = jd_parser.parse_job_description(jd_text)
                
                # Save to database
                jd = JobDescription(
                    title=jd_data['title'],
                    description=jd_data['description'],
                    must_have_skills=jd_data['must_have_skills'],
                    good_to_have_skills=jd_data['good_to_have_skills'],
                    qualifications=jd_data['qualifications'],
                    location=request.form.get('location', ''),
                    company=request.form.get('company', '')
                )
                db.session.add(jd)
                db.session.commit()
                
                flash('Job description uploaded successfully!', 'success')
                return redirect(url_for('main.upload'))
        
        # Handle resume upload
        elif upload_type == 'resume' and 'resume_file' in request.files:
            resume_file = request.files['resume_file']
            jd_id = request.form.get('jd_id')
            
            if not jd_id:
                flash('Please select a job description.', 'error')
                return render_template('upload.html', job_descriptions=job_descriptions)
            
            if resume_file and allowed_file(resume_file.filename):
                # Save resume file
                filename = secure_filename(resume_file.filename)
                file_path = os.path.join(UPLOAD_FOLDER, f"resume_{uuid.uuid4()}_{filename}")
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                resume_file.save(file_path)
                
                # Extract text and parse resume
                resume_text = FileProcessor.extract_text(file_path)
                if not resume_text:
                    flash('Could not extract text from the resume file.', 'error')
                    return render_template('upload.html', job_descriptions=job_descriptions)
                
                resume_parser = ResumeParser()
                resume_data = resume_parser.parse_resume(resume_text)
                
                # Save resume to database
                resume = Resume(
                    filename=file_path,
                    original_filename=filename,
                    student_name=request.form.get('student_name', ''),
                    student_email=request.form.get('student_email', ''),
                    student_location=request.form.get('student_location', ''),
                    extracted_text=resume_data['extracted_text'],
                    skills=resume_data['skills'],
                    education=resume_data['education'],
                    experience=resume_data['experience'],
                    projects=resume_data['projects'],
                    certifications=resume_data['certifications']
                )
                db.session.add(resume)
                db.session.commit()
                
                # Get JD data
                jd = JobDescription.query.get(jd_id)
                if not jd:
                    flash('Selected job description not found.', 'error')
                    return render_template('upload.html', job_descriptions=job_descriptions)
                
                jd_data = {
                    'must_have_skills': jd.must_have_skills or [],
                    'good_to_have_skills': jd.good_to_have_skills or [],
                    'qualifications': jd.qualifications or [],
                    'description': jd.description
                }
                
                # Evaluate resume
                try:
                    evaluation_service = EvaluationService()
                    evaluation_result = evaluation_service.evaluate_resume(resume_data, jd_data)
                    
                    # Save evaluation
                    evaluation = ResumeEvaluation(
                        job_description_id=jd_id,
                        resume_id=resume.id,
                        keyword_score=evaluation_result['keyword_score'],
                        semantic_score=evaluation_result['semantic_score'],
                        final_score=evaluation_result['final_score'],
                        verdict=evaluation_result['verdict'],
                        missing_skills=evaluation_result['missing_elements']['missing_skills'],
                        missing_certifications=[],
                        missing_education=evaluation_result['missing_elements']['missing_qualifications'],
                        missing_projects=[],
                        improvement_feedback=evaluation_result['improvement_feedback']
                    )
                    db.session.add(evaluation)
                    db.session.commit()
                    
                    flash('Resume uploaded and evaluated successfully!', 'success')
                    return redirect(url_for('main.results', evaluation_id=evaluation.id))
                    
                except Exception as e:
                    db.session.rollback()
                    flash(f'Error during evaluation: {str(e)}', 'error')
                    return render_template('upload.html', job_descriptions=job_descriptions)
            else:
                flash('Please select a valid resume file.', 'error')
        
        # Handle bulk resume upload
        elif upload_type == 'bulk' and 'resume_files' in request.files:
            resume_files = request.files.getlist('resume_files')
            jd_id = request.form.get('jd_id')
            auto_evaluate = request.form.get('auto_evaluate') == 'on'
            generate_report = request.form.get('generate_report') == 'on'
            
            if not jd_id:
                flash('Please select a job description.', 'error')
                return render_template('upload.html', job_descriptions=job_descriptions)
            
            if not resume_files or not any(f.filename for f in resume_files):
                flash('Please select at least one resume file.', 'error')
                return render_template('upload.html', job_descriptions=job_descriptions)
            
            # Get JD data
            jd = JobDescription.query.get(jd_id)
            if not jd:
                flash('Selected job description not found.', 'error')
                return render_template('upload.html', job_descriptions=job_descriptions)
            
            jd_data = {
                'must_have_skills': jd.must_have_skills or [],
                'good_to_have_skills': jd.good_to_have_skills or [],
                'qualifications': jd.qualifications or [],
                'description': jd.description
            }
            
            # Process each resume
            evaluations = []
            successful_uploads = 0
            failed_uploads = 0
            
            for resume_file in resume_files:
                if resume_file and allowed_file(resume_file.filename):
                    try:
                        # Save resume file
                        filename = secure_filename(resume_file.filename)
                        file_path = os.path.join(UPLOAD_FOLDER, f"resume_{uuid.uuid4()}_{filename}")
                        os.makedirs(os.path.dirname(file_path), exist_ok=True)
                        resume_file.save(file_path)
                        
                        # Extract text and parse resume
                        resume_text = FileProcessor.extract_text(file_path)
                        if not resume_text:
                            failed_uploads += 1
                            continue
                        
                        resume_parser = ResumeParser()
                        resume_data = resume_parser.parse_resume(resume_text)
                        
                        # Save resume to database
                        resume = Resume(
                            filename=file_path,
                            original_filename=filename,
                            student_name=f"Bulk Upload - {filename}",
                            student_email="",
                            student_location="",
                            extracted_text=resume_data['extracted_text'],
                            skills=resume_data['skills'],
                            education=resume_data['education'],
                            experience=resume_data['experience'],
                            projects=resume_data['projects'],
                            certifications=resume_data['certifications']
                        )
                        db.session.add(resume)
                        db.session.flush()  # Get the resume ID
                        
                        if auto_evaluate:
                            # Evaluate resume
                            evaluation_service = EvaluationService()
                            evaluation_result = evaluation_service.evaluate_resume(resume_data, jd_data)
                            
                            # Save evaluation
                            evaluation = ResumeEvaluation(
                                job_description_id=jd_id,
                                resume_id=resume.id,
                                keyword_score=evaluation_result['keyword_score'],
                                semantic_score=evaluation_result['semantic_score'],
                                final_score=evaluation_result['final_score'],
                                verdict=evaluation_result['verdict'],
                                missing_skills=evaluation_result['missing_elements']['missing_skills'],
                                missing_certifications=[],
                                missing_education=evaluation_result['missing_elements']['missing_qualifications'],
                                missing_projects=[],
                                improvement_feedback=evaluation_result['improvement_feedback']
                            )
                            db.session.add(evaluation)
                            evaluations.append(evaluation)
                        
                        successful_uploads += 1
                        
                    except Exception as e:
                        failed_uploads += 1
                        print(f"Error processing {resume_file.filename}: {str(e)}")
                        continue
            
            try:
                db.session.commit()
                
                if auto_evaluate and evaluations:
                    flash(f'Successfully uploaded {successful_uploads} resumes and evaluated them! {failed_uploads} failed.', 'success')
                    return redirect(url_for('main.bulk_results', jd_id=jd_id))
                else:
                    flash(f'Successfully uploaded {successful_uploads} resumes! {failed_uploads} failed.', 'success')
                    return redirect(url_for('main.upload'))
                    
            except Exception as e:
                db.session.rollback()
                flash(f'Error during bulk upload: {str(e)}', 'error')
                return render_template('upload.html', job_descriptions=job_descriptions)
    
    return render_template('upload.html', job_descriptions=job_descriptions)

@main_bp.route('/dashboard')
def dashboard():
    # Get all evaluations with resume and JD details
    evaluations = ResumeEvaluation.query.join(Resume).join(JobDescription).all()
    return render_template('dashboard.html', evaluations=evaluations)

@main_bp.route('/results/<int:evaluation_id>')
def results(evaluation_id):
    try:
        evaluation = ResumeEvaluation.query.get_or_404(evaluation_id)
        return render_template('results.html', evaluation=evaluation)
    except Exception as e:
        flash(f'Error loading evaluation results: {str(e)}', 'error')
        return redirect(url_for('main.dashboard'))

@main_bp.route('/bulk-results/<int:jd_id>')
def bulk_results(jd_id):
    try:
        # Get job description
        jd = JobDescription.query.get_or_404(jd_id)
        
        # Get all evaluations for this job description
        evaluations = ResumeEvaluation.query.filter_by(job_description_id=jd_id).join(Resume).all()
        
        # Sort by final score (highest first)
        evaluations.sort(key=lambda x: x.final_score or 0, reverse=True)
        
        # Calculate statistics
        total_evaluations = len(evaluations)
        high_suitability = len([e for e in evaluations if e.verdict == 'High'])
        medium_suitability = len([e for e in evaluations if e.verdict == 'Medium'])
        low_suitability = len([e for e in evaluations if e.verdict == 'Low'])
        
        avg_score = sum(e.final_score or 0 for e in evaluations) / total_evaluations if total_evaluations > 0 else 0
        
        return render_template('bulk_results.html', 
                             job_description=jd,
                             evaluations=evaluations,
                             total_evaluations=total_evaluations,
                             high_suitability=high_suitability,
                             medium_suitability=medium_suitability,
                             low_suitability=low_suitability,
                             avg_score=avg_score)
    except Exception as e:
        flash(f'Error loading bulk results: {str(e)}', 'error')
        return redirect(url_for('main.dashboard'))

@main_bp.route('/api/evaluate', methods=['POST'])
def api_evaluate():
    try:
        data = request.json
        resume_text = data.get('resume_text')
        jd_text = data.get('jd_text')
        
        if not resume_text or not jd_text:
            return jsonify({'error': 'Resume text and JD text are required'}), 400
        
        # Parse resume and JD
        resume_parser = ResumeParser()
        jd_parser = JDParser()
        
        resume_data = resume_parser.parse_resume(resume_text)
        jd_data = jd_parser.parse_job_description(jd_text)
        
        # Evaluate
        evaluation_service = EvaluationService()
        result = evaluation_service.evaluate_resume(resume_data, jd_data)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500