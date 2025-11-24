"""
RAG (Retrieval-Augmented Generation) Engine for knowledge base retrieval.

Loads FAISS index and metadata, retrieves relevant chunks based on:
- Parameter being asked about
- Language preference
- User query

To modify:
- Change embedding model: Update `embedding_model_name` in config.py
- Change retrieval strategy: Modify `retrieve()` method
- Add new parameters: Ensure knowledge base chunks have correct metadata
"""

import os
import pickle
import json
from typing import List, Dict, Any, Optional
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from ..config import settings
from ..models import Language


class RAGEngine:
    """
    RAG engine for retrieving relevant knowledge base chunks.
    
    Uses FAISS for fast similarity search and filters by parameter + language.
    """
    
    def __init__(self):
        """Initialize RAG engine by loading index and embedding model."""
        self.embedding_model: Optional[SentenceTransformer] = None
        self.index: Optional[faiss.Index] = None
        self.metadata: Dict[str, Dict[str, Any]] = {}
        self._load_model()
        self._load_index()
    
    def _load_model(self) -> None:
        """Load sentence transformer model for embeddings."""
        try:
            # Use HF token if provided (for private models)
            model_kwargs = {}
            if settings.hf_token:
                model_kwargs["token"] = settings.hf_token
            
            self.embedding_model = SentenceTransformer(
                settings.embedding_model_name,
                **model_kwargs
            )
            print(f"✓ Loaded embedding model: {settings.embedding_model_name}")
        except Exception as e:
            print(f"✗ Error loading embedding model: {e}")
            raise
    
    def _load_index(self) -> None:
        """Load FAISS index and metadata from disk."""
        # Resolve paths relative to backend/ directory
        backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        embeddings_dir = os.path.join(backend_dir, settings.embeddings_dir)
        
        index_path = os.path.join(embeddings_dir, "kb_index.faiss")
        meta_path = os.path.join(embeddings_dir, "kb_index_meta.pkl")
        
        if not os.path.exists(index_path) or not os.path.exists(meta_path):
            print(f"⚠ Index files not found at {embeddings_dir}")
            print("  Run preprocessing script first to build index.")
            return
        
        try:
            self.index = faiss.read_index(index_path)
            with open(meta_path, "rb") as f:
                self.metadata = pickle.load(f)
            print(f"✓ Loaded FAISS index with {self.index.ntotal} chunks")
        except Exception as e:
            print(f"✗ Error loading index: {e}")
            # Don't raise - allow app to start without RAG (helper mode won't work)
            self.index = None
            self.metadata = {}
    
    def retrieve(
        self,
        query: str,
        parameter: str,
        language: Language,
        k: int = 4
    ) -> List[str]:
        """
        Retrieve top-k relevant chunks for a query.
        
        Args:
            query: User's question or context
            parameter: Current parameter being asked about
            language: Language preference ("hi" or "en")
            k: Number of chunks to retrieve
            
        Returns:
            List of text chunks (strings) most relevant to query
        """
        if self.index is None or self.embedding_model is None:
            return []
        
        # Embed the query
        query_embedding = self.embedding_model.encode([query], convert_to_numpy=True)
        query_embedding = query_embedding.astype('float32')
        
        # Search in FAISS
        k_actual = min(k * 3, self.index.ntotal)  # Retrieve more, then filter
        distances, indices = self.index.search(query_embedding, k_actual)
        
        # Score and filter chunks with relaxed matching
        scored_chunks = []
        
        for i, idx in enumerate(indices[0]):
            if idx < 0:  # Invalid index
                continue
            
            chunk_id = str(idx)
            chunk_meta = self.metadata.get(chunk_id, {})
            
            # Get chunk info
            chunk_param = chunk_meta.get("parameter", "").lower()
            chunk_lang = chunk_meta.get("language", "en")
            chunk_text = chunk_meta.get("text", "")
            chunk_type = chunk_meta.get("section_type", "")
            
            if not chunk_text or len(chunk_text) < 20:
                continue
            
            # Calculate relevance score
            score = 1.0 / (i + 1)  # Base score from similarity ranking
            
            # Boost for parameter match (fuzzy)
            param_keywords = {
                "color": ["color", "रंग", "colour"],
                "moisture": ["moisture", "नमी", "wet", "dry", "गीली", "सूखी"],
                "smell": ["smell", "गंध", "odor", "scent"],
                "ph": ["ph", "acid", "alkaline", "अम्ल", "क्षार"],
                "soil_type": ["soil type", "मिट्टी", "clay", "sandy", "loamy", "चिकनी", "रेतीली"],
                "earthworms": ["earthworm", "केंचुए", "worm"],
                "location": ["location", "स्थान", "place"],
                "fertilizer_used": ["fertilizer", "खाद", "manure"],
            }
            
            keywords = param_keywords.get(parameter, [parameter])
            if any(kw in chunk_param or kw in chunk_text.lower()[:100] for kw in keywords):
                score *= 2.0  # Strong boost for parameter match
            
            # Boost for "how to test" sections
            if chunk_type == "how_to_test" or "कैसे जांचें" in chunk_text or "how to" in chunk_text.lower():
                score *= 1.5
            
            # Boost for matching language
            if chunk_lang == language:
                score *= 1.3
            
            # Penalize JSON/code chunks
            if chunk_text.strip().startswith("{") or "```json" in chunk_text:
                score *= 0.1
            
            scored_chunks.append((score, chunk_text, chunk_lang))
        
        # Sort by score and return top k
        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        
        # Prefer same language but include others if needed
        same_lang_chunks = [text for score, text, lang in scored_chunks if lang == language]
        other_lang_chunks = [text for score, text, lang in scored_chunks if lang != language]
        
        result = same_lang_chunks[:k]
        if len(result) < k:
            result.extend(other_lang_chunks[:k - len(result)])
        
        return result[:k]
    
    def is_ready(self) -> bool:
        """Check if RAG engine is ready (index and model loaded)."""
        return self.index is not None and self.embedding_model is not None

