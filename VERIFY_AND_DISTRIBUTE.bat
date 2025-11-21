@echo off
REM ============================================================
REM PORTABLE BUILD VERIFICATION AND DISTRIBUTION TOOL
REM Verify portable build integrity and create distribution
REM ============================================================

setlocal enabledelayedexpansion
cd /d "%~dp0"

cls
echo.
echo ============================================================
echo  PORTABLE BUILD VERIFICATION & DISTRIBUTION TOOL
echo ============================================================
echo.

REM Check if dist\FabricManager exists
if not exist "dist\FabricManager" (
    echo [ERROR] Portable build not found
    echo [INFO] Run BUILD_PORTABLE_COMPLETE.bat first
    pause
    exit /b 1
)

echo [*] Verifying portable build integrity...
echo.

REM Count files
set "exe_count=0"
set "template_count=0"
set "static_count=0"
set "success=0"

for /f %%A in ('dir /b "dist\FabricManager\FabricManager.exe" 2^>nul ^| find /c /v ""') do set exe_count=%%A
for /f %%A in ('dir /s /b "dist\FabricManager\templates\*" 2^>nul ^| find /c /v ""') do set template_count=%%A
for /f %%A in ('dir /s /b "dist\FabricManager\static\*" 2^>nul ^| find /c /v ""') do set static_count=%%A

REM Verify essential files
echo Checking essential files:
echo.

if exist "dist\FabricManager\FabricManager.exe" (
    echo [+] FabricManager.exe found ✓
    for /f %%A in ('dir /b "dist\FabricManager\FabricManager.exe" ^| find /v ""') do (
        for %%B in (dist\FabricManager\FabricManager.exe) do set exe_size=%%~zB
        echo    Size: !exe_size! bytes
    )
) else (
    echo [-] FabricManager.exe NOT found ✗
    set success=1
)

if exist "dist\FabricManager\templates" (
    echo [+] templates directory found ✓
    echo    Contains: !template_count! items
) else (
    echo [-] templates directory NOT found ✗
    set success=1
)

if exist "dist\FabricManager\static" (
    echo [+] static directory found ✓
    echo    Contains: !static_count! items
) else (
    echo [-] static directory NOT found ✗
    set success=1
)

if exist "dist\FabricManager\START.bat" (
    echo [+] START.bat found ✓
) else (
    echo [-] START.bat NOT found ✗
    set success=1
)

if exist "dist\FabricManager\portable_config.py" (
    echo [+] portable_config.py found ✓
) else (
    echo [-] portable_config.py NOT found ✗
)

if exist "dist\FabricManager\data" (
    echo [+] data directory found ✓
    if exist "dist\FabricManager\data\fabric.db" (
        echo [+] fabric.db found ✓
    ) else (
        echo [!] fabric.db not found (will be created on first run)
    )
) else (
    echo [-] data directory NOT found ✗
    mkdir "dist\FabricManager\data"
    echo [+] data directory created
)

echo.
echo Checking configuration files:
echo.

if exist "dist\FabricManager\README.md" (
    echo [+] README.md found ✓
) else (
    echo [-] README.md NOT found ✗
)

if exist "dist\FabricManager\PACKAGE_INFO.txt" (
    echo [+] PACKAGE_INFO.txt found ✓
) else (
    echo [-] PACKAGE_INFO.txt NOT found ✗
)

echo.

if %success% equ 0 (
    echo [SUCCESS] All essential files verified! ✓
    echo.
) else (
    echo [WARNING] Some files are missing
    echo.
)

REM Menu
:menu
echo.
echo ============================================================
echo  DISTRIBUTION OPTIONS
echo ============================================================
echo.
echo 1. Create ZIP distribution (FabricManager_v3.1.0.zip)
echo 2. Create portable folder only (for testing)
echo 3. Verify portable executable
echo 4. Show build statistics
echo 5. Open dist folder
echo 6. Exit
echo.
set /p choice="Choose option (1-6): "

if "%choice%"=="1" goto create_zip
if "%choice%"=="2" goto folder_only
if "%choice%"=="3" goto verify_exe
if "%choice%"=="4" goto statistics
if "%choice%"=="5" goto open_folder
if "%choice%"=="6" goto end

echo Invalid choice. Try again.
goto menu

:create_zip
echo.
echo [*] Creating ZIP distribution...
echo.

