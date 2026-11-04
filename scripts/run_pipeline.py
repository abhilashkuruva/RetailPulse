"""CLI runner for RetailPulse ingestion pipeline."""
import argparse
import json
import sys

from retailpulse.config.settings import get_settings
from retailpulse.ingestion.pipeline import run_full_ingestion_pipeline


def main() -> None:
    parser = argparse.ArgumentParser(description="Execute RetailPulse ingestion pipeline.")
    parser.add_argument("--full-refresh", action="store_true", help="Ignore watermarks and extract all source records.")
    parser.add_argument("--execution-id", type=str, default=None, help="Explicit batch execution ID.")
    args = parser.parse_args()

    settings = get_settings()
    print("=" * 60)
    print("      RETAILPULSE INGESTION PIPELINE EXECUTION")
    print("=" * 60)
    print(f"Target Database : {settings.mysql_database} @ {settings.mysql_host}:{settings.mysql_port}")
    print(f"Target GCS      : gs://{settings.gcs_bucket_name or 'simulated-bucket'}")
    print(f"Target BigQuery : {settings.bigquery_raw_dataset}")
    print(f"Full Refresh    : {args.full_refresh}")
    print("-" * 60)

    summary = run_full_ingestion_pipeline(
        settings=settings,
        execution_id=args.execution_id,
        force_full_refresh=args.full_refresh,
    )

    print(json.dumps(summary, indent=2))
    print("=" * 60)

    failures = [t for t, res in summary.get("tables", {}).items() if res.get("status") != "SUCCESS"]
    if failures:
        print(f"Pipeline finished with failures in: {', '.join(failures)}")
        sys.exit(1)
    else:
        print("Pipeline execution completed successfully!")


if __name__ == "__main__":
    main()
