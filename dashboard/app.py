"""RetailPulse Executive BI Dashboard & Pipeline Control Center.

Production Streamlit application supporting both:
- Live MySQL connection (local development with real MySQL)
- Embedded SQLite (Streamlit Community Cloud deployment via data/retailpulse_live.db)

Displays:
1. Executive KPIs (Total Revenue, Orders, Delivery Rate, Customers, AOV)
2. Revenue Trends (Daily sales time series, 30-day rolling)
3. Geographic breakdown across 10 Indian metropolitan hubs
4. Product Category Performance and Margin Analysis
5. Live Ingestion Pipeline Audit Ledger (pipeline_metadata CDC watermarks)
6. Data Quality Violations & Quarantine Monitor
"""
from __future__ import annotations

import os
import sqlite3
from datetime import datetime
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

# ─── Page config (must be first Streamlit call) ──────────────────────────────
st.set_page_config(
    page_title="RetailPulse | GCP Data Engineering Platform",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://github.com/Kuruva-abhilash/RetailPulse",
        "Report a bug": "https://github.com/Kuruva-abhilash/RetailPulse/issues",
        "About": "RetailPulse: Production-Style GCP Data Engineering Platform | Deloitte GCP Portfolio",
    },
)

# ─── Database connection with MySQL → SQLite automatic failover ───────────────
SQLITE_PATH = Path(__file__).resolve().parent.parent / "data" / "retailpulse_live.db"


@st.cache_resource(show_spinner=False)
def get_db_engine():
    """Returns (connection_factory, engine_name) with automatic failover."""
    force_sqlite = os.getenv("USE_SQLITE", "false").lower() in ("true", "1", "yes")

    if not force_sqlite:
        try:
            from retailpulse.config.settings import get_settings
            settings = get_settings()
            import mysql.connector

            test_conn = mysql.connector.connect(
                host=settings.mysql_host,
                port=settings.mysql_port,
                user=settings.mysql_user,
                password=settings.mysql_password,
                database=settings.mysql_database,
                connection_timeout=2,
            )
            if test_conn.is_connected():
                test_conn.close()
                return "mysql", settings
        except Exception:
            pass

    if SQLITE_PATH.exists():
        return "sqlite", None

    return "none", None


def query_df(sql: str) -> pd.DataFrame:
    """Executes SQL against available database engine and returns a DataFrame."""
    engine, settings = get_db_engine()

    if engine == "mysql":
        import mysql.connector
        conn = mysql.connector.connect(
            host=settings.mysql_host,
            port=settings.mysql_port,
            user=settings.mysql_user,
            password=settings.mysql_password,
            database=settings.mysql_database,
        )
        # Adapt MySQL-specific syntax for compatibility if needed
        df = pd.read_sql(sql, conn)
        conn.close()
        return df

    if engine == "sqlite":
        # Adapt MySQL DATE() → substr for SQLite compatibility
        sqlite_sql = (
            sql
            .replace("DATE(o.order_date)", "substr(o.order_date, 1, 10)")
            .replace("DATE(", "substr(")
        )
        conn = sqlite3.connect(SQLITE_PATH)
        conn.row_factory = sqlite3.Row
        df = pd.read_sql_query(sqlite_sql, conn)
        conn.close()
        return df

    return pd.DataFrame()


# ─── Header ──────────────────────────────────────────────────────────────────
engine_name, _ = get_db_engine()
engine_badge = "🟢 MySQL Live" if engine_name == "mysql" else "🟡 SQLite Demo Mode"

st.title("🛒 RetailPulse: Production GCP Data Engineering Platform")
st.markdown(
    f"**End-to-End E-Commerce Batch ELT & Analytics Engine** | "
    f"*Deloitte GCP Data Engineer Portfolio* &nbsp;&nbsp;|&nbsp;&nbsp; {engine_badge}"
)

if engine_name == "none":
    st.error("No database available. Please run `python scripts/export_sqlite.py` to generate the demo database.")
    st.stop()

# ─── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Pipeline Control Center")

    if engine_name == "mysql":
        from retailpulse.config.settings import get_settings
        settings = get_settings()
        st.info(
            f"**Target DB:** `{settings.mysql_database}`\n"
            f"**Host:** `{settings.mysql_host}:{settings.mysql_port}`"
        )
        if st.button("🚀 Trigger Ingestion Pipeline Now", type="primary", use_container_width=True):
            from retailpulse.ingestion.pipeline import run_full_ingestion_pipeline
            with st.spinner("Extracting CDC records from MySQL → Staging GCS → Loading BigQuery..."):
                try:
                    res = run_full_ingestion_pipeline(settings, force_full_refresh=False)
                    st.success(f"✅ Pipeline succeeded! Execution ID: `{res['execution_id']}`")
                    st.cache_resource.clear()
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Execution failed: {e}")
    else:
        st.info("🗄️ **Demo Mode**\nRunning from embedded SQLite snapshot.\n\nTo connect live MySQL:\n```\nMYSQL_HOST=localhost python -m streamlit run dashboard/app.py\n```")

    st.markdown("---")
    st.markdown("### 🏗️ Architecture Medallion Layers")
    st.markdown(
        "- 🥉 **Bronze:** MySQL CDC → GCS CSV Landing\n"
        "- 🥈 **Silver:** dbt Cleansed & Typed Views\n"
        "- 🥇 **Gold:** Partitioned BigQuery Marts"
    )

    st.markdown("---")
    st.markdown("### 📚 Technical Stack")
    st.markdown(
        "| Layer | Technology |\n"
        "|---|---|\n"
        "| Source | MySQL 8.0 |\n"
        "| Ingestion | Python 3.11+ |\n"
        "| Data Lake | GCS |\n"
        "| Warehouse | BigQuery |\n"
        "| Transform | dbt Core |\n"
        "| Orchestrate | Airflow 2.10 |\n"
        "| Dashboard | Streamlit |"
    )

    st.markdown("---")
    st.markdown(
        "[![GitHub](https://img.shields.io/badge/GitHub-RetailPulse-black?logo=github)]"
        "(https://github.com/Kuruva-abhilash/RetailPulse)"
    )

