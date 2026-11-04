from datetime import datetime, timedelta
from typing import Any

import mysql.connector

from retailpulse.config.settings import Settings


class MySQLExtractor:
    """Read source records using a parameterized, watermark-aware query."""

    def __init__(self, settings: Settings):
        self.settings = settings

    def connection(self):
        return mysql.connector.connect(
            host=self.settings.mysql_host,
            port=self.settings.mysql_port,
            user=self.settings.mysql_user,
            password=self.settings.mysql_password,
            database=self.settings.mysql_database,
            connection_timeout=self.settings.mysql_connect_timeout,
        )

    def extract(
        self, table_name: str, columns: list[str], watermark: datetime | None = None
    ) -> list[dict[str, Any]]:
        allowed_tables = {"customers", "products", "orders", "order_items", "payments"}
        if table_name not in allowed_tables:
            raise ValueError(f"Unsupported source table: {table_name}")
        column_sql = ", ".join(f"`{column}`" for column in columns)
        query = f"SELECT {column_sql} FROM `{table_name}`"
        params: tuple[datetime, ...] = ()
        if watermark is not None:
            query += " WHERE updated_at >= %s"
            params = (watermark - timedelta(minutes=self.settings.watermark_overlap_minutes),)
        query += " ORDER BY updated_at"
        with self.connection() as connection, connection.cursor(dictionary=True) as cursor:
            cursor.execute(query, params)
            return list(cursor.fetchall())
