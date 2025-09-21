from typing import Dict, List, Any, TypedDict, Annotated
import logging
from app.services.llm_service import LLMService
from app.services.embedding_service import EmbeddingService
from app.services.ats_compatibility_service import ATSCompatibilityChecker

# Try to import LangGraph, fallback to basic implementation if not available
try:
    from langgraph.graph import StateGraph, END
    from langgraph.graph.message import add_messages
    from langchain_core.messages import BaseMessage
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    # Create dummy classes for fallback
    class BaseMessage:
        pass
    def add_messages(messages):
        return messages

class EvaluationState(TypedDict):
    """State for the evaluation pipeline"""
    resume_data: Dict[str, Any]
    jd_data: Dict[str, Any]
    keyword_score: float
    semantic_score: float
    ats_score: float
    final_score: float
    verdict: str
    missing_elements: Dict[str, List[str]]
    strengths: List[str]
    improvement_feedback: str
    ats_feedback: List[str]
    messages: Annotated[List[BaseMessage], add_messages]

class EvaluationPipeline:
    def __init__(self):
        """Initialize the evaluation pipeline"""
        self.logger = logging.getLogger(__name__)
        self.llm_service = LLMService()
        self.embedding_service = EmbeddingService()
        self.ats_checker = ATSCompatibilityChecker()
        
        # Build the graph if LangGraph is available
        if LANGGRAPH_AVAILABLE:
            self.graph = self._build_graph()
            self.logger.info("Evaluation pipeline with LangGraph initialized successfully")
        else:
            self.graph = None
            self.logger.info("Evaluation pipeline initialized with basic implementation (LangGraph not available)")
    
    def _build_graph(self):
        """Build the LangGraph evaluation pipeline"""
        if not LANGGRAPH_AVAILABLE:
            return None
            
        workflow = StateGraph(EvaluationState)
        
        # Add nodes
        workflow.add_node("keyword_analysis", self._keyword_analysis)
        workflow.add_node("semantic_analysis", self._semantic_analysis)
        workflow.add_node("ats_analysis", self._ats_analysis)
        workflow.add_node("score_calculation", self._score_calculation)
        workflow.add_node("strength_analysis", self._strength_analysis)
        workflow.add_node("feedback_generation", self._feedback_generation)
        
        # Set entry point
        workflow.set_entry_point("keyword_analysis")
        
        # Add edges
        workflow.add_edge("keyword_analysis", "semantic_analysis")
        workflow.add_edge("semantic_analysis", "ats_analysis")
        workflow.add_edge("ats_analysis", "score_calculation")
        workflow.add_edge("score_calculation", "strength_analysis")
        workflow.add_edge("strength_analysis", "feedback_generation")
        workflow.add_edge("feedback_generation", END)
        
        return workflow.compile()
    
    def evaluate_resume(self, resume_data: Dict, jd_data: Dict) -> Dict:
        """
        Run the complete evaluation pipeline
        """
        try:
            if self.graph is not None and LANGGRAPH_AVAILABLE:
                # Use LangGraph pipeline
                initial_state = EvaluationState(
                    resume_data=resume_data,
                    jd_data=jd_data,
                    keyword_score=0.0,
                    semantic_score=0.0,
                    ats_score=0.0,
                    final_score=0.0,
                    verdict="",
                    missing_elements={},
                    strengths=[],
                    improvement_feedback="",
                    ats_feedback=[],
                    messages=[]
                )
                
                # Run the pipeline
                final_state = self.graph.invoke(initial_state)
                
                # Return results
                return {
                    'keyword_score': final_state['keyword_score'],
                    'semantic_score': final_state['semantic_score'],
                    'ats_score': final_state['ats_score'],
                    'final_score': final_state['final_score'],
                    'verdict': final_state['verdict'],
                    'missing_elements': final_state['missing_elements'],
                    'strengths': final_state['strengths'],
                    'improvement_feedback': final_state['improvement_feedback'],
                    'ats_feedback': final_state['ats_feedback']
                }
            else:
                # Use basic pipeline without LangGraph
                return self._basic_evaluation_pipeline(resume_data, jd_data)
            
        except Exception as e:
            self.logger.error(f"Error in evaluation pipeline: {e}")
            # Return fallback results
            return self._fallback_evaluation(resume_data, jd_data)
    
    def _basic_evaluation_pipeline(self, resume_data: Dict, jd_data: Dict) -> Dict:
        """
        Basic evaluation pipeline without LangGraph
        """
        try:
            # Initialize state
            state = {
                'resume_data': resume_data,
                'jd_data': jd_data,
                'keyword_score': 0.0,
                'semantic_score': 0.0,
                'ats_score': 0.0,
                'final_score': 0.0,
                'verdict': "",
                'missing_elements': {},
                'strengths': [],
                'improvement_feedback': "",
                'ats_feedback': []
            }
            
            # Run each step sequentially
            state = self._keyword_analysis(state)
            state = self._semantic_analysis(state)
            state = self._ats_analysis(state)
            state = self._score_calculation(state)
            state = self._strength_analysis(state)
            state = self._feedback_generation(state)
            
            # Return results
            return {
                'keyword_score': state['keyword_score'],
                'semantic_score': state['semantic_score'],
                'ats_score': state['ats_score'],
                'final_score': state['final_score'],
                'verdict': state['verdict'],
                'missing_elements': state['missing_elements'],
                'strengths': state['strengths'],
                'improvement_feedback': state['improvement_feedback'],
                'ats_feedback': state['ats_feedback']
            }
            
        except Exception as e:
            self.logger.error(f"Error in basic evaluation pipeline: {e}")
            return self._fallback_evaluation(resume_data, jd_data)
    
    def _keyword_analysis(self, state: EvaluationState) -> EvaluationState:
        """Analyze keyword matching"""
        try:
            resume_data = state['resume_data']
            jd_data = state['jd_data']
            
            # Calculate keyword score
            total_keywords = len(jd_data.get('must_have_skills', [])) + len(jd_data.get('good_to_have_skills', []))
            if total_keywords == 0:
                keyword_score = 0.0
            else:
                found_must_have = sum(1 for skill in jd_data.get('must_have_skills', []) 
                                    if skill.lower() in [s.lower() for s in resume_data.get('skills', [])])
                found_good_to_have = sum(1 for skill in jd_data.get('good_to_have_skills', []) 
                                       if skill.lower() in [s.lower() for s in resume_data.get('skills', [])])
                
                # Weight must-have skills more heavily
                must_have_weight = 0.7
                good_to_have_weight = 0.3
                
                if len(jd_data.get('must_have_skills', [])) > 0:
                    must_have_score = (found_must_have / len(jd_data['must_have_skills'])) * must_have_weight
                else:
                    must_have_score = 0
                
                if len(jd_data.get('good_to_have_skills', [])) > 0:
                    good_to_have_score = (found_good_to_have / len(jd_data['good_to_have_skills'])) * good_to_have_weight
                else:
                    good_to_have_score = 0
                
                keyword_score = (must_have_score + good_to_have_score) * 100
            
            state['keyword_score'] = keyword_score
            self.logger.info(f"Keyword analysis completed. Score: {keyword_score}")
            
        except Exception as e:
            self.logger.error(f"Error in keyword analysis: {e}")
            state['keyword_score'] = 0.0
        
        return state
    
    def _semantic_analysis(self, state: EvaluationState) -> EvaluationState:
        """Analyze semantic similarity"""
        try:
            resume_text = state['resume_data'].get('extracted_text', '')
            jd_text = state['jd_data'].get('description', '')
            
            # Calculate semantic similarity
            semantic_score = self.embedding_service.calculate_similarity(resume_text, jd_text) * 100
            
            state['semantic_score'] = semantic_score
            self.logger.info(f"Semantic analysis completed. Score: {semantic_score}")
            
        except Exception as e:
            self.logger.error(f"Error in semantic analysis: {e}")
            state['semantic_score'] = 0.0
        
        return state
    
    def _ats_analysis(self, state: EvaluationState) -> EvaluationState:
        """Analyze ATS compatibility"""
        try:
            resume_text = state['resume_data'].get('extracted_text', '')
            resume_data = state['resume_data']
            
            # Check ATS compatibility
            ats_result = self.ats_checker.check_compatibility(resume_text, resume_data)
            
            state['ats_score'] = ats_result.score
            state['ats_feedback'] = ats_result.quick_fixes
            self.logger.info(f"ATS analysis completed. Score: {ats_result.score}")
            
        except Exception as e:
            self.logger.error(f"Error in ATS analysis: {e}")
            state['ats_score'] = 0.0
            state['ats_feedback'] = []
        
        return state
    
    def _score_calculation(self, state: EvaluationState) -> EvaluationState:
        """Calculate final weighted score and verdict"""
        try:
            keyword_score = state['keyword_score']
            semantic_score = state['semantic_score']
            ats_score = state['ats_score']
            
            # Weighted scoring
            keyword_weight = 0.4
            semantic_weight = 0.4
            ats_weight = 0.2
            
            final_score = (keyword_score * keyword_weight + 
                          semantic_score * semantic_weight + 
                          ats_score * ats_weight)
            
            # Generate verdict
            if final_score >= 80:
                verdict = "High"
            elif final_score >= 60:
                verdict = "Medium"
            else:
                verdict = "Low"
            
            # Find missing elements
            missing_elements = self._find_missing_elements(
                state['resume_data'], 
                state['jd_data']
            )
            
            state['final_score'] = final_score
            state['verdict'] = verdict
            state['missing_elements'] = missing_elements
            
            self.logger.info(f"Score calculation completed. Final score: {final_score}, Verdict: {verdict}")
            
        except Exception as e:
            self.logger.error(f"Error in score calculation: {e}")
            state['final_score'] = 0.0
            state['verdict'] = "Low"
            state['missing_elements'] = {}
        
        return state
    
    def _strength_analysis(self, state: EvaluationState) -> EvaluationState:
        """Analyze resume strengths using LLM"""
        try:
            strengths = self.llm_service.analyze_resume_strengths(
                state['resume_data'], 
                state['jd_data']
            )
            state['strengths'] = strengths
            self.logger.info(f"Strength analysis completed. Found {len(strengths)} strengths")
            
        except Exception as e:
            self.logger.error(f"Error in strength analysis: {e}")
            state['strengths'] = []
        
        return state
    
    def _feedback_generation(self, state: EvaluationState) -> EvaluationState:
        """Generate improvement feedback using LLM"""
        try:
            feedback = self.llm_service.generate_improvement_feedback(
                state['resume_data'],
                state['jd_data'],
                state['missing_elements'],
                state['final_score']
            )
            state['improvement_feedback'] = feedback
            self.logger.info("Feedback generation completed")
            
        except Exception as e:
            self.logger.error(f"Error in feedback generation: {e}")
            state['improvement_feedback'] = "Unable to generate feedback at this time."
        
        return state
    
    def _find_missing_elements(self, resume_data: Dict, jd_data: Dict) -> Dict:
        """Find missing skills, qualifications, etc."""
        missing_skills = [
            skill for skill in jd_data.get('must_have_skills', []) 
            if skill.lower() not in [s.lower() for s in resume_data.get('skills', [])]
        ]
        
        missing_qualifications = [
            qual for qual in jd_data.get('qualifications', []) 
            if qual.lower() not in ' '.join(resume_data.get('education', [])).lower()
        ]
        
        return {
            'missing_skills': missing_skills,
            'missing_qualifications': missing_qualifications
        }
    
    def _fallback_evaluation(self, resume_data: Dict, jd_data: Dict) -> Dict:
        """Fallback evaluation when pipeline fails"""
        return {
            'keyword_score': 0.0,
            'semantic_score': 0.0,
            'ats_score': 0.0,
            'final_score': 0.0,
            'verdict': 'Low',
            'missing_elements': {'missing_skills': [], 'missing_qualifications': []},
            'strengths': [],
            'improvement_feedback': 'Unable to complete evaluation. Please try again.',
            'ats_feedback': []
        }
