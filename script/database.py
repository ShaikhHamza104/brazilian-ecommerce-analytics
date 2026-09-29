# scripts/database.py

import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError


def load_table(
    table_name: str,
    chunk_size: int = 50_000,
) -> pd.DataFrame:
    """Load a MySQL table into a Pandas DataFrame using chunks.

    Reading the table in chunks helps reduce memory usage while
    fetching large tables from the database.

    Args:
        table_name: Name of the MySQL table.
        chunk_size: Number of rows to fetch per chunk.

    Returns:
        A Pandas DataFrame containing all rows from the table.

    Raises:
        ValueError: If table name or chunk_size is invalid.
        SQLAlchemyError: If the database operation fails.
    """
    if not table_name:
        raise ValueError("Table name cannot be empty.")

    if chunk_size <= 0:
        raise ValueError("chunk size must be greater than zero.")

    load_dotenv()

    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT", "3306")
    db_name = os.getenv("DB_NAME")

    connection_url = (
        f"mysql+pymysql://{db_user}:{db_password}"
        f"@{db_host}:{db_port}/{db_name}"
    )

    try:
        engine = create_engine(
            connection_url,
            connect_args={"ssl": {}},
            echo=False,
        )

        query = f"SELECT * FROM `{table_name}`"

        chunks = pd.read_sql(
            query,
            engine,
            chunksize=chunk_size,
        )

        return pd.concat(chunks, ignore_index=True)

    except SQLAlchemyError as err:
        print(f"Database operation failed: {err}")
        raise
