-- ==============================================================================
-- RETAILPULSE BUSINESS INTELLIGENCE & ANALYTICAL SQL QUERIES
-- High-Performance Production Queries Demonstrating Partition Pruning & Aggregations
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- 1. DAILY REVENUE AND ORDER VOLUME (Demonstrating Partition Pruning)
-- Prunes full table scan by leveraging PARTITION BY DATE(order_date).
-- Only blocks corresponding to 2025-01-01 through 2025-01-31 are scanned from GCS/Colossus.
-- ------------------------------------------------------------------------------
SELECT
    DATE(o.order_date) AS order_day,
    COUNT(DISTINCT o.order_id) AS total_orders,
    COUNT(DISTINCT CASE WHEN o.order_status = 'delivered' THEN o.order_id END) AS delivered_orders,
    ROUND(SUM(oi.quantity * oi.unit_price - oi.discount_amount), 2) AS gross_revenue,
    ROUND(AVG(oi.quantity * oi.unit_price - oi.discount_amount), 2) AS avg_item_revenue
FROM `retailpulse_analytics.fct_orders` o
JOIN `retailpulse_raw.order_items` oi
    ON o.order_id = oi.order_id
WHERE DATE(o.order_date) BETWEEN '2025-01-01' AND '2025-01-31'
  AND o.order_status != 'cancelled'
GROUP BY 1
ORDER BY order_day ASC;

-- ------------------------------------------------------------------------------
-- 2. MONTHLY REVENUE AND MONTH-OVER-MONTH (MoM) GROWTH
-- Demonstrates SQL Window functions (LAG) to compute revenue growth percentage.
-- ------------------------------------------------------------------------------
WITH monthly_metrics AS (
    SELECT
        DATE_TRUNC(DATE(order_date), MONTH) AS order_month,
        COUNT(DISTINCT order_id) AS order_count,
        ROUND(SUM(total_amount), 2) AS total_revenue
    FROM `retailpulse_analytics.fct_orders`
    WHERE order_status NOT IN ('cancelled', 'returned')
    GROUP BY 1
)
SELECT
    order_month,
    order_count,
    total_revenue,
    LAG(total_revenue, 1) OVER (ORDER BY order_month) AS prior_month_revenue,
    ROUND(
        (total_revenue - LAG(total_revenue, 1) OVER (ORDER BY order_month))
        / NULLIF(LAG(total_revenue, 1) OVER (ORDER BY order_month), 0) * 100, 2
    ) AS mom_growth_pct
FROM monthly_metrics
ORDER BY order_month ASC;

-- ------------------------------------------------------------------------------
-- 3. REVENUE BY GEOGRAPHIC CITY & STATE
-- Identifies top metropolitan consumer markets across India.
-- ------------------------------------------------------------------------------
SELECT
    c.city,
    c.state,
    COUNT(DISTINCT o.order_id) AS total_orders,
    COUNT(DISTINCT o.customer_id) AS unique_purchasers,
    ROUND(SUM(o.total_amount), 2) AS total_revenue,
    ROUND(SUM(o.total_amount) / NULLIF(COUNT(DISTINCT o.order_id), 0), 2) AS avg_order_value
FROM `retailpulse_analytics.fct_orders` o
JOIN `retailpulse_analytics.dim_customers` c
    ON o.customer_id = c.customer_id
WHERE o.order_status != 'cancelled'
GROUP BY 1, 2
ORDER BY total_revenue DESC
LIMIT 15;

-- ------------------------------------------------------------------------------
-- 4. REVENUE BY PRODUCT CATEGORY & MARGIN ANALYSIS
-- Combines retail pricing with cost price (COGS) to calculate gross margin.
-- ------------------------------------------------------------------------------
SELECT
    p.category,
    COUNT(DISTINCT oi.order_id) AS orders_containing_category,
    SUM(oi.quantity) AS total_units_sold,
    ROUND(SUM(oi.quantity * oi.unit_price - oi.discount_amount), 2) AS total_sales,
    ROUND(SUM(oi.quantity * p.cost_price), 2) AS total_cogs,
    ROUND(
        SUM(oi.quantity * oi.unit_price - oi.discount_amount) - SUM(oi.quantity * p.cost_price), 2
    ) AS gross_profit,
    ROUND(
        (SUM(oi.quantity * oi.unit_price - oi.discount_amount) - SUM(oi.quantity * p.cost_price))
        / NULLIF(SUM(oi.quantity * oi.unit_price - oi.discount_amount), 0) * 100, 2
    ) AS gross_margin_pct
FROM `retailpulse_raw.order_items` oi
JOIN `retailpulse_analytics.dim_products` p
    ON oi.product_id = p.product_id
