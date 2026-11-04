# RetailPulse Comprehensive Setup & Deployment Guide

## 1. System Requirements & Prerequisites
- **Operating System**: Windows 10/11, macOS (Apple Silicon / Intel), or Linux (Ubuntu 22.04+).
- **Python**: Version 3.11 or 3.12 (with `pip` and `virtualenv`).
- **MySQL**: MySQL Server 8.0+ running locally or in a container.
- **Optional**: Docker Desktop (for Airflow standalone orchestration) and Terraform (for automated GCP provisioning).

---

## 2. Local Quickstart (5-Minute Setup)

### Step 1: Clone Repository & Create Virtual Environment
```bash
git clone https://github.com/your-org/retailpulse.git
cd retailpulse

python -m venv .venv

# On Windows (PowerShell):
.venv\Scripts\Activate.ps1

# On Linux / macOS:
source .venv/bin/activate
```

### Step 2: Install Package & Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

### Step 3: Configure Environment Variables
Copy the template configuration file:
```bash
cp .env.example .env
```
Edit `.env` with your local MySQL database credentials:
```ini
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=retailpulse_db

# Storage configuration (defaults to local mock simulation if GCP credentials are not supplied)
GCS_BUCKET_NAME=retailpulse-lake-landing-dev
GCP_PROJECT_ID=retailpulse-dev
GCS_MOCK_DIR=data/gcs_mock
LOCAL_EXPORT_DIR=data/exports
```

### Step 4: Initialize MySQL Schema & Seed Data
```bash
# Creates database tables and metadata tracking
python scripts/init_database.py

# Seeds 1,000 customers, 200 products, 5,000 orders, 9,901 items, 5,000 payments
python scripts/load_data.py
```

### Step 5: Run the End-to-End Ingestion Pipeline
```bash
python scripts/run_pipeline.py --mode full
```

### Step 6: Launch the Interactive Streamlit Web UI
```bash
python -m streamlit run dashboard/app.py --server.port 8501
```
Open your browser at `http://localhost:8501` to view live revenue metrics, orders, customer distributions, and pipeline health logs!

---

## 3. Running Automated Tests & Verifications

### Execute Pytest Suites (Unit & Integration)
```bash
# Run unit tests (fast, in-memory)
pytest tests/unit -v

# Run integration tests against local MySQL
pytest tests/integration -v

# Run full test suite with coverage
pytest --tb=short
```

### Execute Code Quality Linter
```bash
python -m ruff check src tests
```

### Run Human QA Verification Script
```bash
python scripts/verify_qa_scenarios.py
```

---

## 4. Google Cloud Platform Production Setup

### Step 1: Provision Infrastructure via Terraform
```bash
cd infrastructure/gcp
terraform init
terraform apply -var="project_id=YOUR_GCP_PROJECT_ID"
cd ../..
```

### Step 2: Configure Service Account Credentials
1. In Google Cloud Console, generate a JSON key for `retailpulse-pipeline-runner`.
2. Save the key file securely (e.g. `credentials/gcp-sa-key.json`).
3. Set the environment variable in `.env`:
   ```ini
   GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials/gcp-sa-key.json
   GCP_PROJECT_ID=YOUR_GCP_PROJECT_ID
   GCS_BUCKET_NAME=retailpulse-lake-landing-dev
   ```

### Step 3: Execute dbt Transformations
```bash
cd dbt/retailpulse_dbt
dbt deps
dbt debug
dbt run
dbt test
```

---

## 5. Dockerized Deployment

### Standalone Airflow Orchestration
```bash
# Start Postgres metadata database and Airflow webserver/scheduler
docker compose up -d

# Check service logs
docker compose logs -f airflow
```
Access the Airflow UI at `http://localhost:8080` (Username: `airflow`, Password: `airflow`). Unpause the `retailpulse_pipeline` DAG to trigger automated daily batch processing.

---

## 6. Troubleshooting Guide

| Issue | Root Cause | Solution |
| :--- | :--- | :--- |
| `Can't connect to MySQL server on 'localhost:3306'` | MySQL server service stopped or incorrect port. | Start MySQL service via Windows Services (`services.msc`) or `net start MySQL80`. |
| `Access denied for user 'root'@'localhost'` | Wrong password specified in `.env`. | Verify password in `.env` matches your MySQL root account password. |
| `Connection refused: localhost:8080` | Docker Desktop is not running. | Start Docker Desktop or use local Python CLI runner (`python scripts/run_pipeline.py`). |
| `Unknown pytest mark 'unit'` | Custom markers not registered in test runner config. | Ensure markers are declared in `pyproject.toml` under `[tool.pytest.ini_options]`. |

