import re
import json
from typing import Dict, List

class JDParser:
    def parse_job_description(self, jd_text: str) -> Dict:
        """Parse job description text into structured data"""
        jd_data = {
            'title': self._extract_title(jd_text),
            'must_have_skills': self._extract_must_have_skills(jd_text),
            'good_to_have_skills': self._extract_good_to_have_skills(jd_text),
            'qualifications': self._extract_qualifications(jd_text),
            'description': jd_text
        }
        return jd_data
    
    def _extract_title(self, text: str) -> str:
        # Simple title extraction from first few lines
        lines = text.split('\n')
        for line in lines[:5]:
            if line.strip() and len(line.strip()) < 100:
                return line.strip()
        return "Software Engineer"  # Default
    
    def _extract_must_have_skills(self, text: str) -> List[str]:
        skills = []
        
        # Look for must-have patterns
        must_have_patterns = [
            r'must have.*?skills?[:]?(.*?)(?=good to have|required|qualifications|$)',
            r'required skills?[:]?(.*?)(?=preferred|good to have|qualifications|$)',
            r'essential skills?[:]?(.*?)(?=desired|good to have|qualifications|$)',
            r'who you are.*?(.*?)(?=what you will do|qualifications|$)',
            r'requirements?.*?(.*?)(?=responsibilities|duties|what you will do|$)'
        ]
        
        for pattern in must_have_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
            if matches:
                skills.extend(self._extract_skills_from_text(matches[0]))
        
        # Also extract from bullet points and general text
        skills.extend(self._extract_skills_from_text(text))
        
        return list(set(skills))
    
    def _extract_good_to_have_skills(self, text: str) -> List[str]:
        skills = []
        # Look for good-to-have patterns
        good_to_have_patterns = [
            r'good to have.*?skills?[:]?(.*?)(?=must have|required|qualifications|$)',
            r'preferred skills?[:]?(.*?)(?=must have|required|qualifications|$)',
            r'desired skills?[:]?(.*?)(?=must have|required|qualifications|$)'
        ]
        
        for pattern in good_to_have_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
            if matches:
                skills.extend(self._extract_skills_from_text(matches[0]))
        
        return list(set(skills))
    
    def _extract_qualifications(self, text: str) -> List[str]:
        qualifications = []
        # Look for qualification patterns
        qual_patterns = [
            r'qualifications?[:]?(.*?)(?=skills|responsibilities|duties|$)',
            r'education.*?required[:]?(.*?)(?=experience|skills|$)',
            r'degree.*?required[:]?(.*?)(?=experience|skills|$)',
            r'bachelor[\'s]?s?.*?(?:in|of)?\s*(.*?)(?:\s*degree)?',
            r'master[\'s]?s?.*?(?:in|of)?\s*(.*?)(?:\s*degree)?',
            r'ph\.?d\.?.*?(?:in|of)?\s*(.*?)',
            r'degree.*?in\s*(.*?)'
        ]
        
        for pattern in qual_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
            if matches:
                qualifications.extend(self._extract_qualifications_from_text(matches[0]))
        
        # Also extract from general text
        qualifications.extend(self._extract_qualifications_from_text(text))
        
        return list(set(qualifications))
    
    def _extract_skills_from_text(self, text: str) -> List[str]:
        # Common technical skills list
        common_skills = [
            'python', 'java', 'javascript', 'html', 'css', 'react', 'angular', 'vue',
            'node.js', 'express', 'django', 'flask', 'spring', 'sql', 'mysql', 
            'postgresql', 'mongodb', 'aws', 'azure', 'gcp', 'docker', 'kubernetes',
            'jenkins', 'git', 'ci/cd', 'machine learning', 'deep learning', 'ai',
            'data analysis', 'data science', 'tableau', 'power bi', 'excel', 'pandas',
            'r', 'statistics', 'manufacturing', 'engineering', 'automotive', 'aerospace',
            'pandas', 'numpy', 'matplotlib', 'seaborn', 'beautiful soup', 'requests',
            'data manipulation', 'data cleaning', 'eda', 'exploratory data analysis',
            'web scraping', 'power query', 'dax', 'pivot tables', 'conditional formatting',
            'descriptive statistics', 'correlation analysis', 'hypothesis testing',
            'mechanical engineering', 'production engineering', 'manufacturing engineering',
            'automotive engineering', 'aerospace engineering', 'data exploration',
            'data automation', 'business intelligence', 'data visualization',
            'machine learning engineers', 'data scientists', 'data engineers',
            'product managers', 'stakeholders', 'collaboration', 'communication'
        ]
        
        found_skills = []
        for skill in common_skills:
            if re.search(rf'\b{re.escape(skill)}\b', text, re.IGNORECASE):
                found_skills.append(skill)
        
        # Extract skills from bullet points and specific patterns
        bullet_patterns = [
            r'●\s*(.*?)(?=\n|$)',
            r'•\s*(.*?)(?=\n|$)',
            r'-\s*(.*?)(?=\n|$)',
            r'experience in\s+(.*?)(?=\s|,|\.|$)',
            r'proficiency in\s+(.*?)(?=\s|,|\.|$)',
            r'knowledge of\s+(.*?)(?=\s|,|\.|$)',
            r'familiarity with\s+(.*?)(?=\s|,|\.|$)'
        ]
        
        for pattern in bullet_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                # Extract individual skills from the match
                skills_in_match = self._extract_skills_from_text(match)
                found_skills.extend(skills_in_match)
        
        return list(set(found_skills))
    
    def _extract_qualifications_from_text(self, text: str) -> List[str]:
        qualifications = []
        degree_patterns = [
            r'bachelor[\'s]?s?\s+degree\s+in\s+(.*?)(?:\s|,|\.|$)',
            r'bachelor[\'s]?s?\s+in\s+(.*?)(?:\s|,|\.|$)',
            r'master[\'s]?s?\s+degree\s+in\s+(.*?)(?:\s|,|\.|$)',
            r'master[\'s]?s?\s+in\s+(.*?)(?:\s|,|\.|$)',
            r'ph\.?d\.?\s+in\s+(.*?)(?:\s|,|\.|$)',
            r'degree\s+in\s+(.*?)(?:\s|,|\.|$)',
            r'engineering\s+degree\s+in\s+(.*?)(?:\s|,|\.|$)',
            r'mechanical.*?engineering',
            r'automotive.*?engineering',
            r'production.*?engineering',
            r'manufacturing.*?engineering',
            r'aerospace.*?engineering'
        ]
        
        for pattern in degree_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if match.strip():
                    qualifications.append(match.strip())
        
        # Also look for specific degree mentions
        specific_degrees = [
            'bachelor\'s degree in mechanical engineering',
            'bachelor\'s degree in automotive engineering', 
            'bachelor\'s degree in production engineering',
            'bachelor\'s degree in manufacturing engineering',
            'bachelor\'s degree in aerospace engineering',
            'master\'s degree in mechanical engineering',
            'master\'s degree in automotive engineering',
            'master\'s degree in production engineering',
            'master\'s degree in manufacturing engineering',
            'master\'s degree in aerospace engineering'
        ]
        
        for degree in specific_degrees:
            if re.search(degree, text, re.IGNORECASE):
                qualifications.append(degree)
        
        return list(set(qualifications))