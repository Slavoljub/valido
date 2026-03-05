"""
GPU Detection Module
Handles GPU detection and configuration for AI models
"""

import os
import logging
import platform
from typing import Dict, Any, Optional, List
from pathlib import Path

logger = logging.getLogger(__name__)

class GPUDetector:
    """Detects and configures GPU settings for AI models"""
    
    def __init__(self):
        self.gpu_info = self._detect_gpu()
        self.system_info = self._get_system_info()
        
    def _detect_gpu(self) -> Dict[str, Any]:
        """
        Detect available GPU and return configuration
        Returns: dict with gpu_available, gpu_type, memory_gb, compute_capability
        """
        gpu_info = {
            'gpu_available': False,
            'gpu_type': None,
            'gpu_vendor': None,  # 'nvidia', 'amd', 'intel'
            'memory_gb': 0,
            'compute_capability': None,
            'driver_version': None,
            'cuda_version': None,
            'rocm_version': None,  # For AMD GPUs
            'pytorch_available': False,
            'tensorflow_available': False,
            'opencl_available': False,
            'vulkan_available': False
        }
        
        # Check PyTorch availability (CPU or GPU)
        try:
            import torch
            gpu_info['pytorch_available'] = True
            gpu_info['pytorch_version'] = torch.__version__
            
            if torch.cuda.is_available():
                gpu_info['gpu_available'] = True
                gpu_info['gpu_vendor'] = 'nvidia'
                gpu_info['gpu_type'] = torch.cuda.get_device_name(0)
                gpu_info['memory_gb'] = torch.cuda.get_device_properties(0).total_memory / 1e9
                gpu_info['compute_capability'] = torch.cuda.get_device_capability(0)
                gpu_info['cuda_version'] = torch.version.cuda
                logger.info(f"NVIDIA GPU detected: {gpu_info['gpu_type']} ({gpu_info['memory_gb']:.1f}GB)")
            elif hasattr(torch, 'hip') and torch.hip.is_available():
                # AMD ROCm support
                gpu_info['gpu_available'] = True
                gpu_info['gpu_vendor'] = 'amd'
                gpu_info['gpu_type'] = torch.hip.get_device_name(0)
                gpu_info['memory_gb'] = torch.hip.get_device_properties(0).total_memory / 1e9
                gpu_info['rocm_version'] = torch.version.hip
                logger.info(f"AMD GPU detected: {gpu_info['gpu_type']} ({gpu_info['memory_gb']:.1f}GB)")
            else:
                logger.info("No GPU available, PyTorch will use CPU mode")
        except ImportError:
            logger.warning("PyTorch not available")
        
        # Check TensorFlow availability (CPU or GPU)
        try:
            import tensorflow as tf
            gpu_info['tensorflow_available'] = True
            gpu_info['tensorflow_version'] = tf.__version__
            
            if tf.config.list_physical_devices('GPU'):
                gpu_info['tensorflow_gpu_available'] = True
                logger.info("TensorFlow GPU support available")
            else:
                gpu_info['tensorflow_gpu_available'] = False
                logger.info("TensorFlow will use CPU mode")
        except (ImportError, Exception) as e:
            gpu_info['tensorflow_available'] = False
            gpu_info['tensorflow_gpu_available'] = False
            logger.warning(f"TensorFlow not available or failed to load: {e}")
        
        # Check OpenCL availability
        try:
            import pyopencl as cl
            platforms = cl.get_platforms()
            if platforms:
                gpu_info['opencl_available'] = True
                logger.info(f"OpenCL available with {len(platforms)} platforms")
        except ImportError:
            logger.debug("OpenCL not available")
        
        # Check Vulkan availability
        try:
            import vulkan as vk
            gpu_info['vulkan_available'] = True
            logger.info("Vulkan available")
        except ImportError:
            logger.debug("Vulkan not available")
        
        return gpu_info
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Get system information for optimization"""
        import psutil
        
        return {
            'platform': platform.system(),
            'architecture': platform.machine(),
            'cpu_count': psutil.cpu_count(),
            'cpu_count_logical': psutil.cpu_count(logical=True),
            'memory_gb': psutil.virtual_memory().total / 1e9,
            'python_version': platform.python_version()
        }
    
    def get_optimal_config(self, model_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get optimal configuration for a model based on available hardware
        """
        config = model_config.copy()
        
        if self.gpu_info['gpu_available']:
            # GPU mode configuration
            gpu_memory_gb = self.gpu_info['memory_gb']
            gpu_vendor = self.gpu_info['gpu_vendor']
            model_memory_required = config.get('memory_required', 4096) / 1024  # Convert to GB
            
            # Calculate optimal GPU layers based on available memory and vendor
            if gpu_vendor == 'nvidia':
                if gpu_memory_gb >= 8:  # 8GB+ GPU
                    config['gpu_layers'] = 32
                    config['n_gpu_layers'] = 32
                elif gpu_memory_gb >= 6:  # 6-8GB GPU
                    config['gpu_layers'] = 24
                    config['n_gpu_layers'] = 24
                elif gpu_memory_gb >= 4:  # 4-6GB GPU
                    config['gpu_layers'] = 16
                    config['n_gpu_layers'] = 16
                else:  # <4GB GPU
                    config['gpu_layers'] = 8
                    config['n_gpu_layers'] = 8
                
                config['device'] = 'cuda:0'
                config['compute_backend'] = 'cuda'
                
            elif gpu_vendor == 'amd':
                # AMD GPUs might need different optimization
                if gpu_memory_gb >= 8:  # 8GB+ GPU
                    config['gpu_layers'] = 24
                    config['n_gpu_layers'] = 24
                elif gpu_memory_gb >= 6:  # 6-8GB GPU
                    config['gpu_layers'] = 16
                    config['n_gpu_layers'] = 16
                elif gpu_memory_gb >= 4:  # 4-6GB GPU
                    config['gpu_layers'] = 12
                    config['n_gpu_layers'] = 12
                else:  # <4GB GPU
                    config['gpu_layers'] = 6
                    config['n_gpu_layers'] = 6
                
                config['device'] = 'hip:0'
                config['compute_backend'] = 'rocm'
            
            config['use_gpu'] = True
            config['gpu_vendor'] = gpu_vendor
            
            logger.info(f"{gpu_vendor.upper()} GPU mode: {config['gpu_layers']} layers, {gpu_memory_gb:.1f}GB available")
        else:
            # CPU mode configuration
            config['gpu_layers'] = 0
            config['n_gpu_layers'] = 0
            config['device'] = 'cpu'
            config['use_gpu'] = False
            config['compute_backend'] = 'cpu'
            config['gpu_vendor'] = None
            
            # Optimize CPU threads based on available cores
            cpu_threads = min(self.system_info['cpu_count'], 8)  # Max 8 threads
            config['cpu_threads'] = cpu_threads
            config['n_threads'] = cpu_threads
            
            # CPU-specific optimizations
            config['use_mkl'] = True  # Use Intel MKL if available
            config['use_openmp'] = True  # Use OpenMP for parallel processing
            
            logger.info(f"CPU mode: {cpu_threads} threads")
        
        return config
    
    def get_model_loading_params(self, model_name: str, model_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get parameters for loading a specific model
        """
        optimal_config = self.get_optimal_config(model_config)
        
        # Common parameters for llama-cpp-python
        params = {
            'model_path': optimal_config.get('local_path', ''),
            'n_ctx': optimal_config.get('context_length', 4096),
            'n_threads': optimal_config.get('cpu_threads', 4),
            'n_gpu_layers': optimal_config.get('gpu_layers', 0),
            'verbose': False,
            'use_mmap': True,
            'use_mlock': False
        }
        
        # Add GPU-specific parameters
        if optimal_config.get('use_gpu', False):
            params.update({
                'n_gpu_layers': optimal_config['gpu_layers'],
                'main_gpu': 0,
                'tensor_split': None,  # Use all GPU memory
                'rope_scaling': None
            })
        else:
            # CPU-specific optimizations
            params.update({
                'n_gpu_layers': 0,
                'use_mkl': optimal_config.get('use_mkl', True),
                'use_openmp': optimal_config.get('use_openmp', True),
                'threads': optimal_config.get('n_threads', 4)
            })
        
        return params
    
    def get_model_config(self, model_name: str) -> Dict[str, Any]:
        """Get specific configuration for a model"""
        base_config = self.get_optimal_config({})
        
        # Model-specific optimizations
        if '7b' in model_name.lower():
            if self.gpu_info['memory_gb'] >= 8:
                base_config['gpu_layers'] = min(base_config.get('gpu_layers', 25), 25)
            else:
                base_config['gpu_layers'] = min(base_config.get('gpu_layers', 15), 15)
        
        elif '13b' in model_name.lower():
            if self.gpu_info['memory_gb'] >= 16:
                base_config['gpu_layers'] = min(base_config.get('gpu_layers', 35), 35)
            else:
                base_config['gpu_layers'] = min(base_config.get('gpu_layers', 20), 20)
        
        elif '4b' in model_name.lower() or '3b' in model_name.lower():
            base_config['gpu_layers'] = min(base_config.get('gpu_layers', 20), 20)
        
        return base_config
    
    def install_gpu_dependencies(self) -> bool:
        """Install GPU dependencies based on detected hardware"""
        try:
            if self.gpu_info['gpu_vendor'] == 'nvidia':
                return self._install_cuda_dependencies()
            elif self.gpu_info['gpu_vendor'] == 'amd':
                return self._install_rocm_dependencies()
            elif self.gpu_info['gpu_vendor'] == 'apple_silicon':
                return self._install_metal_dependencies()
            else:
                return self._install_cpu_dependencies()
        except Exception as e:
            logger.error(f"Failed to install GPU dependencies: {e}")
            return False
    
    def _install_cuda_dependencies(self) -> bool:
        """Install CUDA dependencies"""
        try:
            import subprocess
            import sys
            
            # Install PyTorch with CUDA support
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', 
                'torch', 'torchvision', 'torchaudio', '--index-url', 
                'https://download.pytorch.org/whl/cu118'
            ])
            
            # Install llama-cpp-python with CUDA
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', 
                'llama-cpp-python', '--force-reinstall', '--index-url', 
                'https://jllllll.github.io/llama-cpp-python-cuBLAS-wheels/cu118'
            ])
            
            logger.info("CUDA dependencies installed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to install CUDA dependencies: {e}")
            return False
    
    def _install_rocm_dependencies(self) -> bool:
        """Install ROCm dependencies"""
        try:
            import subprocess
            import sys
            
            # Install PyTorch with ROCm support
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', 
                'torch', 'torchvision', 'torchaudio', '--index-url', 
                'https://download.pytorch.org/whl/rocm5.6'
            ])
            
            logger.info("ROCm dependencies installed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to install ROCm dependencies: {e}")
            return False
    
    def _install_metal_dependencies(self) -> bool:
        """Install Metal dependencies for Apple Silicon"""
        try:
            import subprocess
            import sys
            
            # Install PyTorch with Metal support
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', 
                'torch', 'torchvision', 'torchaudio'
            ])
            
            # Install llama-cpp-python with Metal
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', 
                'llama-cpp-python', '--force-reinstall', '--index-url', 
                'https://jllllll.github.io/llama-cpp-python-cuBLAS-wheels/metal'
            ])
            
            logger.info("Metal dependencies installed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to install Metal dependencies: {e}")
            return False
    
    def _install_cpu_dependencies(self) -> bool:
        """Install CPU-only dependencies"""
        try:
            import subprocess
            import sys
            
            # Install PyTorch CPU version
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', 
                'torch', 'torchvision', 'torchaudio', '--index-url', 
                'https://download.pytorch.org/whl/cpu'
            ])
            
            # Install llama-cpp-python CPU version
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', 
                'llama-cpp-python'
            ])
            
            logger.info("CPU dependencies installed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to install CPU dependencies: {e}")
            return False
    
    def get_recommended_models(self) -> List[str]:
        """Get recommended models based on hardware"""
        models = []
        
        if self.gpu_info['gpu_available']:
            if self.gpu_info['memory_gb'] >= 16:
                models.extend([
                    'llama-3.1-8b-gguf',
                    'qwen2.5-7b-gguf',
                    'mistral-7b-gguf',
                    'phi-3.5-4b-gguf'
                ])
            elif self.gpu_info['memory_gb'] >= 8:
                models.extend([
                    'qwen2.5-4b-gguf',
                    'phi-3.5-4b-gguf',
                    'llama-3.1-1b-gguf'
                ])
            else:
                models.extend([
                    'phi-3.5-4b-gguf',
                    'llama-3.1-1b-gguf'
                ])
        else:
            # CPU-only recommendations
            models.extend([
                'phi-3.5-4b-gguf',
                'llama-3.1-1b-gguf'
            ])
        
        return models
    
    def check_memory_requirements(self, model_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check if system meets memory requirements for a model
        """
        model_memory_gb = model_config.get('memory_required', 4096) / 1024
        available_memory_gb = self.system_info['memory_gb']
        
        if self.gpu_info['gpu_available']:
            gpu_memory_gb = self.gpu_info['memory_gb']
            gpu_sufficient = gpu_memory_gb >= model_memory_gb
            cpu_sufficient = available_memory_gb >= model_memory_gb
            
            return {
                'gpu_sufficient': gpu_sufficient,
                'cpu_sufficient': cpu_sufficient,
                'recommended_mode': 'gpu' if gpu_sufficient else 'cpu',
                'gpu_memory_gb': gpu_memory_gb,
                'cpu_memory_gb': available_memory_gb,
                'required_memory_gb': model_memory_gb
            }
        else:
            cpu_sufficient = available_memory_gb >= model_memory_gb
            
            return {
                'gpu_sufficient': False,
                'cpu_sufficient': cpu_sufficient,
                'recommended_mode': 'cpu',
                'gpu_memory_gb': 0,
                'cpu_memory_gb': available_memory_gb,
                'required_memory_gb': model_memory_gb
            }
    
    def get_system_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive system summary for debugging
        """
        return {
            'gpu_info': self.gpu_info,
            'system_info': self.system_info,
            'environment': {
                'CUDA_VISIBLE_DEVICES': os.environ.get('CUDA_VISIBLE_DEVICES'),
                'PYTORCH_CUDA_ALLOC_CONF': os.environ.get('PYTORCH_CUDA_ALLOC_CONF'),
                'TF_FORCE_GPU_ALLOW_GROWTH': os.environ.get('TF_FORCE_GPU_ALLOW_GROWTH')
            }
        }
    
    def get_pytorch_device(self) -> str:
        """
        Get the optimal PyTorch device (cuda, hip, or cpu)
        """
        if self.gpu_info['gpu_available'] and self.gpu_info['pytorch_available']:
            if self.gpu_info['gpu_vendor'] == 'nvidia':
                return 'cuda'
            elif self.gpu_info['gpu_vendor'] == 'amd':
                return 'hip'
        return 'cpu'
    
    def get_pytorch_config(self) -> Dict[str, Any]:
        """
        Get PyTorch-specific configuration
        """
        config = {
            'device': self.get_pytorch_device(),
            'pytorch_available': self.gpu_info['pytorch_available'],
            'tensorflow_available': self.gpu_info['tensorflow_available']
        }
        
        if config['device'] == 'cuda':
            config.update({
                'cuda_available': True,
                'gpu_memory_gb': self.gpu_info['memory_gb'],
                'compute_capability': self.gpu_info['compute_capability']
            })
        else:
            config.update({
                'cuda_available': False,
                'cpu_threads': self.system_info['cpu_count'],
                'use_mkl': True,
                'use_openmp': True
            })
        
        return config

    def get_available_gpus(self) -> List[Dict[str, Any]]:
        """Get list of available GPUs for selection"""
        gpus = []
        
        # Add CPU option
        gpus.append({
            'id': 'cpu',
            'name': 'CPU (Fallback)',
            'type': 'cpu',
            'memory_gb': 0,
            'description': 'Use CPU for inference (slower but always available)',
            'recommended': not self.gpu_info['gpu_available']
        })
        
        # Add detected GPU if available
        if self.gpu_info['gpu_available']:
            gpu_info = {
                'id': 'gpu_0',
                'name': self.gpu_info['gpu_type'],
                'type': self.gpu_info['gpu_vendor'],
                'memory_gb': self.gpu_info['memory_gb'],
                'description': f"{self.gpu_info['gpu_vendor'].upper()} GPU with {self.gpu_info['memory_gb']:.1f}GB memory",
                'recommended': True,
                'compute_capability': self.gpu_info.get('compute_capability'),
                'driver_version': self.gpu_info.get('driver_version'),
                'cuda_version': self.gpu_info.get('cuda_version'),
                'rocm_version': self.gpu_info.get('rocm_version')
            }
            gpus.append(gpu_info)
        
        return gpus
    
    def get_gpu_config(self, gpu_id: str = 'auto') -> Dict[str, Any]:
        """Get GPU configuration for model inference"""
        if gpu_id == 'auto':
            # Auto-select best available GPU
            if self.gpu_info['gpu_available']:
                gpu_id = 'gpu_0'
            else:
                gpu_id = 'cpu'
        
        if gpu_id == 'cpu':
            return {
                'device': 'cpu',
                'backend': 'cpu',
                'layers': 0,
                'context_length': 2048,
                'batch_size': 1
            }
        elif gpu_id == 'gpu_0' and self.gpu_info['gpu_available']:
            gpu_memory = self.gpu_info['memory_gb']
            
            # Configure based on GPU memory
            if gpu_memory >= 16:
                layers = 35  # Use most layers for large models
                context_length = 8192
                batch_size = 4
            elif gpu_memory >= 8:
                layers = 25  # Moderate layer usage
                context_length = 4096
                batch_size = 2
            elif gpu_memory >= 4:
                layers = 15  # Conservative layer usage
                context_length = 2048
                batch_size = 1
            else:
                layers = 8  # Minimal layer usage
                context_length = 1024
                batch_size = 1
            
            return {
                'device': 'cuda' if self.gpu_info['gpu_vendor'] == 'nvidia' else 'mps',
                'backend': 'cuda' if self.gpu_info['gpu_vendor'] == 'nvidia' else 'mps',
                'layers': layers,
                'context_length': context_length,
                'batch_size': batch_size,
                'memory_gb': gpu_memory
            }
        
        # Fallback to CPU
        return {
            'device': 'cpu',
            'backend': 'cpu',
            'layers': 0,
            'context_length': 2048,
            'batch_size': 1
        }
    
    def get_gpu_status(self) -> Dict[str, Any]:
        """Get current GPU status and capabilities"""
        return {
            'gpu_available': self.gpu_info['gpu_available'],
            'gpu_type': self.gpu_info['gpu_type'],
            'gpu_vendor': self.gpu_info['gpu_vendor'],
            'memory_gb': self.gpu_info['memory_gb'],
            'compute_capability': self.gpu_info.get('compute_capability'),
            'pytorch_available': self.gpu_info['pytorch_available'],
            'tensorflow_available': self.gpu_info['tensorflow_available'],
            'cuda_version': self.gpu_info.get('cuda_version'),
            'rocm_version': self.gpu_info.get('rocm_version'),
            'recommended_backend': self._get_recommended_backend()
        }
    
    def _get_recommended_backend(self) -> str:
        """Get recommended backend based on available hardware"""
        if self.gpu_info['gpu_available']:
            if self.gpu_info['gpu_vendor'] == 'nvidia':
                return 'cuda'
            elif self.gpu_info['gpu_vendor'] == 'amd':
                return 'rocm'
            elif platform.system() == 'Darwin':  # macOS
                return 'mps'
        return 'cpu'

# Global GPU detector instance
gpu_detector = GPUDetector()
