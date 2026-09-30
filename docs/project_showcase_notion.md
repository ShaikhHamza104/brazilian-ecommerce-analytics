# 📊 Brazilian E-Commerce (Olist) Sales & Customer Intelligence Platform
> **Customer Segmentation (RFM), Cohort Retention, Logistics Intelligence, and Unit Economics Analysis**  
> **Author:** Mohd Hamza Shaikh  
> **Target Role:** Data Analyst  
> **Core Competencies:** Exploratory Data Analysis (EDA), Advanced SQL (Window Functions, CTEs, Cohort Matrices), Customer Segmentation (RFM), Logistics Diagnostics, Data Storytelling, Business Intelligence, Python (Pandas, SQLAlchemy, PyArrow), Power BI  

---

## 📌 Executive Summary & Project Origin

This project originated as part of **Project 2 (E-Commerce Sales Analysis)** in the **Data Analytics Mentorship Program (DAMP 1.0 by CampusX)**. The program provided a rock-solid architectural foundation:
* Extracting transactional e-commerce data from relational databases using SQL.
* Preprocessing, cleaning, and transforming complex datasets using Python.
* Loading transformed tables into an analytical data warehouse structure.
* Designing interactive Power BI dashboards to translate data into executive decision-making.

### Taking the Project Beyond the Classroom: Where the Baseline Ends, Applied Analysis Begins
While standard course projects often conclude after basic descriptive KPIs and high-level charts, **I expanded this analysis into a modular, tested analytics pipeline**. 

In commercial e-commerce environments, a Data Analyst cannot merely follow a generic script. Real-world data contains domain edge cases: in-flight shipments, account-versus-individual identifiers, geographic delivery disparities, and merchant concentration risks. 

I extended the project across five analytical dimensions:
1. **Critical Edge-Case Auditing:** Investigated four vital domain nuances that standard pipelines overlook, successfully preserving **2,957 non-delivered operational order records**, **23,000 early-delivery items**, and **2,888 repeat buyers (R$ 890K in GMV revenue)**.
2. **Modular Analytics Engineering:** Refactored one-off scripts into an installable Python package (`src/e_commerce_sales_analysis`) with connection pooling, automated chunked ingestion, Portuguese text normalization (`unidecode`), and a 23-test automated test suite (`pytest`) with GitHub Actions CI.
3. **Advanced SQL Analytical Views & Queries (MySQL 8.0):** Engineered analytical views and standalone analytics scripts leveraging **Common Table Expressions (CTEs)**, **Window Functions (`ROW_NUMBER()`, `SUM() OVER ()`, `LAG()`)**, and conditional classification (`CASE WHEN`).
4. **Customer & Merchant Diagnostics:** Built 6-month monthly cohort retention matrices, mapped the regional logistics divide, and quantified seller revenue concentration across 3,095 active merchants.
5. **Columnar Star Schema for BI:** Transformed relational tables into an dimensional model exported to columnar **Parquet** files (`dim_*` and `fact_*`), eliminating Cartesian join risks and preparing the data for reporting.

---

## 🔬 Advanced Data Integrity & Edge-Case Preservations

During the exploratory data analysis phase, I audited data cleaning assumptions to ensure the dataset accurately reflected operational truth:

| # | Domain Nuance & Edge Case | Standard / Baseline Handling | Modular Pipeline Solution & Value Preserved |
|---|---|---|---|
| **1** | **Customer Account vs. Unique Individual** | Using `customer_id` for both transactions and customer counting. | Differentiated `customer_id` (transaction token) from `customer_unique_id` (actual human buyer). Identified all **3,217 repeat purchase events** across **2,888 repeat buyers** on revenue orders (distinguished from the raw 3,345 account gap in uncleaned data), revealing that repeat buyers averaged **R$ 145.82** per order (AOV) and **R$ 308.26** in cumulative lifetime spend, compared to **R$ 161.18** for one-time buyers. |
| **2** | **In-Flight & Canceled Shipments** | Naive date subtraction (`delivery - purchase >= 0`), which inadvertently drops rows where delivery date is `NULL`. | Scoped date integrity validation conditionally to `delivered` status only. Preserved **2,957 in-flight and non-delivered orders**, retaining full operational visibility into order cancellations, processing lag, and active shipments. |
| **3** | **Early Carrier Fulfillment** | Filtering out items where `shipping_limit_date < delivery_date` under the assumption of an invalid sequence. | Recognized that packages delivered *before* the seller dispatch deadline represent exceptional logistics performance. Preserved **23,000 line items**. |
| **4** | **Financial Granularity (Items vs. Payments)** | Merging payments (1:M) and order items (1:N) directly into a single flat denormalized table. | Preserved accounting integrity by designing a **Star Schema** with separate Fact tables for Items and Payments, preventing Cartesian join inflation that artificially doubles revenue (verified via order `03ecec245220b63fd7f68c1737ba99ba`). |

