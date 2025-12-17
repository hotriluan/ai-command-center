import pandas as pd

file_path = r'c:\dev\ai-command-center\demodata\zrsd0021612.xlsx'
df = pd.read_excel(file_path, engine='openpyxl')

print("Excel file columns:")
for i, col in enumerate(df.columns, 1):
    print(f"{i:2}. {col}")

print(f"\nTotal rows: {len(df)}")

print("\nFirst 3 rows of key columns:")
key_cols = ['Billing Document', 'Billing Item', 'Material', 'Net Value', 'Salesman Name']
existing_cols = [col for col in key_cols if col in df.columns]
print(df[existing_cols].head(3))

print("\nChecking for NaN in Billing Document and Billing Item:")
if 'Billing Document' in df.columns:
    nan_count = df['Billing Document'].isna().sum()
    print(f"  Billing Document NaN count: {nan_count}")
if 'Billing Item' in df.columns:
    nan_count = df['Billing Item'].isna().sum()
    print(f"  Billing Item NaN count: {nan_count}")
