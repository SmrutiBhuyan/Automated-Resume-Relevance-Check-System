"""
Resume Parsing Module
Extracts and structures data from PDF and DOCX resumes
"""

import os
import re
try:
    import fitz  # PyMuPDF
except ImportError:
    import pymupdf as fitz  # Alternative import
from docx import Document
import spacy
from typing import Dict, List, Optional
import json

class ResumeParser:
    def __init__(self):
        # Load spaCy model for NLP processing
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("Warning: spaCy model not found. Install with: python -m spacy download en_core_web_sm")
            self.nlp = None
    
    def parse_resume(self, file_path: str) -> Dict:
        """Parse resume file and extract structured data"""
        file_extension = file_path.split('.')[-1].lower()
        
        if file_extension == 'pdf':
            text = self._extract_from_pdf(file_path)
        elif file_extension == 'docx':
            text = self._extract_from_docx(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")
        
        # Clean and structure the text
        structured_data = self._structure_resume_data(text)
        
        return {
            'raw_text': text,
            'structured_data': structured_data,
            'file_type': file_extension
        }
    
    def _extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            doc = fitz.open(file_path)
            text = ""
            
            for page in doc:
                text += page.get_text()
            
            doc.close()
            return text
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")
    
    def _extract_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        try:
            doc = Document(file_path)
            text = ""
            
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            return text
        except Exception as e:
            raise Exception(f"Error extracting text from DOCX: {str(e)}")
    
    def _structure_resume_data(self, text: str) -> Dict:
        """Structure the extracted text into resume sections"""
        # Clean the text
        text = self._clean_text(text)
        
        # Extract different sections
        sections = {
            'personal_info': self._extract_personal_info(text),
            'contact_info': self._extract_contact_info(text),
            'summary': self._extract_summary(text),
            'experience': self._extract_experience(text),
            'education': self._extract_education(text),
            'skills': self._extract_skills(text),
            'certifications': self._extract_certifications(text),
            'projects': self._extract_projects(text),
            'achievements': self._extract_achievements(text)
        }
        
        return sections
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.\,\;\:\!\?\-\(\)]', '', text)
        return text.strip()
    
    def _extract_personal_info(self, text: str) -> Dict:
        """Extract personal information"""
        if not self.nlp:
            return {}
        
        doc = self.nlp(text)
        personal_info = {}
        
        # Extract names (first person mentioned)
        for ent in doc.ents:
            if ent.label_ == "PERSON" and not personal_info.get('name'):
                personal_info['name'] = ent.text
                break
        
        return personal_info
    
    def _extract_contact_info(self, text: str) -> Dict:
        """Extract contact information"""
        contact_info = {}
        
        # Email pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        if emails:
            contact_info['email'] = emails[0]
        
        # Phone pattern
        phone_pattern = r'(\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})'
        phones = re.findall(phone_pattern, text)
        if phones:
            contact_info['phone'] = ''.join(phones[0])
        
        # LinkedIn pattern
        linkedin_pattern = r'linkedin\.com/in/[\w-]+'
        linkedin = re.search(linkedin_pattern, text, re.IGNORECASE)
        if linkedin:
            contact_info['linkedin'] = linkedin.group()
        
        return contact_info
    
    def _extract_summary(self, text: str) -> str:
        """Extract professional summary/objective"""
        summary_keywords = ['summary', 'objective', 'profile', 'about', 'overview']
        
        lines = text.split('\n')
        for i, line in enumerate(lines):
            line_lower = line.lower().strip()
            if any(keyword in line_lower for keyword in summary_keywords):
                # Extract next few lines as summary
                summary_lines = []
                for j in range(i + 1, min(i + 5, len(lines))):
                    if lines[j].strip():
                        summary_lines.append(lines[j].strip())
                    else:
                        break
                return ' '.join(summary_lines)
        
        return ""
    
    def _extract_experience(self, text: str) -> List[Dict]:
        """Extract work experience"""
        experience_keywords = ['experience', 'employment', 'work history', 'career']
        experience = []
        
        lines = text.split('\n')
        in_experience_section = False
        current_experience = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            line_lower = line.lower()
            
            # Check if we're entering experience section
            if any(keyword in line_lower for keyword in experience_keywords):
                in_experience_section = True
                continue
            
            if in_experience_section:
                # Look for job title patterns
                if self._is_job_title(line):
                    if current_experience:
                        experience.append(current_experience)
                    current_experience = {'title': line}
                # Look for company patterns
                elif self._is_company_name(line):
                    if current_experience:
                        current_experience['company'] = line
                # Look for date patterns
                elif self._is_date_range(line):
                    if current_experience:
                        current_experience['duration'] = line
                # Look for description
                elif current_experience and len(line) > 20:
                    if 'description' not in current_experience:
                        current_experience['description'] = line
                    else:
                        current_experience['description'] += ' ' + line
        
        if current_experience:
            experience.append(current_experience)
        
        return experience
    
    def _extract_education(self, text: str) -> List[Dict]:
        """Extract education information"""
        education_keywords = ['education', 'academic', 'qualification', 'degree']
        education = []
        
        lines = text.split('\n')
        in_education_section = False
        current_education = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            line_lower = line.lower()
            
            # Check if we're entering education section
            if any(keyword in line_lower for keyword in education_keywords):
                in_education_section = True
                continue
            
            if in_education_section:
                # Look for degree patterns
                degree_patterns = ['bachelor', 'master', 'phd', 'diploma', 'certificate', 'degree']
                if any(pattern in line_lower for pattern in degree_patterns):
                    if current_education:
                        education.append(current_education)
                    current_education = {'degree': line}
                # Look for institution patterns
                elif current_education and ('university' in line_lower or 'college' in line_lower or 'institute' in line_lower):
                    current_education['institution'] = line
                # Look for date patterns
                elif self._is_date_range(line):
                    if current_education:
                        current_education['year'] = line
        
        if current_education:
            education.append(current_education)
        
        return education
    
    def _extract_skills(self, text: str) -> List[str]:
        """Extract technical skills"""
        skills_keywords = ['skills', 'technical skills', 'technologies', 'tools']
        skills = []
        
        lines = text.split('\n')
        in_skills_section = False
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            line_lower = line.lower()
            
            # Check if we're entering skills section
            if any(keyword in line_lower for keyword in skills_keywords):
                in_skills_section = True
                continue
            
            if in_skills_section:
                # Extract skills from the line
                # Split by common separators
                skill_candidates = re.split(r'[,;|•\-\n]', line)
                for skill in skill_candidates:
                    skill = skill.strip()
                    if len(skill) > 2 and len(skill) < 50:  # Reasonable skill length
                        skills.append(skill)
        
        # If no skills section found, try to extract from entire text
        if not skills:
            skills = self._extract_skills_from_text(text)
        
        return list(set(skills))  # Remove duplicates
    
    def _extract_skills_from_text(self, text: str) -> List[str]:
        """Extract skills from entire text using common tech terms"""
        common_skills = [
            'python', 'java', 'javascript', 'react', 'angular', 'vue', 'node.js',
            'sql', 'mongodb', 'postgresql', 'mysql', 'aws', 'azure', 'docker',
            'kubernetes', 'git', 'jenkins', 'agile', 'scrum', 'machine learning',
            'data science', 'artificial intelligence', 'deep learning', 'tensorflow',
            'pytorch', 'pandas', 'numpy', 'scikit-learn', 'flask', 'django',
            'spring', 'hibernate', 'microservices', 'rest api', 'graphql'
        ]
        
        found_skills = []
        text_lower = text.lower()
        
        for skill in common_skills:
            if skill in text_lower:
                found_skills.append(skill)
        
        return found_skills
    
    def _extract_certifications(self, text: str) -> List[str]:
        """Extract certifications"""
        cert_keywords = ['certification', 'certificate', 'certified', 'license']
        certifications = []
        
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in cert_keywords):
                certifications.append(line)
        
        return certifications
    
    def _extract_projects(self, text: str) -> List[Dict]:
        """Extract project information"""
        project_keywords = ['projects', 'project', 'portfolio']
        projects = []
        
        lines = text.split('\n')
        in_projects_section = False
        current_project = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            line_lower = line.lower()
            
            # Check if we're entering projects section
            if any(keyword in line_lower for keyword in project_keywords):
                in_projects_section = True
                continue
            
            if in_projects_section:
                # Look for project title patterns
                if len(line) > 5 and len(line) < 100 and not line.endswith(':'):
                    if current_project:
                        projects.append(current_project)
                    current_project = {'title': line}
                # Look for project description
                elif current_project and len(line) > 20:
                    if 'description' not in current_project:
                        current_project['description'] = line
                    else:
                        current_project['description'] += ' ' + line
        
        if current_project:
            projects.append(current_project)
        
        return projects
    
    def _extract_achievements(self, text: str) -> List[str]:
        """Extract achievements and awards"""
        achievement_keywords = ['achievement', 'award', 'recognition', 'honor']
        achievements = []
        
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in achievement_keywords):
                achievements.append(line)
        
        return achievements
    
    def _is_job_title(self, line: str) -> bool:
        """Check if line contains a job title"""
        job_title_indicators = ['engineer', 'developer', 'analyst', 'manager', 'director', 'lead', 'senior', 'junior']
        return any(indicator in line.lower() for indicator in job_title_indicators)
    
    def _is_company_name(self, line: str) -> bool:
        """Check if line contains a company name"""
        company_indicators = ['inc', 'corp', 'ltd', 'llc', 'company', 'technologies', 'solutions']
        return any(indicator in line.lower() for indicator in company_indicators)
    
    def _is_date_range(self, line: str) -> bool:
        """Check if line contains a date range"""
        date_patterns = [
            r'\d{4}\s*-\s*\d{4}',  # 2020-2023
            r'\d{4}\s*to\s*\d{4}',  # 2020 to 2023
            r'\d{1,2}/\d{4}\s*-\s*\d{1,2}/\d{4}',  # 01/2020-12/2023
            r'present',  # Present
            r'current'   # Current
        ]
        return any(re.search(pattern, line.lower()) for pattern in date_patterns)
