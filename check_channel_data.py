"""
Check actual channel data from LIVE database
Uses the same database connection as the backend
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from database import SessionLocal
from sqlalchemy import text

print("=" * 60)
print("LIVE DATABASE CHANNEL INSPECTION")
print("=" * 60)

db = SessionLocal()
try:
    # Check total rows
    result = db.execute(text("SELECT COUNT(*) FROM sales_data"))
    total_rows = result.fetchone()[0]
    print(f"\nTotal rows in sales_data: {total_rows:,}")
    
    # Check distinct dist values
    print("\n--- DISTINCT DIST VALUES ---")
    result = db.execute(text("SELECT DISTINCT dist, COUNT(*) as count FROM sales_data GROUP BY dist ORDER BY count DESC"))
    
    dist_values = []
    for row in result:
        val = row[0]
        count = row[1]
        dist_values.append((val, count))
        print(f"Value: {repr(val):20} | Type: {type(val).__name__:10} | Count: {count:,}")
    
    # Test mapping
    print("\n--- MAPPING TEST ---")
    CHANNEL_MAP = {
        '11': 'Industry',
        '13': 'Retail',
        '15': 'Project'
    }
    
    print(f"Map keys: {list(CHANNEL_MAP.keys())}")
    print(f"Map key types: {[type(k).__name__ for k in CHANNEL_MAP.keys()]}")
    
    print("\n--- MAPPING RESULTS ---")
    for val, count in dist_values[:10]:
        # Test direct mapping
        direct_map = CHANNEL_MAP.get(val, 'Others')
        
        # Test string conversion
        str_val = str(val)
        str_map = CHANNEL_MAP.get(str_val, 'Others')
        
        # Test stripped
        stripped_val = str_val.strip()
        stripped_map = CHANNEL_MAP.get(stripped_val, 'Others')
        
        # Test without .0
        clean_val = str_val.strip().replace('.0', '')
        clean_map = CHANNEL_MAP.get(clean_val, 'Others')
        
        print(f"\nRaw: {repr(val):15}")
        print(f"  Direct:   {direct_map:10} (type: {type(val).__name__})")
        print(f"  As str:   {str_map:10} ('{str_val}')")
        print(f"  Stripped: {stripped_map:10} ('{stripped_val}')")
        print(f"  Clean:    {clean_map:10} ('{clean_val}')")
        print(f"  Count:    {count:,}")
    
    # Sample data
    print("\n--- SAMPLE RECORDS ---")
    result = db.execute(text("SELECT dist, net_value, year, month_number FROM sales_data LIMIT 5"))
    for row in result:
        print(f"dist={repr(row[0]):15} revenue={row[1]:15,.0f} year={row[2]} month={row[3]}")
        
finally:
    db.close()

print("\n" + "=" * 60)
print("INSPECTION COMPLETE")
print("=" * 60)
