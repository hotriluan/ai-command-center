import sqlite3

conn = sqlite3.connect('command_center_v2.db')
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cursor.fetchall()]
print("Tables in command_center_v2.db:")
for table in tables:
    print(f"\n{table}:")
    cursor.execute(f"PRAGMA table_info({table})")
    columns = cursor.fetchall()
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")

conn.close()
