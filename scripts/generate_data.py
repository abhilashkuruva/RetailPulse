"""Generate deterministic, referentially valid RetailPulse CSV fixtures."""
import argparse
import csv
import random
from datetime import datetime, timedelta
from pathlib import Path


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def generate(
    output: Path,
    customers_count: int = 1000,
    products_count: int = 200,
    orders_count: int = 5000,
    seed: int = 42,
) -> None:
    rng = random.Random(seed)
    output.mkdir(parents=True, exist_ok=True)

    indian_cities = [
        ("Hyderabad", "Telangana"),
        ("Bengaluru", "Karnataka"),
        ("Chennai", "Tamil Nadu"),
        ("Mumbai", "Maharashtra"),
        ("Delhi", "Delhi"),
        ("Pune", "Maharashtra"),
        ("Kolkata", "West Bengal"),
        ("Ahmedabad", "Gujarat"),
        ("Jaipur", "Rajasthan"),
        ("Kochi", "Kerala"),
    ]

    first_names = [
        "Aarav", "Aditi", "Kabir", "Ananya", "Rohan", "Ishita", "Vikram", "Meera",
        "Siddharth", "Pooja", "Arjun", "Priya", "Rahul", "Neha", "Amit", "Sneha",
        "Karan", "Tanvi", "Varun", "Rhea", "Nikhil", "Divya", "Gaurav", "Shreya"
    ]
    last_names = [
        "Sharma", "Verma", "Patel", "Reddy", "Rao", "Nair", "Mehta", "Iyer",
        "Mukherjee", "Chatterjee", "Gupta", "Malhotra", "Joshi", "Bhat", "Deshmukh"
    ]

    # 1. Customers
    customers = []
    base_reg_date = datetime(2024, 1, 1)
    for customer_id in range(1, customers_count + 1):
        city, state = rng.choice(indian_cities)
        first = rng.choice(first_names)
        last = rng.choice(last_names)
        reg_date = base_reg_date + timedelta(days=rng.randint(0, 400))
        reg_str = reg_date.strftime("%Y-%m-%d")
        timestamp_str = reg_date.strftime("%Y-%m-%d %H:%M:%S")

        customers.append({
            "customer_id": customer_id,
            "first_name": first,
            "last_name": f"{last}_{customer_id}",
            "email": f"{first.lower()}.{last.lower()}.{customer_id}@retailpulse.example.in",
            "phone": f"+9198{rng.randint(10000000, 99999999)}",
            "city": city,
            "state": state,
            "country": "India",
            "registration_date": reg_str,
            "created_at": timestamp_str,
            "updated_at": timestamp_str,
        })

    # 2. Products
    categories = {
        "Electronics": ["Smartphone", "Wireless Earbuds", "Smartwatch", "Laptop Stand", "Power Bank", "Bluetooth Speaker"],
        "Fashion": ["Cotton T-Shirt", "Slim Fit Denim", "Running Shoes", "Leather Wallet", "Analog Watch"],
        "Home & Kitchen": ["Air Fryer", "Stainless Steel Bottle", "Coffee Maker", "Ceramic Dinner Set", "Bed Linen"],
        "Beauty & Wellness": ["Vitamin C Serum", "Moisturizing Cream", "Sunscreen SPF50", "Herbal Shampoo"],
        "Sports & Fitness": ["Yoga Mat", "Dumbbell Set 10kg", "Resistance Bands", "Gym Duffle Bag"],
    }
    brands = ["PulseTech", "AuraFit", "UrbanLiving", "TerraCare", "ZephyrStyle", "TitanCraft", "EchoWave", "NovaPure"]

    products = []
    for product_id in range(1, products_count + 1):
        cat = rng.choice(list(categories.keys()))
        prod_title = rng.choice(categories[cat])
        brand = rng.choice(brands)
        if cat == "Electronics":
            price = round(rng.uniform(999.0, 49999.0), 2)
        elif cat == "Fashion":
            price = round(rng.uniform(499.0, 4999.0), 2)
        elif cat == "Home & Kitchen":
            price = round(rng.uniform(399.0, 8999.0), 2)
        elif cat == "Beauty & Wellness":
            price = round(rng.uniform(199.0, 1999.0), 2)
        else:
            price = round(rng.uniform(299.0, 6999.0), 2)

        cost = round(price * rng.uniform(0.55, 0.75), 2)
        stock = rng.randint(20, 1000)
        prod_time = "2024-01-01 00:00:00"

        products.append({
            "product_id": product_id,
            "product_name": f"{brand} {prod_title} v{product_id}",
            "category": cat,
            "brand": brand,
            "unit_price": price,
            "cost_price": cost,
            "stock_quantity": stock,
            "created_at": prod_time,
            "updated_at": prod_time,
        })

    # 3. Orders, Order Items, and Payments
    orders, order_items, payments = [], [], []
    order_base_date = datetime(2025, 1, 1)
    order_statuses = ["confirmed", "shipped", "delivered", "delivered", "delivered", "cancelled", "returned"]
    payment_methods = ["UPI", "UPI", "CREDIT_CARD", "DEBIT_CARD", "NETBANKING", "COD"]

    item_id_counter = 1
    payment_id_counter = 1

    for order_id in range(1, orders_count + 1):
        customer = rng.choice(customers)
        city, state = customer["city"], customer["state"]
        order_days = rng.randint(0, 365)
        order_dt = order_base_date + timedelta(days=order_days, hours=rng.randint(0, 23), minutes=rng.randint(0, 59))
        order_str = order_dt.strftime("%Y-%m-%d %H:%M:%S")

        status = rng.choice(order_statuses)
        pay_method = rng.choice(payment_methods)

        orders.append({
            "order_id": order_id,
            "customer_id": customer["customer_id"],
            "order_date": order_str,
            "order_status": status,
            "payment_method": pay_method,
            "shipping_city": city,
            "shipping_state": state,
            "created_at": order_str,
            "updated_at": order_str,
        })

        # Average 2 items per order to achieve ~10,000 order items across 5,000 orders
        num_items = rng.choices([1, 2, 3, 4], weights=[40, 40, 15, 5])[0]
        order_total = 0.0

        for _ in range(num_items):
            product = rng.choice(products)
            qty = rng.choices([1, 2, 3, 5], weights=[70, 20, 8, 2])[0]
            unit_price = product["unit_price"]
            discount = round(unit_price * qty * rng.choice([0.0, 0.05, 0.10, 0.15]), 2)
            item_total = (unit_price * qty) - discount
            order_total += item_total

            order_items.append({
                "order_item_id": item_id_counter,
                "order_id": order_id,
                "product_id": product["product_id"],
                "quantity": qty,
                "unit_price": unit_price,
                "discount_amount": discount,
                "created_at": order_str,
                "updated_at": order_str,
            })
            item_id_counter += 1

        order_total = round(order_total, 2)

        # Payment record
        if status == "cancelled":
            payment_status = "failed"
        elif pay_method == "COD" and status in ["confirmed", "shipped"]:
            payment_status = "pending"
        else:
            payment_status = "success"

        payments.append({
            "payment_id": payment_id_counter,
            "order_id": order_id,
            "payment_method": pay_method,
            "payment_amount": order_total,
            "payment_status": payment_status,
            "transaction_date": order_str,
            "created_at": order_str,
            "updated_at": order_str,
        })
        payment_id_counter += 1

    tables_data = [
        ("customers", customers),
        ("products", products),
        ("orders", orders),
        ("order_items", order_items),
        ("payments", payments),
    ]

    for name, rows in tables_data:
        csv_file = output / f"{name}.csv"
        write_csv(csv_file, rows)
        print(f"Generated {len(rows):>6} rows for {name:<12} -> {csv_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate realistic e-commerce synthetic data.")
    parser.add_argument("--output", type=Path, default=Path("data/exports"))
    parser.add_argument("--customers", type=int, default=1000)
    parser.add_argument("--products", type=int, default=200)
    parser.add_argument("--orders", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    generate(args.output, args.customers, args.products, args.orders, args.seed)
