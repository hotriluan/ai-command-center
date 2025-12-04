import sqlite3

conn = sqlite3.connect('command_center_v2.db')
c = conn.cursor()
c.execute("SELECT sql FROM sqlite_master WHERE type='view' AND name='view_sales_performance_v2'")
result = c.fetchone()

if result:
    print(result[0])
else:
    print("View not found")

conn.close()
