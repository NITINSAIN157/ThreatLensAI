"""
ThreatLens AI - Embeddings Engine
Generates dense vector representations using Sentence Transformers on CPU,
with fallback handling for isolated/offline environments.
"""

import os
import sys
import numpy as np
from pathlib import Path
from typing import List, Union

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

class ThreatLensEmbedder:
    """CPU-optimized embedding generator for cybersecurity RAG."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        self._load_model()
        
    def _load_model(self):
        try:
            from sentence_transformers import SentenceTransformer
            # Suppress excessive huggingface downloads if local cache exists
            self.model = SentenceTransformer(self.model_name, device="cpu")
            if hasattr(self.model, "get_embedding_dimension"):
                self.embedding_dim = self.model.get_embedding_dimension()
            else:
                self.embedding_dim = self.model.get_sentence_embedding_dimension()
            print(f"Loaded SentenceTransformer '{self.model_name}' (dim={self.embedding_dim}) on CPU.")
        except Exception as e:
            print(f"Warning: Could not load SentenceTransformer ({e}). Initializing fallback embedder.")
            self.model = None
            self.embedding_dim = 384

    def encode(self, texts: Union[str, List[str]]) -> np.ndarray:
        """Encodes single string or list of strings into normalized float32 numpy arrays."""
        if isinstance(texts, str):
            texts = [texts]
            
        if self.model is not None:
            embeddings = self.model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
            return embeddings.astype(np.float32)
        else:
            # Deterministic fallback hashing embeddings for offline air-gapped environments
            embeddings = []
            for t in texts:
                np.random.seed(abs(hash(t)) % (2**32))
                vec = np.random.normal(0, 1, self.embedding_dim).astype(np.float32)
                vec /= np.linalg.norm(vec) + 1e-8
                embeddings.append(vec)
            return np.array(embeddings, dtype=np.float32)
