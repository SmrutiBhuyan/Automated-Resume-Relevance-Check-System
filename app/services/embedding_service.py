import re
import math
from typing import List, Tuple
import logging

class EmbeddingService:
    def __init__(self):
        """Initialize the embedding service"""
        self.logger = logging.getLogger(__name__)
        self.logger.info("EmbeddingService initialized successfully")
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate semantic similarity between two texts using TF-IDF and cosine similarity
        
        Args:
            text1 (str): First text to compare
            text2 (str): Second text to compare
            
        Returns:
            float: Similarity score between 0 and 1
        """
        try:
            # Use TF-IDF based similarity
            return self._tfidf_similarity(text1, text2)
            
        except Exception as e:
            self.logger.error(f"Error calculating similarity: {e}")
            return self._fallback_similarity(text1, text2)
    
    def _fallback_similarity(self, text1: str, text2: str) -> float:
        """
        Fallback similarity calculation using simple word overlap
        """
        # Convert to lowercase and split into words
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        # Calculate Jaccard similarity
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        if union == 0:
            return 0.0
        
        return intersection / union
    
    def _tfidf_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity using TF-IDF and cosine similarity
        """
        # Tokenize and clean texts
        words1 = self._tokenize(text1)
        words2 = self._tokenize(text2)
        
        if not words1 or not words2:
            return 0.0
        
        # Get all unique words
        all_words = set(words1 + words2)
        
        # Calculate term frequencies
        tf1 = {word: words1.count(word) for word in all_words}
        tf2 = {word: words2.count(word) for word in all_words}
        
        # Calculate document frequencies
        df = {}
        for word in all_words:
            df[word] = 0
            if word in words1:
                df[word] += 1
            if word in words2:
                df[word] += 1
        
        # Calculate TF-IDF vectors
        tfidf1 = []
        tfidf2 = []
        
        for word in all_words:
            # TF-IDF = TF * log(N / DF) where N is total number of documents
            idf = math.log(2 / (df[word] + 1))  # +1 to avoid division by zero
            tfidf1.append(tf1[word] * idf)
            tfidf2.append(tf2[word] * idf)
        
        # Calculate cosine similarity
        dot_product = sum(a * b for a, b in zip(tfidf1, tfidf2))
        magnitude1 = math.sqrt(sum(a * a for a in tfidf1))
        magnitude2 = math.sqrt(sum(a * a for a in tfidf2))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    def _tokenize(self, text: str) -> List[str]:
        """
        Simple tokenization - split by whitespace and remove punctuation
        """
        # Convert to lowercase and remove punctuation
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        # Split by whitespace and filter out empty strings
        return [word for word in text.split() if word]
    
    def find_most_similar(self, query_text: str, candidate_texts: List[str]) -> Tuple[int, float]:
        """
        Find the most similar text from a list of candidates
        
        Args:
            query_text (str): Query text
            candidate_texts (List[str]): List of candidate texts
            
        Returns:
            Tuple[int, float]: Index of most similar text and similarity score
        """
        if not candidate_texts:
            return -1, 0.0
        
        similarities = []
        for candidate in candidate_texts:
            similarity = self.calculate_similarity(query_text, candidate)
            similarities.append(similarity)
        
        max_idx = similarities.index(max(similarities))
        max_similarity = similarities[max_idx]
        
        return int(max_idx), float(max_similarity)
