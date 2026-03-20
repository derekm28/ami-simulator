import pandas as pd
from datetime import datetime

# Load the data
df = pd.read_csv('ami_meter_reads.csv')
df['read_timestamp'] = pd.to_datetime(df['read_timestamp'])

today = datetime.now()

# Calculate days since last read
df['days_since_read'] = (today - df['read_timestamp']).dt.days

# === EXCEPTION REPORTS (same as WSSC job) ===
unread_meters = df[(df['status'] == 'Failed') | (df['days_since_read'] > 1)]
alert_summary = df.groupby('alert_type').size().reset_index(name='count')

# Save the files
df.to_csv('clean_meter_reads.csv', index=False)
unread_meters.to_csv('exceptions_report.csv', index=False)
alert_summary.to_csv('alert_summary.csv', index=False)

print("✅ AMI Data Processing Complete!")
print(f"   Total meters: {len(df)}")
print(f"   Exceptions found: {len(unread_meters)}")
print("\nFiles created:")
print("   - clean_meter_reads.csv")
print("   - exceptions_report.csv")
print("   - alert_summary.csv")
