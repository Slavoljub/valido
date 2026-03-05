# ValidoAI Duplicate Files Analysis and Fix Script
# Focus on source code duplicates that need attention

param(
    [switch]$FixDuplicates = $false,
    [switch]$GenerateReport = $true,
    [switch]$Interactive = $true
)

Write-Host "🔍 ValidoAI Duplicate Files Analysis" -ForegroundColor Green
Write-Host "=" * 50

# Function to get source files only
function Get-SourceFiles {
    param([string]$Path)

    Get-ChildItem -Path $Path -Recurse -File | Where-Object {
        # Include source files
        $_.Extension -in @('.py', '.html', '.css', '.js', '.json', '.yaml', '.yml', '.md', '.txt', '.sql') -and
        # Exclude common directories
        $_.FullName -notmatch '\\(node_modules|venv|\.venv|__pycache__|\\.git|\.cache|dist|build)\\'
    }
}

# Function to find problematic duplicates
function Find-ProblematicDuplicates {
    param([array]$Files)

    $fileGroups = $Files | Group-Object Name

    foreach ($group in $fileGroups | Where-Object { $_.Count -gt 1 }) {
        $files = $group.Group

        # Check if files are identical
        $firstFile = $files[0]
        $allIdentical = $true

        # Compare each file with the first one
        foreach ($file in $files | Select-Object -Skip 1) {
            try {
                $firstContent = Get-Content -Path $firstFile.FullName -Raw -Encoding UTF8
                $currentContent = Get-Content -Path $file.FullName -Raw -Encoding UTF8

                if ($firstContent -ne $currentContent) {
                    $allIdentical = $false
                    break
                }
            } catch {
                $allIdentical = $false
                break
            }
        }

        # Only report if files are different or in important locations
        if (-not $allIdentical) {
            @{
                FileName = $group.Name
                Count = $group.Count
                Files = $files
                AllIdentical = $allIdentical
                Size = ($files | Measure-Object Length -Sum).Sum
            }
        }
    }
}

# Function to analyze by directory structure
function Analyze-ByDirectory {
    param([array]$Files)

    $Files | Group-Object { Split-Path $_.DirectoryName -Leaf } | ForEach-Object {
        $dirName = $_.Name
        $filesInDir = $_.Group
        $duplicatesInDir = $filesInDir | Group-Object Name | Where-Object Count -gt 1

        if ($duplicatesInDir) {
            @{
                Directory = $dirName
                DuplicateCount = ($duplicatesInDir | Measure-Object).Count
                TotalFiles = $filesInDir.Count
                Duplicates = $duplicatesInDir
            }
        }
    }
}

# Function to get recommendations
function Get-DuplicateRecommendations {
    param([array]$Duplicates)

    $recommendations = @()

    # Large number of duplicates
    if ($Duplicates.Count -gt 20) {
        $recommendations += @{
            Priority = "High"
            Issue = "High number of duplicate files ($($Duplicates.Count))"
            Action = "Consider major refactoring to eliminate redundant files"
        }
    }

    # Files with many copies
    $filesWithManyCopies = $Duplicates | Where-Object Count -gt 3
    if ($filesWithManyCopies) {
        $recommendations += @{
            Priority = "Medium"
            Issue = "$($filesWithManyCopies.Count) files have more than 3 copies"
            Action = "Review and consolidate files with multiple copies"
            Files = $filesWithManyCopies.FileName
        }
    }

    # Large files duplicated
    $largeDuplicates = $Duplicates | Where-Object Size -gt 100KB
    if ($largeDuplicates) {
        $recommendations += @{
            Priority = "High"
            Issue = "$($largeDuplicates.Count) large files are duplicated"
            Action = "Large files should not be duplicated - use shared resources"
            Files = $largeDuplicates.FileName
        }
    }

    return $recommendations
}

