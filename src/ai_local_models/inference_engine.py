"""
Inference Engine
Handles loading and running local AI models for inference
"""

import os
import logging
import time
import threading
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
import json

from .gpu_detector import gpu_detector

logger = logging.getLogger(__name__)

class InferenceEngine:
    """Manages local AI model inference"""
    
    def __init__(self, models_dir: str = "src/ai_local_models"):
        self.models_dir = Path(models_dir)
        self.loaded_models: Dict[str, Any] = {}
        self.model_locks: Dict[str, threading.Lock] = {}
        self.model_configs: Dict[str, Any] = {}
        self.gpu_detector = gpu_detector
        
        # Initialize model types
        self.model_handlers = {
            "gguf": self._load_gguf_model,
            "pytorch": self._load_pytorch_model,
            "tensorflow": self._load_tensorflow_model,
            "spacy": self._load_spacy_model,
            "transformers": self._load_transformers_model
        }
    
    def load_model(self, model_name: str, model_config: Dict[str, Any]) -> bool:
        """
        Load a model into memory
        
        Args:
            model_name: Name of the model
            model_config: Model configuration
            
        Returns:
            bool: True if model loaded successfully
        """
        try:
            if model_name in self.loaded_models:
                logger.info(f"Model {model_name} already loaded")
                return True
            
            # Create lock for this model
            if model_name not in self.model_locks:
                self.model_locks[model_name] = threading.Lock()
            
            with self.model_locks[model_name]:
                model_format = model_config.get("format", "").lower()
                model_path = model_config.get("local_path", "")
                
                if not model_path or not os.path.exists(model_path):
                    logger.error(f"Model path not found: {model_path}")
                    return False
                
                # Load model based on format
                handler = self.model_handlers.get(model_format)
                if not handler:
                    logger.error(f"Unsupported model format: {model_format}")
                    return False
                
                model = handler(model_name, model_path, model_config)
                if model:
                    self.loaded_models[model_name] = model
                    self.model_configs[model_name] = model_config
                    logger.info(f"Successfully loaded model: {model_name}")
                    return True
                else:
                    logger.error(f"Failed to load model: {model_name}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error loading model {model_name}: {e}")
            return False
    
    def _load_gguf_model(self, model_name: str, model_path: str, config: Dict[str, Any]) -> Optional[Any]:
        """Load a GGUF model using llama-cpp-python with GPU support"""
        try:
            from llama_cpp import Llama
            
            # Get optimal configuration based on hardware
            optimal_config = self.gpu_detector.get_optimal_config(config)
            
            # Model parameters with GPU detection
            n_ctx = optimal_config.get("context_length", 4096)
            n_threads = optimal_config.get("cpu_threads", 4)
            n_gpu_layers = optimal_config.get("gpu_layers", 0)
            
            logger.info(f"Loading GGUF model {model_name} with {n_gpu_layers} GPU layers, {n_threads} CPU threads")
            
            model = Llama(
                model_path=model_path,
                n_ctx=n_ctx,
                n_threads=n_threads,
                n_gpu_layers=n_gpu_layers,
                verbose=False,
                use_mmap=True,
                use_mlock=False
            )
            
            return model
            
        except ImportError:
            logger.error("llama-cpp-python not installed. Install with: pip install llama-cpp-python")
            return None
        except Exception as e:
            logger.error(f"Failed to load GGUF model {model_name}: {e}")
            return None
    
    def _load_pytorch_model(self, model_name: str, model_path: str, config: Dict[str, Any]) -> Optional[Any]:
        """Load a PyTorch model with CPU/GPU support"""
        try:
            import torch
            from transformers import AutoModel, AutoTokenizer, AutoModelForCausalLM
            
            # Get PyTorch device configuration
            pytorch_config = self.gpu_detector.get_pytorch_config()
            device = pytorch_config['device']
            
            logger.info(f"Loading PyTorch model {model_name} on device: {device}")
            
            # Load tokenizer and model
            tokenizer = AutoTokenizer.from_pretrained(model_path)
            
            # Try to load as causal LM first, fallback to regular model
            try:
                model = AutoModelForCausalLM.from_pretrained(model_path)
            except:
                model = AutoModel.from_pretrained(model_path)
            
            # Move model to appropriate device
            model = model.to(device)
            
            # Set to evaluation mode
            model.eval()
            
            # CPU-specific optimizations
            if device == 'cpu':
                # Enable CPU optimizations
                if hasattr(torch, 'set_num_threads'):
                    torch.set_num_threads(pytorch_config.get('cpu_threads', 4))
                
                # Use MKL if available
                if pytorch_config.get('use_mkl', True):
                    try:
                        import torch.backends.mkl
                        torch.backends.mkl.enabled = True
                    except:
                        pass
            
            return {
                "model": model,
                "tokenizer": tokenizer,
                "type": "pytorch",
                "device": device,
                "config": pytorch_config
            }
            
        except ImportError:
            logger.error("PyTorch/Transformers not installed. Install with: pip install torch transformers")
            return None
        except Exception as e:
            logger.error(f"Failed to load PyTorch model {model_name}: {e}")
            return None
    
    def _load_tensorflow_model(self, model_name: str, model_path: str, config: Dict[str, Any]) -> Optional[Any]:
        """Load a TensorFlow model with CPU/GPU support"""
        try:
            import tensorflow as tf
            
            # Check GPU availability
            gpus = tf.config.list_physical_devices('GPU')
            device = 'gpu' if gpus else 'cpu'
            
            logger.info(f"Loading TensorFlow model {model_name} on device: {device}")
            
            # Configure GPU memory growth if using GPU
            if gpus:
                try:
                    for gpu in gpus:
                        tf.config.experimental.set_memory_growth(gpu, True)
                    logger.info("GPU memory growth enabled")
                except Exception as e:
                    logger.warning(f"Could not set GPU memory growth: {e}")
            
            # Load model
            model = tf.keras.models.load_model(model_path)
            
            return {
                "model": model,
                "type": "tensorflow",
                "device": device,
                "gpu_available": bool(gpus)
            }
            
        except ImportError:
            logger.error("TensorFlow not installed. Install with: pip install tensorflow")
            return None
        except Exception as e:
            logger.error(f"Failed to load TensorFlow model {model_name}: {e}")
            return None
    
    def _load_spacy_model(self, model_name: str, model_path: str, config: Dict[str, Any]) -> Optional[Any]:
        """Load a SpaCy model"""
        try:
            import spacy
            
            # Load SpaCy model
            nlp = spacy.load(model_path)
            
            return {
                "model": nlp,
                "type": "spacy"
            }
            
        except ImportError:
            logger.error("SpaCy not installed. Install with: pip install spacy")
            return None
        except Exception as e:
            logger.error(f"Failed to load SpaCy model {model_name}: {e}")
            return None
    
    def _load_transformers_model(self, model_name: str, model_path: str, config: Dict[str, Any]) -> Optional[Any]:
        """Load a Transformers model"""
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            
            # Load tokenizer and model
            tokenizer = AutoTokenizer.from_pretrained(model_path)
            model = AutoModelForCausalLM.from_pretrained(model_path)
            
            return {
                "model": model,
                "tokenizer": tokenizer,
                "type": "transformers"
            }
            
        except ImportError:
            logger.error("Transformers not installed. Install with: pip install transformers")
            return None
        except Exception as e:
            logger.error(f"Failed to load Transformers model {model_name}: {e}")
            return None
    
    def is_model_loaded(self, model_name: str) -> bool:
        """Check if a model is currently loaded"""
        return model_name in self.loaded_models
    
    def generate_text(self, model_name: str, prompt: str, **kwargs) -> Optional[str]:
        """
        Generate text using a loaded model
        
        Args:
            model_name: Name of the loaded model
            prompt: Input prompt
            **kwargs: Additional generation parameters
            
        Returns:
            Optional[str]: Generated text or None if failed
        """
        try:
            if model_name not in self.loaded_models:
                logger.error(f"Model {model_name} not loaded")
                return None
            
            model = self.loaded_models[model_name]
            config = self.model_configs[model_name]
            
            # Get generation parameters
            temperature = kwargs.get("temperature", config.get("temperature", 0.7))
            max_tokens = kwargs.get("max_tokens", config.get("max_tokens", 2048))
            
            # Generate based on model type
            if hasattr(model, 'create_completion'):  # GGUF model
                return self._generate_gguf_text(model, prompt, temperature, max_tokens)
            elif isinstance(model, dict) and model.get("type") == "pytorch":
                return self._generate_pytorch_text(model, prompt, temperature, max_tokens)
            elif isinstance(model, dict) and model.get("type") == "transformers":
                return self._generate_transformers_text(model, prompt, temperature, max_tokens)
            else:
                logger.error(f"Unsupported model type for text generation: {type(model)}")
                return None
                
        except Exception as e:
            logger.error(f"Error generating text with {model_name}: {e}")
            return None
    
    def _generate_gguf_text(self, model: Any, prompt: str, temperature: float, max_tokens: int) -> Optional[str]:
        """Generate text using GGUF model"""
        try:
            response = model.create_completion(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                stop=["</s>", "\n\n", "Human:", "Assistant:"]
            )
            
            return response['choices'][0]['text'].strip()
            
        except Exception as e:
            logger.error(f"Error generating text with GGUF model: {e}")
            return None
    
    def _generate_pytorch_text(self, model_dict: Dict[str, Any], prompt: str, temperature: float, max_tokens: int) -> Optional[str]:
        """Generate text using PyTorch model"""
        try:
            import torch
            
            model = model_dict["model"]
            tokenizer = model_dict["tokenizer"]
            
            # Tokenize input
            inputs = tokenizer.encode(prompt, return_tensors="pt")
            
            # Generate
            with torch.no_grad():
                outputs = model.generate(
                    inputs,
                    max_length=inputs.shape[1] + max_tokens,
                    temperature=temperature,
                    do_sample=True,
                    pad_token_id=tokenizer.eos_token_id
                )
            
            # Decode output
            generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Remove input prompt
            if generated_text.startswith(prompt):
                generated_text = generated_text[len(prompt):].strip()
            
            return generated_text
            
        except Exception as e:
            logger.error(f"Error generating text with PyTorch model: {e}")
            return None
    
    def _generate_transformers_text(self, model_dict: Dict[str, Any], prompt: str, temperature: float, max_tokens: int) -> Optional[str]:
        """Generate text using Transformers model"""
        try:
            import torch
            
            model = model_dict["model"]
            tokenizer = model_dict["tokenizer"]
            
            # Tokenize input
            inputs = tokenizer.encode(prompt, return_tensors="pt")
            
            # Generate
            with torch.no_grad():
                outputs = model.generate(
                    inputs,
                    max_length=inputs.shape[1] + max_tokens,
                    temperature=temperature,
                    do_sample=True,
                    pad_token_id=tokenizer.eos_token_id
                )
            
            # Decode output
            generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Remove input prompt
            if generated_text.startswith(prompt):
                generated_text = generated_text[len(prompt):].strip()
            
            return generated_text
            
        except Exception as e:
            logger.error(f"Error generating text with Transformers model: {e}")
            return None
    
    def get_embeddings(self, model_name: str, text: str) -> Optional[List[float]]:
        """
        Get embeddings for text using a loaded model
        
        Args:
            model_name: Name of the loaded model
            text: Input text
            
        Returns:
            Optional[List[float]]: Text embeddings or None if failed
        """
        try:
            if model_name not in self.loaded_models:
                logger.error(f"Model {model_name} not loaded")
                return None
            
            model = self.loaded_models[model_name]
            
            # Get embeddings based on model type
            if isinstance(model, dict) and model.get("type") == "pytorch":
                return self._get_pytorch_embeddings(model, text)
            elif isinstance(model, dict) and model.get("type") == "spacy":
                return self._get_spacy_embeddings(model, text)
            else:
                logger.error(f"Unsupported model type for embeddings: {type(model)}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting embeddings with {model_name}: {e}")
            return None
    
    def _get_pytorch_embeddings(self, model_dict: Dict[str, Any], text: str) -> Optional[List[float]]:
        """Get embeddings using PyTorch model"""
        try:
            import torch
            
            model = model_dict["model"]
            tokenizer = model_dict["tokenizer"]
            
            # Tokenize and get embeddings
            inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
            
            with torch.no_grad():
                outputs = model(**inputs)
                embeddings = outputs.last_hidden_state.mean(dim=1)  # Mean pooling
            
            return embeddings[0].tolist()
            
        except Exception as e:
            logger.error(f"Error getting PyTorch embeddings: {e}")
            return None
    
    def _get_spacy_embeddings(self, model_dict: Dict[str, Any], text: str) -> Optional[List[float]]:
        """Get embeddings using SpaCy model"""
        try:
            nlp = model_dict["model"]
            doc = nlp(text)
            
            # Get document vector
            return doc.vector.tolist()
            
        except Exception as e:
            logger.error(f"Error getting SpaCy embeddings: {e}")
            return None
    
    def unload_model(self, model_name: str) -> bool:
        """
        Unload a model from memory
        
        Args:
            model_name: Name of the model to unload
            
        Returns:
            bool: True if model unloaded successfully
        """
        try:
            if model_name in self.loaded_models:
                del self.loaded_models[model_name]
                if model_name in self.model_configs:
                    del self.model_configs[model_name]
                if model_name in self.model_locks:
                    del self.model_locks[model_name]
                
                logger.info(f"Unloaded model: {model_name}")
                return True
            else:
                logger.warning(f"Model {model_name} not loaded")
                return False
                
        except Exception as e:
            logger.error(f"Error unloading model {model_name}: {e}")
            return False
    
    def get_loaded_models(self) -> List[str]:
        """Get list of currently loaded models"""
        return list(self.loaded_models.keys())
    
    def get_model_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a loaded model"""
        if model_name in self.loaded_models:
            config = self.model_configs.get(model_name, {})
            return {
                "name": model_name,
                "type": config.get("type", "unknown"),
                "format": config.get("format", "unknown"),
                "memory_required": config.get("memory_required", 0),
                "context_length": config.get("context_length", 0),
                "loaded": True
            }
        return None
    
    def cleanup(self):
        """Clean up all loaded models"""
        for model_name in list(self.loaded_models.keys()):
            self.unload_model(model_name)
