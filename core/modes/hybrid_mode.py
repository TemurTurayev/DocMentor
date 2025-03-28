"""
Hybrid mode implementation for DocMentor.
Combines local and cloud functionalities for optimal performance.
"""

import logging
from pathlib import Path
from typing import List, Dict, Optional, Union, Tuple
import asyncio
import time
import os
import json

from .base_mode import BaseMode
from .local_mode import LocalMode
from .cloud_mode import CloudMode
from ..utils.sync_manager import SyncManager
from ..utils.cache_manager import CacheManager

logger = logging.getLogger(__name__)

class HybridMode(BaseMode):
    """
    Hybrid mode combining local and cloud capabilities.
    
    This mode intelligently routes queries between local and cloud processing
    based on availability, network conditions, and query complexity.
    """
    
    def __init__(
        self,
        local_storage_path: Union[str, Path],
        cloud_endpoint: str,
        api_key: Optional[str] = None,
        sync_interval: int = 3600,  # 1 hour by default
        model_name: str = "Qwen2.5-MED-3B",
        offline_mode: bool = False,
        prefer_local: bool = True,
    ):
        """
        Initialize hybrid mode.
        
        Args:
            local_storage_path: Path to local storage
            cloud_endpoint: URL of the cloud server
            api_key: API key for cloud server authentication
            sync_interval: Interval between syncs in seconds
            model_name: Name of the model to use
            offline_mode: Whether to start in offline mode
            prefer_local: Whether to prefer local processing over cloud
        """
        super().__init__(local_storage_path, model_name)
        
        # Initialize local and cloud modes
        self.local_mode = LocalMode(local_storage_path, model_name)
        self.cloud_mode = CloudMode(
            storage_path=local_storage_path,
            cloud_endpoint=cloud_endpoint,
            api_key=api_key,
            model_name=model_name
        )
        
        # Sync manager for data synchronization
        self.sync_manager = SyncManager(
            local_path=local_storage_path,
            cloud_endpoint=cloud_endpoint,
            api_key=api_key,
            sync_interval=sync_interval
        )
        
        # Cache manager for local caching
        self.cache_manager = CacheManager(str(local_storage_path / "cache"))
        
        # Configuration
        self.offline_mode = offline_mode
        self.prefer_local = prefer_local
        self.last_sync_time = 0
        self.sync_interval = sync_interval
        
        # Connection monitoring
        self.cloud_available = not offline_mode
        self.connection_check_task = None
        
        # Start background tasks if not in offline mode
        if not offline_mode:
            self._start_background_tasks()
    
    def _start_background_tasks(self):
        """Start background tasks for synchronization and monitoring."""
        loop = asyncio.get_event_loop()
        self.connection_check_task = loop.create_task(self._monitor_cloud_connection())
        loop.create_task(self._periodic_sync())
    
    async def _monitor_cloud_connection(self):
        """Continuously monitor cloud connection status."""
        while True:
            try:
                status = await self.cloud_mode.check_connection()
                self.cloud_available = status
                
                if status and self.offline_mode:
                    logger.info("Cloud connection restored, exiting offline mode")
                    self.offline_mode = False
                    # Trigger sync after reconnection
                    await self.sync_manager.sync()
                    self.last_sync_time = time.time()
                    
                elif not status and not self.offline_mode:
                    logger.warning("Cloud connection lost, entering offline mode")
                    self.offline_mode = True
                    
            except Exception as e:
                logger.error(f"Error checking cloud connection: {str(e)}")
                self.cloud_available = False
                self.offline_mode = True
                
            await asyncio.sleep(60)  # Check every minute
    
    async def _periodic_sync(self):
        """Periodically synchronize with cloud server."""
        while True:
            if self.cloud_available and not self.offline_mode:
                current_time = time.time()
                if current_time - self.last_sync_time >= self.sync_interval:
                    try:
                        logger.info("Starting periodic sync with cloud")
                        await self.sync_manager.sync()
                        self.last_sync_time = current_time
                        logger.info("Periodic sync completed successfully")
                    except Exception as e:
                        logger.error(f"Error during periodic sync: {str(e)}")
            
            await asyncio.sleep(300)  # Check every 5 minutes
    
    def process_document(self, file_path: Union[str, Path], metadata: Optional[Dict] = None) -> Dict:
        """
        Process document in hybrid mode.
        
        This method tries to process the document locally first, then syncs with cloud
        if available.
        
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
            "mode": "hybrid",
            "filename": file_path.name,
            "processed_at_local": True
        })
        
        # Process document locally
        try:
            result = self.local_mode.process_document(file_path, metadata)
            logger.info(f"Document {file_path.name} processed locally")
            
            # Schedule cloud sync if available
            if self.cloud_available and not self.offline_mode:
                asyncio.create_task(self._sync_document(file_path, metadata))
                
            return result
            
        except Exception as e:
            logger.error(f"Error processing document locally: {str(e)}")
            
            # Try cloud processing if available
            if self.cloud_available and not self.offline_mode:
                try:
                    logger.info(f"Attempting to process document {file_path.name} in cloud")
                    metadata["processed_at_local"] = False
                    return self.cloud_mode.process_document(file_path, metadata)
                except Exception as cloud_e:
                    logger.error(f"Error processing document in cloud: {str(cloud_e)}")
                    
            # Re-raise original exception if both methods fail
            raise
    
    async def _sync_document(self, file_path: Path, metadata: Dict):
        """
        Synchronize processed document with cloud.
        
        Args:
            file_path: Path to document
            metadata: Document metadata
        """
        try:
            await self.sync_manager.sync_document(file_path, metadata)
            logger.info(f"Document {file_path.name} synchronized with cloud")
        except Exception as e:
            logger.error(f"Error synchronizing document {file_path.name}: {str(e)}")
    
    def search(self, query: str, k: int = 4, filter_dict: Optional[Dict] = None) -> List[Dict]:
        """
        Search in hybrid mode.
        
        This method intelligently routes search queries between local and cloud
        based on configuration and availability.
        
        Args:
            query: Search query
            k: Number of results to return
            filter_dict: Optional metadata filters
            
        Returns:
            List of relevant chunks with metadata
        """
        if filter_dict is None:
            filter_dict = {}
            
        # Check cache first
        cache_key = self._generate_cache_key(query, k, filter_dict)
        cached_results = self.cache_manager.get(cache_key, "search_results")
        
        if cached_results:
            logger.info(f"Search results found in cache for query: {query}")
            return cached_results
        
        # Determine whether to use local or cloud search
        use_local = self.offline_mode or self.prefer_local
        
        try:
            if use_local:
                # Try local search first
                results = self.local_mode.search(query, k, filter_dict)
                
                # If results are insufficient and cloud is available, supplement with cloud results
                if len(results) < k and self.cloud_available and not self.offline_mode:
                    cloud_results = self.cloud_mode.search(query, k - len(results), filter_dict)
                    results.extend(cloud_results)
                    
                    # Deduplicate results
                    seen_texts = set()
                    unique_results = []
                    for result in results:
                        text_hash = hash(result.get("text", ""))
                        if text_hash not in seen_texts:
                            seen_texts.add(text_hash)
                            unique_results.append(result)
                    
                    results = unique_results[:k]
            else:
                # Try cloud search first if preferred and available
                if self.cloud_available and not self.offline_mode:
                    results = self.cloud_mode.search(query, k, filter_dict)
                else:
                    # Fall back to local search if cloud is unavailable
                    results = self.local_mode.search(query, k, filter_dict)
        
        except Exception as e:
            logger.error(f"Error in hybrid search: {str(e)}")
            
            # Fall back to the other mode if one fails
            if use_local:
                logger.info("Falling back to cloud search")
                if self.cloud_available and not self.offline_mode:
                    results = self.cloud_mode.search(query, k, filter_dict)
                else:
                    raise  # Re-raise if cloud is also unavailable
            else:
                logger.info("Falling back to local search")
                results = self.local_mode.search(query, k, filter_dict)
        
        # Cache successful results
        if results:
            self.cache_manager.put(cache_key, results, "search_results")
        
        return results
    
    def _generate_cache_key(self, query: str, k: int, filter_dict: Dict) -> str:
        """Generate a deterministic cache key for search queries."""
        key_parts = [query, str(k)]
        
        if filter_dict:
            # Sort filter dict items for deterministic ordering
            sorted_filters = sorted(filter_dict.items())
            for key, value in sorted_filters:
                key_parts.append(f"{key}:{value}")
                
        return self.cache_manager._compute_hash(":".join(key_parts))
    
    def toggle_offline_mode(self, offline: bool):
        """
        Toggle offline mode.
        
        Args:
            offline: Whether to enable offline mode
        """
        self.offline_mode = offline
        logger.info(f"Offline mode {'enabled' if offline else 'disabled'}")
        
        # Trigger sync when going online
        if not offline and self.cloud_available:
            asyncio.create_task(self.sync_manager.sync())
            self.last_sync_time = time.time()
    
    def toggle_prefer_local(self, prefer_local: bool):
        """
        Toggle preference for local processing.
        
        Args:
            prefer_local: Whether to prefer local processing over cloud
        """
        self.prefer_local = prefer_local
        logger.info(f"Local processing preference {'enabled' if prefer_local else 'disabled'}")
    
    async def force_sync(self) -> Dict:
        """
        Force immediate synchronization with cloud.
        
        Returns:
            Dict with sync results
        """
        if not self.cloud_available:
            return {"status": "error", "message": "Cloud server unavailable"}
            
        if self.offline_mode:
            return {"status": "error", "message": "Cannot sync in offline mode"}
            
        try:
            result = await self.sync_manager.sync(force=True)
            self.last_sync_time = time.time()
            return {"status": "success", "details": result}
        except Exception as e:
            logger.error(f"Error during forced sync: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def get_status(self) -> Dict:
        """
        Get current status of hybrid mode.
        
        Returns:
            Dict with status information
        """
        return {
            "mode": "hybrid",
            "offline_mode": self.offline_mode,
            "prefer_local": self.prefer_local,
            "cloud_available": self.cloud_available,
            "last_sync_time": self.last_sync_time,
            "local_storage": str(self.local_mode.storage_path),
            "cloud_endpoint": self.cloud_mode.cloud_endpoint
        }
    
    def clear_cache(self):
        """Clear the local cache."""
        self.cache_manager.clear()
        logger.info("Local cache cleared")
    
    def save(self):
        """Save current state of both local and cloud stores."""
        self.local_mode.save()
        
        if self.cloud_available and not self.offline_mode:
            try:
                self.cloud_mode.save()
            except Exception as e:
                logger.error(f"Error saving cloud store: {str(e)}")
                
        # Save hybrid mode configuration
        config_path = self.local_mode.storage_path / "hybrid_config.json"
        config = {
            "offline_mode": self.offline_mode,
            "prefer_local": self.prefer_local,
            "sync_interval": self.sync_interval,
            "last_sync_time": self.last_sync_time,
            "cloud_endpoint": self.cloud_mode.cloud_endpoint
        }
        
        with open(config_path, 'w') as f:
            json.dump(config, f)
            
        logger.info("Hybrid mode configuration saved")