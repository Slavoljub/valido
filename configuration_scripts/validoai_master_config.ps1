# =============================================================================
# VALIDOAI - MASTER CONFIGURATION SCRIPT (Cross-Platform)
# =============================================================================
# Unified setup script for Windows, Linux, and macOS
# Handles PostgreSQL, Julia, Python, optimization, and cleanup
# Following DRY principles and Cursor rules

param(
    [string]$Action = "setup",
    [switch]$Force,
    [switch]$DryRun,
    [switch]$SkipDatabase,
    [switch]$SkipJulia,
    [switch]$SkipPython,
    [switch]$SkipOptimization,
    [switch]$Help
)

# =============================================================================
# CROSS-PLATFORM DETECTION AND UTILITIES
# =============================================================================

function Get-PlatformInfo {
    $platform = $null
    $isWSL = $false
    $isMacOS = $false

    # Check for WSL
    if ($env:WSL_DISTRO_NAME -or $env:WSLENV -or $env:WSL_INTEROP) {
        $isWSL = $true
        $platform = "wsl"
    }
    # Check for Windows
    elseif ($PSVersionTable.Platform -eq "Win32NT" -or $env:OS -eq "Windows_NT") {
        $platform = "windows"
    }
    # Check for Linux
    elseif ($PSVersionTable.Platform -eq "Unix") {
        $platform = "linux"
    }
    # Check for macOS
    elseif ($PSVersionTable.Platform -eq "Unix" -and $env:OSTYPE -eq "darwin") {
        $platform = "macos"
        $isMacOS = $true
    }

    return @{
        Platform = $platform
        IsWSL = $isWSL
        IsMacOS = $isMacOS
    }
}

function Write-ColoredMessage {
    param([string]$Message, [string]$Color = "White")
    $colorMap = @{
        "Red" = [ConsoleColor]::Red
        "Green" = [ConsoleColor]::Green
        "Yellow" = [ConsoleColor]::Yellow
        "Blue" = [ConsoleColor]::Blue
        "Magenta" = [ConsoleColor]::Magenta
        "Cyan" = [ConsoleColor]::Cyan
        "White" = [ConsoleColor]::White
    }
    Write-Host $Message -ForegroundColor $colorMap[$Color]
}

function Test-CommandExists {
    param([string]$Command)
    $null -ne (Get-Command $Command -ErrorAction SilentlyContinue)
}

# =============================================================================
# PYTHON ENVIRONMENT MANAGEMENT
# =============================================================================

function Install-PythonRequirements {
    Write-ColoredMessage "🔄 Installing Python requirements..." "Blue"

    if (Test-CommandExists "pip") {
        pip install -r requirements.txt
        if ($LASTEXITCODE -eq 0) {
            Write-ColoredMessage "✅ Python requirements installed successfully" "Green"
        } else {
            Write-ColoredMessage "❌ Failed to install Python requirements" "Red"
        }
    } else {
        Write-ColoredMessage "❌ pip not found. Please install Python first." "Red"
    }
}

function Create-PythonEnvironment {
    param([string]$EnvName = "validoai_env")

    Write-ColoredMessage "🔄 Creating Python virtual environment..." "Blue"

    if (Test-CommandExists "python3") {
        python3 -m venv $EnvName
        if ($LASTEXITCODE -eq 0) {
            Write-ColoredMessage "✅ Python virtual environment created: $EnvName" "Green"
            Write-ColoredMessage "🔄 Activating environment and installing requirements..." "Blue"

            # Activate and install requirements
            if ($IsWindows) {
                & "$EnvName\Scripts\activate.ps1"
            } else {
                & "$EnvName/bin/activate"
            }

            Install-PythonRequirements
        } else {
            Write-ColoredMessage "❌ Failed to create Python virtual environment" "Red"
        }
    } else {
        Write-ColoredMessage "❌ python3 not found. Please install Python 3.8+ first." "Red"
    }
}

# =============================================================================
# JULIA ENVIRONMENT MANAGEMENT
# =============================================================================

