-- =====================================================================
-- Analysis: 05_repeat_buyer_aov.sql
-- Purpose: Recompute Average Order Value (AOV), Customer Lifetime Spend,
--          and Revenue Share for One-Time vs. Repeat Buyers
-- Author: Mohd Hamza Shaikh
-- Domain: Customer Economics & Unit Economics
-- =====================================================================

-- Context & Analytical Framing:
-- In transactional e-commerce, comparing cumulative customer spend between
-- one-time and repeat buyers can create an illusion of higher purchasing power
-- (+91% spend), when in reality repeat buyers simply accumulate spend across multiple orders.
--
-- This query isolates:
-- 1. Order-level Average Order Value (AOV = Total Revenue / Total Orders)
-- 2. Customer-level Lifetime Spend (Total Revenue / Unique Customers)
-- 3. Repeat buyer share of TOTAL marketplace revenue

WITH excluded_statuses AS (
    -- Revenue Excluded Statuses (aligns with REVENUE_EXCLUDED_STATUSES in Python pipeline)
    SELECT 'canceled' AS status
    UNION ALL
    SELECT 'unavailable' AS status
),
base_orders AS (
    -- Cleaned orders: filter out corrupt canceled-with-delivery orders
    -- and non-revenue operational statuses
    SELECT o.order_id, o.customer_id, o.order_status
    FROM olist_orders o
    WHERE NOT (o.order_status = 'canceled' AND o.order_delivered_customer_date IS NOT NULL)
      AND o.order_status NOT IN (SELECT status FROM excluded_statuses)
),
order_summary AS (
    -- 1. Calculate revenue per order (item price + freight)
    --    Scoped to revenue orders (excluding canceled & unavailable)
    SELECT 
        o.order_id,
        c.customer_unique_id,
        COALESCE(SUM(oi.price + oi.freight_value), 0) AS order_total_value
    FROM base_orders o
    INNER JOIN olist_customers c 
        ON o.customer_id = c.customer_id
    LEFT JOIN olist_order_items oi 
        ON o.order_id = oi.order_id
    GROUP BY o.order_id, c.customer_unique_id
),
customer_order_frequency AS (
    -- 2. Segment by unique customer identity: Repeat vs. One-Time
    SELECT 
        customer_unique_id,
        COUNT(order_id) AS total_orders_placed,
        SUM(order_total_value) AS lifetime_customer_spend,
        CASE 
            WHEN COUNT(order_id) > 1 THEN 'Repeat Buyer'
            ELSE 'One-Time Buyer'
        END AS customer_type
    FROM order_summary
    GROUP BY customer_unique_id
),
segmented_orders AS (
    -- 3. Attach customer loyalty segment back to each individual order
    SELECT 
        os.order_id,
        os.customer_unique_id,
        os.order_total_value,
        cof.customer_type
    FROM order_summary os
    INNER JOIN customer_order_frequency cof 
        ON os.customer_unique_id = cof.customer_unique_id
)
SELECT 
    customer_type,
    
    -- Volume Counts
    COUNT(DISTINCT customer_unique_id) AS total_customers,
    COUNT(DISTINCT order_id) AS total_orders,
    ROUND(COUNT(DISTINCT order_id) / COUNT(DISTINCT customer_unique_id), 2) AS avg_orders_per_customer,
    
    -- Financial Totals (BRL / R$)
    ROUND(SUM(order_total_value), 2) AS total_revenue_brl,
    
    -- Order-Level Economics (Real AOV)
    ROUND(SUM(order_total_value) / NULLIF(COUNT(DISTINCT order_id), 0), 2) AS average_order_value_brl,
    
    -- Customer-Level Lifetime Spend
    ROUND(SUM(order_total_value) / NULLIF(COUNT(DISTINCT customer_unique_id), 0), 2) AS avg_lifetime_spend_brl,
    
    -- Revenue Contribution Percentage
    ROUND(
        100.0 * SUM(order_total_value) / (SELECT SUM(order_total_value) FROM segmented_orders), 
        2
    ) AS revenue_share_pct

FROM segmented_orders
GROUP BY customer_type
ORDER BY total_revenue_brl DESC;
