from database import SessionLocal
from sqlalchemy import text

db = SessionLocal()

try:
    # Check if view exists and works
    result = db.execute(text('SELECT * FROM view_sales_performance_v2 LIMIT 5'))
    rows = result.fetchall()
    
    if rows:
        print(f"View has {len(rows)} rows (showing first 5)")
        # Show column names
        print("\nColumns:", result.keys())
        for row in rows:
            print(row)
    else:
        print("View exists but has no data")
        
except Exception as e:
    print(f"Error querying view: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
