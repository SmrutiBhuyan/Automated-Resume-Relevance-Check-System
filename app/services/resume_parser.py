import re
from typing import Dict
from app.utils.text_normalizer import TextNormalizer

class ResumeParser:
    def __init__(self):
        self.normalizer = TextNormalizer()
    
    def parse_resume(self, resume_text: str) -> Dict:
        """Parse resume text into structured data"""
        cleaned_text = self.normalizer.clean_text(resume_text)
        
        resume_data = {
            'skills': self.normalizer.extract_skills(cleaned_text),
            'education': self._extract_education(cleaned_text),
            'experience': self._extract_experience(cleaned_text),
            'projects': self._extract_projects(cleaned_text),
            'certifications': self._extract_certifications(cleaned_text),
            'extracted_text': resume_text
        }
        
        return resume_data
    
    def _extract_education(self, text: str) -> list:
        education = []
        # Look for education patterns
        edu_patterns = [
            r'(?:bachelor|b\.?s?\.?|b\.?tech).*?(?:in|of)?\s*([^\n,.]+)',
            r'(?:master|m\.?s?\.?|m\.?tech).*?(?:in|of)?\s*([^\n,.]+)',
            r'(?:ph\.?d\.?|doctorate).*?(?:in|of)?\s*([^\n,.]+)',
            r'degree.*?in\s*([^\n,.]+)'
        ]
        
        for pattern in edu_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            education.extend(matches)
        
        return list(set(education))
    
    def _extract_experience(self, text: str) -> list:
        experience = []
        # Simple experience extraction
        exp_patterns = [
            r'experience.*?:\s*(.*?)(?=skills|education|projects|$)',
            r'work history.*?:\s*(.*?)(?=skills|education|projects|$)'
        ]
        
        for pattern in exp_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
            if matches:
                experience.append(matches[0].strip())
        
        return experience
    
    def _extract_projects(self, text: str) -> list:
        projects = []
        # Simple project extraction
        project_patterns = [
            r'projects.*?:\s*(.*?)(?=experience|education|skills|$)',
            r'project.*?:\s*(.*?)(?=experience|education|skills|$)'
        ]
        
        for pattern in project_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
            if matches:
                projects.append(matches[0].strip())
        
        return projects
    
    def _extract_certifications(self, text: str) -> list:
        certifications = []
        # Look for certification patterns
        cert_patterns = [
            r'certifications?.*?:\s*(.*?)(?=skills|education|experience|$)',
            r'certificate.*?:\s*(.*?)(?=skills|education|experience|$)'
        ]
        
        for pattern in cert_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
            if matches:
                certifications.append(matches[0].strip())
        
        return certifications