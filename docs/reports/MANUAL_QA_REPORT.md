# RetailPulse Manual Quality Assurance (QA) Report
**Date:** 2026-11-04  
**Author:** RetailPulse Data Quality & QA Automation Engineering Team  
**Environment:** Windows / MySQL 8.0.45 / Python 3.13 / Airflow 2.10.3 / BigQuery & GCS Simulation  

---

## Executive Summary
This document provides empirical validation logs for the 10 manual QA testing scenarios defined in Section 19 of the project engineering specification. All scenarios were executed against live MySQL databases and ingestion services.

---

## Test Scenario Execution Matrix

| Scenario ID | Test Scenario Description | Execution Type | Expected Outcome | Actual Outcome | Status |
|---|---|---|---|---|---|
| **SC-01** | First-Time Execution | End-to-End Batch | Full baseline ingestion of customers, products, orders, items, payments | Ingested all 5 tables (5000 orders, 9901 items, 1000 customers) | **PASS** |
| **SC-02** | Incremental Execution (CDC) | Watermark Trigger | Only extract newly added or updated rows based on `updated_at` | Extracted 20 changed records matching watermark window | **PASS** |
| **SC-03** | Duplicate Key Handling | Constraint Validation | Duplicate source IDs flagged and rejected or deduplicated | Detected duplicate primary key {101}; zero corruptions | **PASS** |
| **SC-04** | Missing Mandatory Values | Contract Assertion | Reject rows missing mandatory fields (`order_id`, `customer_id`) | Caught missing `order_id` error; flagged record | **PASS** |
| **SC-05** | Invalid Business Logic | Range & Domain Check | Filter out negative prices, negative stock, and illegal statuses | Detected negative price (-200), negative qty (-5), and illegal status | **PASS** |
| **SC-06** | Airflow Failure Isolation | Orchestration Simulation | Upstream task failure stops all downstream data mutations | Linear dependency graph blocked downstream execution on upstream error | **PASS** |
| **SC-07** | Pipeline Idempotency | Re-execution | Consecutive runs of identical batch create no duplicate rows | Re-run completed with 0 primary key errors or row duplications | **PASS** |
| **SC-08** | Empty Data Incremental Run | Boundary Case | Pipeline executes safely without error when 0 new rows exist | 0 incremental records handled safely; exit code 0 | **PASS** |
| **SC-09** | Large Dataset Scalability | Performance Test | Stream ~10,000 items without memory spikes or timeouts | Chunked cursor extraction streamed 9,901 line-items under 1.2s | **PASS** |
| **SC-10** | Intermediate Failure Recovery | Fault Recovery | Staging failure aborts watermark advancement; retry succeeds | Failed batch preserved watermark; subsequent run recovered cleanly | **PASS** |

---

## Detailed Scenario Logs

### Scenario 1: First-Time Execution
- **Preconditions:** Freshly initialized MySQL database `retailpulse_db`.
- **Command:** `python scripts/run_pipeline.py --full-refresh`
- **Observations:** Extracted 1,000 customers, 200 products, 5,000 orders, 9,901 order items, 5,000 payments. Objects staged into partitioned date directories `raw/<table>/year=2026/month=11/day=04/`. Initialized `pipeline_metadata` with baseline watermarks.

### Scenario 2: Incremental Execution (CDC & Updated Records)
- **Mutation:** Inserted new customer (ID: 99991) and new order (ID: 88881). Updated Order #1 status from `confirmed` to `delivered`.
- **Command:** `python scripts/run_pipeline.py`
- **Observations:** Ingestion service queried `WHERE updated_at >= :watermark - 5m`. Extracted and loaded only updated/new records without re-processing entire 5,000 order history.

### Scenario 3: Duplicate Handling
- **Preconditions:** Injected fixture containing duplicate `order_id = 101`.
- **Observations:** `duplicate_ids()` validator isolated key `101`. MySQL table constraints enforced unique primary key; dbt schema tests assert `unique` on `order_id`.

### Scenario 4: Missing Values
- **Preconditions:** Provided record with null `order_id`.
- **Observations:** `validate_order_row()` emitted `['order_id is required']`. Prevented corrupt record from entering the analytics warehouse.

### Scenario 5: Invalid Records
- **Preconditions:** Provided record with `quantity = -5`, `unit_price = -200`, `order_status = 'UNKNOWN_BOGUS_STATUS'`.
- **Observations:** All three violations flagged and quarantined before staging.

### Scenario 7: Idempotency
- **Execution:** Executed `run_full_ingestion_pipeline` back-to-back twice.
- **Observations:** `ON DUPLICATE KEY UPDATE` and BigQuery deduplication MERGE strategies ensured table counts remained exact with 0 duplicated rows.

### Scenario 8: Empty Data Handling
- **Execution:** Ingestion executed with watermark set to future date (`2099-01-01`).
- **Observations:** Extracted 0 rows. File exporter generated empty header-only file; loader skipped partition without corrupting existing data.

### Scenario 10: Intermediate Failure Recovery
- **Execution:** Injected artificial failure during load stage after extraction completed.
- **Observations:** `pipeline_metadata` recorded `execution_status = 'FAILED'`. `last_successful_extraction_timestamp` was NOT updated. Next pipeline execution safely resumed from previous watermark, guaranteeing **at-least-once** delivery with zero data loss.

