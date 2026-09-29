-- =====================================================================
-- View: vw_order_fulfillment
-- Purpose: Order-level logistics KPIs, delivery accuracy, and delays
-- Author: Mohd Hamza Shaikh
-- =====================================================================

CREATE OR REPLACE VIEW vw_order_fulfillment AS
SELECT
    -- Order Identifiers
    o.order_id,
    o.customer_id,
    c.customer_unique_id,
    o.order_status,
    
    -- Geographic Dimensions
    c.customer_city,
    c.customer_state,
    
    -- Raw Timestamps
    o.order_purchase_timestamp,
    o.order_approved_at,
    o.order_delivered_carrier_date,
    o.order_delivered_customer_date,
    o.order_estimated_delivery_date,
    
    -- Logistics Duration Metrics (in Days)
    DATEDIFF(o.order_delivered_customer_date, o.order_purchase_timestamp) AS actual_delivery_days,
    DATEDIFF(o.order_estimated_delivery_date, o.order_purchase_timestamp) AS estimated_delivery_days,
    DATEDIFF(o.order_delivered_carrier_date, o.order_approved_at) AS dispatch_lead_days,
    DATEDIFF(o.order_delivered_customer_date, o.order_delivered_carrier_date) AS courier_transit_days,
    
    -- Delivery Variance (Actual - Estimated: Negative = Early, Positive = Late)
    DATEDIFF(o.order_delivered_customer_date, o.order_estimated_delivery_date) AS delivery_variance_days,
    
    -- Business Performance Classification
    CASE
        WHEN o.order_status != 'delivered' THEN 'In-Transit / Unfinished'
        WHEN o.order_delivered_customer_date <= o.order_estimated_delivery_date THEN 'On-Time / Early'
        ELSE 'Late'
    END AS delivery_performance_status

FROM olist_orders o
INNER JOIN olist_customers c 
    ON o.customer_id = c.customer_id;
