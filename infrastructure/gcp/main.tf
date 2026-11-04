# Terraform Configuration for RetailPulse GCP Infrastructure

terraform {
  required_version = ">= 1.5.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# 1. Google Cloud Storage Bucket for Raw Lake Landing
resource "google_storage_bucket" "raw_lake" {
  name          = var.gcs_bucket_name
  location      = var.region
  force_destroy = false

  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition {
      age = 90
    }
    action {
      type = "SetStorageClass"
      storage_class = "NEARLINE"
    }
  }

  labels = {
    environment = var.environment
    project     = "retailpulse"
  }
}

# 2. BigQuery Datasets for Medallion Architecture
resource "google_bigquery_dataset" "raw_dataset" {
  dataset_id                  = var.raw_dataset_id
  friendly_name               = "RetailPulse Bronze Raw Ingestion"
  description                 = "Raw external table loads landed from GCS CSV extracts"
  location                    = var.region
  default_table_expiration_ms = null

  labels = {
    layer       = "bronze"
    project     = "retailpulse"
    environment = var.environment
  }
}

resource "google_bigquery_dataset" "staging_dataset" {
  dataset_id                  = var.staging_dataset_id
  friendly_name               = "RetailPulse Silver Staging Views"
  description                 = "Cleansed, typed and standardized dbt staging models"
  location                    = var.region
  default_table_expiration_ms = null

  labels = {
    layer       = "silver"
    project     = "retailpulse"
    environment = var.environment
  }
}

resource "google_bigquery_dataset" "analytics_dataset" {
  dataset_id                  = var.analytics_dataset_id
  friendly_name               = "RetailPulse Gold Analytics Marts"
  description                 = "Star-schema fact and dimension tables and executive reporting marts"
  location                    = var.region
  default_table_expiration_ms = null

  labels = {
    layer       = "gold"
    project     = "retailpulse"
    environment = var.environment
  }
}

# 3. Dedicated Service Account for CI/CD and Airflow Pipeline Runner
resource "google_service_account" "pipeline_runner" {
  account_id   = "retailpulse-pipeline-runner"
  display_name = "RetailPulse Automated Ingestion Pipeline Runner"
}

resource "google_project_iam_member" "gcs_admin" {
  project = var.project_id
  role    = "roles/storage.objectAdmin"
  member  = "serviceAccount:${google_service_account.pipeline_runner.email}"
}

resource "google_project_iam_member" "bq_editor" {
  project = var.project_id
  role    = "roles/bigquery.dataEditor"
  member  = "serviceAccount:${google_service_account.pipeline_runner.email}"
}

resource "google_project_iam_member" "bq_job_user" {
  project = var.project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.pipeline_runner.email}"
}

