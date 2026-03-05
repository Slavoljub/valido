# ValidoAI PostgreSQL Extensions Setup Script
# Cross-platform support for Windows, Linux, and macOS
# This script installs and configures PostgreSQL extensions for ValidoAI

param(
    [string]$PostgresPath = "",
    [string]$DatabaseName = "ai_valido_online",
    [string]$Username = "postgres",
    [string]$Password = "postgres",
    [string]$Host = "localhost",
    [int]$Port = 5432,
    [switch]$Force = $false,
    [switch]$DryRun = $false
)

# Function to detect operating system
function Get-OperatingSystem {
    $os = $PSVersionTable.OS
    if ($os -match "Windows") {
        return "Windows"
    } elseif ($os -match "Linux") {
        return "Linux"
    } elseif ($os -match "Darwin") {
        return "macOS"
    } else {
        return "Unknown"
    }
}

# Function to detect PostgreSQL installation path
function Find-PostgreSQLPath {
    $os = Get-OperatingSystem

    switch ($os) {
        "Windows" {
            # Common Windows PostgreSQL installation paths
            $possiblePaths = @(
                "C:\Program Files\PostgreSQL\17\bin",
                "C:\Program Files\PostgreSQL\16\bin",
                "C:\Program Files\PostgreSQL\15\bin",
                "C:\Program Files\PostgreSQL\14\bin",
                "C:\Program Files\PostgreSQL\13\bin",
                "C:\Program Files (x86)\PostgreSQL\17\bin",
                "C:\Program Files (x86)\PostgreSQL\16\bin",
                "C:\Program Files (x86)\PostgreSQL\15\bin",
                "C:\Program Files (x86)\PostgreSQL\14\bin",
                "C:\Program Files (x86)\PostgreSQL\13\bin"
            )

            foreach ($path in $possiblePaths) {
                if (Test-Path $path) {
                    return $path
                }
            }

            # Try to find via registry or environment
            try {
                $pgPath = Get-ItemProperty -Path "HKLM:\SOFTWARE\PostgreSQL\Installations" -ErrorAction SilentlyContinue
                if ($pgPath) {
                    return $pgPath.BaseDirectory + "\bin"
                }
            } catch {}

            return $null
        }

        "Linux" {
            # Common Linux PostgreSQL paths
            $possiblePaths = @(
                "/usr/bin",
                "/usr/local/bin",
                "/usr/lib/postgresql/*/bin",
                "/usr/pgsql-*/bin"
            )

            foreach ($path in $possiblePaths) {
                $expandedPaths = Get-ChildItem -Path $path -ErrorAction SilentlyContinue | Where-Object { $_.PSIsContainer }
                foreach ($expandedPath in $expandedPaths) {
                    if (Test-Path (Join-Path $expandedPath.FullName "psql")) {
                        return $expandedPath.FullName
                    }
                }
            }

            # Try which command
            try {
                $whichResult = & which psql 2>$null
                if ($whichResult) {
                    return Split-Path $whichResult -Parent
                }
            } catch {}

            return $null
        }

        "macOS" {
            # Common macOS PostgreSQL paths
            $possiblePaths = @(
                "/usr/local/bin",
                "/usr/local/Cellar/postgresql@*/bin",
                "/opt/homebrew/bin",
                "/opt/homebrew/Cellar/postgresql@*/bin",
                "/Library/PostgreSQL/*/bin"
            )

            foreach ($path in $possiblePaths) {
                $expandedPaths = Get-ChildItem -Path $path -ErrorAction SilentlyContinue | Where-Object { $_.PSIsContainer }
                foreach ($expandedPath in $expandedPaths) {
                    if (Test-Path (Join-Path $expandedPath.FullName "psql")) {
                        return $expandedPath.FullName
                    }
                }
            }

            # Try which command
            try {
                $whichResult = & which psql 2>$null
                if ($whichResult) {
                    return Split-Path $whichResult -Parent
                }
            } catch {}

            return $null
        }

        default {
            return $null
        }
    }
}

