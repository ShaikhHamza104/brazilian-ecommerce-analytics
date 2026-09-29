# 📊 Brazilian E-Commerce (Olist) Sales & Customer Intelligence Platform
> **From Solid Foundations to Advanced Analytics: Customer Segmentation (RFM), Cohort Retention, Logistics Intelligence, and Strategic Revenue Insights**  
> **Author:** Mohd Hamza Shaikh  
> **Target Role:** Data Analyst / Data Scientist / Product & Business Analyst  
> **Core Competencies:** Exploratory Data Analysis (EDA), Advanced SQL (Window Functions, CTEs, Cohort Matrices), Customer Segmentation (RFM), Logistics Diagnostics, Data Storytelling, Business Intelligence, Python (Pandas, SQLAlchemy, PyArrow), Power BI  

---

## 📌 Executive Summary & Project Origin

This project originated as part of **Project 2 (E-Commerce Sales Analysis)** in the **Data Analytics Mentorship Program (DAMP 1.0 by CampusX)**. The program provided a rock-solid architectural foundation:
* Extracting transactional e-commerce data from relational databases using SQL.
* Preprocessing, cleaning, and transforming complex datasets using Python.
* Loading transformed tables into an analytical data warehouse structure.
* Designing interactive Power BI dashboards to translate data into executive decision-making.

### Taking the Project Beyond the Classroom: Where the Baseline Ends, the Deep-Dive Begins
While standard course projects stop after basic descriptive KPIs and high-level charts, **I chose to push this analysis to production-grade enterprise standards**. 

In live e-commerce companies, a Data Analyst or Data Scientist cannot merely follow a generic script. Real-world data is full of domain edge-cases: in-flight shipments, account-versus-individual identifiers, geographic disparities, and merchant concentration risks. 

I extended the project across five advanced dimensions:
1. **Critical Edge-Case Auditing:** Investigated four vital domain nuances that standard pipelines overlook, successfully preserving **2,965 non-delivered operational order records**, **23,000+ early-delivery items**, and **2,814 repeat customers ($861K+ in revenue)**.
2. **Modular Production Engineering:** Refactored one-off scripts into an installable Python package (`src/e_commerce_sales_analysis`) with connection pooling, automated chunked ingestion, Portuguese text normalization (`unidecode`), and a complete 19-test automated suite (`pytest`).
3. **Advanced SQL Analytical Views & Queries (MySQL 8.0):** Engineered production views and standalone analytics scripts leveraging **Common Table Expressions (CTEs)**, **Window Functions (`ROW_NUMBER()`, `SUM() OVER ()`, `LAG()`)**, and conditional tagging (`CASE WHEN`).
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

## 💡 Key Business Insights & Analytical Findings

### 1. Customer RFM Segmentation & Repeat Buyer Value (`vw_customer_rfm`)
* **One-Time Shoppers (92,867 customers):** Average lifetime spend of **$160.19** across 1 order.
* **Repeat Buyers (2,814 customers):** Average lifetime spend of **$305.99** across 2.11 orders (**+91% higher customer value**).
* **Business Takeaway:** Repeat customers generated **$861,063.72 in revenue** despite representing only 2.9% of total customers. Converting just 1% more one-time buyers into repeat purchasers represents an immediate **~$290,000 revenue growth opportunity**.

```
Customer Loyalty Segment Breakdown:
┌─────────────────────────┬──────────────────┬─────────────┬────────────────────┬────────────────────┐
│ Loyalty Segment         │ Total Customers  │ Avg Orders  │ Avg Lifetime Spend │ Total Revenue      │
├─────────────────────────┼──────────────────┼─────────────┼────────────────────┼────────────────────┤
│ One-Time Buyer          │ 92,867           │ 1.00        │ $160.19            │ $14,876,603.80     │
│ Repeat Buyer            │  2,814           │ 2.11        │ $305.99            │    $861,063.72     │
└─────────────────────────┴──────────────────┴─────────────┴────────────────────┴────────────────────┘
```

