-- ==============================================================================
-- RETAILPULSE WAREHOUSE VALIDATION & DATA AUDIT QUERIES
-- Asserts schema invariants, row counts, partition metadata, and referential integrity
-- ==============================================================================

-- 1. ROW COUNT AUDIT ACROSS ALL LAYERS
SELECT 'raw.customers' AS table_name, COUNT(*) AS row_count FROM `retailpulse_raw.customers`
UNION ALL
SELECT 'raw.products', COUNT(*) FROM `retailpulse_raw.products`
UNION ALL
SELECT 'raw.orders', COUNT(*) FROM `retailpulse_raw.orders`
UNION ALL
SELECT 'raw.order_items', COUNT(*) FROM `retailpulse_raw.order_items`
UNION ALL
SELECT 'raw.payments', COUNT(*) FROM `retailpulse_raw.payments`
UNION ALL
SELECT 'analytics.dim_customers', COUNT(*) FROM `retailpulse_analytics.dim_customers`
UNION ALL
SELECT 'analytics.dim_products', COUNT(*) FROM `retailpulse_analytics.dim_products`
UNION ALL
SELECT 'analytics.fct_orders', COUNT(*) FROM `retailpulse_analytics.fct_orders`
UNION ALL
SELECT 'analytics.fct_payments', COUNT(*) FROM `retailpulse_analytics.fct_payments`;

-- 2. PARTITION METADATA VERIFICATION (BigQuery INFORMATION_SCHEMA)
-- Confirms physical partitions exist for orders table
SELECT
    project_id,
    dataset_id,
    table_name,
    partition_id,
    total_rows,
    ROUND(total_logical_bytes / 1024 / 1024, 2) AS logical_size_mb,
    last_modified_time
FROM `retailpulse_raw.INFORMATION_SCHEMA.PARTITIONS`
WHERE table_name = 'orders'
  AND partition_id NOT IN ('__NULL__', '__UNPARTITIONED__')
ORDER BY partition_id DESC
LIMIT 20;

-- 3. ZERO-ORPHAN FOREIGN KEY ASSERTION (Fact Orders -> Dim Customers)
SELECT
    COUNT(*) AS orphan_orders_count
FROM `retailpulse_analytics.fct_orders` o
LEFT JOIN `retailpulse_analytics.dim_customers` c
    ON o.customer_id = c.customer_id
WHERE c.customer_id IS NULL;

-- 4. FINANCIAL RECONCILIATION ASSERTION (Order Total vs Line Item Aggregates)
-- Asserts that captured order total equals sum of line items within acceptable rounding tolerance
WITH item_totals AS (
    SELECT
        order_id,
        ROUND(SUM(quantity * unit_price - discount_amount), 2) AS calculated_items_total
    FROM `retailpulse_raw.order_items`
    GROUP BY order_id
)
SELECT
    o.order_id,
    o.total_amount AS order_header_total,
    i.calculated_items_total,
    ROUND(ABS(o.total_amount - i.calculated_items_total), 2) AS variance
FROM `retailpulse_analytics.fct_orders` o
JOIN item_totals i ON o.order_id = i.order_id
WHERE ABS(o.total_amount - i.calculated_items_total) > 0.05;

-- 5. DUPLICATE PRIMARY KEY INTEGRITY ASSERTION (Unique Grain Test)
SELECT
    order_id,
    COUNT(*) AS duplicate_instances
FROM `retailpulse_analytics.fct_orders`
GROUP BY order_id
HAVING COUNT(*) > 1;

