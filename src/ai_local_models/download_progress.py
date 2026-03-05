import json
import time
import threading
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import logging

@dataclass
class DownloadProgress:
    """Download progress information"""
    model_name: str
    status: str  # pending, downloading, completed, failed, paused
    progress: float  # 0-100
    downloaded_bytes: int = 0
    total_bytes: int = 0
    speed: float = 0.0  # bytes per second
    eta: int = 0  # estimated time remaining in seconds
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3

class DownloadProgressTracker:
    """Tracks download progress for multiple models"""
    
    def __init__(self):
        self.progress_data: Dict[str, DownloadProgress] = {}
        self.callbacks: List[Callable] = []
        self.lock = threading.Lock()
        self.logger = logging.getLogger(__name__)
    
    def add_callback(self, callback: Callable):
        """Add a callback function to be called on progress updates"""
        self.callbacks.append(callback)
    
    def remove_callback(self, callback: Callable):
        """Remove a callback function"""
        if callback in self.callbacks:
            self.callbacks.remove(callback)
    
    def _notify_callbacks(self, model_name: str, progress: DownloadProgress):
        """Notify all registered callbacks of progress update"""
        for callback in self.callbacks:
            try:
                callback(model_name, progress)
            except Exception as e:
                self.logger.error(f"Error in progress callback: {e}")
    
    def start_download(self, model_name: str, total_bytes: int = 0):
        """Start tracking a new download"""
        with self.lock:
            progress = DownloadProgress(
                model_name=model_name,
                status="pending",
                progress=0.0,
                total_bytes=total_bytes,
                start_time=datetime.now()
            )
            self.progress_data[model_name] = progress
            self._notify_callbacks(model_name, progress)
            self.logger.info(f"Started tracking download for {model_name}")
    
    def update_progress(self, model_name: str, downloaded_bytes: int, total_bytes: int = None):
        """Update download progress"""
        with self.lock:
            if model_name not in self.progress_data:
                self.logger.warning(f"No progress tracking found for {model_name}")
                return
            
            progress = self.progress_data[model_name]
            
            if progress.status == "pending":
                progress.status = "downloading"
            
            if total_bytes:
                progress.total_bytes = total_bytes
            
            progress.downloaded_bytes = downloaded_bytes
            
            if progress.total_bytes > 0:
                progress.progress = (downloaded_bytes / progress.total_bytes) * 100
            else:
                progress.progress = 0.0
            
            # Calculate speed and ETA
            if progress.start_time:
                elapsed = (datetime.now() - progress.start_time).total_seconds()
                if elapsed > 0:
                    progress.speed = downloaded_bytes / elapsed
                    if progress.speed > 0 and progress.total_bytes > downloaded_bytes:
                        remaining_bytes = progress.total_bytes - downloaded_bytes
                        progress.eta = int(remaining_bytes / progress.speed)
            
            self._notify_callbacks(model_name, progress)
    
    def complete_download(self, model_name: str, success: bool = True, error_message: str = None):
        """Mark download as completed or failed"""
        with self.lock:
            if model_name not in self.progress_data:
                self.logger.warning(f"No progress tracking found for {model_name}")
                return
            
            progress = self.progress_data[model_name]
            progress.status = "completed" if success else "failed"
            progress.progress = 100.0 if success else progress.progress
            progress.end_time = datetime.now()
            progress.error_message = error_message
            
            if success:
                progress.downloaded_bytes = progress.total_bytes
            
            self._notify_callbacks(model_name, progress)
            
            if success:
                self.logger.info(f"Download completed for {model_name}")
            else:
                self.logger.error(f"Download failed for {model_name}: {error_message}")
    
    def pause_download(self, model_name: str):
        """Pause a download"""
        with self.lock:
            if model_name in self.progress_data:
                self.progress_data[model_name].status = "paused"
                self._notify_callbacks(model_name, self.progress_data[model_name])
                self.logger.info(f"Download paused for {model_name}")
    
    def resume_download(self, model_name: str):
        """Resume a paused download"""
        with self.lock:
            if model_name in self.progress_data:
                progress = self.progress_data[model_name]
                if progress.status == "paused":
                    progress.status = "downloading"
                    self._notify_callbacks(model_name, progress)
                    self.logger.info(f"Download resumed for {model_name}")
    
    def retry_download(self, model_name: str):
        """Retry a failed download"""
        with self.lock:
            if model_name in self.progress_data:
                progress = self.progress_data[model_name]
                if progress.status == "failed" and progress.retry_count < progress.max_retries:
                    progress.retry_count += 1
                    progress.status = "pending"
                    progress.progress = 0.0
                    progress.downloaded_bytes = 0
                    progress.start_time = datetime.now()
                    progress.end_time = None
                    progress.error_message = None
                    self._notify_callbacks(model_name, progress)
                    self.logger.info(f"Retrying download for {model_name} (attempt {progress.retry_count})")
                    return True
            return False
    
    def cancel_download(self, model_name: str):
        """Cancel a download"""
        with self.lock:
            if model_name in self.progress_data:
                progress = self.progress_data[model_name]
                progress.status = "cancelled"
                progress.end_time = datetime.now()
                self._notify_callbacks(model_name, progress)
                self.logger.info(f"Download cancelled for {model_name}")
    
    def get_progress(self, model_name: str) -> Optional[DownloadProgress]:
        """Get progress for a specific model"""
        with self.lock:
            return self.progress_data.get(model_name)
    
    def get_all_progress(self) -> Dict[str, DownloadProgress]:
        """Get progress for all models"""
        with self.lock:
            return self.progress_data.copy()
    
    def get_active_downloads(self) -> List[DownloadProgress]:
        """Get all active downloads"""
        with self.lock:
            return [
                progress for progress in self.progress_data.values()
                if progress.status in ["pending", "downloading"]
            ]
    
    def get_completed_downloads(self) -> List[DownloadProgress]:
        """Get all completed downloads"""
        with self.lock:
            return [
                progress for progress in self.progress_data.values()
                if progress.status == "completed"
            ]
    
    def get_failed_downloads(self) -> List[DownloadProgress]:
        """Get all failed downloads"""
        with self.lock:
            return [
                progress for progress in self.progress_data.values()
                if progress.status == "failed"
            ]
    
    def clear_completed(self):
        """Clear completed downloads from memory"""
        with self.lock:
            to_remove = [
                model_name for model_name, progress in self.progress_data.items()
                if progress.status in ["completed", "cancelled"]
            ]
            for model_name in to_remove:
                del self.progress_data[model_name]
    
    def clear_all(self):
        """Clear all progress data"""
        with self.lock:
            self.progress_data.clear()
    
    def to_dict(self, model_name: str = None) -> Dict:
        """Convert progress data to dictionary"""
        with self.lock:
            if model_name:
                progress = self.progress_data.get(model_name)
                return asdict(progress) if progress else None
            else:
                return {
                    name: asdict(progress) 
                    for name, progress in self.progress_data.items()
                }
    
    def get_summary(self) -> Dict:
        """Get download summary statistics"""
        with self.lock:
            total = len(self.progress_data)
            active = len([p for p in self.progress_data.values() if p.status in ["pending", "downloading"]])
            completed = len([p for p in self.progress_data.values() if p.status == "completed"])
            failed = len([p for p in self.progress_data.values() if p.status == "failed"])
            paused = len([p for p in self.progress_data.values() if p.status == "paused"])
            
            total_bytes = sum(p.total_bytes for p in self.progress_data.values())
            downloaded_bytes = sum(p.downloaded_bytes for p in self.progress_data.values())
            
            return {
                "total_downloads": total,
                "active_downloads": active,
                "completed_downloads": completed,
                "failed_downloads": failed,
                "paused_downloads": paused,
                "total_bytes": total_bytes,
                "downloaded_bytes": downloaded_bytes,
                "overall_progress": (downloaded_bytes / total_bytes * 100) if total_bytes > 0 else 0
            }


