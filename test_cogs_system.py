"""
COGS System Verification Script
Tests the Real Profit Calculation Engine
"""

import requests
import os

BASE_URL = "http://localhost:8000"

def test_cogs_upload():
    """Test COGS file upload"""
    print("=" * 60)
    print("TEST 1: COGS Upload")
    print("=" * 60)
    
    cogs_file = "demodata/cogsupload.xlsx"
    
    if not os.path.exists(cogs_file):
        print(f"❌ COGS file not found: {cogs_file}")
        return False
    
    print(f"📁 Uploading: {cogs_file}")
    
    with open(cogs_file, 'rb') as f:
        files = {'file': f}
        response = requests.post(f"{BASE_URL}/api/upload-cogs", files=files)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ SUCCESS: {result.get('message')}")
        print(f"   Rows Processed: {result.get('rows_processed')}")
        return True
    else:
        print(f"❌ FAILED: {response.status_code}")
        print(f"   Error: {response.text}")
        return False

def test_sales_upload():
    """Test sales data upload (triggers profit recalculation)"""
    print("\n" + "=" * 60)
    print("TEST 2: Sales Data Upload (with COGS)")
    print("=" * 60)
    
    sales_file = "demodata/zrsd002_11.xlsx"
    
    if not os.path.exists(sales_file):
        print(f"❌ Sales file not found: {sales_file}")
        return False
    
    print(f"📁 Uploading: {sales_file}")
    
    with open(sales_file, 'rb') as f:
        files = {'file': f}
        response = requests.post(f"{BASE_URL}/api/upload", files=files)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ SUCCESS: Processed {result.get('rows_processed')} rows")
        return True
    else:
        print(f"❌ FAILED: {response.status_code}")
        print(f"   Error: {response.text}")
        return False

def test_dashboard_data():
    """Verify dashboard shows real profit data"""
    print("\n" + "=" * 60)
    print("TEST 3: Dashboard Data Verification")
    print("=" * 60)
    
    response = requests.get(f"{BASE_URL}/api/dashboard")
    
    if response.status_code == 200:
        data = response.json()
        kpi = data.get('kpi', {})
        
        print("📊 KPI Metrics:")
        print(f"   Revenue:       {kpi.get('revenue'):,.0f} VND")
        print(f"   Profit:        {kpi.get('profit'):,.0f} VND")
        print(f"   Margin:        {kpi.get('margin'):.2f}%")
        print(f"   Revenue Growth: {kpi.get('revenue_growth'):.1f}%")
        print(f"   Profit Growth:  {kpi.get('profit_growth'):.1f}%")
        
        margin = kpi.get('margin', 0)
        
        # Check if margin is different from fixed 30%
        if abs(margin - 30.0) > 0.1:
            print(f"\n✅ REAL PROFIT ACTIVE: Margin is {margin:.2f}% (not fixed 30%)")
            return True
        else:
            print(f"\n⚠️  WARNING: Margin is still 30% - COGS may not be applied")
            print("   Make sure to upload COGS BEFORE sales data")
            return False
    else:
        print(f"❌ FAILED: {response.status_code}")
        return False

import sys

def main():
    with open("test_log.txt", "w", encoding="utf-8") as log_file:
        sys.stdout = log_file
        print("\n🎯 REAL PROFIT CALCULATION ENGINE - VERIFICATION\n")
        
        # Check if backend is running
        try:
            response = requests.get(BASE_URL)
            print(f"✅ Backend is running at {BASE_URL}\n")
        except requests.exceptions.ConnectionError:
            print(f"❌ Backend is NOT running at {BASE_URL}")
            print("   Please start: python -m uvicorn main:app --reload --port 8000")
            return
        
        # Run tests
        test1 = test_cogs_upload()
        
        if test1:
            test2 = test_sales_upload()
            
            if test2:
                test3 = test_dashboard_data()
                
                print("\n" + "=" * 60)
                print("VERIFICATION SUMMARY")
                print("=" * 60)
                
                if test1 and test2 and test3:
                    print("✅ ALL TESTS PASSED - Real Profit Engine is ACTIVE!")
                    print("\n🎉 Next Steps:")
                    print("   1. Open http://localhost:3000")
                    print("   2. Check the Profit Margin KPI card")
                    print("   3. Ask AI Analyst: 'What is our profit margin?'")
                else:
                    print("⚠️  Some tests failed - check logs above")
        
        sys.stdout = sys.__stdout__
        print("Test complete. Check test_log.txt")

if __name__ == "__main__":
    main()
