# PowerShell script to prepare USB deployment
# Run: .\PREPARE_USB.ps1

Write-Host ""
Write-Host "╔═══════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   FABRIC MANAGER - USB DEPLOYMENT PREPARATION       ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Check if dist folder exists
if (-not (Test-Path "dist")) {
    Write-Host "❌ Error: dist/ folder not found" -ForegroundColor Red
    Write-Host ""
    Write-Host "You need to build the executable first:" -ForegroundColor Yellow
    Write-Host "  1. Run: BUILD_PORTABLE.bat" -ForegroundColor White
    Write-Host "  2. Wait for build to complete" -ForegroundColor White
    Write-Host "  3. Then run this script again" -ForegroundColor White
    Write-Host ""
    Read-Host "Press Enter to close"
    exit 1
}

# Check for executable
$exePath = Get-ChildItem -Path "dist" -Name "FabricManager.exe" -ErrorAction SilentlyContinue
if (-not $exePath) {
    Write-Host "❌ Error: FabricManager.exe not found in dist/" -ForegroundColor Red
    Read-Host "Press Enter to close"
    exit 1
}

Write-Host "✓ Found FabricManager.exe" -ForegroundColor Green
Write-Host ""

# Get USB drive letter
Write-Host "USB Drive Options:" -ForegroundColor Yellow
$drives = Get-Volume | Where-Object {$_.DriveType -eq 'Removable'} | Select-Object -ExpandProperty DriveLetter

if ($drives.Count -eq 0) {
    Write-Host "❌ No USB drives detected" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please:" -ForegroundColor Yellow
    Write-Host "  1. Insert USB drive" -ForegroundColor White
    Write-Host "  2. Run this script again" -ForegroundColor White
    Write-Host ""
    Read-Host "Press Enter to close"
    exit 1
}

Write-Host ""
$counter = 0
foreach ($drive in $drives) {
    $counter++
    Write-Host "  [$counter] $($drive):\" -ForegroundColor White
}
Write-Host ""

# Let user choose drive
$choice = Read-Host "Select USB drive number (1-$($drives.Count))"

if ([int]$choice -lt 1 -or [int]$choice -gt $drives.Count) {
    Write-Host "❌ Invalid selection" -ForegroundColor Red
    exit 1
}

$selectedDrive = $drives[[int]$choice - 1]
$usbPath = "$($selectedDrive):\"

Write-Host ""
Write-Host "Creating deployment structure..." -ForegroundColor Yellow

# Create folder structure on USB
$deployFolder = Join-Path $usbPath "FabricManager"
if (Test-Path $deployFolder) {
    Write-Host "Folder exists. Backing up old version..." -ForegroundColor Yellow
    $backupFolder = "$deployFolder-backup-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
    Move-Item $deployFolder $backupFolder -Force
    Write-Host "Old version backed up to: $backupFolder" -ForegroundColor Gray
}

New-Item -ItemType Directory -Path $deployFolder -Force | Out-Null

# Copy files
Write-Host "Copying files to USB..." -ForegroundColor Yellow

$filesToCopy = @(
    ("dist\FabricManager.exe", "FabricManager.exe"),
    ("USER_GUIDE.md", "USER_GUIDE.md"),
    ("README.txt", "README.txt"),
    ("PORTABLE_BUILD_GUIDE.md", "BUILD_GUIDE.md")
)

foreach ($file in $filesToCopy) {
    $source = $file[0]
    $dest = $file[1]
    
    if (Test-Path $source) {
        Copy-Item $source (Join-Path $deployFolder $dest) -Force
        Write-Host "  ✓ $dest" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "Creating data folder..." -ForegroundColor Yellow
New-Item -ItemType Directory -Path (Join-Path $deployFolder "data") -Force | Out-Null
Write-Host "  ✓ data/" -ForegroundColor Green

Write-Host ""
Write-Host "╔═══════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                  DEPLOYMENT READY!                   ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

Write-Host "USB Location: $deployFolder" -ForegroundColor White
Write-Host ""
Write-Host "Files deployed:" -ForegroundColor Yellow
Write-Host "  ✓ FabricManager.exe (the application)" -ForegroundColor Green
Write-Host "  ✓ USER_GUIDE.md (detailed instructions)" -ForegroundColor Green
Write-Host "  ✓ README.txt (quick start)" -ForegroundColor Green
Write-Host "  ✓ data/ folder (for database)" -ForegroundColor Green
Write-Host ""

Write-Host "NEXT STEPS FOR YOUR CLIENT:" -ForegroundColor Yellow
Write-Host "  1. Safely eject USB" -ForegroundColor White
Write-Host "  2. Give USB to client" -ForegroundColor White
Write-Host "  3. Client double-clicks: FabricManager.exe" -ForegroundColor White
Write-Host "  4. App opens and works!" -ForegroundColor White
Write-Host ""

Write-Host "SIZE INFO:" -ForegroundColor Yellow
$exeSize = (Get-Item (Join-Path $deployFolder "FabricManager.exe")).Length / 1MB
Write-Host "  Executable size: $([Math]::Round($exeSize, 1)) MB" -ForegroundColor Gray
Write-Host ""

Write-Host "✅ Deployment package ready on USB!" -ForegroundColor Green
Write-Host ""

Read-Host "Press Enter to close"