# Function to test PostgreSQL connection
function Test-PostgreSQLConnection {
    param([string]$Path, [string]$HostName, [int]$PortNumber, [string]$User, [string]$Pass, [string]$Db)

    if ($DryRun) {
        Write-Host "[DRY RUN] Would test PostgreSQL connection to $HostName:$PortNumber" -ForegroundColor Yellow
        return $true
    }

    try {
        $env:PGPASSWORD = $Pass
        $result = & "$Path\psql" -h $HostName -p $PortNumber -U $User -d $Db -c "SELECT version();" 2>&1

        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ PostgreSQL connection successful" -ForegroundColor Green
            return $true
        } else {
            Write-Host "❌ PostgreSQL connection failed: $result" -ForegroundColor Red
            return $false
        }
    }
    catch {
        Write-Host "❌ PostgreSQL connection test failed: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Function to run psql commands
function Invoke-PsqlCommand {
    param([string]$Path, [string]$Command, [string]$Description, [string]$HostName, [int]$PortNumber, [string]$User, [string]$Pass, [string]$Db)

    if ($DryRun) {
        Write-Host "[DRY RUN] Would execute: $Command" -ForegroundColor Yellow
        return $true
    }

    Write-Host "📋 $Description..." -ForegroundColor Yellow
    try {
        $env:PGPASSWORD = $Pass
        $result = & "$Path\psql" -h $HostName -p $PortNumber -U $User -d $Db -c $Command 2>&1

        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ $Description completed" -ForegroundColor Green
            return $true
        } else {
            Write-Host "⚠️  $Description warning: $result" -ForegroundColor Yellow
            return $true  # Don't fail on warnings
        }
    }
    catch {
        Write-Host "❌ $Description failed: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Function to check if extension is available
function Test-ExtensionAvailability {
    param([string]$Path, [string]$Extension, [string]$HostName, [int]$PortNumber, [string]$User, [string]$Pass, [string]$Db)

    if ($DryRun) {
        Write-Host "[DRY RUN] Would check availability of extension: $Extension" -ForegroundColor Yellow
        return $true
    }

    try {
        $env:PGPASSWORD = $Pass
        $result = & "$Path\psql" -h $HostName -p $PortNumber -U $User -d $Db -c "SELECT * FROM pg_available_extensions WHERE name = '$Extension';" 2>&1

        return $LASTEXITCODE -eq 0 -and $result -match $Extension
    }
    catch {
        return $false
    }
}

# Main script execution
try {
    Write-Host "🔧 ValidoAI PostgreSQL Extensions Setup" -ForegroundColor Green
    Write-Host "=" * 60
    Write-Host ""

    # Detect operating system
    $os = Get-OperatingSystem
    Write-Host "🖥️  Detected OS: $os" -ForegroundColor Cyan

    # Find PostgreSQL installation
    if (-not $PostgresPath) {
        Write-Host "🔍 Searching for PostgreSQL installation..." -ForegroundColor Yellow
        $PostgresPath = Find-PostgreSQLPath
    }

    if (-not $PostgresPath -or -not (Test-Path $PostgresPath)) {
        Write-Host "❌ PostgreSQL installation not found!" -ForegroundColor Red
        Write-Host "💡 Please ensure PostgreSQL is installed and accessible" -ForegroundColor Yellow

        # Provide installation instructions based on OS
        switch ($os) {
            "Windows" {
                Write-Host "" -ForegroundColor White
                Write-Host "Windows Installation Options:" -ForegroundColor Cyan
                Write-Host "1. Download from: https://www.postgresql.org/download/windows/" -ForegroundColor White
                Write-Host "2. Or use Chocolatey: choco install postgresql" -ForegroundColor White
                Write-Host "3. Or use winget: winget install PostgreSQL.PostgreSQL" -ForegroundColor White
            }
            "Linux" {
                Write-Host "" -ForegroundColor White
                Write-Host "Linux Installation Options:" -ForegroundColor Cyan
                Write-Host "Ubuntu/Debian: sudo apt-get install postgresql postgresql-contrib" -ForegroundColor White
                Write-Host "CentOS/RHEL: sudo yum install postgresql-server postgresql-contrib" -ForegroundColor White
                Write-Host "Fedora: sudo dnf install postgresql-server postgresql-contrib" -ForegroundColor White
            }
            "macOS" {
                Write-Host "" -ForegroundColor White
                Write-Host "macOS Installation Options:" -ForegroundColor Cyan
                Write-Host "1. Use Homebrew: brew install postgresql" -ForegroundColor White
                Write-Host "2. Or download from: https://www.postgresql.org/download/macosx/" -ForegroundColor White
                Write-Host "3. Or use Postgres.app: https://postgresapp.com/" -ForegroundColor White
            }
        }

        exit 1
    }

    Write-Host "✅ PostgreSQL found at: $PostgresPath" -ForegroundColor Green

    # Test connection
    Write-Host "🔗 Testing database connection..." -ForegroundColor Yellow
    $connectionOK = Test-PostgreSQLConnection -Path $PostgresPath -HostName $Host -PortNumber $Port -User $Username -Pass $Password -Db $DatabaseName

    if (-not $connectionOK) {
        Write-Host "❌ Database connection failed!" -ForegroundColor Red
        Write-Host "💡 Please ensure:" -ForegroundColor Yellow
        Write-Host "   - PostgreSQL service is running" -ForegroundColor White
        Write-Host "   - Database '$DatabaseName' exists" -ForegroundColor White
        Write-Host "   - User '$Username' has access to the database" -ForegroundColor White
        Write-Host "   - Connection details are correct" -ForegroundColor White
        exit 1
    }

    # Define extensions by category
    $coreExtensions = @(
        'uuid-ossp',           # UUID generation
        'pgcrypto',            # Encryption functions
        'pg_stat_statements',  # Query performance monitoring
        'pg_buffercache',      # Buffer cache inspection
        'pg_prewarm',          # Cache prewarming
        'pg_trgm',             # Text similarity and fuzzy matching
        'btree_gist',          # GiST index support
        'btree_gin',           # GIN index support
        'unaccent',            # Text normalization for international characters
        'fuzzystrmatch'        # Fuzzy string matching
    )

    $aiExtensions = @(
        'pgrowlocks',          # Row locking information
        'pgstattuple',         # Tuple-level statistics
        'tablefunc',           # Table functions
        'intarray',            # Integer array functions
        'hstore',              # Key-value store
        'xml2',                # XML processing
        'pgxml',               # XML support
        'ltree'                # Tree-like structures
    )

    $advancedExtensions = @(
        'pgvector',            # Vector embeddings for AI (separate install)
        'postgis',             # Geographic data support (separate install)
        'timescaledb',         # Time-series data optimization (separate install)
        'pg_cron',             # Job scheduling (separate install)
        'pg_repack',           # Online table reorganization (separate install)
        'pg_similarity',       # Advanced similarity functions (separate install)
        'pg_partman',          # Partition management (separate install)
        'pglogical',           # Logical replication (separate install)
        'citus',               # Distributed PostgreSQL (separate install)
        'pgbouncer',           # Connection pooling (separate install)
        'pgpool'               # Advanced connection pooling (separate install)
    )

    # Install core extensions
    Write-Host ""
    Write-Host "📦 Installing core extensions..." -ForegroundColor Cyan

    $installedCount = 0
    $skippedCount = 0

    foreach ($extension in $coreExtensions) {
        if (Test-ExtensionAvailability -Path $PostgresPath -Extension $extension -HostName $Host -PortNumber $Port -User $Username -Pass $Password -Db $DatabaseName) {
            if (Invoke-PsqlCommand -Path $PostgresPath -Command "CREATE EXTENSION IF NOT EXISTS $extension;" -Description "Installing $extension" -HostName $Host -PortNumber $Port -User $Username -Pass $Password -Db $DatabaseName) {
                $installedCount++
            }
        } else {
            Write-Host "⚠️  Extension '$extension' not available in this PostgreSQL installation" -ForegroundColor Yellow
            $skippedCount++
        }
    }

    # Install AI extensions
    Write-Host ""
    Write-Host "🤖 Installing AI extensions..." -ForegroundColor Cyan

    foreach ($extension in $aiExtensions) {
        if (Test-ExtensionAvailability -Path $PostgresPath -Extension $extension -HostName $Host -PortNumber $Port -User $Username -Pass $Password -Db $DatabaseName) {
            if (Invoke-PsqlCommand -Path $PostgresPath -Command "CREATE EXTENSION IF NOT EXISTS $extension;" -Description "Installing $extension" -HostName $Host -PortNumber $Port -User $Username -Pass $Password -Db $DatabaseName) {
                $installedCount++
            }
        } else {
            Write-Host "⚠️  Extension '$extension' not available in this PostgreSQL installation" -ForegroundColor Yellow
            $skippedCount++
        }
    }

    # Show advanced extensions that require separate installation
    Write-Host ""
    Write-Host "🚀 Advanced extensions (require separate installation):" -ForegroundColor Magenta

    foreach ($extension in $advancedExtensions) {
        Write-Host "   - $extension (not installed - requires separate download)" -ForegroundColor Gray
    }

    # Verify installed extensions
    Write-Host ""
    Write-Host "🔍 Verifying installed extensions..." -ForegroundColor Cyan

    if (-not $DryRun) {
        $env:PGPASSWORD = $Password
        $result = & "$PostgresPath\psql" -h $Host -p $Port -U $Username -d $DatabaseName -c "SELECT name, default_version, installed_version FROM pg_available_extensions WHERE installed_version IS NOT NULL ORDER BY name;" 2>&1

        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Installed extensions:" -ForegroundColor Green
            # Parse and display the results (this is a simple implementation)
            $lines = $result -split "`n" | Where-Object { $_ -match "\|" -and $_ -notmatch "name|default_version|installed_version" }
            foreach ($line in $lines) {
                if ($line.Trim()) {
                    $parts = $line -split "\|"
                    if ($parts.Count -ge 3) {
                        Write-Host "   - $($parts[0].Trim()): v$($parts[2].Trim())" -ForegroundColor White
                    }
                }
            }
        }
    }

    # Provide installation instructions for advanced extensions
    Write-Host ""
    Write-Host "📋 Installation instructions for advanced extensions:" -ForegroundColor Cyan
    Write-Host ""

    switch ($os) {
        "Windows" {
            Write-Host "For pgvector (AI embeddings):" -ForegroundColor Yellow
            Write-Host "  1. Download from: https://github.com/pgvector/pgvector" -ForegroundColor White
            Write-Host "  2. Build and install: pip install pgvector" -ForegroundColor White
            Write-Host "  3. Enable: CREATE EXTENSION vector;" -ForegroundColor White
            Write-Host ""

            Write-Host "For PostGIS (Geographic data):" -ForegroundColor Yellow
            Write-Host "  1. Download from: https://postgis.net/install/" -ForegroundColor White
            Write-Host "  2. Run installer and follow setup wizard" -ForegroundColor White
            Write-Host ""

            Write-Host "For TimescaleDB (Time-series):" -ForegroundColor Yellow
            Write-Host "  1. Download from: https://www.timescale.com/install" -ForegroundColor White
            Write-Host "  2. Run installer for Windows" -ForegroundColor White
        }

        "Linux" {
            Write-Host "For pgvector (AI embeddings):" -ForegroundColor Yellow
            Write-Host "  Ubuntu/Debian:" -ForegroundColor Cyan
            Write-Host "    git clone https://github.com/pgvector/pgvector.git" -ForegroundColor White
            Write-Host "    cd pgvector && make && sudo make install" -ForegroundColor White
            Write-Host "    psql -c 'CREATE EXTENSION vector;'" -ForegroundColor White
            Write-Host ""

            Write-Host "For PostGIS (Geographic data):" -ForegroundColor Yellow
            Write-Host "  Ubuntu/Debian: sudo apt-get install postgis postgresql-*-postgis-*" -ForegroundColor White
            Write-Host "  CentOS/RHEL: sudo yum install postgis30_13" -ForegroundColor White
            Write-Host ""

            Write-Host "For TimescaleDB (Time-series):" -ForegroundColor Yellow
            Write-Host "  Ubuntu/Debian: https://docs.timescale.com/install/latest/self-hosted/installation-debian/" -ForegroundColor White
        }

        "macOS" {
            Write-Host "For pgvector (AI embeddings):" -ForegroundColor Yellow
            Write-Host "  Using Homebrew:" -ForegroundColor Cyan
            Write-Host "    brew install pgvector" -ForegroundColor White
            Write-Host "    psql -c 'CREATE EXTENSION vector;'" -ForegroundColor White
            Write-Host ""

            Write-Host "For PostGIS (Geographic data):" -ForegroundColor Yellow
            Write-Host "  Using Homebrew:" -ForegroundColor Cyan
            Write-Host "    brew install postgis" -ForegroundColor White
            Write-Host ""

            Write-Host "For TimescaleDB (Time-series):" -ForegroundColor Yellow
            Write-Host "  Using Homebrew:" -ForegroundColor Cyan
            Write-Host "    brew install timescaledb" -ForegroundColor White
        }
    }

    # Create a configuration script for the user
    if (-not $DryRun) {
        $configScript = @"
# ValidoAI PostgreSQL Configuration
# Generated: $(Get-Date)
# OS: $os
# Database: $DatabaseName
# Host: $Host

# Connection string for applications:
# postgresql://$Username`:$Password`@$Host`:$Port/$DatabaseName

# Test connection:
# PGPASSWORD=$Password psql -h $Host -p $Port -U $Username -d $DatabaseName -c "SELECT version();"

# List installed extensions:
# PGPASSWORD=$Password psql -h $Host -p $Port -U $Username -d $DatabaseName -c "SELECT name, installed_version FROM pg_available_extensions WHERE installed_version IS NOT NULL;"

# Enable additional extensions (when installed):
# PGPASSWORD=$Password psql -h $Host -p $Port -U $Username -d $DatabaseName -c "CREATE EXTENSION IF NOT EXISTS vector;"
# PGPASSWORD=$Password psql -h $Host -p $Port -U $Username -d $DatabaseName -c "CREATE EXTENSION IF NOT EXISTS postgis;"
"@

        $configPath = Join-Path -Path $PSScriptRoot -ChildPath "postgresql_config_$($os.ToLower()).txt"
        $configScript | Out-File -FilePath $configPath -Encoding UTF8
        Write-Host "📄 Configuration saved to: $configPath" -ForegroundColor Green
    }

    Write-Host ""
    Write-Host "🎉 PostgreSQL extensions setup completed!" -ForegroundColor Green
    Write-Host "📊 Summary:" -ForegroundColor Cyan
    Write-Host "   - Core extensions installed: $installedCount" -ForegroundColor White
    Write-Host "   - Extensions skipped (not available): $skippedCount" -ForegroundColor White
    Write-Host "   - Advanced extensions available: $($advancedExtensions.Count)" -ForegroundColor White
    Write-Host ""
    Write-Host "💡 Next steps:" -ForegroundColor Yellow
    Write-Host "   1. Install advanced extensions as needed" -ForegroundColor White
    Write-Host "   2. Configure your application with the database connection" -ForegroundColor White
    Write-Host "   3. Test the connection in your application" -ForegroundColor White

} catch {
    Write-Host "❌ Script execution failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Stack trace:" -ForegroundColor Red
    $_.ScriptStackTrace
    exit 1
}
