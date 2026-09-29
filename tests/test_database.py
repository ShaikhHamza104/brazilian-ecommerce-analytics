import pandas as pd
import pytest
from sqlalchemy import text

from e_commerce_sales_analysis.db import load_table

def test_empty_table_name():
    with pytest.raises(ValueError):
        load_table("")


def test_invalid_chunk_size():
    with pytest.raises(ValueError):
        load_table("olist_customers", chunk_size=0)


def test_load_table_success():
    """Verify loading a small table returns a valid DataFrame."""
    df = load_table("product_category_name_translation")
    assert isinstance(df, pd.DataFrame)
    assert not df.empty


@pytest.mark.parametrize(
    "table_name",
    [
        "olist_customers",
        "olist_geolocation",
        "olist_order_items",
        "olist_order_payments",
        "olist_order_reviews",
        "olist_orders",
        "olist_products",
        "olist_sellers",
        "product_category_name_translation",
    ],
)
def test_tables_have_data(db_engine, table_name):
    """Ensure each table in MySQL has at least one record."""
    with db_engine.connect() as conn:
        row = conn.execute(text(f"SELECT 1 FROM `{table_name}` LIMIT 1;")).fetchone()
        assert row is not None, f"Table '{table_name}' has no data"
