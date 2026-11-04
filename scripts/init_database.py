"""Initialize MySQL database, tables, sample data, and foreign key integrity checks."""
import sys
from pathlib import Path

import mysql.connector

# Ensure src is on Python path
sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from retailpulse.config.settings import get_settings
from retailpulse.utils.logger import get_logger

LOGGER = get_logger("retailpulse.init_db")


def init_database() -> bool:
    settings = get_settings()
    root_dir = Path(__file__).parents[1]
    schema_file = root_dir / "database" / "schema.sql"
    exports_dir = root_dir / "data" / "exports"

    LOGGER.info("Connecting to MySQL host=%s:%s user=%s...", settings.mysql_host, settings.mysql_port, settings.mysql_user)

    # 1. Connect without database to ensure database creation
    conn = mysql.connector.connect(
        host=settings.mysql_host,
        port=settings.mysql_port,
        user=settings.mysql_user,
        password=settings.mysql_password,
        connection_timeout=settings.mysql_connect_timeout,
    )
    cursor = conn.cursor()

    try:
        LOGGER.info("Ensuring database '%s' exists...", settings.mysql_database)
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{settings.mysql_database}`;")
        cursor.execute(f"USE `{settings.mysql_database}`;")

        # 2. Execute schema statements
        LOGGER.info("Applying schema DDL from %s...", schema_file)
        schema_sql = schema_file.read_text(encoding="utf-8")
        for statement in schema_sql.split(";"):
            cleaned = statement.strip()
            if cleaned:
                cursor.execute(cleaned)
        conn.commit()
        LOGGER.info("Schema tables successfully created/verified.")

        # 3. Check existing data. If empty, generate and load sample data
        cursor.execute("SELECT COUNT(*) FROM customers")
        customer_count = cursor.fetchone()[0]

        if customer_count == 0:
            LOGGER.info("No customers found. Generating realistic sample dataset...")
            from scripts.generate_data import generate
            generate(output=exports_dir, customers_count=1000, products_count=200, orders_count=5000)

            # Load into MySQL
            from scripts.load_data import load_table, TABLES
            LOGGER.info("Loading generated datasets into MySQL tables...")
            for table in TABLES:
                csv_path = exports_dir / f"{table}.csv"
                if csv_path.exists():
                    loaded = load_table(cursor, table, csv_path)
                    conn.commit()
                    LOGGER.info("Loaded %d rows into %s", loaded, table)
        else:
            LOGGER.info("Database already contains %d customers. Skipping duplicate insertion.", customer_count)

        # 4. Validate row counts
        tables = ["customers", "products", "orders", "order_items", "payments", "pipeline_metadata"]
        print("\n" + "=" * 55)
        print("          RETAILPULSE MYSQL VALIDATION REPORT")
        print("=" * 55)
        for tbl in tables:
            cursor.execute(f"SELECT COUNT(*) FROM `{tbl}`")
            cnt = cursor.fetchone()[0]
            print(f"Table: {tbl:<20} | Row Count: {cnt:>8}")

        # 5. Verify referential integrity (foreign keys)
        fk_checks = [
            ("Orders with invalid customers", "SELECT COUNT(*) FROM orders o LEFT JOIN customers c ON o.customer_id = c.customer_id WHERE c.customer_id IS NULL"),
            ("Order items with invalid orders", "SELECT COUNT(*) FROM order_items oi LEFT JOIN orders o ON oi.order_id = o.order_id WHERE o.order_id IS NULL"),
            ("Order items with invalid products", "SELECT COUNT(*) FROM order_items oi LEFT JOIN products p ON oi.product_id = p.product_id WHERE p.product_id IS NULL"),
            ("Payments with invalid orders", "SELECT COUNT(*) FROM payments p LEFT JOIN orders o ON p.order_id = o.order_id WHERE o.order_id IS NULL"),
        ]

        print("-" * 55)
        print("          FOREIGN KEY REFERENTIAL INTEGRITY")
        print("-" * 55)
        all_passed = True
        for desc, query in fk_checks:
            cursor.execute(query)
            orphan_count = cursor.fetchone()[0]
            status = "PASS (0 orphans)" if orphan_count == 0 else f"FAIL ({orphan_count} orphans)"
            print(f"{desc:<35}: {status}")
            if orphan_count > 0:
                all_passed = False

        print("=" * 55 + "\n")
        return all_passed

    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    success = init_database()
    if not success:
        sys.exit(1)
