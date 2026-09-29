"""Database table and query loading utilities."""

import re
import pandas as pd
from sqlalchemy import Engine,text

from .connection import get_engine

_VALID_TABLE_REGEX = re.compile(r"^[a-zA-Z0-9_]+$")

def load_table(
    table_name: str,
    chunk_size: int = 50_000,
    engine: Engine | None = None,
) -> pd.DataFrame:
    """Load a MySQL table into a DataFrame using chunked reading.
    Args:
        table_name: Name of the table to load.
        chunk_size: Number of rows per batch to prevent memory spikes.
        engine: Optional SQLAlchemy engine. Uses default engine if None.
    Returns:
        pd.DataFrame containing all rows from the table.
    """
    if not table_name or not table_name.strip():
        raise ValueError("Table name cannot be empty.")

    if not _VALID_TABLE_REGEX.match(table_name):
        raise ValueError(
            f"Invalid table name: '{table_name}'. Only alphanumeric characters and underscores allowed."
        )
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero.")
    eng = engine or get_engine()
    query = f"SELECT * FROM `{table_name}`"
    chunks = pd.read_sql(query, con=eng, chunksize=chunk_size)
    return pd.concat(chunks, ignore_index=True)


def query_to_dataframe(
    query: str,
    params: dict | None = None,
    engine: Engine | None = None,
) -> pd.DataFrame:
    """Execute a custom SQL query and return the result as a DataFrame."""
    if not query or not query.strip():
        raise ValueError("SQL query cannot be empty.")
    eng = engine or get_engine()
    with eng.connect() as conn:
        return pd.read_sql(text(query), con=conn, params=params)
