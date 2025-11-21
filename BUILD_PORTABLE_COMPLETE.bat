@echo off
REM ============================================================
REM FABRIC INVENTORY MANAGEMENT - PORTABLE BUILD SCRIPT
REM Enhanced Build System for Windows Portable Distribution
REM ============================================================

setlocal enabledelayedexpansion
cd /d "%~dp0"

echo.
echo ============================================================
echo  FABRIC INVENTORY PORTABLE BUILD SYSTEM
echo ============================================================
echo.

REM Color codes
for /F %%A in ('echo prompt $H ^| cmd') do set "BS=%%A"

REM Check Python installation
echo [*] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo [INFO] Please install Python 3.8+ and add to PATH
    pause
    exit /b 1
)
python --version
echo.

REM Virtual environment setup
echo [*] Setting up virtual environment...
if not exist ".venv" (
    echo [+] Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [+] Virtual environment created
) else (
    echo [+] Virtual environment already exists
)
echo.

REM Activate virtual environment
echo [*] Activating virtual environment...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)
echo [+] Virtual environment activated
echo.

REM Upgrade pip
echo [*] Upgrading pip...
python -m pip install --upgrade pip setuptools wheel >nul 2>&1
echo [+] pip upgraded
echo.

REM Install requirements
echo [*] Installing dependencies...
echo [+] Installing: fastapi, uvicorn, sqlalchemy, jinja2, reportlab, pydantic...
pip install -r requirements.txt -q
if errorlevel 1 (
    echo [ERROR] Failed to install requirements
    echo [INFO] Trying with --no-cache-dir...
    pip install -r requirements.txt --no-cache-dir
    if errorlevel 1 (
        pause
        exit /b 1
    )
)
echo [+] Dependencies installed successfully
echo.

REM Install PyInstaller
echo [*] Installing PyInstaller...
pip install pyinstaller -q
if errorlevel 1 (
    echo [ERROR] Failed to install PyInstaller
    pause
    exit /b 1
)
echo [+] PyInstaller installed
echo.

REM Clean previous builds
echo [*] Cleaning previous builds...
if exist "build" (
    echo [+] Removing old build directory...
    rmdir /s /q build >nul 2>&1
)
if exist "dist" (
    echo [+] Keeping dist folder for reference...
    REM rmdir /s /q dist >nul 2>&1
)
if exist "__pycache__" (
    rmdir /s /q __pycache__ >nul 2>&1
)
echo [+] Previous builds cleaned
echo.

REM Verify required files
echo [*] Verifying required files...
if not exist "portable_main.py" (
    echo [ERROR] portable_main.py not found
    pause
    exit /b 1
)
if not exist "main.py" (
    echo [ERROR] main.py not found
    pause
    exit /b 1
)
if not exist "templates" (
    echo [ERROR] templates folder not found
    pause
    exit /b 1
)
if not exist "static" (
    echo [ERROR] static folder not found
    pause
    exit /b 1
)
echo [+] All required files verified
echo.

REM Initialize database
echo [*] Initializing database...
python -c "import database, models; models.Base.metadata.create_all(bind=database.engine); print('Database initialized')" >nul 2>&1
if exist "fabric.db" (
    if not exist "data\fabric.db" (
        mkdir data 2>nul
        copy fabric.db data\fabric.db >nul
    )
    echo [+] Database initialized in data directory
) else (
    echo [WARNING] Could not create database
)
echo.

REM Build executable with PyInstaller
echo [*] Building portable executable...
echo [+] Compiling with PyInstaller...
call pyinstaller --name=FabricManager ^
    --onefile ^
    --windowed ^
    --icon=app_icon.ico ^
    --add-data "templates;templates" ^
    --add-data "static;static" ^
    --add-data "data;data" ^
    --hidden-import=fastapi ^
    --hidden-import=uvicorn ^
    --hidden-import=sqlalchemy ^
    --hidden-import=jinja2 ^
    --hidden-import=reportlab ^
    --hidden-import=pydantic ^
    --hidden-import=starlette ^
    --hidden-import=anyio ^
    --hidden-import=sniffio ^
    --hidden-import=h11 ^
    portable_main.py

if errorlevel 1 (
    echo [ERROR] PyInstaller build failed
    pause
    exit /b 1
)
echo [+] Executable compiled successfully
echo.

