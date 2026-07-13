import logging
import hashlib
from typing import List, Optional
import numpy as np
from langchain_core.embeddings import Embeddings
from src.config.settings import settings

logger = logging.getLogger(__name__)

import re

class DeterministicMockEmbeddings(Embeddings):
    """
    A lightweight, high-performance mock embedding generator that runs offline.
    Uses word-level hashing (a deterministic bag-of-words representational model)
    suitable for offline similarity search tests and local validation.
    """
    def __init__(self, dimension: int = 768):
        self.dimension = dimension

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Embeds a list of documents deterministically using word term hashing.
        """
        embeddings = []
        for text in texts:
            vec = np.zeros(self.dimension)
            # Find all alphanumeric words, lowercased
            words = re.findall(r'\w+', text.lower())
            for word in words:
                # Deterministic index projection via md5 hash
                h_idx = int(hashlib.md5(word.encode('utf-8')).hexdigest(), 16) % self.dimension
                vec[h_idx] += 1.0
                
            # Normalize vector to unit length
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec = vec / norm
            else:
                # fallback vector
                vec[0] = 1.0
                
            embeddings.append(vec.tolist())
            
        return embeddings

    def embed_query(self, text: str) -> List[float]:
        """
        Embeds a single query string.
        """
        return self.embed_documents([text])[0]


class EmbeddingManager:
    """
    Orchestrator to configure, fetch, and instantiate embedding functions.
    Binds GoogleGenAIEmbeddings in production/integrated settings,
    and falls back to deterministic mock vectors in offline/testing conditions.
    """
    def __init__(self, google_api_key: Optional[str] = None):
        self.api_key = google_api_key or settings.GEMINI_API_KEY
        self.use_mock = not bool(self.api_key) or self.api_key == "your_gemini_api_key_here"
        
        self.embedder = self._initialize_embedder()

    def _initialize_embedder(self) -> Embeddings:
        if self.use_mock:
            logger.info("Initializing offline DeterministicMockEmbeddings (no GEMINI_API_KEY configured).")
            return DeterministicMockEmbeddings()
        else:
            try:
                from langchain_google_genai import GoogleGenAIEmbeddings
                logger.info("Initializing GoogleGenAIEmbeddings (models/embedding-001).")
                return GoogleGenAIEmbeddings(
                    model="models/embedding-001",
                    google_api_key=self.api_key
                )
            except Exception as e:
                logger.warning(
                    f"Failed to initialize GoogleGenAIEmbeddings (error: {e}). "
                    "Falling back to DeterministicMockEmbeddings for safety."
                )
                return DeterministicMockEmbeddings()

    def get_embeddings(self) -> Embeddings:
        """
        Returns the instantiated Embeddings instance.
        """
        return self.embedder
