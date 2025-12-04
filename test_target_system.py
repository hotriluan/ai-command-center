import requests
import sys
import json

BASE_URL = "http://localhost:8000"

def test_target_upload():
    print("\n" + "=" * 60)
    print("TEST 1: Target Upload")
    print("=" * 60)
    
    file_path = "demodata/target.xlsx"
    print(f"📁 Uploading: {file_path}")
    
    try:
        with open(file_path, "rb") as f:
            files = {"file": f}
            response = requests.post(f"{BASE_URL}/api/upload-target", files=files)
            
        if response.status_code == 200:
            result = response.json()
            if "error" in result:
                print(f"❌ FAILED: {result['error']}")
                return False
            print(f"✅ SUCCESS: {result.get('message')}")
            return True
        else:
            print(f"❌ FAILED: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        return False

def test_dashboard_kpi():
    print("\n" + "=" * 60)
    print("TEST 2: Dashboard KPI Verification")
    print("=" * 60)
    
    try:
        response = requests.get(f"{BASE_URL}/api/dashboard")
        if response.status_code == 200:
            data = response.json()
            sales_perf = data.get("sales_performance", [])
            
            print(f"📊 Sales Performance Records: {len(sales_perf)}")
            
            if len(sales_perf) > 0:
                print("\nTop 3 Performers:")
                for item in sales_perf[:3]:
                    print(f"   - {item['name']} (Sem {item['semester']}): {item['actual']:,.0f} / {item['target']:,.0f} ({item['rate']}%) [{item['status']}]")
                
                print("\n✅ KPI Data Verified!")
                return True
            else:
                print("⚠️  WARNING: No sales performance data found. Did you upload Sales Data?")
                return False
        else:
            print(f"❌ FAILED: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        return False

def main():
    print("\n🎯 SALES TARGET KPI ENGINE - VERIFICATION\n")
    
    if test_target_upload():
        test_dashboard_kpi()

if __name__ == "__main__":
    main()
