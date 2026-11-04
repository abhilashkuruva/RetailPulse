import csv
from pathlib import Path

import pytest

from retailpulse.quality.validators import duplicate_ids, validate_order_row


@pytest.mark.unit
def test_invalid_order_is_reported():
    errors = validate_order_row(
        {"order_id": 1, "quantity": 0, "unit_price": -1, "order_status": "unknown"}
    )
    assert len(errors) == 3


@pytest.mark.unit
def test_duplicate_ids():
    assert duplicate_ids([{"id": 1}, {"id": 1}, {"id": 2}], "id") == {1}


@pytest.mark.unit
def test_corrupted_orders_fixture():
    fixture_path = (
        Path(__file__).resolve().parent.parent / "fixtures" / "corrupted" / "bad_orders.csv"
    )
    assert fixture_path.exists(), f"Missing fixture file: {fixture_path}"
    with fixture_path.open(encoding="utf-8") as f:
        reader = list(csv.DictReader(f))
    assert len(reader) >= 1
    garbage_rows = [r for r in reader if r.get("order_status") == "UNKNOWN_GARBAGE_STATUS"]
    assert len(garbage_rows) >= 1
