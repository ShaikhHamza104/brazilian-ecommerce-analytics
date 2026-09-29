-- =====================================================================
-- View: vw_customer_rfm
-- Purpose: Customer-level RFM (Recency, Frequency, Monetary) Segmentation
-- Author: Mohd Hamza Shaikh
-- =====================================================================

CREATE OR REPLACE VIEW vw_customer_rfm AS
WITH dataset_max_date AS (
    SELECT MAX(order_purchase_timestamp) AS max_date 
    FROM olist_orders
)
SELECT
    -- Customer Unique Identity (Real Human / Account)
    c.customer_unique_id,
    
    -- Geographic Attributes
    c.customer_city,
    c.customer_state,
    
    -- Recency: Days between dataset snapshot date and customer's last purchase
    DATEDIFF(dmd.max_date, MAX(o.order_purchase_timestamp)) AS recency_days,
    
    -- Frequency: Total distinct orders placed by this customer
    COUNT(DISTINCT o.order_id) AS frequency_orders,
    
    -- Monetary: Total spend across all purchases
    ROUND(COALESCE(SUM(oi.price), 0), 2) AS total_item_spend,
    ROUND(COALESCE(SUM(oi.freight_value), 0), 2) AS total_freight_spend,
    ROUND(COALESCE(SUM(oi.price + oi.freight_value), 0), 2) AS monetary_total_spend,
    
    -- Average Order Value (AOV)
    ROUND(
        COALESCE(SUM(oi.price + oi.freight_value), 0) / NULLIF(COUNT(DISTINCT o.order_id), 0), 
        2
    ) AS average_order_value,
    
    -- Timestamps
    MIN(o.order_purchase_timestamp) AS first_order_date,
    MAX(o.order_purchase_timestamp) AS last_order_date,
    
    -- Customer Retention Segmentation
    CASE 
        WHEN COUNT(DISTINCT o.order_id) > 1 THEN 'Repeat Buyer'
        ELSE 'One-Time Buyer'
    END AS customer_loyalty_segment

FROM olist_customers c
CROSS JOIN dataset_max_date dmd
INNER JOIN olist_orders o 
    ON c.customer_id = o.customer_id
LEFT JOIN olist_order_items oi 
    ON o.order_id = oi.order_id
WHERE o.order_status != 'canceled'
GROUP BY 
    c.customer_unique_id,
    c.customer_city,
    c.customer_state,
    dmd.max_date;
