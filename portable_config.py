"""
Portable Configuration File
Customize these settings for your deployment
Enhanced Version with Bank Statement Support
"""

import os
from pathlib import Path

# ============== SERVER SETTINGS ==============

# Server host and port
SERVER_HOST = "127.0.0.1"  # localhost only (internal)
SERVER_PORT = 8000         # Change if port is in use (e.g., 8001, 8002)

# Auto-open browser after server starts
AUTO_OPEN_BROWSER = True
BROWSER_OPEN_DELAY = 3     # seconds before opening browser

# Auto-launch on startup
AUTO_START_SERVER = True

# ============== DATABASE SETTINGS ==============

# Database location (relative to app root)
DB_RELATIVE_PATH = "data/fabric.db"

# Auto-create database if missing
AUTO_CREATE_DB = True

# Enable database backup on startup
AUTO_BACKUP_DB = True
BACKUP_DIR = "data/backups"

# Database schema version
DB_SCHEMA_VERSION = "3.1"  # Supports bank statements

# ============== LOGGING SETTINGS ==============

LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR

# Save logs to file
SAVE_LOGS = True
LOG_FILE = "data/app.log"
LOG_MAX_SIZE = 10  # MB - rotate when reaches this size
LOG_BACKUP_COUNT = 5  # Keep last 5 logs

# ============== SECURITY SETTINGS ==============

# Restrict to localhost only (no network access from other machines)
LOCALHOST_ONLY = True

# Session timeout (minutes)
SESSION_TIMEOUT = 480  # 8 hours

# Enable HTTPS (requires certificate) - set to False for localhost
ENABLE_HTTPS = False

# Password protection (optional, set to None to disable)
REQUIRE_PASSWORD = False
DEFAULT_PASSWORD = "fabric123"  # Change this!

# ============== UI SETTINGS ==============

# Application name shown in browser title
APP_NAME = "Fabric Inventory Manager"

# Application version
APP_VERSION = "3.1.0"

# Theme: "light", "dark", or "auto"
THEME = "auto"

# Default currency
CURRENCY = "₹"  # Rupees
CURRENCY_SYMBOL = "₹"
CURRENCY_CODE = "INR"

# ============== FEATURES ==============

# Enable bank statement module
ENABLE_BANK_STATEMENTS = True

# Enable payment tracking
ENABLE_PAYMENT_TRACKING = True

# Enable ledger system
ENABLE_LEDGER = True

# Enable tax calculation
ENABLE_TAX = True
DEFAULT_TAX_RATE = 18  # percent

# Enable PDF export
ENABLE_PDF_EXPORT = True

# Enable CSV export
ENABLE_CSV_EXPORT = True

# ============== PERFORMANCE ==============

# Number of records per page
RECORDS_PER_PAGE = 20

# Enable query caching
ENABLE_CACHE = True
CACHE_TTL = 300  # seconds

# Enable debug mode (set to False in production)
DEBUG_MODE = False

# ============== BACKUP & RECOVERY ==============

# Auto-backup interval (hours)
AUTO_BACKUP_INTERVAL = 24

# Number of auto-backups to keep
MAX_AUTO_BACKUPS = 30

# Backup location
BACKUP_LOCATION = "data/backups"

# ============== ADVANCED ==============

# Max file upload size (MB)
MAX_UPLOAD_SIZE = 50

# Request timeout (seconds)
REQUEST_TIMEOUT = 30

# Connection pool size
CONNECTION_POOL_SIZE = 20

# Worker threads
WORKER_THREADS = 4

# ============== PORTABLE SPECIFIC ==============

# Run as service (Windows)
RUN_AS_SERVICE = False
SERVICE_NAME = "FabricInventoryManager"

# Update check (connects to internet)
CHECK_FOR_UPDATES = False

# Analytics (no data sent, local tracking only)
ENABLE_ANALYTICS = True

# Crash reporting
ENABLE_CRASH_REPORTS = False

# ============== DEVELOPMENT ==============

# Reload on code changes (development only)
RELOAD_ON_CHANGE = False

# Show detailed errors (development only)
DETAILED_ERRORS = False

# Enable Swagger UI at /docs
ENABLE_SWAGGER = True

# Enable ReDoc at /redoc
ENABLE_REDOC = False

# ============== INTEGRATION ==============

# Support email for error reports
SUPPORT_EMAIL = "support@fabricmanager.local"

# Contact information
CONTACT_PHONE = ""
CONTACT_ADDRESS = ""

# Company/Organization name
ORG_NAME = ""

# ============== DEPLOYMENT ==============

# Deployment type: "portable", "docker", "windows_service", "cloud"
DEPLOYMENT_TYPE = "portable"

# Environment: "development", "staging", "production"
ENVIRONMENT = "production"  # Set to production for portable

# Machine name (for multi-instance deployment)
MACHINE_ID = os.environ.get('COMPUTERNAME', 'default')

# ============== HELPER FUNCTIONS ==============

def get_app_config():
    """Get current configuration as dictionary"""
    return {
        'server_host': SERVER_HOST,
        'server_port': SERVER_PORT,
        'auto_open_browser': AUTO_OPEN_BROWSER,
        'browser_delay': BROWSER_OPEN_DELAY,
        'db_path': DB_RELATIVE_PATH,
        'app_name': APP_NAME,
        'app_version': APP_VERSION,
        'currency': CURRENCY,
        'theme': THEME,
        'debug': DEBUG_MODE,
        'features': {
            'bank_statements': ENABLE_BANK_STATEMENTS,
            'payments': ENABLE_PAYMENT_TRACKING,
            'ledger': ENABLE_LEDGER,
            'tax': ENABLE_TAX,
            'pdf_export': ENABLE_PDF_EXPORT,
            'csv_export': ENABLE_CSV_EXPORT,
        }
    }

def validate_config():
    """Validate configuration settings"""
    errors = []
    
    if not isinstance(SERVER_PORT, int) or SERVER_PORT < 1024 or SERVER_PORT > 65535:
        errors.append(f"Invalid SERVER_PORT: {SERVER_PORT} (must be 1024-65535)")
    
    if not isinstance(SESSION_TIMEOUT, int) or SESSION_TIMEOUT < 1:
        errors.append(f"Invalid SESSION_TIMEOUT: {SESSION_TIMEOUT}")
    
    if not isinstance(DEFAULT_TAX_RATE, (int, float)) or DEFAULT_TAX_RATE < 0 or DEFAULT_TAX_RATE > 100:
        errors.append(f"Invalid DEFAULT_TAX_RATE: {DEFAULT_TAX_RATE}")
    
    if not isinstance(RECORDS_PER_PAGE, int) or RECORDS_PER_PAGE < 1:
        errors.append(f"Invalid RECORDS_PER_PAGE: {RECORDS_PER_PAGE}")
    
    return errors

# Run validation on import
if __name__ == "__main__":
    errors = validate_config()
    if errors:
        print("Configuration errors found:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("Configuration is valid")
        config = get_app_config()
        print("\nCurrent Configuration:")
        for key, value in config.items():
            if isinstance(value, dict):
                print(f"  {key}:")
                for k, v in value.items():
                    print(f"    - {k}: {v}")
            else:
                print(f"  {key}: {value}")
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
