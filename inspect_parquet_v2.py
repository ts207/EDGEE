import pandas as pd
import numpy as np

file_path = "/home/irene/Edge/artifacts/golden_synthetic_discovery/reports/volatility_transition/synthetic_2month_run_v6/volatility_transition_events.parquet"

try:
    df = pd.read_parquet(file_path, columns=["event_id"])
    
    print(f"Dtype: {df['event_id'].dtype}")
    print(f"Total rows: {len(df)}")
    print(f"Null count: {df['event_id'].isna().sum()}")
    
    # Check for string nulls
    string_nulls = df[df['event_id'].astype(str).str.lower().isin(['nan', 'null', 'none', ''])].shape[0]
    print(f"String-like nulls ('nan', 'null', 'none', ''): {string_nulls}")

    # Check for weird characters
    weird_chars = df[~df['event_id'].astype(str).str.match(r'^[a-zA-Z0-9_\-]+$', na=True)]
    print(f"Values with non-alphanumeric/hyphen/underscore: {len(weird_chars)}")
    if len(weird_chars) > 0:
        print("Sample weird values:")
        print(weird_chars['event_id'].head().tolist())

    unique_count = df['event_id'].nunique()
    print(f"Unique count: {unique_count}")
    print(f"Duplicates: {len(df) - unique_count}")

except Exception as e:
    print(f"Error: {e}")
