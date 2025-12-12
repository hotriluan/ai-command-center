
import pandas as pd
from io import BytesIO

# Read the file
df = pd.read_excel('demodata/ZRFI005.xlsx', engine='openpyxl')

print("=" * 80)
print("ZRFI005.XLSX FILE ANALYSIS")
print("=" * 80)

print(f"\nTotal rows: {len(df)}")
print(f"\nColumns ({len(df.columns)}):")
for i, col in enumerate(df.columns):
    print(f"  {i+1}. {col}")

print("\n" + "=" * 80)
print("SAMPLE DATA (First 3 rows)")
print("=" * 80)
print(df.head(3).to_string())

print("\n" + "=" * 80)
print("NULL VALUE ANALYSIS")
print("=" * 80)
null_counts = df.isnull().sum()
for col in df.columns:
    if null_counts[col] > 0:
        print(f"  {col}: {null_counts[col]} null values")

print("\n" + "=" * 80)
print("CRITICAL COLUMNS CHECK")
print("=" * 80)
critical_cols = ['Customer Code', 'Customer Name', 'Distribution Channel']
for col in critical_cols:
    if col in df.columns:
        null_count = df[col].isnull().sum()
        empty_count = (df[col].astype(str).str.strip() == '').sum()
        print(f"  {col}:")
        print(f"    - Null: {null_count}")
        print(f"    - Empty strings: {empty_count}")
        print(f"    - Sample values: {df[col].dropna().head(3).tolist()}")
    else:
        print(f"  {col}: COLUMN NOT FOUND!")
