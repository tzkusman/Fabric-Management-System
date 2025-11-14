@echo off
setlocal

REM Change to the directory where this batch file is located
cd /d "%~dp0"

echo Starting Uvicorn server in a new PowerShell window...

REM Launch PowerShell to run uvicorn
REM This command activates the virtual environment *within the new PowerShell window*
REM and then runs the uvicorn command.
start "Uvicorn Server" powershell.exe -NoExit -Command "& '.\venv\Scripts\Activate.ps1'; uvicorn main:app --reload --host 0.0.0.0 --port 8000"

echo.
echo Giving the server a moment to start (3 seconds)...
timeout /t 3 >nul

echo Opening application in default web browser: http://127.0.0.1:8000
start http://127.0.0.1:8000

echo.
echo Uvicorn server launched. Check the new PowerShell window for output.
echo This batch file will now close.
exit /b