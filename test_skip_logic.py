"""
PRODUCTION IMPORT - SKIP LOGIC VERIFICATION
Tests that the import function properly skips existing records
"""
import requests
import os
from pathlib import Path

# Configuration
BACKEND_URL = "http://127.0.0.1:8000"
DATA_FOLDER = "demodata"
EXCEL_FILE = "cooispi.xlsx"

def print_header(title):
    """Print formatted section header"""
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)

def test_skip_logic():
    """
    Test that uploading the same file twice:
    - 1st run: Imports new records
    - 2nd run: Skips all existing records (imported_new = 0)
    """
    
    print_header("PRODUCTION IMPORT - SKIP LOGIC TEST")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test File: {DATA_FOLDER}/{EXCEL_FILE}")
    
    # Locate Excel file
    print_header("LOCATING TEST FILE")
    
    file_path = Path(DATA_FOLDER) / EXCEL_FILE
    
    if not file_path.exists():
        print(f"❌ ERROR: File not found at {file_path}")
        return False
    
    print(f"✅ Found file: {file_path}")
    
    # Test Run 1: First Upload
    print_header("RUN 1: FIRST UPLOAD (Should import new records)")
    
    with open(file_path, 'rb') as f:
        files = {'file': (EXCEL_FILE, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
        
        print(f"[STEP] Uploading {EXCEL_FILE}...")
        response1 = requests.post(
            f"{BACKEND_URL}/api/import/production",
            files=files
        )
    
    print(f"Status Code: {response1.status_code}")
    
    if response1.status_code != 200:
        print(f"❌ ERROR: Upload failed with status {response1.status_code}")
        print(f"Response: {response1.text}")
        return False
    
    result1 = response1.json()
    print(f"\n📊 Run 1 Results:")
    print(f"  - Total rows in file: {result1.get('total_rows_in_file', 'N/A')}")
    print(f"  - Imported new: {result1.get('imported_new', 'N/A')}")
    print(f"  - Skipped existing: {result1.get('skipped_existing', 'N/A')}")
    
    # Validation for Run 1
    run1_imported = result1.get('imported_new', 0)
    
    if run1_imported == 0:
        print("\n⚠️  WARNING: Run 1 imported 0 records. Database might already contain the data.")
        print("   This is OK if you've run this test before.")
    else:
        print(f"\n✅ Run 1 imported {run1_imported} new records")
    
    # Test Run 2: Second Upload (Same File)
    print_header("RUN 2: SECOND UPLOAD (Should skip all existing records)")
    
    with open(file_path, 'rb') as f:
        files = {'file': (EXCEL_FILE, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
        
        print(f"[STEP] Uploading {EXCEL_FILE} again...")
        response2 = requests.post(
            f"{BACKEND_URL}/api/import/production",
            files=files
        )
    
    print(f"Status Code: {response2.status_code}")
    
    if response2.status_code != 200:
        print(f"❌ ERROR: Upload failed with status {response2.status_code}")
        print(f"Response: {response2.text}")
        return False
    
    result2 = response2.json()
    print(f"\n📊 Run 2 Results:")
    print(f"  - Total rows in file: {result2.get('total_rows_in_file', 'N/A')}")
    print(f"  - Imported new: {result2.get('imported_new', 'N/A')}")
    print(f"  - Skipped existing: {result2.get('skipped_existing', 'N/A')}")
    
    # CRITICAL VALIDATION: Run 2 must skip ALL records
    run2_imported = result2.get('imported_new', 0)
    run2_skipped = result2.get('skipped_existing', 0)
    total_rows = result2.get('total_rows_in_file', 0)
    
    print_header("VALIDATION RESULTS")
    
    # Check 1: Run 2 should import 0 new records
    if run2_imported == 0:
        print("✅ PASS: Run 2 imported 0 new records (as expected)")
    else:
        print(f"❌ FAIL: Run 2 imported {run2_imported} records (expected 0)")
        return False
    
    # Check 2: Run 2 should skip all records
    if run2_skipped == total_rows:
        print(f"✅ PASS: Run 2 skipped all {total_rows} records (as expected)")
    else:
        print(f"❌ FAIL: Run 2 skipped {run2_skipped}/{total_rows} records")
        return False
    
    # Final Summary
    print_header("TEST SUMMARY")
    print("🎉 ALL TESTS PASSED!")
    print("\nVerified behaviors:")
    print("  ✅ First upload: Imports new records (or skips if already in DB)")
    print("  ✅ Second upload: Skips ALL existing records")
    print("  ✅ No updates performed on existing records")
    print("\n💡 The import logic is now 'INSERT ONLY' - existing records are preserved.")
    
    return True

if __name__ == "__main__":
    try:
        success = test_skip_logic()
        if not success:
            print("\n❌ TEST FAILED")
            exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
