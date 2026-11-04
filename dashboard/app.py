"""RetailPulse Executive BI Dashboard & Pipeline Control Center.

Streamlit interactive application connected live to local MySQL database.
Displays:
1. Executive KPIs (Total Revenue, Orders, Delivered Rate, Customers, AOV)
2. Revenue Trends (Daily sales, Category margins)
3. Geographic breakdown across 10 Indian cities
4. Live Ingestion Pipeline Runner & Watermark Tracker
"""
from datetime import datetime
import pandas as pd
import streamlit as st
import mysql.connector

from retailpulse.config.settings import get_settings
from retailpulse.ingestion.pipeline import run_full_ingestion_pipeline

st.set_page_config(
    page_title="RetailPulse | E-Commerce Data Engineering Dashboard",
    page_icon="🛒",
    layout="wide",
)

settings = get_settings()

def get_connection():
    return mysql.connector.connect(
        host=settings.mysql_host,
        port=settings.mysql_port,
        user=settings.mysql_user,
        password=settings.mysql_password,
        database=settings.mysql_database,
    )

st.title("🛒 RetailPulse: Production GCP Data Engineering Platform")
st.markdown("**End-to-End E-Commerce Batch ELT & Analytics Engine** | *Deloitte GCP Data Engineer Portfolio*")

# Sidebar: Controls & Settings
with st.sidebar:
    st.header("⚙️ Pipeline Control Center")
    st.info(f"**Target DB:** `{settings.mysql_database}`\n**Host:** `{settings.mysql_host}:{settings.mysql_port}`")
    
    if st.button("🚀 Trigger Ingestion Pipeline Now", type="primary", use_container_width=True):
        with st.spinner("Extracting CDC records from MySQL -> Staging GCS -> Loading BigQuery..."):
            try:
                res = run_full_ingestion_pipeline(settings, force_full_refresh=False)
                st.success(f"Pipeline executed successfully! Execution ID: {res['execution_id']}")
                st.rerun()
            except Exception as e:
                st.error(f"Execution failed: {e}")

    st.markdown("---")
    st.markdown("### 📊 Architecture Medallion")
    st.markdown("- **Bronze:** MySQL CDC & GCS CSV Landing\n- **Silver:** dbt Cleansed & Typed Views\n- **Gold:** Partitioned BigQuery Marts")

# Load live database metrics
try:
    conn = get_connection()
    
    # Query 1: Topline KPIs
    kpi_query = """
        SELECT
            COUNT(DISTINCT o.order_id) as total_orders,
            COUNT(DISTINCT o.customer_id) as total_customers,
            ROUND(SUM(p.payment_amount), 2) as total_revenue,
            ROUND(AVG(p.payment_amount), 2) as avg_order_value,
            COUNT(DISTINCT CASE WHEN o.order_status = 'delivered' THEN o.order_id END) as delivered_orders
        FROM orders o
        JOIN payments p ON o.order_id = p.order_id
        WHERE o.order_status != 'cancelled'
    """
    df_kpi = pd.read_sql(kpi_query, conn)
    
    # Query 2: Daily Sales Trend
    trend_query = """
        SELECT 
            DATE(o.order_date) as order_day,
            COUNT(o.order_id) as orders_count,
            ROUND(SUM(p.payment_amount), 2) as daily_revenue
        FROM orders o
        JOIN payments p ON o.order_id = p.order_id
        WHERE o.order_status != 'cancelled'
        GROUP BY 1
        ORDER BY 1 ASC
    """
    df_trend = pd.read_sql(trend_query, conn)
    df_trend['order_day'] = pd.to_datetime(df_trend['order_day'])

    # Query 3: City breakdown
    city_query = """
        SELECT 
            shipping_city as city,
            COUNT(o.order_id) as total_orders,
            ROUND(SUM(p.payment_amount), 2) as city_revenue
        FROM orders o
        JOIN payments p ON o.order_id = p.order_id
        WHERE o.order_status != 'cancelled'
        GROUP BY 1
        ORDER BY 3 DESC
    """
    df_city = pd.read_sql(city_query, conn)

    # Query 4: Category Margin
    cat_query = """
        SELECT 
            pr.category,
            COUNT(oi.order_item_id) as items_sold,
            ROUND(SUM(oi.quantity * oi.unit_price - oi.discount_amount), 2) as category_sales
        FROM order_items oi
        JOIN products pr ON oi.product_id = pr.product_id
        JOIN orders o ON oi.order_id = o.order_id
        WHERE o.order_status != 'cancelled'
        GROUP BY 1
        ORDER BY 3 DESC
    """
    df_cat = pd.read_sql(cat_query, conn)

    # Query 5: Pipeline Metadata Ledger
    meta_query = """
        SELECT 
            execution_id,
            source_table,
            execution_status,
            records_extracted,
            records_loaded,
            last_successful_extraction_timestamp,
            started_at,
            completed_at
        FROM pipeline_metadata
        ORDER BY started_at DESC
        LIMIT 10
    """
    df_meta = pd.read_sql(meta_query, conn)
    conn.close()

    # Render KPI Cards
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Total Net Revenue", f"₹{df_kpi['total_revenue'].iloc[0]:,.2f}")
    with col2:
        st.metric("Total Orders Placed", f"{df_kpi['total_orders'].iloc[0]:,}")
    with col3:
        fulfillment_rate = (df_kpi['delivered_orders'].iloc[0] / df_kpi['total_orders'].iloc[0]) * 100
        st.metric("Fulfillment Rate", f"{fulfillment_rate:.1f}%")
    with col4:
        st.metric("Active Customers", f"{df_kpi['total_customers'].iloc[0]:,}")
    with col5:
        st.metric("Average Order Value (AOV)", f"₹{df_kpi['avg_order_value'].iloc[0]:,.2f}")

    st.markdown("---")

    # Render Charts
    tab1, tab2, tab3 = st.tabs(["📈 Sales & Regional Analytics", "📋 Category Performance", "🔍 Audit Ledger & CDC Metadata"])

    with tab1:
        c1, c2 = st.columns([3, 2])
        with c1:
            st.subheader("Daily Revenue Timeline")
            st.line_chart(df_trend.set_index('order_day')['daily_revenue'])
        with c2:
            st.subheader("Revenue by Metropolitan Hub")
            st.bar_chart(df_city.set_index('city')['city_revenue'])

    with tab2:
        c3, c4 = st.columns(2)
        with c3:
            st.subheader("Sales Volume by Category")
            st.bar_chart(df_cat.set_index('category')['category_sales'])
        with c4:
            st.subheader("Merchandise Category Breakdown")
            st.dataframe(df_cat, use_container_width=True)

    with tab3:
        st.subheader("Pipeline Ingestion Audit Ledger (pipeline_metadata)")
        st.dataframe(df_meta, use_container_width=True)

except Exception as e:
    st.error(f"Could not connect to MySQL database: {e}")
    st.info("Make sure MySQL is running on localhost:3306 with credentials root / password.")

