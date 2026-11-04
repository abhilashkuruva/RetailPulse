from datetime import UTC, datetime

from retailpulse.ingestion.file_exporter import build_export_filename, export_rows


def test_filename_is_deterministic():
    now = datetime(2026, 11, 4, 6, 37, tzinfo=UTC)
    assert build_export_filename("orders", now) == "orders_20261104_063700.csv"


def test_export_writes_headers_and_escaped_values(tmp_path):
    path = export_rows(
        "orders", [{"id": 1, "name": 'A, "B"'}], tmp_path, datetime(2026, 1, 1, tzinfo=UTC)
    )
    assert path.read_text(encoding="utf-8").splitlines() == ["id,name", '1,"A, ""B"""']
