# RetailPulse Sample Datasets & Fixtures

## Overview
The `data/` directory contains generated realistic synthetic datasets simulating a high-volume Indian e-commerce marketplace (RetailPulse).

### Standard Datasets (`data/exports/*.csv`)
Generated deterministically with fixed random seeds for testing and reproducibility:
- **`customers.csv`** (1,000 records): Indian shoppers across 10 major metropolitan hubs (Bengaluru, Mumbai, Delhi, Hyderabad, Chennai, Pune, Kolkata, Ahmedabad, Jaipur, Kochi). Includes validated phone numbers, emails, and registration dates.
- **`products.csv`** (200 records): Merchandise distributed across Electronics, Fashion, Home & Kitchen, Beauty & Wellness, and Sports & Fitness categories, with realistic unit prices, cost of goods sold (COGS), and inventory levels.
- **`orders.csv`** (5,000 records): Transaction orders spanning 2025 with multiple statuses (`confirmed`, `shipped`, `delivered`, `cancelled`, `returned`) and payment channels (`UPI`, `CREDIT_CARD`, `DEBIT_CARD`, `COD`, `NETBANKING`).
- **`order_items.csv`** (9,901 records): Line items mapped 1:N from orders to products, incorporating volume quantities and promotional discounts.
- **`payments.csv`** (5,000 records): Financial ledger entries matching order amounts, tracking settlement statuses (`success`, `pending`, `failed`).

### Corrupted Test Fixtures (`tests/fixtures/corrupted/*.csv`)
Engineered specifically for Data Quality (DQ) testing and pipeline resilience validation:
- **`bad_customers.csv`**: Demonstrates missing required fields (empty `first_name`), invalid email regex format, and intentional duplicate customer IDs to test primary key deduplication.
- **`bad_products.csv`**: Demonstrates negative unit prices (`-150.00`) and negative inventory balances (`-5`).
- **`bad_orders.csv`**: Demonstrates orphaned orders (customer ID does not exist in master customer table) and unmapped status values (`UNKNOWN_GARBAGE_STATUS`).
- **`bad_order_items.csv`**: Demonstrates zero and negative purchase quantities.
- **`bad_payments.csv`**: Demonstrates negative transaction amounts and corrupted statuses.

### Generating Fixtures
```bash
# Generate clean production dataset
python scripts/generate_data.py --customers 1000 --products 200 --orders 5000

# Generate corrupted demonstration fixtures
python scripts/generate_bad_data.py --output tests/fixtures/corrupted
```

