# =============================================================================
# VALIDOAI - CLEAN REDUNDANT CONFIGURATION SCRIPTS
# =============================================================================
# Remove redundant scripts that have been merged into master configuration scripts

param(
    [switch]$DryRun,
    [switch]$Force,
    [string]$LogFile = "script_cleanup.log"
)

# Configuration
$ScriptPath = $PSScriptRoot
$LogPath = Join-Path $ScriptPath $LogFile

# Scripts to remove (merged into master config)
$RedundantScripts = @(
    # PostgreSQL setup scripts (merged into master config)
    "connect_postgres.ps1",
    "install_postgres_extensions_auto.ps1",
    "install_postgres_extensions.ps1",
    "pg_extensions.ps1",
    "postgres_configure.ps1",
    "postgres_extensions_install.ps1",
    "postgres_performance_optimize.ps1",
    "postgres_setup_summary.ps1",
    "setup_database_auto.ps1",
    "setup_postgres_consolidated.ps1",
    "test_postgres_consolidated.ps1",
    "validate_database_completeness.ps1",

    # Source optimization scripts (merged into master config)
    "clean_src_directory.ps1",
    "optimize_src_structure.ps1",

    # General setup scripts (merged into master config)
    "setup_comprehensive.ps1",
    "setup_comprehensivex.ps1",
    "setup_julia_environment.ps1",
    "validoai_cleanup.ps1",

    # Fix scripts (project-specific, may not be needed anymore)
    "fix_data_loading.ps1",
    "fix_missing_functions_v2.ps1",
    "fix_missing_functions_v3.ps1",
    "fix_missing_functions.ps1",
    "fix_missing_tables_v2.ps1",
    "fix_missing_tables.ps1"
)

# Scripts to keep (still have unique value)
$KeepScripts = @(
    "validoai_master_config.ps1",
    "validoai_master_config.sh",
    "README.md",
    "README_ValidoAI_PostgreSQL_Setup.md"
)

# Documentation files to potentially archive
$DocumentationFiles = @(
    "validoai_advanced_features_plan.md",
    "validoai_current_state_assessment.md",
    "validoai_final_consolidation_plan.md",
    "validoai_final_status_report.md",
    "validoai_final_truthful_summary.md",
    "validoai_truthful_assessment.md"
)

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

function Write-Log {
    param([string]$Message)
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$Timestamp - $Message" | Out-File -FilePath $LogPath -Append
}

function Get-ScriptStats {
    $totalScripts = (Get-ChildItem -Path $ScriptPath -File -Include "*.ps1", "*.sh", "*.md").Count
    $redundantCount = $RedundantScripts.Count
    $keepCount = $KeepScripts.Count

    return @{
        Total = $totalScripts
        Redundant = $redundantCount
        Keep = $keepCount
        Documentation = $DocumentationFiles.Count
    }
}

function Show-Analysis {
    Write-ColoredMessage "🔍 Analyzing configuration scripts directory..." "Blue"
    Write-ColoredMessage "" "White"

    $stats = Get-ScriptStats

    Write-ColoredMessage "📊 Current Status:" "Cyan"
    Write-ColoredMessage "   Total scripts: $($stats.Total)" "White"
    Write-ColoredMessage "   Master scripts: 2 (validoai_master_config.ps1/.sh)" "Green"
    Write-ColoredMessage "   Redundant scripts: $($stats.Redundant)" "Yellow"
    Write-ColoredMessage "   Scripts to keep: $($stats.Keep)" "Green"
    Write-ColoredMessage "   Documentation: $($stats.Documentation)" "Blue"
    Write-ColoredMessage "" "White"

    Write-ColoredMessage "🗑️ Scripts to be removed:" "Yellow"
    foreach ($script in $RedundantScripts) {
        $scriptPath = Join-Path $ScriptPath $script
        if (Test-Path $scriptPath) {
            $size = (Get-Item $scriptPath).Length
            Write-ColoredMessage "   - $script ($([math]::Round($size/1KB, 2)) KB)" "Yellow"
        } else {
            Write-ColoredMessage "   - $script (not found)" "Red"
        }
    }

    Write-ColoredMessage "" "White"
    Write-ColoredMessage "✅ Scripts to keep:" "Green"
    foreach ($script in $KeepScripts) {
        $scriptPath = Join-Path $ScriptPath $script
        if (Test-Path $scriptPath) {
            $size = (Get-Item $scriptPath).Length
            Write-ColoredMessage "   - $script ($([math]::Round($size/1KB, 2)) KB)" "Green"
        } else {
            Write-ColoredMessage "   - $script (not found)" "Red"
        }
    }
}

