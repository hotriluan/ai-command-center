import sqlite3

conn = sqlite3.connect('command_center.db')
cursor = conn.cursor()

# Get sales_data schema
cursor.execute("PRAGMA table_info(sales_data)")
columns = cursor.fetchall()

print("sales_data columns:")
for col in columns:
    print(f"  - {col[1]} ({col[2]})")

conn.close()
