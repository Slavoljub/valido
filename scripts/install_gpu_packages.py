#!/usr/bin/env python3
"""
GPU Package Installation Script
Automatically detects and installs appropriate GPU packages for AI/ML workloads
"""

import subprocess
import sys
import platform
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GPUPackageInstaller:
    def __init__(self):
        self.system = platform.system()
        self.cuda_available = self.check_cuda()
        self.rocm_available = self.check_rocm()
        self.metal_available = self.check_metal()
        
    def check_cuda(self):
        """Check if CUDA is available"""
        try:
            result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    def check_rocm(self):
        """Check if ROCm is available (AMD GPUs)"""
        try:
            result = subprocess.run(['rocm-smi'], capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    def check_metal(self):
        """Check if Metal Performance Shaders are available (Apple Silicon)"""
        return self.system == "Darwin" and platform.machine() == "arm64"
    
    def run_command(self, command, description):
        """Run a command with logging"""
        logger.info(f"Running: {description}")
        logger.info(f"Command: {' '.join(command)}")
        
        try:
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            logger.info(f"✅ {description} completed successfully")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ {description} failed: {e}")
            logger.error(f"Error output: {e.stderr}")
            return False
    
    def install_base_packages(self):
        """Install base packages required for all setups"""
        logger.info("Installing base AI/ML packages...")
        
        base_packages = [
            "torch>=2.6.0",
            "transformers>=4.35.0",
            "sentence-transformers>=2.2.2",
            "accelerate>=0.24.1",
            "huggingface-hub>=0.16.0",
            "datasets>=2.12.0",
            "librosa>=0.10.0",
            "soundfile>=0.12.0"
        ]
        
        for package in base_packages:
            self.run_command([sys.executable, "-m", "pip", "install", package], f"Installing {package}")
    
    def install_cuda_packages(self):
        """Install CUDA-specific packages"""
        logger.info("Installing CUDA packages...")
        
        # Install PyTorch with CUDA support
        cuda_commands = [
            [sys.executable, "-m", "pip", "install", "torch", "torchvision", "torchaudio", "--index-url", "https://download.pytorch.org/whl/cu121"],
            [sys.executable, "-m", "pip", "install", "nvidia-ml-py3>=7.352.0"],
            [sys.executable, "-m", "pip", "install", "pynvml>=11.4.1"],
            [sys.executable, "-m", "pip", "install", "bitsandbytes>=0.41.1"],
        ]
        
        for command in cuda_commands:
            self.run_command(command, f"Installing CUDA package: {command[-1] if not command[-1].startswith('https') else 'PyTorch CUDA'}")
        
        # Install llama-cpp-python with CUDA support
        os.environ["CMAKE_ARGS"] = "-DLLAMA_CUBLAS=on"
        self.run_command(
            [sys.executable, "-m", "pip", "install", "llama-cpp-python[server]", "--force-reinstall", "--no-cache-dir"],
            "Installing llama-cpp-python with CUDA support"
        )
    
    def install_rocm_packages(self):
        """Install ROCm-specific packages (AMD GPUs)"""
        logger.info("Installing ROCm packages...")
        
        rocm_commands = [
            [sys.executable, "-m", "pip", "install", "torch", "torchvision", "torchaudio", "--index-url", "https://download.pytorch.org/whl/rocm5.6"],
        ]
        
        for command in rocm_commands:
            self.run_command(command, f"Installing ROCm package")
        
        # Install llama-cpp-python with ROCm support
        os.environ["CMAKE_ARGS"] = "-DLLAMA_HIPBLAS=on"
        self.run_command(
            [sys.executable, "-m", "pip", "install", "llama-cpp-python[server]", "--force-reinstall", "--no-cache-dir"],
            "Installing llama-cpp-python with ROCm support"
        )
    
    def install_metal_packages(self):
        """Install Metal-specific packages (Apple Silicon)"""
        logger.info("Installing Metal packages...")
        
        # Install PyTorch with Metal support
        self.run_command(
            [sys.executable, "-m", "pip", "install", "torch", "torchvision", "torchaudio"],
            "Installing PyTorch with Metal support"
        )
        
        # Install llama-cpp-python with Metal support
        os.environ["CMAKE_ARGS"] = "-DLLAMA_METAL=on"
        self.run_command(
            [sys.executable, "-m", "pip", "install", "llama-cpp-python[server]", "--force-reinstall", "--no-cache-dir"],
            "Installing llama-cpp-python with Metal support"
        )
    
    def install_cpu_packages(self):
        """Install CPU-only packages"""
        logger.info("Installing CPU-only packages...")
        
        # Install CPU-only PyTorch
        self.run_command(
            [sys.executable, "-m", "pip", "install", "torch", "torchvision", "torchaudio", "--index-url", "https://download.pytorch.org/whl/cpu"],
            "Installing PyTorch CPU-only"
        )
        
        # Install llama-cpp-python CPU-only
        self.run_command(
            [sys.executable, "-m", "pip", "install", "llama-cpp-python[server]"],
            "Installing llama-cpp-python CPU-only"
        )
    
    def install_audio_packages(self):
        """Install audio processing packages"""
        logger.info("Installing audio processing packages...")
        
        audio_packages = [
            "openai-whisper>=20230314",
            "whisper>=1.1.10",
        ]
        
        # Try to install pyaudio (might need system dependencies)
        try:
            if self.system == "Windows":
                self.run_command([sys.executable, "-m", "pip", "install", "pyaudio"], "Installing PyAudio for Windows")
            elif self.system == "Darwin":
                logger.info("On macOS, you may need to install portaudio: brew install portaudio")
                self.run_command([sys.executable, "-m", "pip", "install", "pyaudio"], "Installing PyAudio for macOS")
            else:  # Linux
                logger.info("On Linux, you may need to install: sudo apt-get install portaudio19-dev python3-pyaudio")
                self.run_command([sys.executable, "-m", "pip", "install", "pyaudio"], "Installing PyAudio for Linux")
        except Exception as e:
            logger.warning(f"PyAudio installation failed: {e}. Audio input may not work.")
        
        for package in audio_packages:
            self.run_command([sys.executable, "-m", "pip", "install", package], f"Installing {package}")
    
    def install(self):
        """Main installation function"""
        logger.info("🚀 Starting GPU package installation...")
        logger.info(f"System: {self.system}")
        logger.info(f"CUDA Available: {self.cuda_available}")
        logger.info(f"ROCm Available: {self.rocm_available}")
        logger.info(f"Metal Available: {self.metal_available}")
        
        # Install base packages first
        self.install_base_packages()
        
        # Install GPU-specific packages
        if self.cuda_available:
            logger.info("🎮 Installing CUDA packages...")
            self.install_cuda_packages()
        elif self.rocm_available:
            logger.info("🔥 Installing ROCm packages...")
            self.install_rocm_packages()
        elif self.metal_available:
            logger.info("🍎 Installing Metal packages...")
            self.install_metal_packages()
        else:
            logger.info("💻 Installing CPU-only packages...")
            self.install_cpu_packages()
        
        # Install audio packages
        self.install_audio_packages()
        
        logger.info("✅ Installation completed!")
        
        # Verify installation
        self.verify_installation()
    
    def verify_installation(self):
        """Verify that packages are installed correctly"""
        logger.info("🔍 Verifying installation...")
        
        try:
            import torch
            logger.info(f"✅ PyTorch version: {torch.__version__}")
            logger.info(f"✅ CUDA available: {torch.cuda.is_available()}")
            if torch.cuda.is_available():
                logger.info(f"✅ CUDA device count: {torch.cuda.device_count()}")
                for i in range(torch.cuda.device_count()):
                    logger.info(f"   Device {i}: {torch.cuda.get_device_name(i)}")
            
            # Check MPS (Metal Performance Shaders) for Apple Silicon
            if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                logger.info("✅ Metal Performance Shaders available")
        except ImportError:
            logger.error("❌ PyTorch not found")
        
        try:
            import transformers
            logger.info(f"✅ Transformers version: {transformers.__version__}")
        except ImportError:
            logger.error("❌ Transformers not found")
        
        try:
            import llama_cpp
            logger.info(f"✅ llama-cpp-python installed")
        except ImportError:
            logger.error("❌ llama-cpp-python not found")

if __name__ == "__main__":
    installer = GPUPackageInstaller()
    installer.install()
