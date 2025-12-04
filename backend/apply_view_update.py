"""
Apply view update after migration
"""
import sqlite3
import os

def apply_view_update():
    """Apply updated view definition"""
    db_path = os.path.join(os.path.dirname(__file__), 'command_center_v2.db')
    
    print("=" * 80)
    print("APPLYING VIEW UPDATE")
    print("=" * 80)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("\n[Step 1] Reading SQL file...")
        with open('update_view_sales_performance_v2.sql', 'r') as f:
            sql_script = f.read()
        
        print("[Step 2] Executing SQL...")
        for statement in sql_script.split(';'):
            if statement.strip():
                cursor.execute(statement)
                print(f"  ✅ {statement.strip()[:60]}...")
        
        conn.commit()
        
        print("\n[Step 3] Verification...")
        cursor.execute("SELECT COUNT(*) FROM view_sales_performance_v2")
        count = cursor.fetchone()[0]
        print(f"  ✅ View has {count} rows")
        
        # Sample query
        cursor.execute("""
            SELECT salesman_name, year, month_number, total_revenue, total_target, achievement_percentage
            FROM view_sales_performance_v2
            WHERE year = 2025 AND month_number = 1
            LIMIT 3
        """)
        
        samples = cursor.fetchall()
        print(f"\n  Sample data (Year 2025, Month 1):")
        for s in samples:
            print(f"    {s[0][:20]:20} | Revenue: {s[3]:>15,.0f} | Target: {s[4]:>15,.0f} | Achievement: {s[5]:>6.1f}%")
        
        print("\n" + "=" * 80)
        print("✅ VIEW UPDATE COMPLETED")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    apply_view_update()