# Main execution
try {
    Write-Host "📂 Scanning source files..." -ForegroundColor Yellow
    $sourceFiles = Get-SourceFiles -Path $PSScriptRoot

    Write-Host "📊 Analyzing duplicates..." -ForegroundColor Yellow
    $problematicDuplicates = Find-ProblematicDuplicates -Files $sourceFiles

    Write-Host "📁 Analyzing directory structure..." -ForegroundColor Yellow
    $directoryAnalysis = Analyze-ByDirectory -Files $sourceFiles

    # Display results
    Write-Host ""
    Write-Host "📈 ANALYSIS RESULTS" -ForegroundColor Green
    Write-Host "=" * 30

    Write-Host "Total source files: $($sourceFiles.Count)" -ForegroundColor White
    Write-Host "Problematic duplicates: $($problematicDuplicates.Count)" -ForegroundColor $(if ($problematicDuplicates.Count -gt 0) { "Red" } else { "Green" })

    if ($problematicDuplicates.Count -gt 0) {
        Write-Host ""
        Write-Host "⚠️  PROBLEMATIC DUPLICATES FOUND:" -ForegroundColor Red

        foreach ($dup in $problematicDuplicates | Sort-Object Count -Descending) {
            Write-Host ""
            Write-Host "📄 $($dup.FileName)" -ForegroundColor Yellow
            Write-Host "   Copies: $($dup.Count)" -ForegroundColor White
            Write-Host "   Total size: $([math]::Round($dup.Size / 1KB, 2)) KB" -ForegroundColor White
            Write-Host "   Locations:" -ForegroundColor White

            foreach ($file in $dup.Files) {
                Write-Host "     $($file.FullName)" -ForegroundColor Gray
            }
        }
    }

    # Directory analysis
    if ($directoryAnalysis) {
        Write-Host ""
        Write-Host "📂 DUPLICATES BY DIRECTORY:" -ForegroundColor Cyan

        foreach ($dir in $directoryAnalysis | Sort-Object DuplicateCount -Descending) {
            Write-Host "  $($dir.Directory): $($dir.DuplicateCount) duplicates ($($dir.TotalFiles) files)" -ForegroundColor White
        }
    }

    # Recommendations
    $recommendations = Get-DuplicateRecommendations -Duplicates $problematicDuplicates

    if ($recommendations) {
        Write-Host ""
        Write-Host "💡 RECOMMENDATIONS:" -ForegroundColor Magenta

        foreach ($rec in $recommendations) {
            $color = switch ($rec.Priority) {
                "High" { "Red" }
                "Medium" { "Yellow" }
                "Low" { "Green" }
            }

            Write-Host "  [$($rec.Priority)] $($rec.Issue)" -ForegroundColor $color
            Write-Host "  Action: $($rec.Action)" -ForegroundColor White

            if ($rec.Files) {
                Write-Host "  Files: $($rec.Files -join ', ')" -ForegroundColor Gray
            }
            Write-Host ""
        }
    }

    # Generate detailed report
    if ($GenerateReport) {
        $reportPath = Join-Path -Path $PSScriptRoot -ChildPath "duplicate_analysis_$(Get-Date -Format 'yyyyMMdd_HHmmss').txt"

        $report = @"
ValidoAI Duplicate Files Analysis Report
=========================================
Generated: $(Get-Date)
Total source files: $($sourceFiles.Count)
Problematic duplicates: $($problematicDuplicates.Count)

DETAILED FINDINGS:
==================
"@

        if ($problematicDuplicates) {
            foreach ($dup in $problematicDuplicates) {
                $report += "`n`nFile: $($dup.FileName)"
                $report += "`nCopies: $($dup.Count)"
                $report += "`nSize: $([math]::Round($dup.Size / 1KB, 2)) KB"
                $report += "`nLocations:"
                foreach ($file in $dup.Files) {
                    $report += "`n  $($file.FullName)"
                }
            }
        }

        $report | Out-File -FilePath $reportPath -Encoding UTF8
        Write-Host "📄 Detailed report saved to: $reportPath" -ForegroundColor Green
    }

    # Interactive fixing
    if ($Interactive -and $problematicDuplicates) {
        Write-Host ""
        Write-Host "🔧 INTERACTIVE MODE" -ForegroundColor Yellow
        $fix = Read-Host "Do you want to review and fix duplicates? (y/N)"

        if ($fix -eq 'y' -or $fix -eq 'Y') {
            foreach ($dup in $problematicDuplicates) {
                Write-Host ""
                Write-Host "📄 Processing: $($dup.FileName)" -ForegroundColor Yellow
                Write-Host "Found $($dup.Count) copies:" -ForegroundColor White

                for ($i = 0; $i -lt $dup.Files.Count; $i++) {
                    $file = $dup.Files[$i]
                    Write-Host "  [$i] $($file.FullName)" -ForegroundColor Gray
                }

                $action = Read-Host "Action: (s)kip, (d)elete specific, (k)eep first delete rest, (v)iew differences"

                switch ($action) {
                    'd' {
                        $indices = Read-Host "Enter indices to delete (comma-separated)"
                        $indices -split ',' | ForEach-Object {
                            $index = $_.Trim() -as [int]
                            if ($index -ge 0 -and $index -lt $dup.Files.Count) {
                                $fileToDelete = $dup.Files[$index]
                                Remove-Item -Path $fileToDelete.FullName -Force
                                Write-Host "  Deleted: $($fileToDelete.FullName)" -ForegroundColor Red
                            }
                        }
                    }
                    'k' {
                        for ($i = 1; $i -lt $dup.Files.Count; $i++) {
                            $fileToDelete = $dup.Files[$i]
                            Remove-Item -Path $fileToDelete.FullName -Force
                            Write-Host "  Deleted: $($fileToDelete.FullName)" -ForegroundColor Red
                        }
                    }
                    'v' {
                        if ($dup.Files.Count -ge 2) {
                            Write-Host "Comparing first two files..." -ForegroundColor Cyan
                            $diff = Compare-Object (Get-Content $dup.Files[0].FullName) (Get-Content $dup.Files[1].FullName)
                            if ($diff) {
                                Write-Host "Files are different. First 10 differences:" -ForegroundColor Yellow
                                $diff | Select-Object -First 10 | ForEach-Object {
                                    Write-Host "  $($_.SideIndicator) $($_.InputObject)" -ForegroundColor Gray
                                }
                            } else {
                                Write-Host "Files are identical" -ForegroundColor Green
                            }
                        }
                    }
                }
            }
        }
    }

    Write-Host ""
    Write-Host "✅ Analysis completed!" -ForegroundColor Green

} catch {
    Write-Error "❌ Error during analysis: $($_.Exception.Message)"
    Write-Host "Stack trace:" -ForegroundColor Red
    $_.ScriptStackTrace
}
