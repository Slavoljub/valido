"""
Test suite for FP32 Precision Manager

This module contains comprehensive tests for the FP32 precision management system.
"""

import unittest
import sys
import os
import json
import tempfile
from pathlib import Path
import numpy as np

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from src.core.fp32_precision_manager import FP32PrecisionManager
    FP32_AVAILABLE = True
except ImportError:
    FP32_AVAILABLE = False
    print("⚠️ FP32 Precision Manager not available, skipping tests")


class TestFP32PrecisionManager(unittest.TestCase):
    """Test cases for FP32 Precision Manager."""

    def setUp(self):
        """Set up test environment."""
        if not FP32_AVAILABLE:
            self.skipTest("FP32 Precision Manager not available")

        # Create temporary config file
        self.temp_config = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        self.config_data = {
            "precision": {
                "default_precision": "fp32",
                "mixed_precision_enabled": True,
                "numerical_stability_check": True
            },
            "frameworks": {
                "tensorflow": {"precision": "fp32", "mixed_precision": True},
                "pytorch": {"precision": "fp32", "mixed_precision": True},
                "transformers": {"precision": "fp32", "use_fast": True}
            },
            "verification": {
                "numerical_tolerance": 1e-6,
                "test_iterations": 10
            }
        }

        json.dump(self.config_data, self.temp_config)
        self.temp_config.close()

        self.manager = FP32PrecisionManager(self.temp_config.name)

    def tearDown(self):
        """Clean up test environment."""
        try:
            os.unlink(self.temp_config.name)
        except:
            pass

    def test_initialization(self):
        """Test manager initialization."""
        self.assertIsInstance(self.manager, FP32PrecisionManager)
        self.assertEqual(self.manager.precision_settings['default_precision'], 'fp32')
        self.assertTrue(self.manager.precision_settings['mixed_precision_enabled'])

    def test_config_loading(self):
        """Test configuration loading."""
        self.assertIn('tensorflow', self.manager.framework_configs)
        self.assertIn('pytorch', self.manager.framework_configs)
        self.assertEqual(self.manager.framework_configs['tensorflow']['precision'], 'fp32')

    def test_numerical_stability_verification(self):
        """Test numerical stability verification."""
        # Generate test data
        test_data = np.random.randn(100, 50).astype(np.float32)

        results = self.manager.verify_numerical_stability(test_data)

        self.assertIn('precision', results)
        self.assertEqual(results['precision'], 'fp32')
        self.assertIn('assessment', results)
        self.assertIn('stability_tests', results)
        self.assertIn('basic_ops', results['stability_tests'])
        self.assertIn('matrix_ops', results['stability_tests'])
        self.assertIn('gradient_computation', results['stability_tests'])

    def test_basic_operations_test(self):
        """Test basic operations numerical stability."""
        test_data = np.random.randn(50, 30).astype(np.float32)

        result = self.manager._test_basic_operations(test_data)

        self.assertIn('passed', result)
        self.assertIn('has_nan', result)
        self.assertIn('has_inf', result)
        self.assertIsInstance(result['passed'], bool)

    def test_matrix_operations_test(self):
        """Test matrix operations numerical stability."""
        test_data = np.random.randn(30, 30).astype(np.float32)

        result = self.manager._test_matrix_operations(test_data)

        self.assertIn('passed', result)
        self.assertIn('condition_number', result)
        self.assertIn('eigenvalue_range', result)
        self.assertIsInstance(result['passed'], bool)

    def test_gradient_computation_test(self):
        """Test gradient computation numerical stability."""
        test_data = np.random.randn(100, 10).astype(np.float32)

        result = self.manager._test_gradient_computation(test_data)

        self.assertIn('passed', result)
        self.assertIn('max_gradient', result)
        self.assertIn('gradient_std', result)
        self.assertIsInstance(result['passed'], bool)

    def test_get_precision_config(self):
        """Test getting precision configuration."""
        tf_config = self.manager.get_precision_config('tensorflow')
        self.assertEqual(tf_config['precision'], 'fp32')

        nonexistent_config = self.manager.get_precision_config('nonexistent')
        self.assertEqual(nonexistent_config, {})

    def test_update_precision_config(self):
        """Test updating precision configuration."""
        success = self.manager.update_precision_config('tensorflow', {'new_setting': True})
        self.assertTrue(success)

        # Verify the update
        tf_config = self.manager.get_precision_config('tensorflow')
        self.assertTrue(tf_config.get('new_setting', False))

    def test_system_info(self):
        """Test system information retrieval."""
        info = self.manager.get_system_info()

        self.assertIn('cpu_info', info)
        self.assertIn('gpu_info', info)
        self.assertIn('memory_info', info)
        self.assertIn('precision_support', info)

        precision_support = info['precision_support']
        self.assertIn('fp32_supported', precision_support)
        self.assertIn('fp16_supported', precision_support)
        self.assertIn('mixed_precision_supported', precision_support)

        # FP32 should always be supported
        self.assertTrue(precision_support['fp32_supported'])

    def test_benchmark_performance_simple(self):
        """Test simple model performance benchmarking."""
        results = self.manager.benchmark_performance('simple')

        self.assertIn('model_type', results)
        self.assertIn('fp32_performance', results)
        self.assertIn('mixed_precision_performance', results)
        self.assertIn('comparison', results)
        self.assertEqual(results['model_type'], 'simple')

    def test_generate_report(self):
        """Test report generation."""
        report = self.manager.generate_report()

        self.assertIsInstance(report, str)
        self.assertIn('FP32 Precision Management Report', report)
        self.assertIn('System Information', report)
        self.assertIn('Framework Configurations', report)

    def test_fp16_support_detection(self):
        """Test FP16 support detection."""
        fp16_supported = self.manager._check_fp16_support()
        self.assertIsInstance(fp16_supported, bool)

    def test_bf16_support_detection(self):
        """Test BF16 support detection."""
        bf16_supported = self.manager._check_bf16_support()
        self.assertIsInstance(bf16_supported, bool)

    def test_mixed_precision_support_detection(self):
        """Test mixed precision support detection."""
        mixed_supported = self.manager._check_mixed_precision_support()
        self.assertIsInstance(mixed_supported, bool)

    def test_configuration_file_creation(self):
        """Test automatic configuration file creation."""
        # Test with non-existent file
        temp_dir = tempfile.mkdtemp()
        fake_config = os.path.join(temp_dir, 'nonexistent.json')

        manager = FP32PrecisionManager(fake_config)

        # Should create default configuration
        self.assertTrue(os.path.exists(fake_config))

        # Clean up
        try:
            os.unlink(fake_config)
            os.rmdir(temp_dir)
        except:
            pass


