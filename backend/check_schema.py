from database import engine
from sqlalchemy import inspect

inspector = inspect(engine)
print('Sales Data Columns:')
cols = inspector.get_columns('sales_data')
for i, col in enumerate(cols, 1):
    nullable = "NULL" if col['nullable'] else "NOT NULL"
    default = f" DEFAULT {col['default']}" if col.get('default') else ""
    print(f"{i:2}. {col['name']:20} {str(col['type']):20} {nullable}{default}")

print(f"\nTotal columns: {len(cols)}")

# Check for primary key
pk = inspector.get_pk_constraint('sales_data')
print(f"\nPrimary Key: {pk}")
