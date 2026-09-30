-- =====================================================================
-- View: vw_customer_rfm
-- Purpose: Customer-level RFM (Recency, Frequency, Monetary) Segmentation
-- Grain: Exactly one row per customer_unique_id
-- Author: Mohd Hamza Shaikh
-- =====================================================================

CREATE OR REPLACE VIEW vw_customer_rfm AS
WITH dataset_snapshot AS (
    -- Fixed analysis snapshot date: max purchase timestamp in dataset (2018-10-17 17:30:18) + 1 day
    -- Documented constant: '2018-10-18 17:30:18'
    -- Anchoring to (max + 1 day) prevents shifting Recency values over time
    SELECT DATE_ADD(MAX(order_purchase_timestamp), INTERVAL 1 DAY) AS snapshot_date 
    FROM olist_orders
),
valid_orders AS (
    -- Scoped to revenue orders (excluding canceled & unavailable, and 6 corrupt orders)
    -- Rank orders per customer to isolate latest location attributes
    SELECT 
        o.order_id,
        o.customer_id,
        o.order_purchase_timestamp,
        c.customer_unique_id,
        c.customer_city,
        c.customer_state,
        ROW_NUMBER() OVER (
            PARTITION BY c.customer_unique_id 
            ORDER BY o.order_purchase_timestamp DESC, o.order_id DESC
        ) AS rn
    FROM olist_orders o
    INNER JOIN olist_customers c 
        ON o.customer_id = c.customer_id
    WHERE NOT (o.order_status = 'canceled' AND o.order_delivered_customer_date IS NOT NULL)
      AND o.order_status NOT IN ('canceled', 'unavailable')
),
latest_customer_geo AS (
    -- Exactly one city/state pair per customer from their most recent order
    SELECT 
        customer_unique_id,
        customer_city,
        customer_state
    FROM valid_orders
    WHERE rn = 1
),
customer_rfm_agg AS (
    -- Aggregate RFM metrics per customer across all revenue orders
    SELECT 
        vo.customer_unique_id,
        DATEDIFF(snap.snapshot_date, MAX(vo.order_purchase_timestamp)) AS recency_days,
        COUNT(DISTINCT vo.order_id) AS frequency_orders,
        ROUND(COALESCE(SUM(oi.price), 0), 2) AS total_item_spend,
        ROUND(COALESCE(SUM(oi.freight_value), 0), 2) AS total_freight_spend,
        ROUND(COALESCE(SUM(oi.price + oi.freight_value), 0), 2) AS monetary_total_spend,
        ROUND(
            COALESCE(SUM(oi.price + oi.freight_value), 0) / NULLIF(COUNT(DISTINCT vo.order_id), 0), 
            2
        ) AS average_order_value,
        MIN(vo.order_purchase_timestamp) AS first_order_date,
        MAX(vo.order_purchase_timestamp) AS last_order_date,
        CASE 
            WHEN COUNT(DISTINCT vo.order_id) > 1 THEN 'Repeat Buyer'
            ELSE 'One-Time Buyer'
        END AS customer_loyalty_segment
    FROM valid_orders vo
    CROSS JOIN dataset_snapshot snap
    LEFT JOIN olist_order_items oi 
        ON vo.order_id = oi.order_id
    GROUP BY vo.customer_unique_id, snap.snapshot_date
)
SELECT 
    agg.customer_unique_id,
    geo.customer_city,
    geo.customer_state,
    agg.recency_days,
    agg.frequency_orders,
    agg.total_item_spend,
    agg.total_freight_spend,
    agg.monetary_total_spend,
    agg.average_order_value,
    agg.first_order_date,
    agg.last_order_date,
    agg.customer_loyalty_segment
FROM customer_rfm_agg agg
INNER JOIN latest_customer_geo geo 
    ON agg.customer_unique_id = geo.customer_unique_id;
