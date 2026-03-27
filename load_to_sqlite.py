import pandas as pd
from sqlalchemy import create_engine

engine = create_engine('sqlite:///ami_data.db')
df = pd.read_csv('ami_meter_reads.csv')
df['read_timestamp'] = pd.to_datetime(df['read_timestamp'])
df.to_sql('meter_reads', engine, if_exists='replace', index=False)
print("Loaded data into SQLite table 'meter_reads'")