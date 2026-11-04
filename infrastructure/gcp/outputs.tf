output "gcs_bucket_url" {
  description = "The URI of the created GCS raw bucket"
  value       = google_storage_bucket.raw_lake.url
}

output "bigquery_raw_dataset" {
  description = "The BigQuery Raw dataset ID"
  value       = google_bigquery_dataset.raw_dataset.dataset_id
}

output "bigquery_staging_dataset" {
  description = "The BigQuery Staging dataset ID"
  value       = google_bigquery_dataset.staging_dataset.dataset_id
}

output "bigquery_analytics_dataset" {
  description = "The BigQuery Analytics dataset ID"
  value       = google_bigquery_dataset.analytics_dataset.dataset_id
}

output "service_account_email" {
  description = "The email address of the pipeline runner service account"
  value       = google_service_account.pipeline_runner.email
}

