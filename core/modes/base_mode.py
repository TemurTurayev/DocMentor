"""
Base mode module for DocMentor.
Handles interaction between PDF converter and vector store.
"""

import logging
from pathlib import Path
from typing import List, Dict, Optional, Union
from abc import ABC, abstractmethod
import os

from ..vector_store import FAISSStore

logger = logging.getLogger(__name__)

class BaseMode(ABC):
    """Base class for DocMentor operation modes."""
    
    def __init__(
        self,
        storage_path: Union[str, Path],
        model_name: str = "distilbert-base-multilingual-cased"
    ):
        """
        Initialize base mode.
        
        Args:
            storage_path: Path to store vectors and processed documents
            model_name: Name of the transformer model to use
        """
        self.storage_path = Path(storage_path)
        self.model_name = model_name
        self.store = self._initialize_store()
        
    def _initialize_store(self) -> FAISSStore:
        """Initialize or load vector store."""
        store_path = self.storage_path / "vector_store"
        
        if store_path.exists():
            logger.info(f"Loading existing vector store from {store_path}")
            return FAISSStore.load_local(str(store_path), self.model_name)
        
        logger.info("Creating new vector store")
        store = FAISSStore(model_name=self.model_name)
        
        # Create directory if it doesn't exist
        store_path.mkdir(parents=True, exist_ok=True)
        store.save_local(str(store_path))
        
        return store
        
    @abstractmethod
    def process_document(self, file_path: Union[str, Path], metadata: Optional[Dict] = None) -> Dict:
        """Process document and add to vector store."""
        pass
        
    @abstractmethod
    def search(self, query: str, k: int = 4, filter_dict: Optional[Dict] = None) -> List[Dict]:
        """Search for relevant document chunks."""
        pass
        
    def save(self):
        """Save current state."""
        store_path = self.storage_path / "vector_store"
        self.store.save_local(str(store_path))
        logger.info(f"Saved vector store to {store_path}")