function Remove-RedundantScripts {
    param([switch]$DryRun, [switch]$Force)

    $removedCount = 0
    $totalSize = 0

    Write-ColoredMessage "🗑️ Removing redundant scripts..." "Blue"
    Write-Log "Starting cleanup of redundant configuration scripts"

    foreach ($script in $RedundantScripts) {
        $scriptPath = Join-Path $ScriptPath $script

        if (Test-Path $scriptPath) {
            $fileInfo = Get-Item $scriptPath
            $size = $fileInfo.Length

            if ($DryRun) {
                Write-ColoredMessage "   Would remove: $script ($([math]::Round($size/1KB, 2)) KB)" "Yellow"
            } else {
                try {
                    Remove-Item -Path $scriptPath -Force
                    Write-ColoredMessage "   ✅ Removed: $script ($([math]::Round($size/1KB, 2)) KB)" "Green"
                    Write-Log "Removed: $script ($size bytes)"
                    $removedCount++
                    $totalSize += $size
                } catch {
                    Write-ColoredMessage "   ❌ Failed to remove: $script - $($_.Exception.Message)" "Red"
                    Write-Log "Failed to remove: $script - $($_.Exception.Message)"
                }
            }
        } else {
            Write-ColoredMessage "   ⚠️ Not found: $script" "Yellow"
        }
    }

    if (-not $DryRun -and $removedCount -gt 0) {
        Write-ColoredMessage "" "White"
        Write-ColoredMessage "📊 Cleanup Summary:" "Cyan"
        Write-ColoredMessage "   Files removed: $removedCount" "Green"
        Write-ColoredMessage "   Space freed: $([math]::Round($totalSize/1KB, 2)) KB" "Green"
        Write-ColoredMessage "   Log saved to: $LogPath" "Blue"
    }

    return @{
        RemovedCount = $removedCount
        TotalSizeFreed = $totalSize
    }
}

function Archive-Documentation {
    param([switch]$DryRun)

    $archiveDir = Join-Path $ScriptPath "archived_docs"

    if ($DryRun) {
        Write-ColoredMessage "📁 Would create archive directory: $archiveDir" "Blue"
        foreach ($doc in $DocumentationFiles) {
            $docPath = Join-Path $ScriptPath $doc
            if (Test-Path $docPath) {
                Write-ColoredMessage "   Would archive: $doc" "Yellow"
            }
        }
        return
    }

    if (-not (Test-Path $archiveDir)) {
        New-Item -ItemType Directory -Path $archiveDir | Out-Null
        Write-ColoredMessage "📁 Created archive directory: $archiveDir" "Blue"
    }

    $archivedCount = 0
    foreach ($doc in $DocumentationFiles) {
        $docPath = Join-Path $ScriptPath $doc
        $archivePath = Join-Path $archiveDir $doc

        if (Test-Path $docPath) {
            try {
                Move-Item -Path $docPath -Destination $archivePath
                Write-ColoredMessage "   📄 Archived: $doc" "Blue"
                Write-Log "Archived documentation: $doc"
                $archivedCount++
            } catch {
                Write-ColoredMessage "   ❌ Failed to archive: $doc" "Red"
            }
        }
    }

    if ($archivedCount -gt 0) {
        Write-ColoredMessage "📊 Archived $archivedCount documentation files to $archiveDir" "Green"
    }
}

# Main execution
Write-ColoredMessage "🧹 ValidoAI Configuration Scripts Cleanup" "Magenta"
Write-ColoredMessage "=====================================" "Magenta"
Write-ColoredMessage "" "White"

if ($DryRun) {
    Write-ColoredMessage "🔍 DRY RUN MODE - No files will be modified" "Yellow"
    Write-ColoredMessage "" "White"
}

# Show analysis first
Show-Analysis
Write-ColoredMessage "" "White"

# Confirm before proceeding with actual removal
if (-not $DryRun -and -not $Force) {
    $confirmation = Read-Host "Do you want to proceed with removing redundant scripts? (y/N)"
    if ($confirmation -ne 'y' -and $confirmation -ne 'Y') {
        Write-ColoredMessage "❌ Operation cancelled by user" "Yellow"
        exit 0
    }
}

# Remove redundant scripts
$result = Remove-RedundantScripts -DryRun:$DryRun -Force:$Force

# Optionally archive documentation
if (-not $DryRun) {
    Write-ColoredMessage "" "White"
    $archiveDocs = Read-Host "Do you want to archive documentation files? (y/N)"
    if ($archiveDocs -eq 'y' -or $archiveDocs -eq 'Y') {
        Archive-Documentation -DryRun:$DryRun
    }
}

# Final summary
Write-ColoredMessage "" "White"
if ($DryRun) {
    Write-ColoredMessage "🔍 Dry run completed. Use -Force to actually remove files." "Cyan"
} else {
    Write-ColoredMessage "✅ Cleanup completed successfully!" "Green"
    Write-ColoredMessage "" "White"
    Write-ColoredMessage "🎯 Remaining files:" "Cyan"
    Get-ChildItem -Path $ScriptPath -File | ForEach-Object {
        Write-ColoredMessage "   - $($_.Name) ($([math]::Round($_.Length/1KB, 2)) KB)" "White"
    }
}

Write-ColoredMessage "" "White"
Write-ColoredMessage "📖 For help, see README.md in the configuration_scripts directory" "Blue"
