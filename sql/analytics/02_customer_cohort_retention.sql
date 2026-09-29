-- =====================================================================
-- Analysis: 02_customer_cohort_retention.sql
-- Purpose: Monthly customer cohort retention analysis (Month 0 to Month 6)
-- Author: Mohd Hamza Shaikh
-- Domain: Product Analytics & Customer Retention
-- =====================================================================

WITH customer_cohort AS (
    -- 1. Identify the first purchase month (Cohort Month) for each unique customer
    SELECT 
        c.customer_unique_id,
        MIN(o.order_purchase_timestamp) AS first_purchase_date,
        CONCAT(YEAR(MIN(o.order_purchase_timestamp)), '-', LPAD(MONTH(MIN(o.order_purchase_timestamp)), 2, '0')) AS cohort_month
    FROM olist_orders o
    INNER JOIN olist_customers c 
        ON o.customer_id = c.customer_id
    WHERE o.order_status NOT IN ('canceled', 'unavailable')
    GROUP BY c.customer_unique_id
),
customer_orders AS (
    -- 2. Map all customer orders to their cohort and calculate the month index (0, 1, 2...)
    SELECT 
        cc.cohort_month,
        cc.customer_unique_id,
        o.order_id,
        (YEAR(o.order_purchase_timestamp) - YEAR(cc.first_purchase_date)) * 12 + 
        (MONTH(o.order_purchase_timestamp) - MONTH(cc.first_purchase_date)) AS month_number
    FROM olist_orders o
    INNER JOIN olist_customers c 
        ON o.customer_id = c.customer_id
    INNER JOIN customer_cohort cc 
        ON c.customer_unique_id = cc.customer_unique_id
    WHERE o.order_status NOT IN ('canceled', 'unavailable')
),
cohort_sizes AS (
    -- 3. Calculate total unique customers who joined in each cohort (Month 0 Base)
    SELECT 
        cohort_month,
        COUNT(DISTINCT customer_unique_id) AS cohort_size
    FROM customer_cohort
    GROUP BY cohort_month
)
SELECT 
    co.cohort_month,
    cs.cohort_size,
    co.month_number,
    COUNT(DISTINCT co.customer_unique_id) AS retained_customers,
    ROUND((COUNT(DISTINCT co.customer_unique_id) / cs.cohort_size) * 100, 2) AS retention_rate_pct

FROM customer_orders co
INNER JOIN cohort_sizes cs 
    ON co.cohort_month = cs.cohort_month
WHERE co.cohort_month BETWEEN '2017-01' AND '2017-06'
  AND co.month_number <= 6
GROUP BY 
    co.cohort_month, 
    cs.cohort_size, 
    co.month_number
ORDER BY 
    co.cohort_month, 
    co.month_number;