function Install-Julia {
    param([string]$JuliaVersion = "1.9.4")

    Write-ColoredMessage "🔄 Installing Julia $JuliaVersion..." "Blue"

    $platformInfo = Get-PlatformInfo

    if ($platformInfo.Platform -eq "windows") {
        # Windows installation
        $installerUrl = "https://julialang-s3.julialang.org/bin/winnt/x64/1.9/julia-$JuliaVersion-win64.exe"
        $installerPath = "$env:TEMP\julia-installer.exe"

        Invoke-WebRequest -Uri $installerUrl -OutFile $installerPath
        Start-Process -FilePath $installerPath -ArgumentList "/S" -Wait

        Write-ColoredMessage "✅ Julia installed on Windows" "Green"
    }
    elseif ($platformInfo.Platform -eq "macos") {
        # macOS installation
        $installerUrl = "https://julialang-s3.julialang.org/bin/mac/x64/1.9/julia-$JuliaVersion-mac64.dmg"
        $installerPath = "$env:TEMP\julia-installer.dmg"

        Invoke-WebRequest -Uri $installerUrl -OutFile $installerPath
        hdiutil attach $installerPath
        sudo installer -pkg "/Volumes/Julia-1.9.4/Julia-1.9.4.pkg" -target /

        Write-ColoredMessage "✅ Julia installed on macOS" "Green"
    }
    else {
        # Linux installation
        $installerUrl = "https://julialang-s3.julialang.org/bin/linux/x64/1.9/julia-$JuliaVersion-linux-x86_64.tar.gz"
        $installerPath = "$env:TEMP\julia-installer.tar.gz"

        Invoke-WebRequest -Uri $installerUrl -OutFile $installerPath
        sudo tar -xzf $installerPath -C /opt/

        Write-ColoredMessage "✅ Julia installed on Linux" "Green"
    }
}

function Setup-JuliaEnvironment {
    Write-ColoredMessage "🔄 Setting up Julia environment..." "Blue"

    if (Test-CommandExists "julia") {
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

        Write-ColoredMessage "✅ Julia packages installed successfully" "Green"
    } else {
        Write-ColoredMessage "❌ Julia not found. Installing Julia first..." "Yellow"
        Install-Julia
        Setup-JuliaEnvironment
    }
}

# =============================================================================
# POSTGRESQL MANAGEMENT
# =============================================================================

function Find-PostgresPath {
    $possiblePaths = @(
        "C:\Program Files\PostgreSQL\*\bin\psql.exe",
        "C:\Program Files\PostgreSQL\bin\psql.exe",
        "/usr/bin/psql",
        "/usr/local/bin/psql",
        "/opt/homebrew/bin/psql",
        "/usr/lib/postgresql/*/bin/psql"
    )

    foreach ($path in $possiblePaths) {
        $resolvedPaths = Get-ChildItem -Path $path -ErrorAction SilentlyContinue
        foreach ($resolvedPath in $resolvedPaths) {
            if (Test-Path $resolvedPath.FullName) {
                return $resolvedPath.FullName
            }
        }
    }

    return $null
}

function Test-PostgresConnection {
    param(
        [string]$HostName = "localhost",
        [int]$Port = 5432,
        [string]$Username = "postgres",
        [string]$Password = "postgres",
        [string]$Database = "postgres"
    )

    $psqlPath = Find-PostgresPath
    if (-not $psqlPath) {
        Write-ColoredMessage "❌ PostgreSQL psql not found" "Red"
        return $false
    }

    $env:PGPASSWORD = $Password

    $result = & $psqlPath -h $HostName -p $Port -U $Username -d $Database -c "SELECT version();" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-ColoredMessage "✅ PostgreSQL connection successful" "Green"
        return $true
    } else {
        Write-ColoredMessage "❌ PostgreSQL connection failed" "Red"
        return $false
    }
}

function Setup-PostgresDatabase {
    param(
        [string]$HostName = "localhost",
        [int]$Port = 5432,
        [string]$Username = "postgres",
        [string]$Password = "postgres",
        [string]$Database = "ai_valido_online"
    )

    Write-ColoredMessage "🔄 Setting up PostgreSQL database..." "Blue"

    $psqlPath = Find-PostgresPath
    if (-not $psqlPath) {
        Write-ColoredMessage "❌ PostgreSQL psql not found" "Red"
        return $false
    }

    $env:PGPASSWORD = $Password

    # Create database if it doesn't exist
    & $psqlPath -h $HostName -p $Port -U $Username -d postgres -c "CREATE DATABASE $Database;" 2>&1 | Out-Null

    if ($LASTEXITCODE -eq 0) {
        Write-ColoredMessage "✅ Database '$Database' created successfully" "Green"

        # Install essential extensions
        $extensions = @("uuid-ossp", "pgcrypto", "postgis", "plpython3u")
        foreach ($extension in $extensions) {
            & $psqlPath -h $HostName -p $Port -U $Username -d $Database -c "CREATE EXTENSION IF NOT EXISTS \"$extension\";" 2>&1 | Out-Null
            if ($LASTEXITCODE -eq 0) {
                Write-ColoredMessage "✅ Extension '$extension' installed" "Green"
            }
        }
        return $true
    } else {
        Write-ColoredMessage "❌ Failed to create database '$Database'" "Red"
        return $false
    }
}

