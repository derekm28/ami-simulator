# AMI Data Validation Simulator

Simulated Advanced Metering Infrastructure (AMI) system to practice data validation, exception reporting, and dashboard creation — tailored for utility roles like WSSC Water's AMI Analyst.

**Features**
- Generates realistic smart water meter data (timestamps, usage in gallons, statuses, alerts, MD geo coordinates)
- Detects common AMI exceptions: unread meters, tamper alerts, constant/zero reads, comm failures
- Interactive Streamlit app with:
  - KPI cards (total meters, unread count, alerts breakdown)
  - Filterable exception table
  - Usage trends & alert charts
  - Map of problem meters

**Tech Stack**
- Python (pandas, datetime)
- Streamlit + Plotly for interactive dashboard
- Simulated SQL-style logic for exception detection

**To Run Locally**
```bash
pip install streamlit plotly pandas
streamlit run ami_dashboard.py
