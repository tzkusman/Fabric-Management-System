# Portable Fabric Inventory Manager - Build & Deployment Guide

## 📦 Three Options to Deliver Your Application

---

## OPTION 1: Python-Based Portable (Easiest - Client needs Python)

**How it works:** Client has Python installed, runs a batch/PowerShell script

**Requirements:**
- Python 3.9+ installed on client machine
- First run auto-installs dependencies

**Setup for Client:**
1. Extract USB folder to any location
2. Double-click `START.bat` (Windows) or `START.ps1` (PowerShell)
3. Application auto-launches in browser
4. Data persists in `data/` folder

**Files needed on USB:**
```
FabricManager/
├── START.bat                 (Double-click to run)
├── START.ps1                 (PowerShell alternative)
├── portable_main.py          (Entry point)
├── main.py
├── models.py
├── database.py
├── crud.py
├── schemas.py
├── requirements.txt          (Auto-installed on first run)
├── templates/                (All HTML files)
├── static/                   (All CSS/JS files)
├── scripts/                  (Migration scripts)
└── data/                     (Created automatically)
    └── fabric.db             (Database persists here)
```

**Pros:**
- ✅ Easiest to build
- ✅ Smallest file size (~30MB after Python)
- ✅ Easy to update (just replace Python files)

**Cons:**
- ❌ Requires Python installed (~100MB)

---

## OPTION 2: Full Standalone Executable (Best for Clients - No Installation)

**How it works:** One `.exe` file with everything bundled

**Requirements for Building:**
- PyInstaller: `pip install pyinstaller`
- Your development machine has Python

**Build Steps:**

```powershell
# Step 1: Navigate to app directory
cd "path\to\fabric inventory"

# Step 2: Install PyInstaller
pip install pyinstaller

# Step 3: Build executable
pyinstaller build_portable.spec

# Step 4: Executable created in dist/ folder
# dist/FabricManager.exe (single file or folder)
```

**Output Structure:**
```
After building, you get:
dist/
├── FabricManager.exe         (Run this directly!)
└── (supporting DLLs auto-handled by PyInstaller)
```

**For Client - Super Simple:**
1. Copy `FabricManager.exe` to USB
2. Double-click `FabricManager.exe`
3. App starts with auto-opening browser

**Pros:**
- ✅ **ZERO installation** - truly portable
- ✅ **Single executable** (or small folder)
- ✅ **No Python required** on client
- ✅ Professional delivery

**Cons:**
- ❌ Larger file size (~200-300MB for first build)
- ⚠️ Antivirus may flag exe (can add certificate to fix)
- ❌ Slightly slower startup first time

---

## OPTION 3: Hybrid - Folder-Based with Embedded Python (Best Balance)

**Create a portable Python + App bundle:**

```batch
# Create folder structure
FabricManager/
├── python-embedded/         (Embedded Python runtime)
├── app/                      (Your FastAPI app)
│   ├── portable_main.py
│   ├── main.py
│   ├── models.py
│   ├── etc...
├── data/                     (Database folder)
├── RUN.bat                   (Launch script)
└── README.txt
```

**RUN.bat with embedded Python:**
```batch
@echo off
set APP_PATH=%~dp0
set PYTHON_PATH=%APP_PATH%python-embedded\python.exe
cd /d "%APP_PATH%app"
"%PYTHON_PATH%" portable_main.py
pause
```

---

## 🚀 QUICK START: Build Standalone .EXE

### Step 1: On Your Development PC

```powershell
# Open PowerShell in app directory
cd "G:\fabric inventory_V2\fabric inventory"

# Install build tool
pip install pyinstaller

# Create the executable
pyinstaller build_portable.spec
```

### Step 2: Test It

```powershell
# Run from dist folder
.\dist\FabricManager.exe
```

### Step 3: Deliver to Client

Copy `dist/FabricManager.exe` to USB stick or email

**Client Usage:**
```
1. Copy FabricManager.exe to Documents or Desktop
2. Double-click FabricManager.exe
3. Done! Browser opens with the app
```

