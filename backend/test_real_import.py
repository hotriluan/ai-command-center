"""
Test import with real data from demodata folder
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from database import SessionLocal
from import_services import import_sales_data, import_cogs_data
import pandas as pd

def inspect_excel_file(file_path):
    """Inspect Excel file structure"""
    print("=" * 80)
    print(f"INSPECTING: {file_path}")
    print("=" * 80)
    
    df = pd.read_excel(file_path, engine='openpyxl')
    
    print(f"\nTotal Rows: {len(df)}")
    print(f"Total Columns: {len(df.columns)}")
    
    print("\nColumn Names:")
    for i, col in enumerate(df.columns, 1):
        print(f"  {i}. {col}")
    
    print("\nFirst 3 rows:")
    print(df.head(3).to_string())
    
    print("\n" + "=" * 80)
    return df

def test_sales_import():
    """Test sales data import with real file"""
    print("\n" + "=" * 80)
    print("TESTING SALES DATA IMPORT")
    print("=" * 80)
    
    # Path to demo file
    demo_file = os.path.join(os.path.dirname(__file__), '..', 'demodata', 'zrsd002template.xlsx')
    
    if not os.path.exists(demo_file):
        print(f"❌ File not found: {demo_file}")
        return
    
    # Inspect file first
    df = inspect_excel_file(demo_file)
    
    # Read file for import
    with open(demo_file, 'rb') as f:
        file_contents = f.read()
    
    # Test import
    db = SessionLocal()
    try:
        print("\n[Import] Starting import...")
        result = import_sales_data(file_contents, db)
        
        print("\n[Result]")
        print(f"  Status: {result['status']}")
        print(f"  Message: {result.get('message', 'N/A')}")
        
        if 'rows_imported' in result:
            print(f"  Rows Imported: {result['rows_imported']}")
        
        if 'report_path' in result:
            print(f"  Report Path: {result['report_path']}")
            print(f"  Missing Count: {result.get('missing_count', 0)}")
        
        if result['status'] == 'success':
            print("\n✅ IMPORT SUCCESSFUL")
        elif result['status'] == 'error':
            print("\n⚠️ IMPORT BLOCKED (Missing COGS)")
        else:
            print(f"\nℹ️ {result['message']}")
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    test_sales_import()
