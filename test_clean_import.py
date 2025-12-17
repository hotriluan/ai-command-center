"""
PRODUCTION IMPORT - CLEAN DATABASE TEST
Demonstrates the full import behavior from a clean state
"""
import requests
import sqlite3
import os
from pathlib import Path

# Configuration
BACKEND_URL = "http://127.0.0.1:8000"
DATA_FOLDER = "demodata"
EXCEL_FILE = "cooispi.xlsx"
DB_PATH = "backend/database.db"  # Adjust if your DB path is different

def print_header(title):
    """Print formatted section header"""
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)

def get_production_order_count():
    """Query the database directly to count production orders"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM production_orders")
        count = cursor.fetchone()[0]
        conn.close()
        return count
    except Exception as e:
        print(f"⚠️  Could not query database: {e}")
        return None

def test_clean_import():
    """
    Test import behavior starting from clean state:
    1. Clear production_orders table
    2. First upload: Should import all records
    3. Second upload: Should skip all records
    """
    
    print_header("PRODUCTION IMPORT - CLEAN DATABASE TEST")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test File: {DATA_FOLDER}/{EXCEL_FILE}")
    print(f"Database: {DB_PATH}")
    
    # Step 0: Check initial state
    print_header("STEP 0: CHECK INITIAL STATE")
    
    initial_count = get_production_order_count()
    if initial_count is not None:
        print(f"📊 Current production orders in database: {initial_count}")
    
    # Step 1: Clear production_orders table
    print_header("STEP 1: CLEAR PRODUCTION ORDERS TABLE")
    
    user_input = input("⚠️  This will DELETE all records from production_orders table. Proceed? (yes/no): ")
    
    if user_input.lower() != 'yes':
        print("❌ Test cancelled by user")
        return False
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM production_orders")
        conn.commit()
        deleted_count = cursor.rowcount
        conn.close()
        print(f"✅ Deleted {deleted_count} records from production_orders table")
    except Exception as e:
        print(f"❌ ERROR: Could not clear table: {e}")
        return False
    
    # Verify table is empty
    empty_count = get_production_order_count()
    if empty_count == 0:
        print(f"✅ Table is now empty (0 records)")
    else:
        print(f"⚠️  Table still has {empty_count} records")
    
    # Step 2: First Upload
    print_header("STEP 2: FIRST UPLOAD (Clean State)")
    
    file_path = Path(DATA_FOLDER) / EXCEL_FILE
    
    if not file_path.exists():
        print(f"❌ ERROR: File not found at {file_path}")
        return False
    
    with open(file_path, 'rb') as f:
        files = {'file': (EXCEL_FILE, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
        
        print(f"[STEP] Uploading {EXCEL_FILE}...")
        response1 = requests.post(
            f"{BACKEND_URL}/api/import/production",
            files=files
        )
    
    print(f"Status Code: {response1.status_code}")
    
    if response1.status_code != 200:
        print(f"❌ ERROR: Upload failed")
        print(f"Response: {response1.text}")
        return False
    
    result1 = response1.json()
    print(f"\n📊 First Upload Results:")
    print(f"  - Total rows in file: {result1.get('total_rows_in_file', 'N/A')}")
    print(f"  - Imported new: {result1.get('imported_new', 'N/A')}")
    print(f"  - Skipped existing: {result1.get('skipped_existing', 'N/A')}")
    
    # Verify database count
    count_after_first = get_production_order_count()
    if count_after_first is not None:
        print(f"  - Database count: {count_after_first}")
    
    # Validation
    expected_imported = result1.get('total_rows_in_file', 0)
    actual_imported = result1.get('imported_new', 0)
    
    if actual_imported == expected_imported:
        print(f"\n✅ PASS: First upload imported all {actual_imported} records")
    else:
        print(f"\n❌ FAIL: Expected {expected_imported}, got {actual_imported}")
        return False
    
    # Step 3: Second Upload (Should skip all)
    print_header("STEP 3: SECOND UPLOAD (Same File)")
    
    with open(file_path, 'rb') as f:
        files = {'file': (EXCEL_FILE, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
        
        print(f"[STEP] Uploading {EXCEL_FILE} again...")
        response2 = requests.post(
            f"{BACKEND_URL}/api/import/production",
            files=files
        )
    
    print(f"Status Code: {response2.status_code}")
    
    if response2.status_code != 200:
        print(f"❌ ERROR: Upload failed")
        return False
    
    result2 = response2.json()
    print(f"\n📊 Second Upload Results:")
    print(f"  - Total rows in file: {result2.get('total_rows_in_file', 'N/A')}")
    print(f"  - Imported new: {result2.get('imported_new', 'N/A')}")
    print(f"  - Skipped existing: {result2.get('skipped_existing', 'N/A')}")
    
    # Verify database count unchanged
    count_after_second = get_production_order_count()
    if count_after_second is not None:
        print(f"  - Database count: {count_after_second}")
    
    # Validation
    if result2.get('imported_new', 0) == 0 and result2.get('skipped_existing', 0) == result2.get('total_rows_in_file', 0):
        print(f"\n✅ PASS: Second upload skipped all records (no duplicates created)")
    else:
        print(f"\n❌ FAIL: Second upload should skip all records")
        return False
    
    # Verify counts match
    if count_after_first == count_after_second:
        print(f"✅ PASS: Database count unchanged ({count_after_first} = {count_after_second})")
    else:
        print(f"❌ FAIL: Database count changed ({count_after_first} → {count_after_second})")
        return False
    
    # Final Summary
    print_header("TEST SUMMARY")
    print("🎉 ALL TESTS PASSED!")
    print("\nVerified behaviors:")
    print(f"  ✅ Clean import: Imported {actual_imported} new records")
    print(f"  ✅ Duplicate upload: Skipped all {result2.get('skipped_existing', 0)} existing records")
    print(f"  ✅ Database integrity: No duplicate records created")
    print("\n💡 Import logic is working correctly:")
    print("   - INSERT ONLY: New records are added")
    print("   - SKIP EXISTING: Existing records are preserved (no updates)")
    
    return True

if __name__ == "__main__":
    try:
        success = test_clean_import()
        if not success:
            print("\n❌ TEST FAILED")
            exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
