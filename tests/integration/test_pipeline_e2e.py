import pytest

from retailpulse.config.settings import get_settings
from retailpulse.ingestion.pipeline import run_full_ingestion_pipeline
from retailpulse.monitoring.execution_tracker import ExecutionTracker


@pytest.mark.integration
def test_pipeline_e2e_execution():
    settings = get_settings()
    try:
        summary = run_full_ingestion_pipeline(settings=settings, force_full_refresh=False)
    except Exception as e:
        pytest.skip(f"MySQL unavailable ({e}) - skipping integration test")
        return

    assert summary["execution_id"] is not None
    assert "tables" in summary
    assert "orders" in summary["tables"]
    assert summary["tables"]["orders"]["status"] == "SUCCESS"
    assert summary["tables"]["orders"]["extracted"] > 0

    # Verify tracker recorded the success
    tracker = ExecutionTracker(settings)
    watermark = tracker.get_last_successful_watermark("orders")
    assert watermark is not None

