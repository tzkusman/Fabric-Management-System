# ============================================================================
# FABRIC INVENTORY MANAGEMENT SYSTEM - ONE-CLICK INSTALLER
# Installs Python, dependencies, and sets up the complete application
# ============================================================================

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

# Colors for output
$Colors = @{
    Success = "Green"
    Error = "Red"
    Warning = "Yellow"
    Info = "Cyan"
    Header = "Magenta"
}

function Write-Header {
    param([string]$Text)
    Write-Host ""
    Write-Host ("=" * 70) -ForegroundColor $Colors.Header
    Write-Host $Text -ForegroundColor $Colors.Header
    Write-Host ("=" * 70) -ForegroundColor $Colors.Header
}

function Write-Success {
    param([string]$Text)
    Write-Host "✓ $Text" -ForegroundColor $Colors.Success
}

function Write-Error-Custom {
    param([string]$Text)
    Write-Host "✗ $Text" -ForegroundColor $Colors.Error
}

function Write-Warning-Custom {
    param([string]$Text)
    Write-Host "⚠ $Text" -ForegroundColor $Colors.Warning
}

function Write-Info {
    param([string]$Text)
    Write-Host "ℹ $Text" -ForegroundColor $Colors.Info
}

# Check if running as admin
function Check-Admin {
    $isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    if (-not $isAdmin) {
        Write-Error-Custom "This script requires Administrator privileges!"
        Write-Info "Right-click INSTALL.ps1 and select 'Run as administrator'"
        exit 1
    }
    Write-Success "Running with administrator privileges"
}

# Check if Python is installed
function Check-Python {
    Write-Header "Checking Python Installation"
    
    $python = Get-Command python -ErrorAction SilentlyContinue
    if ($python) {
        $version = python --version 2>&1
        Write-Success "Python found: $version"
        return $true
    }
    return $false
}

# Download and install Python
function Install-Python {
    Write-Header "Installing Python 3.11"
    
    $pythonUrl = "https://www.python.org/ftp/python/3.11.7/python-3.11.7-amd64.exe"
    $installerPath = "$env:TEMP\python-installer.exe"
    
    Write-Info "Downloading Python 3.11.7..."
    try {
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        (New-Object System.Net.WebClient).DownloadFile($pythonUrl, $installerPath)
        Write-Success "Python installer downloaded"
    }
    catch {
        Write-Error-Custom "Failed to download Python: $_"
        exit 1
    }
    
    Write-Info "Running Python installer..."
    $installArgs = "/quiet InstallAllUsers=1 PrependPath=1 Include_test=0 Include_tcltk=0"
    Start-Process $installerPath -ArgumentList $installArgs -Wait
    
    # Refresh PATH
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
    
    if (Get-Command python -ErrorAction SilentlyContinue) {
        Write-Success "Python installed successfully"
        Remove-Item $installerPath -Force
        return $true
    }
    else {
        Write-Error-Custom "Python installation failed"
        return $false
    }
}

# Create virtual environment
function Setup-VirtualEnv {
    param([string]$AppPath)
    
    Write-Header "Setting up Python Virtual Environment"
    
    $venvPath = Join-Path $AppPath ".venv"
    
    if (Test-Path $venvPath) {
        Write-Info "Virtual environment already exists"
        return $venvPath
    }
    
    Write-Info "Creating virtual environment..."
    python -m venv $venvPath
    
    if (Test-Path $venvPath) {
        Write-Success "Virtual environment created"
        return $venvPath
    }
    else {
        Write-Error-Custom "Failed to create virtual environment"
        exit 1
    }
}

# Install requirements
function Install-Requirements {
    param([string]$VenvPath, [string]$AppPath)
    
    Write-Header "Installing Python Dependencies"
    
    $requirementsPath = Join-Path $AppPath "requirements.txt"
    
    if (-not (Test-Path $requirementsPath)) {
        Write-Warning-Custom "requirements.txt not found at $requirementsPath"
        return $false
    }
    
    $activateScript = Join-Path $VenvPath "Scripts\Activate.ps1"
    
    # Activate venv and install requirements
    Write-Info "Installing packages from requirements.txt..."
    & $activateScript
    python -m pip install --upgrade pip
    pip install -r $requirementsPath
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "All dependencies installed successfully"
        return $true
    }
    else {
        Write-Error-Custom "Failed to install dependencies"
        return $false
    }
}

# Create data directories
function Setup-Directories {
    param([string]$AppPath)
    
    Write-Header "Setting up Application Directories"
    
    $dirs = @(
        (Join-Path $AppPath "data"),
        (Join-Path $AppPath "templates"),
        (Join-Path $AppPath "static"),
        (Join-Path $AppPath "scripts")
    )
    
    foreach ($dir in $dirs) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
            Write-Success "Created directory: $(Split-Path $dir -Leaf)"
        }
    }
}

