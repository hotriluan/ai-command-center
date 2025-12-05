import sqlite3
conn = sqlite3.connect('command_center_v2.db')
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(product_cost)")
print(cursor.fetchall())
conn.close()
