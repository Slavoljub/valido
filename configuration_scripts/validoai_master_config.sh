#!/bin/bash
# =============================================================================
# VALIDOAI - MASTER CONFIGURATION SCRIPT (Linux/macOS)
# =============================================================================
# Unified setup script for Linux and macOS
# Handles PostgreSQL, Julia, Python, optimization, and cleanup
# Following DRY principles and Cursor rules

set -e

# Configuration variables
ACTION="${ACTION:-setup}"
DRY_RUN="${DRY_RUN:-false}"
FORCE="${FORCE:-false}"
SKIP_DATABASE="${SKIP_DATABASE:-false}"
SKIP_JULIA="${SKIP_JULIA:-false}"
SKIP_PYTHON="${SKIP_PYTHON:-false}"
SKIP_OPTIMIZATION="${SKIP_OPTIMIZATION:-false}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

print_colored() {
    local message="$1"
    local color="$2"
    echo -e "${color}${message}${NC}"
}

print_header() {
    echo
    print_colored "==================================================" "$MAGENTA"
    print_colored " $1" "$MAGENTA"
    print_colored "==================================================" "$MAGENTA"
    echo
}

print_status() { print_colored "[INFO] $1" "$BLUE"; }
print_success() { print_colored "[SUCCESS] $1" "$GREEN"; }
print_warning() { print_colored "[WARNING] $1" "$YELLOW"; }
print_error() { print_colored "[ERROR] $1" "$RED"; }

command_exists() {
    command -v "$1" >/dev/null 2>&1
}

get_platform() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if [[ -n "$WSL_DISTRO_NAME" ]] || [[ -n "$WSLENV" ]] || [[ -n "$WSL_INTEROP" ]]; then
            echo "wsl"
        else
            echo "linux"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    else
        echo "unknown"
    fi
}

# =============================================================================
# PYTHON ENVIRONMENT MANAGEMENT
# =============================================================================

install_python_requirements() {
    print_status "Installing Python requirements..."

    if command_exists pip3; then
        pip3 install -r requirements.txt
        if [[ $? -eq 0 ]]; then
            print_success "Python requirements installed successfully"
        else
            print_error "Failed to install Python requirements"
            return 1
        fi
    elif command_exists pip; then
        pip install -r requirements.txt
        if [[ $? -eq 0 ]]; then
            print_success "Python requirements installed successfully"
        else
            print_error "Failed to install Python requirements"
            return 1
        fi
    else
        print_error "pip not found. Please install Python first."
        return 1
    fi
}

create_python_environment() {
    local env_name="${1:-validoai_env}"
    print_status "Creating Python virtual environment..."

    if command_exists python3; then
        python3 -m venv "$env_name"
        if [[ $? -eq 0 ]]; then
            print_success "Python virtual environment created: $env_name"
            print_status "Activating environment and installing requirements..."

            # Activate and install requirements
            source "$env_name/bin/activate"
            install_python_requirements
        else
            print_error "Failed to create Python virtual environment"
            return 1
        fi
    else
        print_error "python3 not found. Please install Python 3.8+ first."
        return 1
    fi
}

# =============================================================================
# JULIA ENVIRONMENT MANAGEMENT
# =============================================================================

install_julia() {
    local julia_version="${1:-1.9.4}"
    print_status "Installing Julia $julia_version..."

    local platform=$(get_platform)

    if [[ "$platform" == "macos" ]]; then
        # macOS installation
        if command_exists brew; then
            brew install julia
            print_success "Julia installed via Homebrew"
        else
            print_error "Homebrew not found. Please install Homebrew first."
            return 1
        fi
    elif [[ "$platform" == "linux" ]] || [[ "$platform" == "wsl" ]]; then
        # Linux/WSL installation
        local arch=$(uname -m)
        local julia_archive="julia-$julia_version-linux-$arch.tar.gz"
        local download_url="https://julialang-s3.julialang.org/bin/linux/$arch/1.9/$julia_archive"

        print_status "Downloading Julia from $download_url..."
        wget -O "/tmp/$julia_archive" "$download_url"

        print_status "Extracting Julia..."
        sudo tar -xzf "/tmp/$julia_archive" -C /opt/
        local julia_dir=$(tar -tf "/tmp/$julia_archive" | head -1 | cut -d/ -f1)
        sudo ln -sf "/opt/$julia_dir/bin/julia" /usr/local/bin/julia

        print_success "Julia installed on Linux"
    fi
}