# =============================================================================
# FILE OPTIMIZATION AND CLEANUP
# =============================================================================

function Optimize-SourceStructure {
    param([switch]$DryRun)

    Write-ColoredMessage "🔄 Analyzing source structure for optimization..." "Blue"

    $srcPath = Join-Path $PSScriptRoot "..\src"

    if (-not (Test-Path $srcPath)) {
        Write-ColoredMessage "❌ src/ directory not found" "Red"
        return
    }

    $totalFiles = (Get-ChildItem -Path $srcPath -Recurse -File -Include "*.py").Count
    Write-ColoredMessage "📊 Found $totalFiles Python files in src/" "Cyan"

    if ($DryRun) {
        Write-ColoredMessage "🔍 Dry run mode - no changes will be made" "Yellow"
    }

    # Analyze file sizes and potential mergers
    $files = Get-ChildItem -Path $srcPath -Recurse -File -Include "*.py" |
             Select-Object FullName, Length, Name |
             Sort-Object Length -Descending

    $largeFiles = $files | Where-Object { $_.Length -gt 100KB }
    $smallFiles = $files | Where-Object { $_.Length -lt 1KB }

    Write-ColoredMessage "📈 Large files (>100KB): $($largeFiles.Count)" "Cyan"
    Write-ColoredMessage "📉 Small files (<1KB): $($smallFiles.Count)" "Cyan"

    if (-not $DryRun) {
        # Create backup before optimization
        $backupPath = Join-Path $PSScriptRoot "..\src_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
        Copy-Item -Path $srcPath -Destination $backupPath -Recurse
        Write-ColoredMessage "✅ Backup created: $backupPath" "Green"
    }
}

