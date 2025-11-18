@echo off
REM ============================================
REM Build Portable Package for Distribution
REM Creates a self-contained folder ready to run
REM on any Windows computer with Python
REM ============================================

setlocal enabledelayedexpansion

echo.
echo ============================================
echo   Building Portable Package
echo ============================================
echo.

REM Get current directory
set BUILD_DIR=%cd%
set DIST_FOLDER=%BUILD_DIR%\dist\fabric-manager

echo [INFO] Creating distribution folder...
if exist "%DIST_FOLDER%" (
    echo [WARN] Folder already exists, cleaning...
    rmdir /s /q "%DIST_FOLDER%"
)

mkdir "%DIST_FOLDER%"
cd /d "%DIST_FOLDER%"

echo [OK] Distribution folder created: %DIST_FOLDER%

echo.
echo [INFO] Copying core files...

REM Copy Python source files
copy "%BUILD_DIR%\main.py" .
copy "%BUILD_DIR%\models.py" .
copy "%BUILD_DIR%\crud.py" .
copy "%BUILD_DIR%\database.py" .
copy "%BUILD_DIR%\schemas.py" .
copy "%BUILD_DIR%\requirements.txt" .

echo [OK] Core files copied

echo.
echo [INFO] Copying folders...

REM Copy folder structure
xcopy "%BUILD_DIR%\templates" templates /E /I /Q
xcopy "%BUILD_DIR%\static" static /E /I /Q
xcopy "%BUILD_DIR%\scripts" scripts /E /I /Q

echo [OK] Folders copied

echo.
echo [INFO] Copying startup scripts...

REM Copy startup scripts
copy "%BUILD_DIR%\START.bat" .
copy "%BUILD_DIR%\README.md" .

echo [OK] Startup scripts copied

echo.
echo [INFO] Creating data directory...
mkdir data

echo.
echo [INFO] Creating deployment guide...

REM Create a quick start file
(
    echo Fabric Management System - Quick Start
    echo.
    echo To run this application:
    echo.
    echo 1. Make sure Python 3.9+ is installed
    echo 2. Double-click START.bat
    echo 3. Browser opens to http://127.0.0.1:8000
    echo.
    echo First run may take 20-30 seconds to install dependencies.
    echo.
    echo For help, read README.md or DEPLOY_TO_OTHER_COMPUTER.md
) > QUICK_START.txt

echo [OK] Quick start guide created

echo.
echo ============================================
echo   Package Created Successfully!
echo ============================================
echo.
echo Location: %DIST_FOLDER%
echo.
echo Next steps:
echo 1. Copy this entire folder to another computer
echo 2. On that computer, double-click START.bat
echo 3. Application will start automatically
echo.
echo To use on USB drive:
echo - Copy to USB drive
echo - Run START.bat from the USB
echo.
echo To share:
echo - ZIP this folder
echo - Send the ZIP file
echo - Extract on other computer
echo - Run START.bat
echo.
pause