setup_julia_environment() {
    print_status "Setting up Julia environment..."

    if command_exists julia; then
        # Create Julia project
        julia -e "
        using Pkg
        Pkg.add([
            \"DataFrames\", \"CSV\", \"JSON\", \"HTTP\", \"Sockets\",
            \"Plots\", \"StatsPlots\", \"MLJ\", \"Flux\", \"Turing\",
            \"Distributions\", \"Statistics\", \"Optim\", \"JuMP\",
            \"LightGraphs\", \"MetaGraphs\", \"GraphPlot\", \"NetworkLayout\",
            \"TimeSeries\", \"Temporal\", \"BusinessDays\", \"MarketData\",
            \"FinancialModelingPrep\", \"AlphaVantage\", \"CoinMarketCap\",
            \"OpenAI\", \"Anthropic\", \"GoogleGenAI\", \"Cohere\",
            \"HuggingFace\", \"Transformers\", \"SentenceTransformers\",
            \"Word2Vec\", \"GloVe\", \"FastText\", \"Doc2Vec\",
            \"ImageIO\", \"Images\", \"ImageFiltering\", \"ImageFeatures\",
            \"ComputerVision\", \"Metalhead\", \"FluxVision\",
            \"AudioIO\", \"WAV\", \"MP3\", \"LibSndFile\", \"SampledSignals\",
            \"Unicode\", \"StringEncodings\", \"Cyrillic\", \"PyCall\"
        ])
        "

        print_success "Julia packages installed successfully"
    else
        print_warning "Julia not found. Installing Julia first..."
        install_julia
        setup_julia_environment
    fi
}

# =============================================================================
# POSTGRESQL MANAGEMENT
# =============================================================================

find_postgres_path() {
    local possible_paths=(
        "/usr/bin/psql"
        "/usr/local/bin/psql"
        "/opt/homebrew/bin/psql"
        "/usr/lib/postgresql/*/bin/psql"
    )

    for path_pattern in "${possible_paths[@]}"; do
        # Use find to locate psql executable
        local psql_path=$(find $path_pattern 2>/dev/null | head -1)
        if [[ -n "$psql_path" ]] && [[ -x "$psql_path" ]]; then
            echo "$psql_path"
            return 0
        fi
    done

    echo ""
    return 1
}

test_postgres_connection() {
    local host="${1:-localhost}"
    local port="${2:-5432}"
    local username="${3:-postgres}"
    local password="${4:-postgres}"
    local database="${5:-postgres}"

    local psql_path=$(find_postgres_path)
    if [[ -z "$psql_path" ]]; then
        print_error "PostgreSQL psql not found"
        return 1
    fi

    export PGPASSWORD="$password"

    local result=$("$psql_path" -h "$host" -p "$port" -U "$username" -d "$database" -c "SELECT version();" 2>&1)
    if [[ $? -eq 0 ]]; then
        print_success "PostgreSQL connection successful"
        return 0
    else
        print_error "PostgreSQL connection failed"
        return 1
    fi
}

setup_postgres_database() {
    local host="${1:-localhost}"
    local port="${2:-5432}"
    local username="${3:-postgres}"
    local password="${4:-postgres}"
    local database="${5:-ai_valido_online}"

    print_status "Setting up PostgreSQL database..."

    local psql_path=$(find_postgres_path)
    if [[ -z "$psql_path" ]]; then
        print_error "PostgreSQL psql not found"
        return 1
    fi

    export PGPASSWORD="$password"

    # Create database if it doesn't exist
    "$psql_path" -h "$host" -p "$port" -U "$username" -d postgres -c "CREATE DATABASE $database;" 2>/dev/null

    if [[ $? -eq 0 ]]; then
        print_success "Database '$database' created successfully"

        # Install essential extensions
        local extensions=("uuid-ossp" "pgcrypto" "postgis" "plpython3u")
        for extension in "${extensions[@]}"; do
            "$psql_path" -h "$host" -p "$port" -U "$username" -d "$database" -c "CREATE EXTENSION IF NOT EXISTS \"$extension\";" 2>/dev/null
            if [[ $? -eq 0 ]]; then
                print_success "Extension '$extension' installed"
            fi
        done
        return 0
    else
        print_error "Failed to create database '$database'"
        return 1
    fi
}

# =============================================================================
# FILE OPTIMIZATION AND CLEANUP
# =============================================================================

