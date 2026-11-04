"""Pipeline execution and watermark tracking service."""
import uuid
from datetime import UTC, datetime

import mysql.connector

from retailpulse.config.settings import Settings
from retailpulse.utils.logger import get_logger

LOGGER = get_logger("retailpulse.monitoring")


class ExecutionTracker:
    def __init__(self, settings: Settings):
        self.settings = settings

    def _get_connection(self):
        return mysql.connector.connect(
            host=self.settings.mysql_host,
            port=self.settings.mysql_port,
            user=self.settings.mysql_user,
            password=self.settings.mysql_password,
            database=self.settings.mysql_database,
            connection_timeout=self.settings.mysql_connect_timeout,
        )

    def get_last_successful_watermark(self, table_name: str) -> datetime | None:
        """Fetch the latest successful extraction timestamp for a table."""
        query = """
            SELECT MAX(last_successful_extraction_timestamp)
            FROM pipeline_metadata
            WHERE source_table = %s AND execution_status = 'SUCCESS'
        """
        try:
            with self._get_connection() as conn, conn.cursor() as cursor:
                cursor.execute(query, (table_name,))
                result = cursor.fetchone()
                if result and result[0]:
                    LOGGER.info("Watermark for %s: %s", table_name, result[0])
                    return result[0]
        except Exception as e:
            LOGGER.warning("Could not query watermark for %s: %s", table_name, e)
        return None

    def start_execution(self, source_table: str, execution_id: str | None = None) -> str:
        """Record the start of a pipeline extraction batch."""
        ts = datetime.now(UTC).strftime('%Y%m%d%H%M%S')
        exec_id = execution_id or f"run_{uuid.uuid4().hex[:12]}_{ts}"
        now = datetime.now(UTC)
        query = """
            INSERT INTO pipeline_metadata
                (execution_id, source_table, execution_status, started_at)
            VALUES (%s, %s, 'RUNNING', %s)
            ON DUPLICATE KEY UPDATE execution_status = 'RUNNING', started_at = VALUES(started_at)
        """
        try:
            with self._get_connection() as conn, conn.cursor() as cursor:
                cursor.execute(query, (exec_id, source_table, now))
                conn.commit()
        except Exception as e:
            LOGGER.error("Failed to record start execution for %s: %s", source_table, e)
        return exec_id

    def record_success(
        self,
        execution_id: str,
        source_table: str,
        records_extracted: int,
        records_loaded: int,
        extraction_watermark: datetime,
    ) -> None:
        """Record successful completion and advance watermark."""
        now = datetime.now(UTC)
        query = """
            UPDATE pipeline_metadata
            SET execution_status = 'SUCCESS',
                records_extracted = %s,
                records_loaded = %s,
                last_successful_extraction_timestamp = %s,
                completed_at = %s,
                error_message = NULL
            WHERE execution_id = %s AND source_table = %s
        """
        try:
            with self._get_connection() as conn, conn.cursor() as cursor:
                params = (
                    records_extracted,
                    records_loaded,
                    extraction_watermark,
                    now,
                    execution_id,
                    source_table,
                )
                cursor.execute(query, params)
                conn.commit()
                LOGGER.info("Execution %s for %s marked SUCCESS", execution_id, source_table)
        except Exception as e:
            LOGGER.error("Failed to record success for %s: %s", execution_id, e)

    def record_failure(self, execution_id: str, source_table: str, error_message: str) -> None:
        """Record batch execution failure with error diagnostic."""
        now = datetime.now(UTC)
        query = """
            UPDATE pipeline_metadata
            SET execution_status = 'FAILED',
                completed_at = %s,
                error_message = %s
            WHERE execution_id = %s AND source_table = %s
        """
        try:
            with self._get_connection() as conn, conn.cursor() as cursor:
                cursor.execute(query, (now, error_message[:1000], execution_id, source_table))
                conn.commit()
                LOGGER.error(
                    "Execution %s for %s FAILED: %s",
                    execution_id,
                    source_table,
                    error_message,
                )
        except Exception as e:
            LOGGER.error("Failed to record failure for %s: %s", execution_id, e)
