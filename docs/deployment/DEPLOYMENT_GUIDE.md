# RetailPulse: Complete Deployment Guide

## A. Deploy the Streamlit Dashboard (Streamlit Community Cloud)

### Prerequisites
- GitHub account with the RetailPulse repository pushed (public)
- Streamlit Community Cloud account: https://share.streamlit.io (sign in with GitHub)

### Step-by-Step

1. **Go to** https://share.streamlit.io → **New app**
2. **Connect GitHub:** Select `Kuruva-abhilash/RetailPulse`
3. **Branch:** `master`
4. **Main file path:** `dashboard/app.py`
5. **App URL:** Choose something like `retailpulse-dashboard`
6. Under **Advanced settings**, add one secret:
   ```toml
   USE_SQLITE = "true"
   ```
7. Click **Deploy**

Streamlit Community Cloud will:
- Install dependencies from `requirements.txt`
- Install the package from `pyproject.toml`
- Start the app pointing at the embedded SQLite database
- Auto-redeploy every time you push to `master`

**Live URL:** `https://retailpulse-dashboard.streamlit.app`

---

## B. Deploy the FastAPI Backend (Render.com)

### Prerequisites
- Render.com account: https://render.com (sign in with GitHub)

### Step-by-Step

1. **Go to** https://dashboard.render.com → **New** → **Web Service**
2. **Connect GitHub:** Select `Kuruva-abhilash/RetailPulse`
3. Render will auto-detect the `render.yaml` — click **Apply**

   Or configure manually:
   - **Build Command:** `pip install -r requirements.txt && pip install -e .`
   - **Start Command:** `uvicorn retailpulse.api.main:app --host 0.0.0.0 --port $PORT`
   - **Region:** Singapore
   - **Instance Type:** Free

4. Under **Environment Variables**, add:
   ```
   USE_SQLITE = true
   PYTHONUNBUFFERED = 1
   ```
5. Click **Create Web Service**

**Health check URL:** `https://retailpulse-api.onrender.com/health`  
**API docs:** `https://retailpulse-api.onrender.com/docs`

---

## C. Environment Variables Reference

| Variable | Development (`.env`) | Streamlit Cloud Secret | Render Env Var |
| :--- | :--- | :--- | :--- |
| `USE_SQLITE` | `false` | `true` | `true` |
| `MYSQL_HOST` | `localhost` | (not needed) | (not needed) |
| `MYSQL_PORT` | `3306` | (not needed) | (not needed) |
| `MYSQL_USER` | `root` | (not needed) | (not needed) |
| `MYSQL_PASSWORD` | `password` | (not needed) | (not needed) |
| `MYSQL_DATABASE` | `retailpulse_db` | (not needed) | (not needed) |
| `GCS_BUCKET_NAME` | `retailpulse-lake-landing-dev` | (not needed) | (not needed) |
| `GCP_PROJECT_ID` | `retailpulse-dev` | (not needed) | (not needed) |

---

## D. Refreshing the Demo Database

When MySQL data changes locally:
```bash
# 1. Run the pipeline to get fresh data
python scripts/run_pipeline.py --mode full

# 2. Export to SQLite snapshot
python scripts/export_sqlite.py

# 3. Commit and push (triggers auto-redeploy)
git add data/retailpulse_live.db
git commit -m "data: refresh SQLite demo snapshot"
git push origin master
```

---

## E. Troubleshooting

| Problem | Likely Cause | Solution |
| :--- | :--- | :--- |
| Streamlit app shows "Sleeping" page | 12h inactivity | Click "Yes, get this app back up!" — wakes in ~30s |
| Render API returns 502 | Service spinning up after 15min idle | Wait 30-60s and retry |
| `ModuleNotFoundError: retailpulse` | Package not installed | Verify `-e .` in build command |
| SQLite "table not found" | Old database schema | Re-run `python scripts/export_sqlite.py` and push |
| Dashboard shows "Could not connect" | SQLite file missing | Confirm `data/retailpulse_live.db` is tracked in git |

---

## F. Local Development (Always Works)

```bash
# Dashboard (MySQL or SQLite auto-detected)
python -m streamlit run dashboard/app.py --server.port 8501

# REST API (SQLite mode for fast local testing)
USE_SQLITE=true uvicorn retailpulse.api.main:app --reload --port 8000

# Full pipeline with live MySQL
python scripts/run_pipeline.py --mode full
```
