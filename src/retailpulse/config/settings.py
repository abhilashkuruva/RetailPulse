from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Validated environment configuration for local and cloud execution."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    mysql_host: str = "localhost"
    mysql_port: int = 3306
    mysql_user: str = "root"
    mysql_password: str = "password"
    mysql_database: str = "retailpulse_db"
    mysql_connect_timeout: int = 10
    gcp_project_id: str = ""
    gcp_region: str = "asia-south1"
    gcs_bucket_name: str = ""
    bigquery_raw_dataset: str = "retailpulse_raw"
    bigquery_staging_dataset: str = "retailpulse_staging"
    bigquery_analytics_dataset: str = "retailpulse_analytics"
    google_application_credentials: str = ""
    watermark_overlap_minutes: int = Field(default=5, ge=0, le=1440)
    export_dir: Path = Path("data/exports")

    @property
    def has_gcp_configuration(self) -> bool:
        return bool(self.gcp_project_id and self.gcs_bucket_name)


@lru_cache
def get_settings() -> Settings:
    return Settings()
