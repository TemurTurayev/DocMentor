"""
Local mode implementation for DocMentor.
Handles local document processing and search with offline capability.
"""

import logging
from pathlib import Path
from typing import List, Dict, Optional, Union
import shutil

from .base_mode import BaseMode

logger = logging.getLogger(__name__)

class LocalMode(BaseMode):
    """Local mode with offline document storage and processing."""

    def process_document(self, file_path: Union[str, Path], metadata: Optional[Dict] = None) -> Dict:
        """
        Process document locally and add to vector store.

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
            "mode": "local",
            "filename": file_path.name,
        })

        # Copy document to local storage
        doc_storage = self.storage_path / "documents" / "local"
        doc_storage.mkdir(parents=True, exist_ok=True)

        target_path = doc_storage / file_path.name
        if not target_path.exists():
            shutil.copy2(file_path, target_path)

        # Use local PDF processor
        try:
            from ..converter.enhanced_processor import EnhancedProcessor

            processor = EnhancedProcessor(cache_dir=str(self.storage_path / "cache"))

            # Process document synchronously
            import asyncio
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            doc_data = loop.run_until_complete(
                processor.process_document(target_path, use_cache=True)
            )

            # Extract text chunks from processed pages
            chunks = []
            for page_data in doc_data.get("pages", []):
                text = page_data.get("text", "").strip()
                if text:
                    chunks.append(text)

            if not chunks:
                raise ValueError("No text content extracted from document")

            # Update metadata with document info
            metadata.update({
                "title": doc_data.get("metadata", {}).get("title", file_path.name),
                "total_pages": len(doc_data.get("pages", [])),
                "author": doc_data.get("metadata", {}).get("author", ""),
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
        Search in local documents.

        Args:
            query: Search query
            k: Number of results to return
            filter_dict: Optional metadata filters

        Returns:
            List of relevant chunks with metadata
        """
        # Ensure we only search local documents
        if filter_dict is None:
            filter_dict = {}
        filter_dict["mode"] = "local"

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
