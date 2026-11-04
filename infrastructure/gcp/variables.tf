variable "project_id" {
  description = "The Google Cloud Platform Project ID"
  type        = string
  default     = "retailpulse-dev"
}

variable "region" {
  description = "Primary GCP region for resources"
  type        = string
  default     = "asia-south1"
}

variable "environment" {
  description = "Deployment environment tag (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "gcs_bucket_name" {
  description = "Name of the GCS bucket for raw data lake landing"
  type        = string
  default     = "retailpulse-lake-landing-dev"
}

variable "raw_dataset_id" {
  description = "BigQuery dataset ID for Bronze Raw tables"
  type        = string
  default     = "retailpulse_raw"
}

variable "staging_dataset_id" {
  description = "BigQuery dataset ID for Silver Staging views"
  type        = string
  default     = "retailpulse_staging"
}

variable "analytics_dataset_id" {
  description = "BigQuery dataset ID for Gold Analytics dimensional marts"
  type        = string
  default     = "retailpulse_dbt"
}
