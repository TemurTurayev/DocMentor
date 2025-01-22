"""
Public mode implementation for DocMentor.
Handles public document processing and search.
"""

import logging
from pathlib import Path
from typing import List, Dict, Optional, Union
import shutil

from .base_mode import BaseMode

logger = logging.getLogger(__name__)

class PublicMode(BaseMode):
    """Public mode with shared document storage."""
    
    def process_document(self, file_path: Union[str, Path], metadata: Optional[Dict] = None) -> Dict:
        """
        Process public document and add to vector store.
        
        Args:
            file_path: Path to PDF document
            metadata: Optional metadata for document
            
        Returns:
            Dict with processing results
        """
        file_path = Path(file_path)
        if metadata is None:
            metadata = {}
            
        # Add mode information to metadata
        metadata.update({
            "mode": "public",
            "filename": file_path.name,
        })
        
        # Copy document to public storage
        doc_storage = self.storage_path / "documents" / "public"
        doc_storage.mkdir(parents=True, exist_ok=True)
        
        target_path = doc_storage / file_path.name
        if not target_path.exists():
            shutil.copy2(file_path, target_path)
            
        # Import here to avoid circular imports
        from advanced_medical_pdf_converter import process_medical_pdf
        
        # Process document
        try:
            doc_data = process_medical_pdf(str(target_path))
            chunks = doc_data["chunks"]
            
            # Update metadata with document info
            metadata.update({
                "title": doc_data.get("title", ""),
                "total_pages": doc_data.get("total_pages", 0),
                "processed_at": doc_data.get("processed_at", ""),
            })
            
            # Add chunks to vector store
            chunk_metadata = [metadata.copy() for _ in chunks]
            self.store.add_texts(chunks, chunk_metadata)
            self.save()
            
            return {
                "status": "success",
                "chunks": len(chunks),
                "metadata": metadata
            }
            
        except Exception as e:
            logger.error(f"Error processing document {file_path}: {str(e)}")
            raise
            
    def search(self, query: str, k: int = 4, filter_dict: Optional[Dict] = None) -> List[Dict]:
        """
        Search in public documents.
        
        Args:
            query: Search query
            k: Number of results to return
            filter_dict: Optional metadata filters
            
        Returns:
            List of relevant chunks with metadata
        """
        # Ensure we only search public documents
        if filter_dict is None:
            filter_dict = {}
        filter_dict["mode"] = "public"
        
        # Perform search
        results = self.store.similarity_search(query, k=k, filter_dict=filter_dict)
        
        # Format results
        formatted_results = []
        for text, metadata, score in results:
            formatted_results.append({
                "text": text,
                "metadata": metadata,
                "score": score
            })
            
        return formatted_results
        
    def get_available_documents(self) -> List[Dict]:
        """
        Get list of available public documents.
        
        Returns:
            List of document metadata
        """
        doc_storage = self.storage_path / "documents" / "public"
        if not doc_storage.exists():
            return []
            
        documents = []
        for file_path in doc_storage.glob("*.pdf"):
            try:
                doc_info = {
                    "filename": file_path.name,
                    "size": file_path.stat().st_size,
                    "mode": "public"
                }
                documents.append(doc_info)
            except Exception as e:
                logger.error(f"Error getting info for {file_path}: {str(e)}")
                continue
                
        return documents