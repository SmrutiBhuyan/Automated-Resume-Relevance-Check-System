from datetime import datetime
from app import db

class JobDescription(db.Model):
    __tablename__ = 'job_descriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    must_have_skills = db.Column(db.JSON)  # List of skills
    good_to_have_skills = db.Column(db.JSON)  # List of skills
    qualifications = db.Column(db.JSON)  # List of qualifications
    location = db.Column(db.String(100))
    company = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    evaluations = db.relationship('ResumeEvaluation', backref='job_description', lazy=True)

class Resume(db.Model):
    __tablename__ = 'resumes'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200), nullable=False)
    original_filename = db.Column(db.String(200), nullable=False)
    student_name = db.Column(db.String(100))
    student_email = db.Column(db.String(100))
    student_location = db.Column(db.String(100))
    extracted_text = db.Column(db.Text)
    skills = db.Column(db.JSON)  # List of extracted skills
    education = db.Column(db.JSON)  # List of education details
    experience = db.Column(db.JSON)  # List of experience details
    projects = db.Column(db.JSON)  # List of projects
    certifications = db.Column(db.JSON)  # List of certifications
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    evaluations = db.relationship('ResumeEvaluation', backref='resume', lazy=True)

class ResumeEvaluation(db.Model):
    __tablename__ = 'resume_evaluations'
    
    id = db.Column(db.Integer, primary_key=True)
    job_description_id = db.Column(db.Integer, db.ForeignKey('job_descriptions.id'), nullable=False)
    resume_id = db.Column(db.Integer, db.ForeignKey('resumes.id'), nullable=False)
    
    # Scores
    keyword_score = db.Column(db.Float)
    semantic_score = db.Column(db.Float)
    ats_score = db.Column(db.Float)  # New ATS compatibility score
    final_score = db.Column(db.Float)
    
    # Verdict
    verdict = db.Column(db.String(20))  # High/Medium/Low
    
    # Missing elements
    missing_skills = db.Column(db.JSON)
    missing_certifications = db.Column(db.JSON)
    missing_education = db.Column(db.JSON)
    missing_projects = db.Column(db.JSON)
    
    # Enhanced feedback
    improvement_feedback = db.Column(db.Text)
    strengths = db.Column(db.JSON)  # List of identified strengths
    ats_feedback = db.Column(db.JSON)  # ATS optimization tips
    
    # Metadata
    evaluated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Upload session tracking
    upload_session_id = db.Column(db.String(36))  # UUID for grouping bulk uploads
    is_bulk_upload = db.Column(db.Boolean, default=False)
    
    # Index for better query performance
    __table_args__ = (
        db.Index('idx_job_resume', 'job_description_id', 'resume_id'),
        db.Index('idx_final_score', 'final_score'),
        db.Index('idx_verdict', 'verdict'),
        db.Index('idx_upload_session', 'upload_session_id'),
        db.Index('idx_bulk_upload', 'is_bulk_upload'),
    )