# Create Windows shortcut
function Create-Shortcut {
    param([string]$AppPath)
    
    Write-Header "Creating Desktop Shortcut"
    
    $desktopPath = [Environment]::GetFolderPath("Desktop")
    $shortcutPath = Join-Path $desktopPath "Fabric Manager.lnk"
    $startBatPath = Join-Path $AppPath "START.bat"
    
    if (-not (Test-Path $startBatPath)) {
        Write-Warning-Custom "START.bat not found, skipping shortcut creation"
        return
    }
    
    $WshShell = New-Object -ComObject WScript.Shell
    $shortcut = $WshShell.CreateShortcut($shortcutPath)
    $shortcut.TargetPath = $startBatPath
    $shortcut.WorkingDirectory = $AppPath
    $shortcut.IconLocation = "C:\Windows\System32\cmd.exe"
    $shortcut.Save()
    
    Write-Success "Desktop shortcut created: Fabric Manager"
}

# Create START.ps1 for easy launching with auto-browser
function Create-StartScript {
    param([string]$AppPath)
    
    Write-Header "Creating Startup Script"
    
    $startScriptPath = Join-Path $AppPath "START.ps1"
    
    $scriptContent = @'
# ============================================================================
# FABRIC INVENTORY MANAGEMENT SYSTEM - LAUNCHER
# Starts the application and opens browser automatically
# ============================================================================

$appRoot = Split-Path -Parent $PSCommandPath

# Activate virtual environment
$venvActivate = Join-Path $appRoot ".venv\Scripts\Activate.ps1"

if (Test-Path $venvActivate) {
    & $venvActivate
} else {
    Write-Host "Virtual environment not found. Please run INSTALL.bat first." -ForegroundColor Red
    exit 1
}

# Set working directory
Set-Location $appRoot

# Start the application
Write-Host "Starting Fabric Inventory Management System..." -ForegroundColor Green
Write-Host "Opening browser at http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host ""

# Open browser in background
Start-Process "http://127.0.0.1:8000" -ErrorAction SilentlyContinue

# Start server
python main.py
'@
    
    $scriptContent | Set-Content -Path $startScriptPath -Encoding UTF8
    Write-Success "START.ps1 created"
}

# Final verification
function Verify-Installation {
    param([string]$AppPath)
    
    Write-Header "Verifying Installation"
    
    $requiredFiles = @(
        "main.py",
        "crud.py",
        "models.py",
        "database.py",
        "requirements.txt",
        "START.bat",
        "START.ps1"
    )
    
    $allFound = $true
    foreach ($file in $requiredFiles) {
        $filePath = Join-Path $AppPath $file
        if (Test-Path $filePath) {
            Write-Success "Found: $file"
        }
        else {
            Write-Error-Custom "Missing: $file"
            $allFound = $false
        }
    }
    
    return $allFound
}

# Main installation flow
function Main {
    Clear-Host
    Write-Host ""
    Write-Header "FABRIC INVENTORY MANAGEMENT SYSTEM INSTALLER"
    
    # Get application path
    $appPath = Split-Path -Parent $PSCommandPath
    Write-Info "Installation path: $appPath"
    
    # Check admin privileges
    Check-Admin
    
    # Check and install Python
    if (-not (Check-Python)) {
        Write-Warning-Custom "Python not found, attempting to install..."
        if (-not (Install-Python)) {
            exit 1
        }
    }
    
    # Setup virtual environment
    $venvPath = Setup-VirtualEnv -AppPath $appPath
    
    # Install requirements
    if (-not (Install-Requirements -VenvPath $venvPath -AppPath $appPath)) {
        exit 1
    }
    
    # Setup directories
    Setup-Directories -AppPath $appPath
    
    # Create startup script
    Create-StartScript -AppPath $appPath
    
    # Create shortcut
    Create-Shortcut -AppPath $appPath
    
    # Verify installation
    if (-not (Verify-Installation -AppPath $appPath)) {
        Write-Warning-Custom "Some files are missing, but installation completed"
    }
    
    # Success message
    Write-Header "INSTALLATION COMPLETE!"
    Write-Host ""
    Write-Host "You can now:" -ForegroundColor $Colors.Success
    Write-Host "  1. Double-click START.ps1 (auto-opens browser)" -ForegroundColor $Colors.Success
    Write-Host "  2. Or double-click START.bat to run manually" -ForegroundColor $Colors.Success
    Write-Host "  3. Or use the 'Fabric Manager' shortcut on your desktop" -ForegroundColor $Colors.Success
    Write-Host "  4. The application will open at http://127.0.0.1:8000" -ForegroundColor $Colors.Success
    Write-Host ""
    Write-Host "Features available:" -ForegroundColor $Colors.Info
    Write-Host "  • Company & Supplier Management" -ForegroundColor $Colors.Info
    Write-Host "  • Purchase & Sales Tracking" -ForegroundColor $Colors.Info
    Write-Host "  • Stock Management" -ForegroundColor $Colors.Info
    Write-Host "  • Bank Statement Reconciliation" -ForegroundColor $Colors.Info
    Write-Host "  • Ledger & Reports" -ForegroundColor $Colors.Info
    Write-Host "  • Payment Tracking" -ForegroundColor $Colors.Info
    Write-Host ""
    
    Read-Host "Press Enter to exit"
}

# Run installer
Main
