import sqlite3

conn = sqlite3.connect('command_center_v2.db')
cursor = conn.cursor()

# Test the view
cursor.execute("SELECT * FROM view_sales_performance WHERE salesman_name LIKE '%HÙNG%'")
results = cursor.fetchall()

print("Testing view_sales_performance:")
print(f"Found {len(results)} rows for HÙNG")
for row in results:
    print(f"  {row}")

conn.close()
