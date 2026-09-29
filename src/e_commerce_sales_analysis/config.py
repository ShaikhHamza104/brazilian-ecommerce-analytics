"""Project configuration and path resolution."""

import os
from pathlib import Path
from urllib.parse import quote_plus
from dotenv import load_dotenv

# Project Root: 3 levels up from this file
# (config.py -> e_commerce_sales_analysis -> src -> ROOT)
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Load environment variables from .env file
load_dotenv(PROJECT_ROOT / ".env")


# Directory Paths
DATA_DIR = PROJECT_ROOT / "data"
DATA_RAW_DIR = DATA_DIR / "raw"
DATA_PROCESSED_DIR = DATA_DIR / "processed"
SQL_DIR = PROJECT_ROOT / "sql"
DOCS_DIR = PROJECT_ROOT / "docs"


# Database Credentials
DB_USER = os.getenv("DB_USER", "")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_NAME = os.getenv("DB_NAME", "")
DB_SSL_CA = os.getenv("DB_SSL_CA", "")

def get_db_url() -> str:
    """Construct a safe MySQL SQLAlchemy connection URL with encoded credentials."""
    encoded_user = quote_plus(DB_USER)
    encoded_password = quote_plus(DB_PASSWORD)
    return (
        f"mysql+pymysql://{encoded_user}:{encoded_password}"
        f"@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
    )
