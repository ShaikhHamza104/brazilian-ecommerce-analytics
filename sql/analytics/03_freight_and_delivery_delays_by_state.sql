-- =====================================================================
-- Analysis: 03_freight_and_delivery_delays_by_state.sql
-- Purpose: Analyze logistics performance, freight burden, and customer 
--          satisfaction (NPS / Review Score) by destination state.
-- Author: Mohd Hamza Shaikh
-- Domain: Supply Chain Logistics & Customer Experience Analytics
-- =====================================================================

WITH order_financials AS (
    -- 1. Pre-aggregate order items at order_id level to prevent Cartesian duplicates
    SELECT 
        order_id,
        COUNT(order_item_id) AS total_items,
        SUM(price) AS order_items_value,
        SUM(freight_value) AS order_freight_value
    FROM olist_order_items
    GROUP BY order_id
),
order_reviews_deduped AS (
    -- 2. Take the average review score per order in case of multiple review entries
    SELECT 
        order_id,
        AVG(review_score) AS avg_order_review_score
    FROM olist_order_reviews
    GROUP BY order_id
),
order_level_metrics AS (
    -- 3. Combine delivery fulfillment dates, state geography, and financials
    SELECT 
        o.order_id,
        c.customer_state,
        f.order_items_value,
        f.order_freight_value,
        (f.order_freight_value / NULLIF(f.order_items_value + f.order_freight_value, 0)) * 100 AS freight_ratio_pct,
        DATEDIFF(o.order_delivered_customer_date, o.order_purchase_timestamp) AS actual_delivery_days,
        DATEDIFF(o.order_estimated_delivery_date, o.order_purchase_timestamp) AS estimated_delivery_days,
        DATEDIFF(o.order_delivered_customer_date, o.order_estimated_delivery_date) AS delay_days,
        CASE 
            WHEN o.order_delivered_customer_date > o.order_estimated_delivery_date THEN 1 
            ELSE 0 
        END AS is_delayed,
        r.avg_order_review_score
    FROM olist_orders o
    INNER JOIN olist_customers c 
        ON o.customer_id = c.customer_id
    INNER JOIN order_financials f 
        ON o.order_id = f.order_id
    LEFT JOIN order_reviews_deduped r 
        ON o.order_id = r.order_id
    WHERE o.order_status = 'delivered'
      AND o.order_delivered_customer_date IS NOT NULL
      AND o.order_purchase_timestamp IS NOT NULL
)
-- 4. State-level aggregated logistics and customer experience scorecard
SELECT 
    customer_state,
    COUNT(order_id) AS total_delivered_orders,
    ROUND(AVG(actual_delivery_days), 1) AS avg_actual_delivery_days,
    ROUND(AVG(estimated_delivery_days), 1) AS avg_estimated_delivery_days,
    ROUND(AVG(delay_days), 1) AS avg_delay_days,
    ROUND((SUM(is_delayed) / COUNT(order_id)) * 100, 2) AS late_delivery_rate_pct,
    ROUND(AVG(order_freight_value), 2) AS avg_freight_cost,
    ROUND(AVG(freight_ratio_pct), 2) AS avg_freight_ratio_pct,
    ROUND(AVG(avg_order_review_score), 2) AS avg_review_score

FROM order_level_metrics
GROUP BY customer_state
ORDER BY avg_actual_delivery_days DESC;