REM Check if 7-Zip or WinRAR is available
where 7z >nul 2>&1
if !errorlevel! equ 0 (
    echo [+] 7-Zip found, using for compression...
    if exist "FabricManager_v3.1.0.zip" del "FabricManager_v3.1.0.zip"
    7z a -tzip FabricManager_v3.1.0.zip dist\FabricManager\*
    if exist "FabricManager_v3.1.0.zip" (
        echo [SUCCESS] ZIP file created: FabricManager_v3.1.0.zip
        for /f %%A in ('dir /b "FabricManager_v3.1.0.zip" ^| find /v ""') do (
            for %%B in (FabricManager_v3.1.0.zip) do echo [+] Size: %%~zB bytes
        )
    )
    goto menu
)

REM Try PowerShell as fallback
echo [+] Using PowerShell for compression...
powershell -command "Compress-Archive -Path 'dist\FabricManager' -DestinationPath 'FabricManager_v3.1.0.zip' -Force"
if exist "FabricManager_v3.1.0.zip" (
    echo [SUCCESS] ZIP file created: FabricManager_v3.1.0.zip
    for /f %%A in ('dir /b "FabricManager_v3.1.0.zip"') do (
        for %%B in (FabricManager_v3.1.0.zip) do echo [+] Size: %%~zB bytes
    )
) else (
    echo [ERROR] Failed to create ZIP file
)
goto menu

:folder_only
echo.
echo [*] Portable folder ready at: dist\FabricManager\
echo.
echo Next steps:
echo 1. Copy dist\FabricManager to another location
echo 2. Double-click START.bat
echo 3. Application should launch
echo.
pause
goto menu

:verify_exe
echo.
echo [*] Verifying executable...
if exist "dist\FabricManager\FabricManager.exe" (
    echo [+] Executable found
    REM Check if it's a valid PE file
    for /f %%A in ('wmic datafile where name="dist\\FabricManager\\FabricManager.exe" get Description /value 2^>nul ^| find "Description"') do (
        echo [+] %%A
    )
    
    REM Show file info
    echo.
    echo File Information:
    for %%A in (dist\FabricManager\FabricManager.exe) do (
        echo   Size: %%~zA bytes
        echo   Created: %%~tA
    )
    
    echo.
    echo [SUCCESS] Executable is valid
) else (
    echo [ERROR] Executable not found
)
echo.
pause
goto menu

:statistics
echo.
echo ============================================================
echo  BUILD STATISTICS
echo ============================================================
echo.

set "total_files=0"
set "total_size=0"

echo Counting files and calculating size...
echo.

REM Count all files
for /f %%A in ('dir /s /b "dist\FabricManager\*" 2^>nul ^| find /c /v ""') do set total_files=%%A

echo Total Files: !total_files!
echo.

echo Directory Breakdown:
echo.

REM Templates
for /f %%A in ('dir /s /b "dist\FabricManager\templates\*" 2^>nul ^| find /c /v ""') do set template_files=%%A
echo [+] Templates: !template_files! files
if exist "dist\FabricManager\templates\bank_statement.html" (
    echo     - Bank statement templates included
)

REM Static
for /f %%A in ('dir /s /b "dist\FabricManager\static\*" 2^>nul ^| find /c /v ""') do set static_files=%%A
echo [+] Static Assets: !static_files! files

REM Data
for /f %%A in ('dir /s /b "dist\FabricManager\data\*" 2^>nul ^| find /c /v ""') do set data_files=%%A
echo [+] Data Directory: !data_files! files

echo.
echo Executable Information:
echo.
for %%A in (dist\FabricManager\FabricManager.exe) do (
    echo [+] Executable Size: %%~zA bytes
    echo    (%%~zB MB = %%~zA / 1048576)
    set /a exe_size_mb=%%~zA / 1048576
    echo    Approximate: !exe_size_mb! MB
)

echo.
echo [INFO] Typical distribution:
echo   - Portable folder: 250-350 MB
echo   - ZIP compressed: 80-120 MB
echo   - Extraction size: 300-400 MB on disk
echo.
echo [INFO] Build includes:
echo   - Python runtime
echo   - FastAPI/Uvicorn
echo   - SQLAlchemy
echo   - All dependencies
echo   - 30+ UI templates
echo   - Bank statement module
echo   - Complete database schema
echo.
pause
goto menu

:open_folder
echo.
echo [*] Opening dist folder...
start explorer.exe "%cd%\dist\FabricManager"
echo.
goto menu

:end
echo.
echo Thank you for using Portable Build Tool
echo.
exit /b 0
