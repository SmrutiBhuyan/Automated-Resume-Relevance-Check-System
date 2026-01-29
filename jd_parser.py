"""
Job Description Parsing Module
Extracts and structures requirements from job descriptions
"""

import re
import spacy
from typing import Dict, List, Optional
import json

class JobDescriptionParser:
    def __init__(self):
        # Load spaCy model for NLP processing
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("Warning: spaCy model not found. Install with: python -m spacy download en_core_web_sm")
            self.nlp = None
    
    def parse_job_description(self, jd_text: str) -> Dict:
        """Parse job description and extract structured requirements"""
        # Clean the text
        jd_text = self._clean_text(jd_text)
        
        # Extract different sections
        structured_data = {
            'title': self._extract_job_title(jd_text),
            'company': self._extract_company_name(jd_text),
            'location': self._extract_location(jd_text),
            'experience_level': self._extract_experience_level(jd_text),
            'employment_type': self._extract_employment_type(jd_text),
            'salary_range': self._extract_salary_range(jd_text),
            'must_have_skills': self._extract_must_have_skills(jd_text),
            'good_to_have_skills': self._extract_good_to_have_skills(jd_text),
            'qualifications': self._extract_qualifications(jd_text),
            'responsibilities': self._extract_responsibilities(jd_text),
            'benefits': self._extract_benefits(jd_text),
            'education_requirements': self._extract_education_requirements(jd_text),
            'certifications': self._extract_certification_requirements(jd_text),
            'soft_skills': self._extract_soft_skills(jd_text),
            'technical_requirements': self._extract_technical_requirements(jd_text)
        }
        
        return structured_data
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.\,\;\:\!\?\-\(\)]', '', text)
        return text.strip()
    
    def _extract_job_title(self, text: str) -> str:
        """Extract job title from the beginning of the text"""
        lines = text.split('\n')
        for line in lines[:5]:  # Check first 5 lines
            line = line.strip()
            if len(line) > 5 and len(line) < 100:
                # Look for common job title patterns
                title_indicators = ['engineer', 'developer', 'analyst', 'manager', 'specialist', 'consultant', 'architect']
                if any(indicator in line.lower() for indicator in title_indicators):
                    return line
        return ""
    
    def _extract_company_name(self, text: str) -> str:
        """Extract company name"""
        lines = text.split('\n')
        for line in lines[:10]:  # Check first 10 lines
            line = line.strip()
            if len(line) > 3 and len(line) < 100:
                # Look for company indicators
                company_indicators = ['inc', 'corp', 'ltd', 'llc', 'company', 'technologies', 'solutions', 'systems']
                if any(indicator in line.lower() for indicator in company_indicators):
                    return line
        return ""
    
    def _extract_location(self, text: str) -> str:
        """Extract job location"""
        if not self.nlp:
            return ""
        
        doc = self.nlp(text)
        for ent in doc.ents:
            if ent.label_ == "GPE":  # Geopolitical entity
                return ent.text
        
        # Fallback: look for common location patterns
        location_patterns = [
            r'(?:in|at|based in|located in)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),\s*(?:India|USA|UK|Canada|Australia)'
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return ""
    
    def _extract_experience_level(self, text: str) -> str:
        """Extract required experience level"""
        experience_patterns = {
            'entry': r'(?:entry|fresher|0-1|0-2)\s*(?:years?|yrs?)',
            'junior': r'(?:junior|1-3|2-4)\s*(?:years?|yrs?)',
            'mid': r'(?:mid|3-5|4-6|5-7)\s*(?:years?|yrs?)',
            'senior': r'(?:senior|5-8|6-10|7-12)\s*(?:years?|yrs?)',
            'lead': r'(?:lead|principal|8-12|10-15)\s*(?:years?|yrs?)',
            'executive': r'(?:executive|director|15\+|12\+)\s*(?:years?|yrs?)'
        }
        
        text_lower = text.lower()
        for level, pattern in experience_patterns.items():
            if re.search(pattern, text_lower):
                return level
        
        return "not_specified"
    
    def _extract_employment_type(self, text: str) -> str:
        """Extract employment type"""
        text_lower = text.lower()
        
        if 'full-time' in text_lower or 'full time' in text_lower:
            return 'full-time'
        elif 'part-time' in text_lower or 'part time' in text_lower:
            return 'part-time'
        elif 'contract' in text_lower:
            return 'contract'
        elif 'intern' in text_lower:
            return 'internship'
        elif 'remote' in text_lower:
            return 'remote'
        else:
            return 'not_specified'
    
    def _extract_salary_range(self, text: str) -> Dict:
        """Extract salary range"""
        salary_patterns = [
            r'₹?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)\s*-\s*₹?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:lpa|lakhs?|crores?|k|thousand)',
            r'₹?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:lpa|lakhs?|crores?|k|thousand)\s*-\s*₹?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:lpa|lakhs?|crores?|k|thousand)',
            r'(\d+)\s*-\s*(\d+)\s*(?:lpa|lakhs?|crores?)'
        ]
        
        for pattern in salary_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return {
                    'min': match.group(1),
                    'max': match.group(2),
                    'currency': 'INR' if '₹' in text or 'lpa' in text.lower() else 'USD'
                }
        
        return {}
    
    def _extract_must_have_skills(self, text: str) -> List[str]:
        """Extract must-have skills"""
        must_have_sections = self._find_requirement_sections(text, ['must have', 'required', 'mandatory', 'essential'])
        skills = []
        
        for section in must_have_sections:
            skills.extend(self._extract_skills_from_section(section))
        
        return list(set(skills))
    
    def _extract_good_to_have_skills(self, text: str) -> List[str]:
        """Extract good-to-have skills"""
        good_to_have_sections = self._find_requirement_sections(text, ['good to have', 'preferred', 'nice to have', 'desired', 'optional'])
        skills = []
        
        for section in good_to_have_sections:
            skills.extend(self._extract_skills_from_section(section))
        
        return list(set(skills))
    
    def _extract_qualifications(self, text: str) -> List[str]:
        """Extract educational qualifications"""
        qualification_keywords = ['bachelor', 'master', 'phd', 'diploma', 'degree', 'certification', 'qualification']
        qualifications = []
        
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in qualification_keywords):
                qualifications.append(line)
        
        return qualifications
    
    def _extract_responsibilities(self, text: str) -> List[str]:
        """Extract job responsibilities"""
        responsibility_sections = self._find_requirement_sections(text, ['responsibilities', 'duties', 'role', 'what you will do'])
        responsibilities = []
        
        for section in responsibility_sections:
            # Split by bullet points or line breaks
            items = re.split(r'[•\-\*\n]', section)
            for item in items:
                item = item.strip()
                if len(item) > 10:  # Meaningful responsibility
                    responsibilities.append(item)
        
        return responsibilities
    
    def _extract_benefits(self, text: str) -> List[str]:
        """Extract job benefits"""
        benefit_sections = self._find_requirement_sections(text, ['benefits', 'perks', 'compensation', 'package'])
        benefits = []
        
        for section in benefit_sections:
            # Split by bullet points or line breaks
            items = re.split(r'[•\-\*\n]', section)
            for item in items:
                item = item.strip()
                if len(item) > 5:  # Meaningful benefit
                    benefits.append(item)
        
        return benefits
    
    def _extract_education_requirements(self, text: str) -> List[str]:
        """Extract education requirements"""
        education_keywords = ['bachelor', 'master', 'phd', 'diploma', 'degree', 'education', 'qualification']
        education_requirements = []
        
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in education_keywords):
                education_requirements.append(line)
        
        return education_requirements
    
    def _extract_certification_requirements(self, text: str) -> List[str]:
        """Extract certification requirements"""
        cert_keywords = ['certification', 'certificate', 'certified', 'license', 'accreditation']
        certifications = []
        
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in cert_keywords):
                certifications.append(line)
        
        return certifications
    
    def _extract_soft_skills(self, text: str) -> List[str]:
        """Extract soft skills requirements"""
        soft_skills = [
            'communication', 'leadership', 'teamwork', 'problem solving', 'analytical',
            'creative', 'adaptable', 'time management', 'project management', 'mentoring',
            'collaboration', 'presentation', 'negotiation', 'customer service'
        ]
        
        found_skills = []
        text_lower = text.lower()
        
        for skill in soft_skills:
            if skill in text_lower:
                found_skills.append(skill)
        
        return found_skills
    
    def _extract_technical_requirements(self, text: str) -> List[str]:
        """Extract technical requirements"""
        technical_skills = [
            'python', 'java', 'javascript', 'react', 'angular', 'vue', 'node.js',
            'sql', 'mongodb', 'postgresql', 'mysql', 'aws', 'azure', 'docker',
            'kubernetes', 'git', 'jenkins', 'agile', 'scrum', 'machine learning',
            'data science', 'artificial intelligence', 'deep learning', 'tensorflow',
            'pytorch', 'pandas', 'numpy', 'scikit-learn', 'flask', 'django',
            'spring', 'hibernate', 'microservices', 'rest api', 'graphql'
        ]
        
        found_skills = []
        text_lower = text.lower()
        
        for skill in technical_skills:
            if skill in text_lower:
                found_skills.append(skill)
        
        return found_skills
    
    def _find_requirement_sections(self, text: str, keywords: List[str]) -> List[str]:
        """Find sections containing specific keywords"""
        sections = []
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            line_lower = line.lower().strip()
            if any(keyword in line_lower for keyword in keywords):
                # Extract the section content
                section_content = []
                for j in range(i + 1, min(i + 10, len(lines))):  # Next 10 lines
                    if lines[j].strip():
                        section_content.append(lines[j].strip())
                    else:
                        break
                if section_content:
                    sections.append(' '.join(section_content))
        
        return sections
    
    def _extract_skills_from_section(self, section: str) -> List[str]:
        """Extract skills from a specific section"""
        skills = []
        
        # Split by common separators
        skill_candidates = re.split(r'[,;|•\-\n]', section)
        for skill in skill_candidates:
            skill = skill.strip()
            if len(skill) > 2 and len(skill) < 100:  # Reasonable skill length
                skills.append(skill)
        
        return skills
