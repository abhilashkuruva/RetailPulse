# RetailPulse: Live Deployment & Validation Report

## 1. Project Overview & Deployment Summary

- **Repository:** [github.com/abhilashkuruva/RetailPulse](https://github.com/abhilashkuruva/RetailPulse)
- **Git Commit:** `fa4f7b4` (Clean, audited, verified)
- **CI/CD Status:**
  - ✅ **Python Unit Tests & API Validation:** PASS (19/19 tests)
  - ✅ **Code Quality & Secret Scan:** PASS (0 lint issues, 0 leaked credentials)
  - ✅ **dbt Model Validation & Parse:** PASS (all medallion models verified)

---

## 2. Cloud Hosting Architecture & Tier Specifications

| Component | Cloud Platform | Instance Tier | Cost | Cold Start / Uptime |
| :--- | :--- | :--- | :--- | :--- |
| **BI Dashboard** | Streamlit Community Cloud | Standard (2.7 GB RAM) | $0.00 / month | Sleeps after 12h inactivity, instant wake |
| **REST API** | Render.com | Free Web Service (512 MB RAM) | $0.00 / month | Spins down after 15m inactivity (~30s spin-up) |
| **Demo Database** | Embedded SQLite Snapshot | Bundled in Git (`data/retailpulse_live.db`) | $0.00 / month | 0ms network latency, zero maintenance |

---

## 3. Automated Test Suite Validation

### Local & CI Test Results (19 Tests Passed in 3.12s)

| Test Module | Test Case | Target Tested | Result |
| :--- | :--- | :--- | :--- |
| `tests/unit/test_api.py` | `test_api_root` | Root `/` endpoint discovery | **PASS** |
| `tests/unit/test_api.py` | `test_api_health` | Database connection & health probe | **PASS** |
| `tests/unit/test_api.py` | `test_api_metrics_summary` | Revenue, orders, AOV, watermark KPIs | **PASS** |
| `tests/unit/test_api.py` | `test_api_sales_daily` | 30-day timeline series aggregation | **PASS** |
| `tests/unit/test_api.py` | `test_api_sales_category` | Category distribution & item counts | **PASS** |
| `tests/unit/test_api.py` | `test_api_orders_pagination` | Order pagination & status filtering | **PASS** |
| `tests/unit/test_api.py` | `test_api_quality_violations` | Data quality corruption reporting | **PASS** |
| `tests/unit/test_file_exporter.py` | `test_filename_is_deterministic` | Deterministic staging filenames | **PASS** |
| `tests/unit/test_file_exporter.py` | `test_export_writes_headers_and_escaped_values` | CSV quoting & RFC 4180 format | **PASS** |
| `tests/unit/test_gcs_uploader.py` | `test_gcs_object_name_partitioning_path` | Hive-style GCS partitioning paths | **PASS** |
| `tests/unit/test_gcs_uploader.py` | `test_gcs_simulated_upload` | GCS client upload simulation | **PASS** |
| `tests/unit/test_quality.py` | `test_invalid_order_is_reported` | Data validation schema assertion | **PASS** |
| `tests/unit/test_quality.py` | `test_duplicate_ids` | Primary key uniqueness rule | **PASS** |
| `tests/unit/test_quality.py` | `test_corrupted_orders_fixture` | Corrupted CSV ingestion rejection | **PASS** |
| `tests/unit/test_settings.py` | `test_gcp_configuration_is_explicit` | GCP environment validation | **PASS** |
| `tests/unit/test_watermark.py` | `test_extractor_query_with_watermark_overlap` | 5-min CDC overlap window | **PASS** |
| `tests/unit/test_watermark.py` | `test_extractor_disallows_arbitrary_tables` | SQL injection defense | **PASS** |
| `tests/integration/test_mysql_database.py` | `test_mysql_connection_and_table_presence` | MySQL schema & record presence | **PASS** |
| `tests/integration/test_pipeline_e2e.py` | `test_pipeline_e2e_execution` | End-to-end extraction pipeline | **PASS** |

---

## 4. REST API Endpoint Specification & Verification

| HTTP Method | Endpoint | Description | Sample Output / Status |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | API Information & Directory | `{"service": "RetailPulse API", "version": "1.0.0"}` |
| `GET` | `/health` | Live Health & DB Connectivity | `{"status": "healthy", "database": "connected", "latency_ms": 1.2}` |
| `GET` | `/api/metrics/summary` | Executive KPIs | `{"gross_revenue": 1054320.50, "total_orders": 5000}` |
| `GET` | `/api/sales/daily?days=30`| 30-Day Sales Trend | `[{"order_day": "2024-03-01", "orders": 42, "revenue": 8920.4}]` |
| `GET` | `/api/sales/category` | Category Breakdown | `[{"category": "Electronics", "revenue": 340120.0}]` |
| `GET` | `/api/orders?limit=20` | Paginated Orders | `[{"order_id": 1, "order_status": "delivered", ...}]` |
| `GET` | `/api/pipeline/audit` | Pipeline Metadata Ledger | Last 50 runs with status and watermark timestamps |
| `GET` | `/docs` | Interactive Swagger UI | OpenAPI interactive testing console |

---

## 5. Security & Secret Leak Prevention Audit

- **Tracked files scanned:** All `.py`, `.yml`, `.yaml`, `.json`, `.sql`, `.toml` files.
- **Rules evaluated:**
  - No `.env` committed
  - No GCP service account JSON private keys committed
  - No database passwords hardcoded in source
  - No API tokens or PATs committed
- **Result:** **100% CLEAN** — verified by automated CI secret scan in GitHub Actions.
