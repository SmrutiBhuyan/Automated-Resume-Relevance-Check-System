import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import spacy

# Download NLTK data
nltk.download('punkt')
nltk.download('stopwords')

class TextNormalizer:
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            spacy.cli.download("en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm")

    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters and digits
        text = re.sub(r'[^a-zA-Z\s]', ' ', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text

    def extract_skills(self, text: str) -> list:
        """Extract skills from text using simple pattern matching"""
        # Common technical skills patterns
        skill_patterns = [
            r'\bpython\b', r'\bjava\b', r'\bjavascript\b', r'\bhtml\b', r'\bcss\b',
            r'\breact\b', r'\bnode\.js\b', r'\bexpress\b', r'\bmongodb\b',
            r'\bsql\b', r'\bmysql\b', r'\bpostgresql\b', r'\baws\b', r'\bazure\b',
            r'\bdocker\b', r'\bkubernetes\b', r'\bgit\b', r'\bjenkins\b',
            r'\bmachine learning\b', r'\bdeep learning\b', r'\bai\b',
            r'\bdata analysis\b', r'\bdata science\b', r'\btableau\b', r'\bpower bi\b',
            r'\bpandas\b', r'\br\b', r'\bexcel\b', r'\bstatistics\b'
        ]
        
        skills = []
        for pattern in skill_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                skills.append(pattern.strip('\\b'))
        
        return list(set(skills))