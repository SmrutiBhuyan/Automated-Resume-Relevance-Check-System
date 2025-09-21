import os
from typing import Dict, List, Any, Optional
import logging
from dotenv import load_dotenv

load_dotenv()

# Try to import LangChain components, fallback to basic implementation if not available
try:
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import HumanMessage, SystemMessage
    from langchain_core.prompts import PromptTemplate
    import openai
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    # Create dummy classes for fallback
    class HumanMessage:
        def __init__(self, content):
            self.content = content
    class SystemMessage:
        def __init__(self, content):
            self.content = content
    class PromptTemplate:
        def __init__(self, input_variables, template):
            self.input_variables = input_variables
            self.template = template
        def format(self, **kwargs):
            return self.template.format(**kwargs)

class LLMService:
    def __init__(self):
        """Initialize LLM service with OpenAI integration"""
        self.logger = logging.getLogger(__name__)
        
        # Initialize OpenAI if available
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.llm = None
        
        if LANGCHAIN_AVAILABLE and self.api_key:
            try:
                openai.api_key = self.api_key
                self.llm = ChatOpenAI(
                    model_name="gpt-3.5-turbo",
                    temperature=0.3,
                    max_tokens=1000
                )
                self.logger.info("OpenAI LLM initialized successfully")
            except Exception as e:
                self.logger.warning(f"Failed to initialize OpenAI LLM: {e}")
                self.llm = None
        else:
            if not LANGCHAIN_AVAILABLE:
                self.logger.warning("LangChain not available. LLM features will be disabled.")
            if not self.api_key:
                self.logger.warning("OpenAI API key not found. LLM features will be disabled.")
    
    def generate_improvement_feedback(self, resume_data: Dict, jd_data: Dict, 
                                    missing_elements: Dict, final_score: float) -> str:
        """
        Generate personalized improvement feedback using LLM
        """
        if not self.llm:
            return self._generate_basic_feedback(missing_elements, final_score)
        
        try:
            # Create prompt template
            prompt_template = PromptTemplate(
                input_variables=["resume_skills", "jd_skills", "missing_skills", 
                               "missing_qualifications", "final_score", "jd_title"],
                template="""
                You are an expert career counselor helping a student improve their resume for a {jd_title} position.
                
                Resume Skills: {resume_skills}
                Required Skills: {jd_skills}
                Missing Skills: {missing_skills}
                Missing Qualifications: {missing_qualifications}
                Current Score: {final_score}/100
                
                Provide personalized, actionable feedback to help the student improve their resume. 
                Focus on:
                1. Specific skills to develop or highlight
                2. How to better align with the job requirements
                3. Practical steps to improve their application
                
                Keep the feedback encouraging but honest. Limit to 3-4 key recommendations.
                """
            )
            
            # Format the prompt
            prompt = prompt_template.format(
                resume_skills=", ".join(resume_data.get('skills', [])),
                jd_skills=", ".join(jd_data.get('must_have_skills', []) + jd_data.get('good_to_have_skills', [])),
                missing_skills=", ".join(missing_elements.get('missing_skills', [])),
                missing_qualifications=", ".join(missing_elements.get('missing_qualifications', [])),
                final_score=final_score,
                jd_title=jd_data.get('title', 'Software Engineer')
            )
            
            # Generate response
            messages = [
                SystemMessage(content="You are a helpful career counselor with expertise in resume optimization."),
                HumanMessage(content=prompt)
            ]
            
            response = self.llm.invoke(messages)
            return response.content.strip()
            
        except Exception as e:
            self.logger.error(f"Error generating LLM feedback: {e}")
            return self._generate_basic_feedback(missing_elements, final_score)
    
    def analyze_resume_strengths(self, resume_data: Dict, jd_data: Dict) -> List[str]:
        """
        Analyze and identify resume strengths using LLM
        """
        if not self.llm:
            return self._analyze_basic_strengths(resume_data, jd_data)
        
        try:
            prompt = f"""
            Analyze this resume for a {jd_data.get('title', 'Software Engineer')} position:
            
            Skills: {', '.join(resume_data.get('skills', []))}
            Education: {', '.join(resume_data.get('education', []))}
            Experience: {', '.join(resume_data.get('experience', []))}
            Projects: {', '.join(resume_data.get('projects', []))}
            
            Required Skills: {', '.join(jd_data.get('must_have_skills', []))}
            
            Identify 3-4 key strengths that make this candidate suitable for the role.
            Be specific and highlight relevant experience or skills.
            """
            
            messages = [
                SystemMessage(content="You are an expert recruiter analyzing resume strengths."),
                HumanMessage(content=prompt)
            ]
            
            response = self.llm.invoke(messages)
            # Parse response into list of strengths
            strengths = [line.strip('- ').strip() for line in response.content.split('\n') 
                        if line.strip() and not line.strip().startswith('**')]
            return strengths[:4]  # Limit to 4 strengths
            
        except Exception as e:
            self.logger.error(f"Error analyzing resume strengths: {e}")
            return self._analyze_basic_strengths(resume_data, jd_data)
    
    def generate_ats_optimization_tips(self, resume_text: str, ats_issues: List[str]) -> List[str]:
        """
        Generate ATS optimization tips using LLM
        """
        if not self.llm:
            return self._generate_basic_ats_tips(ats_issues)
        
        try:
            prompt = f"""
            This resume has the following ATS compatibility issues:
            {', '.join(ats_issues)}
            
            Provide 3-4 specific, actionable tips to make this resume more ATS-friendly.
            Focus on practical improvements that can be implemented immediately.
            """
            
            messages = [
                SystemMessage(content="You are an ATS optimization expert helping improve resume compatibility."),
                HumanMessage(content=prompt)
            ]
            
            response = self.llm.invoke(messages)
            tips = [line.strip('- ').strip() for line in response.content.split('\n') 
                   if line.strip() and not line.strip().startswith('**')]
            return tips[:4]
            
        except Exception as e:
            self.logger.error(f"Error generating ATS tips: {e}")
            return self._generate_basic_ats_tips(ats_issues)
    
    def _generate_basic_feedback(self, missing_elements: Dict, final_score: float) -> str:
        """Fallback basic feedback generation"""
        feedback = []
        
        if missing_elements.get('missing_skills'):
            feedback.append(f"Missing must-have skills: {', '.join(missing_elements['missing_skills'])}")
        
        if missing_elements.get('missing_qualifications'):
            feedback.append(f"Consider adding qualifications: {', '.join(missing_elements['missing_qualifications'])}")
        
        if final_score < 60:
            feedback.append("Consider gaining more relevant experience in the required technologies.")
        
        if not feedback:
            feedback.append("Your resume looks strong for this position!")
        
        return ' '.join(feedback)
    
    def _analyze_basic_strengths(self, resume_data: Dict, jd_data: Dict) -> List[str]:
        """Fallback basic strength analysis"""
        strengths = []
        
        # Check for matching skills
        matching_skills = set(resume_data.get('skills', [])).intersection(
            set(jd_data.get('must_have_skills', []))
        )
        if matching_skills:
            strengths.append(f"Strong technical skills: {', '.join(matching_skills)}")
        
        # Check for education
        if resume_data.get('education'):
            strengths.append("Relevant educational background")
        
        # Check for experience
        if resume_data.get('experience'):
            strengths.append("Professional experience in the field")
        
        # Check for projects
        if resume_data.get('projects'):
            strengths.append("Hands-on project experience")
        
        return strengths[:4]
    
    def _generate_basic_ats_tips(self, ats_issues: List[str]) -> List[str]:
        """Fallback basic ATS tips"""
        tips = []
        
        if "Contains tables" in ats_issues:
            tips.append("Convert tables to plain text format")
        if "Complex formatting detected" in ats_issues:
            tips.append("Use simple, clean formatting")
        if "Missing skills section" in ats_issues:
            tips.append("Add a dedicated skills section")
        if "Missing contact information" in ats_issues:
            tips.append("Include complete contact information")
        
        return tips[:4]
