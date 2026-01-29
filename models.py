"""
Database Models for Resume Evaluation System
"""

from app import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON
import uuid

class Job(db.Model):
    """Job Description Model"""
    __tablename__ = 'jobs'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(200), nullable=False)
    company = db.Column(db.String(200), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    requirements = db.Column(JSON)  # Must-have skills, good-to-have skills, qualifications
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    evaluations = db.relationship('Evaluation', backref='job', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'company': self.company,
            'location': self.location,
            'description': self.description,
            'requirements': self.requirements,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'is_active': self.is_active,
            'evaluation_count': len(self.evaluations)
        }

class Resume(db.Model):
    """Resume Model"""
    __tablename__ = 'resumes'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(10), nullable=False)  # PDF, DOCX
    student_name = db.Column(db.String(200), nullable=False)
    student_email = db.Column(db.String(255), nullable=False)
    student_phone = db.Column(db.String(20))
    extracted_text = db.Column(db.Text)
    parsed_data = db.Column(JSON)  # Structured resume data
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_processed = db.Column(db.Boolean, default=False)
    
    # Relationships
    evaluations = db.relationship('Evaluation', backref='resume', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_type': self.file_type,
            'student_name': self.student_name,
            'student_email': self.student_email,
            'student_phone': self.student_phone,
            'extracted_text': self.extracted_text,
            'parsed_data': self.parsed_data,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'is_processed': self.is_processed,
            'evaluation_count': len(self.evaluations)
        }

class Evaluation(db.Model):
    """Resume Evaluation Results Model"""
    __tablename__ = 'evaluations'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = db.Column(db.String(36), db.ForeignKey('jobs.id'), nullable=False)
    resume_id = db.Column(db.String(36), db.ForeignKey('resumes.id'), nullable=False)
    
    # Scoring
    relevance_score = db.Column(db.Float, nullable=False)  # 0-100
    hard_match_score = db.Column(db.Float)  # Keyword/skill matching score
    semantic_match_score = db.Column(db.Float)  # LLM-based semantic score
    
    # Results
    verdict = db.Column(db.String(20), nullable=False)  # High, Medium, Low
    missing_skills = db.Column(JSON)  # List of missing skills
    missing_certifications = db.Column(JSON)  # List of missing certifications
    missing_projects = db.Column(JSON)  # List of missing project types
    strengths = db.Column(JSON)  # List of strengths
    weaknesses = db.Column(JSON)  # List of weaknesses
    
    # Feedback
    improvement_suggestions = db.Column(db.Text)
    detailed_feedback = db.Column(db.Text)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    processing_time = db.Column(db.Float)  # Time taken to process in seconds
    
    # Unique constraint
    __table_args__ = (db.UniqueConstraint('job_id', 'resume_id', name='unique_job_resume_evaluation'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'job_id': self.job_id,
            'resume_id': self.resume_id,
            'relevance_score': self.relevance_score,
            'hard_match_score': self.hard_match_score,
            'semantic_match_score': self.semantic_match_score,
            'verdict': self.verdict,
            'missing_skills': self.missing_skills,
            'missing_certifications': self.missing_certifications,
            'missing_projects': self.missing_projects,
            'strengths': self.strengths,
            'weaknesses': self.weaknesses,
            'improvement_suggestions': self.improvement_suggestions,
            'detailed_feedback': self.detailed_feedback,
            'created_at': self.created_at.isoformat(),
            'processing_time': self.processing_time
        }
