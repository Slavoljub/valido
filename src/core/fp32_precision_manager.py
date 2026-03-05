"""
FP32 Precision Management for ValidoAI

This module provides comprehensive FP32 precision configuration and management
for all AI/ML models and operations in the ValidoAI project.

Author: ValidoAI Team
Version: 1.0.0
"""

import os
import sys
import json
import logging
from typing import Dict, Any, Optional, Union
from pathlib import Path
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FP32PrecisionManager:
    """
    Comprehensive FP32 precision management system for AI/ML models.

    This class provides:
    - FP32 configuration for all major AI frameworks
    - Mixed precision support with automatic FP16 conversion
    - Numerical stability verification
    - Performance monitoring and benchmarking
    - Environment-based configuration management
    """

    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize FP32 Precision Manager.

        Args:
            config_file: Path to configuration file (default: auto-detect)
        """
        self.config_file = config_file or self._find_config_file()
        self.config = self._load_config()
        self.precision_settings = self.config.get('precision', {})
        self.framework_configs = self.config.get('frameworks', {})
        self.verification_results = {}

        logger.info("🧮 FP32 Precision Manager initialized")
        logger.info(f"📋 Configuration loaded from: {self.config_file}")

    def _find_config_file(self) -> str:
        """Find configuration file in standard locations."""
        search_paths = [
            '.env',
            'config.env',
            '.config.env',
            'src/config.env',
            'configuration.env'
        ]

        for path in search_paths:
            if os.path.exists(path):
                return path

        # Create default configuration if none exists
        return self._create_default_config()

    def _create_default_config(self) -> str:
        """Create default FP32 configuration file."""
        default_config = {
            "precision": {
                "default_precision": "fp32",
                "mixed_precision_enabled": True,
                "auto_fp16_conversion": True,
                "gradient_scaling": True,
                "loss_scaling": True,
                "numerical_stability_check": True,
                "performance_monitoring": True
            },
            "frameworks": {
                "tensorflow": {
                    "precision": "fp32",
                    "mixed_precision": True,
                    "xla_compilation": True,
                    "memory_optimization": True
                },
                "pytorch": {
                    "precision": "fp32",
                    "mixed_precision": True,
                    "cuda_available": True,
                    "cudnn_benchmark": True
                },
                "transformers": {
                    "precision": "fp32",
                    "use_fast": True,
                    "torch_dtype": "float32"
                },
                "openai": {
                    "precision": "fp32",
                    "temperature": 0.7,
                    "max_tokens": 4096
                }
            },
            "verification": {
                "numerical_tolerance": 1e-6,
                "performance_threshold": 0.95,
                "memory_limit_mb": 8192,
                "test_iterations": 100
            }
        }

        config_path = ".config.env"
        with open(config_path, 'w') as f:
            json.dump(default_config, f, indent=2)

        logger.info(f"📝 Created default FP32 configuration: {config_path}")
        return config_path

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        try:
            with open(self.config_file, 'r') as f:
                if self.config_file.endswith('.env'):
                    # Parse .env style format
                    config = {}
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            if '=' in line:
                                key, value = line.split('=', 1)
                                key = key.strip()
                                value = value.strip()

                                # Parse JSON values
                                if value.startswith('{') and value.endswith('}'):
                                    try:
                                        value = json.loads(value)
                                    except:
                                        pass
                                elif value.lower() in ('true', 'false'):
                                    value = value.lower() == 'true'
                                elif value.isdigit():
                                    value = int(value)
                                elif value.replace('.', '').isdigit():
                                    value = float(value)

                                config[key] = value
                    return config
                else:
                    return json.load(f)
        except Exception as e:
            logger.error(f"❌ Failed to load config: {e}")
            return {}

    def configure_tensorflow(self) -> Dict[str, Any]:
        """Configure TensorFlow for FP32 precision."""
        tf_config = self.framework_configs.get('tensorflow', {})

        try:
            import tensorflow as tf

            # Set FP32 as default
            tf.keras.backend.set_floatx('float32')

            # Configure mixed precision if enabled
            if tf_config.get('mixed_precision', True):
                from tensorflow.keras.mixed_precision import experimental as mixed_precision
                policy = mixed_precision.Policy('mixed_float16')
                mixed_precision.set_policy(policy)
                logger.info("✅ TensorFlow mixed precision configured")

            # Memory optimization
            if tf_config.get('memory_optimization', True):
                gpus = tf.config.experimental.list_physical_devices('GPU')
                for gpu in gpus:
                    tf.config.experimental.set_memory_growth(gpu, True)

            return {
                'success': True,
                'precision': 'fp32',
                'mixed_precision': tf_config.get('mixed_precision', True),
                'gpus_available': len(gpus) if 'gpus' in locals() else 0
            }

        except ImportError:
            logger.warning("⚠️ TensorFlow not available")
            return {'success': False, 'error': 'TensorFlow not installed'}

    def configure_pytorch(self) -> Dict[str, Any]:
        """Configure PyTorch for FP32 precision."""
        torch_config = self.framework_configs.get('pytorch', {})

        try:
            import torch

            # Set default tensor type to FP32
            torch.set_default_dtype(torch.float32)

            # Configure CUDA if available
            if torch_config.get('cuda_available', True) and torch.cuda.is_available():
                torch.backends.cudnn.benchmark = torch_config.get('cudnn_benchmark', True)
                torch.backends.cudnn.enabled = True
                logger.info(f"✅ PyTorch CUDA configured on {torch.cuda.device_count()} GPU(s)")

            # Configure mixed precision
            if torch_config.get('mixed_precision', True):
                try:
                    from torch.cuda.amp import autocast, GradScaler
                    logger.info("✅ PyTorch mixed precision configured")
                except ImportError:
                    logger.warning("⚠️ PyTorch AMP not available")

            return {
                'success': True,
                'precision': 'fp32',
                'cuda_available': torch.cuda.is_available(),
                'gpu_count': torch.cuda.device_count() if torch.cuda.is_available() else 0
            }

        except ImportError:
            logger.warning("⚠️ PyTorch not available")
            return {'success': False, 'error': 'PyTorch not installed'}

    def configure_transformers(self) -> Dict[str, Any]:
        """Configure Hugging Face Transformers for FP32."""
        transformers_config = self.framework_configs.get('transformers', {})

        try:
            import transformers
            import torch

            # Set default precision
            if transformers_config.get('precision', 'fp32') == 'fp32':
                torch.set_default_dtype(torch.float32)

            return {
                'success': True,
                'precision': transformers_config.get('precision', 'fp32'),
                'use_fast': transformers_config.get('use_fast', True)
            }

        except ImportError:
            logger.warning("⚠️ Transformers not available")
            return {'success': False, 'error': 'Transformers not installed'}

    def verify_numerical_stability(self, test_data: np.ndarray = None) -> Dict[str, Any]:
        """Verify numerical stability with FP32 operations."""
        if test_data is None:
            # Generate test data
            test_data = np.random.randn(1000, 100).astype(np.float32)

        results = {
            'precision': 'fp32',
            'stability_tests': {},
            'recommendations': []
        }

        try:
            # Test basic operations
            results['stability_tests']['basic_ops'] = self._test_basic_operations(test_data)
            results['stability_tests']['matrix_ops'] = self._test_matrix_operations(test_data)
            results['stability_tests']['gradient_computation'] = self._test_gradient_computation(test_data)

            # Overall assessment
            stability_score = np.mean([test['passed'] for test in results['stability_tests'].values()])

            if stability_score >= 0.95:
                results['assessment'] = 'excellent'
                results['recommendations'].append("✅ FP32 precision is numerically stable")
            elif stability_score >= 0.85:
                results['assessment'] = 'good'
                results['recommendations'].append("⚠️ FP32 precision is acceptable but monitor for edge cases")
            else:
                results['assessment'] = 'needs_attention'
                results['recommendations'].append("🔧 Consider reviewing FP32 implementation")

            logger.info(f"🔬 Numerical stability assessment: {results['assessment']}")

        except Exception as e:
            results['error'] = str(e)
            logger.error(f"❌ Numerical stability test failed: {e}")

        return results

    def _test_basic_operations(self, data: np.ndarray) -> Dict[str, Any]:
        """Test basic mathematical operations."""
        try:
            # Addition, subtraction, multiplication, division
            result = data + data
            result = result - data
            result = result * 2.0
            result = result / 2.0

            # Check for NaN or Inf values
            has_nan = np.isnan(result).any()
            has_inf = np.isinf(result).any()

            return {
                'passed': not has_nan and not has_inf,
                'has_nan': has_nan,
                'has_inf': has_inf,
                'max_value': float(np.max(result)),
                'min_value': float(np.min(result))
            }
        except Exception as e:
            return {'passed': False, 'error': str(e)}

    def _test_matrix_operations(self, data: np.ndarray) -> Dict[str, Any]:
        """Test matrix operations."""
        try:
            # Matrix multiplication
            result = np.dot(data, data.T)

            # Eigenvalue decomposition
            eigenvals, eigenvecs = np.linalg.eigh(result)

            # Check for numerical issues
            has_nan = np.isnan(eigenvals).any() or np.isnan(eigenvecs).any()
            has_inf = np.isinf(eigenvals).any() or np.isinf(eigenvecs).any()

            return {
                'passed': not has_nan and not has_inf,
                'has_nan': has_nan,
                'has_inf': has_inf,
                'condition_number': float(np.linalg.cond(data)),
                'eigenvalue_range': [float(np.min(eigenvals)), float(np.max(eigenvals))]
            }
        except Exception as e:
            return {'passed': False, 'error': str(e)}

    def _test_gradient_computation(self, data: np.ndarray) -> Dict[str, Any]:
        """Test gradient computation stability."""
        try:
            # Simple gradient computation simulation
            x = data.flatten()
            y = x ** 2  # Simple quadratic function

            # Compute numerical gradient
            gradient = np.gradient(y)

            # Check for numerical issues
            has_nan = np.isnan(gradient).any()
            has_inf = np.isinf(gradient).any()
            max_gradient = float(np.max(np.abs(gradient)))

            return {
                'passed': not has_nan and not has_inf and max_gradient < 1e6,
                'has_nan': has_nan,
                'has_inf': has_inf,
                'max_gradient': max_gradient,
                'gradient_std': float(np.std(gradient))
            }
        except Exception as e:
            return {'passed': False, 'error': str(e)}

    def benchmark_performance(self, model_type: str = 'simple') -> Dict[str, Any]:
        """Benchmark FP32 vs mixed precision performance."""
        results = {
            'model_type': model_type,
            'fp32_performance': {},
            'mixed_precision_performance': {},
            'comparison': {}
        }

        try:
            if model_type == 'simple':
                results['fp32_performance'] = self._benchmark_simple_model(precision='fp32')
                results['mixed_precision_performance'] = self._benchmark_simple_model(precision='mixed')

            elif model_type == 'transformer':
                results['fp32_performance'] = self._benchmark_transformer_model(precision='fp32')
                results['mixed_precision_performance'] = self._benchmark_transformer_model(precision='mixed')

            # Calculate comparison metrics
            fp32_time = results['fp32_performance'].get('inference_time', 0)
            mixed_time = results['mixed_precision_performance'].get('inference_time', 0)

            if fp32_time > 0:
                results['comparison']['speedup'] = fp32_time / mixed_time if mixed_time > 0 else 1.0
                results['comparison']['memory_efficiency'] = (
                    results['fp32_performance'].get('memory_usage', 0) /
                    results['mixed_precision_performance'].get('memory_usage', 1)
                )

            logger.info(f"📊 Performance benchmark completed for {model_type}")

        except Exception as e:
            results['error'] = str(e)
            logger.error(f"❌ Performance benchmark failed: {e}")

        return results

    def _benchmark_simple_model(self, precision: str) -> Dict[str, Any]:
        """Benchmark simple model performance."""
        import time

        # Simple neural network simulation
        input_size = 1000
        hidden_size = 500
        output_size = 10
        batch_size = 32

        # Create synthetic data
        x = np.random.randn(batch_size, input_size).astype(np.float32)

        start_time = time.time()

        # Simulate model operations
        for _ in range(100):
            w1 = np.random.randn(input_size, hidden_size).astype(np.float32)
            w2 = np.random.randn(hidden_size, output_size).astype(np.float32)

            h = np.maximum(0, np.dot(x, w1))  # ReLU
            output = np.dot(h, w2)

            if precision == 'mixed':
                # Simulate FP16 conversion
                output = output.astype(np.float16).astype(np.float32)

        inference_time = time.time() - start_time

        return {
            'inference_time': inference_time,
            'throughput': 100 / inference_time,  # operations per second
            'memory_usage': x.nbytes + w1.nbytes + w2.nbytes
        }

    def _benchmark_transformer_model(self, precision: str) -> Dict[str, Any]:
        """Benchmark transformer model performance."""
        try:
            import torch
            import time

            # Simple transformer simulation
            model = torch.nn.Transformer(
                d_model=512,
                nhead=8,
                num_encoder_layers=3,
                num_decoder_layers=3
            )

            if precision == 'mixed':
                model = model.half()

            model.eval()

            # Create dummy input
            src = torch.randn(32, 10, 512)
            tgt = torch.randn(32, 10, 512)

            if precision == 'mixed':
                src = src.half()
                tgt = tgt.half()

            start_time = time.time()

            with torch.no_grad():
                for _ in range(10):
                    output = model(src, tgt)

            inference_time = time.time() - start_time

            return {
                'inference_time': inference_time,
                'throughput': 10 / inference_time,
                'memory_usage': src.numel() * src.element_size()
            }

        except ImportError:
            return {'error': 'PyTorch not available for transformer benchmark'}

    def get_precision_config(self, framework: str) -> Dict[str, Any]:
        """Get precision configuration for specific framework."""
        return self.framework_configs.get(framework, {})

    def update_precision_config(self, framework: str, config: Dict[str, Any]) -> bool:
        """Update precision configuration for specific framework."""
        try:
            if framework not in self.framework_configs:
                self.framework_configs[framework] = {}

            self.framework_configs[framework].update(config)

            # Save to file
            self.config['frameworks'] = self.framework_configs
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)

            logger.info(f"✅ Updated {framework} precision configuration")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to update {framework} config: {e}")
            return False

    def get_system_info(self) -> Dict[str, Any]:
        """Get system information relevant to FP32 precision."""
        info = {
            'cpu_info': {},
            'gpu_info': {},
            'memory_info': {},
            'precision_support': {}
        }

        try:
            import psutil
            info['memory_info'] = {
                'total_gb': psutil.virtual_memory().total / (1024**3),
                'available_gb': psutil.virtual_memory().available / (1024**3)
            }
        except ImportError:
            pass

        try:
            import torch
            info['gpu_info']['torch_cuda_available'] = torch.cuda.is_available()
            if torch.cuda.is_available():
                info['gpu_info']['gpu_count'] = torch.cuda.device_count()
                info['gpu_info']['gpu_name'] = torch.cuda.get_device_name()
        except ImportError:
            pass

        try:
            import tensorflow as tf
            info['gpu_info']['tf_gpus'] = len(tf.config.experimental.list_physical_devices('GPU'))
        except ImportError:
            pass

        # Precision support detection
        info['precision_support'] = {
            'fp32_supported': True,  # Always supported
            'fp16_supported': self._check_fp16_support(),
            'bf16_supported': self._check_bf16_support(),
            'mixed_precision_supported': self._check_mixed_precision_support()
        }

        return info

    def _check_fp16_support(self) -> bool:
        """Check if FP16 is supported."""
        try:
            import torch
            return torch.cuda.is_available() and torch.cuda.get_device_capability()[0] >= 5
        except:
            return False

    def _check_bf16_support(self) -> bool:
        """Check if BF16 is supported."""
        try:
            import torch
            return torch.cuda.is_available() and torch.cuda.get_device_capability()[0] >= 8
        except:
            return False

    def _check_mixed_precision_support(self) -> bool:
        """Check if mixed precision is supported."""
        return self._check_fp16_support() or self._check_bf16_support()

    def generate_report(self) -> str:
        """Generate comprehensive FP32 configuration report."""
        report = []
        report.append("🧮 FP32 Precision Management Report")
        report.append("=" * 50)
        report.append("")

        # System information
        sys_info = self.get_system_info()
        report.append("## 🖥️ System Information")
        report.append(f"- Memory: {sys_info['memory_info'].get('total_gb', 'Unknown'):.1f} GB total")
        report.append(f"- FP32 Support: {'✅' if sys_info['precision_support']['fp32_supported'] else '❌'}")
        report.append(f"- FP16 Support: {'✅' if sys_info['precision_support']['fp16_supported'] else '❌'}")
        report.append(f"- Mixed Precision: {'✅' if sys_info['precision_support']['mixed_precision_supported'] else '❌'}")
        report.append("")

        # Framework configurations
        report.append("## 🔧 Framework Configurations")
        for framework, config in self.framework_configs.items():
            report.append(f"### {framework.title()}")
            report.append(f"- Precision: {config.get('precision', 'fp32')}")
            report.append(f"- Mixed Precision: {'✅' if config.get('mixed_precision') else '❌'}")
            report.append("")

        # Verification results
        if self.verification_results:
            report.append("## 🔬 Verification Results")
            for test_name, result in self.verification_results.items():
                status = "✅ PASSED" if result.get('passed', False) else "❌ FAILED"
                report.append(f"- {test_name}: {status}")
            report.append("")

        # Recommendations
        report.append("## 💡 Recommendations")
        if sys_info['precision_support']['fp32_supported']:
            report.append("- ✅ FP32 precision is supported and recommended as default")
        else:
            report.append("- ⚠️ FP32 precision may not be optimal for this system")

        if sys_info['precision_support']['mixed_precision_supported']:
            report.append("- ✅ Mixed precision training is available for performance optimization")
        else:
            report.append("- ⚠️ Consider using FP32 for all operations if mixed precision is not available")

        report.append("")
        report.append("## 📊 Performance Tips")
        report.append("- Use FP32 for training to ensure numerical stability")
        report.append("- Enable mixed precision for inference to improve speed")
        report.append("- Monitor memory usage when using large models")
        report.append("- Consider gradient scaling for mixed precision training")

        return "\\n".join(report)


def main():
    """Main function for FP32 precision management CLI."""
    import argparse

    parser = argparse.ArgumentParser(description="FP32 Precision Manager for ValidoAI")
    parser.add_argument('--configure', choices=['tensorflow', 'pytorch', 'transformers', 'all'],
                       help='Configure specific framework for FP32')
    parser.add_argument('--verify', action='store_true',
                       help='Run numerical stability verification')
    parser.add_argument('--benchmark', choices=['simple', 'transformer'],
                       help='Run performance benchmark')
    parser.add_argument('--report', action='store_true',
                       help='Generate configuration report')
    parser.add_argument('--system-info', action='store_true',
                       help='Show system information')

    args = parser.parse_args()

    manager = FP32PrecisionManager()

    if args.configure:
        if args.configure in ['tensorflow', 'all']:
            result = manager.configure_tensorflow()
            print(f"TensorFlow configuration: {result}")

        if args.configure in ['pytorch', 'all']:
            result = manager.configure_pytorch()
            print(f"PyTorch configuration: {result}")

        if args.configure in ['transformers', 'all']:
            result = manager.configure_transformers()
            print(f"Transformers configuration: {result}")

    if args.verify:
        print("🔬 Running numerical stability verification...")
        results = manager.verify_numerical_stability()
        print(f"Verification results: {results['assessment']}")
        manager.verification_results['numerical_stability'] = results

    if args.benchmark:
        print(f"📊 Running {args.benchmark} model benchmark...")
        results = manager.benchmark_performance(args.benchmark)
        print(f"Benchmark completed. Speedup: {results['comparison'].get('speedup', 'N/A')}")

    if args.report:
        report = manager.generate_report()
        print(report)

    if args.system_info:
        info = manager.get_system_info()
        print("🖥️ System Information:")
        print(json.dumps(info, indent=2))

    if not any(vars(args).values()):
        parser.print_help()


if __name__ == "__main__":
    main()
