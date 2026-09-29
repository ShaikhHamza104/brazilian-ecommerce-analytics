# 📊 Brazilian E-Commerce (Olist) Sales & Customer Intelligence Platform

[![Python Version](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![Database](https://img.shields.io/badge/Database-MySQL%208.0-orange.svg)](https://www.mysql.com/)
[![Package Manager](https://img.shields.io/badge/Package%20Manager-uv-purple.svg)](https://github.com/astral-sh/uv)
[![Testing](https://img.shields.io/badge/Tests-19%20Passed%20(pytest)-brightgreen.svg)]()
[![Data Stack](https://img.shields.io/badge/Stack-Pandas%20%7C%20SQLAlchemy%20%7C%20PyArrow%20%7C%20Power%20BI-green.svg)]()

> **An end-to-end data analytics and business intelligence solution built on the Brazilian E-Commerce Public Dataset by Olist (~100,000 orders).**  
> **Author:** Mohd Hamza Shaikh  
> **Target Domain:** Data Analyst / Data Scientist / Product & Business Analyst  

---

## 📖 Table of Contents
- [Project Overview & Origin](#-project-overview--origin)
- [Advanced Data Integrity & Edge-Case Preservations](#-advanced-data-integrity--edge-case-preservations)
- [Architectural Pipeline & Star Schema](#-architectural-pipeline--star-schema)
- [Production SQL Layer](#-production-sql-layer)
  - [Analytical Database Views (`sql/views/`)](#1-analytical-database-views-sqlviews)
  - [Deep-Dive Business Queries (`sql/analytics/`)](#2-deep-dive-business-queries-sqlanalytics)
- [Key Business Insights & Discoveries](#-key-business-insights--discoveries)
- [Repository Structure](#-repository-structure)
- [Testing & Quality Assurance](#-testing--quality-assurance)
- [Installation & Quick Start](#-installation--quick-start)
- [Roadmap & Next Steps](#-roadmap--next-steps)
- [Author & Acknowledgments](#-author--acknowledgments)

---

## 🎯 Project Overview & Origin

This project originated as part of **Project 2 (E-Commerce Sales Analysis)** in the **Data Analytics Mentorship Program (DAMP 1.0 by CampusX)**. The curriculum established a strong core foundation across the end-to-end data lifecycle:
* Extracting transactional e-commerce data from relational databases using SQL.
* Preprocessing, cleaning, and transforming complex datasets using Python.
* Loading transformed tables into an analytical data warehouse structure.
* Creating interactive Power BI dashboards for sales analysis and executive decision-making.

### Where the Classroom Ends, Enterprise Investigation Begins
While standard course projects stop after basic descriptive statistics and initial charts, **I chose to take this project further into enterprise-grade analytics**.

In live business environments, an impactful Data Analyst or Data Scientist must understand the operational context behind the numbers. Real-world transactional datasets contain subtle domain nuances: in-flight orders, customer account tokens versus individual shoppers, geographic logistics divides, and platform merchant risks.

I expanded this project across five advanced enterprise dimensions:
1. **Critical Edge-Case Auditing:** Investigated real-world domain nuances that standard pipelines overlook, successfully preserving **2,965 non-delivered operational order records**, **23,000+ early-delivery items**, and **2,814 repeat customers ($861K+ in revenue)**.
2. **Modular Production Engineering:** Refactored one-off scripts into an installable Python package (`src/e_commerce_sales_analysis`) with connection pooling, automated chunked ingestion, Portuguese text normalization (`unidecode`), and a complete 19-test automated suite (`pytest`).
3. **Advanced SQL Analytical Views & Queries (MySQL 8.0):** Engineered production views and standalone analytics scripts leveraging **Common Table Expressions (CTEs)**, **Window Functions (`ROW_NUMBER()`, `SUM() OVER ()`, `LAG()`)**, and conditional classification (`CASE WHEN`).
4. **Customer & Merchant Diagnostics:** Built 6-month monthly cohort retention matrices, mapped the "Two Brazils" logistics inequality, and proved the Pareto 80/20 distribution across 3,053 merchants.
5. **Columnar Star Schema for BI & ML:** Transformed relational tables into an optimized dimensional model exported to columnar **Parquet** files (`dim_*` and `fact_*`), eliminating Cartesian join risks and preparing the data for predictive modeling.

---

## 🔬 Advanced Data Integrity & Edge-Case Preservations

During the exploratory data analysis phase, I audited data cleaning assumptions to ensure the dataset accurately reflected operational truth:

| # | Domain Nuance & Edge Case | Standard / Baseline Handling | My Production-Grade Solution & Value Preserved |
|---|---|---|---|
| **1** | **Customer Account vs. Unique Individual** | Using `customer_id` for both transactions and customer counting. | Differentiated `customer_id` (transaction token) from `customer_unique_id` (actual human buyer). Rescued all **3,345 repeat purchase events** across **2,814 repeat buyers** and proved repeat buyers spend **$305.99** vs. **$160.19** for one-time buyers. |
| **2** | **In-Flight & Canceled Shipments** | Naive date subtraction (`delivery - purchase >= 0`), which inadvertently drops rows where delivery date is `NULL`. | Scoped date integrity validation conditionally to `delivered` status only. Preserved **2,965 in-flight and non-delivered orders**, retaining full operational visibility into order cancellations, processing lag, and active shipments. |
| **3** | **Early Carrier Fulfillment** | Filtering out items where `shipping_limit_date < delivery_date` under the assumption of an invalid sequence. | Recognized that packages delivered *before* the seller dispatch deadline represent exceptional logistics performance. Preserved **23,000+ line items**. |
| **4** | **Financial Granularity (Items vs. Payments)** | Merging payments (1:M) and order items (1:N) directly into a single flat denormalized table. | Preserved accounting integrity by designing a **Star Schema** with separate Fact tables for Items and Payments, preventing Cartesian join inflation that artificially doubles revenue (verified via order `03ecec245220b63fd7f68c1737ba99ba`). |

---

## 🏗️ Architectural Pipeline & Star Schema

### Data Flow Pipeline

```mermaid
flowchart TD
    subgraph Raw Data [Source Data]
        CSV[9 Raw CSV Files\n~100,000 Orders]
    end

    subgraph Database Layer [MySQL 8.0 3NF Database]
        DDL["sql/ddl/01_schema.sql\n(Tables with Primary & Foreign Key Integrity)"]
        LOAD["script/export_to_mysql.py\n(Chunked Multi-Row Importer)"]
        VIEWS["sql/views/\n(vw_order_fulfillment, vw_customer_rfm, vw_sales_master)"]
    end

    subgraph Analytical Processing [Python & SQL Engine]
        EDA["notebook/01_eda_and_cleaning.ipynb\n(Bias Elimination, Portuguese Diacritics, Parquet Export)"]
        SQL_ANALYTICS["sql/analytics/\n(MoM Growth, Cohort Retention, Logistics, Pareto Tiers)"]
    end

    subgraph Presentation & Modeling [Downstream Layer]
        PARQUET["data/processed/\n(8 Star Schema Columnar Parquet Files)"]
        BI["Power BI Dashboards\n(Sales, Logistics & Customer Intelligence)"]
    end

    CSV --> LOAD --> DDL
    DDL --> VIEWS
    VIEWS --> SQL_ANALYTICS
    DDL --> EDA --> PARQUET
    PARQUET --> BI
    SQL_ANALYTICS --> BI
```

### Relational Entity-Relationship Diagram (ERD)

The complete 9-table relational schema is verified with proper Crow's Foot cardinality and zero orphan tables. You can review the full visual schema diagram in [docs/diagrams/databaseschema.png](file:///d:/E-commerce%20Sales%20Analysis/docs/diagrams/databaseschema.png).

```
[olist_customers] (1) ──────────── (N) [olist_orders] (1) ─── (N) [olist_order_items] (N) ─── (1) [olist_products]
                                         │            (1) ─── (N) [olist_order_payments]            │ (N)
                                         │            (1) ─── (N) [olist_order_reviews]             │
                                         │                                                          ▼ (1)
                                   (Ref Lookup)                                     [product_category_name_translation]
                                [olist_geolocation]
```

### Processed Analytical Star Schema (`data/processed/`)
- **Dimension Tables:** `dim_customers.parquet`, `dim_products.parquet`, `dim_sellers.parquet`, `dim_orders.parquet`, `dim_order_reviews.parquet`
- **Fact Tables:** `fact_order_items.parquet` (Grain: 1 row per product sold), `fact_order_payments.parquet` (Grain: 1 row per payment installment)
- **Analytical Master:** `olist_master_cleaned.parquet` (Unified line-item dataset for quick feature engineering)

---

## 💻 Production SQL Layer

### 1. Analytical Database Views (`sql/views/`)
- **[`vw_order_fulfillment.sql`](file:///d:/E-commerce%20Sales%20Analysis/sql/views/vw_order_fulfillment.sql):** Computes actual vs. estimated delivery duration, delay variance, and on-time delivery classification.
- **[`vw_customer_rfm.sql`](file:///d:/E-commerce%20Sales%20Analysis/sql/views/vw_customer_rfm.sql):** Dynamic Recency (days since snapshot), Frequency, and Monetary aggregation with loyalty tier tagging.
- **[`vw_sales_master.sql`](file:///d:/E-commerce%20Sales%20Analysis/sql/views/vw_sales_master.sql):** Unified line-item transaction view classifying routes (`Same State` vs. `Inter-State`) and joining seller/customer geography with review ratings.

### 2. Deep-Dive Business Queries (`sql/analytics/`)
- **[`01_monthly_revenue_growth_mom.sql`](file:///d:/E-commerce%20Sales%20Analysis/sql/analytics/01_monthly_revenue_growth_mom.sql):** Calculates Monthly GMV, order volume, Average Order Value (AOV), and Month-over-Month growth percentage via `LAG()`. Captures the November 2017 Black Friday revenue surge to **$1.17M**.
- **[`02_customer_cohort_retention.sql`](file:///d:/E-commerce%20Sales%20Analysis/sql/analytics/02_customer_cohort_retention.sql):** Tracks monthly customer acquisition cohorts over a 6-month window to calculate customer retention rates.
- **[`03_freight_and_delivery_delays_by_state.sql`](file:///d:/E-commerce%20Sales%20Analysis/sql/analytics/03_freight_and_delivery_delays_by_state.sql): Computes state-level logistics transit times, delay rates, freight-to-basket ratios, and average customer review scores.
- **[`04_seller_performance_and_concentration.sql`](file:///d:/E-commerce%20Sales%20Analysis/sql/analytics/04_seller_performance_and_concentration.sql):** Applies window functions (`SUM() OVER`) to segment merchants into Pareto Tiers, tracking revenue concentration and carrier dispatch speeds.

---

## 📈 Key Business Insights & Discoveries

### 1. Customer Loyalty & The Repeat Buyer Premium
- **One-Time Shoppers (92,867 customers):** Average spend of **$160.19**.
- **Repeat Shoppers (2,814 customers):** Average spend of **$305.99** (**+91% higher spend**).
- **Revenue Opportunity:** Repeat buyers generate **$861,063.72 in revenue** despite representing only 2.9% of the customer base.

### 2. The "Leaky Bucket" Cohort Retention Reality
- **Month 1 Retention:** Stays below **0.60% across all cohorts** (averaging ~0.40%).
- **Business Conclusion:** Olist is an acquisition-driven marketplace for durable, infrequent purchases (furniture, electronics, auto accessories). Because customer repeat rates are low, **Customer Acquisition Cost (CAC) must be amortized entirely on the first transaction**; the platform cannot operate on loss-leader first orders.

### 3. Supply Chain Disparities: "The Two Brazils"
- **Fulfillment Speed:** São Paulo (`SP`) averages **8.7 days** delivery turnaround with a **5.89%** delay rate. In contrast, Roraima (`RR`) averages **29.3 days** in transit.
- **The Freight Tax:** Northern and Northeastern customers pay nearly **3× more in freight** ($48.34 in `RR` vs $17.33 in `SP`), with shipping making up over **32% of total order cost**.
- **Customer Satisfaction Impact:** Alagoas (`AL`) suffers from a **23.9% late delivery rate**, dragging customer review scores down to **3.85 / 5.0**.

### 4. Merchant Pareto Concentration (The 80/20 Rule)
- **Top 18 Elite Sellers (0.59% of sellers):** Generate **20% of all marketplace GMV ($2.69M)**, averaging **$149,741/seller**.
- **Top 128 Core Sellers (4.19% of sellers):** Drive **50% of all marketplace GMV ($6.78M)**.
- **Top 539 Sellers (17.65% of sellers):** Drive **80% of total marketplace GMV ($10.84M)**.
- **Fulfillment Discipline:** Elite merchants maintain a late dispatch rate of **7.84%**, compared to **11.42%** among the 2,514 long-tail merchants.

---

## 📂 Repository Structure

```plaintext
E-commerce Sales Analysis/
├── data/
│   ├── raw/                 # 9 original source CSV datasets
│   └── processed/           # 8 production Parquet files (Star Schema)
├── docs/
│   ├── diagrams/            # databaseschema.png (Verified Crow's Foot ERD)
│   ├── olist_data_dictionary.pdf
│   └── project_showcase_notion.md      # Complete portfolio report & interview guide
├── notebook/
│   └── 01_eda_and_cleaning.ipynb  # Documented cleaning, diagnostics & Parquet exports
├── script/
│   └── export_to_mysql.py   # Multi-row batch CSV-to-MySQL ingestion CLI
├── sql/
│   ├── ddl/
│   │   └── 01_schema.sql    # 3NF relational schema DDL with PK/FK constraints
│   ├── views/
│   │   ├── vw_order_fulfillment.sql  # Delivery performance & delay classification
│   │   ├── vw_customer_rfm.sql        # Customer RFM metrics & loyalty tiers
│   │   └── vw_sales_master.sql        # Denormalized line-item sales with route tagging
│   └── analytics/
│       ├── 01_monthly_revenue_growth_mom.sql       # MoM GMV, volume & Black Friday
│       ├── 02_customer_cohort_retention.sql         # 6-month retention matrix
│       ├── 03_freight_and_delivery_delays_by_state.sql # State logistics & review score
│       └── 04_seller_performance_and_concentration.sql # Pareto 80/20 merchant analysis
├── src/e_commerce_sales_analysis/
│   ├── config.py            # Dynamic project root & settings
│   ├── db/
│   │   ├── connection.py    # SQLAlchemy connection pool with SSL & health-checks
│   │   └── loader.py        # Chunked database reader & query runner
│   └── cleaning/
│       └── text.py          # unidecode Brazilian diacritic normalization
├── tests/                   # 19 automated unit & integration tests (pytest)
├── pyproject.toml           # Project metadata & dependency definitions (uv managed)
└── README.md
```

---

## 🧪 Testing & Quality Assurance

The codebase includes an automated test suite executed via `pytest`. All 19 tests validate database connections, string cleaning routines, chunked loading logic, and data transformations.

```bash
uv run pytest -v tests
```

Output:
```plaintext
============================= test session starts =============================
platform win32 -- Python 3.11.16, pytest-9.1.1, pluggy-1.6.0
rootdir: D:\E-commerce Sales Analysis
configfile: pyproject.toml
collected 19 items

tests/test_cleaning.py::test_clean_city_state_suffix PASSED              [  5%]
tests/test_cleaning.py::test_clean_city_hyphen_and_spaces PASSED         [ 10%]
tests/test_cleaning.py::test_clean_city_accents PASSED                   [ 15%]
tests/test_cleaning.py::test_clean_city_nulls PASSED                     [ 21%]
tests/test_database.py::test_empty_table_name PASSED                     [ 26%]
tests/test_database.py::test_invalid_chunk_size PASSED                   [ 31%]
tests/test_database.py::test_load_table_success PASSED                   [ 36%]
tests/test_database.py::test_tables_have_data[olist_customers] PASSED    [ 42%]
tests/test_database.py::test_tables_have_data[olist_geolocation] PASSED  [ 47%]
tests/test_database.py::test_tables_have_data[olist_order_items] PASSED  [ 52%]
tests/test_database.py::test_tables_have_data[olist_order_payments] PASSED [ 57%]
tests/test_database.py::test_tables_have_data[olist_order_reviews] PASSED [ 63%]
tests/test_database.py::test_tables_have_data[olist_orders] PASSED       [ 68%]
tests/test_database.py::test_tables_have_data[olist_products] PASSED     [ 73%]
tests/test_database.py::test_tables_have_data[olist_sellers] PASSED      [ 78%]
tests/test_database.py::test_tables_have_data[product_category_name_translation] PASSED [ 84%]
tests/test_db_connection.py::test_database_connection PASSED             [ 89%]
tests/test_env.py::test_environment_variables PASSED                     [ 94%]
tests/test_optional_ssl.py::test_optional_ssl_certificate PASSED         [100%]

============================= 19 passed in 2.86s ==============================
```

---

## 🚀 Installation & Quick Start

### 1. Prerequisites
- **Python 3.11+**
- **MySQL Server 8.0+**
- [**uv**](https://github.com/astral-sh/uv) (recommended) or `pip`

### 2. Setup Environment
```bash
# Clone the repository
git clone https://github.com/ShaikhHamza104/brazilian-ecommerce-analytics.git
cd brazilian-ecommerce-analytics

# Create virtual environment and install dependencies via uv
uv sync
```

### 3. Configure Database
Create a `.env` file in the root directory (refer to `.env.sample`):
```ini
DB_USER=root
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306
DB_NAME=ecommerce_sales
```

Initialize the database schema:
```sql
CREATE DATABASE IF NOT EXISTS ecommerce_sales
CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 4. Ingest Raw Data
Import CSV datasets into MySQL using the chunked ingestion CLI:
```bash
uv run python script/export_to_mysql.py
```

### 5. Run Analytics Queries
You can run any of the analytical queries directly in your SQL client or via Python:
```bash
# Example: Run Customer Cohort Retention Analysis
uv run python -c "
from e_commerce_sales_analysis.db.connection import get_engine
import pandas as pd

engine = get_engine()
with open('sql/analytics/02_customer_cohort_retention.sql', 'r') as f:
    df = pd.read_sql(f.read(), engine)
print(df.head(10).to_string(index=False))
"
```

---

## 🗺️ Roadmap & Next Steps

- [x] Initial relational schema DDL with primary and foreign key constraints.
- [x] Chunked multi-row CSV-to-MySQL data ingestion engine.
- [x] Exploratory data analysis, bias elimination, and Parquet export pipeline.
- [x] Unit and data integrity test suite (19/19 passing).
- [x] Production analytical SQL views (`vw_order_fulfillment`, `vw_customer_rfm`, `vw_sales_master`).
- [x] Deep-dive business SQL queries (MoM growth, cohort retention, logistics disparity, seller Pareto).
- [ ] Connect Power BI to the MySQL semantic views and Parquet files for interactive executive dashboards.
- [ ] Build a Customer Repeat Purchase Propensity model using scikit-learn / XGBoost.
- [ ] Deploy an Automated Delivery Delay Risk Prediction pipeline.

---

## 👤 Author & Acknowledgments

- **Author:** Mohd Hamza Shaikh ([kmohdhamza10@gmail.com](mailto:kmohdhamza10@gmail.com))
- **Role:** Data Analyst / Data Scientist
- **Foundational Mentorship & Curriculum:** Special thanks to **Nitish Singh** and the **CampusX Data Analytics Mentorship Program (DAMP 1.0)** for providing the rigorous foundational framework (Project 2: E-Commerce Sales Analysis) that inspired this enterprise-grade deep dive.
- **Dataset Source:** [Olist Brazilian E-Commerce Public Dataset on Kaggle](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