optimize_source_structure() {
    local dry_run="$1"
    print_status "Analyzing source structure for optimization..."

    local script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    local src_path="$script_dir/../src"

    if [[ ! -d "$src_path" ]]; then
        print_error "src/ directory not found"
        return 1
    fi

    local total_files=$(find "$src_path" -name "*.py" -type f | wc -l)
    print_colored "📊 Found $total_files Python files in src/" "$CYAN"

    if [[ "$dry_run" == "true" ]]; then
        print_colored "🔍 Dry run mode - no changes will be made" "$YELLOW"
    fi

    # Analyze file sizes
    local large_files=$(find "$src_path" -name "*.py" -type f -size +100k | wc -l)
    local small_files=$(find "$src_path" -name "*.py" -type f -size -1k | wc -l)

    print_colored "📈 Large files (>100KB): $large_files" "$CYAN"
    print_colored "📉 Small files (<1KB): $small_files" "$CYAN"

    if [[ "$dry_run" != "true" ]]; then
        # Create backup before optimization
        local backup_path="$script_dir/../src_backup_$(date +%Y%m%d_%H%M%S)"
        cp -r "$src_path" "$backup_path"
        print_success "Backup created: $backup_path"
    fi
}

clean_source_directory() {
    local dry_run="$1"
    local force="$2"
    print_status "Cleaning source directory..."

    local script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    local src_path="$script_dir/../src"

    if [[ ! -d "$src_path" ]]; then
        print_error "src/ directory not found"
        return 1
    fi

    # Define files that are known to be used
    local used_files=(
        "src/config/master_config.py"
        "src/config/__init__.py"
        "src/core/global_logger.py"
        "src/core/lazy_importer.py"
        "src/core/__init__.py"
        "src/models/unified_models.py"
        "src/models/__init__.py"
        "src/controllers/__init__.py"
        "src/ai/sentiment.py"
        "src/ai/__init__.py"
        "src/database.py"
        "src/routes.py"
        "src/app.py"
    )

    local all_files=$(find "$src_path" -name "*.py" -type f)
    local unused_files=()

    while IFS= read -r file; do
        local relative_path=${file#"$src_path/"}
        relative_path=${relative_path//\//\/}  # Replace / with / for consistency

        local is_used=false
        for used_file in "${used_files[@]}"; do
            if [[ "$relative_path" == "$used_file" ]]; then
                is_used=true
                break
            fi
        done

        if [[ "$is_used" != "true" ]]; then
            unused_files+=("$file")
        fi
    done <<< "$all_files"

    local total_count=$(echo "$all_files" | wc -l)
    local used_count=${#used_files[@]}
    local unused_count=${#unused_files[@]}

    print_colored "📊 Total files: $total_count" "$CYAN"
    print_colored "📊 Used files: $used_count" "$GREEN"
    print_colored "📊 Unused files: $unused_count" "$YELLOW"

    if [[ "$dry_run" != "true" ]] && ([[ "$force" == "true" ]] || [[ $unused_count -eq 0 ]]); then
        for file in "${unused_files[@]}"; do
            rm "$file"
            print_colored "🗑️ Removed: $(basename "$file")" "$YELLOW"
        done
        print_success "Cleanup completed"
    elif [[ "$dry_run" == "true" ]]; then
        print_colored "🔍 Dry run mode - no files will be removed" "$YELLOW"
        print_colored "Use FORCE=true to actually remove files" "$YELLOW"
    fi
}

# =============================================================================
# COMPREHENSIVE SYSTEM HEALTH CHECK
# =============================================================================

test_system_health() {
    print_status "Running system health check..."

    declare -A health_status

    # Check Python
    health_status["Python"]=false
    if command_exists python3 || command_exists python; then
        health_status["Python"]=true
    fi

    # Check Julia
    health_status["Julia"]=false
    if command_exists julia; then
        health_status["Julia"]=true
    fi

    # Check PostgreSQL
    health_status["PostgreSQL"]=false
    if [[ -n "$(find_postgres_path)" ]]; then
        health_status["PostgreSQL"]=true
    fi

    # Check Node.js (for potential frontend)
    health_status["Node.js"]=false
    if command_exists node; then
        health_status["Node.js"]=true
    fi

    # Check Git
    health_status["Git"]=false
    if command_exists git; then
        health_status["Git"]=true
    fi

    # Check Docker
    health_status["Docker"]=false
    if command_exists docker; then
        health_status["Docker"]=true
    fi

    print_colored "📊 System Health Status:" "$CYAN"
    for component in "${!health_status[@]}"; do
        if [[ "${health_status[$component]}" == "true" ]]; then
            print_colored "  ✅ $component" "$GREEN"
        else
            print_colored "  ❌ $component" "$RED"
        fi
    done
}

# =============================================================================
# MAIN EXECUTION LOGIC
# =============================================================================

show_help() {
    print_colored "ValidoAI Master Configuration Script (Linux/macOS)" "$MAGENTA"
    print_colored "=================================================" "$MAGENTA"
    echo
    print_colored "USAGE:" "$CYAN"
    print_colored "  ./validoai_master_config.sh [options]" "$WHITE"
    echo
    print_colored "OPTIONS:" "$CYAN"
    print_colored "  ACTION=<action>         Action to perform (setup, health, optimize, clean, julia, python, postgres)" "$WHITE"
    print_colored "  DRY_RUN=true            Show what would be done without making changes" "$WHITE"
    print_colored "  FORCE=true              Force operations without confirmation" "$WHITE"
    print_colored "  SKIP_DATABASE=true      Skip database setup" "$WHITE"
    print_colored "  SKIP_JULIA=true         Skip Julia setup" "$WHITE"
    print_colored "  SKIP_PYTHON=true        Skip Python setup" "$WHITE"
    print_colored "  SKIP_OPTIMIZATION=true  Skip source optimization" "$WHITE"
    echo
    print_colored "ACTIONS:" "$CYAN"
    print_colored "  setup       Complete system setup (default)" "$WHITE"
    print_colored "  health      System health check" "$WHITE"
    print_colored "  optimize    Optimize source code structure" "$WHITE"
    print_colored "  clean       Clean unused files" "$WHITE"
    print_colored "  julia       Setup Julia environment" "$WHITE"
    print_colored "  python      Setup Python environment" "$WHITE"
    print_colored "  postgres    Setup PostgreSQL database" "$WHITE"
    echo
    print_colored "EXAMPLES:" "$CYAN"
    print_colored "  ./validoai_master_config.sh ACTION=setup" "$WHITE"
    print_colored "  ./validoai_master_config.sh ACTION=health DRY_RUN=true" "$WHITE"
    print_colored "  ./validoai_master_config.sh ACTION=optimize FORCE=true" "$WHITE"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --help)
            show_help
            exit 0
            ;;
        --dry-run)
            DRY_RUN="true"
            shift
            ;;
        --force)
            FORCE="true"
            shift
            ;;
        --skip-database)
            SKIP_DATABASE="true"
            shift
            ;;
        --skip-julia)
            SKIP_JULIA="true"
            shift
            ;;
        --skip-python)
            SKIP_PYTHON="true"
            shift
            ;;
        --skip-optimization)
            SKIP_OPTIMIZATION="true"
            shift
            ;;
        *)
            if [[ $1 == ACTION=* ]]; then
                ACTION="${1#*=}"
            fi
            shift
            ;;
    esac
