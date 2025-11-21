"""
Portable Configuration File
Customize these settings for your deployment
"""

import os
from pathlib import Path

# ============== SERVER SETTINGS ==============

# Server host and port
SERVER_HOST = "127.0.0.1"  # localhost only (internal)
SERVER_PORT = 8000         # Change if port is in use

# Auto-open browser after server starts
AUTO_OPEN_BROWSER = True
BROWSER_OPEN_DELAY = 3     # seconds

# ============== DATABASE SETTINGS ==============

# Database location (relative to app root)
DB_RELATIVE_PATH = "data/fabric.db"

# Auto-create database if missing
AUTO_CREATE_DB = True

# ============== LOGGING SETTINGS ==============

LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR

# Save logs to file
SAVE_LOGS = True
LOG_FILE = "data/app.log"

# ============== SECURITY SETTINGS ==============

# Restrict to localhost only (no network access)
LOCALHOST_ONLY = True

# Session timeout (minutes)
SESSION_TIMEOUT = 480  # 8 hours

# ============== UI SETTINGS ==============

# Application name shown in browser title
APP_NAME = "Fabric Inventory Manager"

# Version
APP_VERSION = "1.0.0"

# Show debug info on dashboard
DEBUG_MODE = False

# ============== PERFORMANCE SETTINGS ==============

# Number of worker threads
WORKERS = 2

# Request timeout (seconds)
REQUEST_TIMEOUT = 300

# ============== DATA SETTINGS ==============

# Auto-backup database on startup
AUTO_BACKUP_ON_STARTUP = False

# Keep backup history (number of backups)
BACKUP_HISTORY = 5

# ============== FEATURES ==============

# Enable payment tracking
ENABLE_PAYMENTS = True

# Enable ledger system
ENABLE_LEDGERS = True

# Default tax rate (%)
DEFAULT_TAX_RATE = 18

# Enable ngrok tunneling (external access)
ENABLE_NGROK = False

# ============== FILE SETTINGS ==============

def get_app_root():
    """Get application root directory"""
    if os.path.basename(os.path.abspath(__file__)) == 'portable_config.py':
        return os.path.dirname(os.path.abspath(__file__))
    return os.getcwd()

def get_db_path():
    """Get full database path"""
    app_root = get_app_root()
    db_path = os.path.join(app_root, DB_RELATIVE_PATH)
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    return db_path

def get_log_path():
    """Get full log file path"""
    if not SAVE_LOGS:
        return None
    app_root = get_app_root()
    log_path = os.path.join(app_root, LOG_FILE)
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    return log_path

# ============== RUNTIME CONFIGURATION ==============

RUNTIME_CONFIG = {
    'db_path': get_db_path(),
    'log_path': get_log_path(),
    'app_root': get_app_root(),
}