---

## 💡 Key Business Insights & Analytical Findings

### 1. Customer RFM Segmentation & Repeat Buyer Economics (`vw_customer_rfm` & `05_repeat_buyer_aov.sql`)
* **One-Time Shoppers (92,102 customers):** Generated **R$ 14,845,268.53** across 92,102 orders, with an Average Order Value (AOV) of **R$ 161.18** (or R$ 138.37 merchandise price AOV).
* **Repeat Buyers (2,888 customers):** Generated **R$ 890,258.50** across 6,105 orders, with an Average Order Value of **R$ 145.82** (or R$ 122.93 merchandise price AOV) and an average cumulative lifetime spend of **R$ 308.26** across ~2.11 orders.
* **Analytical Framing:** While lifetime spend per customer was naturally higher for repeat buyers (+91.3%) due to placing multiple orders, their spend per individual order (AOV) was slightly lower (-9.5%) than one-time buyers. Repeat buyers represented 5.66% of total platform GMV (and 5.56% of merchandise price revenue).

```
Customer Loyalty Segment Breakdown (Revenue Orders):
┌─────────────────────────┬──────────────────┬─────────────┬─────────────┬────────────────────┬────────────────────┬────────────────┐
│ Loyalty Segment         │ Total Customers  │ Total Orders│ Avg Orders  │ AOV (Order Level)  │ Avg Lifetime Spend │ Total Revenue  │
├─────────────────────────┼──────────────────┼─────────────┼─────────────┼────────────────────┼────────────────────┼────────────────┤
│ One-Time Buyer          │ 92,102           │ 92,102      │ 1.00        │ R$ 161.18          │ R$ 161.18          │ R$ 14,845,269  │
│ Repeat Buyer            │  2,888           │  6,105      │ 2.11        │ R$ 145.82          │ R$ 308.26          │ R$    890,259  │
└─────────────────────────┴──────────────────┴─────────────┴─────────────┴────────────────────┴────────────────────┴────────────────┘
```

### 2. Customer Cohort Retention Analysis: The "Leaky Bucket" Reality (`02_customer_cohort_retention.sql`)
Tracking monthly customer acquisition cohorts from Month 0 through Month 6 uncovered a vital pattern in Olist's unit economics:

```
cohort_month  cohort_size  M0 (Base)   M1 Retention   M2 Retention   M3 Retention   M6 Retention
2017-01          752         100%         0.40%          0.27%          0.13%          0.40%
2017-02         1690         100%         0.24%          0.30%          0.12%          0.24%
2017-03         2571         100%         0.51%          0.35%          0.39%          0.16%
2017-04         2325         100%         0.60%          0.22%          0.17%          0.34%
2017-05         3541         100%         0.48%          0.48%          0.40%          0.42%
2017-06         3102         100%         0.45%          0.35%          0.39%          0.35%
```
* **The Diagnostic:** Month 1 customer retention across all cohorts consistently stabilized below **0.60%** (averaging ~0.45%).
* **Strategic Hypothesis:** Olist functioned structurally as an **acquisition-driven marketplace**. Customers purchased durable, infrequent items (furniture, appliances, auto parts) and rarely returned for recurring shopping. Therefore, **Customer Acquisition Cost (CAC) likely needed to be recovered on the initial transaction**, as the business could not bank on recurring Lifetime Value (LTV) to offset unprofitable first orders. *(Note: This dataset does not track marketing spend or CAC).*

