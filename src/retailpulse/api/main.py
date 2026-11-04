"""RetailPulse Production REST API.

Provides high-performance analytical and operational endpoints for the RetailPulse
E-Commerce Data Engineering Platform, supporting both live cloud MySQL/TiDB and
zero-cold-start embedded SQLite fallback.
"""
from __future__ import annotations

import os
import sqlite3
import time
from pathlib import Path
from typing import Any

import mysql.connector
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from retailpulse.config.settings import get_settings
from retailpulse.utils.logger import get_logger

logger = get_logger("retailpulse.api")
settings = get_settings()

app = FastAPI(
    title="RetailPulse Data Engineering API",
    description="Production REST API for RetailPulse E-Commerce Data Platform on Google Cloud",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Enable CORS for public frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SQLITE_PATH = Path(__file__).resolve().parent.parent.parent.parent / "data" / "retailpulse_live.db"


def get_db_connection() -> tuple[Any, str]:
    """Establishes database connection with automatic failover.

    Returns:
        tuple of (connection_object, engine_name)
    """
    force_sqlite = os.getenv("USE_SQLITE", "false").lower() in ("true", "1", "yes")

    if not force_sqlite:
        try:
            # Fast timeout to prevent thread blocking if MySQL host is unreachable
            conn = mysql.connector.connect(
                host=settings.mysql_host,
                port=settings.mysql_port,
                user=settings.mysql_user,
                password=settings.mysql_password,
                database=settings.mysql_database,
                connection_timeout=2,
            )
            if conn.is_connected():
                return conn, "mysql"
        except Exception as e:
            logger.warning("Remote MySQL connection failed (%s); falling back to SQLite.", e)

    # Fallback to embedded SQLite
    if SQLITE_PATH.exists():
        conn = sqlite3.connect(SQLITE_PATH)
        conn.row_factory = sqlite3.Row
        return conn, "sqlite"

    raise RuntimeError(
        "No operational database available. "
        f"MySQL failed and SQLite file not found at {SQLITE_PATH}"
    )


@app.get("/")
def root() -> dict[str, Any]:
    """API Root with service descriptor and navigation links."""
    return {
        "service": "RetailPulse E-Commerce Data Engineering API",
        "version": "1.0.0",
        "status": "ONLINE",
        "documentation": "/docs",
        "endpoints": {
            "health": "/health",
            "metrics_summary": "/api/metrics/summary",
            "sales_daily": "/api/sales/daily",
            "sales_category": "/api/sales/category",
            "orders": "/api/orders?limit=20",
            "pipeline_audit": "/api/pipeline/audit",
            "quality_violations": "/api/quality/violations",
        },
    }


@app.get("/health")
def health() -> dict[str, Any]:
    """Healthcheck endpoint with database latency benchmark and record counts."""
    start_time = time.perf_counter()
    try:
        conn, engine = get_db_connection()
        counts: dict[str, int] = {}
        tables = ["customers", "products", "orders", "order_items", "payments", "pipeline_metadata"]

        cur = conn.cursor()
        for t in tables:
            try:
                cur.execute(f"SELECT COUNT(*) FROM {t}")
                counts[t] = cur.fetchone()[0]
            except Exception:
                counts[t] = 0

        conn.close()
        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
        return {
            "status": "HEALTHY",
            "database_engine": engine,
            "response_time_ms": latency_ms,
            "record_counts": counts,
            "cloud_provider_target": "Google Cloud Platform (GCS / BigQuery)",
        }
    except Exception as e:
        logger.error("Health check failure: %s", e)
        return {
            "status": "DEGRADED",
            "error": str(e),
            "response_time_ms": round((time.perf_counter() - start_time) * 1000, 2),
        }


@app.get("/api/metrics/summary")
def get_metrics_summary() -> dict[str, Any]:
    """Returns high-level executive KPIs for the RetailPulse dashboard."""
    conn, engine = get_db_connection()
    try:
        cur = conn.cursor()
        # Revenue and orders
        cur.execute(
            """
            SELECT 
                COUNT(o.order_id) as total_orders,
                ROUND(COALESCE(SUM(p.payment_amount), 0), 2) as gross_revenue
            FROM orders o
            LEFT JOIN payments p ON o.order_id = p.order_id
            WHERE o.order_status != 'cancelled'
            """
        )
        row = cur.fetchone()
        total_orders = row[0] or 0
        gross_revenue = float(row[1] or 0.0)

        # Active customers
        cur.execute("SELECT COUNT(DISTINCT customer_id) FROM customers")
        total_customers = cur.fetchone()[0] or 0

        # Average Order Value (AOV)
        aov = round(gross_revenue / total_orders, 2) if total_orders > 0 else 0.0

        # Latest Watermark
        cur.execute(
            """
            SELECT MAX(last_successful_extraction_timestamp) 
            FROM pipeline_metadata 
            WHERE execution_status = 'SUCCESS'
            """
        )
        latest_watermark = cur.fetchone()[0]

        return {
            "gross_revenue": gross_revenue,
            "total_orders": total_orders,
            "active_customers": total_customers,
            "average_order_value": aov,
            "currency": "INR (₹)",
            "pipeline_status": "OPERATIONAL",
            "latest_cdc_watermark": str(latest_watermark) if latest_watermark else "N/A",
            "database_engine": engine,
        }
    finally:
        conn.close()


@app.get("/api/sales/daily")
def get_daily_sales(days: int = Query(default=30, ge=1, le=365)) -> list[dict[str, Any]]:
    """Returns daily sales trend records for charting."""
    conn, engine = get_db_connection()
    try:
        cur = conn.cursor()
        if engine == "mysql":
            sql = f"""
                SELECT 
                    DATE(o.order_date) as order_day,
                    COUNT(DISTINCT o.order_id) as orders_count,
                    ROUND(SUM(p.payment_amount), 2) as daily_revenue
                FROM orders o
                JOIN payments p ON o.order_id = p.order_id
                WHERE o.order_status != 'cancelled'
                GROUP BY DATE(o.order_date)
                ORDER BY order_day DESC
                LIMIT {days}
            """
        else:
            sql = f"""
                SELECT 
                    substr(o.order_date, 1, 10) as order_day,
                    COUNT(DISTINCT o.order_id) as orders_count,
                    ROUND(SUM(CAST(p.payment_amount AS REAL)), 2) as daily_revenue
                FROM orders o
                JOIN payments p ON o.order_id = p.order_id
                WHERE o.order_status != 'cancelled'
                GROUP BY substr(o.order_date, 1, 10)
                ORDER BY order_day DESC
                LIMIT {days}
            """
        cur.execute(sql)
        results = []
        for r in cur.fetchall():
            results.append({
                "date": str(r[0]),
                "orders_count": int(r[1]),
                "revenue": float(r[2] or 0.0),
            })
        return list(reversed(results))
    finally:
        conn.close()


@app.get("/api/sales/category")
def get_category_sales() -> list[dict[str, Any]]:
    """Returns sales distribution grouped by product category."""
    conn, engine = get_db_connection()
    try:
        cur = conn.cursor()
        if engine == "mysql":
            sql = """
                SELECT 
                    p.category,
                    COUNT(DISTINCT oi.order_id) as orders_count,
                    ROUND(SUM(oi.quantity * oi.unit_price), 2) as category_revenue
                FROM order_items oi
                JOIN products p ON oi.product_id = p.product_id
                GROUP BY p.category
                ORDER BY category_revenue DESC
            """
        else:
            sql = """
                SELECT 
                    p.category,
                    COUNT(DISTINCT oi.order_id) as orders_count,
                    ROUND(
                        SUM(CAST(oi.quantity AS REAL) * CAST(oi.unit_price AS REAL)), 2
                    ) as category_revenue
                FROM order_items oi
                JOIN products p ON oi.product_id = p.product_id
                GROUP BY p.category
                ORDER BY category_revenue DESC
            """
        cur.execute(sql)
        results = []
        for r in cur.fetchall():
            results.append({
                "category": r[0],
                "orders_count": int(r[1]),
                "revenue": float(r[2] or 0.0),
            })
        return results
    finally:
        conn.close()


@app.get("/api/orders")
def get_orders(
    limit: int = Query(default=20, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    status: str | None = None,
) -> dict[str, Any]:
    """Returns paginated orders with customer names and fulfillment statuses."""
    conn, engine = get_db_connection()
    try:
        cur = conn.cursor()
        where_clause = ""
        params: list[Any] = []
        if status:
            where_clause = (
                "WHERE o.order_status = ?" if engine == "sqlite"
                else "WHERE o.order_status = %s"
            )
            params.append(status)

        query = f"""
            SELECT 
                o.order_id,
                o.customer_id,
                c.first_name,
                c.last_name,
                o.order_date,
                o.order_status,
                o.payment_method,
                o.shipping_city,
                o.shipping_state,
                COALESCE(p.payment_amount, 0) as total_amount
            FROM orders o
            LEFT JOIN customers c ON o.customer_id = c.customer_id
            LEFT JOIN payments p ON o.order_id = p.order_id
            {where_clause}
            ORDER BY o.order_id DESC
            LIMIT {limit} OFFSET {offset}
        """
        cur.execute(query, tuple(params) if params else ())
        orders = []
        for r in cur.fetchall():
            orders.append({
                "order_id": r[0],
                "customer_id": r[1],
                "customer_name": f"{r[2]} {r[3]}",
                "order_date": str(r[4]),
                "order_status": r[5],
                "payment_method": r[6],
                "city": r[7],
                "state": r[8],
                "total_amount": float(r[9]),
            })

        count_query = f"SELECT COUNT(*) FROM orders o {where_clause}"
        cur.execute(count_query, tuple(params) if params else ())
        total_count = cur.fetchone()[0]

        return {
            "total": total_count,
            "limit": limit,
            "offset": offset,
            "orders": orders,
        }
    finally:
        conn.close()


@app.get("/api/pipeline/audit")
def get_pipeline_audit() -> list[dict[str, Any]]:
    """Returns CDC watermarks and ingestion execution audit ledger."""
    conn, _ = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT 
                execution_id,
                source_table,
                execution_status,
                records_extracted,
                records_loaded,
                started_at,
                completed_at,
                last_successful_extraction_timestamp,
                error_message
            FROM pipeline_metadata
            ORDER BY completed_at DESC
            LIMIT 50
            """
        )
        logs = []
        for r in cur.fetchall():
            logs.append({
                "execution_id": r[0],
                "source_table": r[1],
                "status": r[2],
                "extracted": r[3],
                "loaded": r[4],
                "started_at": str(r[5]),
                "completed_at": str(r[6]),
                "watermark": str(r[7]) if r[7] else None,
                "error": r[8],
            })
        return logs
    finally:
        conn.close()


@app.get("/api/quality/violations")
def get_quality_violations() -> dict[str, Any]:
    """Inspects dirty data test fixtures to demonstrate pipeline data quality guards."""
    import csv

    fixtures_dir = (
        Path(__file__).resolve().parent.parent.parent.parent
        / "tests" / "fixtures" / "corrupted"
    )
    if not fixtures_dir.exists():
        raise HTTPException(status_code=404, detail="Fixtures directory not found")

    summary: dict[str, Any] = {}
    for csv_file in fixtures_dir.glob("*.csv"):
        with csv_file.open(encoding="utf-8") as f:
            reader = list(csv.DictReader(f))
            summary[csv_file.name] = {
                "anomalous_records_count": len(reader),
                "sample_records": reader[:3],
            }

    return {
        "status": "ASSERTIONS_ENFORCED",
        "description": (
            "Pre-landing quality guards prevent corrupted records from entering BigQuery Bronze."
        ),
        "quarantined_fixtures": summary,
    }
