"""
VERIFICATION SCRIPT - Check actual channel mapping
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from database import SessionLocal
from sqlalchemy import text

def map_channel_robust(val):
    """FORCE STRING CONVERSION & CLEANUP"""
    s = str(val).strip().replace('.0', '')  # Turns 11, 11.0, ' 11 ' into '11'
    mapping = {'11': 'Industry', '13': 'Retail', '15': 'Project'}
    return mapping.get(s, 'Others')

print("=" * 70)
print("CHANNEL MAPPING VERIFICATION")
print("=" * 70)

db = SessionLocal()
try:
    # Get total count
    result = db.execute(text("SELECT COUNT(*) FROM sales_data"))
    total = result.fetchone()[0]
    print(f"\nTotal rows in sales_data: {total:,}")
    
    if total == 0:
        print("\n❌ ERROR: No data in sales_data table!")
        print("Cannot verify channel mapping without data.")
    else:
        # Get distinct dist values
        print("\n--- DISTINCT DIST VALUES ---")
        result = db.execute(text("""
            SELECT dist, COUNT(*) as count 
            FROM sales_data 
            GROUP BY dist 
            ORDER BY count DESC 
            LIMIT 20
        """))
        
        rows = result.fetchall()
        print(f"Found {len(rows)} distinct dist values\n")
        
        for row in rows:
            raw_val = row[0]
            count = row[1]
            mapped = map_channel_robust(raw_val)
            
            print(f"Raw: {repr(raw_val):15} (type: {type(raw_val).__name__:8}) -> Mapped: {mapped:10} | Count: {count:,}")
        
        # Summary
        print("\n--- MAPPING SUMMARY ---")
        result = db.execute(text("SELECT dist FROM sales_data"))
        all_vals = [row[0] for row in result.fetchall()]
        
        mapped_counts = {}
        for val in all_vals:
            channel = map_channel_robust(val)
            mapped_counts[channel] = mapped_counts.get(channel, 0) + 1
        
        print("\nChannel Distribution:")
        for channel, count in sorted(mapped_counts.items(), key=lambda x: -x[1]):
            pct = (count / total * 100) if total > 0 else 0
            print(f"  {channel:15} {count:8,} rows ({pct:5.1f}%)")
        
        # Check if mapping is working
        if mapped_counts.get('Others', 0) == total:
            print("\n❌ WARNING: ALL data mapped to 'Others'!")
            print("   This means dist values don't match '11', '13', '15'")
        elif mapped_counts.get('Others', 0) > 0:
            print(f"\n⚠️  {mapped_counts['Others']:,} rows mapped to 'Others'")
        else:
            print("\n✅ All data successfully mapped to channels!")
            
finally:
    db.close()

print("\n" + "=" * 70)
print("VERIFICATION COMPLETE")
print("=" * 70)
