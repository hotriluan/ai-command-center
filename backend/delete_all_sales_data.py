
import sqlite3
import os
import time

DB_FILE = "command_center_v2.db"

def delete_all_data():
    print(f"Connecting to {DB_FILE} for FULL deletion...")
    if not os.path.exists(DB_FILE):
        print(f"Error: {DB_FILE} not found!")
        return

    conn = None
    try:
        conn = sqlite3.connect(DB_FILE, timeout=10)
        cursor = conn.cursor()
        
        # Check before
        cursor.execute("SELECT count(*) FROM sales_data;")
        count_before = cursor.fetchone()[0]
        print(f"PRE-CHECK: Found {count_before} total records in sales_data.")
        
        if count_before == 0:
            print("Table is already empty.")
            return

        # Delete
        print("Executing DELETE FROM sales_data...")
        cursor.execute("DELETE FROM sales_data;")
        deleted_rows = cursor.rowcount
        print(f"Rows affected: {deleted_rows}")
        
        conn.commit()
        print("Commit successful.")
        
        # Check after
        cursor.execute("SELECT count(*) FROM sales_data;")
        count_after = cursor.fetchone()[0]
        print(f"POST-CHECK: Remaining records: {count_after}")
        
        if count_after == 0:
            print("SUCCESS: All sales data has been permanently deleted.")
        else:
            print("WARNING: Some data remains.")
            
    except sqlite3.OperationalError as e:
        print(f"Database LOCKED or ERROR: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    delete_all_data()
