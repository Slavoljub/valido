# ValidoAI Documentation Consolidation Script
# Consolidates 54 documentation files into 8 organized files
# Based on 28-08-all.md Implementation Plan

param(
    [switch]$DryRun,
    [switch]$Backup,
    [switch]$Execute
)

# Configuration
$ProjectRoot = Get-Location
$DocsDir = "$ProjectRoot\docs"
$BackupDir = "$ProjectRoot\backup_docs_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
$LogFile = "$ProjectRoot\docs_consolidation_log.txt"

# Initialize logging
function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] [$Level] $Message"
    Write-Host $logMessage
    Add-Content -Path $LogFile -Value $logMessage
}

# Create backup
function Backup-Documentation {
    Write-Log "Creating backup of current documentation..."
    if (Test-Path $BackupDir) {
        Remove-Item $BackupDir -Recurse -Force
    }
    Copy-Item -Path $DocsDir -Destination $BackupDir -Recurse
    Write-Log "Backup created at: $BackupDir"
}

# Analyze documentation files
function Analyze-Documentation {
    Write-Log "Analyzing documentation files..."
    
    $allFiles = Get-ChildItem -Path $DocsDir -Recurse -File -Filter "*.md"
    $fileCount = $allFiles.Count
    
    Write-Log "Found $fileCount documentation files"
    
    # Create analysis report
    $analysis = @{
        TotalFiles = $fileCount
        FilesBySize = @{}
        FilesByContent = @{}
        DuplicateContent = @()
        Categories = @{
            "Architecture" = @()
            "Guides" = @()
            "API" = @()
            "Deployment" = @()
            "Security" = @()
            "Tutorials" = @()
            "Development" = @()
            "General" = @()
        }
    }
    
    foreach ($file in $allFiles) {
        $content = Get-Content -Path $file.FullName -Raw
        $size = $file.Length
        $hash = [System.Security.Cryptography.SHA256]::Create().ComputeHash([System.Text.Encoding]::UTF8.GetBytes($content))
        $hashString = [System.BitConverter]::ToString($hash).Replace("-", "")
        
        $analysis.FilesBySize[$file.Name] = $size
        $analysis.FilesByContent[$file.Name] = $hashString
        
        # Categorize files
        $category = "General"
        if ($file.Directory.Name -eq "architecture") { $category = "Architecture" }
        elseif ($file.Directory.Name -eq "guides") { $category = "Guides" }
        elseif ($file.Directory.Name -eq "api") { $category = "API" }
        elseif ($file.Directory.Name -eq "deployment") { $category = "Deployment" }
        elseif ($file.Directory.Name -eq "security") { $category = "Security" }
        elseif ($file.Directory.Name -eq "tutorials") { $category = "Tutorials" }
        elseif ($file.Directory.Name -eq "development") { $category = "Development" }
        
        $analysis.Categories[$category] += $file.Name
    }
    
    # Find duplicates
    $contentGroups = $analysis.FilesByContent.Values | Group-Object
    foreach ($group in $contentGroups) {
        if ($group.Count -gt 1) {
            $duplicateFiles = $analysis.FilesByContent.GetEnumerator() | Where-Object { $_.Value -eq $group.Name }
            $analysis.DuplicateContent += $duplicateFiles.Name
        }
    }
    
    Write-Log "Analysis complete. Found $($analysis.DuplicateContent.Count) duplicate files"
    return $analysis
}

# Create consolidated documentation structure
function Create-ConsolidatedDocs {
    param($Analysis)
    
    Write-Log "Creating consolidated documentation structure..."
    
    # Create new documentation structure
    $newDocsStructure = @{
        "README.md" = "Main project documentation and overview"
        "ARCHITECTURE.md" = "System architecture, database design, and technical specifications"
        "API_REFERENCE.md" = "Complete API documentation with endpoints and examples"
        "DEPLOYMENT_GUIDE.md" = "Deployment instructions, Docker setup, and production configuration"
        "DEVELOPMENT_GUIDE.md" = "Developer setup, coding standards, and contribution guidelines"
        "USER_GUIDE.md" = "User documentation, features, and tutorials"
        "SECURITY_GUIDE.md" = "Security policies, authentication, and data protection"
        "PERFORMANCE_GUIDE.md" = "Performance optimization, monitoring, and best practices"
    }
    
    # Create consolidated files
    foreach ($file in $newDocsStructure.Keys) {
        $filePath = Join-Path $DocsDir $file
        $content = "# $($newDocsStructure[$file])`n`n"
        $content += "## Overview`n`n"
        $content += "This document consolidates all related information from the original scattered documentation.`n`n"
        $content += "## Table of Contents`n`n"
        $content += "1. [Overview](#overview)`n"
        $content += "2. [Key Features](#key-features)`n"
        $content += "3. [Implementation Details](#implementation-details)`n"
        $content += "4. [Best Practices](#best-practices)`n"
        $content += "5. [Troubleshooting](#troubleshooting)`n`n"
        
        Set-Content -Path $filePath -Value $content
        Write-Log "Created consolidated file: $file"
    }
    
    return $newDocsStructure
}

