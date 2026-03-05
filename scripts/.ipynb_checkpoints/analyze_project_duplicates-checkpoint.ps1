# ValidoAI Project Analysis Script
# Comprehensive duplicate file analysis and project organization recommendations

param(
    [string]$ProjectPath = $PSScriptRoot,
    [switch]$RemoveDuplicates = $false,
    [switch]$GenerateReport = $true
)

# Function to analyze project structure
function Analyze-ProjectStructure {
    param([string]$Path)

    Write-Host "🔍 Analyzing project structure..." -ForegroundColor Cyan

    # Get all files excluding common ignore patterns
    $files = Get-ChildItem -Path $Path -Recurse -File -Exclude @(
        "*.pyc", "*.pyo", "__pycache__", "*.log", ".git*", "node_modules", "venv", ".venv",
        "*.min.js", "*.min.css", "*.map", "*.cache", "*.tmp", "*.temp"
    ) | Where-Object {
        $_.FullName -notmatch '\\(node_modules|venv|\.venv|__pycache__|\\.git)\\'
    }

    # Group by filename
    $fileGroups = $files | Group-Object Name

    # Find duplicates
    $duplicates = $fileGroups | Where-Object { $_.Count -gt 1 }

    return @{
        TotalFiles = $files.Count
        DuplicateGroups = $duplicates
        FileTypes = $files | Group-Object Extension | Sort-Object Count -Descending
        LargestFiles = $files | Sort-Object Length -Descending | Select-Object -First 10
        EmptyFiles = $files | Where-Object { $_.Length -eq 0 }
    }
}

# Function to analyze directory structure
function Analyze-DirectoryStructure {
    param([string]$Path)

    Write-Host "📁 Analyzing directory structure..." -ForegroundColor Cyan

    $directories = Get-ChildItem -Path $Path -Directory -Recurse | Where-Object {
        $_.FullName -notmatch '\\(node_modules|venv|\.venv|__pycache__|\\.git)\\'
    }

    return @{
        TotalDirectories = $directories.Count
        DirectorySizes = $directories | ForEach-Object {
            $size = (Get-ChildItem -Path $_.FullName -Recurse -File -ErrorAction SilentlyContinue | Measure-Object Length -Sum).Sum
            [PSCustomObject]@{
                Path = $_.FullName
                SizeMB = [math]::Round($size / 1MB, 2)
                FileCount = (Get-ChildItem -Path $_.FullName -Recurse -File -ErrorAction SilentlyContinue).Count
            }
        } | Sort-Object SizeMB -Descending
    }
}

# Function to identify problematic duplicates
function Get-ProblematicDuplicates {
    param([array]$Duplicates)

    $problematic = @()

    foreach ($group in $Duplicates) {
        $files = $group.Group

        # Check if files are in different important directories
        $paths = $files | Select-Object -ExpandProperty DirectoryName

        # Check if these are source code files that shouldn't be duplicated
        $sourceExtensions = @('.py', '.html', '.css', '.js', '.sql', '.md', '.json', '.yaml', '.yml')
        $isSourceFile = $sourceExtensions -contains $files[0].Extension

        # Check if files are identical
        $firstFile = $files[0]
        $allIdentical = $true
        $firstHash = Get-FileHash -Path $firstFile.FullName -Algorithm SHA256

        foreach ($file in $files | Select-Object -Skip 1) {
            $hash = Get-FileHash -Path $file.FullName -Algorithm SHA256
            if ($hash.Hash -ne $firstHash.Hash) {
                $allIdentical = $false
                break
            }
        }

        if ($isSourceFile -and -not $allIdentical) {
            $problematic += @{
                FileName = $group.Name
                Count = $group.Count
                Files = $files
                IsIdentical = $allIdentical
                IsSourceFile = $isSourceFile
            }
        }
    }

    return $problematic
}

# Function to generate recommendations
function Get-Recommendations {
    param([hashtable]$Analysis)

    $recommendations = @()

    # Check for large files
    $largeFiles = $Analysis.LargestFiles | Where-Object { $_.Length -gt 10MB }
    if ($largeFiles) {
        $recommendations += @{
            Type = "Performance"
            Priority = "High"
            Title = "Large Files Detected"
            Description = "Found $($largeFiles.Count) files larger than 10MB"
            Action = "Consider moving large files to external storage or implementing streaming"
            Files = $largeFiles.Name
        }
    }

    # Check for empty files
    if ($Analysis.EmptyFiles.Count -gt 0) {
        $recommendations += @{
            Type = "Cleanup"
            Priority = "Low"
            Title = "Empty Files Found"
            Description = "Found $($Analysis.EmptyFiles.Count) empty files"
            Action = "Review and remove unnecessary empty files"
            Files = $Analysis.EmptyFiles.Name
        }
    }

    # Check for many small files
    $smallFiles = $Analysis.FileTypes | Where-Object { $_.Name -eq ".py" -and $_.Count -gt 100 }
    if ($smallFiles) {
        $recommendations += @{
            Type = "Organization"
            Priority = "Medium"
            Title = "Many Small Files"
            Description = "Found $($smallFiles.Count) Python files - consider consolidating"
            Action = "Review if small files can be combined into modules"
            Files = $smallFiles.Name
        }
    }

    # Check directory structure
    $dirAnalysis = Analyze-DirectoryStructure -Path $ProjectPath
    $largeDirs = $dirAnalysis.DirectorySizes | Where-Object { $_.SizeMB -gt 100 }
    if ($largeDirs) {
        $recommendations += @{
            Type = "Organization"
            Priority = "High"
            Title = "Large Directories"
            Description = "Found $($largeDirs.Count) directories larger than 100MB"
            Action = "Consider splitting large directories or implementing subdirectories"
            Directories = $largeDirs
        }
    }

    return $recommendations
}

