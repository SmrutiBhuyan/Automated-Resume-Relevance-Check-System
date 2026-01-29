"""
Utility functions for the Resume Evaluation System
"""

import os
import re
import uuid
from typing import List, Dict, Any
from werkzeug.utils import secure_filename
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def allowed_file(filename: str, allowed_extensions: set = None) -> bool:
    """Check if file extension is allowed"""
    if allowed_extensions is None:
        allowed_extensions = {'pdf', 'docx'}
    
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def generate_unique_filename(original_filename: str) -> str:
    """Generate a unique filename for uploaded files"""
    filename = secure_filename(original_filename)
    name, ext = os.path.splitext(filename)
    unique_id = str(uuid.uuid4())
    return f"{unique_id}_{name}{ext}"

def clean_text(text: str) -> str:
    """Clean and normalize text"""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s\.\,\;\:\!\?\-\(\)]', '', text)
    return text.strip()

def extract_skills_from_text(text: str) -> List[str]:
    """Extract skills from text using common patterns"""
    common_skills = [
        'python', 'java', 'javascript', 'react', 'angular', 'vue', 'node.js',
        'sql', 'mongodb', 'postgresql', 'mysql', 'aws', 'azure', 'docker',
        'kubernetes', 'git', 'jenkins', 'agile', 'scrum', 'machine learning',
        'data science', 'artificial intelligence', 'deep learning', 'tensorflow',
        'pytorch', 'pandas', 'numpy', 'scikit-learn', 'flask', 'django',
        'spring', 'hibernate', 'microservices', 'rest api', 'graphql',
        'html', 'css', 'bootstrap', 'jquery', 'php', 'ruby', 'go', 'rust',
        'c++', 'c#', 'swift', 'kotlin', 'android', 'ios', 'xamarin',
        'tableau', 'power bi', 'excel', 'vba', 'r', 'matlab', 'sas',
        'linux', 'windows', 'macos', 'unix', 'bash', 'powershell'
    ]
    
    found_skills = []
    text_lower = text.lower()
    
    for skill in common_skills:
        if skill in text_lower:
            found_skills.append(skill)
    
    return found_skills

def calculate_text_similarity(text1: str, text2: str) -> float:
    """Calculate similarity between two texts using simple word overlap"""
    if not text1 or not text2:
        return 0.0
    
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    if not words1 or not words2:
        return 0.0
    
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    return len(intersection) / len(union) if union else 0.0

def format_score(score: float) -> str:
    """Format score for display"""
    return f"{score:.1f}"

def get_verdict_color(verdict: str) -> str:
    """Get color code for verdict display"""
    colors = {
        'High': '#2E8B57',  # Green
        'Medium': '#FFD700',  # Gold
        'Low': '#DC143C'  # Red
    }
    return colors.get(verdict, '#666666')

def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to specified length"""
    if not text:
        return ""
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length-3] + "..."

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone: str) -> bool:
    """Validate phone number format"""
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone)
    # Check if it's a valid length (7-15 digits)
    return 7 <= len(digits) <= 15

def create_upload_directories(base_path: str) -> None:
    """Create necessary upload directories"""
    directories = [
        os.path.join(base_path, 'resumes'),
        os.path.join(base_path, 'job_descriptions'),
        os.path.join(base_path, 'temp')
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"Created directory: {directory}")

def get_file_size_mb(file_path: str) -> float:
    """Get file size in MB"""
    try:
        size_bytes = os.path.getsize(file_path)
        return size_bytes / (1024 * 1024)
    except OSError:
        return 0.0

def is_valid_file_size(file_path: str, max_size_mb: float = 16.0) -> bool:
    """Check if file size is within limits"""
    file_size_mb = get_file_size_mb(file_path)
    return file_size_mb <= max_size_mb

def extract_file_extension(filename: str) -> str:
    """Extract file extension from filename"""
    return filename.rsplit('.', 1)[1].lower() if '.' in filename else ''

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage"""
    # Remove or replace unsafe characters
    filename = re.sub(r'[^\w\s.-]', '', filename)
    # Replace spaces with underscores
    filename = re.sub(r'\s+', '_', filename)
    # Remove multiple underscores
    filename = re.sub(r'_+', '_', filename)
    return filename.strip('_.')

def format_timestamp(timestamp) -> str:
    """Format timestamp for display"""
    if hasattr(timestamp, 'strftime'):
        return timestamp.strftime('%Y-%m-%d %H:%M:%S')
    return str(timestamp)

def calculate_processing_time(start_time: float, end_time: float = None) -> float:
    """Calculate processing time in seconds"""
    if end_time is None:
        import time
        end_time = time.time()
    return round(end_time - start_time, 2)

def get_error_message(error: Exception) -> str:
    """Get user-friendly error message"""
    error_messages = {
        'FileNotFoundError': 'File not found. Please check the file path.',
        'PermissionError': 'Permission denied. Please check file permissions.',
        'ValueError': 'Invalid input. Please check your data.',
        'KeyError': 'Missing required field. Please provide all necessary information.',
        'ConnectionError': 'Connection failed. Please check your network connection.',
        'TimeoutError': 'Request timed out. Please try again.',
    }
    
    error_type = type(error).__name__
    return error_messages.get(error_type, f'An error occurred: {str(error)}')

def log_error(error: Exception, context: str = "") -> None:
    """Log error with context"""
    error_msg = get_error_message(error)
    if context:
        logger.error(f"{context}: {error_msg}")
    else:
        logger.error(error_msg)

def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> List[str]:
    """Validate that all required fields are present"""
    missing_fields = []
    for field in required_fields:
        if field not in data or not data[field]:
            missing_fields.append(field)
    return missing_fields

def safe_get(data: Dict[str, Any], key: str, default: Any = None) -> Any:
    """Safely get value from dictionary with default"""
    try:
        return data.get(key, default)
    except (KeyError, TypeError):
        return default

def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """Split list into chunks of specified size"""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

def remove_duplicates(lst: List[Any]) -> List[Any]:
    """Remove duplicates while preserving order"""
    seen = set()
    result = []
    for item in lst:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result
