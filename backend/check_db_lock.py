
import sqlite3
import os
import time

DB_FILE = "command_center_v2.db"

def check_lock():
    print(f"Checking access to {DB_FILE}...")
    if not os.path.exists(DB_FILE):
        print(f"Error: {DB_FILE} not found!")
        return

    try:
        conn = sqlite3.connect(DB_FILE, timeout=5)
        cursor = conn.cursor()
        cursor.execute("PRAGMA integrity_check;")
        result = cursor.fetchone()
        print(f"Integrity check: {result}")
        
        cursor.execute("SELECT count(*) FROM sales_data WHERE year=2025 AND month_number=12;")
        count = cursor.fetchone()[0]
        print(f"accessible rows for Dec 2025: {count}")
        
        conn.close()
        print("Database access SUCCESS.")
    except sqlite3.OperationalError as e:
        print(f"Database LOCKED or ERROR: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    check_lock()
