#!/usr/bin/env python3
"""
ValidoAI AI/ML Operations (DRY Implementation)
Consolidated AI model management, downloads, and operations
"""

import os
import sys
import json
import requests
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional
import urllib.parse

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

class AIModelManager:
    """Consolidated AI/ML operations manager"""

    def __init__(self):
        self.models_dir = Path("local_llm_models")
        self.models_dir.mkdir(exist_ok=True)
        self.config_file = Path("local_models_config.json")

        # Default model configurations
        self.default_models = {
            "qwen-3": {
                "name": "Qwen 3B",
                "url": "https://huggingface.co/Qwen/Qwen2-4B-Instruct-GGUF/resolve/main/qwen2-4b-instruct-q4_k_m.gguf",
                "size": "4GB",
                "type": "chat",
                "description": "Qwen 4B instruction-tuned model"
            },
            "phi-3": {
                "name": "Phi-3 Mini",
                "url": "https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf/resolve/main/phi-3-mini-4k-instruct-q4.gguf",
                "size": "2.3GB",
                "type": "chat",
                "description": "Microsoft Phi-3 mini model"
            },
            "mistral-7b": {
                "name": "Mistral 7B",
                "url": "https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF/resolve/main/mistral-7b-instruct-v0.1.Q4_K_M.gguf",
                "size": "4.1GB",
                "type": "chat",
                "description": "Mistral 7B instruction model"
            }
        }

        self.load_config()

    def load_config(self):
        """Load AI models configuration"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
            except Exception as e:
                print(f"Warning: Could not load config file: {e}")
                self.config = {"models": {}, "settings": {}}
        else:
            self.config = {"models": {}, "settings": {}}

    def save_config(self):
        """Save AI models configuration"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            print("✅ Configuration saved")
        except Exception as e:
            print(f"❌ Error saving configuration: {e}")

    def download_file(self, url: str, filename: str, show_progress: bool = True) -> bool:
        """Download file with progress tracking"""
        try:
            response = requests.get(url, stream=True, timeout=300)
            response.raise_for_status()
            total_size = int(response.headers.get('content-length', 0))

            with open(filename, 'wb') as file:
                if show_progress and total_size > 0:
                    from tqdm import tqdm
                    with tqdm(total=total_size, unit='B', unit_scale=True, desc=Path(filename).name) as pbar:
                        for data in response.iter_content(chunk_size=8192):
                            file.write(data)
                            pbar.update(len(data))
                else:
                    for data in response.iter_content(chunk_size=8192):
                        file.write(data)

            return True
        except Exception as e:
            print(f"❌ Error downloading {url}: {e}")
            return False

    def download_model(self, model_key: str, force: bool = False):
        """Download a specific AI model"""
        if model_key not in self.default_models:
            print(f"❌ Model '{model_key}' not found. Available models:")
            for key, info in self.default_models.items():
                print(f"  - {key}: {info['name']} ({info['size']})")
            return False

        model_info = self.default_models[model_key]
        model_path = self.models_dir / f"{model_key}.gguf"

        if model_path.exists() and not force:
            print(f"✅ Model {model_info['name']} already exists at {model_path}")
            return True

        print(f"📥 Downloading {model_info['name']} ({model_info['size']})...")

        if self.download_file(model_info['url'], str(model_path)):
            # Update configuration
            self.config["models"][model_key] = {
                "name": model_info['name'],
                "path": str(model_path),
                "downloaded": True,
                "size": model_info['size'],
                "type": model_info['type'],
                "url": model_info['url']
            }
            self.save_config()
            print(f"✅ Model {model_info['name']} downloaded successfully")
            return True
        else:
            print(f"❌ Failed to download {model_info['name']}")
            return False

    def download_all_models(self, force: bool = False):
        """Download all available AI models"""
        print("🚀 Starting download of all AI models...")

        success_count = 0
        total_count = len(self.default_models)

        for model_key in self.default_models.keys():
            if self.download_model(model_key, force):
                success_count += 1

        print(f"📊 Download Summary: {success_count}/{total_count} models downloaded successfully")

        if success_count == total_count:
            print("🎉 All AI models downloaded successfully!")
        else:
            print(f"⚠️  {total_count - success_count} models failed to download")

    def list_models(self, detailed: bool = False):
        """List available and downloaded models"""
        print("🤖 AI Models Status")
        print("=" * 50)

        for model_key, model_info in self.default_models.items():
            model_path = self.models_dir / f"{model_key}.gguf"
            exists = model_path.exists()
            status = "✅ Downloaded" if exists else "❌ Not Downloaded"

            if detailed:
                print(f"\n{model_info['name']} ({model_key})")
                print(f"  Status: {status}")
                print(f"  Size: {model_info['size']}")
                print(f"  Type: {model_info['type']}")
                print(f"  Description: {model_info['description']}")
                if exists:
                    size_mb = model_path.stat().st_size / (1024 * 1024)
                    print(f"  File Size: {size_mb:.1f} MB")
                    print(f"  Location: {model_path}")
            else:
                print("<15")

    def remove_model(self, model_key: str):
        """Remove a specific AI model"""
        if model_key not in self.default_models:
            print(f"❌ Model '{model_key}' not found")
            return False

        model_info = self.default_models[model_key]
        model_path = self.models_dir / f"{model_key}.gguf"

        if not model_path.exists():
            print(f"⚠️  Model {model_info['name']} is not downloaded")
            return True

        try:
            model_path.unlink()
            print(f"✅ Model {model_info['name']} removed successfully")

            # Update configuration
            if model_key in self.config["models"]:
                self.config["models"][model_key]["downloaded"] = False
                self.save_config()

            return True
        except Exception as e:
            print(f"❌ Error removing model: {e}")
            return False

    def clean_models(self):
        """Remove all downloaded models"""
        print("🧹 Cleaning all AI models...")

        removed_count = 0
        for model_key in self.default_models.keys():
            if self.remove_model(model_key):
                removed_count += 1

        print(f"✅ Cleaned {removed_count} AI models")

        # Reset configuration
        self.config["models"] = {}
        self.save_config()

    def get_model_info(self, model_key: str = None):
        """Get information about models"""
        if model_key:
            if model_key in self.default_models:
                model_info = self.default_models[model_key].copy()
                model_path = self.models_dir / f"{model_key}.gguf"
                model_info["downloaded"] = model_path.exists()
                model_info["path"] = str(model_path)
                return model_info
            else:
                return None
        else:
            # Return all models info
            all_info = {}
            for key, info in self.default_models.items():
                model_path = self.models_dir / f"{key}.gguf"
                all_info[key] = info.copy()
                all_info[key]["downloaded"] = model_path.exists()
                all_info[key]["path"] = str(model_path)
            return all_info

    def verify_models(self):
        """Verify integrity of downloaded models"""
        print("🔍 Verifying AI models...")

        verification_results = {}

        for model_key, model_info in self.default_models.items():
            model_path = self.models_dir / f"{model_key}.gguf"

            if not model_path.exists():
                verification_results[model_key] = {
                    "status": "missing",
                    "message": "Model file not found"
                }
                continue

            # Basic file integrity check
            file_size = model_path.stat().st_size
            min_expected_size = 100 * 1024 * 1024  # 100MB minimum

            if file_size < min_expected_size:
                verification_results[model_key] = {
                    "status": "corrupted",
                    "message": f"File size too small: {file_size} bytes"
                }
            else:
                verification_results[model_key] = {
                    "status": "valid",
                    "message": f"Model appears valid ({file_size} bytes)"
                }

        # Print results
        for model_key, result in verification_results.items():
            status_emoji = {
                "valid": "✅",
                "missing": "❌",
                "corrupted": "⚠️"
            }
            print(f"{status_emoji[result['status']]} {self.default_models[model_key]['name']}: {result['message']}")

        return verification_results

    def setup_server_config(self, model_key: str, port: int = 8000):
        """Generate server configuration for a model"""
        if model_key not in self.default_models:
            print(f"❌ Model '{model_key}' not found")
            return False

        model_info = self.default_models[model_key]
        model_path = self.models_dir / f"{model_key}.gguf"

        if not model_path.exists():
            print(f"❌ Model {model_info['name']} is not downloaded")
            return False

        # Create server configuration
        config = {
            "model": str(model_path),
            "model_alias": model_info['name'],
            "host": "127.0.0.1",
            "port": port,
            "n_ctx": 4096,
            "n_threads": -1,
            "n_batch": 512,
            "n_gpu_layers": 0,  # Set to >0 for GPU acceleration
            "main_gpu": 0,
            "tensor_split": "0.0",
            "seed": -1,
            "n_predict": -1,
            "n_keep": 0,
            "tfs_z": 1.0,
            "typical_p": 1.0,
            "repeat_penalty": 1.1,
            "repeat_last_n": 64,
            "presence_penalty": 0.0,
            "frequency_penalty": 0.0,
            "mirostat": 0,
            "mirostat_tau": 5.0,
            "mirostat_eta": 0.1,
            "memory_f16": true,
            "mlock": false,
            "mmap": true,
            "vocab_only": false,
            "use_mmap": true,
            "use_mlock": false
        }

        config_file = self.models_dir / f"{model_key}_server_config.json"
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)

        print(f"✅ Server configuration created: {config_file}")
        print(f"📝 To start the server:")
        print(f"   llama-server --config-file {config_file}")

        return True

