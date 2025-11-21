"""
Portable Fabric Inventory Management System
Single executable entry point that bundles everything
"""

import os
import sys
import time
import threading
import webbrowser
import logging
from pathlib import Path
from datetime import datetime
from io import StringIO

# Fix stdin/stdout for PyInstaller
if not hasattr(sys.stdin, 'isatty'):
    sys.stdin = StringIO()
if not hasattr(sys.stdout, 'isatty'):
    sys.stdout = StringIO()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_app_root():
    """Get the root directory of the application"""
    if getattr(sys, 'frozen', False):
        # Running as executable
        app_root = os.path.dirname(sys.executable)
    else:
        # Running as script
        app_root = os.path.dirname(os.path.abspath(__file__))
    return app_root

def setup_environment():
    """Setup the environment for the portable app"""
    app_root = get_app_root()
    
    # Set working directory
    os.chdir(app_root)
    sys.path.insert(0, app_root)
    
    # Create data directory if it doesn't exist
    data_dir = os.path.join(app_root, 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    # Ensure database is in the data directory
    db_path = os.path.join(data_dir, 'fabric.db')
    # Convert to forward slashes for SQLite compatibility
    db_path = db_path.replace('\\', '/')
    os.environ['DB_PATH'] = db_path
    
    # Create/ensure templates and static directories exist
    templates_dir = os.path.join(app_root, 'templates')
    static_dir = os.path.join(app_root, 'static')
    
    os.makedirs(templates_dir, exist_ok=True)
    os.makedirs(static_dir, exist_ok=True)
    
    # Set environment variables for paths
    os.environ['TEMPLATES_DIR'] = templates_dir
    os.environ['STATIC_DIR'] = static_dir
    
    logger.info(f"App Root: {app_root}")
    logger.info(f"Database Path: {db_path}")
    logger.info(f"Templates Dir: {templates_dir}")
    logger.info(f"Static Dir: {static_dir}")
    logger.info(f"Templates exist: {os.path.exists(templates_dir)}")
    logger.info(f"Static exist: {os.path.exists(static_dir)}")
    
    return app_root

def open_browser(url, delay=2):
    """Open browser after delay to allow server to start"""
    def _open():
        time.sleep(delay)
        try:
            webbrowser.open(url)
            logger.info(f"Browser opened: {url}")
        except Exception as e:
            logger.error(f"Failed to open browser: {e}")
    
    thread = threading.Thread(target=_open, daemon=True)
    thread.start()

def verify_assets():
    """Verify all required assets are present"""
    app_root = get_app_root()
    
    required_dirs = ['templates', 'static', 'data']
    required_files = {
        'templates': ['base.html', 'index.html'],
        'static': ['styles.css']
    }
    
    logger.info("Verifying application assets...")
    
    for dir_name in required_dirs:
        dir_path = os.path.join(app_root, dir_name)
        if not os.path.exists(dir_path):
            logger.warning(f"Creating missing directory: {dir_name}")
            os.makedirs(dir_path, exist_ok=True)
    
    for dir_name, files in required_files.items():
        for file_name in files:
            file_path = os.path.join(app_root, dir_name, file_name)
            if not os.path.exists(file_path):
                logger.warning(f"Missing file: {dir_name}/{file_name}")
    
    logger.info("Asset verification complete")

def run_server():
    """Run the FastAPI server"""
    import uvicorn
    from main import app
    
    # Try to load config from portable_config.py
    try:
        from portable_config import SERVER_HOST, SERVER_PORT, AUTO_OPEN_BROWSER, BROWSER_OPEN_DELAY
        HOST = SERVER_HOST
        PORT = SERVER_PORT
        AUTO_BROWSER = AUTO_OPEN_BROWSER
        BROWSER_DELAY = BROWSER_OPEN_DELAY
    except ImportError:
        HOST = "127.0.0.1"
        PORT = 8000
        AUTO_BROWSER = True
        BROWSER_DELAY = 3
    
    URL = f"http://{HOST}:{PORT}"
    
    logger.info("=" * 60)
    logger.info("FABRIC INVENTORY MANAGEMENT SYSTEM - PORTABLE")
    logger.info("=" * 60)
    logger.info(f"Starting server at {URL}")
    logger.info("Server is starting, browser will open automatically...")
    logger.info("=" * 60)
    
    # Open browser after slight delay
    open_browser(URL, delay=3)
    
    # Run the server with logging config that handles PyInstaller environment
    try:
        # Disable Uvicorn's default logging config to avoid stdin issues
        uvicorn.run(
            app,
            host=HOST,
            port=PORT,
            log_level="info",
            access_log=True,
            use_colors=False  # Disable colors to avoid TTY issues
        )
    except (KeyboardInterrupt, RuntimeError) as e:
        logger.info(f"Server stopped: {e}")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)

def main():
    """Main entry point"""
    try:
        setup_environment()
        run_server()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