done

# Main execution
platform=$(get_platform)
print_colored "🚀 ValidoAI Master Configuration Script" "$MAGENTA"
print_colored "=======================================" "$MAGENTA"
print_colored "Platform: $platform" "$CYAN"
echo

case "${ACTION,,}" in
    "setup")
        print_status "Starting complete system setup..."

        # Health check first
        test_system_health

        # Python setup
        if [[ "$SKIP_PYTHON" != "true" ]]; then
            create_python_environment
        fi

        # Julia setup
        if [[ "$SKIP_JULIA" != "true" ]]; then
            setup_julia_environment
        fi

        # Database setup
        if [[ "$SKIP_DATABASE" != "true" ]]; then
            setup_postgres_database
        fi

        # Source optimization
        if [[ "$SKIP_OPTIMIZATION" != "true" ]]; then
            optimize_source_structure "$DRY_RUN"
            clean_source_directory "$DRY_RUN" "$FORCE"
        fi

        print_success "Setup completed successfully!"
        ;;

    "health")
        test_system_health
        ;;

    "optimize")
        optimize_source_structure "$DRY_RUN"
        ;;

    "clean")
        clean_source_directory "$DRY_RUN" "$FORCE"
        ;;

    "julia")
        setup_julia_environment
        ;;

    "python")
        create_python_environment
        ;;

    "postgres")
        setup_postgres_database
        ;;

    *)
        print_error "Unknown action: $ACTION"
        print_colored "Use --help for available actions" "$YELLOW"
        exit 1
        ;;
esac

echo
print_success "Operation completed!"
