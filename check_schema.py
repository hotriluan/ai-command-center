import sqlite3
conn = sqlite3.connect('command_center_v2.db')
cursor = conn.cursor()

print("=== SALES_DATA SCHEMA ===")
cursor.execute("PRAGMA table_info(sales_data)")
for col in cursor.fetchall():
    print(f"{col[1]:20} {col[2]:15}")

print("\n=== PRODUCT_COST SCHEMA ===")
cursor.execute("PRAGMA table_info(product_cost)")
for col in cursor.fetchall():
    print(f"{col[1]:20} {col[2]:15}")

print("\n=== SAMPLE SALES_DATA ===")
cursor.execute("SELECT * FROM sales_data LIMIT 1")
row = cursor.fetchone()
cursor.execute("PRAGMA table_info(sales_data)")
cols = [c[1] for c in cursor.fetchall()]
if row:
    for col, val in zip(cols, row):
        print(f"{col:20} = {val}")

conn.close()
