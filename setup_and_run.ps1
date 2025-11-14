# PowerShell script to setup virtual environment, install dependencies, and start Uvicorn server

$ErrorActionPreference = "Stop" # Stop on errors for better debugging

Write-Host "================================================"
Write-Host "  Fabric Inventory System - Setup and Run Script"
Write-Host "================================================"
Write-Host ""

# --- 1. Deactivate any existing virtual environment ---
Write-Host "Deactivating any active virtual environment..."
try {
    # Check if 'deactivate' function exists, indicating an active venv
    if (Get-Command deactivate -ErrorAction SilentlyContinue) {
        deactivate
        Write-Host "Virtual environment deactivated."
    } else {
        Write-Host "No active virtual environment found."
    }
}
catch {
    Write-Warning "Could not deactivate virtual environment (might not be active): $($_.Exception.Message)"
}
Write-Host ""

# --- 2. Change directory to script location ---
Set-Location (Split-Path -Parent $MyInvocation.MyCommand.Definition)
Write-Host "Working directory set to: $(Get-Location)"
Write-Host ""

# --- 3. Remove existing 'venv' directory (to ensure a clean slate) ---
if (Test-Path -Path ".\venv" -PathType Container) {
    Write-Host "Removing existing 'venv' directory..."
    try {
        Remove-Item -Path ".\venv" -Recurse -Force
        Write-Host "'venv' directory removed successfully."
    }
    catch {
        Write-Error "Failed to remove 'venv' directory. Please check permissions or if it's in use. Error: $($_.Exception.Message)"
        Read-Host "Press Enter to exit."
        exit 1
    }
} else {
    Write-Host "No existing 'venv' directory found."
}
Write-Host ""

# --- 4. Create a new virtual environment ---
Write-Host "Creating a new virtual environment..."
try {
    python -m venv venv
    Write-Host "Virtual environment 'venv' created successfully."
}
catch {
    Write-Error "Failed to create virtual environment. Ensure Python is installed and in PATH. Error: $($_.Exception.Message)"
    Read-Host "Press Enter to exit."
    exit 1
}
Write-Host ""

# --- 5. Activate the new virtual environment ---
Write-Host "Activating the new virtual environment..."
$venvActivateScript = (Join-Path (Get-Location) "venv\Scripts\Activate.ps1")
if (Test-Path -Path $venvActivateScript) {
    . $venvActivateScript
    Write-Host "Virtual environment activated."
} else {
    Write-Error "Failed to find 'Activate.ps1' in '.\venv\Scripts'. Virtual environment might not have been created correctly."
    Read-Host "Press Enter to exit."
    exit 1
}
Write-Host ""

# --- 6. Upgrade pip inside the venv ---
Write-Host "Upgrading pip inside virtual environment..."
try {
    pip install --upgrade pip
    Write-Host "pip upgraded successfully."
}
catch {
    Write-Warning "Failed to upgrade pip (continuing anyway). Error: $($_.Exception.Message)"
}
Write-Host ""

# --- 7. Install dependencies ---
$requirementsFile = (Join-Path (Get-Location) "requirements.txt")
if (Test-Path -Path $requirementsFile -PathType Leaf) {
    Write-Host "Installing dependencies from 'requirements.txt'..."
    try {
        pip install -r $requirementsFile
        Write-Host "Dependencies installed successfully."
    }
    catch {
        Write-Error "Failed to install dependencies from 'requirements.txt'. Error: $($_.Exception.Message)"
        Read-Host "Press Enter to exit."
        exit 1
    }
} else {
    Write-Host "No 'requirements.txt' found. Installing 'uvicorn' directly..."
    try {
        pip install uvicorn
        Write-Host "'uvicorn' installed successfully."
    }
    catch {
        Write-Error "Failed to install 'uvicorn'. Error: $($_.Exception.Message)"
        Read-Host "Press Enter to exit."
        exit 1
    }
}
Write-Host ""

# --- 8. Start Uvicorn Server in a new window ---
Write-Host "Starting Uvicorn server in a new PowerShell window..."
$uvicornCommand = "uvicorn main:app --reload --host 0.0.0.0 --port 8000"
try {
    Start-Process -FilePath powershell.exe -ArgumentList "-NoExit", "-Command", $uvicornCommand -WindowStyle Normal
    Write-Host "Uvicorn server launched. Check the new PowerShell window for server output."
}
catch {
    Write-Error "Failed to launch Uvicorn server. Error: $($_.Exception.Message)"
    Read-Host "Press Enter to exit."
    exit 1
}
Write-Host ""

# --- 9. Wait for server to start and open browser ---
Write-Host "Giving the server a moment to start (3 seconds)..."
Start-Sleep -Seconds 3

Write-Host "Opening application in default web browser: http://127.0.0.1:8000"
try {
    Start-Process -FilePath "http://127.0.0.1:8000"
    Write-Host "Browser launched."
}
catch {
    Write-Warning "Failed to open web browser automatically. Please open http://127.0.0.1:8000 manually. Error: $($_.Exception.Message)"
}
Write-Host ""

Write-Host "================================================"
Write-Host "      Setup and Server Launch Completed!"
Write-Host "================================================"
Write-Host "The Uvicorn server is running in a separate window."
Write-Host "You can access your application at: http://127.0.0.1:8000"
Write-Host ""

Read-Host "Press Enter to close this launcher script."
exit 0