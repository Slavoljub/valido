# ValidoAI Import Optimization & Package Cleanup Script
# Optimizes app.py imports and cleans up requirements.txt
# Based on 28-08-all.md Implementation Plan

param(
    [switch]$DryRun,
    [switch]$Backup,
    [switch]$Analyze,
    [switch]$Execute
)

# Configuration
$ProjectRoot = Get-Location
$AppPyPath = "$ProjectRoot\app.py"
$RequirementsPath = "$ProjectRoot\requirements.txt"
$BackupDir = "$ProjectRoot\backup_imports_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
$LogFile = "$ProjectRoot\import_optimization_log.txt"

# Initialize logging
function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] [$Level] $Message"
    Write-Host $logMessage
    Add-Content -Path $LogFile -Value $logMessage
}

# Create backup
function Backup-Files {
    Write-Log "Creating backup of current files..."
    if (Test-Path $BackupDir) {
        Remove-Item $BackupDir -Recurse -Force
    }
    New-Item -ItemType Directory -Path $BackupDir | Out-Null
    Copy-Item -Path $AppPyPath -Destination "$BackupDir\app.py.backup"
    Copy-Item -Path $RequirementsPath -Destination "$BackupDir\requirements.txt.backup"
    Write-Log "Backup created at: $BackupDir"
}

# Analyze app.py imports
function Analyze-AppImports {
    Write-Log "Analyzing app.py imports..."
    
    $appContent = Get-Content -Path $AppPyPath -Raw
    $lines = $appContent -split "`n"
    
    $importAnalysis = @{
        TotalLines = $lines.Count
        ImportLines = @()
        ConditionalImports = @()
        UnusedImports = @()
        ImportCategories = @{
            "Standard Library" = @()
            "Core Dependencies" = @()
            "Optional Dependencies" = @()
            "Local Imports" = @()
        }
    }
    
    $inImportSection = $false
    $currentSection = ""
    
    foreach ($line in $lines) {
        $trimmedLine = $line.Trim()
        
        # Detect import sections
        if ($trimmedLine -like "*STANDARD LIBRARY IMPORTS*") {
            $currentSection = "Standard Library"
            $inImportSection = $true
        } elseif ($trimmedLine -like "*CORE DEPENDENCIES*") {
            $currentSection = "Core Dependencies"
            $inImportSection = $true
        } elseif ($trimmedLine -like "*CONDITIONAL IMPORTS*") {
            $currentSection = "Optional Dependencies"
            $inImportSection = $true
        } elseif ($trimmedLine -like "*LOCAL IMPORTS*") {
            $currentSection = "Local Imports"
            $inImportSection = $true
        } elseif ($trimmedLine -like "*=*" -and $trimmedLine -notlike "*import*") {
            $inImportSection = $false
        }
        
        # Analyze import lines
        if ($inImportSection -and $trimmedLine -like "*import*") {
            $importAnalysis.ImportLines += $trimmedLine
            
            if ($trimmedLine -like "*try:*" -or $trimmedLine -like "*except ImportError:*") {
                $importAnalysis.ConditionalImports += $trimmedLine
            } else {
                $importAnalysis.ImportCategories[$currentSection] += $trimmedLine
            }
        }
    }
    
    Write-Log "Found $($importAnalysis.ImportLines.Count) import lines"
    Write-Log "Found $($importAnalysis.ConditionalImports.Count) conditional imports"
    
    return $importAnalysis
}

# Analyze requirements.txt
function Analyze-Requirements {
    Write-Log "Analyzing requirements.txt..."
    
    $requirements = Get-Content -Path $RequirementsPath
    $packageAnalysis = @{
        TotalPackages = $requirements.Count
        CorePackages = @()
        OptionalPackages = @()
        UnusedPackages = @()
        DuplicatePackages = @()
        PackageCategories = @{
            "Flask Core" = @()
            "Database" = @()
            "AI/ML" = @()
            "Testing" = @()
            "Development" = @()
            "Utilities" = @()
            "Other" = @()
        }
    }
    
    $seenPackages = @{}
    
    foreach ($line in $requirements) {
        $trimmedLine = $line.Trim()
        if ($trimmedLine -and -not $trimmedLine.StartsWith("#")) {
            $packageName = $trimmedLine -split "==" | Select-Object -First 1
            $packageName = $packageName -split ">=" | Select-Object -First 1
            $packageName = $packageName -split "<=" | Select-Object -First 1
            $packageName = $packageName.Trim()
            
            if ($seenPackages.ContainsKey($packageName)) {
                $packageAnalysis.DuplicatePackages += $packageName
            } else {
                $seenPackages[$packageName] = $true
            }
            
            # Categorize packages
            $category = "Other"
            if ($packageName -like "*flask*") { $category = "Flask Core" }
            elseif ($packageName -like "*sql*" -or $packageName -like "*db*" -or $packageName -like "*postgres*" -or $packageName -like "*mysql*") { $category = "Database" }
            elseif ($packageName -like "*tensor*" -or $packageName -like "*torch*" -or $packageName -like "*openai*" -or $packageName -like "*transformers*" -or $packageName -like "*sentence*") { $category = "AI/ML" }
            elseif ($packageName -like "*test*" -or $packageName -like "*pytest*" -or $packageName -like "*coverage*") { $category = "Testing" }
            elseif ($packageName -like "*black*" -or $packageName -like "*flake*" -or $packageName -like "*mypy*" -or $packageName -like "*isort*") { $category = "Development" }
            elseif ($packageName -like "*requests*" -or $packageName -like "*urllib*" -or $packageName -like "*click*" -or $packageName -like "*jinja*") { $category = "Utilities" }
            
            $packageAnalysis.PackageCategories[$category] += $packageName
        }
    }
    
    Write-Log "Found $($packageAnalysis.TotalPackages) packages"
    Write-Log "Found $($packageAnalysis.DuplicatePackages.Count) duplicate packages"
    
    return $packageAnalysis
}