def main():
    parser = argparse.ArgumentParser(description='ValidoAI AI/ML Operations')
    parser.add_argument('action', choices=[
        'download', 'download-all', 'list', 'remove', 'clean', 'verify', 'info', 'setup-server'
    ], help='Action to perform')
    parser.add_argument('--model', help='Specific model for actions')
    parser.add_argument('--force', action='store_true', help='Force download even if exists')
    parser.add_argument('--detailed', action='store_true', help='Show detailed information')
    parser.add_argument('--port', type=int, default=8000, help='Server port for setup-server')

    args = parser.parse_args()

    ai_manager = AIModelManager()

    try:
        if args.action == 'download':
            if not args.model:
                print("❌ Please specify a model with --model")
                sys.exit(1)
            ai_manager.download_model(args.model, args.force)

        elif args.action == 'download-all':
            ai_manager.download_all_models(args.force)

        elif args.action == 'list':
            ai_manager.list_models(args.detailed)

        elif args.action == 'remove':
            if not args.model:
                print("❌ Please specify a model with --model")
                sys.exit(1)
            ai_manager.remove_model(args.model)

        elif args.action == 'clean':
            ai_manager.clean_models()

        elif args.action == 'verify':
            ai_manager.verify_models()

        elif args.action == 'info':
            if args.model:
                info = ai_manager.get_model_info(args.model)
                if info:
                    print(json.dumps(info, indent=2))
                else:
                    print(f"❌ Model '{args.model}' not found")
            else:
                info = ai_manager.get_model_info()
                print(json.dumps(info, indent=2))

        elif args.action == 'setup-server':
            if not args.model:
                print("❌ Please specify a model with --model")
                sys.exit(1)
            ai_manager.setup_server_config(args.model, args.port)

        print("🎉 AI operation completed successfully!")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
