import os
import json
import shutil
import requests
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from datetime import datetime
import threading
import time

from src.models.settings_model import AIModel, SettingsModel

class AIModelService:
    """Service for managing AI models following MVVM pattern"""
    
    def __init__(self):
        self.settings_model = SettingsModel()
        self.models_dir = Path("src/ai_local_models")
        self.models_dir.mkdir(exist_ok=True)
        self.download_threads = {}
    
    def get_all_models(self) -> Dict[str, List[AIModel]]:
        """Get all models organized by type (local/external)"""
        models = self.settings_model.get_ai_models()
        
        local_models = []
        external_models = []
        
        for model in models:
            if model.provider.lower() == 'local':
                local_models.append(model)
            else:
                external_models.append(model)
        
        return {
            'local_models': local_models,
            'external_models': external_models
        }
    
    def get_model_by_id(self, model_id: str) -> Optional[AIModel]:
        """Get a specific model by ID"""
        models = self.settings_model.get_ai_models()
        for model in models:
            if model.model_id == model_id:
                return model
        return None
    
    def download_model(self, model_id: str) -> Dict[str, any]:
        """Download a model asynchronously"""
        model = self.get_model_by_id(model_id)
        if not model:
            return {'success': False, 'message': 'Model not found'}
        
        if model.is_downloaded:
            return {'success': False, 'message': 'Model already downloaded'}
        
        # Check if download is already in progress
        if model_id in self.download_threads and self.download_threads[model_id].is_alive():
            return {'success': False, 'message': 'Download already in progress'}
        
        # Start download in background thread
        thread = threading.Thread(target=self._download_model_thread, args=(model,))
        thread.daemon = True
        thread.start()
        
        self.download_threads[model_id] = thread
        
        # Update status
        self.settings_model.update_model_status(model_id, 'downloading')
        
        return {'success': True, 'message': 'Download started'}
    
    def _download_model_thread(self, model: AIModel):
        """Background thread for downloading model"""
        try:
            # Create model directory
            model_dir = self.models_dir / model.model_id
            model_dir.mkdir(exist_ok=True)
            
            # Download model files
            if model.download_url:
                self._download_from_url(model, model_dir)
            else:
                self._download_from_config(model, model_dir)
            
            # Update status
            self.settings_model.update_model_status(model.model_id, 'available', True)
            
        except Exception as e:
            print(f"Error downloading model {model.model_id}: {e}")
            self.settings_model.update_model_status(model.model_id, 'error')
    
    def _download_from_url(self, model: AIModel, model_dir: Path):
        """Download model from URL"""
        response = requests.get(model.download_url, stream=True)
        response.raise_for_status()
        
        # Determine file extension
        content_type = response.headers.get('content-type', '')
        if 'json' in content_type:
            ext = '.json'
        elif 'bin' in content_type or 'octet-stream' in content_type:
            ext = '.bin'
        else:
            ext = '.model'
        
        model_file = model_dir / f"{model.model_id}{ext}"
        
        with open(model_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
    
    def _download_from_config(self, model: AIModel, model_dir: Path):
        """Download model using configuration"""
        config_path = Path(model.config_path)
        if config_path.exists():
            # Copy from local config location
            shutil.copy2(config_path, model_dir / config_path.name)
        else:
            raise FileNotFoundError(f"Model config not found: {config_path}")
    
    def delete_model(self, model_id: str) -> Dict[str, any]:
        """Delete a downloaded model"""
        model = self.get_model_by_id(model_id)
        if not model:
            return {'success': False, 'message': 'Model not found'}
        
        if not model.is_downloaded:
            return {'success': False, 'message': 'Model not downloaded'}
        
        try:
            # Remove model directory
            model_dir = self.models_dir / model_id
            if model_dir.exists():
                shutil.rmtree(model_dir)
            
            # Update status
            self.settings_model.update_model_status(model_id, 'not_installed', False)
            
            return {'success': True, 'message': 'Model deleted successfully'}
            
        except Exception as e:
            return {'success': False, 'message': f'Error deleting model: {e}'}
    
    def update_model(self, model_id: str) -> Dict[str, any]:
        """Update a model"""
        model = self.get_model_by_id(model_id)
        if not model:
            return {'success': False, 'message': 'Model not found'}
        
        if not model.is_downloaded:
            return {'success': False, 'message': 'Model not downloaded'}
        
        # Delete and re-download
        delete_result = self.delete_model(model_id)
        if not delete_result['success']:
            return delete_result
        
        return self.download_model(model_id)
    
    def get_model_status(self, model_id: str) -> Dict[str, any]:
        """Get detailed model status"""
        model = self.get_model_by_id(model_id)
        if not model:
            return {'success': False, 'message': 'Model not found'}
        
        model_dir = self.models_dir / model_id
        files = []
        
        if model_dir.exists():
            for file_path in model_dir.iterdir():
                if file_path.is_file():
                    files.append({
                        'name': file_path.name,
                        'size': file_path.stat().st_size,
                        'modified': datetime.fromtimestamp(file_path.stat().st_mtime)
                    })
        
        return {
            'success': True,
            'model': {
                'id': model.model_id,
                'name': model.name,
                'status': model.status,
                'is_downloaded': model.is_downloaded,
                'size': model.size,
                'provider': model.provider,
                'last_updated': model.last_updated,
                'files': files
            }
        }
    
    def get_download_progress(self, model_id: str) -> Dict[str, any]:
        """Get download progress for a model"""
        if model_id not in self.download_threads:
            return {'success': False, 'message': 'No download in progress'}
        
        thread = self.download_threads[model_id]
        if thread.is_alive():
            return {
                'success': True,
                'status': 'downloading',
                'progress': 'in_progress'  # In real implementation, track actual progress
            }
        else:
            # Check final status
            model = self.get_model_by_id(model_id)
            if model and model.is_downloaded:
                return {
                    'success': True,
                    'status': 'completed',
                    'progress': '100%'
                }
            else:
                return {
                    'success': True,
                    'status': 'failed',
                    'progress': '0%'
                }
    
    def validate_model_config(self, model_id: str) -> Dict[str, any]:
        """Validate model configuration"""
        model = self.get_model_by_id(model_id)
        if not model:
            return {'success': False, 'message': 'Model not found'}
        
        validation_results = {
            'model_id': model_id,
            'name': model.name,
            'valid': True,
            'issues': []
        }
        
        # Check required fields
        if not model.name:
            validation_results['issues'].append('Model name is required')
            validation_results['valid'] = False
        
        if not model.model_id:
            validation_results['issues'].append('Model ID is required')
            validation_results['valid'] = False
        
        # Check if model files exist if downloaded
        if model.is_downloaded:
            model_dir = self.models_dir / model_id
            if not model_dir.exists():
                validation_results['issues'].append('Model directory not found')
                validation_results['valid'] = False
            else:
                # Check for model files
                files = list(model_dir.iterdir())
                if not files:
                    validation_results['issues'].append('No model files found')
                    validation_results['valid'] = False
        
        return {
            'success': True,
            'validation': validation_results
        }
    
    def get_model_config(self, model_id: str) -> Dict[str, any]:
        """Get model configuration"""
        model = self.get_model_by_id(model_id)
        if not model:
            return {'success': False, 'message': 'Model not found'}
        
        config_path = Path(model.config_path)
        config = {}
        
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
            except Exception as e:
                config = {'error': f'Failed to load config: {e}'}
        
        return {
            'success': True,
            'model_id': model_id,
            'config': config
        }
    
    def update_model_config(self, model_id: str, config: Dict) -> Dict[str, any]:
        """Update model configuration"""
        model = self.get_model_by_id(model_id)
        if not model:
            return {'success': False, 'message': 'Model not found'}
        
        try:
            config_path = Path(model.config_path)
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            return {'success': True, 'message': 'Configuration updated'}
            
        except Exception as e:
            return {'success': False, 'message': f'Error updating config: {e}'}
