"""End-to-End ingestion pipeline orchestrating MySQL, GCS, and BigQuery loading."""
import uuid
from datetime import UTC, datetime
from pathlib import Path

from retailpulse.config.settings import Settings, get_settings
from retailpulse.ingestion.bigquery_loader import BigQueryLoader
from retailpulse.ingestion.file_exporter import export_rows
from retailpulse.ingestion.gcs_uploader import GCSUploader
from retailpulse.ingestion.mysql_extractor import MySQLExtractor
from retailpulse.monitoring.execution_tracker import ExecutionTracker
from retailpulse.utils.logger import get_logger

LOGGER = get_logger("retailpulse.pipeline")

TABLE_COLUMNS = {
    "customers": [
        "customer_id", "first_name", "last_name", "email", "phone", "city", "state",
        "country", "registration_date", "created_at", "updated_at"
    ],
    "products": [
        "product_id", "product_name", "category", "brand", "unit_price", "cost_price",
        "stock_quantity", "created_at", "updated_at"
    ],
    "orders": [
        "order_id", "customer_id", "order_date", "order_status", "payment_method",
        "shipping_city", "shipping_state", "created_at", "updated_at"
    ],
    "order_items": [
        "order_item_id", "order_id", "product_id", "quantity", "unit_price",
        "discount_amount", "created_at", "updated_at"
    ],
    "payments": [
        "payment_id", "order_id", "payment_method", "payment_amount", "payment_status",
        "transaction_date", "created_at", "updated_at"
    ],
}


def extract_to_csv(settings: Settings, watermark: datetime | None = None) -> list[Path]:
    """Extract MySQL source tables to CSV files in export_dir."""
    extractor = MySQLExtractor(settings)
    batch_time = datetime.now(UTC)
    paths = []
    for table, columns in TABLE_COLUMNS.items():
        rows = extractor.extract(table, columns, watermark)
        path = export_rows(table, rows, settings.export_dir, batch_time, columns=columns)
        LOGGER.info("Extracted %s rows from MySQL table '%s' -> %s", len(rows), table, path)
        paths.append(path)
    return paths


def run_full_ingestion_pipeline(
    settings: Settings | None = None,
    execution_id: str | None = None,
    force_full_refresh: bool = False,
) -> dict[str, object]:
    """Run full ingestion pipeline: MySQL -> CSV -> GCS -> BigQuery Raw -> Metadata Tracker."""
    cfg = settings or get_settings()
    ts_label = datetime.now(UTC).strftime('%Y%m%d_%H%M%S')
    exec_id = execution_id or f"batch_{uuid.uuid4().hex[:8]}_{ts_label}"

    tracker = ExecutionTracker(cfg)
    extractor = MySQLExtractor(cfg)
    uploader = GCSUploader(cfg)
    bq_loader = BigQueryLoader(cfg)

    batch_time = datetime.now(UTC)
    summary: dict[str, object] = {
        "execution_id": exec_id,
        "started_at": batch_time.isoformat(),
        "tables": {},
    }

    LOGGER.info("Starting ingestion batch exec_id=%s (force_full_refresh=%s)",
                exec_id, force_full_refresh)

    for table, columns in TABLE_COLUMNS.items():
        tracker.start_execution(table, exec_id)
        watermark = None
        if not force_full_refresh:
            watermark = tracker.get_last_successful_watermark(table)

        try:
            rows = extractor.extract(table, columns, watermark)
            record_count = len(rows)

            csv_path = export_rows(table, rows, cfg.export_dir, batch_time, columns=columns)

            max_record_time = batch_time
            if rows:
                dates = [
                    r["updated_at"]
                    for r in rows
                    if r.get("updated_at") and isinstance(r["updated_at"], datetime)
                ]
                if dates:
                    max_record_time = max(dates)

            gcs_uri = uploader.upload(csv_path, table, batch_time)
            loaded_count = bq_loader.load_csv(csv_path, table, gcs_uri, exec_id)

            tracker.record_success(
                execution_id=exec_id,
                source_table=table,
                records_extracted=record_count,
                records_loaded=loaded_count,
                extraction_watermark=max_record_time,
            )

            summary["tables"][table] = {
                "status": "SUCCESS",
                "extracted": record_count,
                "loaded": loaded_count,
                "gcs_uri": gcs_uri,
            }

        except Exception as e:
            error_msg = f"Failed ingestion for {table}: {e}"
            LOGGER.error(error_msg, exc_info=True)
            tracker.record_failure(exec_id, table, str(e))
            summary["tables"][table] = {
                "status": "FAILED",
                "error": str(e),
            }

    summary["completed_at"] = datetime.now(UTC).isoformat()
    LOGGER.info("Completed RetailPulse ingestion pipeline execution_id=%s", exec_id)
    return summary
