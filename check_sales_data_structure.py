from backend.database import SessionLocal
from sqlalchemy import text, inspect
import json

db = SessionLocal()

# Check sales_data table structure
inspector = inspect(db.get_bind())
columns = inspector.get_columns('sales_data')

print("=" * 80)
print("SALES_DATA TABLE STRUCTURE")
print("=" * 80)
print(f"\nTotal columns: {len(columns)}\n")

for col in columns:
    print(f"  {col['name']:<30} {str(col['type']):<20} {'NULL' if col['nullable'] else 'NOT NULL'}")

# Check if SO No. and SO Date columns exist
print("\n" + "=" * 80)
print("CHECKING FOR SALES ORDER COLUMNS")
print("=" * 80)

column_names = [col['name'] for col in columns]

check_columns = ['so_no', 'so_date', 'SO No.', 'SO Date', 'sales_order', 'sales_order_no']
for check_col in check_columns:
    if check_col in column_names:
        print(f"  ✅ Found: {check_col}")
    else:
        print(f"  ❌ Not found: {check_col}")

# Sample data from sales_data
print("\n" + "=" * 80)
print("SAMPLE DATA (First 3 rows)")
print("=" * 80)

query = text("SELECT * FROM sales_data LIMIT 3")
result = db.execute(query)
rows = result.fetchall()

if rows:
    # Get column names
    col_names = result.keys()
    print(f"\nColumns: {list(col_names)}\n")
    
    for i, row in enumerate(rows, 1):
        print(f"Row {i}:")
        row_dict = dict(zip(col_names, row))
        for key, value in row_dict.items():
            if value is not None and value != '':
                print(f"  {key}: {value}")
        print()

db.close()