### 2. Customer Cohort Retention Analysis: The "Leaky Bucket" Reality (`02_customer_cohort_retention.sql`)
Tracking monthly customer acquisition cohorts from Month 0 through Month 6 uncovered a vital truth about Olist's unit economics:

```
cohort_month  cohort_size  M0 (Base)   M1 Retention   M2 Retention   M3 Retention   M6 Retention
2017-01          752         100%         0.40%          0.27%          0.13%          0.40%
2017-02         1690         100%         0.24%          0.30%          0.12%          0.24%
2017-03         2571         100%         0.51%          0.35%          0.39%          0.16%
2017-04         2325         100%         0.60%          0.22%          0.17%          0.34%
2017-05         3541         100%         0.48%          0.48%          0.40%          0.42%
2017-06         3102         100%         0.45%          0.35%          0.39%          0.35%
```
* **The Diagnostic:** Month 1 customer retention across all cohorts consistently stabilizes below **0.60%** (averaging ~0.40%).
* **Strategic Implication:** Olist is structurally an **Acquisition-driven marketplace**. Customers purchase durable, infrequent items (furniture, appliances, auto parts) and rarely return for recurring shopping. Therefore, **Customer Acquisition Cost (CAC) must be amortized entirely on the initial transaction**, as the business cannot bank on recurring Lifetime Value (LTV) to offset unprofitable first orders.

### 3. Supply Chain Disparities: "The Two Brazils" (`03_freight_and_delivery_delays_by_state.sql`)
Comparing logistics and customer satisfaction across Brazilian destination states reveals severe regional divergence:

| State | Region | Delivered Orders | Avg Delivery Days | Late Delivery % | Avg Freight Cost | Freight Ratio % | Avg Review Score |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **SP** (São Paulo) | Southeast | **40,494** | **8.7 days** | **5.89%** | **$17.33** | **18.20%** | **4.25 / 5** |
| **MG** (Minas Gerais) | Southeast | 11,354 | 11.9 days | 5.61% | $23.46 | 21.55% | 4.19 / 5 |
| **RJ** (Rio de Janeiro) | Southeast | 12,350 | 15.2 days | **13.47%** | $23.95 | 21.36% | **3.97 / 5** |
| **MA** (Maranhão) | Northeast | 717 | 21.5 days | **19.67%** | $42.95 | **29.95%** | **3.83 / 5** |
| **AL** (Alagoas) | Northeast | 397 | 24.5 days | **23.93%** | $38.58 | 26.74% | **3.85 / 5** |
| **RR** (Roraima) | North | 41 | **29.3 days** | 12.20% | **$48.34** | **32.68%** | **3.90 / 5** |

* **The Freight Tax:** Customers in Northern/Northeastern states pay nearly **3× higher shipping fees** ($48.34 in `RR` vs $17.33 in `SP`), with freight consuming up to **33% of total order value**.
* **Delivery Reliability:** Alagoas (`AL`) suffers from a **23.9% late delivery rate**, driving customer review scores down to **3.85**.
* **The Rio Operational Outlier:** Despite bordering São Paulo, Rio de Janeiro (`RJ`) exhibits a high **13.5% delay rate** and a sub-4.0 review score (3.97), highlighting dense urban routing and security friction.

### 4. Merchant Pareto Concentration & Platform Health (`04_seller_performance_and_concentration.sql`)
Applying window functions (`SUM() OVER (ORDER BY GMV DESC)`) revealed the mathematical Pareto distribution across 3,053 active sellers:

| Seller Pareto Tier | Merchant Count | % of All Merchants | Tier Total GMV | Avg Revenue / Seller | Avg Dispatch Time | Late Dispatch % | Avg Review Score |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Tier 1: Top 20% GMV (Elite)** | **18** | **0.59%** | **$2,695,340.57** | **$149,741.14** | 3.4 days | **7.84%** | 4.04 / 5 |
| **Tier 2: Next 30% GMV (Core)** | **110** | **3.60%** | **$4,080,395.82** | **$37,094.51** | 3.5 days | 9.76% | 4.02 / 5 |
| **Tier 3: Next 30% GMV (Growing)** | **411** | **13.46%** | **$4,066,618.80** | **$9,894.45** | 3.6 days | 10.76% | 4.06 / 5 |
| **Tier 4: Long Tail (Remaining 20%)** | **2,514** | **82.35%** | **$2,711,840.12** | **$1,078.70** | 3.7 days | **11.42%** | 4.02 / 5 |

