-- =====================================================================
-- View: vw_sales_master
-- Purpose: Unified line-item sales reporting for Power BI and Analytics
-- Author: Mohd Hamza Shaikh
-- =====================================================================

CREATE OR REPLACE VIEW vw_sales_master AS
WITH latest_reviews AS (
    -- Pick the latest review per order to prevent line item duplication
    SELECT 
        order_id,
        review_score,
        ROW_NUMBER() OVER (
            PARTITION BY order_id 
            ORDER BY review_answer_timestamp DESC
        ) AS rn
    FROM olist_order_reviews
)
SELECT
    -- Order & Line Item Keys
    oi.order_id,
    oi.order_item_id,
    o.customer_id,
    c.customer_unique_id,
    oi.product_id,
    oi.seller_id,
    
    -- Order Status & Lifecycle
    o.order_status,
    o.order_purchase_timestamp,
    DATE(o.order_purchase_timestamp) AS order_purchase_date,
    YEAR(o.order_purchase_timestamp) AS order_year,
    MONTH(o.order_purchase_timestamp) AS order_month,
    QUARTER(o.order_purchase_timestamp) AS order_quarter,
    
    -- Product Dimension (English Translated)
    COALESCE(t.product_category_name_english, p.product_category_name, 'Unknown') AS product_category,
    p.product_weight_g,
    p.product_photos_qty,
    
    -- Geographic Dimensions (Customer vs. Seller)
    c.customer_city,
    c.customer_state,
    s.seller_city,
    s.seller_state,
    CASE 
        WHEN c.customer_state = s.seller_state THEN 'Same-State Shipping'
        ELSE 'Inter-State Shipping'
    END AS shipping_route_type,
    
    -- Monetary Metrics
    oi.price AS item_price,
    oi.freight_value,
    ROUND(oi.price + oi.freight_value, 2) AS total_item_value,
    
    -- Customer Satisfaction (Window Function Output)
    r.review_score

FROM olist_order_items oi
INNER JOIN olist_orders o 
    ON oi.order_id = o.order_id
INNER JOIN olist_customers c 
    ON o.customer_id = c.customer_id
INNER JOIN olist_sellers s 
    ON oi.seller_id = s.seller_id
LEFT JOIN olist_products p 
    ON oi.product_id = p.product_id
LEFT JOIN product_category_name_translation t 
    ON p.product_category_name = t.product_category_name
LEFT JOIN latest_reviews r 
    ON o.order_id = r.order_id AND r.rn = 1;
