"""
Migration Script: Apply view_sales_performance to database
This script reads the SQL file and executes it against the SQLite database.
"""
import sqlite3
import os

# Get the database path (using the ACTUAL database file the app uses)
DB_PATH = os.path.join(os.path.dirname(__file__), 'command_center_v2.db')
SQL_FILE = os.path.join(os.path.dirname(__file__), 'create_view_sales_performance.sql')

def apply_migration():
    """Apply the view creation migration"""
    try:
        # Read SQL file
        with open(SQL_FILE, 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        # Connect to database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Execute SQL script
        cursor.executescript(sql_script)
        conn.commit()
        
        # Verify view was created
        cursor.execute("SELECT name FROM sqlite_master WHERE type='view' AND name='view_sales_performance'")
        result = cursor.fetchone()
        
        if result:
            print("✅ SUCCESS: view_sales_performance created successfully!")
            
            # Test the view
            cursor.execute("SELECT COUNT(*) FROM view_sales_performance")
            count = cursor.fetchone()[0]
            print(f"✅ View contains {count} rows")
            
            # Show sample data
            cursor.execute("SELECT * FROM view_sales_performance LIMIT 3")
            rows = cursor.fetchall()
            print("\n📊 Sample data:")
            for row in rows:
                print(f"  {row}")
        else:
            print("❌ ERROR: View was not created")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    apply_migration()