* **Concentration Risk:** Just **18 sellers (0.59%)** control 20% of GMV. Only **128 merchants (4.2%)** control **50% of total platform sales**.
* **The 80/20 Rule Confirmed:** **17.65% of sellers (539 merchants)** generate **80% of total platform revenue ($10.84M)**.
* **Fulfillment Discipline:** Elite sellers exhibit lower late-dispatch rates (7.84% vs. 11.42% for long-tail sellers), proving that scale is correlated with operational maturity.

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

### Production Star Schema for Power BI & Machine Learning
To enable high-speed aggregation in BI tools and prevent Cartesian revenue inflation, the cleaned data was exported to columnar **Parquet** files:
* **Dimension Tables:** `dim_customers.parquet`, `dim_products.parquet`, `dim_sellers.parquet`, `dim_orders.parquet`, `dim_order_reviews.parquet`
* **Fact Tables:** `fact_order_items.parquet` (Grain: 1 row per product sold), `fact_order_payments.parquet` (Grain: 1 row per payment installment/method)
* **Analytical Master:** `olist_master_cleaned.parquet` (Unified line-item dataset for quick EDA and feature engineering)

---

## 🛠️ Codebase Structure

```
E-commerce Sales Analysis/
├── data/
│   ├── raw/                 # 9 original source CSV datasets
│   └── processed/           # 8 production Parquet tables (Clean Star Schema)
├── docs/
│   ├── diagrams/            # databaseschema.png (Verified, mathematically correct ERD)
│   ├── olist_data_dictionary.pdf
│   └── project_showcase_notion.md      # Complete portfolio report & findings
├── notebook/
│   └── 01_eda_and_cleaning.ipynb   # Documented EDA, Data Quality Diagnostics & Parquet Export
├── sql/
│   ├── ddl/
│   │   └── 01_schema.sql    # Complete MySQL DDL with indexing and primary/foreign keys
│   ├── views/
│   │   ├── vw_order_fulfillment.sql  # Delivery accuracy, transit duration & delay variance
│   │   ├── vw_customer_rfm.sql        # Recency, Frequency, Monetary & Repeat customer view
│   │   └── vw_sales_master.sql        # Unified line-item sales, route classification & ratings
│   └── analytics/
│       ├── 01_monthly_revenue_growth_mom.sql       # MoM GMV, volume, and Black Friday spike
│       ├── 02_customer_cohort_retention.sql         # 6-month retention matrix (Leaky Bucket)
│       ├── 03_freight_and_delivery_delays_by_state.sql # State logistics & review score scorecard
│       └── 04_seller_performance_and_concentration.sql # Pareto 80/20 distribution & merchant health
├── src/e_commerce_sales_analysis/
│   ├── config.py            # Dynamic project path resolution & environment settings
│   ├── db/
│   │   ├── connection.py    # SQLAlchemy engine with connection pooling & SSL
│   │   └── loader.py        # Chunked reader (50k rows/batch) & query execution
│   └── cleaning/
│       └── text.py          # unidecode Brazilian diacritic normalization & regex cleaning
├── tests/                   # 19 automated unit & data integrity tests (pytest)
├── pyproject.toml           # Modern package configuration (uv)
└── README.md
```

---

## 🎯 Interview Talking Points (Data Analyst / Data Scientist Focus)

### Q1: "How did you go beyond the standard course requirements for this project?"
> *"The CampusX DAMP 1.0 program gave me a strong foundational toolkit: extracting e-commerce records via SQL, preprocessing in Python, loading to warehouse tables, and building Power BI reports. But in industry, an impactful Data Analyst or Data Scientist cannot stop at a predefined assignment.*
> 
> *I took ownership of the project by auditing edge cases, investigating how data filtering decisions impact business metrics, establishing production engineering standards (automated pytest suite, connection pooling, modular Python architecture), and writing advanced SQL window functions for cohort retention and merchant Pareto concentration. It reflects my mindset: I master the fundamentals, think critically about the domain, and elevate the work to enterprise standards."*

