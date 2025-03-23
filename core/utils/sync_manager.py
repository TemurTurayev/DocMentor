"""
Synchronization manager for DocMentor.
Handles data synchronization between local edge nodes and cloud server.
"""

import logging
import asyncio
import aiohttp
import json
import time
import os
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
import shutil

logger = logging.getLogger(__name__)

class SyncManager:
    """Manages synchronization between local edge nodes and cloud server."""
    
    def __init__(
        self,
        local_path: Union[str, Path],
        cloud_endpoint: str,
        api_key: Optional[str] = None,
        sync_interval: int = 3600,  # 1 hour by default
        retry_limit: int = 3,
        retry_delay: int = 30  # 30 seconds
    ):
        """
        Initialize sync manager.
        
        Args:
            local_path: Path to local storage
            cloud_endpoint: URL of the cloud server
            api_key: API key for cloud server authentication
            sync_interval: Default interval between syncs in seconds
            retry_limit: Number of retry attempts for failed operations
            retry_delay: Delay between retries in seconds
        """
        self.local_path = Path(local_path)
        self.cloud_endpoint = cloud_endpoint
        self.api_key = api_key
        self.sync_interval = sync_interval
        self.retry_limit = retry_limit
        self.retry_delay = retry_delay
        
        # Create sync directory if it doesn't exist
        self.sync_dir = self.local_path / "sync"
        self.sync_dir.mkdir(parents=True, exist_ok=True)
        
        # Last sync information file
        self.sync_info_file = self.sync_dir / "sync_info.json"
        
        # Initialize sync info
        self.sync_info = self._load_sync_info()
    
    def _load_sync_info(self) -> Dict:
        """Load sync info from file or create default."""
        if self.sync_info_file.exists():
            try:
                with open(self.sync_info_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                logger.error(f"Error parsing sync info file, creating new one")
        
        # Default sync info
        return {
            "last_sync_time": 0,
            "device_id": self._generate_device_id(),
            "synced_documents": [],
            "pending_uploads": [],
            "pending_downloads": [],
            "sync_conflicts": []
        }
    
    def _save_sync_info(self):
        """Save sync info to file."""
        with open(self.sync_info_file, 'w') as f:
            json.dump(self.sync_info, f, indent=2)
    
    def _generate_device_id(self) -> str:
        """Generate a unique device ID for this edge node."""
        # Combine hostname, a timestamp, and a random component
        import socket
        import random
        import uuid
        
        components = [
            socket.gethostname(),
            str(time.time()),
            str(random.randint(1000, 9999)),
            str(uuid.uuid4())
        ]
        
        # Hash the combined string
        device_id = hashlib.sha256(":".join(components).encode()).hexdigest()
        return device_id
    
    async def sync(self, force: bool = False) -> Dict:
        """
        Synchronize data with cloud server.
        
        Args:
            force: Force sync even if interval hasn't elapsed
            
        Returns:
            Dict with sync results
        """
        current_time = time.time()
        last_sync_time = self.sync_info["last_sync_time"]
        
        # Check if sync interval has elapsed, unless forced
        if not force and (current_time - last_sync_time) < self.sync_interval:
            logger.info(f"Sync interval not elapsed, skipping. Last sync: {last_sync_time}")
            return {
                "status": "skipped", 
                "message": f"Sync interval not elapsed. Next sync in {int(self.sync_interval - (current_time - last_sync_time))} seconds"
            }
        
        logger.info(f"Starting sync with cloud server: {self.cloud_endpoint}")
        
        try:
            # Get sync metadata from cloud
            sync_metadata = await self._get_sync_metadata()
            
            # Process pending uploads
            uploaded = await self._process_pending_uploads()
            
            # Process pending downloads
            downloaded = await self._process_pending_downloads(sync_metadata)
            
            # Check for conflicts
            conflicts = await self._check_conflicts(sync_metadata)
            
            # Update sync info
            self.sync_info["last_sync_time"] = current_time
            self._save_sync_info()
            
            return {
                "status": "success",
                "uploaded": uploaded,
                "downloaded": downloaded,
                "conflicts": conflicts,
                "timestamp": current_time
            }
        except Exception as e:
            logger.error(f"Error during sync: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def _get_sync_metadata(self) -> Dict:
        """
        Get synchronization metadata from cloud server.
        
        Returns:
            Dict with metadata about available documents and changes
        """
        device_id = self.sync_info["device_id"]
        last_sync_time = self.sync_info["last_sync_time"]
        
        async with aiohttp.ClientSession() as session:
            headers = self._get_auth_headers()
            
            for attempt in range(self.retry_limit):
                try:
                    async with session.get(
                        f"{self.cloud_endpoint}/api/sync/metadata",
                        headers=headers,
                        params={"device_id": device_id, "last_sync_time": last_sync_time}
                    ) as response:
                        if response.status == 200:
                            return await response.json()
                        else:
                            error_text = await response.text()
                            raise Exception(f"Error getting sync metadata: {response.status} - {error_text}")
                
                except Exception as e:
                    if attempt < self.retry_limit - 1:
                        logger.warning(f"Attempt {attempt + 1} failed: {str(e)}. Retrying in {self.retry_delay} seconds")
                        await asyncio.sleep(self.retry_delay)
                    else:
                        raise
        
        raise Exception("Failed to get sync metadata after multiple attempts")
    
    async def _process_pending_uploads(self) -> List[Dict]:
        """
        Process pending document uploads.
        
        Returns:
            List of successfully uploaded documents
        """
        pending_uploads = self.sync_info["pending_uploads"]
        successful_uploads = []
        
        if not pending_uploads:
            return successful_uploads
        
        logger.info(f"Processing {len(pending_uploads)} pending uploads")
        
        async with aiohttp.ClientSession() as session:
            headers = self._get_auth_headers()
            
            for upload_info in pending_uploads[:]:  # Work on a copy of the list
                file_path = Path(upload_info["file_path"])
                
                if not file_path.exists():
                    logger.warning(f"Upload file not found: {file_path}")
                    pending_uploads.remove(upload_info)
                    continue
                
                try:
                    # Prepare form data
                    form = aiohttp.FormData()
                    form.add_field('file', 
                                   open(file_path, 'rb'),
                                   filename=file_path.name,
                                   content_type='application/octet-stream')
                    
                    form.add_field('metadata', json.dumps(upload_info["metadata"]))
                    form.add_field('device_id', self.sync_info["device_id"])
                    
                    # Upload file
                    async with session.post(
                        f"{self.cloud_endpoint}/api/sync/upload",
                        headers=headers,
                        data=form
                    ) as response:
                        if response.status == 200:
                            result = await response.json()
                            successful_uploads.append({
                                "file_path": str(file_path),
                                "cloud_id": result.get("cloud_id", ""),
                                "timestamp": time.time()
                            })
                            
                            # Remove from pending uploads
                            pending_uploads.remove(upload_info)
                            logger.info(f"Successfully uploaded {file_path.name}")
                        else:
                            error_text = await response.text()
                            logger.error(f"Upload failed: {response.status} - {error_text}")
                
                except Exception as e:
                    logger.error(f"Error uploading {file_path.name}: {str(e)}")
        
        # Update sync info
        self.sync_info["pending_uploads"] = pending_uploads
        self._save_sync_info()
        
        return successful_uploads
    
    async def _process_pending_downloads(self, sync_metadata: Dict) -> List[Dict]:
        """
        Process pending document downloads.
        
        Args:
            sync_metadata: Metadata from cloud server
            
        Returns:
            List of successfully downloaded documents
        """
        available_downloads = sync_metadata.get("available_downloads", [])
        successful_downloads = []
        
        if not available_downloads:
            return successful_downloads
        
        logger.info(f"Processing {len(available_downloads)} available downloads")
        
        async with aiohttp.ClientSession() as session:
            headers = self._get_auth_headers()
            
            for download_info in available_downloads:
                cloud_id = download_info["cloud_id"]
                filename = download_info["filename"]
                target_path = self.local_path / "documents" / "cloud" / filename
                
                # Create directory if it doesn't exist
                target_path.parent.mkdir(parents=True, exist_ok=True)
                
                try:
                    async with session.get(
                        f"{self.cloud_endpoint}/api/sync/download/{cloud_id}",
                        headers=headers
                    ) as response:
                        if response.status == 200:
                            # Save file
                            with open(target_path, 'wb') as f:
                                f.write(await response.read())
                            
                            successful_downloads.append({
                                "cloud_id": cloud_id,
                                "file_path": str(target_path),
                                "metadata": download_info.get("metadata", {}),
                                "timestamp": time.time()
                            })
                            
                            logger.info(f"Successfully downloaded {filename}")
                            
                            # Acknowledge download
                            await self._acknowledge_download(cloud_id)
                        else:
                            error_text = await response.text()
                            logger.error(f"Download failed: {response.status} - {error_text}")
                
                except Exception as e:
                    logger.error(f"Error downloading {filename}: {str(e)}")
        
        # Update sync info with successful downloads
        self.sync_info["synced_documents"].extend(successful_downloads)
        self._save_sync_info()
        
        return successful_downloads
    
    async def _acknowledge_download(self, cloud_id: str) -> bool:
        """
        Acknowledge successful download to cloud server.
        
        Args:
            cloud_id: Cloud ID of the downloaded document
            
        Returns:
            Success status
        """
        async with aiohttp.ClientSession() as session:
            headers = self._get_auth_headers()
            
            try:
                async with session.post(
                    f"{self.cloud_endpoint}/api/sync/acknowledge",
                    headers=headers,
                    json={
                        "device_id": self.sync_info["device_id"],
                        "cloud_id": cloud_id,
                        "status": "downloaded"
                    }
                ) as response:
                    return response.status == 200
            except Exception as e:
                logger.error(f"Error acknowledging download: {str(e)}")
                return False
    
    async def _check_conflicts(self, sync_metadata: Dict) -> List[Dict]:
        """
        Check for conflicts between local and cloud versions.
        
        Args:
            sync_metadata: Metadata from cloud server
            
        Returns:
            List of detected conflicts
        """
        conflicts = []
        conflict_info = sync_metadata.get("conflicts", [])
        
        if not conflict_info:
            return conflicts
        
        logger.info(f"Processing {len(conflict_info)} potential conflicts")
        
        for conflict in conflict_info:
            cloud_id = conflict["cloud_id"]
            filename = conflict["filename"]
            local_path = self.local_path / "documents" / filename
            
            if local_path.exists():
                # Compare metadata
                local_metadata = await self._get_local_metadata(local_path)
                cloud_metadata = conflict.get("metadata", {})
                
                if self._is_conflicting(local_metadata, cloud_metadata):
                    conflict_record = {
                        "cloud_id": cloud_id,
                        "filename": filename,
                        "local_path": str(local_path),
                        "local_timestamp": local_metadata.get("last_modified", 0),
                        "cloud_timestamp": cloud_metadata.get("last_modified", 0),
                        "resolved": False
                    }
                    
                    conflicts.append(conflict_record)
                    
                    # Add to sync conflicts if not already there
                    if not any(c["cloud_id"] == cloud_id for c in self.sync_info["sync_conflicts"]):
                        self.sync_info["sync_conflicts"].append(conflict_record)
                        logger.warning(f"Conflict detected for {filename}")
        
        self._save_sync_info()
        return conflicts
    
    async def _get_local_metadata(self, file_path: Path) -> Dict:
        """
        Get metadata for local file.
        
        Args:
            file_path: Path to local file
            
        Returns:
            Dict with file metadata
        """
        # Basic file stats
        stats = file_path.stat()
        
        metadata = {
            "filename": file_path.name,
            "size": stats.st_size,
            "last_modified": stats.st_mtime,
            "created": stats.st_ctime
        }
        
        # Look for additional metadata file
        metadata_path = file_path.with_suffix('.metadata.json')
        
        if metadata_path.exists():
            try:
                with open(metadata_path, 'r') as f:
                    additional_metadata = json.load(f)
                    metadata.update(additional_metadata)
            except json.JSONDecodeError:
                logger.error(f"Error parsing metadata file: {metadata_path}")
        
        return metadata
    
    def _is_conflicting(self, local_metadata: Dict, cloud_metadata: Dict) -> bool:
        """
        Check if local and cloud versions are in conflict.
        
        Args:
            local_metadata: Local file metadata
            cloud_metadata: Cloud file metadata
            
        Returns:
            True if conflict detected, False otherwise
        """
        # Check if the same version
        if local_metadata.get("version") == cloud_metadata.get("version"):
            return False
        
        # Check timestamps
        local_time = local_metadata.get("last_modified", 0)
        cloud_time = cloud_metadata.get("last_modified", 0)
        
        # If either has been modified since they diverged
        if abs(local_time - cloud_time) > 60:  # More than 1 minute difference
            return True
        
        return False
    
    async def sync_document(self, file_path: Path, metadata: Dict) -> Dict:
        """
        Synchronize a specific document with cloud.
        
        Args:
            file_path: Path to document
            metadata: Document metadata
            
        Returns:
            Dict with sync result
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Add to pending uploads
        upload_info = {
            "file_path": str(file_path),
            "metadata": metadata,
            "timestamp": time.time()
        }
        
        self.sync_info["pending_uploads"].append(upload_info)
        self._save_sync_info()
        
        # Try to upload immediately
        uploaded = await self._process_pending_uploads()
        
        return {
            "status": "success" if uploaded else "pending",
            "file": str(file_path),
            "uploaded": bool(uploaded)
        }
    
    async def resolve_conflict(self, cloud_id: str, resolution: str) -> Dict:
        """
        Resolve a synchronization conflict.
        
        Args:
            cloud_id: Cloud ID of the conflicted document
            resolution: Resolution strategy ('local', 'cloud', or 'manual')
            
        Returns:
            Dict with resolution result
        """
        conflicts = self.sync_info["sync_conflicts"]
        conflict = next((c for c in conflicts if c["cloud_id"] == cloud_id), None)
        
        if not conflict:
            return {"status": "error", "message": f"Conflict not found: {cloud_id}"}
        
        filename = conflict["filename"]
        local_path = Path(conflict["local_path"])
        
        try:
            if resolution == "local":
                # Keep local version and upload to cloud
                await self.sync_document(local_path, {"resolution": "local_preferred"})
                
            elif resolution == "cloud":
                # Download cloud version
                async with aiohttp.ClientSession() as session:
                    headers = self._get_auth_headers()
                    
                    async with session.get(
                        f"{self.cloud_endpoint}/api/sync/download/{cloud_id}",
                        headers=headers
                    ) as response:
                        if response.status == 200:
                            # Create backup of local file
                            backup_path = self.sync_dir / "backups" / f"{filename}.bak"
                            backup_path.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(local_path, backup_path)
                            
                            # Replace local file
                            with open(local_path, 'wb') as f:
                                f.write(await response.read())
                                
                            # Acknowledge resolution
                            await self._acknowledge_resolution(cloud_id, "cloud_preferred")
                        else:
                            error_text = await response.text()
                            raise Exception(f"Download failed: {response.status} - {error_text}")
            
            elif resolution == "manual":
                # Download cloud version as separate file
                async with aiohttp.ClientSession() as session:
                    headers = self._get_auth_headers()
                    
                    async with session.get(
                        f"{self.cloud_endpoint}/api/sync/download/{cloud_id}",
                        headers=headers
                    ) as response:
                        if response.status == 200:
                            # Save as separate file
                            cloud_path = local_path.with_suffix(f".cloud{local_path.suffix}")
                            with open(cloud_path, 'wb') as f:
                                f.write(await response.read())
                                
                            # Mark conflict for manual resolution
                            await self._acknowledge_resolution(cloud_id, "manual_resolution")
                        else:
                            error_text = await response.text()
                            raise Exception(f"Download failed: {response.status} - {error_text}")
            else:
                return {"status": "error", "message": f"Invalid resolution strategy: {resolution}"}
            
            # Mark conflict as resolved
            conflict["resolved"] = True
            self._save_sync_info()
            
            return {
                "status": "success",
                "resolution": resolution,
                "cloud_id": cloud_id,
                "filename": filename
            }
            
        except Exception as e:
            logger.error(f"Error resolving conflict: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def _acknowledge_resolution(self, cloud_id: str, resolution: str) -> bool:
        """
        Acknowledge conflict resolution to cloud server.
        
        Args:
            cloud_id: Cloud ID of the document
            resolution: Resolution strategy applied
            
        Returns:
            Success status
        """
        async with aiohttp.ClientSession() as session:
            headers = self._get_auth_headers()
            
            try:
                async with session.post(
                    f"{self.cloud_endpoint}/api/sync/resolve",
                    headers=headers,
                    json={
                        "device_id": self.sync_info["device_id"],
                        "cloud_id": cloud_id,
                        "resolution": resolution
                    }
                ) as response:
                    return response.status == 200
            except Exception as e:
                logger.error(f"Error acknowledging resolution: {str(e)}")
                return False
    
    def get_sync_status(self) -> Dict:
        """
        Get current synchronization status.
        
        Returns:
            Dict with sync status information
        """
        return {
            "device_id": self.sync_info["device_id"],
            "last_sync_time": self.sync_info["last_sync_time"],
            "pending_uploads": len(self.sync_info["pending_uploads"]),
            "unresolved_conflicts": len([c for c in self.sync_info["sync_conflicts"] if not c.get("resolved", False)]),
            "synced_documents": len(self.sync_info["synced_documents"]),
            "cloud_endpoint": self.cloud_endpoint
        }
    
    def _get_auth_headers(self) -> Dict:
        """Get authentication headers for API requests."""
        headers = {"Content-Type": "application/json"}
        
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
            
        return headers