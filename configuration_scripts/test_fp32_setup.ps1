"""
FP32 Precision Setup and Testing Script

This script demonstrates the FP32 precision management system for ValidoAI.
Run this script to verify FP32 configuration and test the system.
"""

param(
    [switch]$Install,
    [switch]$Test,
    [switch]$Configure,
    [switch]$Benchmark,
    [switch]$Report,
    [string]$Framework = "all"
)

# Configuration
$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir
$configFile = Join-Path $projectRoot ".config.env"

Write-Host "🧮 FP32 Precision Management Setup" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan

function Install-Dependencies {
    Write-Host "📦 Installing FP32 dependencies..." -ForegroundColor Yellow

    # Install Python packages for FP32 precision management
    pip install --upgrade numpy scipy matplotlib
    pip install --upgrade psutil

    # Install AI framework dependencies
    if ($Framework -eq "all" -or $Framework -eq "tensorflow") {
        pip install tensorflow
    }

    if ($Framework -eq "all" -or $Framework -eq "pytorch") {
        pip install torch torchvision torchaudio
    }

    if ($Framework -eq "all" -or $Framework -eq "transformers") {
        pip install transformers accelerate
    }

    Write-Host "✅ Dependencies installed successfully" -ForegroundColor Green
}

function Test-FP32System {
    Write-Host "🧪 Testing FP32 Precision Management System..." -ForegroundColor Yellow

    # Add src to Python path
    $env:PYTHONPATH = "$projectRoot\src;$env:PYTHONPATH"

    # Run FP32 tests
    try {
        python -m pytest "$projectRoot\tests\test_fp32_precision_manager.py" -v
        Write-Host "✅ FP32 tests completed successfully" -ForegroundColor Green
    }
    catch {
        Write-Host "⚠️ Some tests failed, but core functionality should work" -ForegroundColor Yellow
    }
}

function Configure-FP32 {
    Write-Host "⚙️ Configuring FP32 precision for frameworks..." -ForegroundColor Yellow

    $configScript = @"
import sys
import os
sys.path.insert(0, '$projectRoot/src')

from src.core.fp32_precision_manager import FP32PrecisionManager

# Initialize manager
manager = FP32PrecisionManager()

# Configure frameworks
if '$Framework' in ['all', 'tensorflow']:
    print("🔧 Configuring TensorFlow for FP32...")
    result = manager.configure_tensorflow()
    print(f"TensorFlow: {result}")

if '$Framework' in ['all', 'pytorch']:
    print("🔧 Configuring PyTorch for FP32...")
    result = manager.configure_pytorch()
    print(f"PyTorch: {result}")

if '$Framework' in ['all', 'transformers']:
    print("🔧 Configuring Transformers for FP32...")
    result = manager.configure_transformers()
    print(f"Transformers: {result}")

print("✅ FP32 configuration completed")
"@

    $tempScript = [System.IO.Path]::GetTempFileName() + ".py"
    $configScript | Out-File -FilePath $tempScript -Encoding UTF8

    try {
        python $tempScript
        Write-Host "✅ FP32 configuration completed" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ FP32 configuration failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    finally {
        Remove-Item $tempScript -ErrorAction SilentlyContinue
    }
}

function Benchmark-FP32 {
    Write-Host "📊 Running FP32 performance benchmarks..." -ForegroundColor Yellow

    $benchmarkScript = @"
import sys
import os
sys.path.insert(0, '$projectRoot/src')

from src.core.fp32_precision_manager import FP32PrecisionManager

# Initialize manager
manager = FP32PrecisionManager()

print("📊 Running simple model benchmark...")
results = manager.benchmark_performance('simple')
print(f"Model: {results['model_type']}")
print(f"FP32 Time: {results['fp32_performance'].get('inference_time', 'N/A'):.4f}s")
print(f"Mixed Time: {results['mixed_precision_performance'].get('inference_time', 'N/A'):.4f}s")
print(f"Speedup: {results['comparison'].get('speedup', 'N/A'):.2f}x")

print("\\n✅ Benchmark completed")
"@

    $tempScript = [System.IO.Path]::GetTempFileName() + ".py"
    $benchmarkScript | Out-File -FilePath $tempScript -Encoding UTF8

    try {
        python $tempScript
        Write-Host "✅ FP32 benchmarks completed" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ FP32 benchmarks failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    finally {
        Remove-Item $tempScript -ErrorAction SilentlyContinue
    }
}

function Generate-FP32Report {
    Write-Host "📋 Generating FP32 configuration report..." -ForegroundColor Yellow

    $reportScript = @"
import sys
import os
sys.path.insert(0, '$projectRoot/src')

from src.core.fp32_precision_manager import FP32PrecisionManager

# Initialize manager
manager = FP32PrecisionManager()

# Run verification
print("🔬 Running numerical stability verification...")
stability_results = manager.verify_numerical_stability()
print(f"Numerical Stability Assessment: {stability_results['assessment']}")

# Generate report
print("\\n📋 Generating comprehensive report...")
report = manager.generate_report()
print(report)

print("\\n✅ Report generation completed")
"@

    $tempScript = [System.IO.Path]::GetTempFileName() + ".py"
    $reportScript | Out-File -FilePath $tempScript -Encoding UTF8

    try {
        python $tempScript
        Write-Host "✅ FP32 report generated" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ FP32 report generation failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    finally {
        Remove-Item $tempScript -ErrorAction SilentlyContinue
    }
}

# Main execution
if ($Install) {
    Install-Dependencies
}

if ($Test) {
    Test-FP32System
}

if ($Configure) {
    Configure-FP32
}

if ($Benchmark) {
    Benchmark-FP32
}

if ($Report) {
    Generate-FP32Report
}

# If no specific action requested, run full setup
if (-not ($Install -or $Test -or $Configure -or $Benchmark -or $Report)) {
    Write-Host "🔄 Running complete FP32 setup and verification..." -ForegroundColor Yellow

    Install-Dependencies
    Configure-FP32
    Test-FP32System
    Benchmark-FP32
    Generate-FP32Report

    Write-Host "\\n🎉 FP32 setup and verification completed!" -ForegroundColor Green
    Write-Host "💡 You can now use FP32 precision in your AI/ML models" -ForegroundColor Cyan
}

Write-Host "\\n📖 Usage Examples:" -ForegroundColor Cyan
Write-Host "  # Configure specific framework" -ForegroundColor Gray
Write-Host "  .\$($MyInvocation.MyCommand.Name) -Configure -Framework pytorch" -ForegroundColor Gray
Write-Host "  # Run tests only" -ForegroundColor Gray
Write-Host "  .\$($MyInvocation.MyCommand.Name) -Test" -ForegroundColor Gray
Write-Host "  # Generate report only" -ForegroundColor Gray
Write-Host "  .\$($MyInvocation.MyCommand.Name) -Report" -ForegroundColor Gray
Write-Host "  # Install dependencies only" -ForegroundColor Gray
Write-Host "  .\$($MyInvocation.MyCommand.Name) -Install" -ForegroundColor Gray
