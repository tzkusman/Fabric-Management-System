@echo off
setlocal enabledelayedexpansion

echo ================================================
echo        Fabric Inventory Setup Installer
echo ================================================
echo.

:: Change directory to where this .bat file is located
cd /d "%~dp0"

:: Check for Python installation
echo Checking for Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python not found. Downloading and installing Python 3.11.5...
    set "PYTHON_INSTALLER=python_installer.exe"
    curl -L -o "%PYTHON_INSTALLER%" https://www.python.org/ftp/python/3.11.5/python-3.11.5-amd64.exe

    echo Installing Python silently...
    "%PYTHON_INSTALLER%" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
    del "%PYTHON_INSTALLER%"

    echo Waiting for Python to finish installing...
    timeout /t 10 >nul
)

:: Verify Python installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python installation failed. Please install manually.
    pause
    exit /b 1
)

echo.
echo ================================================
echo       Python installation verified
echo ================================================
echo.

:: Upgrade pip globally (just in case)
python -m ensurepip --upgrade
python -m pip install --upgrade pip

:: Create virtual environment if missing
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv "venv"
)

:: Activate virtual environment
echo Activating virtual environment...
call "venv\Scripts\activate"

:: Upgrade pip inside venv safely
echo Upgrading pip inside venv...
"%~dp0venv\Scripts\python.exe" -m ensurepip --upgrade
"%~dp0venv\Scripts\python.exe" -m pip install --upgrade pip

:: Install dependencies
if exist "requirements.txt" (
    echo Installing dependencies from requirements.txt...
    pip install -r "requirements.txt"
) else (
    echo No requirements.txt found, skipping package installation.
)

echo.
echo ================================================
echo     Setup Completed Successfully!
echo ================================================
echo You can now run your app with: run.bat
echo.

pause
exit /b
