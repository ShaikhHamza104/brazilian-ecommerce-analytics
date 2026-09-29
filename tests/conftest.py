import os

from dotenv import load_dotenv
import pytest
from sqlalchemy import create_engine

load_dotenv()


@pytest.fixture(scope="session")
def db_engine():
    """Shared database engine for tests."""
    user = os.getenv("DB_USER")
    pwd = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT", "3306")
    db = os.getenv("DB_NAME")

    url = f"mysql+pymysql://{user}:{pwd}@{host}:{port}/{db}"
    return create_engine(url, connect_args={"ssl": {}}, echo=False)