JOIN `retailpulse_analytics.fct_orders` o
    ON oi.order_id = o.order_id
WHERE o.order_status NOT IN ('cancelled', 'returned')
GROUP BY 1
ORDER BY total_sales DESC;

-- ------------------------------------------------------------------------------
-- 5. TOP 10 BEST-SELLING PRODUCTS BY VOLUME & REVENUE
-- Demonstrates DENSE_RANK() window function.
-- ------------------------------------------------------------------------------
WITH product_sales AS (
    SELECT
        p.product_id,
        p.product_name,
        p.category,
        p.brand,
        SUM(oi.quantity) AS units_sold,
        ROUND(SUM(oi.quantity * oi.unit_price - oi.discount_amount), 2) AS total_revenue
    FROM `retailpulse_raw.order_items` oi
    JOIN `retailpulse_analytics.dim_products` p
        ON oi.product_id = p.product_id
    JOIN `retailpulse_analytics.fct_orders` o
        ON oi.order_id = o.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY 1, 2, 3, 4
)
SELECT
    product_id,
    product_name,
    category,
    brand,
    units_sold,
    total_revenue,
    DENSE_RANK() OVER (ORDER BY total_revenue DESC) AS revenue_rank
FROM product_sales
ORDER BY revenue_rank ASC
LIMIT 10;

-- ------------------------------------------------------------------------------
-- 6. ORDER COUNTS BY STATUS & FULFILLMENT RATE
-- ------------------------------------------------------------------------------
SELECT
    order_status,
    COUNT(*) AS order_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS percentage_of_total
FROM `retailpulse_analytics.fct_orders`
GROUP BY 1
ORDER BY order_count DESC;

-- ------------------------------------------------------------------------------
-- 7. CANCELLED ORDERS & LOSS ANALYSIS BY REGION
-- ------------------------------------------------------------------------------
SELECT
    shipping_city,
    shipping_state,
    COUNT(order_id) AS cancelled_orders,
    ROUND(SUM(total_amount), 2) AS lost_potential_revenue
FROM `retailpulse_analytics.fct_orders`
WHERE order_status = 'cancelled'
GROUP BY 1, 2
ORDER BY cancelled_orders DESC
LIMIT 10;

-- ------------------------------------------------------------------------------
-- 8. CUSTOMER PURCHASE FREQUENCY & REPEAT PURCHASE COHORT
-- Segregates one-time buyers from high-value repeat shoppers.
-- ------------------------------------------------------------------------------
WITH customer_orders AS (
    SELECT
        customer_id,
        COUNT(order_id) AS lifetime_orders,
        SUM(total_amount) AS lifetime_spend
    FROM `retailpulse_analytics.fct_orders`
    WHERE order_status != 'cancelled'
    GROUP BY 1
)
SELECT
    CASE
        WHEN lifetime_orders = 1 THEN '1. One-time Purchaser'
        WHEN lifetime_orders BETWEEN 2 AND 4 THEN '2. Casual Repeat (2-4 orders)'
        WHEN lifetime_orders BETWEEN 5 AND 9 THEN '3. Frequent Buyer (5-9 orders)'
        ELSE '4. VIP Power Buyer (10+ orders)'
    END AS customer_segment,
    COUNT(customer_id) AS customer_count,
    ROUND(SUM(lifetime_spend), 2) AS segment_revenue,
    ROUND(AVG(lifetime_spend), 2) AS avg_customer_value
FROM customer_orders
GROUP BY 1
ORDER BY customer_segment ASC;

-- ------------------------------------------------------------------------------
-- 9. AVERAGE ORDER VALUE (AOV) TREND BY PAYMENT METHOD
-- ------------------------------------------------------------------------------
SELECT
    payment_method,
    COUNT(order_id) AS total_orders,
    ROUND(SUM(total_amount), 2) AS total_spend,
    ROUND(AVG(total_amount), 2) AS average_order_value
FROM `retailpulse_analytics.fct_orders`
WHERE order_status != 'cancelled'
GROUP BY 1
ORDER BY total_spend DESC;

-- ------------------------------------------------------------------------------
-- 10. PAYMENT CONVERSION & SUCCESS RATE BY GATEWAY CHANNEL
-- ------------------------------------------------------------------------------
SELECT
    payment_method,
    COUNT(*) AS total_transactions,
    COUNTIF(payment_status = 'success') AS successful_payments,
    COUNTIF(payment_status = 'failed') AS failed_payments,
    COUNTIF(payment_status = 'pending') AS pending_payments,
    ROUND(COUNTIF(payment_status = 'success') * 100.0 / NULLIF(COUNT(*), 0), 2) AS success_rate_pct
FROM `retailpulse_analytics.fct_payments`
GROUP BY 1
ORDER BY total_transactions DESC;
