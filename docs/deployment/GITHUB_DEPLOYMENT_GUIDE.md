# RetailPulse: GitHub Publishing & Deployment Guide

## 1. GitHub Repository Information
- **Repository:** [github.com/Kuruva-abhilash/RetailPulse](https://github.com/Kuruva-abhilash/RetailPulse)
- **Visibility:** Public (required for Streamlit Community Cloud free tier)
- **Default Branch:** `master`
- **Git Author:** Kuruva_abhilash <srinivasabhilash8210@gmail.com>

---

## 2. Repository Structure

```
RetailPulse/
├── .github/workflows/           # CI/CD pipelines
│   ├── python-tests.yml         # Unit tests + ruff on every push
│   ├── code-quality.yml         # Lint + secret scan on every push
│   └── dbt-validation.yml       # dbt model syntax check
├── src/retailpulse/             # Core Python package
│   ├── api/main.py              # FastAPI REST API (MySQL + SQLite failover)
│   ├── ingestion/               # CDC extractor, GCS uploader, BQ loader
│   ├── monitoring/              # Execution tracker & watermarks
│   ├── quality/                 # Data validation contracts
│   └── utils/                   # Logger and exception taxonomy
├── dashboard/app.py             # Streamlit BI Dashboard (MySQL + SQLite failover)
├── data/retailpulse_live.db     # Embedded SQLite demo database (~2.3 MB)
├── database/                    # MySQL schema DDL and seed SQL
├── dbt/retailpulse_dbt/         # dbt Medallion models (Staging, Intermediate, Marts)
├── airflow/dags/                # Apache Airflow DAG
├── infrastructure/              # Terraform GCP + Docker configs
├── tests/                       # 19 automated tests
├── docs/                        # Architecture, setup, audit reports
├── render.yaml                  # Render.com API deployment config
├── Procfile                     # Heroku/Render start command
├── .streamlit/config.toml       # Streamlit theme & server config
└── requirements.txt             # Pinned production dependencies
```

---

## 3. How to Update the Repository

### Standard update workflow:
```bash
# 1. Make changes to source files
# 2. Run tests
python -m pytest tests/unit -v

# 3. Run linter
python -m ruff check src tests

# 4. Regenerate SQLite demo data (if MySQL data changed)
python scripts/export_sqlite.py

# 5. Stage, commit, and push
git add .
git commit -m "feat: your change description"
git push origin master
```

### Streamlit Community Cloud auto-deploys on every push to master.

---

## 4. Branch Strategy
| Branch | Purpose |
| :--- | :--- |
| `master` | Production — triggers auto-deployment to Streamlit Cloud |
| `develop` | Feature development & integration testing |
| `feature/*` | Individual feature branches, merged via PR |

---

## 5. CI/CD Configuration

### GitHub Actions Workflows:
| Workflow | Trigger | Actions |
| :--- | :--- | :--- |
| `python-tests.yml` | Push/PR to master | Installs deps, runs `pytest tests/unit`, runs `ruff` |
| `code-quality.yml` | Push/PR to master | Ruff lint, secret scan |
| `dbt-validation.yml` | Push/PR to master | dbt model syntax validation |

### Workflow Badges (add to README):
```markdown
[![Tests](https://github.com/Kuruva-abhilash/RetailPulse/actions/workflows/python-tests.yml/badge.svg)](https://github.com/Kuruva-abhilash/RetailPulse/actions)
[![Code Quality](https://github.com/Kuruva-abhilash/RetailPulse/actions/workflows/code-quality.yml/badge.svg)](https://github.com/Kuruva-abhilash/RetailPulse/actions)
```

---

## 6. Security Pre-Push Checklist

Before every push to public GitHub, verify:
- [ ] `.env` is not staged (`git status` confirms)
- [ ] `credentials/` is not staged
- [ ] `.streamlit/secrets.toml` is not staged
- [ ] No MySQL password in Python source (only via `settings.mysql_password` from env)
- [ ] No GCP service account JSON committed
- [ ] `data/retailpulse_live.db` contains only synthetic demo data

---

## 7. Setting Up a Fresh Clone

```bash
git clone https://github.com/Kuruva-abhilash/RetailPulse.git
cd RetailPulse

# Create virtual environment
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# OR
.venv\Scripts\Activate.ps1  # Windows PowerShell

# Install dependencies
pip install -r requirements.txt
pip install -e .

# Configure environment (copy the template)
cp .env.example .env
# Edit .env with your local MySQL credentials

# Initialize local MySQL database
python scripts/init_database.py
python scripts/load_data.py

# Run the dashboard locally
python -m streamlit run dashboard/app.py
```