### Q2: "What is your philosophy on handling missing values and data cleaning?"
> *"My philosophy is that data cleaning must be driven by business domain logic, not coding convenience. For instance, when analyzing why 4,353 orders lacked delivery timestamps, I recognized they were active in-flight or canceled orders—critical data for measuring cancellation rates and carrier lead times. By scoping validation conditionally rather than dropping nulls globally, I preserved 100% of cancellation records, ensuring operational metrics remain reliable."*

### Q3: "How did you design the RFM analysis, and what strategic action would you recommend?"
> *"I built a dedicated SQL view (`vw_customer_rfm`) that calculated Recency against the snapshot date using a CTE and `CROSS JOIN`, Frequency via distinct order counts, and Monetary value from item and freight totals. The analysis proved that repeat customers spend nearly double ($305.99 vs. $160.19) and generate over $860K in revenue. My strategic recommendation to marketing would be to deploy automated post-purchase onboarding sequences within 30 days of initial delivery, as repeat buyers represent our highest ROI customer segment."*

### Q4: "What did your cohort retention and seller concentration queries teach you about platform economics?"
> *"Two critical strategic insights:*
> *1. **The Leaky Bucket:** Month 1 cohort retention was under 0.50%, meaning Olist cannot count on LTV to justify expensive customer acquisition; first-order contribution margin must cover CAC.*
> *2. **Merchant Concentration:** The Pareto 80/20 analysis proved that just 17.6% of sellers drive 80% of platform sales, and only 18 elite merchants control 20% of GMV. Losing a handful of top merchants would severely threaten revenue, making Key Account Management (KAM) retention programs an urgent platform priority."*

### Q5: "What machine learning models can be built on top of this Star Schema?"
> *"Because the data is organized with strict entity grains and clean temporal features, it directly supports 3 high-impact models:*
> 1. * **Customer Churn & Repeat Purchase Propensity:** Classification model using RFM features and review scores to predict which buyers are likely to make a second purchase.*
> 2. * **Delivery Delay Predictor:** Regression model using origin-destination state routes, item weight, and freight charges to predict actual delivery days at checkout.*
> 3. * **Review Sentiment & Rating Prediction:** NLP and tabular modeling using review comments and delivery delay variance to predict 1-star dissatisfaction before it occurs.*

---

## 📈 Completed Milestones & Roadmap
- [x] Initial relational database schema and DDL definitions with foreign keys.
- [x] Batch ingestion pipeline with chunking and CLI management.
- [x] Comprehensive data cleaning pipeline in `notebook/01_eda_and_cleaning.ipynb` with 8 Parquet exports.
- [x] Automated test suite (19/19 pytest tests passing).
- [x] Production SQL views (`vw_order_fulfillment`, `vw_customer_rfm`, `vw_sales_master`).
- [x] 4 Deep-dive analytics SQL queries (MoM growth, cohort retention, state logistics, seller Pareto).
- [ ] Connect Power BI to the MySQL semantic views and Parquet files for interactive executive dashboards.
- [ ] Build a Customer Repeat Purchase Propensity model using scikit-learn / XGBoost.

---

## 👤 Author & Acknowledgments
* **Author:** Mohd Hamza Shaikh ([kmohdhamza10@gmail.com](mailto:kmohdhamza10@gmail.com))
* **Target Role:** Data Analyst / Data Scientist / Product & Business Analyst
* **Foundational Mentorship & Curriculum:** Special thanks to **Nitish Singh** and the **CampusX Data Analytics Mentorship Program (DAMP 1.0)** for providing the rigorous foundational framework (Project 2: E-Commerce Sales Analysis) that inspired this enterprise-grade deep dive.
* **Dataset Source:** [Olist Brazilian E-Commerce Public Dataset on Kaggle](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)

