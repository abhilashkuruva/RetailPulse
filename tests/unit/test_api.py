"""Unit tests for RetailPulse Production REST API."""
import os

os.environ["USE_SQLITE"] = "true"

import pytest
from fastapi.testclient import TestClient

from retailpulse.api.main import app

client = TestClient(app)


@pytest.mark.unit
def test_api_root():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "RetailPulse E-Commerce Data Engineering API"
    assert "endpoints" in data


@pytest.mark.unit
def test_api_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ("HEALTHY", "DEGRADED")
    assert "response_time_ms" in data
    assert "record_counts" in data


@pytest.mark.unit
def test_api_metrics_summary():
    response = client.get("/api/metrics/summary")
    assert response.status_code == 200
    data = response.json()
    assert "gross_revenue" in data
    assert "total_orders" in data
    assert "active_customers" in data
    assert data["currency"] == "INR (₹)"


@pytest.mark.unit
def test_api_sales_daily():
    response = client.get("/api/sales/daily?days=7")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.unit
def test_api_sales_category():
    response = client.get("/api/sales/category")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.unit
def test_api_orders_pagination():
    response = client.get("/api/orders?limit=10&offset=0")
    assert response.status_code == 200
    data = response.json()
    assert "orders" in data
    assert len(data["orders"]) <= 10
    assert "total" in data


@pytest.mark.unit
def test_api_quality_violations():
    response = client.get("/api/quality/violations")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ASSERTIONS_ENFORCED"
    assert "quarantined_fixtures" in data
