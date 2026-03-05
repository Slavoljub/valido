"""
Enhanced Local Model Manager
Main coordinator for local AI model management and operations with LLM support
"""

import os
import logging
import threading
import time
import hashlib
import requests
from typing import Dict, List, Optional, Any, Callable, Tuple
from pathlib import Path
import json
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed

from .config_manager import UnifiedConfigManager, ModelConfig
from .model_downloader import ModelDownloader
from .inference_engine import InferenceEngine
# Import from config manager instead of direct module
# local_models_config, LocalModelConfig are handled by UnifiedConfigManager

logger = logging.getLogger(__name__)

@dataclass
class ModelInfo:
    """Model information structure"""
    name: str
    model_id: str
    size_gb: float
    download_url: str
    description: str
    license: str
    requirements: Dict[str, str]
    supported_tasks: List[str]
    framework: str  # 'transformers', 'tensorflow', 'onnx', 'pytorch'
    quantization: Optional[str] = None
    local_path: Optional[str] = None
    is_downloaded: bool = False
    download_progress: float = 0.0
    model_format: str = "huggingface"  # huggingface, tensorflow, onnx, pytorch

class LocalModelManager:
    """Enhanced manager for local AI models with LLM support"""
    
    def __init__(self, 
                 models_dir: str = "src/ai_local_models",
                 download_dir: str = "cache/downloads",
                 db_path: str = "data/sqlite/sample.db"):
        
        self.models_dir = Path(models_dir)
        self.download_dir = Path(download_dir)
        self.db_path = db_path
        
        # Create directories
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.download_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.config_manager = UnifiedConfigManager()
        self.downloader = ModelDownloader(str(download_dir))
        self.inference_engine = InferenceEngine(str(models_dir))
        
        # Status tracking
        self.download_progress: Dict[str, Dict[str, Any]] = {}
        self.load_progress: Dict[str, Dict[str, Any]] = {}
        
        # Threading
        self._lock = threading.Lock()
        self._download_threads: Dict[str, threading.Thread] = {}
        self._load_threads: Dict[str, threading.Thread] = {}
        
        # LLM Models configuration
        self.available_models = self._initialize_llm_models()
    
    def _initialize_llm_models(self) -> Dict[str, ModelInfo]:
        """Initialize available LLM models configuration"""
        return {
            # Transformers/Hugging Face Models
            "llama2-7b": ModelInfo(
                name="Llama 2 7B",
                model_id="meta-llama/Llama-2-7b-chat-hf",
                size_gb=13.5,
                download_url="https://huggingface.co/meta-llama/Llama-2-7b-chat-hf",
                description="Meta's Llama 2 7B parameter model, optimized for chat",
                license="Meta License",
                requirements={"transformers": ">=4.31.0", "torch": ">=2.0.0"},
                supported_tasks=["text-generation", "chat", "question-answering"],
                framework="transformers",
                quantization="4bit"
            ),
            "llama2-13b": ModelInfo(
                name="Llama 2 13B",
                model_id="meta-llama/Llama-2-13b-chat-hf",
                size_gb=26.0,
                download_url="https://huggingface.co/meta-llama/Llama-2-13b-chat-hf",
                description="Meta's Llama 2 13B parameter model, higher quality responses",
                license="Meta License",
                requirements={"transformers": ">=4.31.0", "torch": ">=2.0.0"},
                supported_tasks=["text-generation", "chat", "question-answering"],
                framework="transformers",
                quantization="4bit"
            ),
            "mistral-7b": ModelInfo(
                name="Mistral 7B",
                model_id="mistralai/Mistral-7B-Instruct-v0.2",
                size_gb=14.0,
                download_url="https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2",
                description="Mistral AI's 7B parameter model, excellent performance",
                license="Apache 2.0",
                requirements={"transformers": ">=4.34.0", "torch": ">=2.0.0"},
                supported_tasks=["text-generation", "chat", "instruction-following"],
                framework="transformers",
                quantization="4bit"
            ),
            "phi-2": ModelInfo(
                name="Phi-2",
                model_id="microsoft/phi-2",
                size_gb=2.7,
                download_url="https://huggingface.co/microsoft/phi-2",
                description="Microsoft's Phi-2 model, small but powerful",
                license="MIT",
                requirements={"transformers": ">=4.36.0", "torch": ">=2.0.0"},
                supported_tasks=["text-generation", "code-generation", "reasoning"],
                framework="transformers",
                quantization="8bit"
            ),
            "qwen3-4b": ModelInfo(
                name="Qwen 3 4B",
                model_id="Qwen/Qwen2.5-4B-Instruct",
                size_gb=4.0,
                download_url="https://huggingface.co/Qwen/Qwen2.5-4B-Instruct",
                description="Qwen 3 4B parameter model, efficient and capable",
                license="Qwen License",
                requirements={"transformers": ">=4.37.0", "torch": ">=2.0.0"},
                supported_tasks=["text-generation", "chat", "instruction-following"],
                framework="transformers",
                quantization="4bit"
            ),
            "qwen3-7b": ModelInfo(
                name="Qwen 3 7B",
                model_id="Qwen/Qwen2.5-7B-Instruct",
                size_gb=7.0,
                download_url="https://huggingface.co/Qwen/Qwen2.5-7B-Instruct",
                description="Qwen 3 7B parameter model, higher quality",
                license="Qwen License",
                requirements={"transformers": ">=4.37.0", "torch": ">=2.0.0"},
                supported_tasks=["text-generation", "chat", "instruction-following"],
                framework="transformers",
                quantization="4bit"
            )
        }
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of all available models"""
        try:
            # Use UnifiedConfigManager instead
            local_models = self.config_manager.get_all_models()
            
            models = []
            for model in local_models:
                models.append({
                    "name": model.name,
                    "display_name": model.display_name,
                    "type": model.model_type,
                    "format": model.model_type,
                    "size": model.size_gb,
                    "description": model.description,
                    "memory_required": model.memory_required,
                    "is_downloaded": model.is_downloaded,
                    "is_loaded": model.is_loaded,
                    "local_path": model.model_path,
                    "tags": model.tags,
                    "supported_tasks": model.supported_tasks
                })
            
            return models
        except Exception as e:
            logger.error(f"Error getting available models: {e}")
            return []
    
    def get_model_info(self, model_id: str) -> Optional[ModelInfo]:
        """Get information about a specific model"""
        return self.available_models.get(model_id)
    
    def download_model(self, model_id: str, progress_callback: Optional[Callable] = None) -> bool:
        """
        Download a model asynchronously
        
        Args:
            model_name: Name of the model to download
            progress_callback: Optional callback for progress updates
            
        Returns:
            bool: True if download started successfully
        """
        try:
            with self._lock:
                if model_id in self._download_threads and self._download_threads[model_id].is_alive():
                    logger.warning(f"Download already in progress for {model_id}")
                    return False
                
                # Get model config
                model_config = self.config_manager.get_model(model_id)
                if not model_config:
                    logger.error(f"Model {model_id} not found in configuration")
                    return False
                
                # Check if already downloaded
                if model_config.is_downloaded and os.path.exists(model_config.local_path):
                    logger.info(f"Model {model_id} already downloaded")
                    return True
                
                # Initialize progress tracking
                self.download_progress[model_id] = {
                    "status": "starting",
                    "progress": 0,
                    "downloaded_bytes": 0,
                    "total_bytes": 0,
                    "start_time": time.time()
                }
                
                # Start download thread
                thread = threading.Thread(
                    target=self._download_model_thread,
                    args=(model_id, model_config, progress_callback)
                )
                thread.daemon = True
                thread.start()
                
                self._download_threads[model_id] = thread
                logger.info(f"Started download for model: {model_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error starting download for {model_id}: {e}")
            return False
    
    def _download_model_thread(self, model_id: str, model_config: ModelConfig, 
                             progress_callback: Optional[Callable]):
        """Background thread for model download"""
        try:
            with self._lock:
                self.download_progress[model_id]["status"] = "downloading"
            
            # Set up progress callback
            def progress_update(filename: str, progress: float):
                with self._lock:
                    self.download_progress[model_id]["progress"] = progress
                    if progress_callback:
                        progress_callback(model_id, progress)
            
            self.downloader.set_progress_callback(progress_update)
            
            # Download based on model format
            success = False
            if model_config.format.lower() == "gguf":
                success = self.downloader.download_with_retry(
                    model_config.download_url, 
                    model_config.local_path
                )
            elif model_config.format.lower() == "spacy":
                success = self.downloader.download_spacy_model(
                    model_id, 
                    model_config.local_path
                )
            else:
                # Try Hugging Face download
                success = self.downloader.download_huggingface_model(
                    model_id, 
                    model_config.local_path
                )
            
            with self._lock:
                if success:
                    self.download_progress[model_id]["status"] = "completed"
                    self.download_progress[model_id]["progress"] = 100
                    self.config_manager.update_model_status(model_id, is_downloaded=True)
                    logger.info(f"Successfully downloaded model: {model_id}")
                else:
                    self.download_progress[model_id]["status"] = "failed"
                    logger.error(f"Failed to download model: {model_id}")
                
                # Clean up thread reference
                if model_id in self._download_threads:
                    del self._download_threads[model_id]
                    
        except Exception as e:
            logger.error(f"Error in download thread for {model_id}: {e}")
            with self._lock:
                self.download_progress[model_id]["status"] = "failed"
                if model_id in self._download_threads:
                    del self._download_threads[model_id]
    
    def load_model(self, model_name: str, progress_callback: Optional[Callable] = None) -> bool:
        """
        Load a model into memory asynchronously
        
        Args:
            model_name: Name of the model to load
            progress_callback: Optional callback for progress updates
            
        Returns:
            bool: True if load started successfully
        """
        try:
            with self._lock:
                if model_name in self._load_threads and self._load_threads[model_name].is_alive():
                    logger.warning(f"Load already in progress for {model_name}")
                    return False
                
                # Check if model is downloaded
                model_config = self.config_manager.get_model(model_name)
                if not model_config or not model_config.is_downloaded:
                    logger.error(f"Model {model_name} not downloaded")
                    return False
                
                # Check if already loaded
                if model_name in self.inference_engine.get_loaded_models():
                    logger.info(f"Model {model_name} already loaded")
                    return True
                
                # Initialize progress tracking
                self.load_progress[model_name] = {
                    "status": "starting",
                    "progress": 0,
                    "start_time": time.time()
                }
                
                # Start load thread
                thread = threading.Thread(
                    target=self._load_model_thread,
                    args=(model_name, model_config, progress_callback)
                )
                thread.daemon = True
                thread.start()
                
                self._load_threads[model_name] = thread
                logger.info(f"Started loading model: {model_name}")
                return True
                
        except Exception as e:
            logger.error(f"Error starting load for {model_name}: {e}")
            return False
    
    def _load_model_thread(self, model_name: str, model_config: ModelConfig,
                          progress_callback: Optional[Callable]):
        """Background thread for model loading"""
        try:
            with self._lock:
                self.load_progress[model_name]["status"] = "loading"
                self.load_progress[model_name]["progress"] = 25
            
            # Load model
            success = self.inference_engine.load_model(model_name, model_config.__dict__)
            
            with self._lock:
                if success:
                    self.load_progress[model_name]["status"] = "completed"
                    self.load_progress[model_name]["progress"] = 100
                    self.config_manager.update_model_status(model_name, is_loaded=True)
                    logger.info(f"Successfully loaded model: {model_name}")
                else:
                    self.load_progress[model_name]["status"] = "failed"
                    logger.error(f"Failed to load model: {model_name}")
                
                # Clean up thread reference
                if model_name in self._load_threads:
                    del self._load_threads[model_name]
                    
        except Exception as e:
            logger.error(f"Error in load thread for {model_name}: {e}")
            with self._lock:
                self.load_progress[model_name]["status"] = "failed"
                if model_name in self._load_threads:
                    del self._load_threads[model_name]
    
    def get_download_progress(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Get download progress for a model"""
        return self.download_progress.get(model_name)
    
    def get_load_progress(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Get load progress for a model"""
        return self.load_progress.get(model_name)
    
    def generate_text(self, model_name: str, prompt: str, **kwargs) -> Optional[str]:
        """Generate text using a loaded model"""
        return self.inference_engine.generate_text(model_name, prompt, **kwargs)
    
    def chat(self, session_id: str, message: str, model_name: str = None) -> Dict[str, Any]:
        """Process a chat message"""
        # This would integrate with the enhanced chat interface
        return {"response": "Chat functionality integrated with enhanced chat interface"}
    
    def get_chat_models(self) -> List[Dict[str, Any]]:
        """Get models available for chat"""
        return self.get_available_models()
    
    def get_financial_summary(self) -> Dict[str, Any]:
        """Get financial data summary"""
        # This would integrate with the financial analyzer
        return {"summary": "Financial data available through enhanced chat interface"}
    
    def get_model_stats(self) -> Dict[str, Any]:
        """Get comprehensive model statistics"""
        try:
            config_stats = self.config_manager.get_model_stats()
            loaded_models = self.inference_engine.get_loaded_models()
            
            return {
                **config_stats,
                "currently_loaded": len(loaded_models),
                "download_progress": len(self.download_progress),
                "load_progress": len(self.load_progress),
                "active_downloads": len([t for t in self._download_threads.values() if t.is_alive()]),
                "active_loads": len([t for t in self._load_threads.values() if t.is_alive()])
            }
        except Exception as e:
            logger.error(f"Error getting model stats: {e}")
            return {}
    
    def unload_model(self, model_name: str) -> bool:
        """Unload a model from memory"""
        success = self.inference_engine.unload_model(model_name)
        if success:
            self.config_manager.update_model_status(model_name, is_loaded=False)
        return success
    
    def cleanup(self):
        """Clean up all resources"""
        try:
            # Stop all threads
            for thread in self._download_threads.values():
                if thread.is_alive():
                    thread.join(timeout=1.0)
            
            for thread in self._load_threads.values():
                if thread.is_alive():
                    thread.join(timeout=1.0)
            
            # Clean up inference engine
            self.inference_engine.cleanup()
            
            logger.info("Local model manager cleaned up successfully")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    # LLM-specific methods
    def generate_response(self, model_id: str, prompt: str, max_length: int = 1024) -> Optional[str]:
        """Generate response using LLM model"""
        try:
            model_info = self.get_model_info(model_id)
            if not model_info:
                logger.error(f"Model {model_id} not found")
                return None
            
            if not model_info.is_downloaded:
                logger.error(f"Model {model_id} not downloaded")
                return None
            
            # Use the inference engine to generate response
            return self.inference_engine.generate_text(model_id, prompt, max_length=max_length)
            
        except Exception as e:
            logger.error(f"Error generating response with {model_id}: {e}")
            return None
    
    def get_llm_models(self) -> Dict[str, ModelInfo]:
        """Get all available LLM models"""
        return self.available_models.copy()
    
    def check_model_download_status(self, model_id: str) -> bool:
        """Check if a model is downloaded"""
        model_info = self.get_model_info(model_id)
        if not model_info:
            return False
        
        # Check if model files exist
        if model_info.local_path and os.path.exists(model_info.local_path):
            model_info.is_downloaded = True
            return True
        
        return False
    
    def update_model_download_status(self):
        """Update download status for all models"""
        for model_id, model_info in self.available_models.items():
            model_info.is_downloaded = self.check_model_download_status(model_id)
    
    def get_status(self) -> Dict[str, Any]:
        """Get overall status of the model manager"""
        try:
            return {
                "models_dir": str(self.models_dir),
                "download_dir": str(self.download_dir),
                "db_path": self.db_path,
                "model_stats": self.get_model_stats(),
                "financial_summary": self.get_financial_summary(),
                "download_progress": self.download_progress,
                "load_progress": self.load_progress
            }
        except Exception as e:
            logger.error(f"Error getting status: {e}")
            return {"error": str(e)}
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information for AI models"""
        try:
            # Check GPU availability
            gpu_available = {
                'cuda': False,
                'rocm': False,
                'mps': False,
                'cpu_only': True
            }
            
            # Check PyTorch
            try:
                import torch
                if torch.cuda.is_available():
                    gpu_available['cuda'] = True
                    gpu_available['cpu_only'] = False
            except ImportError:
                pass
            
            # Check TensorFlow
            try:
                import tensorflow as tf
                tensorflow_available = True
            except ImportError:
                tensorflow_available = False
            
            # Get local models stats
            # Use config manager stats instead
            local_stats = {"total": len(self.config_manager.get_all_models())}
            
            return {
                'gpu_available': gpu_available,
                'torch_available': 'torch' in globals(),
                'tensorflow_available': tensorflow_available,
                'total_models': local_stats['total_models'],
                'downloaded_models': local_stats['downloaded_models'],
                'loaded_models': local_stats['loaded_models'],
                'total_size_gb': local_stats['total_size_gb'],
                'models_dir': local_stats['models_dir'],
                'database_path': self.db_path
            }
        except Exception as e:
            logger.error(f"Error getting system info: {e}")
            return {}
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available local models"""
        # Use UnifiedConfigManager instead
        models = []
        for model_id, model_config in self.config_manager.get_all_models().items():
            models.append({
                'name': model_config.name,
                'model_id': model_config.model_id,
                'type': model_config.type,
                'size': model_config.size,
                'is_downloaded': model_config.is_downloaded,
                'is_loaded': model_config.is_loaded,
                'description': model_config.description
            })
        return models
    
    def get_model_status(self, model_name: str) -> Dict[str, Any]:
        """Get download and usage status of a model"""
        try:
            model_config = self.config_manager.get_model_config(model_name)
            if not model_config:
                return {'name': model_name, 'status': 'not_found'}
            
            file_exists = model_config.is_downloaded
            file_size = 0
            if file_exists:
                file_path = Path(model_config.model_path)
                if file_path.exists():
                    file_size = file_path.stat().st_size
            
            return {
                'name': model_name,
                'status': 'downloaded' if file_exists else 'not_downloaded',
                'download_date': None,
                'last_used': None,
                'file_exists': file_exists,
                'file_size': file_size
            }
        except Exception as e:
            logger.error(f"Error getting model status: {e}")
            return {'name': model_name, 'status': 'error'}
    
    def download_model(self, model_name: str, progress_callback=None) -> bool:
        """Download a specific model"""
        try:
            if model_name not in self.available_models:
                logger.error(f"Model {model_name} not found in available models")
                return False
            
            model_info = self.available_models[model_name]
            
            # Check if already downloaded
            if model_info.is_downloaded and model_info.local_path and Path(model_info.local_path).exists():
                logger.info(f"Model {model_name} already downloaded")
                return True
            
            # Start download
            logger.info(f"Starting download for {model_name}")
            return self.downloader.download_model(model_name, model_info.download_url, progress_callback)
            
        except Exception as e:
            logger.error(f"Error downloading model {model_name}: {e}")
            return False
    
    def download_multiple_models(self, model_names: List[str], progress_callback=None) -> Dict[str, bool]:
        """Download multiple models"""
        results = {}
        
        for model_name in model_names:
            results[model_name] = self.download_model(model_name, progress_callback)
        
        return results

# Global instance
model_manager = LocalModelManager()
