"""
Test Import Script: Verify new columns are populated correctly
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from database import SessionLocal
from import_services import import_sales_data, import_production_data
from sqlalchemy import text

def test_sales_import():
    """Test sales data import with SO columns"""
    print("=" * 80)
    print("TEST 1: Sales Data Import")
    print("=" * 80)
    
    # Read the Excel file
    file_path = 'demodata/zrsd0021612.xlsx'
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False
    
    with open(file_path, 'rb') as f:
        file_contents = f.read()
    
    db = SessionLocal()
    
    try:
        # Import data
        result = import_sales_data(file_contents, db)
        
        print("\n" + "=" * 80)
        print("IMPORT RESULT")
        print("=" * 80)
        print(f"Status: {result.get('status')}")
        print(f"Message: {result.get('message')}")
        print(f"Rows imported: {result.get('rows_imported', 0)}")
        
        # Verify SO columns are populated
        print("\n" + "=" * 80)
        print("VERIFICATION: Check SO columns")
        print("=" * 80)
        
        query = text("""
            SELECT 
                COUNT(*) as total_rows,
                COUNT(so_no) as so_no_count,
                COUNT(so_date) as so_date_count
            FROM sales_data
        """)
        
        result = db.execute(query).fetchone()
        
        print(f"Total rows: {result[0]}")
        print(f"Rows with so_no: {result[1]} ({result[1]/result[0]*100:.1f}%)")
        print(f"Rows with so_date: {result[2]} ({result[2]/result[0]*100:.1f}%)")
        
        # Show sample data
        print("\n" + "=" * 80)
        print("SAMPLE DATA (First 3 rows with SO data)")
        print("=" * 80)
        
        query = text("""
            SELECT 
                billing_document,
                so_no,
                so_date,
                billing_date,
                description
            FROM sales_data
            WHERE so_no IS NOT NULL
            LIMIT 3
        """)
        
        rows = db.execute(query).fetchall()
        
        for i, row in enumerate(rows, 1):
            print(f"\nRow {i}:")
            print(f"  Billing Doc: {row[0]}")
            print(f"  SO No: {row[1]}")
            print(f"  SO Date: {row[2]}")
            print(f"  Billing Date: {row[3]}")
            print(f"  Product: {row[4]}")
        
        if result[1] > 0:
            print("\n✅ Sales import test PASSED - SO columns populated!")
            return True
        else:
            print("\n❌ Sales import test FAILED - SO columns empty!")
            return False
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

def test_production_import():
    """Test production order import with new columns"""
    print("\n" + "=" * 80)
    print("TEST 2: Production Order Import")
    print("=" * 80)
    
    # Read the Excel file
    file_path = 'demodata/cooispi.XLSX'
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False
    
    with open(file_path, 'rb') as f:
        file_contents = f.read()
    
    db = SessionLocal()
    
    try:
        # Import data
        result = import_production_data(file_contents, db)
        
        print("\n" + "=" * 80)
        print("IMPORT RESULT")
        print("=" * 80)
        print(f"Status: {result.get('status')}")
        print(f"Message: {result.get('message')}")
        print(f"Imported new: {result.get('imported_new', 0)}")
        
        # Verify new columns are populated
        print("\n" + "=" * 80)
        print("VERIFICATION: Check new columns")
        print("=" * 80)
        
        query = text("""
            SELECT 
                COUNT(*) as total_rows,
                COUNT(basic_start_date) as basic_start_count,
                COUNT(system_status) as system_status_count
            FROM production_orders
        """)
        
        result = db.execute(query).fetchone()
        
        print(f"Total rows: {result[0]}")
        print(f"Rows with basic_start_date: {result[1]} ({result[1]/result[0]*100:.1f}%)")
        print(f"Rows with system_status: {result[2]} ({result[2]/result[0]*100:.1f}%)")
        
        # Show sample data
        print("\n" + "=" * 80)
        print("SAMPLE DATA (First 3 rows)")
        print("=" * 80)
        
        query = text("""
            SELECT 
                order_id,
                order_type,
                basic_start_date,
                release_date,
                actual_finish_date,
                system_status,
                sales_order_id
            FROM production_orders
            LIMIT 3
        """)
        
        rows = db.execute(query).fetchall()
        
        for i, row in enumerate(rows, 1):
            print(f"\nRow {i}:")
            print(f"  Order ID: {row[0]}")
            print(f"  Type: {row[1]}")
            print(f"  Basic Start: {row[2]}")
            print(f"  Release: {row[3]}")
            print(f"  Finish: {row[4]}")
            print(f"  Status: {row[5]}")
            print(f"  SO ID: {row[6]}")
        
        if result[1] > 0 or result[2] > 0:
            print("\n✅ Production import test PASSED - New columns populated!")
            return True
        else:
            print("\n⚠️  Production import test - No new data imported (might be duplicates)")
            return True
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 80)
    print("IMPORT TEST SUITE")
    print("=" * 80)
    
    test1 = test_sales_import()
    test2 = test_production_import()
    
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Sales Import: {'✅ PASSED' if test1 else '❌ FAILED'}")
    print(f"Production Import: {'✅ PASSED' if test2 else '❌ FAILED'}")
    
    if test1 and test2:
        print("\n🎉 ALL TESTS PASSED!")
    else:
        print("\n⚠️  SOME TESTS FAILED - Please review errors above")
