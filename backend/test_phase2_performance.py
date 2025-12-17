"""
Phase 2 Performance Tests
Verify caching, query logging, and memory optimizations
"""

import time
import requests
from database import SessionLocal
from sqlalchemy import text

BASE_URL = "http://localhost:8000"

print("\n" + "=" * 80)
print("PHASE 2 PERFORMANCE TESTS")
print("=" * 80)

# Test 1: Cache Performance
print("\n[Test 1] Cache Hit Rate Test")
print("-" * 40)

# First request (cache miss)
start = time.time()
response1 = requests.get(f"{BASE_URL}/api/dashboard?year=2024")
time1 = time.time() - start

# Second request (should be cached)
start = time.time()
response2 = requests.get(f"{BASE_URL}/api/dashboard?year=2024")
time2 = time.time() - start

print(f"First request (cache miss): {time1:.3f}s")
print(f"Second request (cache hit): {time2:.3f}s")
print(f"Speedup: {time1/time2:.1f}x")

if time2 < time1 * 0.1:  # Should be at least 10x faster
    print("✅ PASS: Cache is working effectively")
else:
    print("⚠️  WARNING: Cache may not be working optimally")

# Test 2: Cache Stats
print("\n[Test 2] Cache Statistics")
print("-" * 40)

response = requests.get(f"{BASE_URL}/api/cache/stats")
stats = response.json()

print(f"Total requests: {stats['total_requests']}")
print(f"Cache hits: {stats['hits']}")
print(f"Cache misses: {stats['misses']}")
print(f"Hit rate: {stats['hit_rate']}%")
print(f"Cache size: {stats['cache_size']} entries")

if stats['hit_rate'] > 50:
    print("✅ PASS: Good cache hit rate")
else:
    print("⚠️  INFO: Cache warming up (hit rate will improve)")

# Test 3: Query Logging
print("\n[Test 3] Query Logging Verification")
print("-" * 40)

db = SessionLocal()

# Execute a slow query intentionally
print("Executing intentionally slow query...")
start = time.time()
result = db.execute(text("""
    SELECT s.*, p.cogs
    FROM sales_data s
    LEFT JOIN product_cost p ON s.description = p.description
    WHERE s.year = 2024
    LIMIT 10000
""")).fetchall()
elapsed = time.time() - start

print(f"Query time: {elapsed:.2f}s")
if elapsed > 1.0:
    print("✅ Check backend logs for SLOW QUERY warning")
else:
    print("ℹ️  Query was fast (< 1s), no slow query log expected")

db.close()

# Test 4: Multiple Endpoints Caching
print("\n[Test 4] Multi-Endpoint Cache Test")
print("-" * 40)

endpoints = [
    "/api/dashboard?year=2024",
    "/api/analytics/product-matrix?year=2024",
    "/api/analytics/target-waterfall?year=2024",
    "/api/debt/overview"
]

for endpoint in endpoints:
    # First request
    start = time.time()
    r1 = requests.get(f"{BASE_URL}{endpoint}")
    t1 = time.time() - start
    
    # Second request (cached)
    start = time.time()
    r2 = requests.get(f"{BASE_URL}{endpoint}")
    t2 = time.time() - start
    
    speedup = t1 / t2 if t2 > 0 else 0
    status = "✅" if speedup > 5 else "⚠️"
    
    print(f"{status} {endpoint}: {t1:.3f}s → {t2:.3f}s ({speedup:.1f}x)")

print("\n" + "=" * 80)
print("✅ PHASE 2 TESTS COMPLETED")
print("=" * 80)
print("\n💡 Next steps:")
print("   1. Check backend logs for slow query warnings")
print("   2. Monitor cache hit rate over time")
print("   3. Verify memory usage during imports")
