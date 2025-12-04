"""
Test COGS validation with real data after fix
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from database import SessionLocal
from import_services import import_sales_data

def test_after_cogs_fix():
    demo_file = os.path.join(os.path.dirname(__file__), '..', 'demodata', 'zrsd002template.xlsx')
    
    print("=" * 80)
    print("TEST: Sales Import After COGS Upload")
    print("=" * 80)
    
    with open(demo_file, 'rb') as f:
        file_contents = f.read()
    
    db = SessionLocal()
    try:
        # Check COGS count first
        from models import ProductCost
        cogs_count = db.query(ProductCost).count()
        print(f"\n[COGS Check] Total COGS in database: {cogs_count}")
        
        # Sample COGS
        sample = db.query(ProductCost).limit(3).all()
        print("\n[Sample COGS]")
        for item in sample:
            print(f"  - {item.description}: {item.cogs}")
        
        # Test import
        print("\n[Import Test] Starting...")
        result = import_sales_data(file_contents, db)
        
        print("\n[RESULT]")
        print(f"  Status: {result['status']}")
        print(f"  Message: {result.get('message', 'N/A')}")
        
        if 'rows_imported' in result:
            print(f"  ✅ Rows Imported: {result['rows_imported']}")
        
        if 'missing_count' in result:
            print(f"  ⚠️ Missing Count: {result['missing_count']}")
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_after_cogs_fix()