# ─── KPIs ────────────────────────────────────────────────────────────────────
kpi_query = """
    SELECT
        COUNT(DISTINCT o.order_id) as total_orders,
        COUNT(DISTINCT o.customer_id) as total_customers,
        ROUND(SUM(CAST(p.payment_amount AS REAL)), 2) as total_revenue,
        ROUND(AVG(CAST(p.payment_amount AS REAL)), 2) as avg_order_value,
        COUNT(DISTINCT CASE WHEN o.order_status = 'delivered' THEN o.order_id END) as delivered_orders,
        COUNT(DISTINCT CASE WHEN o.order_status = 'cancelled' THEN o.order_id END) as cancelled_orders
    FROM orders o
    JOIN payments p ON o.order_id = p.order_id
    WHERE o.order_status != 'cancelled'
"""

try:
    df_kpi = query_df(kpi_query)
    total_revenue = float(df_kpi["total_revenue"].iloc[0] or 0)
    total_orders = int(df_kpi["total_orders"].iloc[0] or 0)
    total_customers = int(df_kpi["total_customers"].iloc[0] or 0)
    aov = float(df_kpi["avg_order_value"].iloc[0] or 0)
    delivered = int(df_kpi["delivered_orders"].iloc[0] or 0)
    fulfilment_rate = (delivered / total_orders * 100) if total_orders else 0

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("💰 Total Net Revenue", f"₹{total_revenue:,.2f}")
    col2.metric("📦 Total Orders", f"{total_orders:,}")
    col3.metric("✅ Fulfillment Rate", f"{fulfilment_rate:.1f}%")
    col4.metric("👥 Active Customers", f"{total_customers:,}")
    col5.metric("💳 Avg Order Value (AOV)", f"₹{aov:,.2f}")

except Exception as e:
    st.error(f"KPI query failed: {e}")

st.markdown("---")

# ─── Tabbed analytics ────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Sales Trends",
    "🗺️ Regional Analytics",
    "📂 Category Performance",
    "🔍 Pipeline Audit Ledger",
])

with tab1:
    st.subheader("Daily Revenue Timeline (Last 90 Days)")
    trend_query = """
        SELECT
            DATE(o.order_date) as order_day,
            COUNT(o.order_id) as orders_count,
            ROUND(SUM(CAST(p.payment_amount AS REAL)), 2) as daily_revenue
        FROM orders o
        JOIN payments p ON o.order_id = p.order_id
        WHERE o.order_status != 'cancelled'
        GROUP BY DATE(o.order_date)
        ORDER BY DATE(o.order_date) ASC
    """
    try:
        df_trend = query_df(trend_query)
        df_trend["order_day"] = pd.to_datetime(df_trend["order_day"])
        df_trend = df_trend.sort_values("order_day").tail(90)

        fig = px.area(
            df_trend, x="order_day", y="daily_revenue",
            labels={"order_day": "Date", "daily_revenue": "Revenue (₹)"},
            color_discrete_sequence=["#1f77b4"],
        )
        fig.update_layout(showlegend=False, height=350)
        st.plotly_chart(fig, use_container_width=True)

        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Daily Orders Count")
            fig2 = px.bar(
                df_trend, x="order_day", y="orders_count",
                labels={"order_day": "Date", "orders_count": "Orders"},
                color_discrete_sequence=["#2ca02c"],
            )
            fig2.update_layout(height=250)
            st.plotly_chart(fig2, use_container_width=True)
        with c2:
            st.subheader("Revenue Summary")
            st.dataframe(
                df_trend[["order_day", "orders_count", "daily_revenue"]]
                .tail(14)
                .sort_values("order_day", ascending=False)
                .rename(columns={
                    "order_day": "Date",
                    "orders_count": "Orders",
                    "daily_revenue": "Revenue (₹)",
                }),
                use_container_width=True,
            )
    except Exception as e:
        st.warning(f"Could not load sales trend: {e}")

