"""
Apply database optimizations: indexes and view update
"""
import sqlite3
import os

def apply_optimizations():
    """Apply database optimizations"""
    db_path = os.path.join(os.path.dirname(__file__), 'command_center_v2.db')
    
    print("=" * 80)
    print("DATABASE OPTIMIZATION")
    print("=" * 80)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Step 1: Create Indexes
        print("\n[Step 1] Creating indexes...")
        
        with open('optimize_database.sql', 'r') as f:
            sql_script = f.read()
        
        # Execute each statement
        for statement in sql_script.split(';'):
            if statement.strip():
                cursor.execute(statement)
                print(f"  ✅ Executed: {statement.strip()[:50]}...")
        
        conn.commit()
        print("\n✅ All indexes created successfully")
        
        # Step 2: Update View
        print("\n[Step 2] Updating view_sales_performance_v2...")
        
        with open('update_view_sales_performance_v2.sql', 'r') as f:
            view_script = f.read()
        
        # Execute view creation
        for statement in view_script.split(';'):
            if statement.strip():
                cursor.execute(statement)
                print(f"  ✅ Executed: {statement.strip()[:50]}...")
        
        conn.commit()
        print("\n✅ View created successfully")
        
        # Step 3: Verify
        print("\n[Step 3] Verification...")
        
        # Check indexes
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%'")
        indexes = cursor.fetchall()
        print(f"\n  Total indexes: {len(indexes)}")
        for idx in indexes:
            print(f"    - {idx[0]}")
        
        # Check view
        cursor.execute("SELECT name FROM sqlite_master WHERE type='view' AND name='view_sales_performance_v2'")
        if cursor.fetchone():
            print(f"\n  ✅ view_sales_performance_v2 exists")
            
            # Test query
            cursor.execute("SELECT COUNT(*) FROM view_sales_performance_v2")
            count = cursor.fetchone()[0]
            print(f"  ✅ View has {count} rows")
        else:
            print(f"\n  ❌ View not found")
        
        print("\n" + "=" * 80)
        print("✅ OPTIMIZATION COMPLETED SUCCESSFULLY")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    apply_optimizations()
