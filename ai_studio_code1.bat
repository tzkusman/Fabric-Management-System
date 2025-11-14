@echo off
echo Starting Fabric Inventory Management System Setup...

REM --- Check for and Install Uvicorn ---

REM Attempt to run uvicorn to see if it's already installed and recognized.
REM We redirect output to nul to keep the console clean for this check.
uvicorn --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Uvicorn not found. Attempting to install Uvicorn...
    pip install uvicorn python-multipart
    IF %ERRORLEVEL% NEQ 0 (
        echo ERROR: Failed to install Uvicorn. Please ensure Python and pip are installed and in your PATH, and you have an internet connection.
        echo You might need to run this script as an administrator.
        pause
        exit /b %ERRORLEVEL%
    ) ELSE (
        echo Uvicorn installed successfully.
    )
) ELSE (
    echo Uvicorn is already installed.
)

REM --- Start the Application ---

echo Starting Uvicorn server...

REM Start the server in a new window so it doesn't block the rest of the script
REM The /k keeps the new command window open after the command finishes (useful for seeing server logs)
start "Uvicorn Server" cmd /k uvicorn main:app --reload --host 0.0.0.0 --port 8000

REM Wait a bit for the server to start (optional, gives it a few seconds)
timeout /t 3 >nul

REM Open the default browser automatically
start http://127.0.0.1:8000

echo.
echo Application started. Press any key to close this window.
pause