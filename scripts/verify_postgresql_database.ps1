# ValidoAI PostgreSQL Database Verification Script
# Check tables, columns, and implementation status

param(
    [string]$PostgresPath = "",
    [string]$DatabaseName = "ai_valido_online",
    [string]$Username = "postgres",
    [string]$Password = "postgres",
    [string]$Host = "localhost",
    [int]$Port = 5432,
    [switch]$Detailed = $false,
    [switch]$ExportSchema = $false
)

# Function to detect PostgreSQL installation path
function Find-PostgreSQLPath {
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
        "C:\Program Files (x86)\PostgreSQL\13\bin",
        "/usr/bin",
        "/usr/local/bin",
        "/usr/lib/postgresql/*/bin",
        "/usr/pgsql-*/bin"
    )

    foreach ($path in $possiblePaths) {
        if (Test-Path (Join-Path $path "psql")) {
            return $path
        }
    }

    return $null
}

# Function to run psql commands
function Invoke-PsqlQuery {
    param([string]$Query, [string]$Description)

    Write-Host "🔍 $Description..." -ForegroundColor Yellow
    try {
        $env:PGPASSWORD = $Password
        $result = & "$PostgresPath\psql" -h $Host -p $Port -U $Username -d $DatabaseName -c $Query 2>&1

        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ $Description completed" -ForegroundColor Green
            return $result
        } else {
            Write-Host "❌ $Description failed: $result" -ForegroundColor Red
            return $null
        }
    }
    catch {
        Write-Host "❌ $Description error: $($_.Exception.Message)" -ForegroundColor Red
        return $null
    }
}

# Function to parse psql output
function Parse-PsqlOutput {
    param([string]$Output)

    $lines = $Output -split "`n" | Where-Object { $_ -and $_ -notmatch '^\s*$' -and $_ -notmatch '^\(' -and $_ -notmatch 'rows\)' -and $_ -notmatch '^\s*-+\s*$' }
    return $lines
}

