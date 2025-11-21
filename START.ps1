# Portable Fabric Inventory Manager - PowerShell Launcher
# Run: .\START.ps1

$ErrorActionPreference = "Continue"

# Get app directory
$appDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $appDir

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "   FABRIC INVENTORY MANAGEMENT SYSTEM - PORTABLE" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "Checking Python installation..." -ForegroundColor Yellow
$pythonCheck = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host ""
    Write-Host "For this version, install Python 3.9+ from python.org" -ForegroundColor Yellow
    Write-Host "Or use the pre-packaged .exe version (no Python needed)" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to close"
    exit 1
}
Write-Host "Python found: $pythonCheck" -ForegroundColor Green

# Check dependencies
Write-Host "Checking dependencies..." -ForegroundColor Yellow
$depsCheck = python -c "import fastapi, uvicorn, sqlalchemy" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Installing required packages (first run only)..." -ForegroundColor Yellow
    Write-Host ""
    pip install -q -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to install dependencies" -ForegroundColor Red
        Read-Host "Press Enter to close"
        exit 1
    }
}
Write-Host "All dependencies ready" -ForegroundColor Green

# Create data directory
if (-not (Test-Path "data")) {
    New-Item -ItemType Directory -Path "data" -Force | Out-Null
}

Write-Host ""
Write-Host "Starting server..." -ForegroundColor Yellow
Write-Host "Browser will open automatically in a few seconds..." -ForegroundColor Yellow
Write-Host ""
Write-Host "NOTE: Keep this window open while using the application" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Cyan
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Run the server
try {
    python portable_main.py
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
    Read-Host "Press Enter to close"
    exit 1
}
