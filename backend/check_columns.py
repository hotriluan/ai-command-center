import pandas as pd

# Read Excel file
df = pd.read_excel('../demodata/ZRFI005.xlsx', engine='openpyxl')

# Write column names to file
with open('column_names.txt', 'w', encoding='utf-8') as f:
    f.write("COLUMN NAMES IN ZRFI005.XLSX:\n")
    f.write("=" * 60 + "\n")
    for i, col in enumerate(df.columns, 1):
        f.write(f"{i:2}. '{col}'\n")
    
    f.write("\n" + "=" * 60 + "\n")
    f.write("FILE INFO:\n")
    f.write("=" * 60 + "\n")
    f.write(f"Total rows: {len(df)}\n")
    f.write(f"Total columns: {len(df.columns)}\n")

print("Column names saved to column_names.txt")
