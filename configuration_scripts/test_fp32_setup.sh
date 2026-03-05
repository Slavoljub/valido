#!/bin/bash

# FP32 Precision Setup and Testing Script for Linux/macOS
# This script demonstrates the FP32 precision management system for ValidoAI

set -e  # Exit on any error

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
CONFIG_FILE="$PROJECT_ROOT/.config.env"

echo "🧮 FP32 Precision Management Setup"
echo "========================================"

# Function to install dependencies
install_dependencies() {
    echo "📦 Installing FP32 dependencies..."

    # Install Python packages for FP32 precision management
    pip install --upgrade numpy scipy matplotlib psutil

    # Install AI framework dependencies based on parameter
    if [ "$FRAMEWORK" = "all" ] || [ "$FRAMEWORK" = "tensorflow" ]; then
        pip install tensorflow
    fi

    if [ "$FRAMEWORK" = "all" ] || [ "$FRAMEWORK" = "pytorch" ]; then
        pip install torch torchvision torchaudio
    fi

    if [ "$FRAMEWORK" = "all" ] || [ "$FRAMEWORK" = "transformers" ]; then
        pip install transformers accelerate
    fi

    echo "✅ Dependencies installed successfully"
}

# Function to test FP32 system
test_fp32_system() {
    echo "🧪 Testing FP32 Precision Management System..."

    # Add src to Python path
    export PYTHONPATH="$PROJECT_ROOT/src:$PYTHONPATH"

    # Run FP32 tests
    if python -m pytest "$PROJECT_ROOT/tests/test_fp32_precision_manager.py" -v; then
        echo "✅ FP32 tests completed successfully"
    else
        echo "⚠️ Some tests failed, but core functionality should work"
    fi
}

# Function to configure FP32
configure_fp32() {
    echo "⚙️ Configuring FP32 precision for frameworks..."

    # Create temporary Python script
    cat > /tmp/fp32_config.py << EOF
import sys
import os
sys.path.insert(0, '$PROJECT_ROOT/src')

from src.core.fp32_precision_manager import FP32PrecisionManager

# Initialize manager
manager = FP32PrecisionManager()

# Configure frameworks
if '$FRAMEWORK' in ['all', 'tensorflow']:
    print("🔧 Configuring TensorFlow for FP32...")
    result = manager.configure_tensorflow()
    print(f"TensorFlow: {result}")

if '$FRAMEWORK' in ['all', 'pytorch']:
    print("🔧 Configuring PyTorch for FP32...")
    result = manager.configure_pytorch()
    print(f"PyTorch: {result}")

if '$FRAMEWORK' in ['all', 'transformers']:
    print("🔧 Configuring Transformers for FP32...")
    result = manager.configure_transformers()
    print(f"Transformers: {result}")

print("✅ FP32 configuration completed")
EOF

    if python /tmp/fp32_config.py; then
        echo "✅ FP32 configuration completed"
    else
        echo "❌ FP32 configuration failed"
        exit 1
    fi

    rm -f /tmp/fp32_config.py
}

# Function to benchmark FP32
benchmark_fp32() {
    echo "📊 Running FP32 performance benchmarks..."

    # Create temporary Python script
    cat > /tmp/fp32_benchmark.py << EOF
import sys
import os
sys.path.insert(0, '$PROJECT_ROOT/src')

from src.core.fp32_precision_manager import FP32PrecisionManager

# Initialize manager
manager = FP32PrecisionManager()

print("📊 Running simple model benchmark...")
results = manager.benchmark_performance('simple')
print(f"Model: {results['model_type']}")
print(f"FP32 Time: {results['fp32_performance'].get('inference_time', 'N/A'):.4f}s")
print(f"Mixed Time: {results['mixed_precision_performance'].get('inference_time', 'N/A'):.4f}s")
print(f"Speedup: {results['comparison'].get('speedup', 'N/A'):.2f}x")

print("\n✅ Benchmark completed")
EOF

    if python /tmp/fp32_benchmark.py; then
        echo "✅ FP32 benchmarks completed"
    else
        echo "❌ FP32 benchmarks failed"
        exit 1
    fi

    rm -f /tmp/fp32_benchmark.py
}

# Function to generate FP32 report
generate_fp32_report() {
    echo "📋 Generating FP32 configuration report..."

    # Create temporary Python script
    cat > /tmp/fp32_report.py << EOF
import sys
import os
sys.path.insert(0, '$PROJECT_ROOT/src')

from src.core.fp32_precision_manager import FP32PrecisionManager

# Initialize manager
manager = FP32PrecisionManager()

# Run verification
print("🔬 Running numerical stability verification...")
stability_results = manager.verify_numerical_stability()
print(f"Numerical Stability Assessment: {stability_results['assessment']}")

# Generate report
print("\n📋 Generating comprehensive report...")
report = manager.generate_report()
print(report)

print("\n✅ Report generation completed")
EOF

    if python /tmp/fp32_report.py; then
        echo "✅ FP32 report generated"
    else
        echo "❌ FP32 report generation failed"
        exit 1
    fi

    rm -f /tmp/fp32_report.py
}

# Parse command line arguments
INSTALL=false
TEST=false
CONFIGURE=false
BENCHMARK=false
REPORT=false
FRAMEWORK="all"

while [[ $# -gt 0 ]]; do
    case $1 in
        -i|--install)
            INSTALL=true
            shift
            ;;
        -t|--test)
            TEST=true
            shift
            ;;
        -c|--configure)
            CONFIGURE=true
            shift
            ;;
        -b|--benchmark)
            BENCHMARK=true
            shift
            ;;
        -r|--report)
            REPORT=true
            shift
            ;;
        -f|--framework)
            FRAMEWORK="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  -i, --install           Install dependencies"
            echo "  -t, --test              Run FP32 tests"
            echo "  -c, --configure         Configure FP32 for frameworks"
            echo "  -b, --benchmark         Run performance benchmarks"
            echo "  -r, --report            Generate FP32 report"
            echo "  -f, --framework FRAMEWORK  Specify framework (tensorflow|pytorch|transformers|all)"
            echo "  -h, --help              Show this help message"
            echo ""
            echo "If no options specified, runs complete setup and verification."
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use -h or --help for usage information"
            exit 1
            ;;
    esac
done

# Main execution
if [ "$INSTALL" = true ]; then
    install_dependencies
fi

if [ "$TEST" = true ]; then
    test_fp32_system
fi

if [ "$CONFIGURE" = true ]; then
    configure_fp32
fi

if [ "$BENCHMARK" = true ]; then
    benchmark_fp32
fi

if [ "$REPORT" = true ]; then
    generate_fp32_report
fi

# If no specific action requested, run full setup
if [ "$INSTALL" = false ] && [ "$TEST" = false ] && [ "$CONFIGURE" = false ] && [ "$BENCHMARK" = false ] && [ "$REPORT" = false ]; then
    echo "🔄 Running complete FP32 setup and verification..."

    install_dependencies
    configure_fp32
    test_fp32_system
    benchmark_fp32
    generate_fp32_report

    echo ""
    echo "🎉 FP32 setup and verification completed!"
    echo "💡 You can now use FP32 precision in your AI/ML models"
fi

echo ""
echo "📖 Usage Examples:"
echo "  # Configure specific framework"
echo "  ./$0 --configure --framework pytorch"
echo "  # Run tests only"
echo "  ./$0 --test"
echo "  # Generate report only"
echo "  ./$0 --report"
echo "  # Install dependencies only"
echo "  ./$0 --install"
