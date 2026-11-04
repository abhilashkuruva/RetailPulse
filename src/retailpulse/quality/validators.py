"""Data quality validators and assertion rules for RetailPulse datasets."""

from collections.abc import Iterable, Mapping
from datetime import UTC, datetime
from decimal import Decimal

VALID_ORDER_STATUSES = {"pending", "confirmed", "shipped", "delivered", "cancelled", "returned"}
VALID_PAYMENT_STATUSES = {"success", "pending", "failed", "refunded"}
VALID_PAYMENT_METHODS = {"UPI", "CREDIT_CARD", "DEBIT_CARD", "COD", "NETBANKING", "CARD"}


def validate_order_row(row: Mapping[str, object]) -> list[str]:
    """Validate order business logic constraints."""
    errors: list[str] = []
    if not row.get("order_id"):
        errors.append("order_id is required")
    if row.get("quantity") is not None and int(row["quantity"]) <= 0:
        errors.append("quantity must be positive")
    if row.get("unit_price") is not None and Decimal(str(row["unit_price"])) < 0:
        errors.append("unit_price must be non-negative")
    if row.get("order_status") not in VALID_ORDER_STATUSES:
        errors.append("unsupported order_status")
    return errors


def validate_product_row(row: Mapping[str, object]) -> list[str]:
    """Validate product inventory and price constraints."""
    errors: list[str] = []
    if not row.get("product_id"):
        errors.append("product_id is required")
    if row.get("unit_price") is not None and Decimal(str(row["unit_price"])) < 0:
        errors.append("unit_price cannot be negative")
    if row.get("cost_price") is not None and Decimal(str(row["cost_price"])) < 0:
        errors.append("cost_price cannot be negative")
    if row.get("stock_quantity") is not None and int(row["stock_quantity"]) < 0:
        errors.append("stock_quantity cannot be negative")
    return errors


def validate_payment_row(row: Mapping[str, object]) -> list[str]:
    """Validate payment ledger transactions."""
    errors: list[str] = []
    if not row.get("payment_id"):
        errors.append("payment_id is required")
    if not row.get("order_id"):
        errors.append("order_id is required")
    if row.get("payment_amount") is not None and Decimal(str(row["payment_amount"])) < 0:
        errors.append("payment_amount cannot be negative")
    if row.get("payment_status") and row["payment_status"] not in VALID_PAYMENT_STATUSES:
        errors.append(f"unsupported payment_status: {row['payment_status']}")
    return errors


def duplicate_ids(rows: Iterable[Mapping[str, object]], key: str) -> set[object]:
    """Identify duplicate IDs within a record batch."""
    seen: set[object] = set()
    duplicates: set[object] = set()
    for row in rows:
        value = row.get(key)
        if value is not None:
            if value in seen:
                duplicates.add(value)
            seen.add(value)
    return duplicates


class QualityResult:
    """Structure for recording data quality test results in monitoring table."""

    def __init__(
        self,
        execution_id: str,
        model_name: str,
        test_name: str,
        test_status: str,
        failed_record_count: int,
        error_details: str = "",
    ):
        self.execution_id = execution_id
        self.model_name = model_name
        self.test_name = test_name
        self.test_status = test_status
        self.failed_record_count = failed_record_count
        self.execution_timestamp = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")
        self.error_details = error_details

    def to_dict(self) -> dict[str, object]:
        return {
            "execution_id": self.execution_id,
            "model_name": self.model_name,
            "test_name": self.test_name,
            "test_status": self.test_status,
            "failed_record_count": self.failed_record_count,
            "execution_timestamp": self.execution_timestamp,
            "error_details": self.error_details,
        }
