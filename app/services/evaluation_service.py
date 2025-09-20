from typing import Dict, Tuple
from app.services.embedding_service import EmbeddingService

class EvaluationService:
    def __init__(self):
        self.embedding_service = EmbeddingService()
    
    def evaluate_resume(self, resume_data: Dict, jd_data: Dict) -> Dict:
        """Evaluate resume against job description"""
        # Calculate keyword match score
        keyword_score = self._calculate_keyword_score(resume_data, jd_data)
        
        # Calculate semantic similarity score
        semantic_score = self._calculate_semantic_score(
            resume_data['extracted_text'], 
            jd_data['description']
        )
        
        # Calculate final weighted score
        final_score = self._calculate_final_score(keyword_score, semantic_score)
        
        # Determine missing elements
        missing_elements = self._find_missing_elements(resume_data, jd_data)
        
        # Generate verdict
        verdict = self._generate_verdict(final_score)
        
        # Generate improvement feedback
        feedback = self._generate_feedback(missing_elements, final_score)
        
        return {
            'keyword_score': keyword_score,
            'semantic_score': semantic_score,
            'final_score': final_score,
            'verdict': verdict,
            'missing_elements': missing_elements,
            'improvement_feedback': feedback
        }
    
    def _calculate_keyword_score(self, resume_data: Dict, jd_data: Dict) -> float:
        """Calculate keyword matching score"""
        total_keywords = len(jd_data['must_have_skills']) + len(jd_data['good_to_have_skills'])
        if total_keywords == 0:
            return 0.0
        
        found_must_have = sum(1 for skill in jd_data['must_have_skills'] 
                            if skill.lower() in [s.lower() for s in resume_data['skills']])
        found_good_to_have = sum(1 for skill in jd_data['good_to_have_skills'] 
                               if skill.lower() in [s.lower() for s in resume_data['skills']])
        
        # Weight must-have skills more heavily
        must_have_weight = 0.7
        good_to_have_weight = 0.3
        
        if len(jd_data['must_have_skills']) > 0:
            must_have_score = (found_must_have / len(jd_data['must_have_skills'])) * must_have_weight
        else:
            must_have_score = 0
        
        if len(jd_data['good_to_have_skills']) > 0:
            good_to_have_score = (found_good_to_have / len(jd_data['good_to_have_skills'])) * good_to_have_weight
        else:
            good_to_have_score = 0
        
        return (must_have_score + good_to_have_score) * 100
    
    def _calculate_semantic_score(self, resume_text: str, jd_text: str) -> float:
        """Calculate semantic similarity score"""
        similarity = self.embedding_service.calculate_similarity(resume_text, jd_text)
        return similarity * 100  # Convert to percentage
    
    def _calculate_final_score(self, keyword_score: float, semantic_score: float) -> float:
        """Calculate weighted final score"""
        keyword_weight = 0.6
        semantic_weight = 0.4
        
        return (keyword_score * keyword_weight) + (semantic_score * semantic_weight)
    
    def _find_missing_elements(self, resume_data: Dict, jd_data: Dict) -> Dict:
        """Find missing skills, qualifications, etc."""
        missing_skills = [
            skill for skill in jd_data['must_have_skills'] 
            if skill.lower() not in [s.lower() for s in resume_data['skills']]
        ]
        
        missing_qualifications = [
            qual for qual in jd_data['qualifications'] 
            if qual.lower() not in ' '.join(resume_data['education']).lower()
        ]
        
        return {
            'missing_skills': missing_skills,
            'missing_qualifications': missing_qualifications
        }
    
    def _generate_verdict(self, final_score: float) -> str:
        """Generate suitability verdict"""
        if final_score >= 80:
            return "High"
        elif final_score >= 60:
            return "Medium"
        else:
            return "Low"
    
    def _generate_feedback(self, missing_elements: Dict, final_score: float) -> str:
        """Generate improvement feedback"""
        feedback = []
        
        if missing_elements['missing_skills']:
            feedback.append(f"Missing must-have skills: {', '.join(missing_elements['missing_skills'])}")
        
        if missing_elements['missing_qualifications']:
            feedback.append(f"Consider adding qualifications: {', '.join(missing_elements['missing_qualifications'])}")
        
        if final_score < 60:
            feedback.append("Consider gaining more relevant experience in the required technologies.")
        
        if not feedback:
            feedback.append("Your resume looks strong for this position!")
        
        return ' '.join(feedback)