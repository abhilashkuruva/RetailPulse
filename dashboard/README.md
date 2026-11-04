# RetailPulse Looker Studio Business Intelligence Dashboard

## Dashboard Overview
The **RetailPulse E-Commerce Executive Dashboard** provides real-time visibility into business KPIs, sales trends, geographic demand, and customer retention. It connects directly to curated BigQuery views in the `retailpulse_analytics` layer.

---

## Dashboard Layout & Visual Components

### 1. Executive Scorecard KPIs
- **Total Revenue (INR):** `SUM(total_amount)` filtered for non-cancelled orders.
- **Total Orders Placed:** `COUNT(DISTINCT order_id)`.
- **Fulfillment Rate:** `(Completed Orders / Total Orders) * 100%`.
- **Active Customers:** `COUNT(DISTINCT customer_id)`.
- **Average Order Value (AOV):** `Total Revenue / Total Orders`.

### 2. Analytical Charts
- **Daily Revenue Trend:** Time series line chart displaying gross and net daily sales over time.
- **Monthly Revenue Growth:** Bar chart with previous-month benchmarks showing MoM trajectories.
- **Revenue by Geographic City:** Geo map and horizontal bar chart breakdown of sales across Indian metropolitan hubs (Bengaluru, Mumbai, Delhi, Hyderabad, Chennai, Pune).
- **Revenue by Product Category:** Treemap or donut chart comparing Electronics, Fashion, Home & Kitchen, Beauty, and Sports.
- **Top 10 Selling Products:** Ranked table chart tracking unit sales volume and gross margins.
- **Order Status Distribution:** Donut chart breakdown (`delivered`, `shipped`, `confirmed`, `cancelled`, `returned`).
- **Payment Gateway Performance:** Stacked bar chart showing success vs failure rates across `UPI`, `CREDIT_CARD`, `DEBIT_CARD`, `NETBANKING`, and `COD`.

### 3. Interactive Dimension Controls
- **Date Range Picker:** Defaults to trailing 90 days.
- **City & State Dropdown:** Filters data by shipping destination.
- **Product Category Dropdown:** Filter by merchandise taxonomy.

---

## Step-by-Step Connection Guide

1. Navigate to [Google Looker Studio](https://lookerstudio.google.com).
2. Click **Create** -> **Data Source**.
3. Select **BigQuery** connector.
4. Authorize with your Google Cloud account credentials.
5. Select:
   - **Project:** `retailpulse-production` (or your GCP project ID).
   - **Dataset:** `retailpulse_analytics`.
   - **Table/View:** `vw_looker_executive_kpis`.
6. Click **Connect** and set numeric currency types for `total_amount`.
7. Click **Create Report** and drag-and-drop the prepared scorecards and charts!

