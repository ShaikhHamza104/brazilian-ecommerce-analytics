-- =====================================================================
-- Analysis: 04_seller_performance_and_concentration.sql
-- Purpose: Analyze seller revenue concentration (Pareto 80/20 rule),
--          dispatch fulfillment speed, late dispatch rates, and ratings.
-- Author: Mohd Hamza Shaikh
-- Domain: Marketplace Operations & Merchant Health Analytics
-- =====================================================================

WITH seller_orders AS (
    -- 1. Gather all valid item-level transactions joined with order timestamps
    SELECT 
        oi.seller_id,
        oi.order_id,
        oi.price,
        oi.freight_value,
        oi.shipping_limit_date,
        o.order_purchase_timestamp,
        o.order_delivered_carrier_date,
        -- Check if seller handed off to carrier past the required shipping limit date
        CASE 
            WHEN o.order_delivered_carrier_date > oi.shipping_limit_date THEN 1 
            ELSE 0 
        END AS is_late_dispatch,
        -- Carrier dispatch turnaround in days
        TIMESTAMPDIFF(HOUR, o.order_purchase_timestamp, o.order_delivered_carrier_date) / 24.0 AS dispatch_turnaround_days,
        r.review_score
    FROM olist_order_items oi
    INNER JOIN olist_orders o 
        ON oi.order_id = o.order_id
    LEFT JOIN olist_order_reviews r 
        ON oi.order_id = r.order_id
    WHERE o.order_status NOT IN ('canceled', 'unavailable')
),
seller_summary AS (
    -- 2. Aggregate volume, financial metrics, and operational performance per seller
    SELECT 
        seller_id,
        COUNT(DISTINCT order_id) AS total_orders,
        COUNT(*) AS total_items_sold,
        ROUND(SUM(price), 2) AS total_revenue,
        ROUND(AVG(dispatch_turnaround_days), 1) AS avg_dispatch_days,
        ROUND((SUM(is_late_dispatch) / COUNT(*)) * 100, 2) AS late_dispatch_rate_pct,
        ROUND(AVG(review_score), 2) AS avg_seller_review_score
    FROM seller_orders
    GROUP BY seller_id
),
seller_cumulative AS (
    -- 3. Calculate running cumulative revenue to identify Pareto concentration
    SELECT 
        seller_id,
        total_orders,
        total_items_sold,
        total_revenue,
        avg_dispatch_days,
        late_dispatch_rate_pct,
        avg_seller_review_score,
        ROW_NUMBER() OVER (ORDER BY total_revenue DESC) AS revenue_rank,
        COUNT(*) OVER () AS total_seller_count,
        SUM(total_revenue) OVER () AS total_platform_revenue,
        SUM(total_revenue) OVER (ORDER BY total_revenue DESC) AS cumulative_revenue
    FROM seller_summary
),
seller_segmented AS (
    -- 4. Segment sellers into Pareto Tiers based on their cumulative revenue contribution
    SELECT 
        seller_id,
        revenue_rank,
        ROUND((revenue_rank / total_seller_count) * 100, 2) AS seller_percentile_rank,
        total_orders,
        total_items_sold,
        total_revenue,
        avg_dispatch_days,
        late_dispatch_rate_pct,
        avg_seller_review_score,
        ROUND((cumulative_revenue / total_platform_revenue) * 100, 2) AS cumulative_revenue_share_pct,
        CASE 
            WHEN (cumulative_revenue / total_platform_revenue) <= 0.20 THEN 'Tier 1: Top 20 Pct Revenue (Elite)'
            WHEN (cumulative_revenue / total_platform_revenue) <= 0.50 THEN 'Tier 2: Next 30 Pct Revenue (Core)'
            WHEN (cumulative_revenue / total_platform_revenue) <= 0.80 THEN 'Tier 3: Next 30 Pct Revenue (Growing)'
            ELSE 'Tier 4: Long Tail (Remaining 20 Pct)'
        END AS seller_pareto_tier
    FROM seller_cumulative
)
-- 5. Executive Tier Scorecard: Aggregate metrics across the Pareto Tiers
SELECT 
    seller_pareto_tier,
    COUNT(seller_id) AS seller_count,
    ROUND((COUNT(seller_id) / (SELECT COUNT(*) FROM seller_summary)) * 100, 2) AS pct_of_all_sellers,
    ROUND(SUM(total_revenue), 2) AS tier_total_revenue,
    ROUND(AVG(total_revenue), 2) AS avg_revenue_per_seller,
    ROUND(AVG(avg_dispatch_days), 1) AS avg_tier_dispatch_days,
    ROUND(AVG(late_dispatch_rate_pct), 2) AS avg_tier_late_dispatch_pct,
    ROUND(AVG(avg_seller_review_score), 2) AS avg_tier_review_score
FROM seller_segmented
GROUP BY seller_pareto_tier
ORDER BY tier_total_revenue DESC;
