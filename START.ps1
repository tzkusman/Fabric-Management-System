# ============================================================================
# FABRIC INVENTORY MANAGEMENT SYSTEM - LAUNCHER
# Starts the application and opens browser automatically
# ============================================================================

`$appRoot = Split-Path -Parent `$PSCommandPath

# Activate virtual environment
`$venvActivate = Join-Path `$appRoot ".venv\Scripts\Activate.ps1"

if (Test-Path `$venvActivate) {
    & `$venvActivate
} else {
    Write-Host "Virtual environment not found. Please run INSTALL.bat first." -ForegroundColor Red
    exit 1
}

# Set working directory
Set-Location `$appRoot

# Start the application
Write-Host "Starting Fabric Inventory Management System..." -ForegroundColor Green
Write-Host "Opening browser at http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host ""

# Open browser in background
Start-Process "http://127.0.0.1:8000" -ErrorAction SilentlyContinue

# Start server
python main.py
