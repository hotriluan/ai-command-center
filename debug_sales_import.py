"""
Simple test to debug sales import issue
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from database import SessionLocal
from import_services import import_sales_data

# Read the Excel file
file_path = 'demodata/zrsd0021612.xlsx'

with open(file_path, 'rb') as f:
    file_contents = f.read()

db = SessionLocal()

try:
    result = import_sales_data(file_contents, db)
    print("\n" + "=" * 80)
    print("RESULT:")
    print("=" * 80)
    print(result)
except Exception as e:
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
