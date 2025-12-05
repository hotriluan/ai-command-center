"""
Channel Mapping Debug Script
Inspects raw data types and values from sales_data.dist column
to diagnose why channels are falling into "Others" category
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from sqlalchemy import create_engine, text
import pandas as pd

# Database connection - use the correct database file
DATABASE_URL = "sqlite:///./command_center_v2.db"
engine = create_engine(DATABASE_URL)

print("=" * 60)
print("CHANNEL MAPPING AUDIT - RAW DATA INSPECTION")
print("=" * 60)

# STEP 1: Get distinct dist values and counts
print("\n--- STEP 1: DISTINCT DIST VALUES ---")
query = "SELECT dist, COUNT(*) as count FROM sales_data GROUP BY dist ORDER BY count DESC"
df = pd.read_sql(query, engine)
print(df.to_string(index=False))

# STEP 2: Check data type of dist column
print("\n--- STEP 2: DATA TYPE INSPECTION ---")
sample_query = "SELECT dist FROM sales_data WHERE dist IS NOT NULL LIMIT 5"
samples = pd.read_sql(sample_query, engine)

for idx, val in enumerate(samples['dist']):
    print(f"Sample {idx + 1}:")
    print(f"  Value: {repr(val)}")
    print(f"  Type: {type(val).__name__}")
    print(f"  Length: {len(str(val)) if val else 0}")
    
    # Check for whitespace
    if isinstance(val, str):
        print(f"  Stripped: {repr(val.strip())}")
        print(f"  Has leading/trailing spaces: {val != val.strip()}")

# STEP 3: Test mapping logic
print("\n--- STEP 3: MAPPING LOGIC TEST ---")
CHANNEL_MAP = {
    '11': 'Industry',
    '13': 'Retail',
    '15': 'Project'
}

print(f"CHANNEL_MAP keys: {list(CHANNEL_MAP.keys())}")
print(f"CHANNEL_MAP key types: {[type(k).__name__ for k in CHANNEL_MAP.keys()]}")

# Test mapping with actual data
print("\n--- STEP 4: MAPPING SIMULATION ---")
for idx, val in enumerate(samples['dist']):
    mapped = CHANNEL_MAP.get(val, 'Others')
    print(f"Raw value {repr(val)} -> Mapped to: '{mapped}'")
    
    # Try different conversions
    if val is not None:
        str_val = str(val)
        stripped_val = str_val.strip() if isinstance(val, str) else str_val
        
        print(f"  As string: {repr(str_val)} -> {CHANNEL_MAP.get(str_val, 'Others')}")
        print(f"  Stripped: {repr(stripped_val)} -> {CHANNEL_MAP.get(stripped_val, 'Others')}")

# STEP 5: Aggregate by mapped channels
print("\n--- STEP 5: CHANNEL AGGREGATION SIMULATION ---")
query_all = "SELECT dist FROM sales_data WHERE dist IS NOT NULL"
all_dist = pd.read_sql(query_all, engine)

# Apply mapping
all_dist['channel'] = all_dist['dist'].map(CHANNEL_MAP).fillna('Others')
channel_counts = all_dist['channel'].value_counts()

print("\nChannel Distribution:")
print(channel_counts.to_string())

print("\n" + "=" * 60)
print("AUDIT COMPLETE")
print("=" * 60)