class DownloadManager:
    """Manages model downloads with progress tracking"""

    def __init__(self):
        self.download_tracker = DownloadProgressTracker()
        self.active_downloads = {}
        self.lock = threading.Lock()

    def download_model(self, model_id: str, model_name: str) -> str:
        """Start downloading a model with progress tracking"""
        try:
            from .model_downloader import ModelDownloader
            model_downloader = ModelDownloader()

            # Start progress tracking
            progress = self.download_tracker.start_download(model_name)

            def progress_callback(downloaded: int, total: int):
                self.download_tracker.update_progress(model_name, downloaded, total)

            # Start download in background thread
            def download_worker():
                try:
                    # Here you would integrate with the actual model downloader
                    # For now, simulate download progress
                    total_size = 1000000000  # 1GB
                    chunk_size = 1000000    # 1MB chunks
                    downloaded = 0

                    while downloaded < total_size:
                        time.sleep(0.1)  # Simulate network delay
                        downloaded += chunk_size
                        progress_callback(downloaded, total_size)

                    self.download_tracker.complete_download(model_name)

                except Exception as e:
                    self.download_tracker.fail_download(model_name, str(e))

            thread = threading.Thread(target=download_worker)
            thread.daemon = True
            thread.start()

            with self.lock:
                self.active_downloads[model_id] = thread

            return model_id

        except Exception as e:
            self.download_tracker.fail_download(model_name, str(e))
            raise

    def cancel_download(self, model_id: str) -> bool:
        """Cancel a download"""
        with self.lock:
            if model_id in self.active_downloads:
                # In a real implementation, you'd need to signal the download thread to stop
                self.download_tracker.cancel_download(model_id)
                return True
        return False

    def get_download_status(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a download"""
        progress = self.download_tracker.get_download_progress(model_id)
        return asdict(progress) if progress else None

    def get_all_downloads_status(self) -> List[Dict[str, Any]]:
        """Get status of all downloads"""
        downloads = self.download_tracker.get_all_downloads()
        return [asdict(progress) for progress in downloads.values()]


# Global instance
download_manager = DownloadManager()

# Global instance
progress_tracker = DownloadProgressTracker()
