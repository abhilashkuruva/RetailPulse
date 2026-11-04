-- ==============================================================================
-- RETAILPULSE BIGQUERY TABLE DEFINITIONS WITH PARTITIONING & CLUSTERING
-- Project: RetailPulse Production Analytics Warehouse
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- 1. RAW LAYER: customers
-- Architecture Note: Dimension table. Unpartitioned because the table contains ~1k - 50k
-- customer records. Partitioning small tables (< 1 GB) introduces query overhead and
-- exceeds the 4,000 partition limit per table without providing performance benefit.
-- Clustered by customer_id for fast point lookups and join pruning.
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `retailpulse_raw.customers` (
  customer_id INT64 NOT NULL,
  first_name STRING NOT NULL,
  last_name STRING NOT NULL,
  email STRING NOT NULL,
  phone STRING,
  city STRING NOT NULL,
  state STRING NOT NULL,
  country STRING NOT NULL,
  registration_date DATE NOT NULL,
  created_at TIMESTAMP NOT NULL,
  updated_at TIMESTAMP NOT NULL,
  batch_id STRING,
  source_file STRING,
  ingestion_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
CLUSTER BY customer_id
OPTIONS (
  description = 'Raw ingested customer records from MySQL CDC'
);

-- ------------------------------------------------------------------------------
-- 2. RAW LAYER: products
-- Architecture Note: Dimension table (< 10k rows). Unpartitioned to avoid fragmentation.
-- Clustered by category and brand to optimize analytical filtering in product marts.
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `retailpulse_raw.products` (
  product_id INT64 NOT NULL,
  product_name STRING NOT NULL,
  category STRING NOT NULL,
  brand STRING NOT NULL,
  unit_price NUMERIC NOT NULL,
  cost_price NUMERIC NOT NULL,
  stock_quantity INT64 NOT NULL,
  created_at TIMESTAMP NOT NULL,
  updated_at TIMESTAMP NOT NULL,
  batch_id STRING,
  source_file STRING,
  ingestion_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
CLUSTER BY category, brand
OPTIONS (
  description = 'Raw ingested product catalog records from MySQL CDC'
);

-- ------------------------------------------------------------------------------
-- 3. RAW LAYER: orders (HIGH VOLUME TRANSACTION FACT)
-- Architecture Note:
--   PARTITION BY DATE(order_date): Partitions physical storage blocks by calendar day.
--     Queries filtering on order_date (e.g. daily/monthly revenue) prune 99% of storage,
--     reducing BigQuery bytes scanned and billing costs to zero for untouched days.
--   CLUSTER BY customer_id, order_status: Orders within each partition are colocated
--     by customer and status, accelerating joins with customer dimension and status filters.
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `retailpulse_raw.orders` (
  order_id INT64 NOT NULL,
  customer_id INT64 NOT NULL,
  order_date DATETIME NOT NULL,
  order_status STRING NOT NULL,
  payment_method STRING NOT NULL,
  shipping_city STRING NOT NULL,
  shipping_state STRING NOT NULL,
  created_at TIMESTAMP NOT NULL,
  updated_at TIMESTAMP NOT NULL,
  batch_id STRING,
  source_file STRING,
  ingestion_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY DATE(order_date)
CLUSTER BY customer_id, order_status
OPTIONS (
  description = 'Raw ingested order transaction headers partitioned by day and clustered by customer and status'
);

-- ------------------------------------------------------------------------------
-- 4. RAW LAYER: order_items (LINE-ITEM FACT)
-- Architecture Note:
--   CLUSTER BY order_id, product_id: High cardinality line items. Clustered by order_id
--   to enable co-located block reads when joining with the parent orders table.
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `retailpulse_raw.order_items` (
  order_item_id INT64 NOT NULL,
  order_id INT64 NOT NULL,
  product_id INT64 NOT NULL,
  quantity INT64 NOT NULL,
  unit_price NUMERIC NOT NULL,
  discount_amount NUMERIC NOT NULL,
  created_at TIMESTAMP NOT NULL,
  updated_at TIMESTAMP NOT NULL,
  batch_id STRING,
  source_file STRING,
  ingestion_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
CLUSTER BY order_id, product_id
OPTIONS (
  description = 'Raw ingested order line-item details clustered by order and product'
);

-- ------------------------------------------------------------------------------
-- 5. RAW LAYER: payments (FINANCIAL TRANSACTION FACT)
-- Architecture Note:
--   PARTITION BY DATE(transaction_date): Daily financial settlement reconciliation.
--   CLUSTER BY order_id, payment_status: Speeds up order reconciliation and dispute queries.
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `retailpulse_raw.payments` (
  payment_id INT64 NOT NULL,
  order_id INT64 NOT NULL,
  payment_method STRING NOT NULL,
  payment_amount NUMERIC NOT NULL,
  payment_status STRING NOT NULL,
  transaction_date DATETIME NOT NULL,
  created_at TIMESTAMP NOT NULL,
  updated_at TIMESTAMP NOT NULL,
  batch_id STRING,
  source_file STRING,
  ingestion_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY DATE(transaction_date)
CLUSTER BY order_id, payment_status
OPTIONS (
  description = 'Raw ingested payment records partitioned by transaction date'
);

-- ------------------------------------------------------------------------------
-- 6. DATA QUALITY MONITORING LEDGER
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `retailpulse_analytics.data_quality_results` (
  execution_id STRING NOT NULL,
  model_name STRING NOT NULL,
  test_name STRING NOT NULL,
  test_status STRING NOT NULL,
  failed_record_count INT64 NOT NULL,
  execution_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  error_details STRING
)
PARTITION BY DATE(execution_timestamp)
CLUSTER BY model_name, test_status
OPTIONS (
  description = 'Automated data quality and contract verification test audit trail'
);

