"""Export populated MySQL tables into an embedded SQLite database for zero-cost cloud hosting."""
import sqlite3
from pathlib import Path
import mysql.connector
from retailpulse.config.settings import get_settings


def export_mysql_to_sqlite(target_path: Path) -> None:
    settings = get_settings()
    target_path.parent.mkdir(parents=True, exist_ok=True)
    if target_path.exists():
        target_path.unlink()

    mysql_conn = mysql.connector.connect(
        host=settings.mysql_host,
        port=settings.mysql_port,
        user=settings.mysql_user,
        password=settings.mysql_password,
        database=settings.mysql_database,
    )
    sqlite_conn = sqlite3.connect(target_path)

    tables = ["customers", "products", "orders", "order_items", "payments", "pipeline_metadata"]

    with mysql_conn.cursor(dictionary=True) as m_cur, sqlite_conn:
        s_cur = sqlite_conn.cursor()
        for table in tables:
            m_cur.execute(f"SELECT * FROM {table}")
            rows = m_cur.fetchall()
            if not rows:
                continue

            cols = list(rows[0].keys())
            col_defs = ", ".join([f'"{col}" TEXT' for col in cols])
            s_cur.execute(f'CREATE TABLE IF NOT EXISTS "{table}" ({col_defs})')

            placeholders = ", ".join(["?"] * len(cols))
            insert_sql = f'INSERT INTO "{table}" ({", ".join(cols)}) VALUES ({placeholders})'

            batch = [tuple(str(r[c]) if r[c] is not None else None for c in cols) for r in rows]
            s_cur.executemany(insert_sql, batch)
            print(f"Exported {len(batch)} rows from MySQL -> SQLite: '{table}'")

        # Create indexes in SQLite for fast query response
        s_cur.execute("CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders(customer_id)")
        s_cur.execute("CREATE INDEX IF NOT EXISTS idx_orders_date ON orders(order_date)")
        s_cur.execute("CREATE INDEX IF NOT EXISTS idx_items_order ON order_items(order_id)")
        s_cur.execute("CREATE INDEX IF NOT EXISTS idx_payments_order ON payments(order_id)")
        sqlite_conn.commit()

    mysql_conn.close()
    sqlite_conn.close()
    print(f"Successfully generated embedded SQLite database at: {target_path} ({target_path.stat().st_size} bytes)")


if __name__ == "__main__":
    export_mysql_to_sqlite(Path("data/retailpulse_live.db"))

