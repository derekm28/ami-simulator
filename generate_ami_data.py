import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

np.random.seed(42)
random.seed(42)

num_rows = 5000

meter_ids = [f"MD-{10000 + i}" for i in range(num_rows)]
customer_accounts = [f"CUST-{1000 + (i % 1500)}" for i in range(num_rows)]

end_date = datetime.now()
start_date = end_date - timedelta(days=30)
timestamps = [start_date + timedelta(seconds=random.randint(0, int((end_date - start_date).total_seconds()))) for _ in range(num_rows)]

usage_gallons = np.random.normal(150, 80, num_rows).clip(0).round(1)

statuses = np.random.choice(['Success', 'Failed'], num_rows, p=[0.92, 0.08])

alert_types = []
for status in statuses:
    if status == 'Failed':
        alert_types.append(random.choice(['Tamper', 'Constant', 'Zero', 'Comm_Failure']))
    else:
        alert_types.append('None')

lats = np.random.uniform(39.0, 39.6, num_rows)   # Maryland area
lons = np.random.uniform(-77.2, -76.7, num_rows)

df = pd.DataFrame({
    'meter_id': meter_ids,
    'customer_account': customer_accounts,
    'read_timestamp': timestamps,
    'usage_gallons': usage_gallons,
    'status': statuses,
    'alert_type': alert_types,
    'latitude': lats,
    'longitude': lons
})

df = df.sort_values('read_timestamp').reset_index(drop=True)
df.to_csv('ami_meter_reads.csv', index=False)

print(f"✅ Generated {num_rows} realistic AMI meter reads!")
print("\nPreview of first 5 rows:")
print(df.head())
print("\nFile saved: ami_meter_reads.csv")
print(f"\nQuick summary:\n{df['status'].value_counts()}")