REM Copy supporting files to dist
echo [*] Setting up distribution package...
if exist "dist\FabricManager" (
    echo [+] Copying files to portable directory...
    
    REM Create necessary directories
    mkdir dist\FabricManager\data 2>nul
    mkdir dist\FabricManager\logs 2>nul
    
    REM Copy database if exists
    if exist "data\fabric.db" (
        copy data\fabric.db dist\FabricManager\data\fabric.db >nul
        echo [+] Database copied
    )
    
    REM Copy configuration files
    if exist "portable_config.py" (
        copy portable_config.py dist\FabricManager\ >nul
    )
    
    REM Copy README and documentation
    if exist "README.md" (
        copy README.md dist\FabricManager\README.md >nul
    )
    if exist "PORTABLE_BUILD_GUIDE.md" (
        copy PORTABLE_BUILD_GUIDE.md dist\FabricManager\ >nul
    )
    if exist "QUICK_START.txt" (
        copy QUICK_START.txt dist\FabricManager\ >nul
    )
    
    echo [+] Supporting files copied
)
echo.

REM Create launch scripts
echo [*] Creating launch scripts...

REM Create START_PORTABLE.bat
(
    echo @echo off
    echo title Fabric Inventory Manager
    echo cd /d "%%~dp0"
    echo start "" FabricManager.exe
    echo timeout /t 3 /nobreak
) > "dist\FabricManager\START.bat"
echo [+] START.bat created

REM Create START_PORTABLE.ps1
(
    echo # Portable launcher for PowerShell
    echo $AppPath = Split-Path -Parent $MyInvocation.MyCommand.Path
    echo $ExePath = Join-Path $AppPath "FabricManager.exe"
    echo if (Test-Path $ExePath) {
    echo     Start-Process $ExePath
    echo     Start-Sleep -Seconds 2
    echo } else {
    echo     Write-Host "Error: FabricManager.exe not found"
    echo }
) > "dist\FabricManager\START.ps1"
echo [+] START.ps1 created

echo.

REM Create portable package info
echo [*] Creating package information...
(
    echo ============================================================
    echo FABRIC INVENTORY MANAGEMENT - PORTABLE PACKAGE
    echo ============================================================
    echo.
    echo Build Date: %date% %time%
    echo Build Location: %cd%
    echo.
    echo CONTENTS:
    echo - FabricManager.exe (Main Application^)
    echo - templates/ (Web UI templates^)
    echo - static/ (CSS, JavaScript, assets^)
    echo - data/ (Database and logs^)
    echo - Documentation and guides
    echo.
    echo QUICK START:
    echo 1. Run START.bat or double-click FabricManager.exe
    echo 2. Browser opens automatically to http://127.0.0.1:8000
    echo 3. System runs on localhost only (secure^)
    echo.
    echo REQUIREMENTS:
    echo - Windows 7 or later
    echo - No Python installation required
    echo - ~200 MB disk space for application
    echo.
    echo FEATURES:
    echo - Fabric inventory management
    echo - Purchase and sales tracking
    echo - Bank statement reconciliation
    echo - Financial reports
    echo - Stock valuation
    echo - Payment tracking
    echo - Ledger system
    echo.
    echo TROUBLESHOOTING:
    echo - If port 8000 is in use, edit portable_config.py
    echo - Database files stored in data/ directory
    echo - Logs stored in data/ directory
    echo - Delete fabric.db to reset database
    echo.
    echo VERSION: 1.0.0
    echo ============================================================
) > "dist\FabricManager\PACKAGE_INFO.txt"
echo [+] Package info created

echo.

REM Build complete summary
echo ============================================================
echo  BUILD COMPLETE - PORTABLE EXECUTABLE READY
echo ============================================================
echo.
echo [SUCCESS] Portable build completed successfully!
echo.
echo OUTPUT LOCATION: dist\FabricManager\
echo EXECUTABLE: dist\FabricManager\FabricManager.exe
echo.
echo NEXT STEPS:
echo 1. Navigate to: dist\FabricManager\
echo 2. Double-click: START.bat or FabricManager.exe
echo 3. Browser opens automatically
echo 4. Access: http://127.0.0.1:8000
echo.
echo PACKAGE SIZE: Check dist\FabricManager\ folder
echo PACKAGE CONTENTS:
echo   - FabricManager.exe (executable^)
echo   - templates\ (UI files^)
echo   - static\ (assets^)
echo   - data\ (database^)
echo   - Documentation files
echo.
echo DISTRIBUTION:
echo To share this application:
echo 1. Zip the entire dist\FabricManager\ folder
echo 2. Send to users
echo 3. Users extract and run START.bat
echo.
echo For portable build guide, see PORTABLE_BUILD_GUIDE.md
echo.
echo ============================================================
echo.

REM Deactivate venv (optional)
call deactivate 2>nul

pause
