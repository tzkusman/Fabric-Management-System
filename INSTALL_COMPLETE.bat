@echo off
REM ============================================
REM MASTER Installation Script
REM One script to rule them all!
REM ============================================

setlocal enabledelayedexpansion

cls
echo.
echo ╔════════════════════════════════════════╗
echo ║  FABRIC MANAGEMENT SYSTEM              ║
echo ║  Complete Installation Wizard          ║
echo ╚════════════════════════════════════════╝
echo.
echo What would you like to do?
echo.
echo 1) Install Everything (Recommended)
echo    - Checks Python, installs all packages, starts app
echo.
echo 2) Install Python Only
echo    - If you don't have Python installed
echo.
echo 3) Start Application Only
echo    - If already installed, just run the app
echo.
echo 4) View Installation Guide
echo    - Read detailed instructions
echo.

set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" goto install_all
if "%choice%"=="2" goto install_python
if "%choice%"=="3" goto start_app
if "%choice%"=="4" goto view_guide
echo Invalid choice. Please try again.
pause
goto start

:install_all
cls
echo.
echo ============================================
echo  Installing Everything...
echo ============================================
echo.
cd dist\fabric-manager
call INSTALL_ALL.bat
goto end

:install_python
cls
echo.
echo ============================================
echo  Installing Python...
echo ============================================
echo.
cd dist\fabric-manager
call INSTALL_PYTHON.bat
goto end

:start_app
cls
echo.
echo ============================================
echo  Starting Application...
echo ============================================
echo.
cd dist\fabric-manager
call START.bat
goto end

:view_guide
cls
echo.
echo Opening installation guide...
echo.
cd dist\fabric-manager
start INSTALLATION_GUIDE.md
timeout /t 2
goto start

:end
echo.
pause
