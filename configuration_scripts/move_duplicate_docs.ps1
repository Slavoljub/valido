<#!
.SYNOPSIS
    deduplicate markdown docs and move canonical files into new structure.

.DESCRIPTION
    this script hashes every .md under docs/, identifies duplicates, and moves / removes
    them according to the canonical map defined in $MoveMap.  by default it runs in
    -WhatIf mode (dry-run) so no file system changes occur.  execute with -Execute to
    perform actual moves.

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File .\move_duplicate_docs.ps1            # dry run
    powershell -ExecutionPolicy Bypass -File .\move_duplicate_docs.ps1 -Execute   # move files

#>
param(
    [switch]$Execute
)

function Hash-File {
    param([string]$Path)
    if (-not (Test-Path $Path)) { return $null }
    $bytes = [System.IO.File]::ReadAllBytes($Path)
    $sha = [System.Security.Cryptography.SHA256]::Create()
    $hash = $sha.ComputeHash($bytes)
    return ([System.BitConverter]::ToString($hash) -replace "-", "").ToLower()
}

# canonical relocation map – source => destination (relative to docs/)
$MoveMap = @{
    'DEVELOPMENT_GUIDE.md' = 'guides/DEVELOPMENT_GUIDE.md'
    'optimized/README.md'  = 'README.md'
    'ARCHITECTURE.md'      = 'architecture/ARCHITECTURE_AND_DATABASE.md'
    'API_REFERENCE.md'     = 'api/API_REFERENCE.md'
    'deployment/DRY_ANALYSIS_COMPREHENSIVE.md' = 'deployment/CONSOLIDATION_SUMMARY.md'
}

$docsRoot = Join-Path $PSScriptRoot '..' | Join-Path -ChildPath 'docs'

Write-Host "📄 scanning docs directory: $docsRoot" -ForegroundColor Cyan

foreach ($src in $MoveMap.Keys) {
    $srcPath = Join-Path $docsRoot $src
    $dstPath = Join-Path $docsRoot $MoveMap[$src]

    if (-not (Test-Path $srcPath)) {
        Write-Warning "source not found: $srcPath"
        continue
    }

    # ensure destination folder exists
    $dstDir = Split-Path $dstPath -Parent
    if (-not (Test-Path $dstDir)) {
        if ($Execute) {
            New-Item -ItemType Directory -Force -Path $dstDir | Out-Null
        }
        else {
            Write-Host "would create directory: $dstDir" -ForegroundColor Yellow
        }
    }

    # compare hashes – if identical we can delete src after move
    $identical = $false
    if (Test-Path $dstPath) {
        $hashSrc = Hash-File $srcPath
        $hashDst = Hash-File $dstPath
        $identical = ($hashSrc -eq $hashDst)
    }

    if ($identical) {
        # safe to delete duplicate
        if ($Execute) {
            Remove-Item $srcPath -Force
            Write-Host "deleted duplicate: $src" -ForegroundColor Green
        }
        else {
            Write-Host "would delete duplicate: $src" -ForegroundColor Yellow
        }
    }
    else {
        # move or overwrite
        if ($Execute) {
            Move-Item $srcPath $dstPath -Force
            Write-Host "moved $src → $($MoveMap[$src])" -ForegroundColor Green
        }
        else {
            Write-Host "would move $src → $($MoveMap[$src])" -ForegroundColor Yellow
        }
    }
}

Write-Host "✅ deduplication script complete." -ForegroundColor Cyan
if (-not $Execute) {
    Write-Host "run again with -Execute to apply changes." -ForegroundColor Cyan
}
