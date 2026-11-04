-- ==============================================================================
-- RETAILPULSE BIGQUERY DATASET INITIALIZATION
-- Multi-layered Medallion Architecture: Raw (Bronze), Staging (Silver), Analytics (Gold)
-- ==============================================================================

-- 1. Raw Layer (Bronze): Ingestion landing zone for untransformed CSV CDC feeds
CREATE SCHEMA IF NOT EXISTS `retailpulse_raw`
OPTIONS (
  location = 'asia-south1',
  description = 'Landing dataset for raw CDC batches ingested from Google Cloud Storage'
);

-- 2. Staging Layer (Silver): Cleansed, deduplicated, and typed relational models
CREATE SCHEMA IF NOT EXISTS `retailpulse_staging`
OPTIONS (
  location = 'asia-south1',
  description = 'Cleansed, typed, and standardized views and tables managed by dbt'
);

-- 3. Analytics Layer (Gold): Dimensional models, fact tables, and business marts
CREATE SCHEMA IF NOT EXISTS `retailpulse_analytics`
OPTIONS (
  location = 'asia-south1',
  description = 'Curated Star-Schema dimensional warehouse and aggregate data marts for BI dashboards'
);