### 3. Supply Chain Disparities: "The Two Brazils" (`03_freight_and_delivery_delays_by_state.sql`)
Comparing logistics and customer satisfaction across Brazilian destination states revealed clear regional divergence:

| State | Region | Delivered Orders | Avg Delivery Days | Late Delivery % | Avg Freight Cost | Freight Ratio % | Avg Review Score |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **SP** (São Paulo) | Southeast | **40,494** | **8.7 days** | **5.89%** | **R$ 17.33** | **18.20%** | **4.25 / 5** |
| **MG** (Minas Gerais) | Southeast | 11,354 | 11.9 days | 5.61% | R$ 23.46 | 21.55% | 4.19 / 5 |
| **RJ** (Rio de Janeiro) | Southeast | 12,350 | 15.2 days | **13.47%** | R$ 23.95 | 21.36% | **3.97 / 5** |
| **MA** (Maranhão) | Northeast | 717 | 21.5 days | **19.67%** | R$ 42.95 | **29.95%** | **3.83 / 5** |
| **AL** (Alagoas) | Northeast | 397 | 24.5 days | **23.93%** | R$ 38.58 | 26.74% | **3.85 / 5** |
| **RR** (Roraima) | North | 41 | **29.3 days** | 12.20% | **R$ 48.34** | **32.68%** | **3.90 / 5** |

* **The Freight Disparity:** Customers in northern/northeastern states paid nearly **3× higher shipping fees** (R$ 48.34 in `RR` vs R$ 17.33 in `SP`), with freight consuming up to **33% of total order value**.
* **Delivery Reliability:** Alagoas (`AL`) suffered from a **23.93% late delivery rate**, driving customer review scores down to **3.85**.
* **The Rio Operational Outlier:** Despite bordering São Paulo, Rio de Janeiro (`RJ`) exhibited a high **13.5% delay rate** and a sub-4.0 review score (3.97), reflecting dense urban routing friction.

### 4. Merchant Concentration & Platform Health (`04_seller_performance_and_concentration.sql`)
Applying window functions (`SUM() OVER (ORDER BY total_revenue DESC)`) analyzed merchandise price revenue (`SUM(price)`) across 3,053 active sellers on revenue orders:

| Seller Tier | Merchant Count | % of All Merchants | Tier Total Revenue | Avg Revenue / Seller | Avg Dispatch Time | Late Dispatch % | Avg Review Score |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Tier 1: Top 20 Pct Revenue (Elite)** | **18** | **0.59%** | **R$ 2,695,340.57** | **R$ 149,741.14** | 3.4 days | **7.84%** | 4.04 / 5 |
| **Tier 2: Next 30 Pct Revenue (Core)** | **110** | **3.60%** | **R$ 4,080,395.82** | **R$ 37,094.51** | 3.5 days | 9.76% | 4.02 / 5 |
| **Tier 3: Next 30 Pct Revenue (Growing)** | **411** | **13.46%** | **R$ 4,066,618.80** | **R$ 9,894.45** | 3.6 days | 10.76% | 4.06 / 5 |
| **Tier 4: Long Tail (Remaining 20 Pct)** | **2,514** | **82.35%** | **R$ 2,711,840.12** | **R$ 1,078.70** | 3.7 days | **11.42%** | 4.02 / 5 |

* **Base Metric:** Scoped to merchandise price revenue (`SUM(price)`) across 3,053 active merchants on revenue orders.
* **Concentration Profile:** 18 elite sellers (0.59%) generated R$ 2,695,340.57 (19.89% of revenue). Combining Tier 1 and Tier 2, 128 merchants (4.19%) controlled R$ 6,775,736.39 (49.99% of total merchandise price sales).
* **Pareto Pattern:** The top 539 merchants (Tiers 1–3 combined, 17.65% of active sellers) generated **R$ 10,842,355.19 (79.99% of total platform merchandise price revenue)**.
* **Fulfillment Discipline:** Elite sellers maintained lower late-dispatch rates (7.84% vs. 11.42% for long-tail sellers), showing that higher volume correlated with operational consistency.

---

## 🏗️ Relational Architecture (ERD) & Dimensional Modeling

