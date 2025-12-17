"""
Clean and Re-import Data Script
1. Backup current data count
2. Delete old data
3. Re-import with new columns
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from database import SessionLocal
from sqlalchemy import text
from import_services import import_sales_data, import_production_data

def clean_and_reimport():
    db = SessionLocal()
    
    try:
        print("=" * 80)
        print("STEP 1: BACKUP - Count current data")
        print("=" * 80)
        
        # Count sales data
        result = db.execute(text("SELECT COUNT(*) FROM sales_data")).fetchone()
        sales_count = result[0]
        print(f"Current sales_data rows: {sales_count:,}")
        
        # Count production orders
        result = db.execute(text("SELECT COUNT(*) FROM production_orders")).fetchone()
        prod_count = result[0]
        print(f"Current production_orders rows: {prod_count:,}")
        
        # Ask for confirmation
        print("\n" + "=" * 80)
        print("WARNING: About to delete all data!")
        print("=" * 80)
        print(f"This will delete {sales_count:,} sales records")
        print(f"This will delete {prod_count:,} production order records")
        
        confirm = input("\nType 'YES' to confirm deletion: ")
        
        if confirm != 'YES':
            print("Cancelled by user")
            return
        
        print("\n" + "=" * 80)
        print("STEP 2: DELETE old data")
        print("=" * 80)
        
        # Delete sales data
        print("Deleting sales_data...")
        db.execute(text("DELETE FROM sales_data"))
        db.commit()
        print(f"  [OK] Deleted {sales_count:,} sales records")
        
        # Delete production orders
        print("Deleting production_orders...")
        db.execute(text("DELETE FROM production_orders"))
        db.commit()
        print(f"  [OK] Deleted {prod_count:,} production order records")
        
        print("\n" + "=" * 80)
        print("STEP 3: RE-IMPORT sales data")
        print("=" * 80)
        
        # Import sales data
        with open('demodata/zrsd0021612.xlsx', 'rb') as f:
            file_contents = f.read()
        
        result = import_sales_data(file_contents, db)
        
        print(f"\nStatus: {result.get('status')}")
        print(f"Message: {result.get('message')}")
        print(f"Rows imported: {result.get('rows_imported', 0):,}")
        
        if result.get('status') != 'success':
            print("ERROR: Sales import failed!")
            return
        
        print("\n" + "=" * 80)
        print("STEP 4: RE-IMPORT production orders")
        print("=" * 80)
        
        # Import production data
        with open('demodata/cooispi.XLSX', 'rb') as f:
            file_contents = f.read()
        
        result = import_production_data(file_contents, db)
        
        print(f"\nStatus: {result.get('status')}")
        print(f"Message: {result.get('message')}")
        print(f"Rows imported: {result.get('imported_new', 0):,}")
        
        if result.get('status') != 'success':
            print("ERROR: Production import failed!")
            return
        
        print("\n" + "=" * 80)
        print("STEP 5: VERIFY new columns are populated")
        print("=" * 80)
        
        # Check sales data SO columns
        result = db.execute(text("""
            SELECT 
                COUNT(*) as total,
                COUNT(so_no) as so_no_count,
                COUNT(so_date) as so_date_count
            FROM sales_data
        """)).fetchone()
        
        print(f"\nSales Data:")
        print(f"  Total rows: {result[0]:,}")
        print(f"  Rows with so_no: {result[1]:,} ({result[1]/result[0]*100:.1f}%)")
        print(f"  Rows with so_date: {result[2]:,} ({result[2]/result[0]*100:.1f}%)")
        
        # Check production orders new columns
        result = db.execute(text("""
            SELECT 
                COUNT(*) as total,
                COUNT(basic_start_date) as basic_start,
                COUNT(system_status) as sys_status
            FROM production_orders
        """)).fetchone()
        
        print(f"\nProduction Orders:")
        print(f"  Total rows: {result[0]:,}")
        print(f"  Rows with basic_start_date: {result[1]:,} ({result[1]/result[0]*100:.1f}%)")
        print(f"  Rows with system_status: {result[2]:,} ({result[2]/result[0]*100:.1f}%)")
        
        # Show sample data
        print("\n" + "=" * 80)
        print("SAMPLE: Sales data with SO columns")
        print("=" * 80)
        
        rows = db.execute(text("""
            SELECT billing_document, so_no, so_date, billing_date
            FROM sales_data
            WHERE so_no IS NOT NULL
            LIMIT 3
        """)).fetchall()
        
        for i, row in enumerate(rows, 1):
            print(f"\nRow {i}:")
            print(f"  Billing Doc: {row[0]}")
            print(f"  SO No: {row[1]}")
            print(f"  SO Date: {row[2]}")
            print(f"  Billing Date: {row[3]}")
        
        print("\n" + "=" * 80)
        print("SUCCESS! Data cleaned and re-imported")
        print("=" * 80)
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    clean_and_reimport()