function Clean-SourceDirectory {
    param([switch]$DryRun, [switch]$Force)

    Write-ColoredMessage "🧹 Cleaning source directory..." "Blue"

    $srcPath = Join-Path $PSScriptRoot "..\src"

    if (-not (Test-Path $srcPath)) {
        Write-ColoredMessage "❌ src/ directory not found" "Red"
        return
    }

    # Define files that are known to be used
    $usedFiles = @(
        "src/config/master_config.py",
        "src/config/__init__.py",
        "src/core/global_logger.py",
        "src/core/lazy_importer.py",
        "src/core/__init__.py",
        "src/models/unified_models.py",
        "src/models/__init__.py",
        "src/controllers/__init__.py",
        "src/ai/sentiment.py",
        "src/ai/__init__.py",
        "src/database.py",
        "src/routes.py",
        "src/app.py"
    )

    $allFiles = Get-ChildItem -Path $srcPath -Recurse -File -Include "*.py"
    $unusedFiles = $allFiles | Where-Object { $usedFiles -notcontains $_.FullName.Replace($srcPath, "src").Replace("\", "/") }

    Write-ColoredMessage "📊 Total files: $($allFiles.Count)" "Cyan"
    Write-ColoredMessage "📊 Used files: $($usedFiles.Count)" "Green"
    Write-ColoredMessage "📊 Unused files: $($unusedFiles.Count)" "Yellow"

    if (-not $DryRun -and ($Force -or $unusedFiles.Count -eq 0)) {
        foreach ($file in $unusedFiles) {
            Remove-Item -Path $file.FullName -Force
            Write-ColoredMessage "🗑️ Removed: $($file.Name)" "Yellow"
        }
        Write-ColoredMessage "✅ Cleanup completed" "Green"
    } elseif ($DryRun) {
        Write-ColoredMessage "🔍 Dry run mode - no files will be removed" "Yellow"
        Write-ColoredMessage "Use -Force to actually remove files" "Yellow"
    }
}

# =============================================================================
# COMPREHENSIVE SYSTEM HEALTH CHECK
# =============================================================================

function Test-SystemHealth {
    Write-ColoredMessage "🏥 Running system health check..." "Blue"

    $healthStatus = @{}

    # Check Python
    $healthStatus["Python"] = Test-CommandExists "python3" -or Test-CommandExists "python"

    # Check Julia
    $healthStatus["Julia"] = Test-CommandExists "julia"

    # Check PostgreSQL
    $healthStatus["PostgreSQL"] = $null -ne (Find-PostgresPath)

    # Check Node.js (for potential frontend)
    $healthStatus["Node.js"] = Test-CommandExists "node"

    # Check Git
    $healthStatus["Git"] = Test-CommandExists "git"

    # Check Docker
    $healthStatus["Docker"] = Test-CommandExists "docker"

    Write-ColoredMessage "📊 System Health Status:" "Cyan"
    foreach ($component in $healthStatus.Keys) {
        $status = if ($healthStatus[$component]) { "✅" } else { "❌" }
        $color = if ($healthStatus[$component]) { "Green" } else { "Red" }
        Write-ColoredMessage "  $status $component" $color
    }

    return $healthStatus
}

# =============================================================================
# MAIN EXECUTION LOGIC
# =============================================================================

function Show-Help {
    Write-ColoredMessage "ValidoAI Master Configuration Script" "Magenta"
    Write-ColoredMessage "===================================" "Magenta"
    Write-ColoredMessage ""
    Write-ColoredMessage "USAGE:" "Cyan"
    Write-ColoredMessage "  .\validoai_master_config.ps1 [options]" "White"
    Write-ColoredMessage ""
    Write-ColoredMessage "OPTIONS:" "Cyan"
    Write-ColoredMessage "  -Action <string>        Action to perform (setup, health, optimize, clean, julia, python, postgres)" "White"
    Write-ColoredMessage "  -Force                  Force operations without confirmation" "White"
    Write-ColoredMessage "  -DryRun                 Show what would be done without making changes" "White"
    Write-ColoredMessage "  -SkipDatabase           Skip database setup" "White"
    Write-ColoredMessage "  -SkipJulia              Skip Julia setup" "White"
    Write-ColoredMessage "  -SkipPython             Skip Python setup" "White"
    Write-ColoredMessage "  -SkipOptimization       Skip source optimization" "White"
    Write-ColoredMessage "  -Help                   Show this help message" "White"
    Write-ColoredMessage ""
    Write-ColoredMessage "ACTIONS:" "Cyan"
    Write-ColoredMessage "  setup       Complete system setup (default)" "White"
    Write-ColoredMessage "  health      System health check" "White"
    Write-ColoredMessage "  optimize    Optimize source code structure" "White"
    Write-ColoredMessage "  clean       Clean unused files" "White"
    Write-ColoredMessage "  julia       Setup Julia environment" "White"
    Write-ColoredMessage "  python      Setup Python environment" "White"
    Write-ColoredMessage "  postgres    Setup PostgreSQL database" "White"
    Write-ColoredMessage ""
    Write-ColoredMessage "EXAMPLES:" "Cyan"
    Write-ColoredMessage "  .\validoai_master_config.ps1 -Action setup" "White"
    Write-ColoredMessage "  .\validoai_master_config.ps1 -Action health -DryRun" "White"
    Write-ColoredMessage "  .\validoai_master_config.ps1 -Action optimize -Force" "White"
}

# Main execution
if ($Help) {
    Show-Help
    exit 0
}

$platformInfo = Get-PlatformInfo
Write-ColoredMessage "🚀 ValidoAI Master Configuration Script" "Magenta"
Write-ColoredMessage "=====================================" "Magenta"
Write-ColoredMessage "Platform: $($platformInfo.Platform)" "Cyan"
if ($platformInfo.IsWSL) {
    Write-ColoredMessage "Environment: WSL" "Cyan"
}
Write-ColoredMessage ""

switch ($Action.ToLower()) {
    "setup" {
        Write-ColoredMessage "🔧 Starting complete system setup..." "Blue"

        # Health check first
        $health = Test-SystemHealth

        # Python setup
        if (-not $SkipPython) {
            Create-PythonEnvironment
        }

        # Julia setup
        if (-not $SkipJulia) {
            Setup-JuliaEnvironment
        }

        # Database setup
        if (-not $SkipDatabase) {
            Setup-PostgresDatabase
        }

        # Source optimization
        if (-not $SkipOptimization) {
            Optimize-SourceStructure -DryRun:$DryRun
            Clean-SourceDirectory -DryRun:$DryRun -Force:$Force
        }

        Write-ColoredMessage "✅ Setup completed successfully!" "Green"
    }

    "health" {
        Test-SystemHealth | Out-Null
    }

    "optimize" {
        Optimize-SourceStructure -DryRun:$DryRun
    }

    "clean" {
        Clean-SourceDirectory -DryRun:$DryRun -Force:$Force
    }

    "julia" {
        Setup-JuliaEnvironment
    }

    "python" {
        Create-PythonEnvironment
    }

    "postgres" {
        Setup-PostgresDatabase
    }

    default {
        Write-ColoredMessage "❌ Unknown action: $Action" "Red"
        Write-ColoredMessage "Use -Help for available actions" "Yellow"
        exit 1
    }
}

Write-ColoredMessage ""
Write-ColoredMessage "🎉 Operation completed!" "Green"
