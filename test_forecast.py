import requests
import json

BASE_URL = "http://localhost:8000"

def test_forecast():
    print("\n" + "=" * 60)
    print("TEST: Sales Forecast API")
    print("=" * 60)
    
    try:
        response = requests.get(f"{BASE_URL}/api/forecast")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Success! Records: {len(data)}")
            
            if len(data) > 0:
                print("\nSample Data:")
                # Print first 2
                for item in data[:2]:
                    print(f"   {item}")
                print("   ...")
                # Print last 4 (Transition + Future)
                for item in data[-4:]:
                    print(f"   {item}")
                    
                # Verify Connection Point
                # Find last item with revenue value
                last_actual_idx = -1
                for i, item in enumerate(data):
                    if item["revenue"] is not None:
                        last_actual_idx = i
                
                if last_actual_idx != -1:
                    last_actual = data[last_actual_idx]
                    print(f"\nConnection Point ({last_actual['name']}):")
                    print(f"   Revenue: {last_actual['revenue']}")
                    print(f"   Profit:  {last_actual['profit']}")
                    print(f"   Forecast: {last_actual['forecast']}")
                    
                    if last_actual['forecast'] == last_actual['revenue']:
                        print("✅ Connection Point Verified (Forecast == Revenue)")
                    else:
                        print("❌ Connection Point Mismatch")
                
                return True
            else:
                print("⚠️  No data returned.")
                return False
        else:
            print(f"❌ FAILED: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        return False

if __name__ == "__main__":
    test_forecast()