---

## 🗂️ Database Persistence

Database is stored in: `%APPDATA%/FabricManager/fabric.db` (Option 2) or `data/fabric.db` (Option 1 & 3)

**Data survives:**
- ✅ Closing and reopening app
- ✅ Moving folder to different location
- ✅ Restarting computer

**Backup database:**
```powershell
# User can backup from within app:
# Dashboard → Database Operations → Export
# This creates a timestamped backup .db file
```

---

## ✅ Features of Portable Version

- ✅ **Auto-launch browser** - opens to http://127.0.0.1:8000
- ✅ **Auto-create database** on first run
- ✅ **Auto-setup tables** if needed
- ✅ **Data persistence** across runs
- ✅ **Offline-capable** - no internet needed
- ✅ **Clean shutdown** - proper server termination
- ✅ **Error handling** - shows user-friendly messages

---

## 🛠️ Customization Options

### Change Default Port
Edit in `portable_main.py`:
```python
PORT = 8000  # Change this
```

### Add Windows Startup Icon
```python
# In build_portable.spec, add:
icon='your_logo.ico'
```

### Hide Console Window (GUI only)
```python
# Edit EXE generation to use windowed mode:
exe = EXE(
    ...
    console=False,  # Hide console (needs GUI status messages)
)
```

### Add Auto-Start on Boot (Optional)
```powershell
# Add shortcut to Windows Startup folder
$shortcutPath = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\FabricManager.lnk"
```

---

## 🔒 Security Notes

1. **Database Isolation:** Each PC has its own local database
2. **No Cloud Sync:** Data stays on user's machine
3. **Backup Regularly:** Use export feature from app
4. **Multi-User:** Different users on same PC get separate data

---

## 📋 Recommended Delivery Method

### **OPTION 2 (Standalone .EXE) - RECOMMENDED** ✅

**Why?**
- Simplest for client
- Most professional
- No prerequisites
- Easy to update (new .exe)
- Single file delivery

**Delivery Package:**
```
USB STICK: FabricManager
├── FabricManager.exe          ← DOUBLE-CLICK TO RUN
├── README.txt                 (Instructions)
└── BACKUP/
    └── (Optional: sample backup files)
```

**Client Instructions:**
```
1. Copy FabricManager.exe to your USB or computer
2. Double-click FabricManager.exe
3. Wait 3-5 seconds for browser to open
4. Application is ready to use!

To close: Press Ctrl+C in the console window (or close window)

Need help? Contact support
```

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| Exe won't run | Might be blocked by antivirus, add to whitelist |
| Port 8000 in use | Edit `portable_main.py` to change PORT |
| Database lost | Check `data/fabric.db` or use DB export from app |
| Browser doesn't open | Open manually: http://127.0.0.1:8000 |
| Slow first startup | Normal - executable unpacking (~10 sec) |

---

## 📝 Build Command Summary

```powershell
# ONE COMMAND TO BUILD PORTABLE EXE:
pyinstaller --onefile --windowed --add-data "templates;templates" --add-data "static;static" --hidden-import=fastapi --hidden-import=uvicorn --hidden-import=sqlalchemy --hidden-import=jinja2 --hidden-import=reportlab -n FabricManager portable_main.py
```

Or use the spec file:
```powershell
pyinstaller build_portable.spec
```

---

## 🎉 Result

Your client gets:
- ✅ One `.exe` file (or folder) to run
- ✅ No installation needed
- ✅ Browser auto-opens
- ✅ Data persists automatically
- ✅ Professional delivery
- ✅ Can run on any Windows PC

**Size:** ~250MB (first time) | ~50MB updates
**Time to build:** 2-5 minutes
**Time for client to start:** Double-click, wait 3 seconds

---

## Next Steps

1. ✅ Install PyInstaller: `pip install pyinstaller`
2. ✅ Run build: `pyinstaller build_portable.spec`
3. ✅ Test: `dist/FabricManager.exe`
4. ✅ Deliver to client
5. ✅ Done! 🎉