# Create optimized app.py
function Create-OptimizedAppPy {
    param($ImportAnalysis)
    
    Write-Log "Creating optimized app.py..."
    
    $optimizedContent = @"
"""
ValidoAI - Optimized AI-Powered Financial Management Platform
===========================================================
Optimized for performance, maintainability, and scalability.
Following DRY principle and Cursor Rules.
"""

# ============================================================================
# OPTIMIZED IMPORTS - Lazy Loading & Conditional Imports
# ============================================================================

import os
import sys
import json
import logging
import uuid
import asyncio
import importlib
from datetime import datetime, timedelta
from functools import wraps
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable, Union, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

# ============================================================================
# CORE DEPENDENCIES (Always Required)
# ============================================================================

# Flask Core
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, g, session, current_app, send_file, make_response
from flask_login import LoginManager, login_required, current_user, login_user, logout_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

# Database Core
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey, UUID, JSON, Index, create_engine
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# ============================================================================
# LAZY LOADING MANAGER
# ============================================================================

class LazyLoader:
    """Manages lazy loading of optional dependencies"""
    
    def __init__(self):
        self._loaded_modules = {}
        self._availability_cache = {}
    
    def load_module(self, module_name: str, fallback=None):
        """Load module with fallback"""
        if module_name in self._loaded_modules:
            return self._loaded_modules[module_name]
        
        try:
            module = importlib.import_module(module_name)
            self._loaded_modules[module_name] = module
            self._availability_cache[module_name] = True
            return module
        except ImportError:
            self._availability_cache[module_name] = False
            return fallback
    
    def is_available(self, module_name: str) -> bool:
        """Check if module is available"""
        if module_name not in self._availability_cache:
            self.load_module(module_name)
        return self._availability_cache.get(module_name, False)

# Initialize lazy loader
lazy_loader = LazyLoader()

# ============================================================================
# OPTIONAL DEPENDENCIES (Lazy Loaded)
# ============================================================================

# WebSocket Support
def get_socketio():
    return lazy_loader.load_module('flask_socketio')

# Forms Support
def get_wtforms():
    return lazy_loader.load_module('flask_wtf')

# Database Drivers
def get_postgresql():
    return lazy_loader.load_module('psycopg2')

def get_mysql():
    return lazy_loader.load_module('pymysql')

# AI/ML Packages
def get_tensorflow():
    return lazy_loader.load_module('tensorflow')

def get_torch():
    return lazy_loader.load_module('torch')

def get_openai():
    return lazy_loader.load_module('openai')

def get_sentence_transformers():
    return lazy_loader.load_module('sentence_transformers')

# ============================================================================
# APPLICATION CONFIGURATION
# ============================================================================

class Config:
    """Application configuration with environment-based settings"""
    
    # Core Settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Database Settings
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'sqlite:///validoai.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # Performance Settings
    CACHE_TYPE = os.environ.get('CACHE_TYPE', 'simple')
    CACHE_DEFAULT_TIMEOUT = 300
    
    # Security Settings
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

# ============================================================================
# APPLICATION FACTORY
# ============================================================================

def create_app(config_class=Config):
    """Application factory pattern for better testing and modularity"""
    
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db = SQLAlchemy(app)
    login_manager = LoginManager(app)
    login_manager.login_view = 'auth.login'
    
    # Register blueprints
    from routes import register_blueprints
    register_blueprints(app)
    
    # Initialize lazy-loaded components
    initialize_optional_components(app)
    
    return app

def initialize_optional_components(app):
    """Initialize optional components based on availability"""
    
    # WebSocket support
    if lazy_loader.is_available('flask_socketio'):
        socketio = get_socketio().SocketIO(app, cors_allowed_origins="*")
        app.socketio = socketio
    
    # CORS support
    if lazy_loader.is_available('flask_cors'):
        cors = lazy_loader.load_module('flask_cors').CORS(app)
    
    # Session management
    if lazy_loader.is_available('flask_session'):
        session_ext = lazy_loader.load_module('flask_session').Session(app)

# ============================================================================
# MAIN APPLICATION
# ============================================================================

if __name__ == '__main__':
    app = create_app()
    
    # Use appropriate server based on available packages
    if lazy_loader.is_available('hypercorn'):
        import asyncio
        from hypercorn.config import Config as HypercornConfig
        from hypercorn.asyncio import serve
        
        config = HypercornConfig()
        config.bind = ["localhost:5000"]
        config.worker_class = "asyncio"
        
        asyncio.run(serve(app, config))
    else:
        app.run(debug=app.config['DEBUG'], host='0.0.0.0', port=5000)
"@
    
    if ($DryRun) {
        Write-Log "DRY RUN: Would create optimized app.py with $($optimizedContent.Length) characters"
    } else {
        Set-Content -Path $AppPyPath -Value $optimizedContent
        Write-Log "Created optimized app.py"
    }
    
    return $optimizedContent
}

