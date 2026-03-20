import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="AMI Data Validation Simulator", layout="wide")
st.title("🚰 AMI Data Validation Simulator")
st.markdown("**Simulated Smart Water Meter System — WSSC Style**")

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
df['is_constant'] = (df['alert_type'] == 'Constant') | (df['usage_gallons'] == 0)
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

st.caption("Built with Python + Streamlit • Data simulated for WSSC AMI Analyst application")
