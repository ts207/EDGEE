import pandas as pd
import numpy as np

file_path = "/home/irene/Edge/artifacts/golden_synthetic_discovery/reports/volatility_transition/synthetic_2month_run_v6/volatility_transition_events.parquet"

try:
    df = pd.read_parquet(file_path, columns=["event_id"])
    
    print(f"Dtype: {df['event_id'].dtype}")
    print(f"Total rows: {len(df)}")
    print(f"Null count: {df['event_id'].isna().sum()}")
    
    # Check for empty strings if it's an object/string type
    if df['event_id'].dtype == 'object' or df['event_id'].dtype == 'string':
        empty_strings = (df['event_id'].astype(str).str.strip() == '').sum()
        print(f"Empty or whitespace-only strings: {empty_strings}")
        
    print("\nSample values:")
    print(df['event_id'].head(10).tolist())
    
    unique_count = df['event_id'].nunique()
    print(f"\nUnique count: {unique_count}")
    if unique_count != len(df):
        print(f"Duplicates found: {len(df) - unique_count}")
    else:
        print("All values are unique.")

    # Check for non-standard formats (e.g., weird characters)
    # This is a bit exploratory. Let's see if there's anything not alphanumeric/hyphen/underscore if it's a string.
    if df['event_id'].dtype == 'object' or df['event_id'].dtype == 'string':
        weird_chars = df[~df['event_id'].astype(str).str.match(r'^[a-zA-Z0-9_\-]+$', na=True)]
        if not weird_chars.empty:
            print(f"\nFound {len(weird_chars)} values with non-alphanumeric/hyphen/underscore characters.")
            print("Sample weird values:")
            print(weird_chars['event_id'].head().tolist())

except Exception as e:
    print(f"Error: {e}")
