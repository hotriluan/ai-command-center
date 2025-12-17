"""
Check if SO columns are populated
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from database import SessionLocal
from sqlalchemy import text

db = SessionLocal()

try:
    # Check SO columns
    query = text("""
        SELECT 
            COUNT(*) as total_rows,
            COUNT(so_no) as so_no_count,
            COUNT(so_date) as so_date_count
        FROM sales_data
    """)
    
    result = db.execute(query).fetchone()
    
    print("=" * 80)
    print("SALES_DATA SO COLUMNS CHECK")
    print("=" * 80)
    print(f"Total rows: {result[0]:,}")
    print(f"Rows with so_no: {result[1]:,} ({result[1]/result[0]*100:.1f}%)")
    print(f"Rows with so_date: {result[2]:,} ({result[2]/result[0]*100:.1f}%)")
    
    # Show sample
    print("\n" + "=" * 80)
    print("SAMPLE DATA (First 5 rows)")
    print("=" * 80)
    
    query = text("""
        SELECT 
            billing_document,
            so_no,
            so_date,
            billing_date,
            description
        FROM sales_data
        LIMIT 5
    """)
    
    rows = db.execute(query).fetchall()
    
    for i, row in enumerate(rows, 1):
        print(f"\nRow {i}:")
        print(f"  Billing Doc: {row[0]}")
        print(f"  SO No: {row[1]}")
        print(f"  SO Date: {row[2]}")
        print(f"  Billing Date: {row[3]}")
        print(f"  Product: {row[4][:50] if row[4] else None}...")
    
    # Check production orders
    print("\n" + "=" * 80)
    print("PRODUCTION_ORDERS NEW COLUMNS CHECK")
    print("=" * 80)
    
    query = text("""
        SELECT 
            COUNT(*) as total_rows,
            COUNT(basic_start_date) as basic_start_count,
            COUNT(system_status) as system_status_count,
            COUNT(bom_alternative) as bom_alt_count
        FROM production_orders
    """)
    
    result = db.execute(query).fetchone()
    
    print(f"Total rows: {result[0]:,}")
    print(f"Rows with basic_start_date: {result[1]:,} ({result[1]/result[0]*100:.1f}%)")
    print(f"Rows with system_status: {result[2]:,} ({result[2]/result[0]*100:.1f}%)")
    print(f"Rows with bom_alternative: {result[3]:,} ({result[3]/result[0]*100:.1f}%)")
    
finally:
    db.close()
