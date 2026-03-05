"""
AI Models Controller for managing local LLM models
"""
import os
import logging
import json
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime

# Lazy imports for AI/ML libraries
try:
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import cohere
    COHERE_AVAILABLE = True
except ImportError:
    COHERE_AVAILABLE = False

logger = logging.getLogger(__name__)


class AIModelsController:
    """Controller for managing AI models and inference"""
    
    def __init__(self):
        self.loaded_models: Dict[str, Any] = {}
        self.model_configs = self._load_model_configs()
        self.models_dir = os.path.join(os.getcwd(), 'models')
        os.makedirs(self.models_dir, exist_ok=True)
        
    def _load_model_configs(self) -> Dict[str, Dict]:
        """Load model configurations"""
        return {
            'llama2-7b': {
                'name': 'Llama 2 7B',
                'type': 'local',
                'model_id': 'meta-llama/Llama-2-7b-chat-hf',
                'description': 'Meta\'s Llama 2 7B parameter model for chat',
                'max_length': 2048,
                'temperature': 0.7,
                'requires_auth': True
            },
            'llama2-13b': {
                'name': 'Llama 2 13B',
                'type': 'local',
                'model_id': 'meta-llama/Llama-2-13b-chat-hf',
                'description': 'Meta\'s Llama 2 13B parameter model for chat',
                'max_length': 2048,
                'temperature': 0.7,
                'requires_auth': True
            },
            'mistral-7b': {
                'name': 'Mistral 7B',
                'type': 'local',
                'model_id': 'mistralai/Mistral-7B-Instruct-v0.2',
                'description': 'Mistral AI\'s 7B parameter instruction-tuned model',
                'max_length': 2048,
                'temperature': 0.7,
                'requires_auth': False
            },
            'phi-2': {
                'name': 'Microsoft Phi-2',
                'type': 'local',
                'model_id': 'microsoft/phi-2',
                'description': 'Microsoft\'s 2.7B parameter model',
                'max_length': 2048,
                'temperature': 0.7,
                'requires_auth': False
            },
            'gpt-3.5-turbo': {
                'name': 'GPT-3.5 Turbo',
                'type': 'external',
                'provider': 'openai',
                'model_id': 'gpt-3.5-turbo',
                'description': 'OpenAI\'s GPT-3.5 Turbo model',
                'max_length': 4096,
                'temperature': 0.7,
                'requires_api_key': True
            },
            'gpt-4': {
                'name': 'GPT-4',
                'type': 'external',
                'provider': 'openai',
                'model_id': 'gpt-4',
                'description': 'OpenAI\'s GPT-4 model',
                'max_length': 8192,
                'temperature': 0.7,
                'requires_api_key': True
            },
            'cohere-command': {
                'name': 'Cohere Command',
                'type': 'external',
                'provider': 'cohere',
                'model_id': 'command',
                'description': 'Cohere\'s Command model',
                'max_length': 4096,
                'temperature': 0.7,
                'requires_api_key': True
            }
        }
    
    def get_available_models(self) -> List[Dict]:
        """Get list of available models with their status"""
        models = []
        
        for model_id, config in self.model_configs.items():
            model_info = {
                'id': model_id,
                'name': config['name'],
                'type': config['type'],
                'description': config['description'],
                'is_loaded': model_id in self.loaded_models,
                'is_available': self._check_model_availability(config),
                'config': config
            }
            models.append(model_info)
        
        return models
    
    def _check_model_availability(self, config: Dict) -> bool:
        """Check if a model is available for loading"""
        if config['type'] == 'local':
            if not TRANSFORMERS_AVAILABLE:
                return False
            # For local models, we assume they can be downloaded
            return True
        elif config['type'] == 'external':
            if config['provider'] == 'openai':
                return OPENAI_AVAILABLE and os.getenv('OPENAI_API_KEY')
            elif config['provider'] == 'cohere':
                return COHERE_AVAILABLE and os.getenv('COHERE_API_KEY')
        return False
    
    def load_model(self, model_name: str) -> bool:
        """Load a specific model into memory"""
        if model_name not in self.model_configs:
            raise ValueError(f"Model {model_name} not found")
        
        if model_name in self.loaded_models:
            logger.info(f"Model {model_name} already loaded")
            return True
        
        config = self.model_configs[model_name]
        
        try:
            if config['type'] == 'local':
                return self._load_local_model(model_name, config)
            elif config['type'] == 'external':
                return self._load_external_model(model_name, config)
        except Exception as e:
            logger.error(f"Error loading model {model_name}: {e}")
            raise
        
        return False
    
    def _load_local_model(self, model_name: str, config: Dict) -> bool:
        """Load a local model using transformers"""
        if not TRANSFORMERS_AVAILABLE:
            raise ImportError("Transformers library not available")
        
        logger.info(f"Loading local model: {model_name}")
        
        try:
            # Load tokenizer
            tokenizer = AutoTokenizer.from_pretrained(
                config['model_id'],
                cache_dir=self.models_dir,
                trust_remote_code=True
            )
            
            # Load model
            model = AutoModelForCausalLM.from_pretrained(
                config['model_id'],
                cache_dir=self.models_dir,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map="auto" if torch.cuda.is_available() else None,
                trust_remote_code=True
            )
            
            # Create pipeline
            pipe = pipeline(
                "text-generation",
                model=model,
                tokenizer=tokenizer,
                device=0 if torch.cuda.is_available() else -1
            )
            
            self.loaded_models[model_name] = {
                'pipeline': pipe,
                'tokenizer': tokenizer,
                'model': model,
                'config': config,
                'loaded_at': datetime.now().isoformat()
            }
            
            logger.info(f"Successfully loaded model: {model_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading local model {model_name}: {e}")
            raise
    
    def _load_external_model(self, model_name: str, config: Dict) -> bool:
        """Load an external model configuration"""
        logger.info(f"Loading external model configuration: {model_name}")
        
        # For external models, we just store the configuration
        # The actual API calls will be made during inference
        self.loaded_models[model_name] = {
            'config': config,
            'loaded_at': datetime.now().isoformat(),
            'type': 'external'
        }
        
        logger.info(f"Successfully loaded external model config: {model_name}")
        return True
    
    def generate_response(self, model_name: str, prompt: str, **kwargs) -> str:
        """Generate a response using the specified model"""
        if model_name not in self.loaded_models:
            raise ValueError(f"Model {model_name} not loaded")
        
        model_data = self.loaded_models[model_name]
        config = model_data['config']
        
        try:
            if config['type'] == 'local':
                return self._generate_local_response(model_name, prompt, **kwargs)
            elif config['type'] == 'external':
                return self._generate_external_response(model_name, prompt, **kwargs)
        except Exception as e:
            logger.error(f"Error generating response with {model_name}: {e}")
            raise
        
        return ""
    
    def _generate_local_response(self, model_name: str, prompt: str, **kwargs) -> str:
        """Generate response using local model"""
        model_data = self.loaded_models[model_name]
        pipeline = model_data['pipeline']
        config = model_data['config']
        
        # Set default parameters
        max_length = kwargs.get('max_length', config.get('max_length', 2048))
        temperature = kwargs.get('temperature', config.get('temperature', 0.7))
        
        # Generate response
        response = pipeline(
            prompt,
            max_length=max_length,
            temperature=temperature,
            do_sample=True,
            pad_token_id=pipeline.tokenizer.eos_token_id,
            **kwargs
        )
        
        # Extract generated text
        generated_text = response[0]['generated_text']
        
        # Remove the original prompt from the response
        if generated_text.startswith(prompt):
            generated_text = generated_text[len(prompt):].strip()
        
        return generated_text
    
    def _generate_external_response(self, model_name: str, prompt: str, **kwargs) -> str:
        """Generate response using external API"""
        model_data = self.loaded_models[model_name]
        config = model_data['config']
        
        if config['provider'] == 'openai':
            return self._generate_openai_response(model_name, prompt, **kwargs)
        elif config['provider'] == 'cohere':
            return self._generate_cohere_response(model_name, prompt, **kwargs)
        
        raise ValueError(f"Unknown external provider: {config['provider']}")
    
    def _generate_openai_response(self, model_name: str, prompt: str, **kwargs) -> str:
        """Generate response using OpenAI API"""
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI library not available")
        
        config = self.loaded_models[model_name]['config']
        
        try:
            response = openai.ChatCompletion.create(
                model=config['model_id'],
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=kwargs.get('max_length', config.get('max_length', 4096)),
                temperature=kwargs.get('temperature', config.get('temperature', 0.7)),
                **kwargs
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
    
    def _generate_cohere_response(self, model_name: str, prompt: str, **kwargs) -> str:
        """Generate response using Cohere API"""
        if not COHERE_AVAILABLE:
            raise ImportError("Cohere library not available")
        
        config = self.loaded_models[model_name]['config']
        
        try:
            co = cohere.Client(os.getenv('COHERE_API_KEY'))
            response = co.generate(
                model=config['model_id'],
                prompt=prompt,
                max_tokens=kwargs.get('max_length', config.get('max_length', 4096)),
                temperature=kwargs.get('temperature', config.get('temperature', 0.7)),
                **kwargs
            )
            
            return response.generations[0].text
            
        except Exception as e:
            logger.error(f"Cohere API error: {e}")
            raise
    
    def unload_model(self, model_name: str) -> bool:
        """Unload a model from memory"""
        if model_name not in self.loaded_models:
            return False
        
        try:
            model_data = self.loaded_models[model_name]
            
            if model_data['config']['type'] == 'local':
                # Clear GPU memory for local models
                if 'model' in model_data:
                    del model_data['model']
                if 'pipeline' in model_data:
                    del model_data['pipeline']
                if 'tokenizer' in model_data:
                    del model_data['tokenizer']
                
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
            
            del self.loaded_models[model_name]
            logger.info(f"Successfully unloaded model: {model_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error unloading model {model_name}: {e}")
            return False
    
    def get_loaded_models(self) -> List[str]:
        """Get list of currently loaded models"""
        return list(self.loaded_models.keys())
    
    def get_model_info(self, model_name: str) -> Optional[Dict]:
        """Get information about a specific model"""
        if model_name not in self.loaded_models:
            return None
        
        model_data = self.loaded_models[model_name]
        return {
            'name': model_name,
            'config': model_data['config'],
            'loaded_at': model_data['loaded_at'],
            'type': model_data['config']['type']
        }
