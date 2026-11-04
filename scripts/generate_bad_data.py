"""Generate corrupted and anomalous records for testing data quality rules and quarantine handling.

This script intentionally creates fixtures with:
1. Duplicate primary keys and order records.
2. Missing foreign keys (e.g., non-existent customer_id).
3. Invalid quantities (negative or zero).
4. Invalid prices (negative unit_price or cost_price).
5. Unsupported status strings (e.g. 'UNKNOWN_STATE', 'IN_LIMBO').
"""
import argparse
import csv
from pathlib import Path


def generate_bad_data(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Corrupted Customers
    bad_customers = [
        {
            "customer_id": 999901,
            "first_name": "",  # Missing first name
            "last_name": "GhostUser",
            "email": "invalid-email-format",
            "phone": "00000",
            "city": "UnknownCity",
            "state": "UnknownState",
            "country": "Nowhere",
            "registration_date": "2099-01-01",  # Future date anomaly
            "created_at": "2099-01-01 00:00:00",
            "updated_at": "2099-01-01 00:00:00",
        },
        {
            "customer_id": 999902,
            "first_name": "Duplicate",
            "last_name": "Customer",
            "email": "duplicate@example.test",
            "phone": "+919800000000",
            "city": "Bengaluru",
            "state": "Karnataka",
            "country": "India",
            "registration_date": "2025-01-01",
            "created_at": "2025-01-01 00:00:00",
            "updated_at": "2025-01-01 00:00:00",
        },
        {  # Intentional duplicate ID to test uniqueness constraint
            "customer_id": 999902,
            "first_name": "DuplicateSecond",
            "last_name": "Customer",
            "email": "duplicate2@example.test",
            "phone": "+919800000001",
            "city": "Bengaluru",
            "state": "Karnataka",
            "country": "India",
            "registration_date": "2025-01-01",
            "created_at": "2025-01-01 00:00:00",
            "updated_at": "2025-01-01 00:00:00",
        },
    ]

    # 2. Corrupted Products (Negative prices, negative stock)
    bad_products = [
        {
            "product_id": 888801,
            "product_name": "Broken Negative Price Widget",
            "category": "Electronics",
            "brand": "FaultyBrand",
            "unit_price": -150.00,  # Negative price anomaly
            "cost_price": 50.00,
            "stock_quantity": 10,
            "created_at": "2025-01-01 00:00:00",
            "updated_at": "2025-01-01 00:00:00",
        },
        {
            "product_id": 888802,
            "product_name": "Negative Stock Gadget",
            "category": "Home",
            "brand": "FaultyBrand",
            "unit_price": 299.00,
            "cost_price": 100.00,
            "stock_quantity": -5,  # Negative stock anomaly
            "created_at": "2025-01-01 00:00:00",
            "updated_at": "2025-01-01 00:00:00",
        },
    ]

    # 3. Corrupted Orders (Orphan customer, unsupported status)
    bad_orders = [
        {
            "order_id": 777701,
            "customer_id": 9999999,  # Orphan: customer doesn't exist in base DB
            "order_date": "2025-06-01 10:00:00",
            "order_status": "UNKNOWN_GARBAGE_STATUS",  # Unsupported status
            "payment_method": "BITCOIN",
            "shipping_city": "Atlantis",
            "shipping_state": "Ocean",
            "created_at": "2025-06-01 10:00:00",
            "updated_at": "2025-06-01 10:00:00",
        }
    ]

    # 4. Corrupted Order Items (Zero/negative quantity)
    bad_order_items = [
        {
            "order_item_id": 666601,
            "order_id": 777701,
            "product_id": 1,
            "quantity": -2,  # Negative quantity anomaly
            "unit_price": 999.00,
            "discount_amount": 0,
            "created_at": "2025-06-01 10:00:00",
            "updated_at": "2025-06-01 10:00:00",
        },
        {
            "order_item_id": 666602,
            "order_id": 777701,
            "product_id": 1,
            "quantity": 0,  # Zero quantity anomaly
            "unit_price": 999.00,
            "discount_amount": 0,
            "created_at": "2025-06-01 10:00:00",
            "updated_at": "2025-06-01 10:00:00",
        },
    ]

    # 5. Corrupted Payments (Negative payment amount)
    bad_payments = [
        {
            "payment_id": 555501,
            "order_id": 777701,
            "payment_method": "UNKNOWN",
            "payment_amount": -500.00,  # Negative amount anomaly
            "payment_status": "CORRUPTED",
            "transaction_date": "2025-06-01 10:00:00",
            "created_at": "2025-06-01 10:00:00",
            "updated_at": "2025-06-01 10:00:00",
        }
    ]

    datasets = [
        ("bad_customers.csv", bad_customers),
        ("bad_products.csv", bad_products),
        ("bad_orders.csv", bad_orders),
        ("bad_order_items.csv", bad_order_items),
        ("bad_payments.csv", bad_payments),
    ]

    for filename, rows in datasets:
        path = output_dir / filename
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
        print(f"Generated {len(rows)} bad records -> {path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate bad records for testing data quality filters.")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("tests/fixtures/corrupted"),
        help="Target folder for anomalous/corrupted CSV files.",
    )
    args = parser.parse_args()
    generate_bad_data(args.output)

