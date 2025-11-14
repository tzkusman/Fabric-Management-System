"""
Start uvicorn and open a public ngrok tunnel to port 8000.
Usage: python run_with_ngrok.py
Requires: pyngrok installed and ngrok authtoken configured (optional — pyngrok will still work without an authtoken but may have limits).
"""
import sys
import os
import time

try:
    from pyngrok import ngrok
except Exception as e:
    print("pyngrok not installed or failed to import. Install with: pip install pyngrok")
    print(e)
    sys.exit(1)

import subprocess

HOST = "0.0.0.0"
PORT = 8000

# create ngrok tunnel
print(f"Opening ngrok tunnel on port {PORT}...")
public_url = None
try:
    # Optionally set auth token from env var (NGROK_AUTHTOKEN)
    ngrok_token = os.environ.get('NGROK_AUTHTOKEN')
    if ngrok_token:
        try:
            ngrok.set_auth_token(ngrok_token)
            print('Set ngrok authtoken from NGROK_AUTHTOKEN')
        except Exception as e:
            print('Failed to set ngrok authtoken via pyngrok:', e)

    # If NGROK_PATH is provided, tell pyngrok to use that binary instead of downloading
    ngrok_path = os.environ.get('NGROK_PATH')
    pyngrok_config = None
    if ngrok_path:
        ngrok_path = os.path.expanduser(ngrok_path)
        if not os.path.exists(ngrok_path):
            print(f"NGROK_PATH is set but the file does not exist: {ngrok_path}")
        else:
            try:
                from pyngrok import conf as _conf
                pyngrok_config = _conf.PyngrokConfig(ngrok_path=ngrok_path)
                print(f"Using ngrok binary from NGROK_PATH: {ngrok_path}")
            except Exception:
                pyngrok_config = None

    if pyngrok_config:
        tunnel = ngrok.connect(PORT, pyngrok_config=pyngrok_config)
    else:
        tunnel = ngrok.connect(PORT)
    public_url = tunnel.public_url
    print("ngrok public URL:", public_url)
except Exception as e:
    print("Failed to open ngrok tunnel:", e)

# start uvicorn
cmd = [sys.executable, "-m", "uvicorn", "main:app", "--host", HOST, "--port", str(PORT), "--reload"]
print("Starting uvicorn with:", " ".join(cmd))
proc = subprocess.Popen(cmd)
print("uvicorn PID:", proc.pid)
local_url = f"http://127.0.0.1:{PORT}"
print("Local (use this in your browser):", local_url)
print("Note: 0.0.0.0 is a bind address and is not reachable in a browser. Use 127.0.0.1 or localhost instead.")

try:
    while True:
        time.sleep(1)
        if proc.poll() is not None:
            print("uvicorn exited with code", proc.returncode)
            break
except KeyboardInterrupt:
    print("Shutting down...")
    proc.terminate()
    proc.wait()
    if public_url:
        try:
            ngrok.disconnect(public_url)
            ngrok.kill()
        except Exception:
            pass
    print("Stopped.")
