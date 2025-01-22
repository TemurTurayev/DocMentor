"""
FAISS Vector Store module for DocMentor.
Handles vector embeddings storage and similarity search.
"""

import faiss
import numpy as np
from typing import List, Dict, Optional, Tuple
import logging
from pathlib import Path
import pickle
from sentence_transformers import SentenceTransformer
import os

logger = logging.getLogger(__name__)

class FAISSStore:
    """Manages vector embeddings using FAISS."""
    
    def __init__(
        self,
        model_name: str = "distilbert-base-multilingual-cased",
        dimension: int = 768,
        index_type: str = "L2",
    ):
        """
        Initialize FAISS store.
        
        Args:
            model_name: Name of the sentence-transformer model
            dimension: Embedding dimension
            index_type: FAISS index type ("L2" or "IP" - inner product)
        """
        self.dimension = dimension
        self.model = SentenceTransformer(model_name)
        
        # Create FAISS index
        if index_type == "L2":
            self.index = faiss.IndexFlatL2(dimension)
        elif index_type == "IP":
            self.index = faiss.IndexFlatIP(dimension)
        else:
            raise ValueError(f"Unsupported index type: {index_type}")
            
        # Storage for metadata
        self.texts: List[str] = []
        self.metadata: List[Dict] = []
        
    def add_texts(
        self,
        texts: List[str],
        metadata: Optional[List[Dict]] = None,
        batch_size: int = 32
    ) -> List[int]:
        """
        Add texts and their embeddings to the store.
        
        Args:
            texts: List of text chunks to add
            metadata: Optional metadata for each text chunk
            batch_size: Batch size for embedding generation
            
        Returns:
            List of indices for added texts
        """
        if not texts:
            return []
            
        if metadata is None:
            metadata = [{} for _ in texts]
            
        if len(texts) != len(metadata):
            raise ValueError("Number of texts and metadata entries must match")
            
        # Generate embeddings in batches
        all_embeddings = []
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            embeddings = self.model.encode(batch_texts)
            all_embeddings.append(embeddings)
            
        embeddings = np.vstack(all_embeddings)
        
        # Add to FAISS index
        self.index.add(embeddings)
        
        # Store texts and metadata
        start_idx = len(self.texts)
        self.texts.extend(texts)
        self.metadata.extend(metadata)
        
        return list(range(start_idx, start_idx + len(texts)))
        
    def similarity_search(
        self,
        query: str,
        k: int = 4,
        filter_dict: Optional[Dict] = None
    ) -> List[Tuple[str, Dict, float]]:
        """
        Search for most similar texts.
        
        Args:
            query: Query text
            k: Number of results to return
            filter_dict: Optional metadata filters
            
        Returns:
            List of (text, metadata, score) tuples
        """
        # Generate query embedding
        query_embedding = self.model.encode([query])[0].reshape(1, -1)
        
        # Search in FAISS
        scores, indices = self.index.search(query_embedding, k)
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0:  # FAISS may return -1 if not enough results
                continue
                
            text = self.texts[idx]
            meta = self.metadata[idx]
            
            # Apply metadata filters
            if filter_dict is not None:
                if not all(meta.get(key) == value for key, value in filter_dict.items()):
                    continue
                    
            results.append((text, meta, float(score)))
            
        return results
        
    def save_local(self, save_dir: str):
        """
        Save the vector store to disk.
        
        Args:
            save_dir: Directory to save the store
        """
        save_dir = Path(save_dir)
        save_dir.mkdir(parents=True, exist_ok=True)
        
        # Save FAISS index
        faiss.write_index(self.index, str(save_dir / "index.faiss"))
        
        # Save texts and metadata
        with open(save_dir / "store.pkl", "wb") as f:
            pickle.dump({
                "texts": self.texts,
                "metadata": self.metadata
            }, f)
            
    @classmethod
    def load_local(
        cls,
        load_dir: str,
        model_name: str = "distilbert-base-multilingual-cased"
    ) -> "FAISSStore":
        """
        Load vector store from disk.
        
        Args:
            load_dir: Directory containing saved store
            model_name: Name of the sentence-transformer model
            
        Returns:
            Loaded FAISSStore instance
        """
        load_dir = Path(load_dir)
        
        # Create instance
        store = cls(model_name=model_name)
        
        # Load FAISS index
        store.index = faiss.read_index(str(load_dir / "index.faiss"))
        
        # Load texts and metadata
        with open(load_dir / "store.pkl", "rb") as f:
            data = pickle.load(f)
            store.texts = data["texts"]
            store.metadata = data["metadata"]
            
        return store