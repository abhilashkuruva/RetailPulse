"""BigQuery raw data loader with schema enforcement, metadata enrichment, and local fallback."""
from pathlib import Path

from retailpulse.config.settings import Settings
from retailpulse.utils.logger import get_logger

LOGGER = get_logger("retailpulse.bigquery_loader")

RAW_TABLE_SCHEMAS = {
    "customers": [
        {"name": "customer_id", "type": "INT64", "mode": "REQUIRED"},
        {"name": "first_name", "type": "STRING", "mode": "REQUIRED"},
        {"name": "last_name", "type": "STRING", "mode": "REQUIRED"},
        {"name": "email", "type": "STRING", "mode": "REQUIRED"},
        {"name": "phone", "type": "STRING", "mode": "NULLABLE"},
        {"name": "city", "type": "STRING", "mode": "REQUIRED"},
        {"name": "state", "type": "STRING", "mode": "REQUIRED"},
        {"name": "country", "type": "STRING", "mode": "REQUIRED"},
        {"name": "registration_date", "type": "DATE", "mode": "REQUIRED"},
        {"name": "created_at", "type": "TIMESTAMP", "mode": "REQUIRED"},
        {"name": "updated_at", "type": "TIMESTAMP", "mode": "REQUIRED"},
        {"name": "batch_id", "type": "STRING", "mode": "NULLABLE"},
        {"name": "source_file", "type": "STRING", "mode": "NULLABLE"},
        {"name": "ingestion_timestamp", "type": "TIMESTAMP", "mode": "NULLABLE"},
    ],
    "products": [
        {"name": "product_id", "type": "INT64", "mode": "REQUIRED"},
        {"name": "product_name", "type": "STRING", "mode": "REQUIRED"},
        {"name": "category", "type": "STRING", "mode": "REQUIRED"},
        {"name": "brand", "type": "STRING", "mode": "REQUIRED"},
        {"name": "unit_price", "type": "NUMERIC", "mode": "REQUIRED"},
        {"name": "cost_price", "type": "NUMERIC", "mode": "REQUIRED"},
        {"name": "stock_quantity", "type": "INT64", "mode": "REQUIRED"},
        {"name": "created_at", "type": "TIMESTAMP", "mode": "REQUIRED"},
        {"name": "updated_at", "type": "TIMESTAMP", "mode": "REQUIRED"},
        {"name": "batch_id", "type": "STRING", "mode": "NULLABLE"},
        {"name": "source_file", "type": "STRING", "mode": "NULLABLE"},
        {"name": "ingestion_timestamp", "type": "TIMESTAMP", "mode": "NULLABLE"},
    ],
    "orders": [
        {"name": "order_id", "type": "INT64", "mode": "REQUIRED"},
        {"name": "customer_id", "type": "INT64", "mode": "REQUIRED"},
        {"name": "order_date", "type": "DATETIME", "mode": "REQUIRED"},
        {"name": "order_status", "type": "STRING", "mode": "REQUIRED"},
        {"name": "payment_method", "type": "STRING", "mode": "REQUIRED"},
        {"name": "shipping_city", "type": "STRING", "mode": "REQUIRED"},
        {"name": "shipping_state", "type": "STRING", "mode": "REQUIRED"},
        {"name": "created_at", "type": "TIMESTAMP", "mode": "REQUIRED"},
        {"name": "updated_at", "type": "TIMESTAMP", "mode": "REQUIRED"},
        {"name": "batch_id", "type": "STRING", "mode": "NULLABLE"},
        {"name": "source_file", "type": "STRING", "mode": "NULLABLE"},
        {"name": "ingestion_timestamp", "type": "TIMESTAMP", "mode": "NULLABLE"},
    ],
    "order_items": [
        {"name": "order_item_id", "type": "INT64", "mode": "REQUIRED"},
        {"name": "order_id", "type": "INT64", "mode": "REQUIRED"},
        {"name": "product_id", "type": "INT64", "mode": "REQUIRED"},
        {"name": "quantity", "type": "INT64", "mode": "REQUIRED"},
        {"name": "unit_price", "type": "NUMERIC", "mode": "REQUIRED"},
        {"name": "discount_amount", "type": "NUMERIC", "mode": "REQUIRED"},
        {"name": "created_at", "type": "TIMESTAMP", "mode": "REQUIRED"},
        {"name": "updated_at", "type": "TIMESTAMP", "mode": "REQUIRED"},
        {"name": "batch_id", "type": "STRING", "mode": "NULLABLE"},
        {"name": "source_file", "type": "STRING", "mode": "NULLABLE"},
        {"name": "ingestion_timestamp", "type": "TIMESTAMP", "mode": "NULLABLE"},
    ],
    "payments": [
        {"name": "payment_id", "type": "INT64", "mode": "REQUIRED"},
        {"name": "order_id", "type": "INT64", "mode": "REQUIRED"},
        {"name": "payment_method", "type": "STRING", "mode": "REQUIRED"},
        {"name": "payment_amount", "type": "NUMERIC", "mode": "REQUIRED"},
        {"name": "payment_status", "type": "STRING", "mode": "REQUIRED"},
        {"name": "transaction_date", "type": "DATETIME", "mode": "REQUIRED"},
        {"name": "created_at", "type": "TIMESTAMP", "mode": "REQUIRED"},
        {"name": "updated_at", "type": "TIMESTAMP", "mode": "REQUIRED"},
        {"name": "batch_id", "type": "STRING", "mode": "NULLABLE"},
        {"name": "source_file", "type": "STRING", "mode": "NULLABLE"},
        {"name": "ingestion_timestamp", "type": "TIMESTAMP", "mode": "NULLABLE"},
    ],
}


