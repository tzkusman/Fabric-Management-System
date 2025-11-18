@echo off
REM Build Script for Portable Fabric Manager
REM This script creates a standalone .exe file
REM Run this on your development machine (ONLY ONCE)

setlocal enabledelayedexpansion

cls
echo.
echo ============================================================
echo   FABRIC INVENTORY MANAGER - BUILD PORTABLE EXECUTABLE
echo ============================================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Install Python 3.9+ first.
    pause
    exit /b 1
)

echo [1/5] Checking Python...
python --version
echo OK
echo.

REM Check PyInstaller
echo [2/5] Checking PyInstaller...
pip list | find "pyinstaller" >nul
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
    if errorlevel 1 (
        echo ERROR: Failed to install PyInstaller
        pause
        exit /b 1
    )
)
echo OK
echo.

REM Check dependencies
echo [3/5] Installing dependencies...
pip install -q -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo OK
echo.

REM Clean old builds
echo [4/5] Cleaning old builds...
if exist "build" rmdir /s /q "build" >nul 2>&1
if exist "dist" rmdir /s /q "dist" >nul 2>&1
if exist "*.spec" del *.spec >nul 2>&1
echo OK
echo.

REM Build executable
echo [5/5] Building executable...
echo This may take 2-5 minutes...
echo.

pyinstaller --onefile ^
    --windowed ^
    --name FabricManager ^
    --add-data "templates;templates" ^
    --add-data "static;static" ^
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
    echo.
    echo ERROR: Build failed!
    pause
    exit /b 1
)

echo.
echo ============================================================
echo   BUILD SUCCESSFUL!
echo ============================================================
echo.
echo Location: dist\FabricManager.exe
echo Size: Check dist folder
echo.
echo NEXT STEPS:
echo 1. Test the exe: dist\FabricManager.exe
echo 2. If it works, copy to USB:
echo    - Copy dist\FabricManager.exe to USB root
echo    - Optionally copy USER_GUIDE.md and README.txt
echo 3. Give USB to client - they just double-click!
echo.
echo To test now, type: dist\FabricManager.exe
echo.
pause
