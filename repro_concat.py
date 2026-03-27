import pandas as pd
import numpy as np

# Create DF1 with Categorical event_id
df1 = pd.DataFrame({
    'event_id': pd.Categorical(['a', 'b', 'c']),
    'value': [1, 2, 3]
})

# Create DF2 with Categorical event_id
df2 = pd.DataFrame({
    'event_id': pd.Categorical(['d', 'e']),
    'value': [4, 5]
})

print("DF1 dtypes:")
print(df1.dtypes)
print("\nDF2 dtypes:")
print(df2.dtypes)

# Concatenate
result = pd.concat([df1, df2], ignore_index=True)

print("\nConcatenated DF:")
print(result)
print("\nResult dtypes:")
print(result.dtypes)

if result['event_id'].isnull().any():
    print("\nResult contains NaNs in event_id!")
else:
    print("\nNo NaNs in event_id.")
