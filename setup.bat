@echo off
setlocal enabledelayedexpansion

echo ===============================
echo   Checking Python Installation
echo ===============================

:: Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python not found. Installing Python 3.11.5...
    set "PYTHON_INSTALLER=python_installer.exe"
    curl -L -o %PYTHON_INSTALLER% https://www.python.org/ftp/python/3.11.5/python-3.11.5-amd64.exe
    echo Installing Python silently...
    %PYTHON_INSTALLER% /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
    del %PYTHON_INSTALLER%
    echo Waiting for Python to finish installing...
    timeout /t 10 >nul
)

:: Verify Python installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Python installation failed. Please install manually.
    pause
    exit /b 1
)

echo.
echo ===============================
echo   Python is installed!
echo ===============================

:: Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

:: Create virtual environment if not exists
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

:: Activate venv
echo Activating virtual environment...
call venv\Scripts\activate

:: Install dependencies
if exist requirements.txt (
    echo Installing dependencies from requirements.txt...
    pip install --upgrade pip
    pip install -r requirements.txt
) else (
    echo No requirements.txt found, skipping dependency installation.
)

echo.
echo ===============================
echo   Setup Completed Successfully
echo ===============================
echo You can now run your application using: run.bat
echo.

pause
exit /b
