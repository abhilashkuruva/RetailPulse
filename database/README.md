# RetailPulse Database Architecture & Setup

## Overview
RetailPulse uses **MySQL 8.x** as the primary OLTP (Online Transaction Processing) operational database. It models an end-to-end e-commerce store with high-integrity referential constraints, timestamp watermarks, and indexing strategies optimized for batch CDC (Change Data Capture) extraction.

---

## Entity Relationship Summary
```
+---------------+        1:N        +------------+        1:N        +---------------+
|   CUSTOMERS   | ----------------< |   ORDERS   | ----------------< |  ORDER_ITEMS  |
+---------------+                   +------------+                   +---------------+
                                          |                                  |
                                          | 1:N                              | N:1
                                          v                                  v
                                    +------------+                   +---------------+
                                    |  PAYMENTS  |                   |   PRODUCTS    |
                                    +------------+                   +---------------+
```

---

## Tables and Schema Details

### 1. `customers`
Stores customer master profile and registration details.
- `customer_id` (BIGINT, PK): Unique customer identifier.
- `first_name`, `last_name` (VARCHAR(80)): Customer full name.
- `email` (VARCHAR(255), UNIQUE): Unique contact email address.
- `phone` (VARCHAR(30)): Contact telephone number.
- `city`, `state`, `country` (VARCHAR(80)): Geographical residence details.
- `registration_date` (DATE): Onboarding date.
- `created_at`, `updated_at` (TIMESTAMP): Watermark audit timestamps with automatic `ON UPDATE CURRENT_TIMESTAMP`.

### 2. `products`
Catalog of merchandise available for sale.
- `product_id` (BIGINT, PK): Unique product identifier.
- `product_name` (VARCHAR(200)): Product display name.
- `category` (VARCHAR(80)): Classification taxonomy (Electronics, Fashion, Home, etc.).
- `brand` (VARCHAR(100)): Manufacturer or brand label.
- `unit_price` (DECIMAL(12,2)): Retail sale price.
- `cost_price` (DECIMAL(12,2)): Cost of goods sold (COGS) to calculate margin.
- `stock_quantity` (INT): Current inventory balance.
- `created_at`, `updated_at` (TIMESTAMP): Watermarks.

### 3. `orders`
Header table for customer transaction purchase orders.
- `order_id` (BIGINT, PK): Unique order reference.
- `customer_id` (BIGINT, FK -> `customers.customer_id`): Customer placing the order.
- `order_date` (DATETIME): Timestamp when order was placed.
- `order_status` (VARCHAR(30)): Status (`pending`, `confirmed`, `shipped`, `delivered`, `cancelled`, `returned`).
- `payment_method` (VARCHAR(30)): Payment channel (`UPI`, `CREDIT_CARD`, `DEBIT_CARD`, `COD`, `NETBANKING`).
- `shipping_city`, `shipping_state` (VARCHAR(80)): Delivery destination.
- `created_at`, `updated_at` (TIMESTAMP): Watermarks with indexing on `updated_at` for incremental ELT.

### 4. `order_items`
Line-item detail for each product ordered.
- `order_item_id` (BIGINT, PK): Line item identifier.
- `order_id` (BIGINT, FK -> `orders.order_id`): Parent order.
- `product_id` (BIGINT, FK -> `products.product_id`): Item purchased.
- `quantity` (INT): Item count (> 0).
- `unit_price` (DECIMAL(12,2)): Unit price snapshot at time of purchase.
- `discount_amount` (DECIMAL(12,2)): Concession or promotional discount.
- `created_at`, `updated_at` (TIMESTAMP): Watermarks.

### 5. `payments`
Ledger of financial settlements per order.
- `payment_id` (BIGINT, PK): Unique transaction identifier.
- `order_id` (BIGINT, FK -> `orders.order_id`): Associated order.
- `payment_method` (VARCHAR(30)): Instrument used.
- `payment_amount` (DECIMAL(12,2)): Captured sum.
- `payment_status` (VARCHAR(30)): `success`, `pending`, `failed`, `refunded`.
- `transaction_date` (DATETIME): Gateway confirmation time.
- `created_at`, `updated_at` (TIMESTAMP): Watermarks.

### 6. `pipeline_metadata`
Operational audit trail for the Python Ingestion Service.
- `execution_id` (VARCHAR(64), PK): Unique run ID (UUID or timestamp).
- `source_table` (VARCHAR(80)): Table extracted.
- `last_successful_extraction_timestamp` (TIMESTAMP): Incremental watermark marker.
- `records_extracted` (BIGINT): Extracted record tally.
- `records_loaded` (BIGINT): Ingested count.
- `execution_status` (VARCHAR(20)): `RUNNING`, `SUCCESS`, `FAILED`.
- `started_at`, `completed_at` (TIMESTAMP): Pipeline timing metrics.
- `error_message` (TEXT): Diagnostics if failed.

---

## Indexes & Watermarking Strategy
Every table incorporates:
1. Primary key indexes for point lookups and referential validation.
2. Foreign key indexes on `customer_id`, `order_id`, and `product_id` to eliminate table locks and enable fast relational queries.
3. B-Tree index on `updated_at` (`INDEX idx_*_updated_at (updated_at)`):
   This enables MySQL to execute range scans (`WHERE updated_at >= :watermark`) in logarithmic time $O(\log N)$ rather than scanning the entire table.

---

## Idempotent Bootstrap
The database initialization script `scripts/init_database.py` guarantees:
- Re-executing never causes duplicate records (uses `ON DUPLICATE KEY UPDATE`).
- Verifies foreign-key integrity.
- Prints validation counts for all tables.
