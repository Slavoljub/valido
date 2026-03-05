#!/usr/bin/env powershell
<#
.SYNOPSIS
    Setup SSL environment variables for ValidoAI localhost certificates
    
.DESCRIPTION
    This script sets up the environment variables needed for ValidoAI to use
    the localhost SSL certificates located in the /certs directory.
    
.PARAMETER CertPath
    Path to the certificate file (default: certs/localhost-cert.crt)
    
.PARAMETER KeyPath
    Path to the private key file (default: certs/localhost-key.pem)
    
.EXAMPLE
    .\setup_ssl_localhost.ps1
    
.EXAMPLE
    .\setup_ssl_localhost.ps1 -CertPath "certs\my-cert.crt" -KeyPath "certs\my-key.pem"
#>

param(
    [string]$CertPath = "certs\localhost-cert.crt",
    [string]$KeyPath = "certs\localhost-key.pem"
)

Write-Host "🔐 Setting up SSL environment variables for ValidoAI..." -ForegroundColor Green
Write-Host "=" * 60

# Check if certificate files exist
$certExists = Test-Path $CertPath
$keyExists = Test-Path $KeyPath

if (-not $certExists) {
    Write-Host "❌ Certificate file not found: $CertPath" -ForegroundColor Red
    Write-Host "   Available certificate files:" -ForegroundColor Yellow
    Get-ChildItem -Path "certs" -Filter "localhost-*" | ForEach-Object {
        Write-Host "   - $($_.Name)" -ForegroundColor Cyan
    }
    exit 1
}

if (-not $keyExists) {
    Write-Host "❌ Private key file not found: $KeyPath" -ForegroundColor Red
    Write-Host "   Available key files:" -ForegroundColor Yellow
    Get-ChildItem -Path "certs" -Filter "localhost-*" | ForEach-Object {
        Write-Host "   - $($_.Name)" -ForegroundColor Cyan
    }
    exit 1
}

# Set environment variables
$env:SSL_CERT_FILE = $CertPath
$env:SSL_KEY_FILE = $KeyPath
$env:USE_HTTPS = "true"
$env:USE_ASGI = "true"
$env:HTTPS_PORT = "5001"

Write-Host "✅ SSL environment variables set:" -ForegroundColor Green
Write-Host "   SSL_CERT_FILE: $env:SSL_CERT_FILE" -ForegroundColor Cyan
Write-Host "   SSL_KEY_FILE: $env:SSL_KEY_FILE" -ForegroundColor Cyan
Write-Host "   USE_HTTPS: $env:USE_HTTPS" -ForegroundColor Cyan
Write-Host "   USE_ASGI: $env:USE_ASGI" -ForegroundColor Cyan
Write-Host "   HTTPS_PORT: $env:HTTPS_PORT" -ForegroundColor Cyan

Write-Host ""
Write-Host "🚀 To start the server with HTTPS, run:" -ForegroundColor Yellow
Write-Host "   python app.py" -ForegroundColor White
Write-Host ""
Write-Host "📍 The server will be available at:" -ForegroundColor Yellow
Write-Host "   HTTP:  http://localhost:5000" -ForegroundColor White
Write-Host "   HTTPS: https://localhost:5001" -ForegroundColor White
Write-Host ""
Write-Host "⚠️  Note: You may need to trust the certificate in your browser" -ForegroundColor Yellow
Write-Host "   or add it to your system's trusted certificate store." -ForegroundColor Yellow