# Main execution
try {
    Write-Host "🚀 ValidoAI Project Analysis Tool" -ForegroundColor Green
    Write-Host "=================================" -ForegroundColor Green
    Write-Host ""

    # Analyze project
    $analysis = Analyze-ProjectStructure -Path $ProjectPath

    Write-Host "📊 Project Statistics:" -ForegroundColor Yellow
    Write-Host "   Total Files: $($analysis.TotalFiles)" -ForegroundColor White
    Write-Host "   Duplicate Groups: $($analysis.DuplicateGroups.Count)" -ForegroundColor White
    Write-Host "   File Types: $($analysis.FileTypes.Count)" -ForegroundColor White
    Write-Host ""

    # Analyze duplicates
    $problematicDuplicates = Get-ProblematicDuplicates -Duplicates $analysis.DuplicateGroups

    Write-Host "🔍 Duplicate Analysis:" -ForegroundColor Yellow
    Write-Host "   Problematic Duplicates: $($problematicDuplicates.Count)" -ForegroundColor White
    Write-Host ""

    if ($problematicDuplicates.Count -gt 0) {
        Write-Host "⚠️  Problematic Duplicates Found:" -ForegroundColor Red
        foreach ($dup in $problematicDuplicates) {
            Write-Host "   - $($dup.FileName): $($dup.Count) copies" -ForegroundColor Red
            foreach ($file in $dup.Files) {
                Write-Host "     $($file.FullName)" -ForegroundColor Gray
            }
            Write-Host ""
        }
    }

    # Generate recommendations
    $recommendations = Get-Recommendations -Analysis $analysis

    Write-Host "💡 Recommendations:" -ForegroundColor Yellow
    foreach ($rec in $recommendations) {
        $color = switch ($rec.Priority) {
            "High" { "Red" }
            "Medium" { "Yellow" }
            "Low" { "Green" }
            default { "White" }
        }

        Write-Host "   [$($rec.Priority)] $($rec.Title)" -ForegroundColor $color
        Write-Host "   $($rec.Description)" -ForegroundColor Gray
        Write-Host "   Action: $($rec.Action)" -ForegroundColor White
        Write-Host ""
    }

    # Generate detailed report
    if ($GenerateReport) {
        $reportPath = Join-Path -Path $ProjectPath -ChildPath "project_analysis_$(Get-Date -Format 'yyyyMMdd_HHmmss').txt"

        $report = @"
ValidoAI Project Analysis Report
=================================
Generated: $(Get-Date)
Project Path: $ProjectPath

PROJECT STATISTICS
==================
Total Files: $($analysis.TotalFiles)
Duplicate Groups: $($analysis.DuplicateGroups.Count)
File Types: $($analysis.FileTypes.Count)
Empty Files: $($analysis.EmptyFiles.Count)

FILE TYPES BREAKDOWN
===================
$(($analysis.FileTypes | ForEach-Object { "  $($_.Name): $($_.Count) files" }) -join "`n")

LARGEST FILES
=============
$(($analysis.LargestFiles | ForEach-Object { "  $($_.Name): $([math]::Round($_.Length / 1MB, 2)) MB" }) -join "`n")

DUPLICATE ANALYSIS
=================
Problematic Duplicates: $($problematicDuplicates.Count)
"@
        if ($problematicDuplicates) {
            $report += "`n`nPROBLEMATIC DUPLICATES:`n"
            foreach ($dup in $problematicDuplicates) {
                $report += "`n- $($dup.FileName) ($($dup.Count) copies):`n"
                foreach ($file in $dup.Files) {
                    $report += "  $($file.FullName)`n"
                }
            }
        }

        $report | Out-File -FilePath $reportPath -Encoding UTF8
        Write-Host "📄 Detailed report saved to: $reportPath" -ForegroundColor Green
    }

    # Remove duplicates if requested
    if ($RemoveDuplicates -and $problematicDuplicates.Count -gt 0) {
        Write-Host "🗑️  Removing duplicates..." -ForegroundColor Red
        Write-Host "⚠️  This action cannot be undone. Please review the analysis first." -ForegroundColor Yellow

        $confirmation = Read-Host "Are you sure you want to remove duplicates? (y/N)"
        if ($confirmation -eq 'y' -or $confirmation -eq 'Y') {
            foreach ($dup in $problematicDuplicates) {
                # Keep the first file, remove the rest
                $files = $dup.Files | Sort-Object LastWriteTime -Descending
                for ($i = 1; $i -lt $files.Count; $i++) {
                    Remove-Item -Path $files[$i].FullName -Force
                    Write-Host "   Removed: $($files[$i].FullName)" -ForegroundColor Yellow
                }
            }
            Write-Host "✅ Duplicate removal completed" -ForegroundColor Green
        } else {
            Write-Host "❌ Duplicate removal cancelled" -ForegroundColor Yellow
        }
    }

    Write-Host ""
    Write-Host "🎉 Analysis completed successfully!" -ForegroundColor Green

} catch {
    Write-Error "❌ Error during analysis: $($_.Exception.Message)"
    Write-Host "Stack trace:" -ForegroundColor Red
    $_.ScriptStackTrace
}
