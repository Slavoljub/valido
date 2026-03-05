# ValidoAI Master Configuration Scripts

This directory contains unified configuration scripts for setting up and managing the ValidoAI project across all platforms (Windows, Linux, and macOS).

## 📋 Available Scripts

### Cross-Platform Scripts

#### `validoai_master_config.ps1` (PowerShell)
Primary script for Windows and WSL environments.

#### `validoai_master_config.sh` (Bash)
Primary script for Linux and macOS environments.

## 🚀 Quick Start

### Windows / WSL
```powershell
# Complete setup
.\validoai_master_config.ps1 -Action setup

# Health check only
.\validoai_master_config.ps1 -Action health

# Optimize source code
.\validoai_master_config.ps1 -Action optimize -Force
```

### Linux / macOS
```bash
# Complete setup
./validoai_master_config.sh ACTION=setup

# Health check only
./validoai_master_config.sh ACTION=health

# Optimize source code
./validoai_master_config.sh ACTION=optimize FORCE=true
```

## 📊 Consolidation Results

### Before Consolidation
- **40+ individual scripts** with overlapping functionality
- **Multiple PostgreSQL setup scripts** (10+ variants)
- **Redundant cleanup and optimization scripts**
- **Scattered documentation** across multiple files
- **No unified cross-platform approach**

### After Consolidation
- **8 essential files** total (reduced by 80%)
- **2 master configuration scripts** (Windows + Linux/macOS)
- **Archived 6 documentation files** for future reference
- **Unified functionality** with consistent interfaces
- **Cross-platform compatibility** with automatic detection

### Space Saved
- **Removed 32 redundant scripts**
- **Archived 6 documentation files**
- **Maintained all functionality** in streamlined format
- **Improved maintainability** with single source of truth

## 🎯 Available Actions

| Action | Description |
|--------|-------------|
| `setup` | Complete system setup (Python, Julia, PostgreSQL, optimization) |
| `health` | System health check and diagnostics |
| `optimize` | Analyze and optimize source code structure |
| `clean` | Remove unused files following DRY principles |
| `julia` | Setup Julia environment with all required packages |
| `python` | Setup Python virtual environment and dependencies |
| `postgres` | Setup PostgreSQL database and extensions |

## ⚙️ Configuration Options

### PowerShell Script Options
```powershell
# Skip specific components
.\validoai_master_config.ps1 -Action setup -SkipDatabase -SkipJulia

# Dry run mode (see what would be done)
.\validoai_master_config.ps1 -Action optimize -DryRun

# Force operations without confirmation
.\validoai_master_config.ps1 -Action clean -Force
```

### Bash Script Options
```bash
# Skip specific components
./validoai_master_config.sh ACTION=setup SKIP_DATABASE=true SKIP_JULIA=true

# Dry run mode (see what would be done)
./validoai_master_config.sh ACTION=optimize DRY_RUN=true

# Force operations without confirmation
./validoai_master_config.sh ACTION=clean FORCE=true
```

## 🔧 What Each Script Does

### System Health Check
- ✅ Detects platform (Windows, Linux, macOS, WSL)
- ✅ Checks for required tools (Python, Julia, PostgreSQL, Git, Docker, Node.js)
- ✅ Reports system status with color-coded output

### Python Environment Setup
- ✅ Creates virtual environment (`validoai_env`)
- ✅ Installs all requirements from `requirements.txt`
- ✅ Verifies installation success

### Julia Environment Setup
- ✅ Installs Julia (if not present)
- ✅ Sets up Julia project with comprehensive package list
- ✅ Includes data science, ML, AI, and visualization packages

### PostgreSQL Database Setup
- ✅ Finds PostgreSQL installation automatically
- ✅ Tests database connection
- ✅ Creates `ai_valido_online` database
- ✅ Installs essential extensions (`uuid-ossp`, `pgcrypto`, `postgis`, `plpython3u`)

### Source Code Optimization
- ✅ Analyzes Python file structure in `src/` directory
- ✅ Reports file sizes and optimization opportunities
- ✅ Creates backup before making changes
- ✅ Identifies large files (>100KB) and small files (<1KB)

### Source Code Cleanup
- ✅ Identifies unused Python files
- ✅ Maintains list of known required files
- ✅ Removes redundant files following DRY principles
- ✅ Provides dry-run mode for safe preview

## 📊 Julia Packages Included

The script installs a comprehensive set of Julia packages:

