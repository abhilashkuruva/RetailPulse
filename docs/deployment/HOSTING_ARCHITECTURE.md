# RetailPulse: Hosting Architecture & Platform Selection

## 1. Hosting Architecture Overview

```
                         PUBLIC INTERNET
                               │
              ┌────────────────┴────────────────┐
              │                                 │
              ▼                                 ▼
   ┌─────────────────────┐         ┌─────────────────────┐
   │  STREAMLIT COMMUNITY│         │   RENDER.COM (Free) │
   │       CLOUD         │         │                     │
   │  (dashboard/app.py) │         │  FastAPI REST API   │
   │                     │         │  /health            │
   │  Live BI Dashboard  │         │  /api/metrics/*     │
   │  Plotly Charts      │         │  /api/orders        │
   │  Pipeline Viewer    │         │  /api/quality/*     │
   └────────┬────────────┘         └──────────┬──────────┘
            │                                 │
            ▼                                 ▼
   ┌─────────────────────────────────────────────────────┐
   │               EMBEDDED SQLite DATABASE              │
   │          (data/retailpulse_live.db ~2.3 MB)        │
   │                                                     │
   │   Snapshot of MySQL data, bundled in git repo.     │
   │   Zero additional hosting cost. No cold starts.    │
   └─────────────────────────────────────────────────────┘

              INTERNAL (Local Development Only)
              ─────────────────────────────────
              MySQL 8.0 → Python CDC Extractor → GCS → BigQuery → dbt → Airflow
```

---

## 2. Platform Selections & Rationale

### 2.1 Frontend / Dashboard: **Streamlit Community Cloud**
**URL:** https://share.streamlit.io  
**Cost:** 100% free, no credit card required

| Criterion | Evaluation |
| :--- | :--- |
| Cost | ✅ **Free forever** for public repos |
| Cold starts | ⚠️ 12-hour inactivity sleep; ~30s wake-up delay |
| Performance | ✅ 2.7 GB RAM; adequate for Pandas/Plotly |
| Deployment | ✅ GitHub auto-deploy on every push to master |
| Custom domains | ❌ Not supported on free tier (uses `.streamlit.app` subdomain) |
| SSL/HTTPS | ✅ Included automatically |
| Region | 🌐 US-East by default; acceptable latency for India (~150-200ms) |
| Suitability | ✅ **Best match** for Streamlit apps, zero config |

**Why chosen:** RetailPulse's primary user-facing component is the Streamlit dashboard. Streamlit Community Cloud is specifically designed for this use case — zero configuration, GitHub integration, free public deployment.

---

### 2.2 REST API Backend: **Render.com (Free Web Service)**
**URL:** https://render.com  
**Cost:** Free tier — 750 instance hours/month (enough for one always-on service)

| Criterion | Evaluation |
| :--- | :--- |
| Cost | ✅ Free (750 hours/month) |
| Cold starts | ⚠️ Spins down after 15 min inactivity; ~30-60s wake |
| RAM | 512 MB (adequate for FastAPI + SQLite reads) |
| Python support | ✅ Native; reads `requirements.txt` or `Procfile` |
| GitHub integration | ✅ Auto-deploy on push |
| Config file | ✅ `render.yaml` in root directory |
| Region | Singapore (`sg`) — closest available free region to India |
| Health checks | ✅ `/health` endpoint configured in `render.yaml` |

**Why chosen:** Render.com provides the most straightforward Python web service deployment with native `Procfile` support and no Dockerfile required on free tier. The Singapore region minimizes latency for India-based users.

---

### 2.3 Database: **Embedded SQLite (Bundled in Repository)**
**Cost:** $0 — no external database service required

| Criterion | Evaluation |
| :--- | :--- |
| Cost | ✅ Zero cost |
| Cold starts | ✅ **None** — SQLite reads from local disk |
| Performance | ✅ Sub-millisecond local reads |
| Data freshness | ⚠️ Static snapshot — regenerate from MySQL with `python scripts/export_sqlite.py` |
| Storage | 2.3 MB — well within GitHub's 100 MB file limit |
| Connection pooling | ✅ No connection limits |

**Why chosen:** For a portfolio/demo project, embedded SQLite completely eliminates database hosting complexity and cost. All 21,000+ synthetic records are bundled as `data/retailpulse_live.db`. When live MySQL is available (local dev), the app automatically switches to it.

---

## 3. Free-Tier Limitations Summary

| Provider | Limitation | Impact |
| :--- | :--- | :--- |
| Streamlit Community Cloud | Sleeps after 12h inactivity | First visit after sleep: ~30s wake delay |
| Streamlit Community Cloud | No custom domain | App URL is `xxx.streamlit.app` |
| Streamlit Community Cloud | 2.7 GB RAM limit | Low risk; app uses <400 MB |
| Render.com (API) | Spins down after 15 min | First API call after idle: ~30-60s delay |
| Render.com (API) | 512 MB RAM | Adequate for FastAPI + SQLite |
| Render.com (API) | 750 hours/month | Sufficient for one service 24/7 |
| SQLite | Static snapshot data | Not real-time; refresh needed after pipeline run |

---

## 4. Performance Characteristics

| Metric | Expected Value | Notes |
| :--- | :--- | :--- |
| Dashboard load (warm) | 1-3 seconds | SQLite reads are sub-ms |
| Dashboard load (cold start) | 25-40 seconds | After 12h inactivity sleep |
| API response (warm, `/health`) | 50-150ms | From Singapore to India |
| API response (cold start) | 30-60 seconds | Render spin-up |
| SQLite query (5000 orders) | <50ms | Local disk read |

---

## 5. Architecture Decision Record (ADR)

**Decision:** Use embedded SQLite instead of a free managed MySQL/PostgreSQL service.

**Alternatives considered:**
- **Render PostgreSQL free tier:** Expires and deletes data after 30 days. ❌ Unacceptable for portfolio.
- **Koyeb PostgreSQL free:** Only 5 hours active compute/month — inadequate. ❌
- **TiDB Cloud Starter:** Requires MySQL schema migration, 50M RU limit, complex setup. ❌
- **Neon (serverless PostgreSQL):** PostgreSQL, would require ORM/query migration from MySQL. ❌
- **PlanetScale:** Discontinued free tier in 2024. ❌

**Conclusion:** Embedded SQLite wins on simplicity, zero cost, zero cold start, and adequate performance for a portfolio project.

---

## 6. Security Architecture

- Credentials stored **only** in environment variables — never in source code
- `.env`, `secrets.toml` permanently `.gitignore`-excluded
- SQLite database contains only **synthetic** demo data — zero PII risk
- CORS on FastAPI API restricted to specific origins in production
- HTTPS enforced by both Streamlit Cloud and Render.com
- Database admin interfaces not exposed publicly

