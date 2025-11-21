@echo off
REM ============================================================================
REM FABRIC INVENTORY MANAGEMENT SYSTEM - ONE-CLICK INSTALLER LAUNCHER
REM Double-click this file to install everything automatically
REM ============================================================================

setlocal enabledelayedexpansion

cls
echo.
echo ============================================================================
echo FABRIC INVENTORY MANAGEMENT SYSTEM - INSTALLER v3.5
echo ============================================================================
echo.
echo This installer will:
echo   * Check for Python installation (or install Python 3.11)
echo   * Create a virtual environment
echo   * Install all required packages
echo   * Set up application directories
echo   * Create a desktop shortcut
echo.
echo Press any key to continue...
pause >nul

REM Check for administrator privileges
openfiles >nul 2>&1
if errorlevel 1 (
    echo.
    echo ERROR: Administrator privileges required!
    echo Please right-click this file and select "Run as administrator"
    echo.
    pause
    exit /b 1
)

REM Get the directory where this script is located
cd /d "%~dp0"

REM Run PowerShell installer with full admin privileges
PowerShell -NoProfile -ExecutionPolicy Bypass -Command "& '%~dp0INSTALL.ps1'"

if errorlevel 1 (
    echo.
    echo Installation failed. Please check the error messages above.
    echo.
    echo Installation failed. Please check the error messages above.
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================================================
echo Installation completed successfully!
echo ============================================================================
echo.
echo You can now:
echo   1. Run START.bat to start the application
echo   2. Use the "Fabric Manager" desktop shortcut
echo.
pause
