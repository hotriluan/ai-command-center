import pandas as pd
import sys

# Redirect output properly
sys.stdout.reconfigure(encoding='utf-8')

# Read cooispi.xlsx
print("=" * 80)
print("COOISPI.XLSX - Production Orders")
print("=" * 80)
df_prod = pd.read_excel('demodata/cooispi.XLSX')
print(f"\nTotal rows: {len(df_prod)}")
print(f"\nColumn count: {len(df_prod.columns)}")
print("\nColumn names (if headers exist):")
for i, col in enumerate(df_prod.columns):
    print(f"  {i}: {col}")

print("\nFirst row sample:")
print(df_prod.iloc[0].to_dict())

print("\n" + "=" * 80)
print("ZRSD0021612.XLSX - Sales Data")
print("=" * 80)
df_sales = pd.read_excel('demodata/zrsd0021612.xlsx')
print(f"\nTotal rows: {len(df_sales)}")
print(f"\nColumn count: {len(df_sales.columns)}")
print("\nColumn names:")
for i, col in enumerate(df_sales.columns):
    print(f"  {i}: {col}")

# Check for key columns
key_columns = ['SO No.', 'SO Date', 'Billing Date', 'Sales Order']
print("\nKey columns check:")
for col in key_columns:
    if col in df_sales.columns:
        print(f"  ✅ {col} - Found")
        non_null = df_sales[col].notna().sum()
        print(f"     Non-null values: {non_null}/{len(df_sales)}")
    else:
        print(f"  ❌ {col} - Not found")
