"""Load generated CSV fixtures into MySQL with idempotent upserts."""
import csv
from pathlib import Path

import mysql.connector

from retailpulse.config.settings import get_settings

TABLES = ["customers", "products", "orders", "order_items", "payments"]


def load_table(cursor, table: str, csv_path: Path) -> int:
    with csv_path.open(encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        columns = reader.fieldnames
        if not columns:
            raise ValueError(f"{csv_path} has no header")
        rows = [tuple(row[column] or None for column in columns) for row in reader]
    if not rows:
        return 0
    placeholders = ", ".join(["%s"] * len(columns))
    column_sql = ", ".join(f"`{column}`" for column in columns)
    updates = ", ".join(
        f"`{column}` = VALUES(`{column}`)" for column in columns if column not in {"customer_id",
        "product_id", "order_id", "order_item_id", "payment_id"}
    )
    statement = (
        f"INSERT INTO `{table}` ({column_sql}) VALUES ({placeholders}) "
        f"ON DUPLICATE KEY UPDATE {updates}"
    )
    cursor.executemany(statement, rows)
    return len(rows)


def main() -> None:
    settings = get_settings()
    export_dir = Path(settings.export_dir)
    connection = mysql.connector.connect(
        host=settings.mysql_host,
        port=settings.mysql_port,
        user=settings.mysql_user,
        password=settings.mysql_password,
        database=settings.mysql_database,
    )
    try:
        cursor = connection.cursor()
        counts = {}
        for table in TABLES:
            counts[table] = load_table(cursor, table, export_dir / f"{table}.csv")
        connection.commit()
        print("Loaded rows:", counts)
    finally:
        connection.close()


if __name__ == "__main__":
    main()