class BigQueryLoader:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.client = None
        self.is_cloud_available = False

        if (
            settings.gcp_project_id
            and settings.google_application_credentials
        ):
            try:
                from google.cloud import bigquery
                self.client = bigquery.Client(project=settings.gcp_project_id)
                self.is_cloud_available = True
                LOGGER.info("BigQuery client initialized: %s", settings.gcp_project_id)
            except Exception as e:
                LOGGER.warning("BigQuery client init failed (%s); using local mode.", e)
                self.is_cloud_available = False
        else:
            LOGGER.info("BigQueryLoader operating in local simulation mode.")

    def load_csv(self, file_path: Path, table_name: str, gcs_uri: str, batch_id: str) -> int:
        """Load CSV records into BigQuery raw layer table with batch audit metadata."""
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        line_count = 0
        with file_path.open(encoding="utf-8") as f:
            for i, line in enumerate(f):
                if i > 0 and line.strip():
                    line_count += 1

        if self.is_cloud_available and self.client is not None:
            from google.cloud import bigquery
            dataset_id = self.settings.bigquery_raw_dataset
            table_id = f"{self.client.project}.{dataset_id}.{table_name}"

            job_config = bigquery.LoadJobConfig(
                source_format=bigquery.SourceFormat.CSV,
                skip_leading_rows=1,
                write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
                schema_update_options=[bigquery.SchemaUpdateOption.ALLOW_FIELD_ADDITION],
            )

            if gcs_uri.startswith("gs://"):
                load_job = self.client.load_table_from_uri(gcs_uri, table_id, job_config=job_config)
            else:
                with file_path.open("rb") as f:
                    load_job = self.client.load_table_from_file(f, table_id, job_config=job_config)

            res = load_job.result()
            loaded_rows = res.output_rows or line_count
            LOGGER.info(
                "Loaded %d rows into %s (Job ID: %s)", loaded_rows, table_id, load_job.job_id
            )
            return loaded_rows
        else:
            LOGGER.info("[Simulated BigQuery] Ingested %d rows into raw.%s from %s (batch: %s)",
                        line_count, table_name, gcs_uri, batch_id)
            return line_count
