import re
import math
import os
from typing import List, Tuple, Dict, Any
import logging

class EmbeddingService:
    def __init__(self):
        """Initialize the embedding service with fallback options"""
        self.logger = logging.getLogger(__name__)
        
        # Try to initialize ChromaDB, fallback to basic implementation if it fails
        self.chroma_client = None
        self.resume_collection = None
        self.jd_collection = None
        
        try:
            import chromadb
            from chromadb.config import Settings
            
            # Initialize ChromaDB
            self.chroma_client = chromadb.Client(Settings(
                chroma_db_impl="duckdb+parquet",
                persist_directory="./chroma_db"
            ))
            
            # Create collections for resumes and job descriptions
            self.resume_collection = self.chroma_client.get_or_create_collection(
                name="resumes",
                metadata={"hnsw:space": "cosine"}
            )
            self.jd_collection = self.chroma_client.get_or_create_collection(
                name="job_descriptions", 
                metadata={"hnsw:space": "cosine"}
            )
            self.logger.info("ChromaDB initialized successfully")
            
        except Exception as e:
            self.logger.warning(f"ChromaDB initialization failed: {e}")
            self.logger.info("Falling back to basic embedding service without vector store")
        
        # Initialize sentence transformer model
        self.model = None
        try:
            from sentence_transformers import SentenceTransformer
            import os
            
            # Try to use HuggingFace API key if available
            hf_token = os.getenv('HUGGINGFACE_API_KEY') or os.getenv('HUGGINGFACE_TOKEN')
            if hf_token:
                self.model = SentenceTransformer('all-MiniLM-L6-v2', use_auth_token=hf_token)
                self.logger.info("Sentence transformer model loaded successfully with HuggingFace API key")
            else:
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
                self.logger.info("Sentence transformer model loaded successfully")
        except Exception as e:
            self.logger.warning(f"Could not load sentence transformer: {e}")
            self.logger.info("Falling back to TF-IDF similarity")
        
        # Initialize sklearn for cosine similarity if available
        self.sklearn_available = False
        try:
            from sklearn.metrics.pairwise import cosine_similarity
            import numpy as np
            self.sklearn_available = True
            self.cosine_similarity = cosine_similarity
            self.np = np
        except Exception as e:
            self.logger.warning(f"scikit-learn not available: {e}")
        
        self.logger.info("EmbeddingService initialized successfully")
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate semantic similarity between two texts using sentence transformers
        
        Args:
            text1 (str): First text to compare
            text2 (str): Second text to compare
            
        Returns:
            float: Similarity score between 0 and 1
        """
        try:
            if self.model is not None:
                # Use sentence transformer embeddings
                return self._sentence_transformer_similarity(text1, text2)
            else:
                # Fallback to TF-IDF
                return self._tfidf_similarity(text1, text2)
            
        except Exception as e:
            self.logger.error(f"Error calculating similarity: {e}")
            return self._fallback_similarity(text1, text2)
    
    def _sentence_transformer_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity using sentence transformer embeddings
        """
        try:
            if not self.model:
                return self._tfidf_similarity(text1, text2)
            
            # Generate embeddings
            embeddings = self.model.encode([text1, text2])
            
            # Calculate cosine similarity
            if self.sklearn_available:
                similarity = self.cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
            else:
                # Manual cosine similarity calculation
                similarity = self._manual_cosine_similarity(embeddings[0], embeddings[1])
            
            return float(similarity)
        except Exception as e:
            self.logger.error(f"Error in sentence transformer similarity: {e}")
            return self._tfidf_similarity(text1, text2)
    
    def _manual_cosine_similarity(self, vec1, vec2) -> float:
        """Manual cosine similarity calculation"""
        try:
            if self.np:
                dot_product = self.np.dot(vec1, vec2)
                norm1 = self.np.linalg.norm(vec1)
                norm2 = self.np.linalg.norm(vec2)
                return dot_product / (norm1 * norm2)
            else:
                # Pure Python implementation
                dot_product = sum(a * b for a, b in zip(vec1, vec2))
                norm1 = math.sqrt(sum(a * a for a in vec1))
                norm2 = math.sqrt(sum(a * a for a in vec2))
                return dot_product / (norm1 * norm2)
        except Exception as e:
            self.logger.error(f"Error in manual cosine similarity: {e}")
            return 0.0
    
    def store_resume_embedding(self, resume_id: str, text: str, metadata: Dict[str, Any] = None):
        """
        Store resume text and its embedding in ChromaDB (if available)
        """
        try:
            if self.resume_collection is not None and self.model is not None:
                # Generate embedding
                embedding = self.model.encode([text])[0].tolist()
                
                # Store in ChromaDB
                self.resume_collection.add(
                    ids=[resume_id],
                    embeddings=[embedding],
                    documents=[text],
                    metadatas=[metadata or {}]
                )
                self.logger.info(f"Stored resume embedding for ID: {resume_id}")
            else:
                self.logger.info(f"ChromaDB not available, skipping resume embedding storage for ID: {resume_id}")
        except Exception as e:
            self.logger.error(f"Error storing resume embedding: {e}")
    
    def store_jd_embedding(self, jd_id: str, text: str, metadata: Dict[str, Any] = None):
        """
        Store job description text and its embedding in ChromaDB (if available)
        """
        try:
            if self.jd_collection is not None and self.model is not None:
                # Generate embedding
                embedding = self.model.encode([text])[0].tolist()
                
                # Store in ChromaDB
                self.jd_collection.add(
                    ids=[jd_id],
                    embeddings=[embedding],
                    documents=[text],
                    metadatas=[metadata or {}]
                )
                self.logger.info(f"Stored JD embedding for ID: {jd_id}")
            else:
                self.logger.info(f"ChromaDB not available, skipping JD embedding storage for ID: {jd_id}")
        except Exception as e:
            self.logger.error(f"Error storing JD embedding: {e}")
    
    def find_similar_resumes(self, jd_text: str, n_results: int = 10) -> List[Dict]:
        """
        Find similar resumes for a given job description (if ChromaDB is available)
        """
        try:
            if self.resume_collection is not None and self.model is not None:
                # Generate query embedding
                query_embedding = self.model.encode([jd_text])[0].tolist()
                
                # Search for similar resumes
                results = self.resume_collection.query(
                    query_embeddings=[query_embedding],
                    n_results=n_results
                )
                
                return results
            else:
                self.logger.info("ChromaDB not available, returning empty results for similar resume search")
                return []
        except Exception as e:
            self.logger.error(f"Error finding similar resumes: {e}")
            return []
    
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
