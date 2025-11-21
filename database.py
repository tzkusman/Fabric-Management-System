from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from urllib.parse import quote

# Get database path from environment or use default
db_path = os.environ.get('DB_PATH', './fabric.db')

# Handle path encoding for SQLite with spaces and special characters
# Convert backslashes to forward slashes (for Windows)
db_path = db_path.replace('\\', '/')

# For absolute Windows paths (starting with C:/, D:/, etc.), we need proper SQLite URL encoding
# SQLite URL format: sqlite:///path/to/db.db (note the 3 slashes for absolute paths on Windows)
# But we need to handle spaces and special characters
if ':' in db_path and not db_path.startswith('sqlite'):
    # This is an absolute Windows path like G:/fabric inventory_V2/...
    # Use the file:// protocol with proper encoding
    # First, ensure the path can be safely used in URLs
    try:
        # Try to create the URL properly
        SQLALCHEMY_DATABASE_URL = f"sqlite:///{quote(db_path, safe=':/')}"
    except Exception:
        # Fallback to simple sqlite:/// prefix
        SQLALCHEMY_DATABASE_URL = f"sqlite:///{db_path}"
else:
    # Relative path
    SQLALCHEMY_DATABASE_URL = f"sqlite:///{db_path}"

print(f"DATABASE URL: {SQLALCHEMY_DATABASE_URL}", flush=True)

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
