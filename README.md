# AMI Data Validation Simulator

Simulated Advanced Metering Infrastructure (AMI) system built to demonstrate ETL design, anomaly detection, and operational dashboard development.

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
pip install -r requirements.txt
streamlit run ami_dashboard.py
```

<img width="2240" height="1143" alt="Screenshot 2026-05-20 at 5 57 47 PM" src="https://github.com/user-attachments/assets/52d6ff8f-def0-4c0e-89c8-ec440b7491bf" />

<img width="2240" height="1143" alt="Screenshot 2026-05-20 at 5 58 03 PM" src="https://github.com/user-attachments/assets/4fe0bf1b-8935-41ac-a3d6-3097e5da4362" />

<img width="2240" height="1143" alt="Screenshot 2026-05-20 at 5 58 29 PM" src="https://github.com/user-attachments/assets/141130c1-cc44-424a-8303-13fb26b35ea7" />
