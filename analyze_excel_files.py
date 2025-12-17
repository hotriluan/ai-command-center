import pandas as pd

# Read cooispi.xlsx
print("=" * 80)
print("COOISPI.XLSX - Production Orders")
print("=" * 80)
df_prod = pd.read_excel('demodata/cooispi.XLSX', nrows=5)
print("\nFirst 5 rows:")
print(df_prod)
print("\nColumn names:")
print(df_prod.columns.tolist())
print(f"\nTotal rows: {len(pd.read_excel('demodata/cooispi.XLSX'))}")

print("\n" + "=" * 80)
print("ZRSD0021612.XLSX - Sales Data")
print("=" * 80)
df_sales = pd.read_excel('demodata/zrsd0021612.xlsx', nrows=5)
print("\nFirst 5 rows:")
print(df_sales)
print("\nColumn names:")
print(df_sales.columns.tolist())
print(f"\nTotal rows: {len(pd.read_excel('demodata/zrsd0021612.xlsx'))}")

# Check for SO No. column
if 'SO No.' in df_sales.columns:
    print("\n✅ SO No. column found in sales data")
    print(f"Sample SO No. values: {df_sales['SO No.'].head().tolist()}")
    
if 'SO Date' in df_sales.columns:
    print("✅ SO Date column found in sales data")
    print(f"Sample SO Date values: {df_sales['SO Date'].head().tolist()}")
    
if 'Billing Date' in df_sales.columns:
    print("✅ Billing Date column found in sales data")
    print(f"Sample Billing Date values: {df_sales['Billing Date'].head().tolist()}")
