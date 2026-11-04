# GCP Infrastructure as Code (Terraform)

This directory contains production-ready Terraform modules to provision the Google Cloud infrastructure required by **RetailPulse**:

## Managed Cloud Resources
1. **Google Cloud Storage (GCS)**:
   - Regional raw lake landing bucket (`retailpulse-lake-landing-dev`) with uniform bucket-level access, object versioning, and lifecycle policy (90-day transition to Nearline).
2. **Google BigQuery Datasets**:
   - `retailpulse_raw` (Bronze Ingestion Layer)
   - `retailpulse_staging` (Silver Cleansed & Typed Layer)
   - `retailpulse_dbt` (Gold Star-Schema Dimensional Marts Layer)
3. **Identity and Access Management (IAM)**:
   - Dedicated service account (`retailpulse-pipeline-runner`) with least-privilege roles:
     - `roles/storage.objectAdmin`
     - `roles/bigquery.dataEditor`
     - `roles/bigquery.jobUser`

## Deployment Instructions

```bash
# Initialize Terraform provider plugins
terraform init

# Review execution plan
terraform plan -var="project_id=YOUR_PROJECT_ID"

# Provision resources
terraform apply -var="project_id=YOUR_PROJECT_ID"
```
