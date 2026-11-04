# RetailPulse: Free Hosting Cost Report

## 1. Selected Providers & Current Free-Tier Allowances

### 1.1 Streamlit Community Cloud (Dashboard)
| Item | Value |
| :--- | :--- |
| **Monthly cost** | **$0.00** |
| Credit card required | No |
| Free app count | Unlimited public apps from public repos |
| RAM | 2.7 GB |
| Storage | Repo-bound (GitHub) |
| Bandwidth | Unlimited for public apps |
| Inactivity policy | Sleeps after **12 hours** of no traffic |
| Cold-start time | ~25-45 seconds after sleep |
| Custom domains | ❌ Not available on free tier |
| SSL/HTTPS | ✅ Included |
| Auto-deploy on push | ✅ GitHub integration |
| Free-tier expiry | None — permanently free for public repos |
| **Billing risk** | **None** — no paid upgrade paths exist without explicit action |

---

### 1.2 Render.com (FastAPI REST API)
| Item | Value |
| :--- | :--- |
| **Monthly cost** | **$0.00** |
| Credit card required | No |
| Instance hours | 750 free hours/month per workspace |
| RAM | 512 MB |
| CPU | Shared fractional vCPU |
| Persistent disk | ❌ Not available on free web services |
| Bandwidth | Shared workspace allowance |
| Inactivity policy | Spins down after **15 minutes** of no traffic |
| Cold-start time | ~30-60 seconds after spin-down |
| Custom domains | ✅ Supported (free managed TLS) |
| SSL/HTTPS | ✅ Included |
| Auto-deploy on push | ✅ GitHub integration |
| Free Postgres DB | ⚠️ **Expires after 30 days** — NOT used in this deployment |
| **Billing risk** | **Low** — staying within 750 hours prevents charges |
| **Important note** | 750 hours ≈ 31.25 days continuously — sufficient for one service 24/7 |

---

### 1.3 Embedded SQLite Database (Bundled in GitHub Repo)
| Item | Value |
| :--- | :--- |
| **Monthly cost** | **$0.00** |
| External service required | None |
| File size | ~2.3 MB |
| Cold starts | None — disk read |
| Persistence | Git history (immutable snapshots) |
| Data limits | GitHub 100 MB file limit (using only 2.3 MB) |
| Connection limits | None (SQLite in-process) |
| Billing risk | None |

---

## 2. Total Monthly Cost Breakdown

| Component | Provider | Monthly Cost |
| :--- | :--- | :--- |
| Dashboard (Streamlit) | Streamlit Community Cloud | **$0.00** |
| REST API (FastAPI) | Render.com | **$0.00** |
| Database | Embedded SQLite (GitHub) | **$0.00** |
| CI/CD | GitHub Actions | **$0.00** |
| Repository | GitHub | **$0.00** |
| **TOTAL** | | **$0.00 / month** |

---

## 3. Potential Charges — Risk Assessment

| Scenario | Provider | Risk Level | Mitigation |
| :--- | :--- | :--- | :--- |
| Render.com exceeds 750 hours | Render | 🟡 Low | Only 1 service deployed; 750h = 31.25 days |
| Streamlit paid upgrade | Streamlit | 🟢 None | No paid tier auto-activation |
| GitHub over-storage | GitHub | 🟢 None | Total repo < 10 MB |
| GCP charges (BigQuery/GCS) | Google Cloud | 🟡 Medium if connected | Use `USE_SQLITE=true` to bypass entirely |

> [!WARNING]
> If you connect a **real GCP project** (BigQuery/GCS) to the pipeline, cloud resource usage charges may apply depending on data scanned, storage used, and API calls made. The embedded SQLite deployment path **does not** connect to any GCP services and incurs **zero** cloud charges.

---

## 4. Free-Tier Policy Risks

| Risk | Description | Likelihood |
| :--- | :--- | :--- |
| Streamlit changes free-tier policy | Streamlit has maintained free community tier since 2022 | Low |
| Render removes free web services | Render discontinued free PostgreSQL; web services remain free | Medium |
| GitHub file size increases trigger LFS | SQLite at 2.3 MB; LFS threshold is 100 MB | Very Low |

**Recommendation:** If Render removes free web services in the future, the API can be migrated to Fly.io (free tier: 3 shared VMs, 160 GB bandwidth/month) with minimal configuration changes.

---

## 5. Spending Limits & Alerts

- **Render.com:** Set a **Budget Alert** in Render dashboard under Billing → Budget. Set to $0 to get notified before any charges.
- **Streamlit Community Cloud:** No billing settings needed — genuinely free for public repos.
- **Google Cloud (if connected):** Set a **Budget Alert** at $1 in GCP Console → Billing → Budgets & Alerts. Enable automatic cost controls.

