"""Database connection and engine management."""

import logging
from pathlib import Path
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from e_commerce_sales_analysis.config import DB_SSL_CA, get_db_url

logger = logging.getLogger(__name__)


def get_engine() -> Engine:
    """Create a SQLAlchemy engine with connection pooling and SSL."""
    connect_args = {}
    if DB_SSL_CA and Path(DB_SSL_CA).is_file():
        connect_args = {"ssl": {"ca": DB_SSL_CA}}
    return create_engine(
        get_db_url(), connect_args=connect_args, pool_pre_ping=True, pool_recycle=3600
    )


def ping_connection(engine: Engine | None = None) -> bool:
    """Verify active database connectivity with a lightweight ping query."""
    eng = engine or get_engine()
    try:
        with eng.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True

    except SQLAlchemyError as exc:
        logger.error("Database connection failed: %s", exc)
        return False
