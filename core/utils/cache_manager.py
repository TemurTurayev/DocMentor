"""
Cache manager for DocMentor.
Handles caching of processed documents and embeddings.
"""

import os
import json
import hashlib
import pickle
from pathlib import Path
from typing import Any, Dict, Optional, Union
from datetime import datetime, timedelta

class CacheManager:
    def __init__(self, cache_dir: str = ".cache", max_age_days: int = 7):
        """
        Initialize cache manager.
        
        Args:
            cache_dir: Directory for cache storage
            max_age_days: Maximum age of cache entries in days
        """
        self.cache_dir = Path(cache_dir)
        self.max_age = timedelta(days=max_age_days)
        self._init_cache()
        
    def _init_cache(self) -> None:
        """Create cache directory if it doesn't exist."""
        os.makedirs(self.cache_dir / "documents", exist_ok=True)
        os.makedirs(self.cache_dir / "embeddings", exist_ok=True)
        os.makedirs(self.cache_dir / "metadata", exist_ok=True)
        
        # Initialize metadata index if needed
        self.index_path = self.cache_dir / "metadata" / "index.json"
        if not self.index_path.exists():
            self._save_index({})
            
    def _compute_hash(self, content: Union[str, bytes]) -> str:
        """
        Compute SHA-256 hash of content.
        
        Args:
            content: Content to hash (string or bytes)
            
        Returns:
            Hash string
        """
        if isinstance(content, str):
            content = content.encode()
        return hashlib.sha256(content).hexdigest()
        
    def _save_index(self, index: Dict) -> None:
        """Save metadata index to disk."""
        with open(self.index_path, 'w') as f:
            json.dump(index, f)
            
    def _load_index(self) -> Dict:
        """Load metadata index from disk."""
        with open(self.index_path, 'r') as f:
            return json.load(f)
            
    def _is_expired(self, timestamp: str) -> bool:
        """Check if cache entry has expired."""
        entry_time = datetime.fromisoformat(timestamp)
        return datetime.now() - entry_time > self.max_age
        
    def get(self, key: str, category: str = "documents") -> Optional[Any]:
        """
        Retrieve item from cache.
        
        Args:
            key: Cache key (usually file hash)
            category: Cache category (documents/embeddings)
            
        Returns:
            Cached item if found and not expired, None otherwise
        """
        index = self._load_index()
        if key not in index:
            return None
            
        entry = index[key]
        if self._is_expired(entry["timestamp"]):
            self.invalidate(key)
            return None
            
        cache_path = self.cache_dir / category / f"{key}.pkl"
        if not cache_path.exists():
            self.invalidate(key)
            return None
            
        with open(cache_path, 'rb') as f:
            return pickle.load(f)
            
    def put(self, key: str, value: Any, category: str = "documents", metadata: Dict = None) -> None:
        """
        Store item in cache.
        
        Args:
            key: Cache key (usually file hash)
            value: Item to cache
            category: Cache category (documents/embeddings)
            metadata: Additional metadata to store
        """
        # Save value
        cache_path = self.cache_dir / category / f"{key}.pkl"
        with open(cache_path, 'wb') as f:
            pickle.dump(value, f)
            
        # Update index
        index = self._load_index()
        index[key] = {
            "timestamp": datetime.now().isoformat(),
            "category": category,
            "metadata": metadata or {}
        }
        self._save_index(index)
        
    def invalidate(self, key: str) -> None:
        """
        Remove item from cache.
        
        Args:
            key: Cache key to invalidate
        """
        index = self._load_index()
        if key in index:
            entry = index[key]
            cache_path = self.cache_dir / entry["category"] / f"{key}.pkl"
            if cache_path.exists():
                os.remove(cache_path)
            del index[key]
            self._save_index(index)
            
    def clear(self) -> None:
        """Clear all cache entries."""
        for category in ["documents", "embeddings"]:
            for file in (self.cache_dir / category).glob("*.pkl"):
                os.remove(file)
        self._save_index({})
        
    def get_metadata(self, key: str) -> Optional[Dict]:
        """
        Get metadata for cached item.
        
        Args:
            key: Cache key
            
        Returns:
            Metadata dict if found, None otherwise
        """
        index = self._load_index()
        if key in index:
            return index[key]["metadata"]
        return None
        
    def update_metadata(self, key: str, metadata: Dict) -> None:
        """
        Update metadata for cached item.
        
        Args:
            key: Cache key
            metadata: New metadata dict
        """
        index = self._load_index()
        if key in index:
            index[key]["metadata"].update(metadata)
            self._save_index(index)
