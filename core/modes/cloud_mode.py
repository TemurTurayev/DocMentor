"""
Cloud mode implementation for DocMentor.
Handles cloud-based document processing and search with shared knowledge base.
"""

import logging
from pathlib import Path
from typing import List, Dict, Optional, Union
import shutil

from .base_mode import BaseMode

logger = logging.getLogger(__name__)

class CloudMode(BaseMode):
    """Cloud mode with shared document storage and processing."""

    def __init__(
        self,
        storage_path: Union[str, Path],
        cloud_endpoint: str = "",
        api_key: Optional[str] = None,
        model_name: str = "distilbert-base-multilingual-cased"
    ):
        """
        Initialize cloud mode.

        Args:
            storage_path: Local cache path
            cloud_endpoint: Cloud server endpoint URL
            api_key: API key for authentication
            model_name: Name of the transformer model to use
        """
        super().__init__(storage_path, model_name)
        self.cloud_endpoint = cloud_endpoint
        self.api_key = api_key

    def process_document(self, file_path: Union[str, Path], metadata: Optional[Dict] = None) -> Dict:
        """
        Process document in cloud mode.

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
            "mode": "cloud",
            "filename": file_path.name,
        })

        # Copy document to cloud storage cache
        doc_storage = self.storage_path / "documents" / "cloud"
        doc_storage.mkdir(parents=True, exist_ok=True)

        target_path = doc_storage / file_path.name
        if not target_path.exists():
            shutil.copy2(file_path, target_path)

        # Use local PDF processor (cloud processing can be added later)
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
                "shared": True,  # Mark as shared in cloud
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
        Search in cloud documents.

        Args:
            query: Search query
            k: Number of results to return
            filter_dict: Optional metadata filters

        Returns:
            List of relevant chunks with metadata
        """
        # Search in cloud documents
        if filter_dict is None:
            filter_dict = {}
        filter_dict["mode"] = "cloud"

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
        Get list of available cloud documents.

        Returns:
            List of document metadata
        """
        doc_storage = self.storage_path / "documents" / "cloud"
        if not doc_storage.exists():
            return []

        documents = []
        for file_path in doc_storage.glob("*.pdf"):
            try:
                doc_info = {
                    "filename": file_path.name,
                    "size": file_path.stat().st_size,
                    "mode": "cloud",
                    "shared": True
                }
                documents.append(doc_info)
            except Exception as e:
                logger.error(f"Error getting info for {file_path}: {str(e)}")
                continue

        return documents

    async def check_connection(self) -> bool:
        """
        Check connection to cloud server.

        Returns:
            True if connected, False otherwise
        """
        if not self.cloud_endpoint:
            return False

        try:
            # TODO: Implement actual cloud connection check
            # For now, return True if endpoint is configured
            return True
        except Exception as e:
            logger.error(f"Error checking cloud connection: {str(e)}")
            return False
