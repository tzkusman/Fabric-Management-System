@echo off
REM ============================================
REM Fabric Management System - START Script
REM Runs on any computer with Python installed
REM ============================================

setlocal enabledelayedexpansion

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0
cd /d %SCRIPT_DIR%

echo.
echo ============================================
echo   Fabric Management System
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo.
    echo To fix this:
    echo 1. Download Python from https://www.python.org/downloads/
    echo 2. During installation, CHECK "Add Python to PATH"
    echo 3. Then run this script again
    echo.
    pause
    exit /b 1
)

echo [OK] Python found
python --version

REM Check if required files exist
echo.
echo [CHECK] Verifying file structure...

if not exist "main.py" (
    echo [ERROR] main.py not found in %SCRIPT_DIR%
    pause
    exit /b 1
)
if not exist "models.py" (
    echo [ERROR] models.py not found
    pause
    exit /b 1
)
if not exist "database.py" (
    echo [ERROR] database.py not found
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

echo [OK] All required files found

REM Check if venv exists, if not create it
echo.
echo [CHECK] Checking Python environment...

if not exist "venv" (
    echo [INFO] Creating Python virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created
)

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)

REM Install dependencies silently
echo [INFO] Checking Python packages...
if exist "requirements.txt" (
    pip install -q -r requirements.txt >nul 2>&1
    if errorlevel 1 (
        echo [WARN] Some packages could not be installed automatically
        echo Installing with verbose output...
        pip install -r requirements.txt
    )
)

REM Create data directory if it doesn't exist
if not exist "data" (
    mkdir data
    echo [OK] Data directory created
)

REM Start the application
echo.
echo ============================================
echo [INFO] Starting application...
echo ============================================
echo.
echo Browser will open automatically...
echo If not, go to: http://127.0.0.1:8000
echo.
echo Press CTRL+C to stop the server
echo.

REM Run the application
python main.py

REM If we get here, the app crashed
echo.
echo [ERROR] Application exited unexpectedly
echo.
pause
