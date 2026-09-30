"""Olist E-commerce MySQL Database Exporter.

Imports Olist CSV datasets into MySQL with schema initialization,
chunked batch loading, deduplication, and status reporting.
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote_plus

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.exc import SQLAlchemyError

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class TableConfig:
    """Mapping of a CSV dataset to a MySQL database table."""

    csv_file: str
    table_name: str
    pk_cols: list[str] | None = None
    date_cols: list[str] | None = None
    ddl: str | None = None


TABLE_CONFIGS: Sequence[TableConfig] = (
    TableConfig(
        csv_file="olist_customers_dataset.csv",
        table_name="olist_customers",
        pk_cols=["customer_id"],
        ddl="""
        CREATE TABLE IF NOT EXISTS olist_customers (
            customer_id VARCHAR(50) PRIMARY KEY,
            customer_unique_id VARCHAR(50),
            customer_zip_code_prefix CHAR(5),
            customer_city VARCHAR(100),
            customer_state VARCHAR(10)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """,
    ),
    TableConfig(
        csv_file="olist_sellers_dataset.csv",
        table_name="olist_sellers",
        pk_cols=["seller_id"],
        ddl="""
        CREATE TABLE IF NOT EXISTS olist_sellers (
            seller_id VARCHAR(50) PRIMARY KEY,
            seller_zip_code_prefix CHAR(5),
            seller_city VARCHAR(100),
            seller_state VARCHAR(10)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """,
    ),
    TableConfig(
        csv_file="product_category_name_translation.csv",
        table_name="product_category_name_translation",
        pk_cols=["product_category_name"],
        ddl="""
        CREATE TABLE IF NOT EXISTS product_category_name_translation (
            product_category_name VARCHAR(100) PRIMARY KEY,
            product_category_name_english VARCHAR(100)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """,
    ),
    TableConfig(
        csv_file="olist_products_dataset.csv",
        table_name="olist_products",
        pk_cols=["product_id"],
        ddl="""
        CREATE TABLE IF NOT EXISTS olist_products (
            product_id VARCHAR(50) PRIMARY KEY,
            product_category_name VARCHAR(100) NULL,
            product_name_lenght FLOAT NULL,
            product_description_lenght FLOAT NULL,
            product_photos_qty FLOAT NULL,
            product_weight_g FLOAT NULL,
            product_length_cm FLOAT NULL,
            product_height_cm FLOAT NULL,
            product_width_cm FLOAT NULL,
            CONSTRAINT fk_products_category
                FOREIGN KEY (product_category_name)
                REFERENCES product_category_name_translation(product_category_name)
                ON DELETE SET NULL ON UPDATE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """,
    ),
    TableConfig(
        csv_file="olist_geolocation_dataset.csv",
        table_name="olist_geolocation",
        pk_cols=None,
        ddl="""
        CREATE TABLE IF NOT EXISTS olist_geolocation (
            geolocation_id INT AUTO_INCREMENT PRIMARY KEY,
            geolocation_zip_code_prefix CHAR(5),
            geolocation_lat DOUBLE NULL,
            geolocation_lng DOUBLE NULL,
            geolocation_city VARCHAR(100),
            geolocation_state VARCHAR(10)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """,
    ),
    TableConfig(
        csv_file="olist_orders_dataset.csv",
        table_name="olist_orders",
        pk_cols=["order_id"],
        date_cols=[
            "order_purchase_timestamp",
            "order_approved_at",
            "order_delivered_carrier_date",
            "order_delivered_customer_date",
            "order_estimated_delivery_date",
        ],
        ddl="""
        CREATE TABLE IF NOT EXISTS olist_orders (
            order_id VARCHAR(50) PRIMARY KEY,
            customer_id VARCHAR(50),
            order_status VARCHAR(50),
            order_purchase_timestamp DATETIME NULL,
            order_approved_at DATETIME NULL,
            order_delivered_carrier_date DATETIME NULL,
            order_delivered_customer_date DATETIME NULL,
            order_estimated_delivery_date DATETIME NULL,
            CONSTRAINT fk_orders_customer
                FOREIGN KEY (customer_id)
                REFERENCES olist_customers(customer_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """,
    ),
    TableConfig(
        csv_file="olist_order_items_dataset.csv",
        table_name="olist_order_items",
        pk_cols=["order_id", "order_item_id"],
        date_cols=["shipping_limit_date"],
        ddl="""
        CREATE TABLE IF NOT EXISTS olist_order_items (
            order_id VARCHAR(50),
            order_item_id INT,
            product_id VARCHAR(50),
            seller_id VARCHAR(50),
            shipping_limit_date DATETIME NULL,
            price DECIMAL(10, 2) NULL,
            freight_value DECIMAL(10, 2) NULL,
            PRIMARY KEY (order_id, order_item_id),
            CONSTRAINT fk_items_order FOREIGN KEY (order_id) REFERENCES olist_orders(order_id),
            CONSTRAINT fk_items_product FOREIGN KEY (product_id) REFERENCES olist_products(product_id),
            CONSTRAINT fk_items_seller FOREIGN KEY (seller_id) REFERENCES olist_sellers(seller_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """,
    ),
    TableConfig(
        csv_file="olist_order_payments_dataset.csv",
        table_name="olist_order_payments",
        pk_cols=None,
        ddl="""
        CREATE TABLE IF NOT EXISTS olist_order_payments (
            payment_id INT AUTO_INCREMENT PRIMARY KEY,
            order_id VARCHAR(50),
            payment_sequential INT,
            payment_type VARCHAR(50),
            payment_installments INT,
            payment_value DECIMAL(10, 2) NULL,
            CONSTRAINT fk_payments_order FOREIGN KEY (order_id) REFERENCES olist_orders(order_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """,
    ),
    TableConfig(
        csv_file="olist_order_reviews_dataset.csv",
        table_name="olist_order_reviews",
        pk_cols=["review_id", "order_id"],
        date_cols=["review_creation_date", "review_answer_timestamp"],
        ddl="""
        CREATE TABLE IF NOT EXISTS olist_order_reviews (
            review_id VARCHAR(50),
            order_id VARCHAR(50),
            review_score INT,
            review_comment_title TEXT NULL,
            review_comment_message TEXT NULL,
            review_creation_date DATETIME NULL,
            review_answer_timestamp DATETIME NULL,
            PRIMARY KEY (review_id, order_id),
            CONSTRAINT fk_reviews_order FOREIGN KEY (order_id) REFERENCES olist_orders(order_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """,
    ),
)


def _dedupe(df: pd.DataFrame, pk_cols: list[str] | None, table_name: str) -> pd.DataFrame:
    """Drop duplicate rows matching primary key columns."""
    if not pk_cols:
        return df
    clean_df = df.drop_duplicates(subset=pk_cols)
    dropped = len(df) - len(clean_df)
    if dropped > 0:
        logger.warning(
            "Dropped %s duplicate(s) from '%s' on %s.",
            f"{dropped:,}",
            table_name,
            pk_cols,
        )
    return clean_df


def _add_missing_categories(df: pd.DataFrame, table_name: str) -> pd.DataFrame:
    """Add unmapped product categories so foreign key integrity never breaks."""
    if table_name == "product_category_name_translation":
        missing = pd.DataFrame([
            {"product_category_name": "pc_gamer", "product_category_name_english": "pc_gamer"},
            {
                "product_category_name": "portateis_cozinha_e_preparadores_de_alimentos",
                "product_category_name_english": "kitchen_and_food_preparation_appliances",
            },
        ])
        df = pd.concat([df, missing], ignore_index=True).drop_duplicates(subset=["product_category_name"])
    return df


def _trim_category_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Trim leading and trailing whitespace from category columns."""
    for col in ("product_category_name", "product_category_name_english"):
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().replace("nan", None)
    return df


def _zero_pad_zip_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Pad postal code prefixes with leading zeros to maintain 5 digits."""
    zip_cols = ("customer_zip_code_prefix", "seller_zip_code_prefix", "geolocation_zip_code_prefix")
    for col in zip_cols:
        if col in df.columns:
            nums = pd.to_numeric(df[col], errors="coerce").dropna().astype("int64").astype(str).str.zfill(5)
            df[col] = nums.reindex(df.index)
    return df


def _parse_date_columns(df: pd.DataFrame, date_cols: list[str] | None) -> pd.DataFrame:
    """Convert date columns to valid datetime objects."""
    if date_cols:
        for col in date_cols:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce")
    return df


class MySQLExporter:
    """Manages database connection, schema creation, and dataset loading."""

    def __init__(self, data_dir: Path | None = None) -> None:
        """Initialize engine and resolve path to raw data directory."""
        project_root = Path(__file__).resolve().parent.parent
        self.data_dir = data_dir or (project_root / "data" / "raw")
        self.engine = self._create_engine()

    @staticmethod
    def _create_engine() -> Engine:
        """Create SQLAlchemy MySQL engine using environment variables."""
        load_dotenv()
        user = os.getenv("DB_USER")
        pwd = os.getenv("DB_PASSWORD")
        host = os.getenv("DB_HOST")
        port = os.getenv("DB_PORT", "3306")
        db = os.getenv("DB_NAME")

        if not all([user, pwd, host, db]):
            raw_url = os.getenv("SQLALCHEMY_DATABASE_URI") or os.getenv("DATABASE_URL")
            if not raw_url:
                raise ValueError("Missing database credentials in .env")
            url = raw_url.replace("mysql://", "mysql+pymysql://", 1)
        else:
            safe_pwd = quote_plus(pwd) if pwd else ""
            url = f"mysql+pymysql://{user}:{safe_pwd}@{host}:{port}/{db}"

        return create_engine(url, connect_args={"ssl": {}}, echo=False)

    def test_connection(self) -> bool:
        """Verify database connectivity."""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1;"))
            logger.info("Successfully connected to MySQL database.")
            return True
        except SQLAlchemyError as exc:
            logger.error("Database connection failed: %s", exc)
            return False

    def init_schema(self) -> None:
        """Execute DDL statements to verify and create tables."""
        logger.info("Verifying database schema...")
        with self.engine.begin() as conn:
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
            try:
                for cfg in TABLE_CONFIGS:
                    if cfg.ddl:
                        conn.execute(text(cfg.ddl))
            finally:
                conn.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
        logger.info("Database schema verified.")

    def get_row_count(self, table_name: str) -> int | None:
        """Fetch current row count for a given table."""
        try:
            with self.engine.connect() as conn:
                return conn.execute(text(f"SELECT COUNT(*) FROM `{table_name}`")).scalar()
        except SQLAlchemyError:
            return None

    def show_status(self) -> None:
        """Display formatted comparison of CSV rows vs MySQL rows."""
        header = f"{'Table Name':<35} | {'CSV Rows':<10} | {'DB Rows':<10} | {'Status'}"
        sep = "-" * len(header)
        print(f"\n{sep}\n{header}\n{sep}")

        for cfg in TABLE_CONFIGS:
            path = self.data_dir / cfg.csv_file
            if path.exists():
                df_temp = pd.read_csv(str(path))
                df_temp = _add_missing_categories(df_temp, cfg.table_name)
                clean_temp = df_temp.drop_duplicates(subset=cfg.pk_cols) if cfg.pk_cols else df_temp
                csv_count = len(clean_temp)
            else:
                csv_count = 0

            db_count = self.get_row_count(cfg.table_name)
            if db_count is None:
                status = "TABLE MISSING"
            elif csv_count == db_count:
                status = "UP TO DATE"
            elif db_count == 0:
                status = "EMPTY (PENDING)"
            else:
                status = f"MISMATCH ({db_count}/{csv_count})"

            db_str = f"{db_count:,}" if db_count is not None else "N/A"
            print(f"{cfg.table_name:<35} | {csv_count:<10,} | {db_str:<10} | {status}")

        print(f"{sep}\n")

    def _truncate_table(self, table_name: str) -> None:
        """Safely truncate all rows from a table."""
        logger.info("Truncating table '%s'...", table_name)
        with self.engine.begin() as conn:
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
            try:
                conn.execute(text(f"TRUNCATE TABLE `{table_name}`;"))
            except SQLAlchemyError:
                conn.execute(text(f"DELETE FROM `{table_name}`;"))
            finally:
                conn.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))

    def import_table(
        self,
        config: TableConfig,
        force: bool = False,
        chunksize: int = 5000,
    ) -> bool:
        """Import a CSV dataset into its MySQL table in batches."""
        csv_path = self.data_dir / config.csv_file
        if not csv_path.exists():
            logger.error("File not found: %s", csv_path)
            return False

        db_count = self.get_row_count(config.table_name)
        logger.info("Processing %s (%s)...", config.table_name, config.csv_file)

        df = pd.read_csv(str(csv_path))
        df = _add_missing_categories(df, config.table_name)
        df = _dedupe(df, config.pk_cols, config.table_name)
        total_rows = len(df)

        if db_count is not None and db_count >= total_rows and not force:
            logger.info("Table '%s' already contains %s records. Skipping.", config.table_name, f"{db_count:,}")
            return True

        if db_count and db_count > 0:
            if force:
                self._truncate_table(config.table_name)
            else:
                logger.warning(
                    "Table '%s' has %s records. Use --force to reload. Skipping.",
                    config.table_name,
                    f"{db_count:,}",
                )
                return False

        # Transform data before loading
        df = _trim_category_columns(df)
        df = _zero_pad_zip_columns(df)
        df = _parse_date_columns(df, config.date_cols)
        df = df.where(pd.notnull(df), None)

        num_chunks = (total_rows + chunksize - 1) // chunksize
        logger.info("Importing %s rows into '%s' in %s chunk(s)...", f"{total_rows:,}", config.table_name, num_chunks)

        try:
            with self.engine.begin() as conn:
                conn.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
                try:
                    for i in range(0, total_rows, chunksize):
                        chunk = df.iloc[i:i + chunksize]
                        chunk.to_sql(
                            name=config.table_name,
                            con=conn,
                            if_exists="append",
                            index=False,
                            method="multi",
                        )
                        current = min(i + chunksize, total_rows)
                        pct = (current / total_rows) * 100
                        logger.info("  [%s] %s/%s rows (%.1f%%)", config.table_name, f"{current:,}", f"{total_rows:,}", pct)
                finally:
                    conn.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
        except Exception as exc:
            logger.error("Failed to import '%s': %s", config.table_name, exc)
            return False

        final_count = self.get_row_count(config.table_name)
        final_str = f"{final_count:,}" if final_count is not None else "N/A"
        logger.info("Finished '%s'. Rows in DB: %s", config.table_name, final_str)
        return True


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Export Olist E-commerce CSV datasets to MySQL.")
    parser.add_argument("--table", "-t", help="Target specific table name or CSV to import.", default=None)
    parser.add_argument("--force", "-f", help="Force truncate and re-import existing data.", action="store_true")
    parser.add_argument("--status", "-s", help="Display dataset status table and exit.", action="store_true")
    parser.add_argument("--chunksize", "-c", help="Batch size for bulk insertion (default: 5000).", type=int, default=5000)
    return parser.parse_args()


def main() -> None:
    """Entry point for command-line execution."""
    args = parse_args()

    try:
        exporter = MySQLExporter()
    except ValueError as err:
        logger.error(err)
        sys.exit(1)

    if not exporter.test_connection():
        sys.exit(1)

    if args.status:
        exporter.show_status()
        return

    exporter.init_schema()

    configs = TABLE_CONFIGS
    if args.table:
        target = args.table.lower().strip()
        configs = [cfg for cfg in TABLE_CONFIGS if target in (cfg.table_name.lower(), cfg.csv_file.lower())]
        if not configs:
            logger.error("No dataset matches '--table %s'.", args.table)
            sys.exit(1)

    for cfg in configs:
        exporter.import_table(config=cfg, force=args.force, chunksize=args.chunksize)

    logger.info("Import workflow complete.")
    exporter.show_status()


if __name__ == "__main__":
    main()
