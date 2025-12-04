"""
Migration Script: Create monthly_targets table and migrate semester data
"""
import sqlite3
import os

def migrate_targets():
    """
    Create monthly_targets table and migrate data from sales_target
    """
    db_path = os.path.join(os.path.dirname(__file__), 'command_center_v2.db')
    
    print("=" * 80)
    print("MIGRATION: Semester Targets → Monthly Targets")
    print("=" * 80)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # STEP 1: Create monthly_targets table
        print("\n[STEP 1] Creating monthly_targets table...")
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS monthly_targets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_name TEXT NOT NULL,
                year INTEGER NOT NULL,
                month_number INTEGER NOT NULL,
                target_amount REAL NOT NULL,
                semester INTEGER NOT NULL,
                UNIQUE(user_name, year, month_number)
            )
        """)
        
        print("  ✅ Table created")
        
        # STEP 2: Check existing data
        print("\n[STEP 2] Checking existing data...")
        
        cursor.execute("SELECT COUNT(*) FROM sales_target")
        semester_count = cursor.fetchone()[0]
        print(f"  Semester targets: {semester_count} records")
        
        cursor.execute("SELECT COUNT(*) FROM monthly_targets")
        monthly_count = cursor.fetchone()[0]
        print(f"  Monthly targets: {monthly_count} records")
        
        if monthly_count > 0:
            print("\n  ⚠️ Monthly targets already exist. Clear first? (y/n)")
            # Auto-clear for migration
            cursor.execute("DELETE FROM monthly_targets")
            print("  ✅ Cleared existing monthly targets")
        
        # STEP 3: Migrate data
        print("\n[STEP 3] Migrating semester → monthly...")
        
        # Read all semester targets
        cursor.execute("""
            SELECT salesman_name, year, semester, target_amount
            FROM sales_target
            ORDER BY salesman_name, year, semester
        """)
        
        semester_targets = cursor.fetchall()
        
        print(f"  Processing {len(semester_targets)} semester records...")
        
        monthly_records = []
        for salesman, year, semester, target_amount in semester_targets:
            # Calculate monthly target
            monthly_target = target_amount / 6.0
            
            # Determine month range
            if semester == 1:
                months = [1, 2, 3, 4, 5, 6]
            else:  # semester == 2
                months = [7, 8, 9, 10, 11, 12]
            
            # Create 6 monthly records
            for month in months:
                monthly_records.append((
                    salesman,
                    year,
                    month,
                    monthly_target,
                    semester
                ))
        
        # Bulk insert
        cursor.executemany("""
            INSERT INTO monthly_targets (user_name, year, month_number, target_amount, semester)
            VALUES (?, ?, ?, ?, ?)
        """, monthly_records)
        
        conn.commit()
        
        print(f"  ✅ Inserted {len(monthly_records)} monthly records")
        
        # STEP 4: Verification
        print("\n[STEP 4] Verification...")
        
        # Sample check
        cursor.execute("""
            SELECT user_name, year, month_number, target_amount, semester
            FROM monthly_targets
            LIMIT 12
        """)
        
        samples = cursor.fetchall()
        print(f"\n  Sample monthly targets:")
        for s in samples:
            print(f"    {s[0][:20]:20} | {s[1]} | Month {s[2]:2} | Semester {s[4]} | Target: {s[3]:,.2f}")
        
        # Count by year
        cursor.execute("""
            SELECT year, COUNT(*) as count
            FROM monthly_targets
            GROUP BY year
            ORDER BY year
        """)
        
        year_counts = cursor.fetchall()
        print(f"\n  Monthly targets by year:")
        for year, count in year_counts:
            print(f"    {year}: {count} records")
        
        # Sanity check: Compare totals
        print(f"\n  Sanity Check:")
        cursor.execute("""
            SELECT 
                st.salesman_name,
                st.year,
                st.semester,
                st.target_amount as semester_target,
                SUM(mt.target_amount) as monthly_sum
            FROM sales_target st
            LEFT JOIN monthly_targets mt ON st.salesman_name = mt.user_name
                                         AND st.year = mt.year
                                         AND st.semester = mt.semester
            GROUP BY st.salesman_name, st.year, st.semester
            LIMIT 3
        """)
        
        checks = cursor.fetchall()
        for check in checks:
            name, year, sem, sem_target, monthly_sum = check
            match = abs(sem_target - monthly_sum) < 0.01
            status = "✅" if match else "❌"
            print(f"    {status} {name[:15]:15} | {year} S{sem} | Semester: {sem_target:,.0f} | Monthly Sum: {monthly_sum:,.0f}")
        
        print("\n" + "=" * 80)
        print("✅ MIGRATION COMPLETED SUCCESSFULLY")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_targets()
