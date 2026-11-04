-- ==============================================================================
-- RETAILPULSE LOOKER STUDIO CURATED REPORTING VIEWS
-- Optimized Flat Reporting Views for Real-Time BI Visualizations
-- ==============================================================================

-- 1. Executive Summary BI View
CREATE OR REPLACE VIEW `retailpulse_analytics.vw_looker_executive_kpis` AS
SELECT
    DATE(o.order_date) AS order_date,
    o.order_id,
    o.customer_id,
    c.full_name AS customer_name,
    c.city AS customer_city,
    c.state AS customer_state,
    c.customer_loyalty_segment,
    c.customer_value_tier,
    o.order_status,
    o.payment_method,
    o.total_amount,
    o.total_units_ordered,
    o.is_delivered,
    o.is_cancelled_or_returned,
    p.payment_status
FROM `retailpulse_analytics.fct_orders` o
JOIN `retailpulse_analytics.dim_customers` c
    ON o.customer_id = c.customer_id
LEFT JOIN `retailpulse_analytics.fct_payments` p
    ON o.order_id = p.order_id;

-- 2. Product Merchandise Performance View
CREATE OR REPLACE VIEW `retailpulse_analytics.vw_looker_product_sales` AS
SELECT
    DATE(o.order_date) AS sale_date,
    p.product_id,
    p.product_name,
    p.category,
    p.brand,
    p.unit_price,
    p.cost_price,
    p.unit_margin,
    oi.quantity AS units_sold,
    oi.gross_amount,
    oi.discount_amount,
    oi.net_amount AS revenue_generated,
    (oi.quantity * p.cost_price) AS cogs_total,
    (oi.net_amount - (oi.quantity * p.cost_price)) AS gross_profit,
    o.shipping_city,
    o.shipping_state
FROM `retailpulse_raw.order_items` oi
JOIN `retailpulse_analytics.dim_products` p
    ON oi.product_id = p.product_id
JOIN `retailpulse_analytics.fct_orders` o
    ON oi.order_id = o.order_id
WHERE o.order_status NOT IN ('cancelled', 'returned');

