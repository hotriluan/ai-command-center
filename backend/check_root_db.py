import sqlite3

# Connect to root database
conn = sqlite3.connect('../command_center.db')
cursor = conn.cursor()

# Check tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cursor.fetchall()]
print("Tables in root database:")
for table in tables:
    print(f"  - {table}")

# Check if sales_data exists and has data
if 'sales_data' in tables:
    cursor.execute("SELECT COUNT(*) FROM sales_data")
    count = cursor.fetchone()[0]
    print(f"\nsales_data has {count} rows")
else:
    print("\n❌ sales_data table NOT FOUND in root database")

conn.close()