### Normalized Source Schema (3NF)
Modeled 9 core tables in MySQL with strict primary keys and foreign key constraints:
* **Lookup / Reference:** `olist_customers`, `olist_sellers`, `olist_products`, `product_category_name_translation`, `olist_geolocation`
* **Orders:** `olist_orders` (central transaction entity)
* **Transaction Children:** `olist_order_items`, `olist_order_payments`, `olist_order_reviews`

```
[olist_customers] (1) ──────────── (N) [olist_orders] (1) ─── (N) [olist_order_items] (N) ─── (1) [olist_products]
                                         │            (1) ─── (N) [olist_order_payments]            │ (N)
                                         │            (1) ─── (N) [olist_order_reviews]             │
                                         │                                                          ▼ (1)
                                   (Ref Lookup)                                     [product_category_name_translation]
                                [olist_geolocation]
```

### Star Schema for Power BI
To enable high-speed aggregation in BI tools and prevent Cartesian revenue inflation, the cleaned data was exported to columnar **Parquet** files:
* **Dimension Tables:** `dim_orders.parquet` (Grain: 1 row per order, 99,435 rows), `dim_customers.parquet`, `dim_products.parquet`, `dim_sellers.parquet`, `dim_order_reviews.parquet`
* **Fact Tables:** `fact_sales_items.parquet` (Grain: 1 row per line item sold, 112,643 rows with products and sellers joined), `fact_order_payments.parquet` (Grain: 1 row per payment installment/method)

---

## 🛠️ Codebase Structure

```plaintext
brazilian-ecommerce-analytics/
├── .github/
│   └── workflows/
│       └── ci.yml             # GitHub Actions CI for flake8 & pytest
├── data/
│   ├── raw/                   # 9 original source CSV datasets (from Kaggle)
│   └── processed/             # 7 analytical Parquet tables (Star Schema)
├── docs/
│   ├── diagrams/              # databaseschema.png (Verified Crow's Foot ERD)
│   ├── olist_data_dictionary.pdf
│   └── project_showcase_notion.md  # Detailed portfolio report
├── notebook/
│   └── 01_eda_and_cleaning.ipynb   # Documented EDA, Data Quality Diagnostics & Parquet Export
├── script/
│   ├── database.py            # Database utility scripts
│   ├── dataclean.py           # Text cleaning utilities
│   └── export_to_mysql.py     # Multi-row batch CSV-to-MySQL ingestion CLI
├── sql/
│   ├── ddl/
│   │   └── 01_schema.sql      # MySQL DDL with indexing and primary/foreign keys
│   ├── views/
│   │   ├── vw_order_fulfillment.sql  # Delivery accuracy, transit duration & delay variance
│   │   ├── vw_customer_rfm.sql        # Fixed snapshot date Recency, Frequency & Monetary view
│   │   └── vw_sales_master.sql        # Unified line-item sales, route classification & ratings
│   └── analytics/
│       ├── 01_monthly_revenue_growth_mom.sql       # MoM GMV, volume, and Black Friday spike
│       ├── 02_customer_cohort_retention.sql         # 6-month retention matrix (Leaky Bucket)
│       ├── 03_freight_and_delivery_delays_by_state.sql # State logistics & review score scorecard
│       ├── 04_seller_performance_and_concentration.sql # Pareto merchant analysis & dispatch speed
│       └── 05_repeat_buyer_aov.sql                 # Repeat buyer AOV, lifetime spend & revenue share
├── src/e_commerce_sales_analysis/
│   ├── config.py              # Dynamic project path resolution & environment settings
│   ├── db/
│   │   ├── connection.py      # SQLAlchemy engine with connection pooling & SSL
│   │   └── loader.py          # Chunked reader & query execution
│   └── cleaning/
│       ├── text.py            # unidecode Brazilian diacritic normalization
│       └── transforms.py      # Route, delivery delay, and loyalty classification
├── tests/                     # 23 automated tests (10 unit tests, 13 DB smoke tests)
├── .flake8                    # Flake8 linter configuration
├── pyproject.toml             # Modern package configuration (uv)
└── README.md
```

---

## 🎯 Interview Talking Points (Data Analyst Focus)

