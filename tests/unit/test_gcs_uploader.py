from datetime import UTC, datetime
from pathlib import Path

from retailpulse.config.settings import Settings
from retailpulse.ingestion.gcs_uploader import GCSUploader


def test_gcs_object_name_partitioning_path():
    settings = Settings(gcs_bucket_name="retailpulse-test-bucket")
    uploader = GCSUploader(settings)

    fixed_time = datetime(2026, 11, 4, 15, 30, 0, tzinfo=UTC)
    dummy_file = Path("orders_20261104_153000.csv")

    obj_name = uploader.build_object_name("orders", dummy_file, fixed_time)
    assert obj_name == "raw/orders/year=2026/month=11/day=04/orders_20261104_153000.csv"


def test_gcs_simulated_upload(tmp_path):
    settings = Settings(gcs_bucket_name="retailpulse-test-bucket", export_dir=tmp_path)
    uploader = GCSUploader(settings)

    test_file = tmp_path / "products.csv"
    test_file.write_text("id,name\n1,Earbuds", encoding="utf-8")

    fixed_time = datetime(2026, 1, 15, 10, 0, 0, tzinfo=UTC)
    uri = uploader.upload(test_file, "products", fixed_time)

    assert uri == "gs://retailpulse-test-bucket/raw/products/year=2026/month=01/day=15/products.csv"
    expected_path = (
        Path("data/gcs_mock/retailpulse-test-bucket/raw/products")
        / "year=2026/month=01/day=15/products.csv"
    )
    assert expected_path.exists()
