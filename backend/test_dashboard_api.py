"""
Test dashboard API to see if data is now showing
"""
import requests
import json

base_url = "http://127.0.0.1:8000"

print("Testing Dashboard API Endpoints")
print("=" * 80)

# Test 1: Get available years
print("\n[TEST 1] Get Available Years")
try:
    response = requests.get(f"{base_url}/api/available-years")
    data = response.json()
    print(f"  Status: {response.status_code}")
    print(f"  Years: {data.get('years')}")
    print(f"  Default Year: {data.get('default_year')}")
except Exception as e:
    print(f"  ❌ Error: {e}")

# Test 2: Get dashboard data
print("\n[TEST 2] Get Dashboard Data")
try:
    response = requests.get(f"{base_url}/api/dashboard")
    data = response.json()
    print(f"  Status: {response.status_code}")
    
    kpi = data.get('kpi', {})
    print(f"\n  KPIs:")
    print(f"    Revenue: {kpi.get('revenue', 0):,.0f}")
    print(f"    Profit: {kpi.get('profit', 0):,.0f}")
    print(f"    Margin: {kpi.get('margin', 0):.1f}%")
    
    charts = data.get('charts', {})
    print(f"\n  Charts:")
    print(f"    Monthly Trend: {len(charts.get('monthly_trend', []))} months")
    print(f"    Channels: {len(charts.get('channel_distribution', []))} channels")
    print(f"    Top Products: {len(charts.get('top_products', []))} products")
    print(f"    Top Salesmen: {len(charts.get('top_salesmen', []))} salesmen")
    
    perf = data.get('sales_performance', [])
    print(f"\n  Sales Performance: {len(perf)} records")
    
except Exception as e:
    print(f"  ❌ Error: {e}")

# Test 3: Get forecast data
print("\n[TEST 3] Get Forecast Data")
try:
    response = requests.get(f"{base_url}/api/forecast")
    data = response.json()
    print(f"  Status: {response.status_code}")
    print(f"  Months with data: {len(data)}")
    if data:
        print(f"  First month: {data[0]}")
except Exception as e:
    print(f"  ❌ Error: {e}")

print("\n" + "=" * 80)
print("✅ Testing completed!")