# Merge content from existing files
function Merge-DocumentationContent {
    param($Analysis, $NewStructure)
    
    Write-Log "Merging content from existing files..."
    
    # Define content mapping
    $contentMapping = @{
        "README.md" = @("README.md", "project_status_*.md", "comprehensive_*.md", "implementation_*.md")
        "ARCHITECTURE.md" = @("ARCHITECTURE_*.md", "DATABASE_*.md", "PROJECT_STATUS_*.md", "comprehensive_implementation_*.md")
        "API_REFERENCE.md" = @("DATABASE_API_*.md", "API_*.md", "endpoint_*.md")
        "DEPLOYMENT_GUIDE.md" = @("deployment_*.md", "CONSOLIDATION_*.md", "Docker_*.md")
        "DEVELOPMENT_GUIDE.md" = @("DEVELOPMENT_*.md", "IMPLEMENTATION_*.md", "OPTIMIZATION_*.md")
        "USER_GUIDE.md" = @("USER_GUIDE_*.md", "FEATURES_*.md", "tutorial_*.md")
        "SECURITY_GUIDE.md" = @("security_*.md", "authentication_*.md")
        "PERFORMANCE_GUIDE.md" = @("PERFORMANCE_*.md", "optimization_*.md", "testing_*.md")
    }
    
    foreach ($consolidatedFile in $contentMapping.Keys) {
        $consolidatedPath = Join-Path $DocsDir $consolidatedFile
        $patterns = $contentMapping[$consolidatedFile]
        
        $mergedContent = Get-Content -Path $consolidatedPath -Raw
        
        foreach ($pattern in $patterns) {
            $matchingFiles = Get-ChildItem -Path $DocsDir -Recurse -File -Filter "*.md" | 
                           Where-Object { $_.Name -like $pattern }
            
            foreach ($file in $matchingFiles) {
                if ($file.Name -ne $consolidatedFile) {
                    $fileContent = Get-Content -Path $file.FullName -Raw
                    $mergedContent += "`n## Content from $($file.Name)`n`n"
                    $mergedContent += $fileContent
                    $mergedContent += "`n---`n"
                    
                    Write-Log "Merged content from $($file.Name) into $consolidatedFile"
                }
            }
        }
        
        Set-Content -Path $consolidatedPath -Value $mergedContent
        Write-Log "Completed merging content for $consolidatedFile"
    }
}

# Remove duplicate files
function Remove-DuplicateFiles {
    param($Analysis)
    
    Write-Log "Removing duplicate and obsolete files..."
    
    $filesToRemove = @()
    
    # Add duplicate files
    $filesToRemove += $Analysis.DuplicateContent
    
    # Add files that have been consolidated
    $allFiles = Get-ChildItem -Path $DocsDir -Recurse -File -Filter "*.md"
    foreach ($file in $allFiles) {
        $fileName = $file.Name
        if ($fileName -notin @("README.md", "ARCHITECTURE.md", "API_REFERENCE.md", "DEPLOYMENT_GUIDE.md", 
                              "DEVELOPMENT_GUIDE.md", "USER_GUIDE.md", "SECURITY_GUIDE.md", "PERFORMANCE_GUIDE.md")) {
            $filesToRemove += $fileName
        }
    }
    
    if ($DryRun) {
        Write-Log "DRY RUN: Would remove $($filesToRemove.Count) files"
        foreach ($file in $filesToRemove) {
            Write-Log "DRY RUN: Would remove $file"
        }
    } else {
        foreach ($file in $filesToRemove) {
            $filePath = Join-Path $DocsDir $file
            if (Test-Path $filePath) {
                Remove-Item -Path $filePath -Force
                Write-Log "Removed duplicate file: $file"
            }
        }
    }
}

# Main execution
function Main {
    Write-Log "Starting ValidoAI Documentation Consolidation"
    Write-Log "Project Root: $ProjectRoot"
    
    if ($Backup) {
        Backup-Documentation
    }
    
    $analysis = Analyze-Documentation
    $newStructure = Create-ConsolidatedDocs -Analysis $analysis
    
    if ($Execute) {
        Merge-DocumentationContent -Analysis $analysis -NewStructure $newStructure
        Remove-DuplicateFiles -Analysis $analysis
        Write-Log "Documentation consolidation completed successfully"
    } else {
        Write-Log "DRY RUN completed. Use -Execute to perform actual consolidation"
    }
    
    # Final report
    $finalFiles = Get-ChildItem -Path $DocsDir -Recurse -File -Filter "*.md"
    Write-Log "Final documentation file count: $($finalFiles.Count)"
    Write-Log "Consolidation script completed"
}

# Execute main function
Main
