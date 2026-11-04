import mysql.connector
import pytest

from retailpulse.config.settings import get_settings


@pytest.mark.integration
def test_mysql_connection_and_table_presence():
    settings = get_settings()
    try:
        conn = mysql.connector.connect(
            host=settings.mysql_host,
            port=settings.mysql_port,
            user=settings.mysql_user,
            password=settings.mysql_password,
            database=settings.mysql_database,
            connection_timeout=settings.mysql_connect_timeout,
        )
    except Exception as e:
        pytest.skip(f"MySQL not reachable on localhost:3306 ({e}) - skipping integration test")
        return

    cursor = conn.cursor()
    cursor.execute("SHOW TABLES")
    tables = {row[0] for row in cursor.fetchall()}

    expected_tables = {
        "customers",
        "products",
        "orders",
        "order_items",
        "payments",
        "pipeline_metadata",
    }
    assert expected_tables.issubset(tables)

    cursor.execute("SELECT COUNT(*) FROM customers")
    assert cursor.fetchone()[0] >= 1000

    cursor.close()
    conn.close()
