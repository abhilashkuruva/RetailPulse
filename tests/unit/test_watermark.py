from datetime import UTC, datetime, timedelta

from retailpulse.config.settings import Settings
from retailpulse.ingestion.mysql_extractor import MySQLExtractor


def test_extractor_query_with_watermark_overlap():
    settings = Settings(watermark_overlap_minutes=15)
    _ = MySQLExtractor(settings)

    watermark = datetime(2026, 11, 4, 12, 0, 0, tzinfo=UTC)
    columns = ["order_id", "updated_at"]

    column_sql = ", ".join(f"`{col}`" for col in columns)
    sql = f"SELECT {column_sql} FROM `orders` WHERE updated_at >= %s ORDER BY updated_at"
    expected_overlap = watermark - timedelta(minutes=15)

    assert "WHERE updated_at >= %s" in sql
    assert settings.watermark_overlap_minutes == 15
    assert expected_overlap == datetime(2026, 11, 4, 11, 45, 0, tzinfo=UTC)


def test_extractor_disallows_arbitrary_tables():
    settings = Settings()
    extractor = MySQLExtractor(settings)
    try:
        extractor.extract("unauthorized_sensitive_table", ["id"])
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Unsupported source table" in str(e)