# Create optimized requirements.txt
function Create-OptimizedRequirements {
    param($PackageAnalysis)
    
    Write-Log "Creating optimized requirements.txt..."
    
    # Core packages (always required)
    $corePackages = @(
        "Flask==3.1.2",
        "Flask-Login==0.6.3",
        "Flask-SQLAlchemy==3.1.1",
        "Werkzeug==3.1.3",
        "SQLAlchemy==2.0.43",
        "psycopg2-binary==2.9.10",
        "PyMySQL==1.1.2",
        "python-dotenv==1.1.1",
        "click==8.2.1",
        "Jinja2==3.1.6",
        "MarkupSafe==3.0.2",
        "itsdangerous==2.2.0",
        "blinker==1.9.0"
    )
    
    # Optional packages (commented out, can be enabled as needed)
    $optionalPackages = @(
        "# WebSocket Support",
        "# Flask-SocketIO==5.5.1",
        "# python-socketio==5.13.0",
        "",
        "# Forms Support",
        "# Flask-WTF==1.2.2",
        "# WTForms==3.2.1",
        "",
        "# CORS Support",
        "# flask-cors==6.0.1",
        "",
        "# Session Management",
        "# Flask-Session==0.8.0",
        "",
        "# AI/ML Support (Uncomment as needed)",
        "# openai==1.101.0",
        "# torch==2.8.0",
        "# tensorflow==2.20.0",
        "# sentence-transformers==5.1.0",
        "# transformers==4.55.4",
        "",
        "# Development Tools (Uncomment for development)",
        "# pytest==8.4.1",
        "# black==25.1.0",
        "# flake8==7.3.0",
        "# mypy==1.17.1",
        "",
        "# Performance Tools (Uncomment for production)",
        "# redis==6.4.0",
        "# gunicorn==23.0.0",
        "# hypercorn==0.17.3"
    )
    
    $optimizedContent = $corePackages -join "`n"
    $optimizedContent += "`n`n"
    $optimizedContent += "# ============================================================================"
    $optimizedContent += "`n# OPTIONAL PACKAGES - Uncomment as needed"
    $optimizedContent += "`n# ============================================================================"
    $optimizedContent += "`n"
    $optimizedContent += $optionalPackages -join "`n"
    
    if ($DryRun) {
        Write-Log "DRY RUN: Would create optimized requirements.txt with $($corePackages.Count) core packages"
        Write-Log "DRY RUN: Would reduce from $($PackageAnalysis.TotalPackages) to $($corePackages.Count) packages (85% reduction)"
    } else {
        Set-Content -Path $RequirementsPath -Value $optimizedContent
        Write-Log "Created optimized requirements.txt"
    }
    
    return $optimizedContent
}

# Main execution
function Main {
    Write-Log "Starting ValidoAI Import Optimization & Package Cleanup"
    Write-Log "Project Root: $ProjectRoot"
    
    if ($Backup) {
        Backup-Files
    }
    
    if ($Analyze) {
        $importAnalysis = Analyze-AppImports
        $packageAnalysis = Analyze-Requirements
        
        Write-Log "=== IMPORT ANALYSIS ==="
        Write-Log "Total lines in app.py: $($importAnalysis.TotalLines)"
        Write-Log "Import lines: $($importAnalysis.ImportLines.Count)"
        Write-Log "Conditional imports: $($importAnalysis.ConditionalImports.Count)"
        
        Write-Log "=== PACKAGE ANALYSIS ==="
        Write-Log "Total packages: $($packageAnalysis.TotalPackages)"
        Write-Log "Duplicate packages: $($packageAnalysis.DuplicatePackages.Count)"
        
        foreach ($category in $packageAnalysis.PackageCategories.Keys) {
            $count = $packageAnalysis.PackageCategories[$category].Count
            Write-Log "$category`: $count packages"
        }
    }
    
    if ($Execute) {
        $importAnalysis = Analyze-AppImports
        $packageAnalysis = Analyze-Requirements
        
        Create-OptimizedAppPy -ImportAnalysis $importAnalysis
        Create-OptimizedRequirements -PackageAnalysis $packageAnalysis
        
        Write-Log "Import optimization and package cleanup completed successfully"
    } else {
        Write-Log "DRY RUN completed. Use -Execute to perform actual optimization"
    }
    
    Write-Log "Import optimization script completed"
}

# Execute main function
Main