### Core Data Processing
- DataFrames, CSV, JSON, HTTP, Sockets
- LibPQ, MySQL, Mongoc, Redis, SearchLight
- SQLite, ODBC, JLD2, HDF5, Arrow, Parquet

### Machine Learning & AI
- MLJ, Flux, Turing, Distributions, Statistics
- Optim, JuMP, LightGraphs, MetaGraphs
- OpenAI, Anthropic, GoogleGenAI, Cohere
- HuggingFace, Transformers, SentenceTransformers

### Computer Vision & Media
- ImageIO, Images, ImageFiltering, ImageFeatures
- ComputerVision, Metalhead, FluxVision
- AudioIO, WAV, MP3, LibSndFile, SampledSignals

### Financial & Time Series
- TimeSeries, Temporal, BusinessDays, MarketData
- FinancialModelingPrep, AlphaVantage, CoinMarketCap

## 🗂️ File Organization

## Configuration Scripts Directory Structure

After consolidation and cleanup, the directory now contains only essential files:

```
configuration_scripts/
├── validoai_master_config.ps1    # Windows master config script
├── validoai_master_config.sh     # Linux/macOS master config script
├── start_hypercorn.sh            # Hypercorn server startup
├── start_uvicorn.sh              # Uvicorn server startup
├── README.md                     # This documentation
├── README_ValidoAI_PostgreSQL_Setup.md  # PostgreSQL setup guide
└── archived_docs/                # Archived documentation
    ├── validoai_advanced_features_plan.md
    ├── validoai_current_state_assessment.md
    ├── validoai_final_consolidation_plan.md
    ├── validoai_final_status_report.md
    ├── validoai_final_truthful_summary.md
    └── validoai_truthful_assessment.md
```

## Source Code Structure (after optimization)

```
src/
├── config/
│   ├── master_config.py    # Unified configuration
│   └── __init__.py
├── core/
│   ├── global_logger.py    # Logging system
│   ├── lazy_importer.py    # Import optimization
│   └── __init__.py
├── models/
│   ├── unified_models.py   # All models consolidated
│   └── __init__.py
├── controllers/
│   └── __init__.py
├── ai/
│   ├── sentiment.py        # AI functionality
│   └── __init__.py
├── database.py             # Database management
├── routes.py              # All routes
└── app.py                 # Main application
```

## 🔒 Security Features

- Environment variable validation
- Secure credential handling for PostgreSQL
- Backup creation before file operations
- Confirmation prompts for destructive operations

## 🚨 Error Handling

- Comprehensive error checking at each step
- Color-coded output for easy issue identification
- Graceful fallback when optional components fail
- Detailed logging of all operations

## 📈 Performance Optimizations

- Lazy loading for heavy imports
- File size analysis for optimization opportunities
- Parallel operations where possible
- Memory-efficient processing

## 🔄 Backup and Recovery

- Automatic backup creation before optimization
- Timestamped backup directories
- Easy rollback capabilities
- Non-destructive dry-run mode

## 🎨 Platform-Specific Features

### Windows
- PowerShell-native operations
- Windows-specific path handling
- WSL integration support
- Windows installer support for Julia

### Linux
- Native bash operations
- System package manager integration
- Docker support
- WSL compatibility

### macOS
- Homebrew integration
- macOS-specific paths
- Native Julia installation via Homebrew

## 🐛 Troubleshooting

### Common Issues

1. **PostgreSQL not found**
   - Ensure PostgreSQL is installed and in PATH
   - Check if service is running

2. **Julia installation fails**
   - Check internet connection
   - Verify disk space (>2GB recommended)

3. **Python virtual environment issues**
   - Ensure python3-venv is installed
   - Check write permissions in current directory

4. **Permission errors**
   - Run with appropriate privileges
   - Check file/directory permissions

### Debug Mode

Enable verbose output:
```bash
# Bash
export VERBOSE=true
./validoai_master_config.sh ACTION=setup

# PowerShell
$VerbosePreference = "Continue"
.\validoai_master_config.ps1 -Action setup -Verbose
```

## 📝 Logging

All operations are logged with timestamps and can be found in:
- PowerShell: `src_optimization.log` (when using optimize action)
- Bash: Console output with color coding

## 🤝 Contributing

When adding new configuration options:

1. Update both PowerShell and Bash scripts
2. Maintain consistent parameter naming
3. Add appropriate help documentation
4. Test on all supported platforms
5. Update this README

## 📄 License

These scripts are part of the ValidoAI project and follow the same license terms.
