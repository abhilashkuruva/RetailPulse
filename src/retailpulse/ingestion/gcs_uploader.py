"""Google Cloud Storage uploader with partitioning paths and local staging fallback."""
import shutil
from datetime import UTC, datetime
from pathlib import Path

from retailpulse.config.settings import Settings
from retailpulse.utils.logger import get_logger

LOGGER = get_logger("retailpulse.gcs_uploader")


class GCSUploader:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.client = None
        self.bucket = None
        self.is_cloud_available = False

        if (
            settings.gcp_project_id
            and settings.gcs_bucket_name
            and settings.google_application_credentials
        ):
            try:
                from google.cloud import storage
                self.client = storage.Client(project=settings.gcp_project_id)
                self.bucket = self.client.bucket(settings.gcs_bucket_name)
                self.is_cloud_available = True
                LOGGER.info("GCS initialized for bucket: gs://%s", settings.gcs_bucket_name)
            except Exception as e:
                LOGGER.warning("GCS init failed (%s); using local simulation.", e)
                self.is_cloud_available = False
        else:
            LOGGER.info("GCS operating in local simulation mode.")

    def build_object_name(
        self, table_name: str, file_path: Path, now: datetime | None = None
    ) -> str:
        """Organize objects: raw/{table}/year=YYYY/month=MM/day=DD/{filename}."""
        ts = now or datetime.now(UTC)
        year = ts.strftime("%Y")
        month = ts.strftime("%m")
        day = ts.strftime("%d")
        return f"raw/{table_name}/year={year}/month={month}/day={day}/{file_path.name}"

    def upload(self, file_path: Path, table_name: str, now: datetime | None = None) -> str:
        """Upload file to GCS or local staging bucket directory, returning the URI."""
        if not file_path.exists():
            raise FileNotFoundError(f"Source file does not exist: {file_path}")

        object_name = self.build_object_name(table_name, file_path, now)
        file_size = file_path.stat().st_size

        if self.is_cloud_available and self.bucket is not None:
            blob = self.bucket.blob(object_name)
            blob.upload_from_filename(str(file_path), content_type="text/csv")
            if not blob.exists():
                raise RuntimeError(f"GCS upload verification failed: {object_name}")
            uri = f"gs://{self.bucket.name}/{object_name}"
            LOGGER.info("Uploaded %s (%d bytes) to GCS -> %s", file_path.name, file_size, uri)
            return uri
        else:
            local_gcs_root = Path("data/gcs_mock") / self.settings.gcs_bucket_name
            target_path = local_gcs_root / object_name
            target_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file_path, target_path)
            uri = f"gs://{self.settings.gcs_bucket_name or 'retailpulse-local'}/{object_name}"
            LOGGER.info(
                "[Simulated GCS] Staged %s (%d bytes) -> %s",
                file_path.name,
                file_size,
                uri,
            )
            return uri