### Q1: "How did you go beyond the standard course requirements for this project?"
> *"The CampusX DAMP 1.0 program gave me a strong foundational toolkit: extracting e-commerce records via SQL, preprocessing in Python, loading to warehouse tables, and building Power BI reports. But in industry, an impactful Data Analyst cannot stop at a predefined assignment.*
> 
> *I took ownership of the project by auditing edge cases, investigating how data filtering decisions impact business metrics, establishing clean code standards (automated pytest suite, connection pooling, modular Python architecture, CI workflow), and writing advanced SQL window functions for cohort retention, repeat buyer economics, and merchant Pareto concentration. It reflects my mindset: I master the fundamentals, think critically about the domain, and build reproducible analytics."*

### Q2: "What is your philosophy on handling missing values and data cleaning?"
> *"My philosophy is that data cleaning must be driven by business domain logic, not coding convenience. For instance, when analyzing why orders lacked delivery timestamps, I recognized they were active in-flight or canceled orders—critical data for measuring cancellation rates and carrier lead times. By scoping validation conditionally rather than dropping nulls globally, I preserved 2,957 non-delivered orders, ensuring operational metrics remain reliable."*

### Q3: "How did you design the RFM analysis, and what strategic action would you recommend?"
> *"I built a dedicated SQL view (`vw_customer_rfm`) that calculated Recency against a fixed dataset snapshot date (max purchase timestamp + 1 day) using a CTE, Frequency via distinct order counts, and Monetary value from item and freight totals. When breaking down order-level unit economics on revenue orders, repeat buyers actually spent slightly less per order (R$ 145.82 AOV) than one-time buyers (R$ 161.18 AOV), though their cumulative spend reached R$ 308.26 across ~2.11 orders. Repeat buyers accounted for 5.66% of platform GMV revenue, suggesting marketing efforts should evaluate post-purchase onboarding campaigns to identify whether repeat purchase rates can be economically improved."*

### Q4: "What did your cohort retention and seller concentration queries teach you about platform economics?"
> *"Two critical strategic insights:*
> *1. **The Leaky Bucket:** Month 1 cohort retention was under 0.60% (averaging ~0.45%), meaning Olist could not count on recurring LTV to justify expensive customer acquisition; first-order contribution margin had to cover acquisition costs.*
> *2. **Merchant Concentration:** The seller Pareto analysis proved that ~17.7% of active sellers (539 merchants) drove ~80% of platform merchandise price sales, and 18 elite merchants generated 19.89% (R$ 2.70M). Losing a handful of top merchants would severely impact revenue, making Key Account Management (KAM) retention programs an urgent platform priority."*

---

## 📈 Completed Milestones & Roadmap
- [x] Initial relational database schema and DDL definitions with foreign keys.
- [x] Batch ingestion pipeline with chunking and CLI management.
- [x] Comprehensive data cleaning pipeline in `notebook/01_eda_and_cleaning.ipynb` with 7 Parquet exports.
- [x] Automated test suite (23 tests: 10 non-DB unit tests, 13 DB smoke tests) with GitHub Actions CI.
- [x] Analytical SQL views (`vw_order_fulfillment`, `vw_customer_rfm`, `vw_sales_master`).
- [x] 5 Deep-dive analytics SQL queries (MoM growth, cohort retention, state logistics, seller Pareto, repeat buyer AOV).
- [ ] Connect Power BI Desktop to the Parquet files for interactive executive reporting.

---

## 👤 Author & Acknowledgments
* **Author:** Mohd Hamza Shaikh ([kmohdhamza10@gmail.com](mailto:kmohdhamza10@gmail.com))
* **Target Role:** Data Analyst
* **Foundational Mentorship & Curriculum:** Special thanks to **Nitish Singh** and the **CampusX Data Analytics Mentorship Program (DAMP 1.0)** for providing the rigorous foundational framework (Project 2: E-Commerce Sales Analysis) that inspired this modular analytics deep dive.
* **Dataset Source & License:** [Olist Brazilian E-Commerce Public Dataset on Kaggle](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) by Olist, released under the **CC BY-NC-SA 4.0** (Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International) license.