# Main execution
try {
    Write-Host "🔍 ValidoAI PostgreSQL Database Verification" -ForegroundColor Green
    Write-Host "=" * 50
    Write-Host ""

    # Find PostgreSQL installation
    if (-not $PostgresPath) {
        Write-Host "🔍 Searching for PostgreSQL installation..." -ForegroundColor Yellow
        $PostgresPath = Find-PostgreSQLPath
    }

    if (-not $PostgresPath -or -not (Test-Path (Join-Path $PostgresPath "psql"))) {
        Write-Host "❌ PostgreSQL psql not found!" -ForegroundColor Red
        Write-Host "Please ensure PostgreSQL is installed and psql is in PATH" -ForegroundColor Yellow
        exit 1
    }

    Write-Host "✅ PostgreSQL found at: $PostgresPath" -ForegroundColor Green

    # Test connection
    Write-Host "🔗 Testing database connection..." -ForegroundColor Yellow
    $testResult = Invoke-PsqlQuery "SELECT version();" "Connection test"
    if (-not $testResult) {
        exit 1
    }

    # Check all tables
    Write-Host ""
    Write-Host "📊 DATABASE TABLES VERIFICATION" -ForegroundColor Cyan
    Write-Host "=" * 35

    $tablesQuery = @"
SELECT
    schemaname,
    tablename,
    tableowner,
    tablespace,
    hasindexes,
    hasrules,
    hastriggers,
    rowsecurity
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY tablename;
"@

    $tablesResult = Invoke-PsqlQuery $tablesQuery "Listing all tables"
    if ($tablesResult) {
        $tableLines = Parse-PsqlOutput $tablesResult
        Write-Host ""
        Write-Host "Found tables:" -ForegroundColor White
        foreach ($line in $tableLines) {
            if ($line -match '\s+(\w+)\s*$') {
                Write-Host "  - $($Matches[1])" -ForegroundColor Green
            }
        }
    }

    # Check table structures
    Write-Host ""
    Write-Host "📋 TABLE STRUCTURES VERIFICATION" -ForegroundColor Cyan
    Write-Host "=" * 35

    $structureQuery = @"
SELECT
    table_name,
    column_name,
    data_type,
    is_nullable,
    column_default,
    character_maximum_length
FROM information_schema.columns
WHERE table_schema = 'public'
ORDER BY table_name, ordinal_position;
"@

    $structureResult = Invoke-PsqlQuery $structureQuery "Getting table structures"
    if ($structureResult) {
        Write-Host ""
        Write-Host "Table structures:" -ForegroundColor White
        $currentTable = ""
        $structureLines = Parse-PsqlOutput $structureResult

        foreach ($line in $structureLines) {
            if ($line -match '^(\w+)\s+\|\s+(\w+)') {
                $tableName = $Matches[1]
                if ($currentTable -ne $tableName) {
                    $currentTable = $tableName
                    Write-Host ""
                    Write-Host "📄 $tableName" -ForegroundColor Yellow
                }
                Write-Host "  $line" -ForegroundColor Gray
            }
        }
    }

    # Check indexes
    Write-Host ""
    Write-Host "🔑 INDEXES VERIFICATION" -ForegroundColor Cyan
    Write-Host "=" * 25

    $indexesQuery = @"
SELECT
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'public'
ORDER BY tablename, indexname;
"@

    $indexesResult = Invoke-PsqlQuery $indexesQuery "Getting indexes"
    if ($indexesResult) {
        Write-Host ""
        Write-Host "Indexes found:" -ForegroundColor White
        $indexLines = Parse-PsqlOutput $indexesResult

        foreach ($line in $indexLines) {
            if ($line -match '\s+(\w+)\s*$') {
                Write-Host "  - $($Matches[1])" -ForegroundColor Cyan
            }
        }
    }

    # Check foreign keys
    Write-Host ""
    Write-Host "🔗 FOREIGN KEY RELATIONSHIPS" -ForegroundColor Cyan
    Write-Host "=" * 30

    $fkQuery = @"
SELECT
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
  ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
  ON ccu.constraint_name = tc.constraint_name
WHERE constraint_type = 'FOREIGN KEY' AND tc.table_schema = 'public'
ORDER BY tc.table_name, kcu.column_name;
"@

    $fkResult = Invoke-PsqlQuery $fkQuery "Getting foreign keys"
    if ($fkResult) {
        Write-Host ""
        Write-Host "Foreign key relationships:" -ForegroundColor White
        $fkLines = Parse-PsqlOutput $fkResult

        foreach ($line in $fkLines) {
            Write-Host "  $line" -ForegroundColor Magenta
        }
    }

    # Check data counts
    Write-Host ""
    Write-Host "📈 DATA COUNTS VERIFICATION" -ForegroundColor Cyan
    Write-Host "=" * 30

    $dataTables = @('users', 'companies', 'invoices', 'customers', 'products', 'ai_insights', 'chat_sessions', 'content')

    foreach ($table in $dataTables) {
        $countQuery = "SELECT COUNT(*) FROM $table;" 2>$null
        if ($countQuery) {
            $countResult = Invoke-PsqlQuery "SELECT COUNT(*) FROM $table;" "$table count"
            if ($countResult) {
                $countLines = Parse-PsqlOutput $countResult
                foreach ($line in $countLines) {
                    if ($line -match '\s+(\d+)\s*$') {
                        Write-Host "  $table`: $($Matches[1]) records" -ForegroundColor $(if ($Matches[1] -gt 0) { "Green" } else { "Yellow" })
                    }
                }
            }
        }
    }

    # Check extensions
    Write-Host ""
    Write-Host "🔧 INSTALLED EXTENSIONS" -ForegroundColor Cyan
    Write-Host "=" * 25

    $extensionsQuery = @"
SELECT
    name,
    default_version,
    installed_version
FROM pg_available_extensions
WHERE installed_version IS NOT NULL
ORDER BY name;
"@

    $extensionsResult = Invoke-PsqlQuery $extensionsQuery "Getting installed extensions"
    if ($extensionsResult) {
        Write-Host ""
        Write-Host "Installed extensions:" -ForegroundColor White
        $extLines = Parse-PsqlOutput $extensionsResult

        foreach ($line in $extLines) {
            if ($line -match '^(\w+)') {
                Write-Host "  - $($Matches[1])" -ForegroundColor Green
            }
        }
    }

    # Check for missing critical tables
    Write-Host ""
    Write-Host "⚠️  MISSING TABLES CHECK" -ForegroundColor Yellow
    Write-Host "=" * 25

    $criticalTables = @(
        'users',
        'companies',
        'invoices',
        'customers',
        'products',
        'ai_insights',
        'chat_sessions',
        'content',
        'workflows',
        'reports'
    )

    $missingTables = @()

    foreach ($table in $criticalTables) {
        $checkQuery = "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = '$table');"
        $checkResult = Invoke-PsqlQuery $checkQuery "Checking $table existence" 2>$null

        if ($checkResult -and $checkResult -match 'f') {
            $missingTables += $table
        }
    }

    if ($missingTables.Count -gt 0) {
        Write-Host ""
        Write-Host "Missing critical tables:" -ForegroundColor Red
        foreach ($table in $missingTables) {
            Write-Host "  - $table" -ForegroundColor Red
        }
        Write-Host ""
        Write-Host "💡 Run the database creation scripts to create missing tables" -ForegroundColor Yellow
    } else {
        Write-Host ""
        Write-Host "✅ All critical tables are present" -ForegroundColor Green
    }

    # Export schema if requested
    if ($ExportSchema) {
        Write-Host ""
        Write-Host "📤 EXPORTING DATABASE SCHEMA" -ForegroundColor Cyan
        Write-Host "=" * 30

        $exportPath = Join-Path -Path $PSScriptRoot -ChildPath "database_schema_$(Get-Date -Format 'yyyyMMdd_HHmmss').sql"

        $env:PGPASSWORD = $Password
        & "$PostgresPath\pg_dump" -h $Host -p $Port -U $Username -d $DatabaseName --schema-only -f $exportPath

        if (Test-Path $exportPath) {
            Write-Host "✅ Schema exported to: $exportPath" -ForegroundColor Green
        } else {
            Write-Host "❌ Schema export failed" -ForegroundColor Red
        }
    }

    # Generate comprehensive report
    $reportPath = Join-Path -Path $PSScriptRoot -ChildPath "database_verification_report_$(Get-Date -Format 'yyyyMMdd_HHmmss').txt"

    $report = @"
ValidoAI PostgreSQL Database Verification Report
===============================================
Generated: $(Get-Date)
Database: $DatabaseName
Host: $Host
Port: $Port

SUMMARY
=======
PostgreSQL Connection: $(if ($testResult) { "SUCCESS" } else { "FAILED" })
Missing Critical Tables: $($missingTables.Count)
Total Tables Found: $(($tableLines | Measure-Object).Count)
Total Indexes Found: $(($indexLines | Measure-Object).Count)

$(if ($missingTables.Count -gt 0) {
"CRITICAL ISSUES FOUND:
=====================
Missing Tables: $($missingTables -join ', ')

RECOMMENDATIONS:
===============
1. Run database creation scripts
2. Check SQL file permissions
3. Verify PostgreSQL user permissions
4. Review database connection settings
"
} else {
"DATABASE HEALTH: EXCELLENT
==========================
All critical tables are present and accessible.
"
})

TECHNICAL DETAILS
================
PostgreSQL Path: $PostgresPath
Connection String: postgresql://$Username`:***@$Host`:$Port/$DatabaseName

For application configuration:
DB_HOST=$Host
DB_PORT=$Port
DB_NAME=$DatabaseName
DB_USER=$Username
DB_PASSWORD=***
"@

    $report | Out-File -FilePath $reportPath -Encoding UTF8
    Write-Host ""
    Write-Host "📄 Detailed report saved to: $reportPath" -ForegroundColor Green

    Write-Host ""
    Write-Host "🎉 Database verification completed!" -ForegroundColor Green

    if ($missingTables.Count -gt 0) {
        Write-Host "⚠️  Some tables are missing. Please run database creation scripts." -ForegroundColor Yellow
        exit 1
    } else {
        Write-Host "✅ Database is properly configured and ready for use." -ForegroundColor Green
        exit 0
    }

} catch {
    Write-Host "❌ Script execution failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Stack trace:" -ForegroundColor Red
    $_.ScriptStackTrace
    exit 1
}