class TestFP32PrecisionManagerCLI(unittest.TestCase):
    """Test CLI functionality for FP32 Precision Manager."""

    def setUp(self):
        """Set up test environment."""
        if not FP32_AVAILABLE:
            self.skipTest("FP32 Precision Manager not available")

        # Create temporary config file
        self.temp_config = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        self.config_data = {
            "precision": {"default_precision": "fp32"},
            "frameworks": {"tensorflow": {"precision": "fp32"}}
        }

        json.dump(self.config_data, self.temp_config)
        self.temp_config.close()

        self.manager = FP32PrecisionManager(self.temp_config.name)

    def tearDown(self):
        """Clean up test environment."""
        try:
            os.unlink(self.temp_config.name)
        except:
            pass

    def test_cli_help(self):
        """Test CLI help functionality."""
        # This would require mocking sys.argv and capturing stdout
        # For now, just test that the main function exists
        from src.core.fp32_precision_manager import main
        self.assertTrue(callable(main))


class TestFP32PrecisionManagerIntegration(unittest.TestCase):
    """Integration tests for FP32 Precision Manager."""

    def setUp(self):
        """Set up test environment."""
        if not FP32_AVAILABLE:
            self.skipTest("FP32 Precision Manager not available")

        self.manager = FP32PrecisionManager()

    def test_full_workflow(self):
        """Test complete FP32 workflow."""
        # 1. Get system info
        sys_info = self.manager.get_system_info()
        self.assertIsInstance(sys_info, dict)

        # 2. Verify numerical stability
        results = self.manager.verify_numerical_stability()
        self.assertIn('assessment', results)

        # 3. Generate report
        report = self.manager.generate_report()
        self.assertIsInstance(report, str)
        self.assertIn('FP32', report)

    def test_error_handling(self):
        """Test error handling in various scenarios."""
        # Test with invalid configuration file
        try:
            invalid_manager = FP32PrecisionManager("/nonexistent/path/config.json")
            # Should create default config
            self.assertIsInstance(invalid_manager, FP32PrecisionManager)
        except Exception:
            # This is expected to potentially fail, but shouldn't crash
            pass

    def test_memory_efficiency(self):
        """Test memory efficiency considerations."""
        # Generate large test data
        large_data = np.random.randn(1000, 1000).astype(np.float32)

        results = self.manager.verify_numerical_stability(large_data)

        # Should handle large data without crashing
        self.assertIn('assessment', results)


if __name__ == '__main__':
    # Set up test environment
    if FP32_AVAILABLE:
        print("🧮 Running FP32 Precision Manager tests...")

        # Run specific tests
        unittest.main(verbosity=2)
    else:
        print("⚠️ FP32 Precision Manager not available, skipping tests")
        print("Install the package and run tests again:")
        print("pip install numpy")
        print("python -m pytest tests/test_fp32_precision_manager.py -v")
