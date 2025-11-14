Fabric Management System (FastAPI + SQLite)

Quick start (Windows PowerShell):

1) Create a venv (recommended):

python -m venv .venv
.\.venv\Scripts\Activate.ps1

2) Install dependencies:

pip install -r "requirements.txt"

3) Start the app:

uvicorn main:app --reload

4) Open in browser:

http://127.0.0.1:8000/
## Full setup & run guide (Windows PowerShell)

This project is a small FastAPI app using SQLite. The steps below assume you are on Windows and using PowerShell (v5.1). Adjust the commands for other shells.

1) Create and activate a virtual environment (recommended)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2) Install dependencies

```powershell
pip install -r "requirements.txt"
```

3) Initialize or migrate the database

- If you're starting from scratch you can let the app create the SQLite DB automatically on first run.
- If you need to apply the included small migration (adds new columns), run:

```powershell
python scripts\migrate_add_columns.py
```

This script is idempotent and safe to run multiple times.

4) Start the development server (uvicorn)

```powershell
uvicorn main:app --reload
```

Open: http://127.0.0.1:8000/

5) Expose the app via ngrok (optional)

- Option A (recommended if you already have ngrok installed):

```powershell
ngrok http 127.0.0.1:8000
```

Use the printed "Forwarding" https URL to access the app remotely.

- Option B (use the helper script which uses pyngrok):

```powershell
python run_with_ngrok.py
```

If the helper fails to auto-download ngrok on Windows, set the environment variable `NGROK_PATH` to a local ngrok executable or install ngrok manually and use Option A. Also set `NGROK_AUTHTOKEN` if you want to link tunnels to your ngrok account.

6) Quick commands

- Export stock as CSV (from the app UI) or use the export route if exposed.
- Generate a PDF invoice: open the sale in the UI and click "Invoice".

7) Running the tests / quick smoke checks

There is a small test script that exercises purchases → sales → stock. Run it like:

```powershell
python scripts\test_sale_stock.py
```

8) Troubleshooting / notes

- If you see an SQLite OperationalError complaining about missing columns, run the migration script in step (3) and restart the app.
- If ngrok shows ERR_NGROK_8012 (upstream refused), prefer binding tunnels to 127.0.0.1 instead of localhost or ::1, e.g. `ngrok http 127.0.0.1:8000`.
- If the app is unreachable after closing VS Code, it will stop; to keep it running on Windows, run uvicorn in a background PowerShell job or a dedicated host/server. For development, re-run the uvicorn command when you return.

9) Optional convenience: create a PowerShell start script

Create `start-local.ps1` in the repo root (example):

```powershell
# .\start-local.ps1
. .\.venv\Scripts\Activate.ps1
uvicorn main:app --reload
```

Then run `.\start-local.ps1` to start the app with one command.

10) Next steps and cleanup

- If you want a fresh database, remove `fabric.db` and re-run the app (it will recreate schema). Back up your DB first.
- If you'd like, I can add the `start-local.ps1` script to the repo, or add a small PowerShell wrapper that also opens the browser automatically. Tell me which you prefer.

---

Requirements coverage: the README now includes setup, migration, running, ngrok tips, tests, and troubleshooting (Done).

Features:
- Add suppliers, customers, purchases, and sales.
- Sales include fixed 18% tax automatically.
- Stock summary (per fabric type).
- Purchase and sales history.
- Generate simple PDF invoice for a sale.

Ngrok integration
-----------------
To expose your local server publicly, install `pyngrok` (it's added in `requirements.txt`) and run:

```powershell
python run_with_ngrok.py
```

This will open an ngrok tunnel to port 8000 and print the public URL in the console. Configure an ngrok authtoken for a persistent URL if needed.
