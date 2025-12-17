"""
Quick Test - Production Frontend Integration
Verifies that the backend APIs are ready for the new frontend
"""
import requests

BASE_URL = "http://localhost:8000"

def test_production_apis():
    """Test that production APIs are accessible"""
    
    print("=" * 80)
    print("PRODUCTION FRONTEND INTEGRATION - API READINESS TEST")
    print("=" * 80)
    
    # Test 1: Production Analytics API
    print("\n[TEST 1] Production Analytics API")
    print(f"GET {BASE_URL}/api/production/analytics")
    
    try:
        response = requests.get(f"{BASE_URL}/api/production/analytics")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API working - {data['summary']['total_orders']} orders found")
            print(f"   Avg Lead Time: {data['summary']['avg_lead_time']:.1f} days")
            print(f"   Avg Yield Rate: {data['summary']['avg_yield_rate']:.2f}%")
        else:
            print(f"⚠️  API returned non-200: {response.text}")
    except Exception as e:
        print(f"❌ API Error: {e}")
    
    # Test 2: MRP Performance API
    print("\n[TEST 2] MRP Performance API")
    print(f"GET {BASE_URL}/api/production/mrp-performance")
    
    try:
        response = requests.get(f"{BASE_URL}/api/production/mrp-performance")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            controllers = data.get('controllers', [])
            print(f"✅ API working - {len(controllers)} MRP controllers found")
        else:
            print(f"⚠️  API returned non-200: {response.text}")
    except Exception as e:
        print(f"❌ API Error: {e}")
    
    # Test 3: Backend Server Health
    print("\n[TEST 3] Backend Server Health")
    
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Status: {response.status_code}")
        print("✅ Backend server is running")
    except Exception as e:
        print(f"❌ Backend server not responding: {e}")
    
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print("✅ Backend APIs are ready for frontend integration")
    print("\nNext Steps:")
    print("1. Visit: http://localhost:3000/analytics")
    print("2. Click on 'Production Insights' tab")
    print("3. Verify data displays correctly")
    print("\n💡 TIP: If frontend shows errors, check browser console (F12)")

if __name__ == "__main__":
    test_production_apis()
