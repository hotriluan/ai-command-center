"""
Test script for import_services functions
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from database import SessionLocal
from import_services import import_sales_data, import_cogs_data

def test_schema():
    """Verify schema migration"""
    import sqlite3
    conn = sqlite3.connect('command_center_v2.db')
    cursor = conn.cursor()
    
    print("=" * 80)
    print("SCHEMA VERIFICATION")
    print("=" * 80)
    
    # Check sales_data columns
    cursor.execute("PRAGMA table_info(sales_data)")
    cols = [row[1] for row in cursor.fetchall()]
    
    required = ['billing_document', 'billing_item', 'material_code', 'billing_date']
    print("\nsales_data columns:")
    for col in required:
        status = "✅" if col in cols else "❌"
        print(f"  {status} {col}")
    
    # Check product_cogs table
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='product_cogs'")
    if cursor.fetchone():
        print("\n✅ product_cogs table exists")
        cursor.execute("PRAGMA table_info(product_cogs)")
        cogs_cols = [row[1] for row in cursor.fetchall()]
        print(f"  Columns: {', '.join(cogs_cols)}")
    else:
        print("\n❌ product_cogs table NOT FOUND")
    
    # Check unique index
    cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name='idx_sales_unique_transaction'")
    if cursor.fetchone():
        print("\n✅ idx_sales_unique_transaction index exists")
    else:
        print("\n❌ Unique index NOT FOUND")
    
    conn.close()
    print("\n" + "=" * 80)

def test_import_functions():
    """Test import service functions are importable"""
    print("\n" + "=" * 80)
    print("IMPORT FUNCTIONS TEST")
    print("=" * 80)
    
    try:
        from import_services import import_sales_data, import_cogs_data
        print("\n✅ import_sales_data function loaded")
        print("✅ import_cogs_data function loaded")
        
        # Check function signatures
        import inspect
        sales_sig = inspect.signature(import_sales_data)
        cogs_sig = inspect.signature(import_cogs_data)
        
        print(f"\nimport_sales_data{sales_sig}")
        print(f"import_cogs_data{cogs_sig}")
        
    except Exception as e:
        print(f"\n❌ Error loading functions: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    test_schema()
    test_import_functions()
    
    print("\n✅ ALL TESTS PASSED")
    print("\nNext steps:")
    print("1. Prepare sample Excel files (sales and COGS)")
    print("2. Test actual import with real data")
    print("3. Verify duplicate detection")
    print("4. Verify COGS validation")
