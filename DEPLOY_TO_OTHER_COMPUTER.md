# Deploy Fabric Management System to Another Computer

## Quick Start - 3 Steps

### Step 1: Prepare the Package
Run this on your computer to create a portable package:
```batch
python BUILD_PORTABLE.bat
```
This creates a `dist/fabric-manager` folder with everything needed.

### Step 2: Copy to USB/Cloud
Copy the entire `dist/fabric-manager` folder to:
- USB drive
- Cloud storage (Google Drive, OneDrive, etc.)
- Email as ZIP
- Network drive

### Step 3: Run on Other Computer
On the other computer:
1. **Extract** the folder (if from ZIP)
2. **Double-click** `START.bat` in the folder
3. Browser opens automatically to `http://127.0.0.1:8000`

---

## What's Inside the Package

```
fabric-manager/
├── FabricManager.exe          ← Main application (if built as EXE)
├── fabric.db                  ← Database (starts empty, auto-creates on first run)
├── templates/                 ← HTML pages
├── static/                    ← CSS, JavaScript, images
├── scripts/                   ← Utility scripts
├── requirements.txt           ← Python dependencies
├── START.bat                  ← Quick start script
├── main.py                    ← Application source code
├── models.py
├── crud.py
├── database.py
└── schemas.py
```

---

## Troubleshooting

### ❌ "Internal Server Error" on Another Computer

**Common Causes:**
1. Missing dependencies → Install Python packages
2. Wrong working directory → Script fails to find files
3. Database file in wrong location → Create new database

**Solution:**
Run this in the folder instead of `START.bat`:

```bash
# If Python 3 is installed:
python main.py

# If that doesn't work, try:
python3 main.py

# See detailed error messages
python -u main.py
```

---

### ❌ "Python not found" Error

**If Python isn't installed on other computer:**

**Option A: Install Python (Recommended)**
- Download from https://www.python.org/downloads/
- During installation, **CHECK** "Add Python to PATH"
- Then run: `python main.py`

**Option B: Use Built Executable**
- Build the executable: `pyinstaller FabricManager.spec`
- Copy the executable from `dist/` folder
- No Python needed

---

### ❌ Database Errors / "3 folders created"

**Problem:** Files scattered in wrong locations

**Fix:**
1. Delete the incorrect folders
2. Create a clean folder structure:
```
fabric-manager/
├── main.py
├── models.py
├── crud.py
├── database.py
├── schemas.py
├── templates/     ← Folder with HTML files
├── static/        ← Folder with CSS/JS
└── fabric.db      ← Database file (will be created)
```

3. Run: `python main.py`

---

## Manual Setup (If Folder Structure is Wrong)

If the files are scattered, fix it:

```powershell
# In PowerShell:

# 1. Create proper folder structure
mkdir fabric-manager
cd fabric-manager

# 2. Copy essential files
copy ..\main.py .
copy ..\models.py .
copy ..\crud.py .
copy ..\database.py .
copy ..\schemas.py .

# 3. Copy folders
xcopy ..\templates templates /E /I
xcopy ..\static static /E /I
xcopy ..\scripts scripts /E /I

# 4. Copy database (if exists)
copy ..\fabric.db . 2>nul

# 5. Install dependencies
pip install -r requirements.txt

# 6. Run
python main.py
```

---

## Best Way to Deploy

### Recommended: Portable Python Environment

Create a self-contained package:

```batch
@echo off
REM Create distribution folder
mkdir dist\fabric-manager
cd dist\fabric-manager

REM Copy all essential files
copy ..\..\main.py .
copy ..\..\models.py .
copy ..\..\crud.py .
copy ..\..\database.py .
copy ..\..\schemas.py .
copy ..\..\requirements.txt .

REM Copy folders
xcopy ..\..\templates templates /E /I
xcopy ..\..\static static /E /I

REM Create venv locally
python -m venv venv
call venv\Scripts\activate.bat
pip install -r requirements.txt

REM Create startup script
@echo cd /d %~dp0 > START.bat
@echo call venv\Scripts\activate.bat >> START.bat
@echo python main.py >> START.bat

echo Package ready in dist\fabric-manager
```

---

## What Works on Other Computer

✅ Database operations (CRUD)  
✅ Add/Edit suppliers, customers, purchases, sales  
✅ Export/Import database  
✅ Generate invoices  
✅ View ledgers and reports  
✅ Payment tracking  

---

## Backup Before Deploying

Always backup your database before moving to another computer:

1. Go to `http://127.0.0.1:8000`
2. Click **Database** → **Backup/Restore**
3. Click **Export Database**
4. Save the ZIP file
5. Copy this ZIP to the other computer
6. On other computer: Import the database

---

## Performance Notes

- **First run:** Takes 10-30 seconds (creates database)
- **Subsequent runs:** Instant (< 2 seconds)
- **On USB:** Slightly slower, but works fine
- **On Cloud:** May need wait for sync before running

---

## Still Having Issues?

1. **Check if Python is installed:**
   ```bash
   python --version
   ```

2. **Verify file structure:**
   ```bash
   dir main.py models.py crud.py database.py schemas.py
   ```

3. **Check if port 8000 is available:**
   ```bash
   netstat -ano | findstr :8000
   ```
   If something is on port 8000, run on different port:
   ```bash
   python main.py  # Edit main.py to change port if needed
   ```

4. **Look for detailed error messages:**
   ```bash
   python main.py 2>&1 | Tee-Object log.txt
   ```

---

## Contact & Support

If issue persists, check:
- `DEPLOYMENT_MANUAL.md` for advanced setup
- `PORTABLE_BUILD_GUIDE.md` for building standalone EXE
- `00_START_HERE.md` for general overview
