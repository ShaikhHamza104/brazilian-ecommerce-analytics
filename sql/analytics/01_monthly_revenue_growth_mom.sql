-- =====================================================================
-- Analysis: 01_monthly_revenue_growth_mom.sql
-- Purpose: Time-series revenue trends, MoM growth %, and cumulative GMV
-- Author: Mohd Hamza Shaikh
-- Domain: Financial & Sales Analytics
--
-- Data Boundary & Period Limitations:
-- - Sparse Months: Sep 2016 (2 orders), Oct 2016 (290 orders), Dec 2016 (1 order), with Nov 2016 missing.
-- - Incomplete Cutoff: Sep 2018 (1 non-canceled order) and Oct 2018 represent the end of the public sample.
-- - Stable Operational Window: Jan 2017 to Aug 2018 (20 consecutive full operational months).
-- =====================================================================

WITH monthly_metrics AS (
    SELECT
        -- Format as YYYY-MM
        CONCAT(YEAR(o.order_purchase_timestamp), '-', LPAD(MONTH(o.order_purchase_timestamp), 2, '0')) AS order_period,

        -- Volume Metrics
        COUNT(DISTINCT o.order_id) AS total_orders,
        COUNT(oi.order_item_id) AS total_items_sold,

        -- Revenue Breakdown
        ROUND(SUM(oi.price), 2) AS gross_merchandise_value,
        ROUND(SUM(oi.freight_value), 2) AS total_freight,
        ROUND(SUM(oi.price + oi.freight_value), 2) AS total_revenue,

        -- Basket / Unit Economics
        ROUND(AVG(oi.price + oi.freight_value), 2) AS avg_item_value,
        ROUND(SUM(oi.price + oi.freight_value) / COUNT(DISTINCT o.order_id), 2) AS avg_order_value

    FROM olist_orders o
    INNER JOIN olist_order_items oi
        ON o.order_id = oi.order_id
    WHERE o.order_status NOT IN ('canceled', 'unavailable')
    GROUP BY CONCAT(YEAR(o.order_purchase_timestamp), '-', LPAD(MONTH(o.order_purchase_timestamp), 2, '0'))
)
SELECT
    order_period,
    total_orders,
    total_items_sold,
    total_revenue,

    -- Previous Month Revenue using LAG() Window Function
    LAG(total_revenue, 1) OVER (ORDER BY order_period) AS prev_month_revenue,

    -- Month-over-Month Revenue Growth Percentage
    ROUND(
        ((total_revenue - LAG(total_revenue, 1) OVER (ORDER BY order_period))
        / LAG(total_revenue, 1) OVER (ORDER BY order_period)) * 100,
        2
    ) AS mom_growth_pct,

    -- Cumulative Running Total of Revenue
    ROUND(SUM(total_revenue) OVER (ORDER BY order_period), 2) AS running_cumulative_revenue,

    avg_order_value

FROM monthly_metrics
ORDER BY order_period;
