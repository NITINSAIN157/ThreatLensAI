"""
ThreatLens AI - Knowledge Base Retriever
Manages vector storage (ChromaDB with In-Memory fallback) and semantic search
for cybersecurity incident response playbooks and standards.
"""

import os
import sys
import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.document_ingestion import ingest_knowledge_base
from src.embeddings import ThreatLensEmbedder

class ThreatLensRetriever:
    """Vector database and semantic search engine for ThreatLens RAG."""
    
    def __init__(self, persist_dir: str = "vector_store", collection_name: str = "threatlens_kb"):
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self.collection_name = collection_name
        self.embedder = ThreatLensEmbedder()
        self.chroma_client = None
        self.collection = None
        
        # In-memory index fallback
        self.chunks_cache: List[Dict[str, Any]] = []
        self.embeddings_cache: Optional[np.ndarray] = None
        
        self._init_vector_store()
        
    def _init_vector_store(self):
        """Initializes ChromaDB persistent client, with automatic fallback if unavailable."""
        try:
            import chromadb
            from chromadb.config import Settings
            self.chroma_client = chromadb.PersistentClient(path=str(self.persist_dir.resolve()))
            self.collection = self.chroma_client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            print(f"ChromaDB initialized at '{self.persist_dir.resolve()}' (Collection: '{self.collection_name}').")
        except Exception as e:
            print(f"Notice: Running with high-performance In-Memory Vector Store ({e}).")
            self.chroma_client = None
            self.collection = None
            
        # Check if index needs building
        if self._is_empty():
            print("Vector store is empty. Building index from knowledge_base/documents...")
            self.build_index()
        else:
            self._load_fallback_cache()

    def _is_empty(self) -> bool:
        if self.collection is not None:
            try:
                return self.collection.count() == 0
            except Exception:
                pass
        cache_file = self.persist_dir / "index_cache.json"
        return not cache_file.exists()

    def build_index(self, docs_dir: str = "knowledge_base/documents"):
        """Ingests documents, computes embeddings, and populates vector index."""
        chunks = ingest_knowledge_base(docs_dir)
        if not chunks:
            print("No documents found to index.")
            return
            
        texts = [c["text"] for c in chunks]
        print(f"Generating embeddings for {len(texts)} document chunks...")
        embeddings = self.embedder.encode(texts)
        
        # Populate ChromaDB if available
        if self.collection is not None:
            try:
                # Clear existing items
                existing = self.collection.get()
                if existing and existing.get("ids"):
                    self.collection.delete(ids=existing["ids"])
                    
                ids = [c["id"] for c in chunks]
                metadatas = [{
                    "source": c["source"],
                    "title": c["title"],
                    "section": c["section"],
                    "page": c["page"]
                } for c in chunks]
                
                self.collection.add(
                    ids=ids,
                    documents=texts,
                    embeddings=embeddings.tolist(),
                    metadatas=metadatas
                )
                print(f"Successfully indexed {len(chunks)} chunks into ChromaDB.")
            except Exception as e:
                print(f"ChromaDB indexing encountered notice ({e}). Storing in persistent cache.")
                
        # Populate persistent fallback cache
        self.chunks_cache = chunks
        self.embeddings_cache = embeddings
        
        cache_file = self.persist_dir / "index_cache.json"
        npz_file = self.persist_dir / "embeddings_cache.npz"
        
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(chunks, f, indent=2)
        np.savez_compressed(npz_file, embeddings=embeddings)
        print(f"Saved persistent vector cache to {self.persist_dir}.")

    def _load_fallback_cache(self):
        cache_file = self.persist_dir / "index_cache.json"
        npz_file = self.persist_dir / "embeddings_cache.npz"
        if cache_file.exists() and npz_file.exists():
            with open(cache_file, "r", encoding="utf-8") as f:
                self.chunks_cache = json.load(f)
            self.embeddings_cache = np.load(npz_file)["embeddings"]

    def retrieve(self, query: str, top_k: int = 4, score_threshold: float = 0.25) -> List[Dict[str, Any]]:
        """
        Retrieves top-k most relevant passages for a query with cosine similarity scores.
        """
        query_vec = self.embedder.encode(query)[0]
        results = []
        
        # 1. Try ChromaDB query
        if self.collection is not None:
            try:
                chroma_res = self.collection.query(
                    query_embeddings=[query_vec.tolist()],
                    n_results=top_k,
                    include=["documents", "metadatas", "distances"]
                )
                if chroma_res and chroma_res.get("documents") and len(chroma_res["documents"][0]) > 0:
                    for doc, meta, dist in zip(chroma_res["documents"][0], chroma_res["metadatas"][0], chroma_res["distances"][0]):
                        # In cosine space, similarity = 1 - distance
                        similarity = max(0.0, 1.0 - float(dist))
                        if similarity >= score_threshold:
                            results.append({
                                "text": doc,
                                "source": meta.get("source", "Unknown"),
                                "title": meta.get("title", "Document"),
                                "section": meta.get("section", "General"),
                                "page": meta.get("page", 1),
                                "score": round(similarity, 4)
                            })
                    if results:
                        return results
            except Exception as e:
                pass
                
        # 2. In-Memory Cosine Similarity Fallback
        if not self.chunks_cache or self.embeddings_cache is None:
            self._load_fallback_cache()
            
        if self.chunks_cache and self.embeddings_cache is not None:
            # Normalized dot product
            scores = np.dot(self.embeddings_cache, query_vec)
            top_indices = np.argsort(scores)[::-1][:top_k]
            
            for idx in top_indices:
                score = float(scores[idx])
                if score >= score_threshold:
                    c = self.chunks_cache[idx]
                    results.append({
                        "text": c["text"],
                        "source": c["source"],
                        "title": c["title"],
                        "section": c["section"],
                        "page": c.get("page", 1),
                        "score": round(score, 4)
                    })
                    
        return results

if __name__ == "__main__":
    retriever = ThreatLensRetriever()
    test_q = "What should I investigate when a network flow shows an unusual packet rate?"
    print(f"\nTest Query: '{test_q}'")
    hits = retriever.retrieve(test_q, top_k=2)
    for i, h in enumerate(hits, 1):
        print(f"\n[Result {i}] Score: {h['score']} | {h['title']} ({h['source']} - {h['section']})")
        print(h['text'][:200] + "...")
