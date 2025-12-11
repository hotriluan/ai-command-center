
import sqlite3
import os
import time

DB_FILE = "command_center_v2.db"

def delete_data_raw():
    print(f"Connecting to {DB_FILE} for deletion...")
    if not os.path.exists(DB_FILE):
        print(f"Error: {DB_FILE} not found!")
        return

    conn = None
    try:
        conn = sqlite3.connect(DB_FILE, timeout=10) # 10s timeout
        cursor = conn.cursor()
        
        # Check before
        cursor.execute("SELECT count(*) FROM sales_data WHERE year=2025 AND month_number=12;")
        count_before = cursor.fetchone()[0]
        print(f"PRE-CHECK: Found {count_before} records to delete.")
        
        if count_before == 0:
            print("Nothing to delete.")
            return

        # Delete
        print("Executing DELETE command...")
        cursor.execute("DELETE FROM sales_data WHERE year=2025 AND month_number=12;")
        deleted_rows = cursor.rowcount
        print(f"Rows affected: {deleted_rows}")
        
        conn.commit()
        print("Commit successful.")
        
        # Check after
        cursor.execute("SELECT count(*) FROM sales_data WHERE year=2025 AND month_number=12;")
        count_after = cursor.fetchone()[0]
        print(f"POST-CHECK: Remaining records: {count_after}")
        
        if count_after == 0:
            print("SUCCESS: Data successfully deleted.")
        else:
            print("WARNING: Data may still exist.")
            
    except sqlite3.OperationalError as e:
        print(f"Database LOCKED or ERROR: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    delete_data_raw()
