"""
Cleanup Script V2: Remove Duplicate Records
Uses ROWID instead of id column
"""
import sqlite3
import os

def cleanup_duplicates_v2():
    """Remove duplicate records from sales_data using ROWID"""
    db_path = os.path.join(os.path.dirname(__file__), 'command_center_v2.db')
    
    print("=" * 80)
    print("CLEANUP V2: Remove Duplicate Records")
    print("=" * 80)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # STEP 1: Count current records
        print("\n[STEP 1] Counting current records...")
        cursor.execute("SELECT COUNT(*) FROM sales_data")
        before_count = cursor.fetchone()[0]
        print(f"  Total records: {before_count:,}")
        
        # STEP 2: Delete duplicates using ROWID
        print("\n[STEP 2] Deleting duplicates (keeping first occurrence)...")
        
        cursor.execute("""
            DELETE FROM sales_data
            WHERE ROWID NOT IN (
                SELECT MIN(ROWID)
                FROM sales_data
                GROUP BY salesman_name, description, net_value, month_number, year, customer_name
            )
        """)
        
        deleted_count = cursor.rowcount
        print(f"  ✅ Deleted {deleted_count:,} duplicate records")
        
        conn.commit()
        
        # STEP 3: Verify cleanup
        print("\n[STEP 3] Verifying cleanup...")
        
        cursor.execute("SELECT COUNT(*) FROM sales_data")
        after_count = cursor.fetchone()[0]
        
        print(f"  Before: {before_count:,} records")
        print(f"  After: {after_count:,} records")
        print(f"  Removed: {before_count - after_count:,} records")
        
        # Check for remaining duplicates
        cursor.execute("""
            SELECT COUNT(*)
            FROM (
                SELECT 
                    salesman_name,
                    description,
                    net_value,
                    month_number,
                    year,
                    COUNT(*) as dup_count
                FROM sales_data
                GROUP BY salesman_name, description, net_value, month_number, year
                HAVING COUNT(*) > 1
            )
        """)
        
        remaining_dups = cursor.fetchone()[0]
        
        if remaining_dups == 0:
            print(f"\n  ✅ All duplicates removed!")
        else:
            print(f"\n  ⚠️ {remaining_dups} duplicate groups still remain")
        
        print("\n" + "=" * 80)
        print("✅ CLEANUP COMPLETED")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    cleanup_duplicates_v2()