with tab2:
    st.subheader("Revenue by Indian Metropolitan Hub")
    city_query = """
        SELECT
            o.shipping_city as city,
            o.shipping_state as state,
            COUNT(o.order_id) as total_orders,
            ROUND(SUM(CAST(p.payment_amount AS REAL)), 2) as city_revenue
        FROM orders o
        JOIN payments p ON o.order_id = p.order_id
        WHERE o.order_status != 'cancelled'
        GROUP BY o.shipping_city, o.shipping_state
        ORDER BY city_revenue DESC
    """
    try:
        df_city = query_df(city_query)
        c1, c2 = st.columns([2, 1])
        with c1:
            fig = px.bar(
                df_city, x="city", y="city_revenue",
                color="city_revenue",
                color_continuous_scale="Blues",
                labels={"city": "City", "city_revenue": "Revenue (₹)"},
            )
            fig.update_layout(showlegend=False, height=350)
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            st.subheader("Top Cities")
            st.dataframe(
                df_city[["city", "state", "total_orders", "city_revenue"]]
                .rename(columns={
                    "city": "City",
                    "state": "State",
                    "total_orders": "Orders",
                    "city_revenue": "Revenue (₹)",
                }),
                use_container_width=True,
            )
    except Exception as e:
        st.warning(f"Could not load regional data: {e}")

with tab3:
    st.subheader("Product Category Performance")
    cat_query = """
        SELECT
            pr.category,
            COUNT(oi.order_item_id) as items_sold,
            ROUND(SUM(CAST(oi.quantity AS REAL) * CAST(oi.unit_price AS REAL)), 2) as gross_sales,
            ROUND(SUM(CAST(oi.discount_amount AS REAL)), 2) as total_discounts
        FROM order_items oi
        JOIN products pr ON oi.product_id = pr.product_id
        JOIN orders o ON oi.order_id = o.order_id
        WHERE o.order_status != 'cancelled'
        GROUP BY pr.category
        ORDER BY gross_sales DESC
    """
    try:
        df_cat = query_df(cat_query)
        df_cat["net_sales"] = df_cat["gross_sales"] - df_cat["total_discounts"]

        c1, c2 = st.columns(2)
        with c1:
            fig = px.pie(
                df_cat, values="gross_sales", names="category",
                title="Gross Sales by Category",
                color_discrete_sequence=px.colors.qualitative.Set2,
            )
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            fig2 = px.bar(
                df_cat, x="category", y=["gross_sales", "total_discounts"],
                title="Gross Sales vs Discounts",
                labels={"value": "Amount (₹)", "category": "Category"},
                color_discrete_sequence=["#1f77b4", "#ff7f0e"],
                barmode="group",
            )
            fig2.update_layout(height=350)
            st.plotly_chart(fig2, use_container_width=True)

        st.dataframe(
            df_cat.rename(columns={
                "category": "Category",
                "items_sold": "Items Sold",
                "gross_sales": "Gross Sales (₹)",
                "total_discounts": "Discounts (₹)",
                "net_sales": "Net Sales (₹)",
            }),
            use_container_width=True,
        )
    except Exception as e:
        st.warning(f"Could not load category data: {e}")

with tab4:
    st.subheader("🔍 CDC Watermark & Ingestion Execution Audit Ledger")
    st.markdown(
        "_The `pipeline_metadata` table records every CDC extraction batch — "
        "tracking watermarks, record counts, execution statuses, and latencies._"
    )
    meta_query = """
        SELECT
            execution_id,
            source_table,
            execution_status,
            records_extracted,
            records_loaded,
            last_successful_extraction_timestamp,
            started_at,
            completed_at,
            error_message
        FROM pipeline_metadata
        ORDER BY started_at DESC
        LIMIT 20
    """
    try:
        df_meta = query_df(meta_query)
        # Colour-code by status
        def style_status(val):
            if val == "SUCCESS":
                return "background-color: #d4edda; color: #155724"
            if val == "FAILED":
                return "background-color: #f8d7da; color: #721c24"
            return "background-color: #fff3cd; color: #856404"

        styled = df_meta.style.applymap(style_status, subset=["execution_status"])
        st.dataframe(styled, use_container_width=True)

        # Watermark summary
        wm_query = """
            SELECT
                source_table,
                MAX(last_successful_extraction_timestamp) as latest_watermark,
                COUNT(execution_id) as total_batches,
                SUM(CAST(records_loaded AS INTEGER)) as total_records_loaded
            FROM pipeline_metadata
            WHERE execution_status = 'SUCCESS'
            GROUP BY source_table
            ORDER BY source_table
        """
        df_wm = query_df(wm_query)
        st.subheader("Current CDC Watermarks per Source Table")
        st.dataframe(
            df_wm.rename(columns={
                "source_table": "Table",
                "latest_watermark": "Latest Watermark",
                "total_batches": "Successful Batches",
                "total_records_loaded": "Total Records Loaded",
            }),
            use_container_width=True,
        )
    except Exception as e:
        st.warning(f"Could not load audit ledger: {e}")

# ─── Footer ──────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    f"<small>RetailPulse v1.0.0 | GCP Data Engineering Platform | "
    f"Built for Deloitte India T&T EAID GCP Data Engineer Portfolio | "
    f"Last refreshed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')}</small>",
    unsafe_allow_html=True,
)
