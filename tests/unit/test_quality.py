from retailpulse.quality.validators import duplicate_ids, validate_order_row


def test_invalid_order_is_reported():
    errors = validate_order_row(
        {"order_id": 1, "quantity": 0, "unit_price": -1, "order_status": "unknown"}
    )
    assert len(errors) == 3


def test_duplicate_ids():
    assert duplicate_ids([{"id": 1}, {"id": 1}, {"id": 2}], "id") == {1}
