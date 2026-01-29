"""
Relevance Engine Module
Implements hybrid scoring system combining hard and semantic matching
"""

import os
import openai
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from fuzzywuzzy import fuzz
from typing import Dict, List, Tuple
import numpy as np
import json

class RelevanceEngine:
    def __init__(self):
        # Initialize OpenAI
        openai.api_key = os.getenv('OPENAI_API_KEY')
        
        # Initialize sentence transformer for semantic similarity
        self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize TF-IDF vectorizer for hard matching
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        
        # Weights for different scoring components
        self.weights = {
            'hard_match': 0.4,
            'semantic_match': 0.4,
            'llm_reasoning': 0.2
        }
    
    def evaluate_relevance(self, resume_data: Dict, job_requirements: Dict) -> Dict:
        """Main method to evaluate resume relevance against job requirements"""
        
        # Extract text for analysis
        resume_text = resume_data.get('raw_text', '')
        job_description = job_requirements.get('description', '')
        
        # Step 1: Hard Match (Keyword and skill matching)
        hard_match_score, hard_match_details = self._calculate_hard_match_score(
            resume_data, job_requirements
        )
        
        # Step 2: Semantic Match (Embedding similarity)
        semantic_score, semantic_details = self._calculate_semantic_score(
            resume_text, job_description
        )
        
        # Step 3: LLM Reasoning (Contextual understanding)
        llm_score, llm_details = self._calculate_llm_score(
            resume_data, job_requirements
        )
        
        # Calculate weighted final score
        final_score = (
            hard_match_score * self.weights['hard_match'] +
            semantic_score * self.weights['semantic_match'] +
            llm_score * self.weights['llm_reasoning']
        )
        
        # Determine verdict
        verdict = self._determine_verdict(final_score)
        
        # Generate missing elements and feedback
        missing_elements = self._identify_missing_elements(resume_data, job_requirements)
        feedback = self._generate_feedback(resume_data, job_requirements, final_score, missing_elements)
        
        return {
            'relevance_score': round(final_score, 2),
            'hard_match_score': round(hard_match_score, 2),
            'semantic_match_score': round(semantic_score, 2),
            'llm_reasoning_score': round(llm_score, 2),
            'verdict': verdict,
            'missing_skills': missing_elements.get('skills', []),
            'missing_certifications': missing_elements.get('certifications', []),
            'missing_projects': missing_elements.get('projects', []),
            'strengths': self._identify_strengths(resume_data, job_requirements),
            'weaknesses': self._identify_weaknesses(resume_data, job_requirements),
            'improvement_suggestions': feedback.get('suggestions', ''),
            'detailed_feedback': feedback.get('detailed', ''),
            'scoring_details': {
                'hard_match': hard_match_details,
                'semantic_match': semantic_details,
                'llm_reasoning': llm_details
            }
        }
    
    def _calculate_hard_match_score(self, resume_data: Dict, job_requirements: Dict) -> Tuple[float, Dict]:
        """Calculate hard match score based on keyword and skill matching"""
        structured_resume = resume_data.get('structured_data', {})
        
        # Extract skills from resume
        resume_skills = structured_resume.get('skills', [])
        resume_skills_text = ' '.join(resume_skills).lower()
        
        # Extract requirements from job
        must_have_skills = job_requirements.get('must_have_skills', [])
        good_to_have_skills = job_requirements.get('good_to_have_skills', [])
        technical_requirements = job_requirements.get('technical_requirements', [])
        
        # Combine all required skills
        all_required_skills = must_have_skills + good_to_have_skills + technical_requirements
        required_skills_text = ' '.join(all_required_skills).lower()
        
        # Calculate TF-IDF similarity
        try:
            tfidf_matrix = self.tfidf_vectorizer.fit_transform([resume_skills_text, required_skills_text])
            tfidf_similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        except:
            tfidf_similarity = 0.0
        
        # Calculate fuzzy matching for individual skills
        skill_matches = []
        for skill in all_required_skills:
            best_match = 0
            for resume_skill in resume_skills:
                match_ratio = fuzz.ratio(skill.lower(), resume_skill.lower())
                best_match = max(best_match, match_ratio)
            skill_matches.append(best_match)
        
        # Calculate average skill match
        avg_skill_match = np.mean(skill_matches) if skill_matches else 0
        
        # Weighted combination
        hard_match_score = (tfidf_similarity * 0.6 + avg_skill_match / 100 * 0.4) * 100
        
        # Calculate match details
        matched_skills = []
        missing_skills = []
        
        for skill in must_have_skills:
            best_match = 0
            best_resume_skill = None
            for resume_skill in resume_skills:
                match_ratio = fuzz.ratio(skill.lower(), resume_skill.lower())
                if match_ratio > best_match:
                    best_match = match_ratio
                    best_resume_skill = resume_skill
            
            if best_match >= 70:  # Threshold for match
                matched_skills.append({
                    'required': skill,
                    'matched': best_resume_skill,
                    'confidence': best_match
                })
            else:
                missing_skills.append(skill)
        
        return hard_match_score, {
            'tfidf_similarity': tfidf_similarity,
            'avg_skill_match': avg_skill_match,
            'matched_skills': matched_skills,
            'missing_skills': missing_skills
        }
    
    def _calculate_semantic_score(self, resume_text: str, job_description: str) -> Tuple[float, Dict]:
        """Calculate semantic similarity using sentence embeddings"""
        try:
            # Generate embeddings
            resume_embedding = self.sentence_model.encode([resume_text])
            job_embedding = self.sentence_model.encode([job_description])
            
            # Calculate cosine similarity
            similarity = cosine_similarity(resume_embedding, job_embedding)[0][0]
            semantic_score = similarity * 100
            
            return semantic_score, {
                'similarity': similarity,
                'embedding_model': 'all-MiniLM-L6-v2'
            }
        except Exception as e:
            return 0.0, {'error': str(e)}
    
    def _calculate_llm_score(self, resume_data: Dict, job_requirements: Dict) -> Tuple[float, Dict]:
        """Calculate LLM-based reasoning score"""
        try:
            # Prepare context for LLM
            resume_summary = self._create_resume_summary(resume_data)
            job_summary = self._create_job_summary(job_requirements)
            
            prompt = f"""
            Analyze the following resume against the job requirements and provide a relevance score (0-100) and reasoning.
            
            JOB REQUIREMENTS:
            {job_summary}
            
            RESUME SUMMARY:
            {resume_summary}
            
            Please provide:
            1. A relevance score from 0-100
            2. Brief reasoning for the score
            3. Key strengths that match the job
            4. Key gaps or weaknesses
            
            Format your response as JSON:
            {{
                "score": <number>,
                "reasoning": "<text>",
                "strengths": ["<strength1>", "<strength2>"],
                "weaknesses": ["<weakness1>", "<weakness2>"]
            }}
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.3
            )
            
            # Parse LLM response
            llm_response = response.choices[0].message.content
            try:
                llm_data = json.loads(llm_response)
                score = float(llm_data.get('score', 0))
                reasoning = llm_data.get('reasoning', '')
                strengths = llm_data.get('strengths', [])
                weaknesses = llm_data.get('weaknesses', [])
            except:
                # Fallback parsing
                score = 50.0
                reasoning = llm_response
                strengths = []
                weaknesses = []
            
            return score, {
                'reasoning': reasoning,
                'strengths': strengths,
                'weaknesses': weaknesses,
                'raw_response': llm_response
            }
            
        except Exception as e:
            return 50.0, {'error': str(e)}
    
    def _create_resume_summary(self, resume_data: Dict) -> str:
        """Create a concise summary of the resume"""
        structured = resume_data.get('structured_data', {})
        
        summary_parts = []
        
        # Add personal info
        personal_info = structured.get('personal_info', {})
        if personal_info.get('name'):
            summary_parts.append(f"Name: {personal_info['name']}")
        
        # Add summary/objective
        if structured.get('summary'):
            summary_parts.append(f"Summary: {structured['summary']}")
        
        # Add experience
        experience = structured.get('experience', [])
        if experience:
            summary_parts.append(f"Experience: {len(experience)} positions")
            for exp in experience[:3]:  # Top 3 experiences
                title = exp.get('title', '')
                company = exp.get('company', '')
                if title and company:
                    summary_parts.append(f"- {title} at {company}")
        
        # Add skills
        skills = structured.get('skills', [])
        if skills:
            summary_parts.append(f"Skills: {', '.join(skills[:10])}")  # Top 10 skills
        
        # Add education
        education = structured.get('education', [])
        if education:
            summary_parts.append(f"Education: {len(education)} degrees")
            for edu in education[:2]:  # Top 2 education entries
                degree = edu.get('degree', '')
                institution = edu.get('institution', '')
                if degree and institution:
                    summary_parts.append(f"- {degree} from {institution}")
        
        return '\n'.join(summary_parts)
    
    def _create_job_summary(self, job_requirements: Dict) -> str:
        """Create a concise summary of the job requirements"""
        summary_parts = []
        
        # Add basic info
        if job_requirements.get('title'):
            summary_parts.append(f"Position: {job_requirements['title']}")
        
        if job_requirements.get('company'):
            summary_parts.append(f"Company: {job_requirements['company']}")
        
        if job_requirements.get('location'):
            summary_parts.append(f"Location: {job_requirements['location']}")
        
        # Add experience level
        if job_requirements.get('experience_level'):
            summary_parts.append(f"Experience Level: {job_requirements['experience_level']}")
        
        # Add must-have skills
        must_have = job_requirements.get('must_have_skills', [])
        if must_have:
            summary_parts.append(f"Must-have Skills: {', '.join(must_have[:10])}")
        
        # Add good-to-have skills
        good_to_have = job_requirements.get('good_to_have_skills', [])
        if good_to_have:
            summary_parts.append(f"Good-to-have Skills: {', '.join(good_to_have[:10])}")
        
        # Add technical requirements
        technical = job_requirements.get('technical_requirements', [])
        if technical:
            summary_parts.append(f"Technical Requirements: {', '.join(technical[:10])}")
        
        # Add responsibilities
        responsibilities = job_requirements.get('responsibilities', [])
        if responsibilities:
            summary_parts.append(f"Key Responsibilities: {len(responsibilities)} listed")
        
        return '\n'.join(summary_parts)
    
    def _determine_verdict(self, score: float) -> str:
        """Determine fit verdict based on score"""
        if score >= 80:
            return "High"
        elif score >= 60:
            return "Medium"
        else:
            return "Low"
    
    def _identify_missing_elements(self, resume_data: Dict, job_requirements: Dict) -> Dict:
        """Identify missing skills, certifications, and projects"""
        structured_resume = resume_data.get('structured_data', {})
        
        missing_elements = {
            'skills': [],
            'certifications': [],
            'projects': []
        }
        
        # Check missing skills
        resume_skills = [skill.lower() for skill in structured_resume.get('skills', [])]
        required_skills = job_requirements.get('must_have_skills', [])
        
        for skill in required_skills:
            skill_lower = skill.lower()
            if not any(fuzz.ratio(skill_lower, resume_skill) >= 70 for resume_skill in resume_skills):
                missing_elements['skills'].append(skill)
        
        # Check missing certifications
        resume_certs = [cert.lower() for cert in structured_resume.get('certifications', [])]
        required_certs = job_requirements.get('certifications', [])
        
        for cert in required_certs:
            cert_lower = cert.lower()
            if not any(fuzz.ratio(cert_lower, resume_cert) >= 70 for resume_cert in resume_certs):
                missing_elements['certifications'].append(cert)
        
        # Check missing project types (based on job requirements)
        resume_projects = structured_resume.get('projects', [])
        project_types = self._infer_required_project_types(job_requirements)
        
        for project_type in project_types:
            if not any(project_type.lower() in project.get('title', '').lower() or 
                      project_type.lower() in project.get('description', '').lower() 
                      for project in resume_projects):
                missing_elements['projects'].append(project_type)
        
        return missing_elements
    
    def _infer_required_project_types(self, job_requirements: Dict) -> List[str]:
        """Infer required project types from job requirements"""
        project_types = []
        
        # Analyze technical requirements to infer project types
        technical_skills = job_requirements.get('technical_requirements', [])
        
        if any('web' in skill.lower() or 'frontend' in skill.lower() for skill in technical_skills):
            project_types.append('Web Application')
        
        if any('mobile' in skill.lower() or 'android' in skill.lower() or 'ios' in skill.lower() for skill in technical_skills):
            project_types.append('Mobile Application')
        
        if any('machine learning' in skill.lower() or 'ai' in skill.lower() or 'data science' in skill.lower() for skill in technical_skills):
            project_types.append('Machine Learning Project')
        
        if any('database' in skill.lower() or 'sql' in skill.lower() for skill in technical_skills):
            project_types.append('Database Project')
        
        if any('api' in skill.lower() or 'microservice' in skill.lower() for skill in technical_skills):
            project_types.append('API Development')
        
        return project_types
    
    def _identify_strengths(self, resume_data: Dict, job_requirements: Dict) -> List[str]:
        """Identify strengths in the resume"""
        strengths = []
        structured_resume = resume_data.get('structured_data', {})
        
        # Check skill matches
        resume_skills = [skill.lower() for skill in structured_resume.get('skills', [])]
        required_skills = job_requirements.get('must_have_skills', [])
        
        matched_skills = []
        for skill in required_skills:
            if any(fuzz.ratio(skill.lower(), resume_skill) >= 70 for resume_skill in resume_skills):
                matched_skills.append(skill)
        
        if matched_skills:
            strengths.append(f"Strong technical skills: {', '.join(matched_skills[:5])}")
        
        # Check experience relevance
        experience = structured_resume.get('experience', [])
        if experience:
            strengths.append(f"Relevant work experience: {len(experience)} positions")
        
        # Check education relevance
        education = structured_resume.get('education', [])
        if education:
            strengths.append(f"Strong educational background: {len(education)} degrees")
        
        return strengths
    
    def _identify_weaknesses(self, resume_data: Dict, job_requirements: Dict) -> List[str]:
        """Identify weaknesses in the resume"""
        weaknesses = []
        structured_resume = resume_data.get('structured_data', {})
        
        # Check missing critical skills
        missing_skills = self._identify_missing_elements(resume_data, job_requirements)['skills']
        if missing_skills:
            weaknesses.append(f"Missing critical skills: {', '.join(missing_skills[:5])}")
        
        # Check experience level
        experience = structured_resume.get('experience', [])
        required_experience = job_requirements.get('experience_level', '')
        
        if required_experience in ['senior', 'lead', 'executive'] and len(experience) < 3:
            weaknesses.append("Limited work experience for senior role")
        
        # Check project diversity
        projects = structured_resume.get('projects', [])
        if len(projects) < 2:
            weaknesses.append("Limited project portfolio")
        
        return weaknesses
    
    def _generate_feedback(self, resume_data: Dict, job_requirements: Dict, score: float, missing_elements: Dict) -> Dict:
        """Generate improvement feedback"""
        suggestions = []
        
        # Skill-based suggestions
        missing_skills = missing_elements.get('skills', [])
        if missing_skills:
            suggestions.append(f"Consider learning or highlighting these skills: {', '.join(missing_skills[:3])}")
        
        # Certification suggestions
        missing_certs = missing_elements.get('certifications', [])
        if missing_certs:
            suggestions.append(f"Consider obtaining these certifications: {', '.join(missing_certs[:2])}")
        
        # Project suggestions
        missing_projects = missing_elements.get('projects', [])
        if missing_projects:
            suggestions.append(f"Consider adding projects related to: {', '.join(missing_projects[:2])}")
        
        # General suggestions based on score
        if score < 60:
            suggestions.append("Focus on gaining more relevant experience in the field")
            suggestions.append("Consider taking online courses to improve technical skills")
        elif score < 80:
            suggestions.append("Highlight your most relevant projects and achievements")
            suggestions.append("Consider obtaining industry-recognized certifications")
        
        detailed_feedback = f"""
        Based on the evaluation, your resume scored {score:.1f}/100 against this job posting.
        
        Key areas for improvement:
        {chr(10).join(f"- {suggestion}" for suggestion in suggestions)}
        
        Focus on demonstrating practical experience with the required technologies and
        consider adding specific examples of your achievements in previous roles.
        """
        
        return {
            'suggestions': '; '.join(suggestions),
            'detailed': detailed_feedback.strip()
        }
