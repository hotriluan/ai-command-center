"""
Auto Clean and Re-import Data Script (No confirmation needed)
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from database import SessionLocal
from sqlalchemy import text
from import_services import import_sales_data, import_production_data

db = SessionLocal()

try:
    print("=" * 80)
    print("AUTO CLEAN AND RE-IMPORT")
    print("=" * 80)
    
    # Count current data
    sales_count = db.execute(text("SELECT COUNT(*) FROM sales_data")).fetchone()[0]
    prod_count = db.execute(text("SELECT COUNT(*) FROM production_orders")).fetchone()[0]
    
    print(f"\nCurrent data:")
    print(f"  Sales: {sales_count:,} rows")
    print(f"  Production: {prod_count:,} rows")
    
    # Delete
    print("\n[1/4] Deleting old data...")
    db.execute(text("DELETE FROM sales_data"))
    db.execute(text("DELETE FROM production_orders"))
    db.commit()
    print("  [OK] Deleted all old data")
    
    # Import sales
    print("\n[2/4] Importing sales data...")
    with open('demodata/zrsd0021612.xlsx', 'rb') as f:
        result = import_sales_data(f.read(), db)
    
    print(f"  Status: {result.get('status')}")
    print(f"  Rows: {result.get('rows_imported', 0):,}")
    
    # Import production
    print("\n[3/4] Importing production orders...")
    with open('demodata/cooispi.XLSX', 'rb') as f:
        result = import_production_data(f.read(), db)
    
    print(f"  Status: {result.get('status')}")
    print(f"  Rows: {result.get('imported_new', 0):,}")
    
    # Verify
    print("\n[4/4] Verifying new columns...")
    
    sales_check = db.execute(text("""
        SELECT COUNT(*) as total, COUNT(so_no) as so_no_count
        FROM sales_data
    """)).fetchone()
    
    prod_check = db.execute(text("""
        SELECT COUNT(*) as total, COUNT(basic_start_date) as basic_start
        FROM production_orders
    """)).fetchone()
    
    print(f"\nSales Data:")
    print(f"  Total: {sales_check[0]:,}")
    print(f"  With SO No: {sales_check[1]:,} ({sales_check[1]/sales_check[0]*100:.1f}%)")
    
    print(f"\nProduction Orders:")
    print(f"  Total: {prod_check[0]:,}")
    print(f"  With Basic Start: {prod_check[1]:,} ({prod_check[1]/prod_check[0]*100:.1f}%)")
    
    # Sample
    print("\n" + "=" * 80)
    print("SAMPLE DATA")
    print("=" * 80)
    
    sample = db.execute(text("""
        SELECT billing_document, so_no, so_date, billing_date
        FROM sales_data
        WHERE so_no IS NOT NULL
        LIMIT 2
    """)).fetchall()
    
    for i, row in enumerate(sample, 1):
        print(f"\nSales Row {i}:")
        print(f"  Billing: {row[0]}, SO: {row[1]}, SO Date: {row[2]}, Billing Date: {row[3]}")
    
    print("\n" + "=" * 80)
    print("SUCCESS!")
    print("=" * 80)
    
except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()
