# RetailPulse: Live Deployment & Validation Report

## 1. Project Overview & Deployment Summary

- **Repository:** [github.com/abhilashkuruva/RetailPulse](https://github.com/abhilashkuruva/RetailPulse)
- **Live FastAPI REST API:** [https://retailpulse-1p48.onrender.com](https://retailpulse-1p48.onrender.com)
- **Interactive Swagger Docs:** [https://retailpulse-1p48.onrender.com/docs](https://retailpulse-1p48.onrender.com/docs)
- **CI/CD Status:**
  - ✅ **Python Unit Tests & API Validation:** PASS (19/19 tests)
  - ✅ **Code Quality & Secret Scan:** PASS (0 lint issues, 0 leaked credentials)
  - ✅ **dbt Model Validation & Parse:** PASS (all medallion models verified)

---

## 2. Cloud Hosting Architecture & Tier Specifications

| Component | Cloud Platform | Instance Tier | Cost | Status / Latency |
| :--- | :--- | :--- | :--- | :--- |
| **REST API** | Render.com | Free Web Service (512 MB RAM) | $0.00 / month | **LIVE** (300ms p95 latency) |
| **BI Dashboard** | Streamlit Community Cloud | Standard (2.7 GB RAM) | $0.00 / month | Ready for one-click deploy |
| **Demo Database** | Embedded SQLite Snapshot | Bundled in Git (`data/retailpulse_live.db`) | $0.00 / month | **LIVE** (0.96ms query latency) |

---

## 3. Live Production REST API Verification

Verified against `https://retailpulse-1p48.onrender.com`:

| Endpoint | HTTP Status | Response Time | Sample Live Response / Field |
| :--- | :--- | :--- | :--- |
| `GET /` | `200 OK` | 348 ms | `{"service": "RetailPulse Data Platform REST API", "version": "1.0.0"}` |
| `GET /health` | `200 OK` | 408 ms | `{"status": "HEALTHY", "database_engine": "sqlite", "response_time_ms": 0.96}` |
| `GET /api/metrics/summary` | `200 OK` | 290 ms | `{"gross_revenue": 596891301.5, "total_orders": 4023, "active_customers": 1001}` |
| `GET /api/sales/daily?days=7` | `200 OK` | 424 ms | 7-day chronological daily revenue & order count breakdown |
| `GET /api/sales/category` | `200 OK` | 252 ms | Category distribution across Electronics, Fashion, Home, etc. |
| `GET /api/orders?limit=3` | `200 OK` | 315 ms | Paginated order history with shipping state and payment status |
| `GET /api/pipeline/audit` | `200 OK` | 395 ms | Last 50 pipeline extraction runs with CDC watermark audit ledger |

---

## 4. Automated Test Suite Validation (Local & CI)

### 19 Automated Tests Passing in 3.12s

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

## 5. Security & Secret Leak Prevention Audit

- **Tracked files scanned:** All `.py`, `.yml`, `.yaml`, `.json`, `.sql`, `.toml` files.
- **Rules evaluated:**
  - No `.env` committed
  - No GCP service account JSON private keys committed
  - No database passwords hardcoded in source
  - No API tokens or PATs committed
- **Result:** **100% CLEAN** — verified by automated CI secret scan in GitHub Actions.
