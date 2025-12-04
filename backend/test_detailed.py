"""
Detailed test with better error handling
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from database import SessionLocal
from import_services import import_sales_data
import traceback

def test_import_detailed():
    demo_file = os.path.join(os.path.dirname(__file__), '..', 'demodata', 'zrsd002template.xlsx')
    
    print("=" * 80)
    print("DETAILED IMPORT TEST")
    print("=" * 80)
    print(f"File: {demo_file}")
    print(f"Exists: {os.path.exists(demo_file)}")
    
    if not os.path.exists(demo_file):
        print("❌ File not found!")
        return
    
    with open(demo_file, 'rb') as f:
        file_contents = f.read()
    
    print(f"File size: {len(file_contents)} bytes")
    
    db = SessionLocal()
    try:
        print("\n[Starting Import...]")
        result = import_sales_data(file_contents, db)
        
        print("\n[RESULT]")
        for key, value in result.items():
            print(f"  {key}: {value}")
        
        # Check if report was created
        report_path = result.get('report_path')
        if report_path:
            print(f"\n[Report Check]")
            print(f"  Path: {report_path}")
            print(f"  Exists: {os.path.exists(report_path)}")
            
            if os.path.exists(report_path):
                import pandas as pd
                df = pd.read_excel(report_path)
                print(f"  Rows: {len(df)}")
                print(f"\n  First 5 products:")
                print(df.head().to_string())
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_import_detailed()
