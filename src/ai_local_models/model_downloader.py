"""
Model Downloader
Handles downloading of AI models from various sources
"""

import os
import requests
import logging
import hashlib
from pathlib import Path
from typing import Optional, Dict, Any, Callable, List
from urllib.parse import urlparse
import zipfile
import tarfile
from tqdm import tqdm
import time

logger = logging.getLogger(__name__)

class ModelDownloader:
    """Downloads AI models from various sources"""
    
    def __init__(self, download_dir: str = "cache/downloads", max_retries: int = 3):
        self.download_dir = Path(download_dir)
        self.max_retries = max_retries
        self.download_dir.mkdir(parents=True, exist_ok=True)
        
        # Download progress callback
        self.progress_callback: Optional[Callable] = None
        
        # Standard model paths to search
        self.standard_paths = self._get_standard_model_paths()
    
    def _get_standard_model_paths(self) -> List[Path]:
        """Get standard paths where AI models are typically stored"""
        import platform
        import subprocess
        
        paths = []
        
        # Common model directories
        home = Path.home()
        
        # LM Studio paths
        if platform.system() == "Windows":
            # Windows paths
            lm_studio_paths = [
                home / "AppData" / "Local" / "LM Studio" / "models",
                home / "AppData" / "Roaming" / "LM Studio" / "models",
                Path("C:/LM Studio/models"),
                Path("D:/LM Studio/models")
            ]
        elif platform.system() == "Darwin":  # macOS
            lm_studio_paths = [
                home / "Library" / "Application Support" / "LM Studio" / "models",
                home / "Documents" / "LM Studio" / "models"
            ]
        else:  # Linux
            lm_studio_paths = [
                home / ".local" / "share" / "lm-studio" / "models",
                home / ".config" / "lm-studio" / "models",
                home / "Documents" / "LM Studio" / "models"
            ]
        
        # Ollama paths with detection
        ollama_paths = []
        
        # Check if Ollama is installed and get its model path
        try:
            result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                # Ollama is installed, get its model directory
                if platform.system() == "Windows":
                    ollama_paths = [
                        home / ".ollama" / "models",
                        Path("C:/ollama/models")
                    ]
                elif platform.system() == "Darwin":  # macOS
                    ollama_paths = [
                        home / ".ollama" / "models",
                        Path("/usr/local/share/ollama/models")
                    ]
                else:  # Linux
                    ollama_paths = [
                        home / ".ollama" / "models",
                        Path("/usr/local/share/ollama/models"),
                        Path("/opt/ollama/models")
                    ]
                logger.info("Ollama detected and available")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            # Fallback to common Ollama paths
            ollama_paths = [
                home / ".ollama" / "models",
                Path("/usr/local/share/ollama/models"),
                Path("/opt/ollama/models")
            ]
        
        # Hugging Face cache
        hf_cache_paths = [
            home / ".cache" / "huggingface" / "hub",
            home / ".huggingface" / "cache"
        ]
        
        # Local project paths
        local_paths = [
            Path("local_llm_models"),
            Path("models"),
            Path("ai_models"),
            Path("cache/models")
        ]
        
        # Combine all paths
        all_paths = lm_studio_paths + ollama_paths + hf_cache_paths + local_paths
        
        # Filter to only existing directories
        for path in all_paths:
            if path.exists() and path.is_dir():
                paths.append(path)
                logger.info(f"Found model directory: {path}")
        
        return paths
    
    def set_progress_callback(self, callback: Callable):
        """Set callback for download progress updates"""
        self.progress_callback = callback
    
    def download_file(self, url: str, destination: str, chunk_size: int = 8192) -> bool:
        """
        Download a file with progress tracking
        
        Args:
            url: URL to download from
            destination: Local file path
            chunk_size: Size of chunks to download
            
        Returns:
            bool: True if download successful
        """
        try:
            # Create destination directory
            dest_path = Path(destination)
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Start download
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            # Get file size for progress tracking
            total_size = int(response.headers.get('content-length', 0))
            
            # Download with progress bar
            with open(destination, 'wb') as f:
                downloaded = 0
                with tqdm(total=total_size, unit='B', unit_scale=True, desc=dest_path.name) as pbar:
                    for chunk in response.iter_content(chunk_size=chunk_size):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            pbar.update(len(chunk))
                            
                            # Call progress callback if set
                            if self.progress_callback and total_size > 0:
                                progress = (downloaded / total_size) * 100
                                self.progress_callback(dest_path.name, progress)
            
            logger.info(f"Successfully downloaded {url} to {destination}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to download {url}: {e}")
            return False
    
    def download_with_retry(self, url: str, destination: str) -> bool:
        """Download with retry logic"""
        for attempt in range(self.max_retries):
            try:
                if self.download_file(url, destination):
                    return True
                logger.warning(f"Download attempt {attempt + 1} failed, retrying...")
                time.sleep(2 ** attempt)  # Exponential backoff
            except Exception as e:
                logger.error(f"Download attempt {attempt + 1} failed: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
        
        return False
    
    def download_huggingface_model(self, model_name: str, local_path: str, 
                                 token: Optional[str] = None) -> bool:
        """
        Download a model from Hugging Face
        
        Args:
            model_name: Hugging Face model name (e.g., "TheBloke/Llama-2-7B-Chat-GGUF")
            local_path: Local path to save the model
            token: Hugging Face token (optional)
            
        Returns:
            bool: True if download successful
        """
        try:
            # Create local directory
            local_dir = Path(local_path).parent
            local_dir.mkdir(parents=True, exist_ok=True)
            
            # For GGUF models, we need to find the model file
            if "gguf" in model_name.lower():
                return self._download_gguf_model(model_name, local_path, token)
            else:
                return self._download_huggingface_files(model_name, local_path, token)
                
        except Exception as e:
            logger.error(f"Failed to download Hugging Face model {model_name}: {e}")
            return False
    
    def _download_gguf_model(self, model_name: str, local_path: str, 
                           token: Optional[str] = None) -> bool:
        """Download a GGUF model file"""
        try:
            # Common GGUF file patterns
            gguf_patterns = [
                "*.gguf",
                "*Q4_K_M.gguf",
                "*Q5_K_M.gguf",
                "*Q8_0.gguf"
            ]
            
            # Try to find the model file
            for pattern in gguf_patterns:
                url = f"https://huggingface.co/{model_name}/resolve/main/{pattern}"
                if self.download_with_retry(url, local_path):
                    return True
            
            # If no specific pattern works, try to list files
            return self._download_from_hf_listing(model_name, local_path, token)
            
        except Exception as e:
            logger.error(f"Failed to download GGUF model {model_name}: {e}")
            return False
    
    def _download_from_hf_listing(self, model_name: str, local_path: str,
                                token: Optional[str] = None) -> bool:
        """Download by listing files from Hugging Face"""
        try:
            # Get model files listing
            headers = {}
            if token:
                headers["Authorization"] = f"Bearer {token}"
            
            api_url = f"https://huggingface.co/api/models/{model_name}/tree/main"
            response = requests.get(api_url, headers=headers)
            response.raise_for_status()
            
            files = response.json()
            
            # Find GGUF files
            gguf_files = [f for f in files if f.get('path', '').endswith('.gguf')]
            
            if not gguf_files:
                logger.error(f"No GGUF files found in {model_name}")
                return False
            
            # Download the first GGUF file (usually the main model)
            file_info = gguf_files[0]
            file_url = f"https://huggingface.co/{model_name}/resolve/main/{file_info['path']}"
            
            return self.download_with_retry(file_url, local_path)
            
        except Exception as e:
            logger.error(f"Failed to get file listing for {model_name}: {e}")
            return False
    
    def _download_huggingface_files(self, model_name: str, local_path: str,
                                  token: Optional[str] = None) -> bool:
        """Download all files from a Hugging Face model"""
        try:
            # This would require more complex logic to download all model files
            # For now, we'll use a simpler approach
            logger.warning(f"Full Hugging Face model download not implemented for {model_name}")
            return False
            
        except Exception as e:
            logger.error(f"Failed to download Hugging Face files for {model_name}: {e}")
            return False
    
    def download_spacy_model(self, model_name: str, local_path: str) -> bool:
        """Download a SpaCy model"""
        try:
            # SpaCy models are typically installed via pip
            # For local installation, we can download the wheel file
            import subprocess
            
            # Create virtual environment for SpaCy model
            model_dir = Path(local_path)
            model_dir.mkdir(parents=True, exist_ok=True)
            
            # Install SpaCy model
            cmd = [
                "python", "-m", "spacy", "download", model_name,
                "--target", str(model_dir)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Successfully downloaded SpaCy model {model_name}")
                return True
            else:
                logger.error(f"Failed to download SpaCy model {model_name}: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to download SpaCy model {model_name}: {e}")
            return False
    
    def verify_download(self, file_path: str, expected_hash: Optional[str] = None) -> bool:
        """
        Verify downloaded file integrity
        
        Args:
            file_path: Path to downloaded file
            expected_hash: Expected SHA256 hash (optional)
            
        Returns:
            bool: True if verification passed
        """
        try:
            if not os.path.exists(file_path):
                return False
            
            if expected_hash:
                # Calculate file hash
                sha256_hash = hashlib.sha256()
                with open(file_path, "rb") as f:
                    for chunk in iter(lambda: f.read(4096), b""):
                        sha256_hash.update(chunk)
                
                file_hash = sha256_hash.hexdigest()
                return file_hash.lower() == expected_hash.lower()
            
            # If no hash provided, just check file exists and has size > 0
            return os.path.getsize(file_path) > 0
            
        except Exception as e:
            logger.error(f"Failed to verify download {file_path}: {e}")
            return False
    
    def get_download_progress(self, model_name: str) -> Dict[str, Any]:
        """Get download progress for a model"""
        # This would track progress across multiple files
        # For now, return basic info
        return {
            "model_name": model_name,
            "status": "unknown",
            "progress": 0,
            "downloaded_bytes": 0,
            "total_bytes": 0
        }
    
    def cleanup_failed_downloads(self, model_name: str):
        """Clean up files from failed downloads"""
        try:
            model_dir = Path(f"cache/downloads/{model_name}")
            if model_dir.exists():
                import shutil
                shutil.rmtree(model_dir)
                logger.info(f"Cleaned up failed download for {model_name}")
        except Exception as e:
            logger.error(f"Failed to cleanup failed download for {model_name}: {e}")
    
    def get_popular_models_config(self) -> Dict[str, Any]:
        """Get configuration for popular LLM models and audio processing models"""
        return {
            # Text/LLM Models
            "phi-3.5-4b-gguf": {
                "name": "Phi-3.5 (4B)",
                "description": "Microsoft's latest Phi model, optimized for reasoning",
                "url": "https://huggingface.co/microsoft/Phi-3.5-4b-gguf/resolve/main/phi-3.5-4b.Q4_K_M.gguf",
                "filename": "phi-3.5-4b.Q4_K_M.gguf",
                "size_mb": 2400,
                "format": "gguf",
                "context_length": 8192,
                "recommended": True,
                "tags": ["reasoning", "coding", "fast"],
                "type": "text"
            },
            "llama-3.1-8b-gguf": {
                "name": "Llama 3.1 (8B)",
                "description": "Meta's latest Llama model, excellent for general tasks",
                "url": "https://huggingface.co/TheBloke/Llama-3.1-8B-GGUF/resolve/main/llama-3.1-8b.Q4_K_M.gguf",
                "filename": "llama-3.1-8b.Q4_K_M.gguf",
                "size_mb": 4800,
                "format": "gguf",
                "context_length": 8192,
                "recommended": True,
                "tags": ["general", "creative", "balanced"],
                "type": "text"
            },
            "qwen2.5-7b-gguf": {
                "name": "Qwen 2.5 (7B)",
                "description": "Alibaba's Qwen model, great for multilingual tasks",
                "url": "https://huggingface.co/Qwen/Qwen2.5-7B-GGUF/resolve/main/qwen2.5-7b.Q4_K_M.gguf",
                "filename": "qwen2.5-7b.Q4_K_M.gguf",
                "size_mb": 4200,
                "format": "gguf",
                "context_length": 32768,
                "recommended": True,
                "tags": ["multilingual", "creative", "large-context"],
                "type": "text"
            },
            "mistral-7b-gguf": {
                "name": "Mistral 7B",
                "description": "Mistral AI's 7B model, excellent performance",
                "url": "https://huggingface.co/TheBloke/Mistral-7B-v0.1-GGUF/resolve/main/mistral-7b-v0.1.Q4_K_M.gguf",
                "filename": "*.gguf",
                "size_mb": 4200,
                "format": "gguf",
                "context_length": 8192,
                "recommended": True,
                "tags": ["performance", "creative", "balanced"],
                "type": "text"
            },
            "llama-3.1-1b-gguf": {
                "name": "Llama 3.1 (1B)",
                "description": "Lightweight Llama model for fast inference",
                "url": "https://huggingface.co/TheBloke/Llama-3.1-1B-GGUF/resolve/main/llama-3.1-1b.Q4_K_M.gguf",
                "filename": "llama-3.1-1b.Q4_K_M.gguf",
                "size_mb": 600,
                "format": "gguf",
                "context_length": 8192,
                "recommended": False,
                "tags": ["fast", "lightweight", "basic"],
                "type": "text"
            },
            "qwen2.5-4b-gguf": {
                "name": "Qwen 2.5 (4B)",
                "description": "Balanced Qwen model for good performance",
                "url": "https://huggingface.co/Qwen/Qwen2.5-4B-GGUF/resolve/main/qwen2.5-4b.Q4_K_M.gguf",
                "filename": "qwen2.5-4b.Q4_K_M.gguf",
                "size_mb": 2400,
                "format": "gguf",
                "context_length": 32768,
                "recommended": True,
                "tags": ["balanced", "multilingual", "good-performance"],
                "type": "text"
            },
            "gemma-2b-gguf": {
                "name": "Gemma 2B",
                "description": "Google's lightweight Gemma model",
                "url": "https://huggingface.co/TheBloke/Gemma-2B-GGUF/resolve/main/gemma-2b.Q4_K_M.gguf",
                "filename": "*.gguf",
                "size_mb": 1200,
                "format": "gguf",
                "context_length": 8192,
                "recommended": False,
                "tags": ["lightweight", "google", "basic"],
                "type": "text"
            },
            "phi-2-gguf": {
                "name": "Phi-2",
                "description": "Microsoft's Phi-2 model, optimized for reasoning",
                "url": "https://huggingface.co/microsoft/Phi-2-gguf/resolve/main/phi-2.Q4_K_M.gguf",
                "filename": "*.gguf",
                "size_mb": 1700,
                "format": "gguf",
                "context_length": 2048,
                "recommended": True,
                "tags": ["reasoning", "coding", "fast"],
                "type": "text"
            },
            "llama2-7b-gguf": {
                "name": "Llama 2 (7B)",
                "description": "Meta's Llama 2 model, excellent for general tasks",
                "url": "https://huggingface.co/TheBloke/Llama-2-7B-GGUF/resolve/main/llama-2-7b.Q4_K_M.gguf",
                "filename": "*.gguf",
                "size_mb": 4200,
                "format": "gguf",
                "context_length": 4096,
                "recommended": True,
                "tags": ["general", "creative", "balanced"],
                "type": "text"
            },
            "qwen2-7b-gguf": {
                "name": "Qwen 2 (7B)",
                "description": "Alibaba's Qwen 2 model, great for multilingual tasks",
                "url": "https://huggingface.co/Qwen/Qwen2-7B-GGUF/resolve/main/qwen2-7b.Q4_K_M.gguf",
                "filename": "*.gguf",
                "size_mb": 4200,
                "format": "gguf",
                "context_length": 32768,
                "recommended": True,
                "tags": ["multilingual", "creative", "large-context"],
                "type": "text"
            },
            "gpt-oss-20b-gguf": {
                "name": "GPT-OSS 20B",
                "description": "Open source GPT model with 20B parameters",
                "url": "https://huggingface.co/TheBloke/GPT-OSS-20B-GGUF/resolve/main/gpt-oss-20b.Q4_K_M.gguf",
                "filename": "*.gguf",
                "size_mb": 12000,
                "format": "gguf",
                "context_length": 8192,
                "recommended": False,
                "tags": ["large", "open-source", "gpt"],
                "type": "text"
            },
            "llama-3.1-70b-gguf": {
                "name": "Llama 3.1 (70B)",
                "description": "Meta's largest Llama 3.1 model for advanced tasks",
                "url": "https://huggingface.co/TheBloke/Llama-3.1-70B-GGUF/resolve/main/llama-3.1-70b.Q4_K_M.gguf",
                "filename": "*.gguf",
                "size_mb": 40000,
                "format": "gguf",
                "context_length": 8192,
                "recommended": False,
                "tags": ["large", "advanced", "high-quality"],
                "type": "text"
            },
            "qwen2.5-32b-gguf": {
                "name": "Qwen 2.5 (32B)",
                "description": "Alibaba's large Qwen model for complex tasks",
                "url": "https://huggingface.co/Qwen/Qwen2.5-32B-GGUF/resolve/main/qwen2.5-32b.Q4_K_M.gguf",
                "filename": "*.gguf",
                "size_mb": 19000,
                "format": "gguf",
                "context_length": 32768,
                "recommended": False,
                "tags": ["large", "multilingual", "complex-tasks"],
                "type": "text"
            },
            "mistral-7b-instruct-gguf": {
                "name": "Mistral 7B Instruct",
                "description": "Mistral's instruction-tuned model for chat",
                "url": "https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf",
                "filename": "*.gguf",
                "size_mb": 4200,
                "format": "gguf",
                "context_length": 8192,
                "recommended": True,
                "tags": ["instruct", "chat", "balanced"],
                "type": "text"
            },
            "codellama-7b-gguf": {
                "name": "Code Llama 7B",
                "description": "Meta's code-focused Llama model",
                "url": "https://huggingface.co/TheBloke/CodeLlama-7B-GGUF/resolve/main/codellama-7b.Q4_K_M.gguf",
                "filename": "*.gguf",
                "size_mb": 4200,
                "format": "gguf",
                "context_length": 8192,
                "recommended": True,
                "tags": ["coding", "programming", "development"],
                "type": "text"
            },
            "codellama-13b-gguf": {
                "name": "Code Llama 13B",
                "description": "Meta's larger code-focused Llama model",
                "url": "https://huggingface.co/TheBloke/CodeLlama-13B-GGUF/resolve/main/codellama-13b.Q4_K_M.gguf",
                "filename": "*.gguf",
                "size_mb": 7800,
                "format": "gguf",
                "context_length": 8192,
                "recommended": False,
                "tags": ["coding", "programming", "large"],
                "type": "text"
            },
            "neural-chat-7b-gguf": {
                "name": "Neural Chat 7B",
                "description": "Intel's conversational AI model",
                "url": "https://huggingface.co/TheBloke/neural-chat-7b-v3-1-GGUF/resolve/main/neural-chat-7b-v3-1.Q4_K_M.gguf",
                "filename": "*.gguf",
                "size_mb": 4200,
                "format": "gguf",
                "context_length": 8192,
                "recommended": True,
                "tags": ["conversational", "intel", "chat"],
                "type": "text"
            },
            "orca-mini-3b-gguf": {
                "name": "Orca Mini 3B",
                "description": "Microsoft's lightweight Orca model",
                "url": "https://huggingface.co/TheBloke/orca-mini-3b-gguf/resolve/main/orca-mini-3b.Q4_K_M.gguf",
                "filename": "*.gguf",
                "size_mb": 1800,
                "format": "gguf",
                "context_length": 8192,
                "recommended": False,
                "tags": ["lightweight", "fast", "microsoft"],
                "type": "text"
            },
            "wizardlm-7b-gguf": {
                "name": "WizardLM 7B",
                "description": "Microsoft's WizardLM for instruction following",
                "url": "https://huggingface.co/TheBloke/WizardLM-7B-V1.0-GGUF/resolve/main/wizardlm-7b-v1.0.Q4_K_M.gguf",
                "filename": "*.gguf",
                "size_mb": 4200,
                "format": "gguf",
                "context_length": 8192,
                "recommended": True,
                "tags": ["instruction", "wizard", "microsoft"],
                "type": "text"
            },
            "vicuna-7b-gguf": {
                "name": "Vicuna 7B",
                "description": "UC Berkeley's Vicuna model for chat",
                "url": "https://huggingface.co/TheBloke/vicuna-7B-v1.5-GGUF/resolve/main/vicuna-7b-v1.5.Q4_K_M.gguf",
                "filename": "*.gguf",
                "size_mb": 4200,
                "format": "gguf",
                "context_length": 8192,
                "recommended": True,
                "tags": ["chat", "conversational", "uc-berkeley"],
                "type": "text"
            },
            "falcon-7b-gguf": {
                "name": "Falcon 7B",
                "description": "Technology Innovation Institute's Falcon model",
                "url": "https://huggingface.co/TheBloke/falcon-7b-GGUF/resolve/main/falcon-7b.Q4_K_M.gguf",
                "filename": "*.gguf",
                "size_mb": 4200,
                "format": "gguf",
                "context_length": 8192,
                "recommended": False,
                "tags": ["falcon", "innovation", "balanced"],
                "type": "text"
            },
            "mpt-7b-gguf": {
                "name": "MPT 7B",
                "description": "MosaicML's MPT model for general tasks",
                "url": "https://huggingface.co/TheBloke/mpt-7b-GGUF/resolve/main/mpt-7b.Q4_K_M.gguf",
                "filename": "*.gguf",
                "size_mb": 4200,
                "format": "gguf",
                "context_length": 8192,
                "recommended": False,
                "tags": ["mosaicml", "general", "balanced"],
                "type": "text"
            },
            
            # Audio Processing Models
            "whisper-large-v3": {
                "name": "Whisper Large v3",
                "description": "OpenAI's Whisper model for speech recognition and transcription",
                "url": "https://huggingface.co/openai/whisper-large-v3/resolve/main/pytorch_model.bin",
                "filename": "whisper-large-v3",
                "size_mb": 1550,
                "format": "pytorch",
                "context_length": None,
                "recommended": True,
                "tags": ["speech-recognition", "transcription", "multilingual"],
                "type": "audio"
            },
            "whisper-medium": {
                "name": "Whisper Medium",
                "description": "Balanced Whisper model for speech recognition",
                "url": "https://huggingface.co/openai/whisper-medium/resolve/main/pytorch_model.bin",
                "filename": "whisper-medium",
                "size_mb": 769,
                "format": "pytorch",
                "context_length": None,
                "recommended": True,
                "tags": ["speech-recognition", "transcription", "balanced"],
                "type": "audio"
            },
            "whisper-small": {
                "name": "Whisper Small",
                "description": "Fast Whisper model for quick transcription",
                "url": "https://huggingface.co/openai/whisper-small/resolve/main/pytorch_model.bin",
                "filename": "whisper-small",
                "size_mb": 244,
                "format": "pytorch",
                "context_length": None,
                "recommended": False,
                "tags": ["speech-recognition", "fast", "lightweight"],
                "type": "audio"
            },
            "bark": {
                "name": "Bark Text-to-Speech",
                "description": "Sunno's Bark model for high-quality text-to-speech",
                "url": "https://huggingface.co/suno/bark/resolve/main/pytorch_model.bin",
                "filename": "bark",
                "size_mb": 3200,
                "format": "pytorch",
                "context_length": None,
                "recommended": True,
                "tags": ["text-to-speech", "voice-synthesis", "high-quality"],
                "type": "audio"
            },
            "coqui-tts": {
                "name": "Coqui TTS",
                "description": "Coqui's text-to-speech model with multiple voices",
                "url": "https://huggingface.co/coqui/XTTS-v2/resolve/main/pytorch_model.bin",
                "filename": "coqui-tts",
                "size_mb": 1800,
                "format": "pytorch",
                "context_length": None,
                "recommended": False,
                "tags": ["text-to-speech", "multilingual", "voice-cloning"],
                "type": "audio"
            },
            "musicgen": {
                "name": "MusicGen",
                "description": "Meta's MusicGen for music generation from text",
                "url": "https://huggingface.co/facebook/musicgen-small/resolve/main/pytorch_model.bin",
                "filename": "musicgen",
                "size_mb": 500,
                "format": "pytorch",
                "context_length": None,
                "recommended": False,
                "tags": ["music-generation", "audio-generation", "creative"],
                "type": "audio"
            },
            "audiocraft": {
                "name": "AudioCraft",
                "description": "Meta's AudioCraft for audio generation and processing",
                "url": "https://huggingface.co/facebook/audiocraft/resolve/main/pytorch_model.bin",
                "filename": "audiocraft",
                "size_mb": 800,
                "format": "pytorch",
                "context_length": None,
                "recommended": False,
                "tags": ["audio-generation", "music", "sound-effects"],
                "type": "audio"
            },
            "tortoise-tts": {
                "name": "Tortoise TTS",
                "description": "Neon's Tortoise TTS for high-quality speech synthesis",
                "url": "https://huggingface.co/neon/tortoise-tts/resolve/main/pytorch_model.bin",
                "filename": "tortoise-tts",
                "size_mb": 2800,
                "format": "pytorch",
                "context_length": None,
                "recommended": False,
                "tags": ["text-to-speech", "high-quality", "voice-cloning"],
                "type": "audio"
            }
        }
    
    def download_popular_model(self, model_id: str, progress_callback=None) -> bool:
        """Download a popular model by ID"""
        model_configs = self.get_popular_models_config()
        
        if model_id not in model_configs:
            logger.error(f"Unknown model: {model_id}")
            return False
        
        config = model_configs[model_id]
        model_dir = Path(self.download_dir) / model_id
        model_dir.mkdir(exist_ok=True)
        
        model_file = model_dir / config['filename']
        
        if model_file.exists():
            logger.info(f"Model {model_id} already downloaded")
            return True
        
        return self.download_file(config['url'], str(model_file), progress_callback)
    
    def download_recommended_models(self, progress_callback=None) -> List[str]:
        """Download all recommended models"""
        model_configs = self.get_popular_models_config()
        recommended_models = [
            model_id for model_id, config in model_configs.items()
            if config['recommended']
        ]
        
        downloaded = []
        for i, model_id in enumerate(recommended_models):
            if progress_callback:
                progress_callback(f"Downloading {i+1}/{len(recommended_models)}: {model_configs[model_id]['name']}")
            
            if self.download_popular_model(model_id):
                downloaded.append(model_id)
        
        return downloaded
    
    def download_essential_models(self, progress_callback=None) -> List[str]:
        """Download essential models for basic functionality"""
        essential_models = [
            "phi-3.5-4b-gguf",  # Fast and capable
            "llama-3.1-1b-gguf"  # Lightweight fallback
        ]
        
        downloaded = []
        for model_id in essential_models:
            if self.download_popular_model(model_id):
                downloaded.append(model_id)
        
        return downloaded
    
    def get_download_size(self, model_ids: List[str]) -> int:
        """Get total download size for models"""
        model_configs = self.get_popular_models_config()
        total_size = 0
        for model_id in model_ids:
            if model_id in model_configs:
                model_file = Path(self.download_dir) / model_id / model_configs[model_id]['filename']
                if not model_file.exists():
                    total_size += model_configs[model_id]['size_mb']
        return total_size
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available models"""
        model_configs = self.get_popular_models_config()
        models = []
        
        for model_id, config in model_configs.items():
            # Check multiple locations for the model
            model_found = False
            model_path = None
            location = None
            
            # 1. Check download directory
            model_file = Path(self.download_dir) / model_id / config['filename']
            if model_file.exists():
                model_found = True
                model_path = str(model_file)
                location = 'downloads'
            
            # 2. Check local_llm_models directory
            if not model_found:
                local_model_dir = Path("local_llm_models") / model_id
                if local_model_dir.exists():
                    gguf_files = list(local_model_dir.glob("*.gguf"))
                    if gguf_files:
                        model_found = True
                        model_path = str(gguf_files[0])
                        location = 'local_llm_models'
            
            # 3. Check standard paths (LM Studio, Ollama, etc.)
            if not model_found:
                for standard_path in self.standard_paths:
                    # Look for model in standard paths
                    potential_paths = [
                        standard_path / model_id,
                        standard_path / model_id.lower(),
                        standard_path / model_id.replace('-', '_'),
                        standard_path / model_id.replace('_', '-')
                    ]
                    
                    for potential_path in potential_paths:
                        if potential_path.exists():
                            # Look for .gguf files
                            gguf_files = list(potential_path.glob("*.gguf"))
                            if gguf_files:
                                model_found = True
                                model_path = str(gguf_files[0])
                                location = str(standard_path.name)
                                break
                        
                        # Also check if the path itself is a .gguf file
                        if potential_path.with_suffix('.gguf').exists():
                            model_found = True
                            model_path = str(potential_path.with_suffix('.gguf'))
                            location = str(standard_path.name)
                            break
                    
                    if model_found:
                        break
            
            # 4. Search for any .gguf files that might match the model name
            if not model_found:
                for standard_path in self.standard_paths:
                    # Search recursively for .gguf files containing model name
                    for gguf_file in standard_path.rglob("*.gguf"):
                        if model_id.lower() in gguf_file.name.lower() or model_id.replace('-', '_').lower() in gguf_file.name.lower():
                            model_found = True
                            model_path = str(gguf_file)
                            location = str(standard_path.name)
                            break
                    if model_found:
                        break
            
            model_info = {
                'id': model_id,
                'name': config['name'],
                'description': config['description'],
                'size_mb': config['size_mb'],
                'format': config['format'],
                'context_length': config['context_length'],
                'recommended': config['recommended'],
                'tags': config['tags'],
                'type': config.get('type', 'text'),
                'downloaded': model_found,
                'path': model_path,
                'location': location
            }
            models.append(model_info)
        
        return models
    
    def get_models_by_type(self, model_type: str) -> List[Dict[str, Any]]:
        """Get models filtered by type (text, audio)"""
        all_models = self.get_available_models()
        return [model for model in all_models if model['type'] == model_type]
    
    def get_text_models(self) -> List[Dict[str, Any]]:
        """Get all text/LLM models"""
        return self.get_models_by_type('text')
    
    def get_audio_models(self) -> List[Dict[str, Any]]:
        """Get all audio processing models"""
        return self.get_models_by_type('audio')
    
    def get_recommended_audio_models(self) -> List[Dict[str, Any]]:
        """Get recommended audio models for basic functionality"""
        audio_models = self.get_audio_models()
        return [model for model in audio_models if model['recommended']]
    
    def get_ollama_models(self) -> List[Dict[str, Any]]:
        """Get models available in Ollama"""
        import subprocess
        import platform
        
        ollama_models = []
        
        try:
            # Check if Ollama is installed
            result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                for line in lines:
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 2:
                            model_name = parts[0]
                            size_str = parts[1] if len(parts) > 1 else "Unknown"
                            
                            # Convert size to MB
                            size_mb = 0
                            if 'GB' in size_str:
                                size_mb = int(float(size_str.replace('GB', '')) * 1024)
                            elif 'MB' in size_str:
                                size_mb = int(float(size_str.replace('MB', '')))
                            
                            ollama_models.append({
                                'id': f"ollama-{model_name}",
                                'name': f"Ollama {model_name}",
                                'description': f"Ollama model: {model_name}",
                                'size_mb': size_mb,
                                'format': 'ollama',
                                'context_length': 8192,
                                'recommended': False,
                                'tags': ['ollama', 'local'],
                                'type': 'text',
                                'downloaded': True,
                                'path': f"ollama://{model_name}",
                                'location': 'ollama'
                            })
                
                logger.info(f"Found {len(ollama_models)} Ollama models")
            else:
                logger.info("Ollama not available or no models installed")
                
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
            logger.info(f"Ollama not available: {e}")
        
        return ollama_models
    
    def get_all_available_models(self) -> List[Dict[str, Any]]:
        """Get all available models including Ollama models"""
        # Get standard models
        standard_models = self.get_available_models()
        
        # Get Ollama models
        ollama_models = self.get_ollama_models()
        
        # Combine and return
        all_models = standard_models + ollama_models
        
        # Sort by recommended first, then by name
        all_models.sort(key=lambda x: (not x.get('recommended', False), x['name']))
        
        return all_models
