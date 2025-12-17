"""
Force kill all processes and drop table
"""
import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

db_config = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'ai_command_center'),
}

print("Connecting...")
connection = pymysql.connect(**db_config)
cursor = connection.cursor()

# Show all processes
print("\nAll processes:")
cursor.execute("SHOW PROCESSLIST")
for row in cursor.fetchall():
    print(f"  ID={row[0]}, User={row[1]}, DB={row[3]}, Command={row[4]}, Time={row[5]}, State={row[6]}")

# Kill all processes touching sales_data except current
print("\nKilling processes...")
cursor.execute("SELECT ID FROM INFORMATION_SCHEMA.PROCESSLIST WHERE DB='ai_command_center' AND ID != CONNECTION_ID()")
for row in cursor.fetchall():
    try:
        pid = row[0]
        cursor.execute(f"KILL {pid}")
        print(f"  ✅ Killed process {pid}")
    except Exception as e:
        print(f"  ⚠️  Could not kill {pid}: {e}")

connection.commit()

print("\nWaiting 2 seconds...")
import time
time.sleep(2)

# Now try to drop
print("\nDropping table...")
try:
    cursor.execute("DROP TABLE IF EXISTS sales_data")
    connection.commit()
    print("  ✅ Table dropped!")
except Exception as e:
    print(f"  ❌ Error: {e}")

cursor.close()
connection.close()
