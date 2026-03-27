import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from sqlalchemy import create_engine


# ====================== SQL DATABASE CONNECTION ======================
engine = create_engine('sqlite:///ami_data.db')

# ====================== SQL QUERIES ======================

sample_cte = """
WITH sample_reads AS (
    SELECT *
    FROM meter_reads
    ORDER BY read_timestamp DESC
    LIMIT 100
)
"""

# 1. Unread Meters (> 7 days)
unread_sql = sample_cte + """
SELECT meter_id, customer_account, read_timestamp, usage_gallons, alert_type,
       julianday('now') - julianday(read_timestamp) AS days_since_read
FROM sample_reads
WHERE julianday('now') - julianday(read_timestamp) > 7
ORDER BY days_since_read DESC
"""

# 2. Tamper Alerts Summary
tamper_sql = sample_cte + """
SELECT alert_type, 
       COUNT(*) as alert_count,
       ROUND(AVG(usage_gallons), 1) as avg_usage_gallons
FROM sample_reads
WHERE alert_type = 'Tamper'
GROUP BY alert_type
"""

# 3. Constant / Zero Reads
constant_sql = sample_cte + """
SELECT meter_id, customer_account, read_timestamp, usage_gallons, alert_type,
       julianday('now') - julianday(read_timestamp) AS days_since_read
FROM sample_reads
WHERE alert_type IN ('Constant', 'Zero') OR usage_gallons = 0
ORDER BY days_since_read DESC
"""

# 4. Communication Failures & Overall Exception Summary
comm_sql = """
WITH sample_reads AS (
    SELECT *
    FROM meter_reads
    ORDER BY read_timestamp DESC
    LIMIT 100
),
alert_types AS (
    SELECT 'Tamper' AS alert_type
    UNION ALL
    SELECT 'Constant'
    UNION ALL
    SELECT 'Zero'
    UNION ALL
    SELECT 'Comm_Failure'
)
SELECT
    alert_types.alert_type,
    COUNT(sample_reads.alert_type) AS count,
    ROUND(COUNT(sample_reads.alert_type) * 100.0 / (SELECT COUNT(*) FROM sample_reads), 1) AS percentage
FROM alert_types
LEFT JOIN sample_reads
    ON sample_reads.alert_type = alert_types.alert_type
GROUP BY alert_types.alert_type
ORDER BY count DESC, alert_types.alert_type
"""

# Execute all queries
unread_df   = pd.read_sql(unread_sql, engine)
tamper_df   = pd.read_sql(tamper_sql, engine)
constant_df = pd.read_sql(constant_sql, engine)
comm_df     = pd.read_sql(comm_sql, engine)

st.set_page_config(page_title="AMI Data Validation Simulator", layout="wide")
st.title("🚰 AMI Data Validation Simulator")
st.markdown("**Simulated Smart Water Meter System**")

st.info("📊 Main dashboard uses **pandas** (CSV data)\n\n"
        "🔍 SQL queries are shown below for demonstration")

st.subheader("📊 Main Dashboard")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("ami_meter_reads.csv")
    df['read_timestamp'] = pd.to_datetime(df['read_timestamp'])
    return df

df = load_data()

# Calculate exception metrics
today = datetime.now()
df['days_since_read'] = (today - df['read_timestamp']).dt.days

df['is_unread'] = df['days_since_read'] > 7
df['is_tamper'] = df['alert_type'] == 'Tamper'
df['is_constant'] = (df['alert_type'] == 'Constant') | (df['alert_type'] == 'Zero') | (df['usage_gallons'] == 0)
df['is_comm_failure'] = df['alert_type'] == 'Comm_Failure'

# Sidebar filters
st.sidebar.header("Filters")
date_range = st.sidebar.date_input("Read Date Range", 
                                  [df['read_timestamp'].min().date(), df['read_timestamp'].max().date()])
alert_filter = st.sidebar.multiselect("Alert Type", 
                                      options=['None', 'Tamper', 'Constant', 'Zero', 'Comm_Failure'],
                                      default=['Tamper', 'Constant', 'Comm_Failure'])

# Filter the data
filtered_df = df[
    (df['read_timestamp'].dt.date >= date_range[0]) &
    (df['read_timestamp'].dt.date <= date_range[1]) &
    (df['alert_type'].isin(alert_filter) | (len(alert_filter) == 0))
]

# KPI Cards
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Meters", f"{len(df):,}")
col2.metric("Unread Meters (7+ days)", f"{filtered_df['is_unread'].sum():,}", delta="High Priority")
col3.metric("Tamper Alerts", f"{filtered_df['is_tamper'].sum():,}", delta="Security")
col4.metric("Constant/Zero Reads", f"{filtered_df['is_constant'].sum():,}")
col5.metric("Comm Failures", f"{filtered_df['is_comm_failure'].sum():,}")

# Charts & Table
tab1, tab2, tab3 = st.tabs(["📊 Overview Charts", "📋 Exception Table", "🗺️ Problem Meter Map"])

with tab1:
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(px.bar(filtered_df['alert_type'].value_counts().reset_index(), 
                               x='alert_type', y='count', title="Alert Types"), use_container_width=True)
    with c2:
        st.plotly_chart(px.histogram(filtered_df, x='usage_gallons', nbins=30, 
                                     title="Usage Distribution (Gallons)"), use_container_width=True)

with tab2:
    st.dataframe(filtered_df[['meter_id', 'customer_account', 'read_timestamp', 
                              'usage_gallons', 'alert_type', 'days_since_read']].sort_values('days_since_read', ascending=False),
                 use_container_width=True, height=400)

with tab3:
    st.plotly_chart(px.scatter_mapbox(filtered_df[filtered_df['is_unread'] | filtered_df['is_tamper']], 
                                      lat="latitude", lon="longitude", 
                                      hover_name="meter_id", hover_data=["alert_type"],
                                      color="alert_type", zoom=9, height=600,
                                      mapbox_style="open-street-map"), use_container_width=True)

st.divider()

# ====================== DISPLAY SQL RESULTS ======================
st.subheader("🔍 SQL Query Results Using 100 Latest Meter Reads")

# Show queries
st.subheader("SQL Queries Used")
with st.expander("View SQL Code - Unread Meters"):
    st.code(unread_sql, language="sql")

with st.expander("View SQL Code - Alert Summary"):
    st.code(comm_sql, language="sql")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Unread Meters (>7 days)", len(unread_df))
col2.metric("Tamper Alerts", tamper_df['alert_count'].iloc[0] if not tamper_df.empty else 0)
col3.metric("Constant/Zero Reads", len(constant_df) if 'constant_df' in locals() else 0)

comm_failure = comm_df.loc[comm_df['alert_type'] == 'Comm_Failure', 'percentage'].iloc[0] if not comm_df.empty else 0
col4.metric("Comm Failures", f"{comm_failure:.1f}%")

col1, col2 = st.columns(2)

with col1:
    if not unread_df.empty:
        st.dataframe(unread_df.head(100), use_container_width=True)
    

# Show full exception summary
st.subheader("Alert Distribution from SQL")
st.dataframe(comm_df, use_container_width=True)

st.caption("Built with Python + Streamlit • Data simulated for WSSC AMI Analyst application")
